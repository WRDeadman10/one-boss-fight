#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
inspect_authored_assets.py
==========================
Read-only Unreal Editor Python inspector and JSON exporter for authored OneBossFight
Data Assets (AG-CONTENT04 / Part C).

Security & Integrity Guards:
    1. Strictly Read-Only: Contains ZERO calls to set_editor_property, create_asset,
       duplicate_asset, save_loaded_asset, or delete_asset.
    2. Authorized Input Paths Only: Rejects paths outside project-owned /Game/OneBossFight/Data/.
    3. Strict Fail-Closed Editor Guard: Requires all editor APIs and non-PIE mode before inspection.
    4. Non-Intrusive Invariant: Compares package dirty states before and after inspection to
       guarantee zero source dirtiness is introduced.
    5. Exact Typed Class Verification: Identifies and verifies URPGCombatCatalog,
       URPGBuildDefinition, URPGWeaponDefinition, and URPGBossDefinition.
    6. Complete Typed Snapshots: Exports full reflected typed properties for all asset classes,
       including boss stats, encounter policy, stagger policy, phase flow, fireball, dependencies,
       stagger profile, dormant wake, phases, and parity fields.
    7. Fail-Closed Error Reporting: Fails closed with non-zero CLI exit code if any asset is missing,
       unloadable, has unrecognized structure, or if package dirty drift occurs.
    8. Offline Float64 Qualification: All offline tests and validators run in CPython float64,
       which does NOT certify native float32 conversion or input-mode parity. The authoring toolkit
       uses struct.pack('f') / struct.unpack('f') to simulate native float32 truncation and verify
       that valid float32 values survive round-trip, but offline execution does not execute native
       UE5.5 C++ serialization, memory layouts, or input-mode controller parity.
"""

import sys
import os
import argparse
import json
from typing import Dict, List, Tuple, Any, Optional

# ---------------------------------------------------------------------------
# Deterministic Import of Shared Authoring Core
# ---------------------------------------------------------------------------
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from authoring_core import (
    CLASS_CATALOG_PATH,
    CLASS_BUILD_DEF_PATH,
    CLASS_WEAPON_DEF_PATH,
    CLASS_BOSS_DEF_PATH,
    validate_package_path,
    exact_fname_equal,
    pythonize_property_name,
)

# ---------------------------------------------------------------------------
# Unreal Module Import Handling (Safe for Offline Compilation & Inspection)
# ---------------------------------------------------------------------------
try:
    import unreal
    HAS_UNREAL = True
except ImportError:
    unreal = None
    HAS_UNREAL = False

ALLOWED_INPUT_ROOTS = (
    "/Game/OneBossFight/Data/Catalog/",
    "/Game/OneBossFight/Data/TypedABIFixtures/"
)


# ---------------------------------------------------------------------------
# Strict Fail-Closed Editor Environment Guard
# ---------------------------------------------------------------------------
def verify_editor_environment() -> Tuple[bool, str]:
    """
    Strict fail-closed editor environment guard.
    Requires:
    1. HAS_UNREAL is True.
    2. unreal.SystemLibrary exists and has callable is_editor, and is_editor() is True.
    3. unreal.get_editor_subsystem exists and is callable.
    4. unreal.UnrealEditorSubsystem exists.
    5. unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem) returns non-null subsystem.
    6. editor_subsystem has callable get_game_world, and get_game_world() is None (not in PIE).
    Absence of ANY required API fails closed immediately.
    """
    if not HAS_UNREAL or unreal is None:
        return False, "Unreal module not available (running in pure offline Python)"

    # 1. SystemLibrary.is_editor check
    if not hasattr(unreal, "SystemLibrary"):
        return False, "Missing required Unreal API: unreal.SystemLibrary"
    system_lib = getattr(unreal, "SystemLibrary")
    if not hasattr(system_lib, "is_editor") or not callable(getattr(system_lib, "is_editor")):
        return False, "Missing required Unreal API: unreal.SystemLibrary.is_editor"
    try:
        if not system_lib.is_editor():
            return False, "Not running in Unreal Editor environment (is_editor() == False)"
    except Exception as ex:
        return False, f"Failed executing unreal.SystemLibrary.is_editor(): {str(ex)}"

    # 2. UnrealEditorSubsystem and non-PIE check
    if not hasattr(unreal, "get_editor_subsystem") or not callable(getattr(unreal, "get_editor_subsystem")):
        return False, "Missing required Unreal API: unreal.get_editor_subsystem"
    if not hasattr(unreal, "UnrealEditorSubsystem"):
        return False, "Missing required Unreal API: unreal.UnrealEditorSubsystem"

    try:
        subsystem_cls = getattr(unreal, "UnrealEditorSubsystem")
        editor_subsystem = unreal.get_editor_subsystem(subsystem_cls)
        if editor_subsystem is None:
            return False, "UnrealEditorSubsystem is not available (returned None)"
        if not hasattr(editor_subsystem, "get_game_world") or not callable(getattr(editor_subsystem, "get_game_world")):
            return False, "Missing required Unreal API: UnrealEditorSubsystem.get_game_world"
        game_world = editor_subsystem.get_game_world()
        if game_world is not None:
            return False, "Unreal Editor is running in PIE / Simulation mode. Execution prohibited."
    except Exception as ex:
        return False, f"Editor subsystem check failed: {str(ex)}"

    return True, ""


# ---------------------------------------------------------------------------
# Path & Boundary Validator
# ---------------------------------------------------------------------------
def validate_inspection_target_path(path: str) -> Tuple[bool, str]:
    if not isinstance(path, str) or not path:
        return False, "Target path is empty"
    if not any(path.startswith(root) for root in ALLOWED_INPUT_ROOTS):
        return False, f"Target path '{path}' is not within authorized project roots: {ALLOWED_INPUT_ROOTS}"
    if ".." in path or "//" in path or "\\" in path or ":" in path:
        return False, f"Non-canonical path rejected: '{path}'"
    return True, ""


# ---------------------------------------------------------------------------
# Struct Property Extraction Helpers (Safe for UE5.5 and Recording Fakes)
# ---------------------------------------------------------------------------
def _safe_str(val: Any) -> str:
    if val is None:
        return ""
    if hasattr(val, "to_string"):
        return str(val.to_string())
    return str(val)


def _extract_struct_dict(struct_obj: Any, field_names: List[str]) -> Dict[str, Any]:
    """Extracts typed struct fields whether backed by UStruct or python dict, respecting UE5.5 pythonized names."""
    result: Dict[str, Any] = {}
    if struct_obj is None:
        return result

    for f in field_names:
        is_b = f.startswith("b") and len(f) > 1 and f[1].isupper()
        py_attr = pythonize_property_name(f, is_bool=is_b)
        val = None

        if isinstance(struct_obj, dict):
            for key in (py_attr, f, f.lower()):
                if key in struct_obj:
                    val = struct_obj[key]
                    break
        else:
            for attr in (py_attr, f, f.lower()):
                if hasattr(struct_obj, "get_editor_property"):
                    try:
                        val = struct_obj.get_editor_property(attr)
                        break
                    except Exception:
                        pass
                if hasattr(struct_obj, attr):
                    val = getattr(struct_obj, attr)
                    break

        if val is not None:
            if hasattr(val, "x") and hasattr(val, "y"):
                val = [float(val.x), float(val.y)]
            elif hasattr(val, "to_string"):
                val = val.to_string()
            elif isinstance(val, (int, float, bool, str, list, dict)):
                pass
            else:
                val = str(val)
        result[f] = val
    return result


# ---------------------------------------------------------------------------
# Live Asset Inspection (Read-Only)
# ---------------------------------------------------------------------------
def inspect_single_asset_live(asset_path: str, inspect_deps: bool = False) -> Dict[str, Any]:
    """
    Inspects a single asset via Unreal Editor Python reflection. Zero mutations.
    """
    if not HAS_UNREAL or unreal is None:
        raise RuntimeError("Live inspection requires Unreal Editor Python environment.")

    result: Dict[str, Any] = {
        "asset_path": asset_path,
        "exists_on_disk": False,
        "package_loaded": False,
        "package_dirty": None,
        "class_name": "Unknown",
        "is_recognized_class": False,
        "properties": {},
        "dependencies": [],
        "errors": []
    }

    if not hasattr(unreal, "EditorAssetLibrary") or not hasattr(unreal.EditorAssetLibrary, "does_asset_exist"):
        result["errors"].append("Missing required Unreal API: unreal.EditorAssetLibrary.does_asset_exist")
        return result

    if not unreal.EditorAssetLibrary.does_asset_exist(asset_path):
        result["errors"].append(f"Asset does not exist on disk: '{asset_path}'")
        return result

    result["exists_on_disk"] = True
    if not hasattr(unreal, "load_package") or not callable(getattr(unreal, "load_package")):
        result["errors"].append("Missing required Unreal API: unreal.load_package")
        return result

    pkg = unreal.load_package(None, asset_path)
    if pkg is None:
        result["errors"].append(f"Failed to load package: '{asset_path}'")
        return result

    result["package_loaded"] = True
    result["package_dirty"] = pkg.is_dirty() if hasattr(pkg, "is_dirty") else False

    if not hasattr(unreal.EditorAssetLibrary, "load_asset"):
        result["errors"].append("Missing required Unreal API: unreal.EditorAssetLibrary.load_asset")
        return result

    asset_obj = unreal.EditorAssetLibrary.load_asset(asset_path)
    if not asset_obj:
        result["errors"].append(f"Failed to load asset object: '{asset_path}'")
        return result

    asset_class = asset_obj.get_class()
    class_path = asset_class.get_path_name() if asset_class else "None"
    result["class_name"] = class_path

    dep_paths: List[str] = []

    # 1. Catalog Class
    if class_path == CLASS_CATALOG_PATH:
        result["is_recognized_class"] = True
        result["properties"]["schema_version"] = int(asset_obj.get_editor_property("schema_version"))
        weapons = [_safe_str(w) for w in asset_obj.get_editor_property("weapons")]
        builds = [_safe_str(b) for b in asset_obj.get_editor_property("builds")]
        result["properties"]["weapons_count"] = len(weapons)
        result["properties"]["weapons"] = weapons
        result["properties"]["builds_count"] = len(builds)
        result["properties"]["builds"] = builds
        dep_paths = weapons + builds

    # 2. Build Definition Class
    elif class_path == CLASS_BUILD_DEF_PATH:
        result["is_recognized_class"] = True
        b_def = asset_obj.get_editor_property("definition")
        result["properties"]["build_id"] = _safe_str(b_def.get_editor_property("build_id"))
        result["properties"]["console_name"] = _safe_str(b_def.get_editor_property("console_name"))
        result["properties"]["aliases"] = [_safe_str(a) for a in b_def.get_editor_property("aliases")]
        result["properties"]["display_name"] = _safe_str(b_def.get_editor_property("display_name"))
        result["properties"]["ui_order"] = int(b_def.get_editor_property("ui_order"))
        result["properties"]["legacy_slot"] = int(b_def.get_editor_property("legacy_slot"))
        result["properties"]["weapon_id"] = _safe_str(b_def.get_editor_property("weapon_id"))
        dep_paths = []

    # 3. Weapon Definition Class
    elif class_path == CLASS_WEAPON_DEF_PATH:
        result["is_recognized_class"] = True
        w_def = asset_obj.get_editor_property("definition")
        result["properties"]["weapon_id"] = _safe_str(w_def.get_editor_property("weapon_id"))
        result["properties"]["style_name"] = _safe_str(w_def.get_editor_property("style_name"))
        item_path = _safe_str(w_def.get_editor_property("item_path"))
        result["properties"]["item_path"] = item_path
        result["properties"]["bRequireExactRows"] = bool(w_def.get_editor_property("b_require_exact_rows"))
        dep_paths = [item_path]

    # 4. Boss Definition Class (Complete Typed Snapshot)
    elif class_path == CLASS_BOSS_DEF_PATH:
        result["is_recognized_class"] = True
        result["properties"]["schema"] = int(asset_obj.get_editor_property("schema"))
        result["properties"]["definition_id"] = _safe_str(asset_obj.get_editor_property("definition_id"))
        result["properties"]["presentation_id"] = _safe_str(asset_obj.get_editor_property("presentation_id"))

        skel_str = _safe_str(asset_obj.get_editor_property("skeleton"))
        result["properties"]["skeleton"] = skel_str
        dep_paths = [skel_str] if skel_str else []

        anims_raw = asset_obj.get_editor_property("animations")
        anims_list = [_safe_str(a) for a in anims_raw] if anims_raw else []
        result["properties"]["animations_count"] = len(anims_list)
        result["properties"]["animations"] = anims_list
        dep_paths.extend(anims_list)

        # Full typed sub-struct snapshots
        stats_obj = asset_obj.get_editor_property("stats")
        result["properties"]["stats"] = _extract_struct_dict(stats_obj, [
            "MaxHealth", "MaxPosture", "PostureRegenDelay", "PostureRegenRate"
        ])

        enc_obj = asset_obj.get_editor_property("encounter_policy")
        result["properties"]["encounter_policy"] = _extract_struct_dict(enc_obj, [
            "GateRadius", "bResetOnPlayerRespawn"
        ])

        stg_obj = asset_obj.get_editor_property("stagger_policy")
        result["properties"]["stagger_policy"] = _extract_struct_dict(stg_obj, [
            "StaggerSeconds", "FreezeAtPosition", "CriticalMultiplier", "RiposteRange",
            "RiposteConeDegrees", "RiposteFacingDegrees", "RiposteArmSeconds",
            "RipostePlayerStartGap", "RiposteAlignSeconds", "RiposteImpactSeconds",
            "RiposteBaseDamage", "CooldownSeconds", "GetUpRate", "bHoldPostureAtZero"
        ])

        flow_obj = asset_obj.get_editor_property("phase_flow")
        result["properties"]["phase_flow"] = _extract_struct_dict(flow_obj, [
            "TransitionSeconds", "bUseRoarClip", "bPausePostureInTransition",
            "bLockLeapUntilPhaseTwo", "AttackAbilityPrefix", "LeapAbilityTag"
        ])

        fire_obj = asset_obj.get_editor_property("fireball")
        result["properties"]["fireball"] = _extract_struct_dict(fire_obj, [
            "bFireballEnabled", "FireballAbility", "FireballCooldown",
            "FireballMinRange", "FireballMaxRange"
        ])

        dep_obj = asset_obj.get_editor_property("phase_dependencies")
        result["properties"]["phase_dependencies"] = _extract_struct_dict(dep_obj, [
            "RoarClip", "TransitionMontage", "ImmunityEffect"
        ])

        stg_prof_obj = asset_obj.get_editor_property("stagger_profile")
        result["properties"]["stagger_profile"] = _extract_struct_dict(stg_prof_obj, [
            "bUseClips", "bUseRiposteClips", "bCriticalOnEveryHit", "HitStunAbilityClassName",
            "FallMontage", "GetUpMontage", "FallClip", "DownClip",
            "RipostePlayerClip", "RiposteBossClip", "ImmunityEffect"
        ])

        wake_obj = asset_obj.get_editor_property("dormant_wake")
        result["properties"]["dormant_wake"] = _extract_struct_dict(wake_obj, [
            "DormantClip", "WakeClip"
        ])

        # Bleed Status Policy Snapshot (DD19)
        bleed_obj = asset_obj.get_editor_property("bleed")
        result["properties"]["bleed"] = _extract_struct_dict(bleed_obj, [
            "InitialThreshold", "ThresholdIncrease", "ThresholdMax", "HpFraction",
            "EffectHeight", "ProcEffect", "ProcSound"
        ])

        # Low Sweep Profile Snapshot (DD20)
        low_sweep_obj = asset_obj.get_editor_property("low_sweep")
        result["properties"]["low_sweep"] = _extract_struct_dict(low_sweep_obj, [
            "bEnabled", "MoveId", "Damage", "Reach",
            "InnerRadius", "BladeHeight", "SweepFromDegrees", "SweepToDegrees"
        ])

        # Phases Array Snapshot
        phases_raw = asset_obj.get_editor_property("phases")
        phases_list: List[Dict[str, Any]] = []
        if phases_raw:
            for p in phases_raw:
                phases_list.append(_extract_struct_dict(p, [
                    "PhaseId", "EntryHealthFraction", "SpeedMultiplier",
                    "RateMultiplier", "AttackMultiplier"
                ]))
        result["properties"]["phases_count"] = len(phases_list)
        result["properties"]["phases"] = phases_list

        # Fields Manifest Snapshot
        fields_raw = asset_obj.get_editor_property("fields")
        fields_list: List[Dict[str, Any]] = []
        if fields_raw:
            for fld in fields_raw:
                fields_list.append(_extract_struct_dict(fld, [
                    "FieldPath", "Value", "Type", "Units", "SourcePath",
                    "SourceSHA256", "SourceSite", "Origin", "Precedence",
                    "Destination", "FirstRead", "Witness"
                ]))
        result["properties"]["fields_count"] = len(fields_list)
        result["properties"]["fields"] = fields_list

    else:
        result["is_recognized_class"] = False
        result["errors"].append(f"Unrecognized class '{class_path}'")
        dep_paths = []

    # Optional dependency inspection (read-only)
    if inspect_deps and dep_paths:
        for dp in dep_paths:
            if not dp or dp == "None":
                continue
            exists = unreal.EditorAssetLibrary.does_asset_exist(dp)
            result["dependencies"].append({
                "path": dp,
                "exists_on_disk": exists
            })

    return result


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Read-only inspector and JSON exporter for authored OneBossFight Data Assets."
    )
    parser.add_argument(
        "asset_paths",
        nargs="*",
        default=[
            "/Game/OneBossFight/Data/Catalog/DA_CombatCatalog",
            "/Game/OneBossFight/Data/Catalog/DA_Build_Starter",
            "/Game/OneBossFight/Data/Catalog/DA_Build_Strength",
            "/Game/OneBossFight/Data/Catalog/DA_Build_Dex",
            "/Game/OneBossFight/Data/Catalog/DA_Weapon_Claymore"
        ],
        help="One or more project-owned asset paths to inspect."
    )
    parser.add_argument(
        "--inspect-dependencies",
        action="store_true",
        help="Opt-in to inspect referenced dependencies (read-only existence check)."
    )
    parser.add_argument(
        "--export-file",
        type=str,
        default="",
        help="Optional file path to export JSON results. Must be inside AuthoringToolkit directory."
    )

    args = parser.parse_args()

    print("=" * 80)
    print("OneBossFight - Authored Asset Inspector (AG-CONTENT04 / Part C)")
    print(f"Environment: {'Unreal Editor Python Subsystem' if HAS_UNREAL else 'Pure Offline Python (Validation Mode)'}")
    print("=" * 80)

    # Validate all input paths
    validated_paths: List[str] = []
    path_errors: List[str] = []
    for p in args.asset_paths:
        p_ok, p_err = validate_inspection_target_path(p)
        if not p_ok:
            path_errors.append(p_err)
        else:
            validated_paths.append(p)

    if path_errors:
        print("[ERROR] Input path validation failed:")
        for e in path_errors:
            print(f"  - {e}")
        sys.exit(1)

    # Validate export file path if provided
    export_path_clean = ""
    if args.export_file:
        norm_export = os.path.normpath(os.path.abspath(args.export_file))
        norm_toolkit = os.path.normpath(_SCRIPT_DIR)
        if not norm_export.startswith(norm_toolkit):
            print(f"[ERROR] Export file '{args.export_file}' must reside inside '{_SCRIPT_DIR}'")
            sys.exit(1)
        export_path_clean = norm_export

    if not HAS_UNREAL:
        print("\n[INFO] Running outside Unreal Editor. Performing offline structural validation of target paths.")
        offline_summary = {
            "status": "OFFLINE_VALIDATION_ONLY",
            "validated_paths_count": len(validated_paths),
            "validated_paths": validated_paths,
            "inspect_dependencies_requested": args.inspect_dependencies,
            "note": "Live property reflection requires running inside the Unreal Editor Python environment."
        }
        print(json.dumps(offline_summary, indent=2))
        sys.exit(0)

    # Editor State & Non-PIE Check (Strict Fail Closed)
    env_ok, env_err = verify_editor_environment()
    if not env_ok:
        print(f"[FATAL] Editor environment check failed: {env_err}")
        sys.exit(1)

    # Pre-inspection package dirty snapshot
    initial_dirty_states: Dict[str, bool] = {}
    for target in validated_paths:
        pkg = unreal.load_package(None, target)
        if pkg is not None and hasattr(pkg, "is_dirty"):
            initial_dirty_states[target] = pkg.is_dirty()

    # Live Inspection Loop
    results: List[Dict[str, Any]] = []
    has_inspection_errors = False

    for target in validated_paths:
        asset_info = inspect_single_asset_live(target, inspect_deps=args.inspect_dependencies)
        results.append(asset_info)
        if asset_info.get("errors"):
            has_inspection_errors = True
        if not asset_info.get("exists_on_disk"):
            has_inspection_errors = True

    # Post-inspection package dirty comparison (Guarantee Zero Dirtiness)
    dirty_drift_detected = False
    for target, was_dirty in initial_dirty_states.items():
        pkg = unreal.load_package(None, target)
        now_dirty = pkg.is_dirty() if (pkg is not None and hasattr(pkg, "is_dirty")) else False
        if not was_dirty and now_dirty:
            print(f"[ERROR] Non-intrusive violation: Package '{target}' became dirty during inspection!")
            dirty_drift_detected = True

    if dirty_drift_detected:
        has_inspection_errors = True

    output_data = {
        "status": "INSPECTION_COMPLETE" if not has_inspection_errors else "INSPECTION_FAILED",
        "inspected_count": len(results),
        "zero_dirtiness_verified": not dirty_drift_detected,
        "results": results
    }

    formatted_json = json.dumps(output_data, indent=2)
    print("\n--- INSPECTION RESULTS ---")
    print(formatted_json)

    if export_path_clean:
        with open(export_path_clean, "w", encoding="utf-8") as f:
            f.write(formatted_json)
        print(f"\n[INFO] Successfully exported inspection results to: {export_path_clean}")

    if has_inspection_errors:
        print("\n[FATAL] Inspection completed with errors. Failing closed.")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
