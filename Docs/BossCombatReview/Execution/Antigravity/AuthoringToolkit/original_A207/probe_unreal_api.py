#!/usr/bin/env python3
"""
probe_unreal_api.py - Read-Only Unreal Engine Python API & Reflection Probe

Authored for Task Orders A-206 / A-207 (Directives C-301 / C-302).
Strictly read-only diagnostic tool that:
1. Statically extracts all `unreal.*` attribute chains from toolkit files with AST.
2. Derives candidate C++ types (USTRUCT, UENUM, UCLASS) dynamically from source headers
   (Source/OneBossFight/Player/RPGEncounterBinding.h and native component headers) and tests
   BOTH the native C++ name and the prefix-stripped Unreal Python wrapper name.
3. Probes the public members of key editor libraries (SystemLibrary, EditorAssetLibrary,
   AssetToolsHelpers, UnrealEditorSubsystem, AssetTools) without underscores.
4. Filters `dir(unreal)` for symbols matching: Editor, Subsystem, AssetTools, DataAsset, Factory, Load, Save, RPG.
5. Compares Python property names for all 17 authored structs against authoring_core.py, marking MATCH/MISMATCH.
6. Compares enumerators of RPGBossDeathMode against toolkit death mode names, marking MATCH/MISMATCH.

SAFEGUARDS & LIMITS:
- STRICTLY READ-ONLY: zero asset creation, zero load of assets, zero save, zero editor property writes.
- Exit code 0 always (diagnostic report, never fails a build or execution gate).
- Zero disk writes unless explicit `--output <path>` is provided.
- Pure Python standard library with -B compliance; runs offline or headlessly in UnrealEditor-Cmd.
- An offline run proves nothing about the engine.
"""

import argparse
import ast
import os
import re
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

STRUCT_RE = re.compile(r"USTRUCT\s*\((?:[^)(]+|\((?:[^)(]+|\([^)(]*\))*\))*\)\s*struct\s+(?:[A-Z0-9_]+_API\s+)?(\w+)", re.MULTILINE)
ENUM_RE = re.compile(r"UENUM\s*\((?:[^)(]+|\((?:[^)(]+|\([^)(]*\))*\))*\)\s*enum\s+(?:class\s+)?(\w+)", re.MULTILINE)
CLASS_RE = re.compile(r"UCLASS\s*\((?:[^)(]+|\((?:[^)(]+|\([^)(]*\))*\))*\)\s*class\s+(?:[A-Z0-9_]+_API\s+)?(\w+)", re.MULTILINE)

SPEC_TO_STRUCT_MAP = {
    "stats": ("FRPGBossStatsConfig", "RPGBossStatsConfig"),
    "encounter_policy": ("FRPGEncounterPolicyConfig", "RPGEncounterPolicyConfig"),
    "stagger_policy": ("FRPGStaggerPolicyConfig", "RPGStaggerPolicyConfig"),
    "phase_flow": ("FRPGPhaseFlowConfig", "RPGPhaseFlowConfig"),
    "fireball": ("FRPGFireballConfig", "RPGFireballConfig"),
    "phase_dependencies": ("FRPGPhaseDependencyConfig", "RPGPhaseDependencyConfig"),
    "stagger_profile": ("FRPGStaggerProfileConfig", "RPGStaggerProfileConfig"),
    "dormant_wake": ("FRPGDormantWakeConfig", "RPGDormantWakeConfig"),
    "bleed": ("FRPGBleedConfig", "RPGBleedConfig"),
    "low_sweep": ("FRPGLowSweepConfig", "RPGLowSweepConfig"),
    "shockwave": ("FRPGShockwaveConfig", "RPGShockwaveConfig"),
    "heal_punish": ("FRPGHealPunishConfig", "RPGHealPunishConfig"),
    "look": ("FRPGLookConfig", "RPGLookConfig"),
    "close_clip_swap": ("FRPGCloseClipSwapConfig", "RPGCloseClipSwapConfig"),
    "death": ("FRPGDeathConfig", "RPGDeathConfig"),
    "phases": ("FRPGPhaseConfig", "RPGPhaseConfig"),
    "fields": ("FRPGParityField", "RPGParityField"),
}

UNREAL_FILTER_KEYWORDS = ["Editor", "Subsystem", "AssetTools", "DataAsset", "Factory", "Load", "Save", "RPG"]

def strip_unreal_prefix(name: str) -> str:
    """
    Strips Unreal Engine C++ prefix letter:
    - 'F' for structs (e.g. FRPGBleedConfig -> RPGBleedConfig, FRPGDeathConfig -> RPGDeathConfig)
    - 'U' or 'A' for classes (e.g. URPGBossDefinition -> RPGBossDefinition, ARPGEncounterBinding -> RPGEncounterBinding)
    - 'E' for enums (e.g. ERPGBossDeathMode -> RPGBossDeathMode)
    Only strips if followed by an uppercase letter and name length > 1.
    """
    if len(name) > 1 and name[0] in ("F", "U", "A", "E") and name[1].isupper():
        return name[1:]
    return name

def extract_cpp_types_from_header(content: str) -> List[Tuple[str, str, str]]:
    """
    Extracts (kind, cpp_name, py_name) from C++ header content.
    """
    types: List[Tuple[str, str, str]] = []
    for s in STRUCT_RE.findall(content):
        types.append(("USTRUCT", s, strip_unreal_prefix(s)))
    for e in ENUM_RE.findall(content):
        types.append(("UENUM", e, strip_unreal_prefix(e)))
    for c in CLASS_RE.findall(content):
        types.append(("UCLASS", c, strip_unreal_prefix(c)))
    return types

def extract_candidate_types_from_cpp(repo_root: str = REPO_ROOT) -> List[Tuple[str, str, str, str]]:
    """
    Scans Source/OneBossFight/Player/RPGEncounterBinding.h and native component headers
    for all USTRUCT, UENUM, and UCLASS declarations.
    Returns: sorted list of (kind, cpp_name, py_name, defining_header_basename)
    """
    player_dir = os.path.join(repo_root, "Source", "OneBossFight", "Player")
    if not os.path.exists(player_dir):
        return []

    target_headers = ["RPGEncounterBinding.h"] + [
        f for f in sorted(os.listdir(player_dir))
        if f.startswith("RPGBoss") and f.endswith(".h")
    ]

    dedup: Dict[str, Tuple[str, str, str, str]] = {}
    for hname in target_headers:
        fpath = os.path.join(player_dir, hname)
        if not os.path.exists(fpath):
            continue
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for kind, cpp_name, py_name in extract_cpp_types_from_header(content):
            if cpp_name not in dedup:
                dedup[cpp_name] = (kind, cpp_name, py_name, hname)

    return sorted(dedup.values(), key=lambda x: (x[0], x[1]))

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
                native_to_py = spec[1]
                if isinstance(native_to_py, dict):
                    struct_props[sname] = sorted(native_to_py.values())
        return struct_props
    except Exception:
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

def run_probe(unreal_mod: Optional[Any] = None, repo_root: str = REPO_ROOT) -> Tuple[List[str], int, int]:
    """
    Executes the static extraction and (if unreal is available) the runtime probe.
    Returns: (lines, present_count, missing_count)
    """
    report_lines: List[str] = []
    static_chains = extract_static_chains(repo_root)
    candidate_types = extract_candidate_types_from_cpp(repo_root)
    py_props = extract_python_property_names()

    # Deduplicate static chains preserving first citation
    unique_chains: Dict[str, List[str]] = {}
    for chain, fpath, lno in static_chains:
        site = f"{os.path.basename(fpath)}:{lno}"
        unique_chains.setdefault(chain, []).append(site)

    report_lines.append("=== STATIC UNREAL API CHAINS & CITATIONS ===")
    for chain in sorted(unique_chains.keys()):
        sites = unique_chains[chain]
        report_lines.append(f"  {chain:50} (cited: {', '.join(sites[:3])})")

    report_lines.append(f"\n=== CANDIDATE TYPES DERIVED FROM C++ HEADERS ({len(candidate_types)} symbols) ===")
    for kind, cpp_name, py_name, hname in candidate_types:
        report_lines.append(f"  {kind:8} cpp={cpp_name:30} py={py_name:30} ({hname})")

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

        # 1. Probe static chains
        report_lines.append("\n--- [1] STATIC ATTRIBUTE CHAIN VERIFICATION ---")
        for chain in sorted(unique_chains.keys()):
            exists, is_callable, type_name = resolve_unreal_chain(unreal_mod, chain)
            if exists:
                present_count += 1
            else:
                missing_count += 1
            report_lines.append(f"[PROBE] {chain} exists={exists} callable={is_callable} type={type_name}")

        # 2. Probe candidate types derived from C++ source headers (testing BOTH cpp and py names)
        report_lines.append("\n--- [2] C++ DERIVED TYPE VERIFICATION (CPP vs PYTHON WRAPPER) ---")
        for kind, cpp_name, py_name, hname in candidate_types:
            exists_cpp = hasattr(unreal_mod, cpp_name)
            exists_py = hasattr(unreal_mod, py_name)
            if exists_py or exists_cpp:
                present_count += 1
            else:
                missing_count += 1
            report_lines.append(f"[PROBE] type cpp={cpp_name} py={py_name} exists_cpp={exists_cpp} exists_py={exists_py}")

        # 3. Probe libraries used by the helper (printing full public members without underscores)
        report_lines.append("\n--- [3] PUBLIC MEMBER LISTS FOR USED LIBRARIES ---")
        library_names = ["SystemLibrary", "EditorAssetLibrary", "AssetToolsHelpers", "UnrealEditorSubsystem", "AssetTools"]
        for lib_name in library_names:
            lib_obj = None
            if lib_name == "AssetTools":
                if hasattr(unreal_mod, "AssetToolsHelpers") and hasattr(unreal_mod.AssetToolsHelpers, "get_asset_tools"):
                    try:
                        lib_obj = unreal_mod.AssetToolsHelpers.get_asset_tools()
                    except Exception:
                        lib_obj = None
                if lib_obj is None and hasattr(unreal_mod, "AssetTools"):
                    lib_obj = getattr(unreal_mod, "AssetTools")
            else:
                if hasattr(unreal_mod, lib_name):
                    lib_obj = getattr(unreal_mod, lib_name)

            if lib_obj is not None:
                members = sorted([m for m in dir(lib_obj) if not m.startswith("_")])
                report_lines.append(f"[PROBE] LIBRARY {lib_name} member_count={len(members)}:")
                for m in members:
                    report_lines.append(f"  [PROBE] {lib_name}.{m}")
            else:
                report_lines.append(f"[PROBE] LIBRARY {lib_name} NOT FOUND in unreal")

        # 4. Filtered dir(unreal) for exported symbols
        report_lines.append(f"\n--- [4] FILTERED UNREAL EXPORTED SYMBOLS (matching keywords) ---")
        unreal_all = dir(unreal_mod)
        matched_symbols = sorted([
            name for name in unreal_all
            if not name.startswith("_") and any(k.lower() in name.lower() for k in UNREAL_FILTER_KEYWORDS)
        ])
        report_lines.append(f"[PROBE] UNREAL_MATCHED_SYMBOLS count={len(matched_symbols)}:")
        for sym in matched_symbols:
            report_lines.append(f"[PROBE] UNREAL_SYMBOL {sym}")

        # 5. Struct property comparisons (dir() properties vs authoring_core.py pythonized names)
        report_lines.append("\n--- [5] STRUCT PROPERTY COMPARISON (MATCH / MISMATCH) ---")
        for spec_key, (cpp_struct, py_struct) in sorted(SPEC_TO_STRUCT_MAP.items()):
            tk_expected = py_props.get(spec_key, [])
            if hasattr(unreal_mod, py_struct):
                struct_cls = getattr(unreal_mod, py_struct)
                engine_props = sorted([p for p in dir(struct_cls) if not p.startswith("_") and not p.startswith("cast")])
                report_lines.append(f"[PROBE] STRUCT {py_struct} property_count={len(engine_props)}:")
                for tk_p in tk_expected:
                    if tk_p in engine_props:
                        report_lines.append(f"  [PROBE] STRUCT_PROP {py_struct} prop={tk_p} toolkit={tk_p} status=MATCH")
                    else:
                        report_lines.append(f"  [PROBE] STRUCT_PROP {py_struct} prop=NONE toolkit={tk_p} status=MISMATCH")
                for ep in engine_props:
                    if ep not in tk_expected:
                        report_lines.append(f"  [PROBE] STRUCT_PROP {py_struct} prop={ep} toolkit=NONE status=MISMATCH")
            else:
                report_lines.append(f"[PROBE] STRUCT {py_struct} NOT FOUND in unreal")
                for tk_p in tk_expected:
                    report_lines.append(f"  [PROBE] STRUCT_PROP {py_struct} prop=NONE toolkit={tk_p} status=MISMATCH")

        # 6. Enum comparison for RPGBossDeathMode
        report_lines.append("\n--- [6] ENUM COMPARISON FOR RPGBossDeathMode ---")
        tk_modes = ["PackMontage", "OwnClip"]
        if hasattr(unreal_mod, "RPGBossDeathMode"):
            enum_cls = getattr(unreal_mod, "RPGBossDeathMode")
            engine_enums = sorted([m for m in dir(enum_cls) if not m.startswith("_") and not m.startswith("cast")])
            report_lines.append(f"[PROBE] ENUM RPGBossDeathMode enumerator_count={len(engine_enums)}:")
            matched_set = set()
            for tk_m in tk_modes:
                matched_name = None
                for ee in engine_enums:
                    if ee == tk_m or ee.lower() == tk_m.lower() or ee.replace("_", "").lower() == tk_m.lower():
                        matched_name = ee
                        matched_set.add(ee)
                        break
                if matched_name:
                    report_lines.append(f"  [PROBE] ENUM_MEMBER RPGBossDeathMode member={matched_name} toolkit={tk_m} status=MATCH")
                else:
                    report_lines.append(f"  [PROBE] ENUM_MEMBER RPGBossDeathMode member=NONE toolkit={tk_m} status=MISMATCH")
            for ee in engine_enums:
                if ee not in matched_set:
                    report_lines.append(f"  [PROBE] ENUM_MEMBER RPGBossDeathMode member={ee} toolkit=NONE status=MISMATCH")
        else:
            report_lines.append("[PROBE] ENUM RPGBossDeathMode NOT FOUND in unreal")
            for tk_m in tk_modes:
                report_lines.append(f"  [PROBE] ENUM_MEMBER RPGBossDeathMode member=NONE toolkit={tk_m} status=MISMATCH")

        report_lines.append(f"\n[PROBE] SUMMARY missing={missing_count} present={present_count}")
    else:
        report_lines.append("\n[PROBE] unreal not importable: runtime part skipped")
        report_lines.append("[PROBE] NOTICE: An offline run proves nothing about the engine.")
        report_lines.append("[PROBE] SUMMARY missing=0 present=0")

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

    # Exit code is always 0 per C-301 / C-302
    sys.exit(0)

if __name__ == "__main__":
    main()
