#!/usr/bin/env python3
"""
probe_unreal_api.py - Read-Only Unreal Engine Python API & Reflection Probe

Authored for Task Order A-206 (C-301).
Strictly read-only diagnostic tool that statically extracts all `unreal.*` attribute chains,
reflection types, and pythonized struct property names referenced by the authoring toolkit,
and (when executed inside the Unreal Editor) probes their existence, callability, and reflection dir().

SAFEGUARDS & LIMITS:
- STRICTLY READ-ONLY: zero asset creation, zero load of assets, zero save, zero editor property writes.
- Exit code 0 always (diagnostic report, never fails a build or execution gate).
- Zero disk writes unless explicit `--output <path>` is provided.
- Pure Python standard library with -B compliance; runs offline or headlessly in UnrealEditor-Cmd.
"""

import argparse
import ast
import json
import os
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

def find_repo_root() -> str:
    candidate = os.path.abspath(os.path.dirname(__file__))
    while candidate and candidate != os.path.dirname(candidate):
        if os.path.exists(os.path.join(candidate, "Source", "OneBossFight")) or os.path.exists(os.path.join(candidate, ".git")):
            return candidate
        candidate = os.path.dirname(candidate)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))

REPO_ROOT = find_repo_root()
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

TOOLKIT_REL_FILES = [
    "Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/draft_boss_profiles.py",
    "Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/authoring_core.py",
    "Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/inspect_authored_assets.py"
]

# Candidate UCLASS, USTRUCT, and UENUM reflection types used by the toolkit
REFLECTION_CANDIDATES = [
    # UCLASS
    ("UCLASS", "unreal.RPGBossDefinition", "RPGBossDefinition"),
    # USTRUCTs
    ("USTRUCT", "unreal.RPGBleedConfig", "RPGBleedConfig"),
    ("USTRUCT", "unreal.FRPGBleedConfig", "FRPGBleedConfig"),
    ("USTRUCT", "unreal.RPGLowSweepConfig", "RPGLowSweepConfig"),
    ("USTRUCT", "unreal.FRPGLowSweepConfig", "FRPGLowSweepConfig"),
    ("USTRUCT", "unreal.RPGShockwaveConfig", "RPGShockwaveConfig"),
    ("USTRUCT", "unreal.FRPGShockwaveConfig", "FRPGShockwaveConfig"),
    ("USTRUCT", "unreal.RPGHealPunishConfig", "RPGHealPunishConfig"),
    ("USTRUCT", "unreal.FRPGHealPunishConfig", "FRPGHealPunishConfig"),
    ("USTRUCT", "unreal.RPGLookConfig", "RPGLookConfig"),
    ("USTRUCT", "unreal.FRPGLookConfig", "FRPGLookConfig"),
    ("USTRUCT", "unreal.RPGCloseClipSwapConfig", "RPGCloseClipSwapConfig"),
    ("USTRUCT", "unreal.FRPGCloseClipSwapConfig", "FRPGCloseClipSwapConfig"),
    ("USTRUCT", "unreal.RPGBossDeathConfig", "RPGBossDeathConfig"),
    ("USTRUCT", "unreal.FRPGBossDeathConfig", "FRPGBossDeathConfig"),
    ("USTRUCT", "unreal.RPGPhaseConfig", "RPGPhaseConfig"),
    ("USTRUCT", "unreal.FRPGPhaseConfig", "FRPGPhaseConfig"),
    ("USTRUCT", "unreal.RPGFireballConfig", "RPGFireballConfig"),
    ("USTRUCT", "unreal.FRPGFireballConfig", "FRPGFireballConfig"),
    ("USTRUCT", "unreal.RPGPhaseDependencyConfig", "RPGPhaseDependencyConfig"),
    ("USTRUCT", "unreal.FRPGPhaseDependencyConfig", "FRPGPhaseDependencyConfig"),
    ("USTRUCT", "unreal.RPGParityField", "RPGParityField"),
    ("USTRUCT", "unreal.FRPGParityField", "FRPGParityField"),
    ("USTRUCT", "unreal.RPGBossStatsConfig", "RPGBossStatsConfig"),
    ("USTRUCT", "unreal.FRPGBossStatsConfig", "FRPGBossStatsConfig"),
    ("USTRUCT", "unreal.RPGBossStaggerPolicy", "RPGBossStaggerPolicy"),
    ("USTRUCT", "unreal.FRPGBossStaggerPolicy", "FRPGBossStaggerPolicy"),
    ("USTRUCT", "unreal.RPGBossStaggerProfile", "RPGBossStaggerProfile"),
    ("USTRUCT", "unreal.FRPGBossStaggerProfile", "FRPGBossStaggerProfile"),
    ("USTRUCT", "unreal.RPGBossPhaseFlow", "RPGBossPhaseFlow"),
    ("USTRUCT", "unreal.FRPGBossPhaseFlow", "FRPGBossPhaseFlow"),
    ("USTRUCT", "unreal.RPGBossEncounterPolicy", "RPGBossEncounterPolicy"),
    ("USTRUCT", "unreal.FRPGBossEncounterPolicy", "FRPGBossEncounterPolicy"),
    ("USTRUCT", "unreal.RPGBossDormantWakeConfig", "RPGBossDormantWakeConfig"),
    ("USTRUCT", "unreal.FRPGBossDormantWakeConfig", "FRPGBossDormantWakeConfig"),
    # UENUM
    ("UENUM", "unreal.ERPGBossDeathMode", "ERPGBossDeathMode"),
    ("UENUM", "unreal.RPGBossDeathMode", "RPGBossDeathMode"),
]

def extract_static_chains(repo_root: str = REPO_ROOT) -> List[Tuple[str, str, int]]:
    """
    Parses toolkit source files with `ast` and extracts every attribute chain rooted at `unreal`
    plus reflective hasattr/getattr invocations.
    Returns: list of (chain_str, repo_relative_path, line_number)
    """
    chains: List[Tuple[str, str, int]] = []

    for rel_fpath in TOOLKIT_REL_FILES:
        full_path = os.path.join(repo_root, rel_fpath)
        if not os.path.exists(full_path):
            continue
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            src = f.read()

        try:
            tree = ast.parse(src, filename=full_path)
        except Exception:
            continue

        for node in ast.walk(tree):
            # 1. Direct AST attribute chains: unreal.A.B
            if isinstance(node, ast.Attribute):
                parts = []
                curr = node
                while isinstance(curr, ast.Attribute):
                    parts.append(curr.attr)
                    curr = curr.value
                if isinstance(curr, ast.Name) and curr.id == "unreal":
                    parts.append("unreal")
                    parts.reverse()
                    chain = ".".join(parts)
                    chains.append((chain, rel_fpath, node.lineno))

            # 2. Reflective calls: hasattr(unreal, "X") or getattr(unreal, "X")
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in ("hasattr", "getattr"):
                    if len(node.args) >= 2:
                        first = node.args[0]
                        second = node.args[1]
                        if isinstance(first, ast.Name) and first.id == "unreal" and isinstance(second, ast.Constant):
                            chain = f"unreal.{second.value}"
                            chains.append((chain, rel_fpath, node.lineno))
                        elif isinstance(first, ast.Attribute):
                            parts = []
                            curr = first
                            while isinstance(curr, ast.Attribute):
                                parts.append(curr.attr)
                                curr = curr.value
                            if isinstance(curr, ast.Name) and curr.id == "unreal" and isinstance(second, ast.Constant):
                                parts.append("unreal")
                                parts.reverse()
                                parts.append(str(second.value))
                                chain = ".".join(parts)
                                chains.append((chain, rel_fpath, node.lineno))
                        elif isinstance(first, ast.Name) and isinstance(second, ast.Constant):
                            # Resolve known reflective variable handles in toolkit guards
                            if first.id == "system_lib":
                                chain = f"unreal.SystemLibrary.{second.value}"
                                chains.append((chain, rel_fpath, node.lineno))
                            elif first.id == "editor_subsystem":
                                chain = f"unreal.UnrealEditorSubsystem.{second.value}"
                                chains.append((chain, rel_fpath, node.lineno))
                            elif first.id == "asset_tools":
                                chain = f"unreal.AssetTools.{second.value}"
                                chains.append((chain, rel_fpath, node.lineno))

    return chains

def extract_python_property_names() -> Dict[str, List[str]]:
    """
    Extracts all generated pythonized property names mapped across the 17 structs in STRUCT_SPECS.
    """
    try:
        from Docs.BossCombatReview.Execution.Antigravity.AuthoringToolkit.authoring_core import STRUCT_SPECS
        struct_props: Dict[str, List[str]] = {}
        for sname, spec in sorted(STRUCT_SPECS.items()):
            if isinstance(spec, tuple) and len(spec) >= 2:
                # spec[1] is native_to_py mapping
                native_to_py = spec[1]
                if isinstance(native_to_py, dict):
                    struct_props[sname] = sorted(native_to_py.values())
        return struct_props
    except Exception as e:
        return {}

def resolve_unreal_chain(unreal_mod: Any, chain: str) -> Tuple[bool, bool, str]:
    """
    Resolves an attribute chain on the unreal module step-by-step.
    Returns: (exists, is_callable, type_name)
    """
    parts = chain.split(".")
    if parts[0] != "unreal":
        return False, False, "invalid_root"

    curr = unreal_mod
    for attr in parts[1:]:
        if not hasattr(curr, attr):
            return False, False, "none"
        try:
            curr = getattr(curr, attr)
        except Exception as ex:
            return False, False, f"error:{type(ex).__name__}"

    return True, callable(curr), type(curr).__name__

def run_probe(unreal_mod: Optional[Any] = None) -> Tuple[List[str], int, int]:
    """
    Executes the static extraction and (if unreal is available) the runtime probe.
    Returns: (lines, present_count, missing_count)
    """
    report_lines: List[str] = []
    static_chains = extract_static_chains()
    py_props = extract_python_property_names()

    # Deduplicate chains preserving first citation
    unique_chains: Dict[str, List[str]] = {}
    for chain, fpath, lno in static_chains:
        site = f"{os.path.basename(fpath)}:{lno}"
        unique_chains.setdefault(chain, []).append(site)

    # Add reflection candidates to unique_chains
    for kind, chain, symbol in REFLECTION_CANDIDATES:
        unique_chains.setdefault(chain, [f"reflection:{kind}"])

    report_lines.append("=== STATIC UNREAL API CHAINS & CITATIONS ===")
    for chain in sorted(unique_chains.keys()):
        sites = unique_chains[chain]
        report_lines.append(f"  {chain:50} (cited: {', '.join(sites[:3])})")

    report_lines.append("\n=== PYTHONIZED STRUCT PROPERTY MAPPINGS (STRUCT_SPECS) ===")
    for sname, props in sorted(py_props.items()):
        report_lines.append(f"  {sname:20} -> [{', '.join(props)}]")

    present_count = 0
    missing_count = 0

    if unreal_mod is None:
        try:
            import unreal as imported_unreal
            unreal_mod = imported_unreal
        except ImportError:
            unreal_mod = None

    if unreal_mod is not None:
        report_lines.append("\n=== RUNTIME PROBE EXECUTION (import unreal SUCCEEDED) ===")
        for chain in sorted(unique_chains.keys()):
            exists, is_callable, type_name = resolve_unreal_chain(unreal_mod, chain)
            if exists:
                present_count += 1
            else:
                missing_count += 1
            report_lines.append(f"[PROBE] {chain} exists={exists} callable={is_callable} type={type_name}")

        report_lines.append("\n=== REFLECTION STRUCT & ENUM DISCOVERY ===")
        for kind, chain, symbol in REFLECTION_CANDIDATES:
            if hasattr(unreal_mod, symbol):
                obj = getattr(unreal_mod, symbol)
                public_attrs = sorted([a for a in dir(obj) if not a.startswith("_") and not a.startswith("cast")])
                if kind == "UENUM":
                    report_lines.append(f"[PROBE] ENUM {symbol} enumerators={public_attrs}")
                else:
                    report_lines.append(f"[PROBE] STRUCT {symbol} properties={public_attrs}")

        report_lines.append(f"\n[PROBE] SUMMARY missing={missing_count} present={present_count}")
    else:
        report_lines.append("\n[PROBE] unreal not importable: runtime part skipped")
        report_lines.append(f"[PROBE] SUMMARY missing=0 present=0")

    return report_lines, present_count, missing_count

def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only probe for Unreal Engine Python reflection and APIs.")
    parser.add_argument("--output", "-o", help="Optional output text path for probe report.")
    args = parser.parse_args()

    lines, present, missing = run_probe()
    output_text = "\n".join(lines)
    print(output_text)

    if args.output:
        out_path = os.path.abspath(args.output) if os.path.isabs(args.output) else os.path.join(REPO_ROOT, args.output)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "wb") as f:
            f.write(output_text.encode("utf-8").replace(b"\n", b"\r\n"))
        print(f"\nWrote probe report to {args.output}")

    # Exit code is always 0 per C-301
    sys.exit(0)

if __name__ == "__main__":
    main()
