#!/usr/bin/env python3
"""Compare a captured PIE command.json with structured requirements in an expected sheet."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REQ_BLOCK = re.compile(r"```command-requirements\s*\n(.*?)\n```", re.DOTALL | re.IGNORECASE)
EXEC = re.compile(r"^-ExecCmds=(.*)$", re.IGNORECASE)
CVAR = re.compile(r"\b(rpg\.[A-Za-z0-9_.]+)\s*(?:=|\s)\s*([A-Za-z0-9_.+-]+)", re.IGNORECASE)
UNSAFE_PREFIXES = ("-saveconfig", "-executepythonscript", "-run=")


def normalize_arg(value: str) -> str:
    return value.strip().strip('"').strip()


def load_requirements(expected: Path) -> tuple[dict[str, object], int]:
    lines = expected.read_text(encoding="utf-8", errors="replace").splitlines()
    match = REQ_BLOCK.search("\n".join(lines))
    if not match:
        raise ValueError("expected sheet must include a ```command-requirements JSON block")
    line = "\n".join(lines).count("\n", 0, match.start()) + 1
    payload = json.loads(match.group(1))
    if not isinstance(payload, dict):
        raise ValueError("command requirements must be a JSON object")
    return payload, line


def audit(command: Path, expected: Path) -> tuple[list[str], list[str]]:
    requirements, _ = load_requirements(expected)
    raw = json.loads(command.read_text(encoding="utf-8"))
    if not isinstance(raw, list) or any(not isinstance(item, str) for item in raw):
        raise ValueError("command.json must be an array of argument strings")
    args = [normalize_arg(item) for item in raw]
    normalized = {item.casefold() for item in args}
    issues: list[str] = []
    for required in requirements.get("required_args", []):
        if not isinstance(required, str):
            raise ValueError("required_args must contain strings")
        if normalize_arg(required).casefold() not in normalized:
            issues.append(f"MISSING required argument {required}")
    present_cvars: dict[str, str] = {}
    for argument in args:
        for key, value in CVAR.findall(argument):
            present_cvars[key.casefold()] = value
    required_cvars = requirements.get("required_cvars", {})
    if not isinstance(required_cvars, dict):
        raise ValueError("required_cvars must be an object")
    for key, value in required_cvars.items():
        observed = present_cvars.get(str(key).casefold())
        if observed is None:
            issues.append(f"MISSING required inline CVar {key}={value}")
        elif observed != str(value):
            issues.append(f"MISMATCH inline CVar {key}: expected {value}, observed {observed}")
    allowed_exec = {normalize_arg(str(item)).casefold() for item in requirements.get("allowed_exec_cmds", [])}
    for argument in args:
        match = EXEC.match(argument)
        if match and normalize_arg(match.group(1)).casefold() not in allowed_exec:
            issues.append(f"UNSAFE unlisted -ExecCmds mutation {argument}")
        folded = argument.casefold()
        if any(folded.startswith(prefix) for prefix in UNSAFE_PREFIXES):
            issues.append(f"UNSAFE disallowed mutation argument {argument}")
    return args, issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", type=Path)
    parser.add_argument("expected", type=Path)
    args = parser.parse_args()
    if not args.command.is_file() or not args.expected.is_file():
        parser.error("command.json and expected sheet must exist")
    try:
        observed, issues = audit(args.command, args.expected)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR {exc}")
        return 2
    print(f"COMMAND {args.command} EXPECTED {args.expected}")
    for issue in issues:
        print(issue)
    if issues:
        print("RESULT: FAIL")
        return 1
    print(f"RESULT: PASS ({len(observed)} arguments matched requirements)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
