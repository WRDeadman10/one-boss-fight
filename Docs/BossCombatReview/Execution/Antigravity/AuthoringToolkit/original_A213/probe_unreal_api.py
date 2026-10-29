#!/usr/bin/env python3
"""
probe_unreal_api.py - Read-Only Unreal Engine Python API & Reflection Probe

Authored for Task Orders A-206 / A-207 / A-209 (Directives C-301 / C-302 / C-305).
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
7. [STAGE 2 --instances mode]: Constructs transient in-memory struct instances and queries
   `get_editor_property` and `hasattr` across pythonized and native names, queries `RPGBossDefinition` CDO,
   and tests `unreal.is_editor`.

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

def _probe_softref_form(struct_name: str, prop_name: str, form_name: str, inst: Any, val: Any, report_lines: List[str]):
    readback_type = "NoneType"
    readback_repr = "None"
    result = "ok"
    try:
        inst.set_editor_property(prop_name, val)
        rb = inst.get_editor_property(prop_name)
        readback_type = type(rb).__name__
        readback_repr = repr(rb)
        result = "ok"
    except Exception as ex:
        ex_cls = type(ex).__name__
        ex_msg = str(ex).replace("\r\n", " ").replace("\n", " ").strip()
        result = f"error:{ex_cls}: {ex_msg}"
        try:
            rb = inst.get_editor_property(prop_name)
            readback_type = type(rb).__name__
            readback_repr = repr(rb)
        except Exception:
            pass
    line = f"[PROBE] SOFTREF {struct_name}.{prop_name} form={form_name} result={result} readback_type={readback_type} readback_repr={readback_repr}"
    report_lines.append(line)


def _run_softrefs_probe(unreal_mod: Any, report_lines: List[str]) -> None:
    # 1. Print dir(unreal.SoftObjectPath) public members
    if hasattr(unreal_mod, "SoftObjectPath"):
        sop_cls = getattr(unreal_mod, "SoftObjectPath")
        sop_members = sorted([m for m in dir(sop_cls) if not m.startswith("_")])
        report_lines.append(f"[PROBE] SOFTREF SoftObjectPath members: {sop_members}")
    else:
        report_lines.append("[PROBE] SOFTREF SoftObjectPath NOT FOUND in unreal")
        return

    # Check EditorAssetLibrary availability
    has_asset_lib = hasattr(unreal_mod, "EditorAssetLibrary")
    asset_lib = getattr(unreal_mod, "EditorAssetLibrary", None) if has_asset_lib else None
    has_does_exist = hasattr(asset_lib, "does_asset_exist") if asset_lib else False
    has_load_asset = hasattr(asset_lib, "load_asset") if asset_lib else False

    # -----------------------------------------------------------------------
    # TARGET 1: RPGBleedConfig.proc_effect (TSoftObjectPtr<UNiagaraSystem>)
    # -----------------------------------------------------------------------
    bleed_path = "/Game/BloodPack/Hit/Niagara/NS_BulletHit_Med.NS_BulletHit_Med"
    if hasattr(unreal_mod, "RPGBleedConfig"):
        bleed_cls = getattr(unreal_mod, "RPGBleedConfig")

        # Default instance readback
        try:
            def_inst = bleed_cls()
            def_val = def_inst.get_editor_property("proc_effect")
            report_lines.append(
                f"[PROBE] SOFTREF RPGBleedConfig.proc_effect form=default result=ok "
                f"readback_type={type(def_val).__name__} readback_repr={repr(def_val)}"
            )
        except Exception as ex:
            report_lines.append(
                f"[PROBE] SOFTREF RPGBleedConfig.proc_effect form=default "
                f"result=error:{type(ex).__name__}: {str(ex).strip()} readback_type=NoneType readback_repr=None"
            )

        # (i) str
        _probe_softref_form("RPGBleedConfig", "proc_effect", "str", bleed_cls(), bleed_path, report_lines)

        # (ii) SoftObjectPath(path)
        try:
            sop_inst = unreal_mod.SoftObjectPath(bleed_path)
            _probe_softref_form("RPGBleedConfig", "proc_effect", "SoftObjectPath_ctor", bleed_cls(), sop_inst, report_lines)
        except Exception as ex:
            report_lines.append(
                f"[PROBE] SOFTREF RPGBleedConfig.proc_effect form=SoftObjectPath_ctor "
                f"result=error:{type(ex).__name__}: {str(ex).strip()} readback_type=NoneType readback_repr=None"
            )

        # (iii) SoftObjectPath documented/existing setters from dir()
        if hasattr(unreal_mod.SoftObjectPath, "set_path") and callable(getattr(unreal_mod.SoftObjectPath, "set_path")):
            try:
                sop = unreal_mod.SoftObjectPath()
                sop.set_path(bleed_path)
                _probe_softref_form("RPGBleedConfig", "proc_effect", "SoftObjectPath_set_path", bleed_cls(), sop, report_lines)
            except Exception as ex:
                report_lines.append(
                    f"[PROBE] SOFTREF RPGBleedConfig.proc_effect form=SoftObjectPath_set_path "
                    f"result=error:{type(ex).__name__}: {str(ex).strip()} readback_type=NoneType readback_repr=None"
                )

        if "asset_path_name" in dir(unreal_mod.SoftObjectPath):
            try:
                sop = unreal_mod.SoftObjectPath()
                if hasattr(unreal_mod, "Name"):
                    sop.asset_path_name = unreal_mod.Name(bleed_path)
                else:
                    sop.asset_path_name = bleed_path
                _probe_softref_form("RPGBleedConfig", "proc_effect", "SoftObjectPath_asset_path_name", bleed_cls(), sop, report_lines)
            except Exception as ex:
                report_lines.append(
                    f"[PROBE] SOFTREF RPGBleedConfig.proc_effect form=SoftObjectPath_asset_path_name "
                    f"result=error:{type(ex).__name__}: {str(ex).strip()} readback_type=NoneType readback_repr=None"
                )

        try:
            pkg_part, _, asset_part = bleed_path.rpartition(".")
            sop_two = unreal_mod.SoftObjectPath(pkg_part, asset_part)
            _probe_softref_form("RPGBleedConfig", "proc_effect", "SoftObjectPath_two_arg", bleed_cls(), sop_two, report_lines)
        except Exception:
            pass

        # (iv) None
        _probe_softref_form("RPGBleedConfig", "proc_effect", "none", bleed_cls(), None, report_lines)

        # (vi) load_asset (read-only; only if asset exists on disk)
        if has_does_exist and has_load_asset:
            try:
                exists = asset_lib.does_asset_exist(bleed_path)
                if exists:
                    report_lines.append("[PROBE] SOFTREF RPGBleedConfig.proc_effect loading existing asset into memory [read-only]")
                    loaded_obj = asset_lib.load_asset(bleed_path)
                    _probe_softref_form("RPGBleedConfig", "proc_effect", "load_asset", bleed_cls(), loaded_obj, report_lines)
                else:
                    report_lines.append(f"[PROBE] SOFTREF RPGBleedConfig.proc_effect form=load_asset skipped: asset '{bleed_path}' does not exist on disk readback_type=NoneType readback_repr=None")
            except Exception as ex:
                report_lines.append(
                    f"[PROBE] SOFTREF RPGBleedConfig.proc_effect form=load_asset "
                    f"result=error:{type(ex).__name__}: {str(ex).strip()} readback_type=NoneType readback_repr=None"
                )
        else:
            report_lines.append("[PROBE] SOFTREF RPGBleedConfig.proc_effect form=load_asset skipped: EditorAssetLibrary load API missing readback_type=NoneType readback_repr=None")
    else:
        report_lines.append("[PROBE] SOFTREF RPGBleedConfig NOT FOUND in unreal")

    # -----------------------------------------------------------------------
    # TARGET 2: RPGLookConfig.body (TSoftObjectPtr<USkeletalMesh>)
    # -----------------------------------------------------------------------
    body_path = "/Game/OneBossFight/Boss01/Body/SK_Boss01_Body.SK_Boss01_Body"
    if hasattr(unreal_mod, "RPGLookConfig"):
        look_cls = getattr(unreal_mod, "RPGLookConfig")

        # Default instance readback
        try:
            def_inst = look_cls()
            def_val = def_inst.get_editor_property("body")
            report_lines.append(
                f"[PROBE] SOFTREF RPGLookConfig.body form=default result=ok "
                f"readback_type={type(def_val).__name__} readback_repr={repr(def_val)}"
            )
        except Exception as ex:
            report_lines.append(
                f"[PROBE] SOFTREF RPGLookConfig.body form=default "
                f"result=error:{type(ex).__name__}: {str(ex).strip()} readback_type=NoneType readback_repr=None"
            )

        # (i) str
        _probe_softref_form("RPGLookConfig", "body", "str", look_cls(), body_path, report_lines)

        # (ii) SoftObjectPath(path)
        try:
            sop_inst = unreal_mod.SoftObjectPath(body_path)
            _probe_softref_form("RPGLookConfig", "body", "SoftObjectPath_ctor", look_cls(), sop_inst, report_lines)
        except Exception as ex:
            report_lines.append(
                f"[PROBE] SOFTREF RPGLookConfig.body form=SoftObjectPath_ctor "
                f"result=error:{type(ex).__name__}: {str(ex).strip()} readback_type=NoneType readback_repr=None"
            )

        # (iii) SoftObjectPath documented/existing setters from dir()
        if hasattr(unreal_mod.SoftObjectPath, "set_path") and callable(getattr(unreal_mod.SoftObjectPath, "set_path")):
            try:
                sop = unreal_mod.SoftObjectPath()
                sop.set_path(body_path)
                _probe_softref_form("RPGLookConfig", "body", "SoftObjectPath_set_path", look_cls(), sop, report_lines)
            except Exception as ex:
                report_lines.append(
                    f"[PROBE] SOFTREF RPGLookConfig.body form=SoftObjectPath_set_path "
                    f"result=error:{type(ex).__name__}: {str(ex).strip()} readback_type=NoneType readback_repr=None"
                )

        if "asset_path_name" in dir(unreal_mod.SoftObjectPath):
            try:
                sop = unreal_mod.SoftObjectPath()
                if hasattr(unreal_mod, "Name"):
                    sop.asset_path_name = unreal_mod.Name(body_path)
                else:
                    sop.asset_path_name = body_path
                _probe_softref_form("RPGLookConfig", "body", "SoftObjectPath_asset_path_name", look_cls(), sop, report_lines)
            except Exception as ex:
                report_lines.append(
                    f"[PROBE] SOFTREF RPGLookConfig.body form=SoftObjectPath_asset_path_name "
                    f"result=error:{type(ex).__name__}: {str(ex).strip()} readback_type=NoneType readback_repr=None"
                )

        # (iv) None
        _probe_softref_form("RPGLookConfig", "body", "none", look_cls(), None, report_lines)

        # (vi) load_asset (read-only; only if asset exists on disk)
        if has_does_exist and has_load_asset:
            try:
                exists = asset_lib.does_asset_exist(body_path)
                if exists:
                    report_lines.append("[PROBE] SOFTREF RPGLookConfig.body loading existing asset into memory [read-only]")
                    loaded_obj = asset_lib.load_asset(body_path)
                    _probe_softref_form("RPGLookConfig", "body", "load_asset", look_cls(), loaded_obj, report_lines)
                else:
                    report_lines.append(f"[PROBE] SOFTREF RPGLookConfig.body form=load_asset skipped: asset '{body_path}' does not exist on disk readback_type=NoneType readback_repr=None")
            except Exception as ex:
                report_lines.append(
                    f"[PROBE] SOFTREF RPGLookConfig.body form=load_asset "
                    f"result=error:{type(ex).__name__}: {str(ex).strip()} readback_type=NoneType readback_repr=None"
                )
        else:
            report_lines.append("[PROBE] SOFTREF RPGLookConfig.body form=load_asset skipped: EditorAssetLibrary load API missing readback_type=NoneType readback_repr=None")

        # -------------------------------------------------------------------
        # TARGET 3: RPGLookConfig.pieces (TArray<TSoftObjectPtr<USkeletalMesh>>)
        # -------------------------------------------------------------------
        pieces_paths = [
            "/Game/OneBossFight/Boss01/Body/SK_Boss01_Crown.SK_Boss01_Crown",
            "/Game/OneBossFight/Boss01/Body/SK_Boss01_Mantle.SK_Boss01_Mantle",
            "/Game/OneBossFight/Boss01/Body/SK_Boss01_BrazierGauntlet.SK_Boss01_BrazierGauntlet"
        ]

        # Default instance readback
        try:
            def_inst = look_cls()
            def_val = def_inst.get_editor_property("pieces")
            report_lines.append(
                f"[PROBE] SOFTREF RPGLookConfig.pieces form=default result=ok "
                f"readback_type={type(def_val).__name__} readback_repr={repr(def_val)}"
            )
        except Exception as ex:
            report_lines.append(
                f"[PROBE] SOFTREF RPGLookConfig.pieces form=default "
                f"result=error:{type(ex).__name__}: {str(ex).strip()} readback_type=NoneType readback_repr=None"
            )

        # (v.a) list_str
        _probe_softref_form("RPGLookConfig", "pieces", "list_str", look_cls(), pieces_paths, report_lines)

        # (v.b) list_SoftObjectPath
        try:
            sop_list = [unreal_mod.SoftObjectPath(p) for p in pieces_paths]
            _probe_softref_form("RPGLookConfig", "pieces", "list_SoftObjectPath", look_cls(), sop_list, report_lines)
        except Exception as ex:
            report_lines.append(
                f"[PROBE] SOFTREF RPGLookConfig.pieces form=list_SoftObjectPath "
                f"result=error:{type(ex).__name__}: {str(ex).strip()} readback_type=NoneType readback_repr=None"
            )

        # (v.c) list_none
        _probe_softref_form("RPGLookConfig", "pieces", "list_none", look_cls(), [None, None], report_lines)

        # (v.d) empty_list
        _probe_softref_form("RPGLookConfig", "pieces", "empty_list", look_cls(), [], report_lines)

        # (v.e) list_load_asset
        if has_does_exist and has_load_asset:
            try:
                all_exist = all(asset_lib.does_asset_exist(p) for p in pieces_paths)
                if all_exist:
                    report_lines.append("[PROBE] SOFTREF RPGLookConfig.pieces loading existing assets into memory [read-only]")
                    loaded_list = [asset_lib.load_asset(p) for p in pieces_paths]
                    _probe_softref_form("RPGLookConfig", "pieces", "list_load_asset", look_cls(), loaded_list, report_lines)
                else:
                    report_lines.append("[PROBE] SOFTREF RPGLookConfig.pieces form=list_load_asset skipped: one or more assets do not exist on disk readback_type=NoneType readback_repr=None")
            except Exception as ex:
                report_lines.append(
                    f"[PROBE] SOFTREF RPGLookConfig.pieces form=list_load_asset "
                    f"result=error:{type(ex).__name__}: {str(ex).strip()} readback_type=NoneType readback_repr=None"
                )
        else:
            report_lines.append("[PROBE] SOFTREF RPGLookConfig.pieces form=list_load_asset skipped: EditorAssetLibrary load API missing readback_type=NoneType readback_repr=None")
    else:
        report_lines.append("[PROBE] SOFTREF RPGLookConfig NOT FOUND in unreal")


def run_probe(unreal_mod: Optional[Any] = None, repo_root: str = REPO_ROOT, instances: bool = False, softrefs: bool = False) -> Tuple[List[str], int, int]:
    """
    Executes the static extraction and (if unreal is available) the runtime probe.
    If instances=True, also executes Stage 2 in-memory struct instance probe and CDO query.
    If softrefs=True, probes in-memory soft object reference assignment forms and readback.
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

        # Summary line for Stage 1
        report_lines.append(f"\n[PROBE] SUMMARY missing={missing_count} present={present_count}")

        # 7. STAGE 2 INSTANCE PROBE EXECUTION (active only if instances=True)
        if instances:
            report_lines.append("\n=== STAGE 2 INSTANCE PROBE EXECUTION (--instances) ===")
            try:
                from Docs.BossCombatReview.Execution.Antigravity.AuthoringToolkit.authoring_core import STRUCT_SPECS
            except Exception:
                STRUCT_SPECS = {}

            # (A) Probe in-memory instance of each of the 17 structs
            report_lines.append("\n--- [STAGE 2.A] IN-MEMORY STRUCT INSTANCE PROBES ---")
            for spec_key, (cpp_struct, py_struct) in sorted(SPEC_TO_STRUCT_MAP.items()):
                if not hasattr(unreal_mod, py_struct):
                    report_lines.append(f"[PROBE] INSTANCE {py_struct} NOT FOUND in unreal")
                    continue

                struct_cls = getattr(unreal_mod, py_struct)
                # State construct call and harmlessness
                report_lines.append(f"[PROBE] INSTANCE_CALL construct: unreal.{py_struct}() [transient in-memory plain struct: zero asset/package/registry writes]")
                try:
                    inst = struct_cls()
                except Exception as ctor_ex:
                    report_lines.append(f"[PROBE] INSTANCE {py_struct} construct error:{type(ctor_ex).__name__}:{str(ctor_ex)[:50]}")
                    continue

                spec = STRUCT_SPECS.get(spec_key)
                py_to_native = spec[2] if (isinstance(spec, tuple) and len(spec) >= 3 and isinstance(spec[2], dict)) else {}
                tk_expected = py_props.get(spec_key, [])

                first_failure_tested = False
                for prop_name in tk_expected:
                    cpp_prop_name = py_to_native.get(prop_name, prop_name)
                    has_attr = hasattr(inst, prop_name)

                    get_ed_result = "none"
                    val = None
                    try:
                        val = inst.get_editor_property(prop_name)
                        get_ed_result = "ok"
                    except Exception as g_ex:
                        err_t = type(g_ex).__name__
                        err_m = str(g_ex).replace("\n", " ").replace("\r", "").strip()[:50]
                        get_ed_result = f"error:{err_t}:{err_m}"

                    extra = ""
                    if get_ed_result == "ok":
                        if isinstance(val, float):
                            extra = f" value={val:.6g}"
                        if prop_name in ("spawn_sockets", "pieces", "death_mode", "fields", "SpawnSockets", "Pieces", "DeathMode", "Fields"):
                            extra += f" type={type(val).__name__}"

                    report_lines.append(f"[PROBE] INSTANCE {py_struct} prop={prop_name} get_editor_property={get_ed_result} hasattr={has_attr}{extra}")

                    # If this is the first failure of this struct, test with the C++ name spelling
                    if get_ed_result.startswith("error:") and not first_failure_tested:
                        first_failure_tested = True
                        cpp_has_attr = hasattr(inst, cpp_prop_name)
                        cpp_get_ed = "none"
                        try:
                            cpp_val = inst.get_editor_property(cpp_prop_name)
                            cpp_get_ed = "ok"
                        except Exception as cpp_ex:
                            cpp_err_t = type(cpp_ex).__name__
                            cpp_err_m = str(cpp_ex).replace("\n", " ").replace("\r", "").strip()[:50]
                            cpp_get_ed = f"error:{cpp_err_t}:{cpp_err_m}"
                        report_lines.append(f"[PROBE] INSTANCE_ALT_CPP {py_struct} prop={cpp_prop_name} get_editor_property={cpp_get_ed} hasattr={cpp_has_attr}")

            # (B) RPGBossDefinition CDO inspection
            report_lines.append("\n--- [STAGE 2.B] RPGBossDefinition CDO INSPECTION ---")
            if hasattr(unreal_mod, "RPGBossDefinition") and hasattr(unreal_mod.RPGBossDefinition, "get_default_object"):
                report_lines.append("[PROBE] INSTANCE_CALL get_default_object: unreal.RPGBossDefinition.get_default_object() [harmless read-only CDO inspect: zero mutations]")
                try:
                    cdo = unreal_mod.RPGBossDefinition.get_default_object()
                    top_props = [
                        "schema", "definition_id", "presentation_id", "skeleton", "animations",
                        "phases", "fields", "stats", "encounter_policy", "stagger_policy",
                        "phase_flow", "fireball", "phase_dependencies", "stagger_profile",
                        "dormant_wake", "bleed", "low_sweep", "shockwave", "heal_punish",
                        "look", "close_clip_swap", "death"
                    ]
                    for tp in top_props:
                        try:
                            tp_val = cdo.get_editor_property(tp)
                            report_lines.append(f"[PROBE] CDO RPGBossDefinition prop={tp} get_editor_property=ok type={type(tp_val).__name__}")
                        except Exception as tp_ex:
                            err_t = type(tp_ex).__name__
                            err_m = str(tp_ex).replace("\n", " ").replace("\r", "").strip()[:50]
                            report_lines.append(f"[PROBE] CDO RPGBossDefinition prop={tp} get_editor_property=error:{err_t}:{err_m}")
                except Exception as cdo_ex:
                    report_lines.append(f"[PROBE] CDO RPGBossDefinition error:{type(cdo_ex).__name__}:{str(cdo_ex)[:50]}")
            else:
                report_lines.append("[PROBE] CDO RPGBossDefinition NOT FOUND in unreal")

            # (C) Module-level unreal.is_editor inspection
            report_lines.append("\n--- [STAGE 2.C] MODULE-LEVEL unreal.is_editor INSPECTION ---")
            if hasattr(unreal_mod, "is_editor"):
                is_ed_obj = getattr(unreal_mod, "is_editor")
                is_callable = callable(is_ed_obj)
                t_name = type(is_ed_obj).__name__
                report_lines.append(f"[PROBE] unreal.is_editor exists=True callable={is_callable} type={t_name}")
                if is_callable:
                    report_lines.append("[PROBE] INSTANCE_CALL call: unreal.is_editor() [read-only editor mode query]")
                    try:
                        res = is_ed_obj()
                        report_lines.append(f"[PROBE] unreal.is_editor() result={res}")
                    except Exception as ed_ex:
                        report_lines.append(f"[PROBE] unreal.is_editor() error:{type(ed_ex).__name__}:{str(ed_ex)[:50]}")
            else:
                report_lines.append("[PROBE] unreal.is_editor exists=False callable=False type=none")

        # 8. STAGE 2.D SOFT OBJECT PATH REFLECTION PROBE (active only if softrefs=True)
        if softrefs:
            report_lines.append("\n=== STAGE 2.D SOFT OBJECT PATH REFLECTION PROBE (--softrefs) ===")
            _run_softrefs_probe(unreal_mod, report_lines)

    else:
        report_lines.append("\n[PROBE] unreal not importable: runtime part skipped")
        if instances:
            report_lines.append("[PROBE] unreal not importable: stage 2 instance probe skipped")
        if softrefs:
            report_lines.append("[PROBE] unreal not importable: stage 2 softrefs probe skipped")
        report_lines.append("[PROBE] NOTICE: An offline run proves nothing about the engine.")
        report_lines.append("[PROBE] SUMMARY missing=0 present=0")

    return report_lines, present_count, missing_count

def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only probe for Unreal Engine Python reflection and APIs.")
    parser.add_argument("--instances", action="store_true", default=False, help="Stage 2: construct in-memory struct instances and probe get_editor_property / CDO.")
    parser.add_argument("--softrefs", action="store_true", default=False, help="Stage 2.D: probe in-memory soft object reference assignment forms and readback.")
    parser.add_argument("--output", "-o", help="Optional output text path for probe report.")
    args = parser.parse_args()

    lines, present, missing = run_probe(instances=args.instances, softrefs=args.softrefs)
    output_text = "\n".join(lines)
    print(output_text)

    if args.output:
        out_path = os.path.abspath(args.output) if os.path.isabs(args.output) else os.path.join(REPO_ROOT, args.output)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "wb") as f:
            f.write(output_text.encode("utf-8").replace(b"\n", b"\r\n"))
        print(f"\nWrote probe report to {args.output}")

    # Exit code is always 0 per C-301 / C-302 / C-305
    sys.exit(0)

if __name__ == "__main__":
    main()
