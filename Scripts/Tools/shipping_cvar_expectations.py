"""BQ-73 (Queue BQ batch 15; D7, KI-168): stage-provenance checker inputs for the Shipping binary string check.

Scripts/CheckShippingBinary.py only looks for 'rpg.Debug' and 'LogRPGDebug'. This library derives, from source, the full
expectation for every rpg.* console variable registration (reusing list_cvars.registrations):
  - expected_absent: registered inside a '#if !UE_BUILD_SHIPPING' region (or the '#else' of '#if UE_BUILD_SHIPPING'),
    so its name must NOT appear in a Shipping binary;
  - expected_present: registered unguarded, so it may appear (the KI-168 "Shipping-visible" set, dispositioned in BQ-23).
``violations(found_names, expectations)`` then turns a set of names found in a binary into fail-closed findings.

Library only: no CLI, no binary is opened here. Feeding real binary strings is the packaged ENG step.
Preprocessor handling is deliberately simple (#if/#ifdef/#ifndef/#elif/#else/#endif nesting on UE_BUILD_SHIPPING); any
region it cannot classify is reported as 'unknown', never silently treated as guarded.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import list_cvars  # noqa: E402

_IF = re.compile(r"^\s*#\s*(if|ifdef|ifndef)\b(.*)$")
_ELIF = re.compile(r"^\s*#\s*elif\b(.*)$")
_ELSE = re.compile(r"^\s*#\s*else\b")
_ENDIF = re.compile(r"^\s*#\s*endif\b")


def _condition_state(expr: str) -> str:
    """'off' when the branch excludes Shipping, 'on' when it is Shipping-only, 'neutral' when unrelated, 'unknown' when mixed."""
    text = expr.replace(" ", "")
    # Development- or Debug-only branches are never compiled into Shipping.
    if text in ("UE_BUILD_DEVELOPMENT", "UE_BUILD_DEBUG", "(UE_BUILD_DEVELOPMENT)", "UE_BUILD_DEVELOPMENT||UE_BUILD_DEBUG"):
        return "off"
    if "UE_BUILD_SHIPPING" not in text:
        return "neutral"
    if text in ("!UE_BUILD_SHIPPING", "!(UE_BUILD_SHIPPING)", "UE_BUILD_SHIPPING==0"):
        return "off"
    if text in ("UE_BUILD_SHIPPING", "(UE_BUILD_SHIPPING)", "UE_BUILD_SHIPPING==1"):
        return "on"
    return "unknown"


def shipping_state_per_line(text: str) -> list[str]:
    """For each 1-based line, 'excluded' (not compiled in Shipping), 'included' or 'unknown'."""
    stack: list[str] = []  # per open #if: the state of the CURRENT branch
    out = []
    for line in text.splitlines():
        m = _IF.match(line)
        if m:
            kind, expr = m.group(1), m.group(2)
            if kind == "ifndef":
                symbol = expr.strip()
                # These build macros have known Shipping truth values. Invert the
                # ordinary #ifdef interpretation; don't mistake `#ifndef UE_BUILD_DEVELOPMENT`
                # for a non-Shipping-only region.
                if symbol == "UE_BUILD_SHIPPING":
                    stack.append("off")
                elif symbol in ("UE_BUILD_DEVELOPMENT", "UE_BUILD_DEBUG"):
                    stack.append("on")
                elif "UE_BUILD_" in symbol:
                    stack.append("unknown")
                else:
                    stack.append("neutral")
            elif kind == "ifdef":
                symbol = expr.strip()
                if symbol in ("UE_BUILD_SHIPPING", "UE_BUILD_DEVELOPMENT", "UE_BUILD_DEBUG"):
                    stack.append(_condition_state(symbol))
                elif "UE_BUILD_" in symbol:
                    stack.append("unknown")
                else:
                    stack.append("neutral")
            else:
                stack.append(_condition_state(expr))
        elif _ELIF.match(line) and stack:
            stack[-1] = "unknown" if stack[-1] != "neutral" or "UE_BUILD_SHIPPING" in line else "neutral"
        elif _ELSE.match(line) and stack:
            stack[-1] = {"off": "on", "on": "off"}.get(stack[-1], stack[-1])
        elif _ENDIF.match(line) and stack:
            stack.pop()
        states = [s for s in stack if s != "neutral"]
        if "unknown" in states:
            out.append("unknown")
        elif "off" in states:
            out.append("excluded")
        else:
            out.append("included")  # 'on' (Shipping-only) or unguarded both compile into Shipping
    return out


def expectations(root: Path) -> dict:
    absent, present, unknown = set(), set(), set()
    source = root / "Source"
    for path in sorted(source.rglob("*.cpp")) + sorted(source.rglob("*.h")):
        text = path.read_text(encoding="utf-8", errors="replace")
        if "TAutoConsoleVariable" not in text:
            continue
        states = shipping_state_per_line(text)
        lines = text.splitlines()
        # RPG_PERF_SWITCH invocations sit outside any guard, but the macro only creates the CVar in the branch where its
        # #define contains TAutoConsoleVariable; classify those names by that definition line.
        perf_define = next((i for i, l in enumerate(lines) if "#define RPG_PERF_SWITCH" in l
                            and "TAutoConsoleVariable" in "".join(lines[i:i + 3])), None)
        for name, _filename, line in list_cvars.registrations(text, path.name):
            if perf_define is not None and 0 < line <= len(lines) and "RPG_PERF_SWITCH" in lines[line - 1]:
                line = perf_define + 1
            state = states[line - 1] if 0 < line <= len(states) else "unknown"
            {"excluded": absent, "included": present}.get(state, unknown).add(name)
    # a name registered both guarded and unguarded somewhere is present in Shipping
    absent -= present
    return {"expected_absent": sorted(absent), "expected_present": sorted(present), "unknown": sorted(unknown)}


def violations(found_names, exp: dict) -> list[str]:
    """Fail-closed findings for names found in a Shipping binary."""
    found = set(found_names)
    problems = ["guarded cvar present in Shipping binary: " + n for n in exp["expected_absent"] if n in found]
    problems += ["unclassified cvar present in Shipping binary: " + n for n in exp["unknown"] if n in found]
    return problems
