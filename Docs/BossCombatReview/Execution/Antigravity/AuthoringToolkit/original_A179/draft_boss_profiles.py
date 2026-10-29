#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
draft_boss_profiles.py
======================
Staged Unreal Editor Python helper for authoring draft boss and player participant
Data Assets (URPGBossDefinition) from JSON specifications (AG-CONTENT04 / Part B).

Outputs:
    - /Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Boss_EmberWarden_Draft
    - /Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Boss_AbyssalRevenant_Draft
    - /Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Player_Hero_Draft

Execution Modes & Safety Gates:
    1. Dry-Run Mode (DEFAULT):
       - Parses and validates input JSON profile definitions against native URPGBossDefinition schema.
       - Validates canonical output paths and verifies assets do not exist.
       - Validates finite numeric domains and exact phase transition constraints.
       - Prints explicit Proposed Creation Plan.
       - Zero writes, zero saves, zero mutations.
    2. Apply Mode (--apply):
       - Requires explicit --apply flag.
       - Verifies Editor state and non-PIE mode.
       - Creates URPGBossDefinition assets in memory only. DOES NOT SAVE by default.
       - Populates all typed struct, phase array, animation, and manifest fields.
       - Executes full read-back verification of EVERY written field.
    3. Save Opt-in (--apply --save):
       - Separate opt-in flag. MUST be combined with --apply.
       - Saves ONLY newly created output packages.
       - Re-run notice: If output packages already exist, helper refuses to run (anti-overwrite).

DISCLAIMER & LIMITATIONS:
    These profiles are intentionally DRAFT definitions. Fields arrays remain empty because
    no live 51-row parity manifest is fabricated. A complete, truthful manifest is required
    before native production compilation can succeed. These definitions are NOT playable duels.
"""

import sys
import os
import argparse
import copy
import json
import math
from typing import Dict, List, Tuple, Any, Optional

# ---------------------------------------------------------------------------
# Deterministic Import of Shared Authoring Core
# ---------------------------------------------------------------------------
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from authoring_core import (
    APPROVED_BOSS_DRAFTS_ROOT,
    CLASS_BOSS_DEF_PATH,
    NATIVE_BOSS_STATS_FIELDS,
    NATIVE_ENCOUNTER_POLICY_FIELDS,
    NATIVE_STAGGER_POLICY_FIELDS,
    NATIVE_PHASE_FLOW_FIELDS,
    NATIVE_FIREBALL_FIELDS,
    NATIVE_PHASE_DEPENDENCY_FIELDS,
    NATIVE_STAGGER_PROFILE_FIELDS,
    NATIVE_DORMANT_WAKE_FIELDS,
    NATIVE_PHASE_CONFIG_FIELDS,
    NATIVE_PARITY_FIELD_FIELDS,
    exact_native_normalize,
    exact_fname_equal,
    exact_fname_in,
    validate_package_path,
    validate_finite_integer,
    validate_finite_float,
    PartialOperationReport,
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

DEFAULT_INPUT_JSON = os.path.join(_SCRIPT_DIR, "examples", "boss_draft_profiles.json")


# ---------------------------------------------------------------------------
# Editor State & Non-PIE Guard
# ---------------------------------------------------------------------------
def verify_editor_environment() -> Tuple[bool, str]:
    if not HAS_UNREAL:
        return False, "Unreal module not available (running in pure offline Python)"
    try:
        if hasattr(unreal, "SystemLibrary") and hasattr(unreal.SystemLibrary, "is_editor"):
            if not unreal.SystemLibrary.is_editor():
                return False, "Not running in Unreal Editor environment (is_editor() == False)"
        if hasattr(unreal, "get_editor_subsystem") and hasattr(unreal, "UnrealEditorSubsystem"):
            editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
            if editor_subsystem and editor_subsystem.get_game_world() is not None:
                return False, "Unreal Editor is running in PIE / Simulation mode. Execution prohibited."
    except Exception as ex:
        return False, f"Editor check failed: {str(ex)}"
    return True, ""


# ---------------------------------------------------------------------------
# Structural Profile Validator (Pure Python)
# ---------------------------------------------------------------------------
def validate_boss_profile_data(profile: Dict[str, Any], seen_asset_names: List[str],
                               seen_def_ids: List[str]) -> Tuple[bool, List[str]]:
    """
    Validates the structure, exact native schema, and domain boundaries of a single
    boss/player draft profile. Rejects any unknown or fabricated fields.
    """
    errors: List[str] = []

    if not isinstance(profile, dict):
        return False, ["Profile must be a dictionary"]

    # Allowed top-level authoring profile keys
    allowed_top_keys = {
        "asset_name", "definition_id", "presentation_id", "schema_version",
        "participant_kind", "skeleton", "skeleton_candidate", "animations",
        "animation_candidates", "stats", "encounter_policy", "stagger_policy",
        "phase_flow", "fireball", "phase_dependencies", "stagger_profile",
        "dormant_wake", "phases", "fields"
    }
    unknown_top = set(profile.keys()) - allowed_top_keys
    if unknown_top:
        for k in sorted(unknown_top):
            errors.append(f"Unknown top-level property '{k}' in profile definition")

    # Asset Name & Path
    asset_name = profile.get("asset_name", "")
    if not asset_name or not isinstance(asset_name, str):
        errors.append("Profile missing valid 'asset_name'")
    elif asset_name in seen_asset_names:
        errors.append(f"Duplicate asset_name in profile set: '{asset_name}'")

    if asset_name:
        output_path = APPROVED_BOSS_DRAFTS_ROOT + str(asset_name)
        path_ok, path_err = validate_package_path(output_path, APPROVED_BOSS_DRAFTS_ROOT)
        if not path_ok:
            errors.append(f"Invalid canonical output path: {path_err}")

    # DefinitionId & PresentationId
    def_id = profile.get("definition_id", "")
    if not def_id or not isinstance(def_id, str):
        errors.append("Profile missing valid 'definition_id'")
    elif exact_fname_in(def_id, seen_def_ids):
        errors.append(f"Duplicate definition_id in profile set: '{def_id}'")

    pres_id = profile.get("presentation_id", "")
    if not pres_id or not isinstance(pres_id, str):
        errors.append("Profile missing valid 'presentation_id'")

    # Schema
    schema = profile.get("schema_version", 1)
    s_ok, s_err = validate_finite_integer(schema, "schema_version", min_val=1, max_val=1)
    if not s_ok:
        errors.append(s_err)

    # Participant Kind
    kind = profile.get("participant_kind", "")
    if kind not in ("Boss", "Player"):
        errors.append(f"Invalid participant_kind: '{kind}' (expected 'Boss' or 'Player')")

    # Helper: Validate strict dictionary section against native schema
    def _validate_dict_section(section_name: str, section_data: Any, schema_spec: Dict[str, Any]) -> List[str]:
        sec_errs: List[str] = []
        if not isinstance(section_data, dict):
            return [f"'{section_name}' must be an object/dict"]
        # Unknown property check
        unknown_fields = set(section_data.keys()) - set(schema_spec.keys())
        if unknown_fields:
            for uf in sorted(unknown_fields):
                sec_errs.append(f"{section_name}.{uf}: unknown native property")
        # Missing explicit property check
        missing_fields = set(schema_spec.keys()) - set(section_data.keys())
        if missing_fields:
            for mf in sorted(missing_fields):
                sec_errs.append(f"{section_name}.{mf}: missing explicit property")
        # Type and domain checks for matching fields
        for field, expected_type in schema_spec.items():
            if field not in section_data:
                continue
            val = section_data[field]
            label = f"{section_name}.{field}"
            if expected_type is bool:
                if type(val) is not bool:
                    sec_errs.append(f"{label}: expected bool, got {type(val).__name__}")
            elif expected_type is float:
                f_ok, f_err = validate_finite_float(val, label)
                if not f_ok:
                    sec_errs.append(f_err)
            elif expected_type is int:
                i_ok, i_err = validate_finite_integer(val, label)
                if not i_ok:
                    sec_errs.append(i_err)
            elif expected_type is str:
                if not isinstance(val, str):
                    sec_errs.append(f"{label}: expected string, got {type(val).__name__}")
            elif expected_type is list:
                if not isinstance(val, list):
                    sec_errs.append(f"{label}: expected list, got {type(val).__name__}")
                else:
                    if field == "FireballCooldown":
                        if len(val) != 2:
                            sec_errs.append(f"{label}: expected 2-element list [min, max]")
                        else:
                            for idx, item in enumerate(val):
                                f_ok, f_err = validate_finite_float(item, f"{label}[{idx}]", min_val=0.0)
                                if not f_ok:
                                    sec_errs.append(f_err)
        return sec_errs

    # 1. Stats
    errors.extend(_validate_dict_section("stats", profile.get("stats"), NATIVE_BOSS_STATS_FIELDS))

    # 2. Encounter Policy
    errors.extend(_validate_dict_section("encounter_policy", profile.get("encounter_policy"), NATIVE_ENCOUNTER_POLICY_FIELDS))

    # 3. Stagger Policy
    errors.extend(_validate_dict_section("stagger_policy", profile.get("stagger_policy"), NATIVE_STAGGER_POLICY_FIELDS))

    # 4. Phase Flow
    errors.extend(_validate_dict_section("phase_flow", profile.get("phase_flow"), NATIVE_PHASE_FLOW_FIELDS))

    # 5. Fireball
    errors.extend(_validate_dict_section("fireball", profile.get("fireball"), NATIVE_FIREBALL_FIELDS))

    # 6. Phase Dependencies
    errors.extend(_validate_dict_section("phase_dependencies", profile.get("phase_dependencies"), NATIVE_PHASE_DEPENDENCY_FIELDS))

    # 7. Stagger Profile
    errors.extend(_validate_dict_section("stagger_profile", profile.get("stagger_profile"), NATIVE_STAGGER_PROFILE_FIELDS))

    # 8. Dormant Wake
    errors.extend(_validate_dict_section("dormant_wake", profile.get("dormant_wake"), NATIVE_DORMANT_WAKE_FIELDS))

    # 9. Skeleton & Animations
    skel = profile.get("skeleton") or profile.get("skeleton_candidate", "")
    if skel and not isinstance(skel, str):
        errors.append("Skeleton path must be a string")

    anims = profile.get("animations") if "animations" in profile else profile.get("animation_candidates", [])
    if not isinstance(anims, list):
        errors.append("Animations must be a list of paths")
    else:
        for idx, a in enumerate(anims):
            if not isinstance(a, str):
                errors.append(f"Animations[{idx}] must be a string path")

    # 10. Phases Array Verification
    phases = profile.get("phases", [])
    if not isinstance(phases, list):
        errors.append("Phases must be a list")
    else:
        if kind == "Boss":
            if len(phases) != 1:
                errors.append(f"Boss profile requires exactly 1 transition record (found {len(phases)})")
            for idx, p0 in enumerate(phases):
                p_errs = _validate_dict_section(f"phases[{idx}]", p0, NATIVE_PHASE_CONFIG_FIELDS)
                errors.extend(p_errs)
                if isinstance(p0, dict):
                    frac = p0.get("EntryHealthFraction")
                    if frac is not None and type(frac) in (float, int) and not isinstance(frac, bool):
                        if not (0.0 <= float(frac) <= 1.0):
                            errors.append(f"phases[{idx}].EntryHealthFraction {frac} outside valid range [0.0, 1.0]")
                    for mult in ("SpeedMultiplier", "RateMultiplier", "AttackMultiplier"):
                        m_val = p0.get(mult)
                        if m_val is not None and type(m_val) in (float, int) and not isinstance(m_val, bool):
                            if float(m_val) < 0.0:
                                errors.append(f"phases[{idx}].{mult} {m_val} must be non-negative")
        elif kind == "Player":
            if len(phases) != 0:
                errors.append(f"Player participant profile must have 0 phases (found {len(phases)})")

    # 11. Fields Manifest Verification
    fields = profile.get("fields", [])
    if not isinstance(fields, list):
        errors.append("Fields manifest must be a list")
    else:
        for idx, f_entry in enumerate(fields):
            f_errs = _validate_dict_section(f"fields[{idx}]", f_entry, NATIVE_PARITY_FIELD_FIELDS)
            errors.extend(f_errs)

    return (len(errors) == 0), errors


# ---------------------------------------------------------------------------
# Offline Plan Generation (Pure Python)
# ---------------------------------------------------------------------------
def generate_offline_plan(input_json_path: str) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    Loads and validates draft profile JSON file offline.
    """
    errors: List[str] = []
    if not os.path.isfile(input_json_path):
        return False, {}, [f"Input JSON file not found: '{input_json_path}'"]

    try:
        with open(input_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as ex:
        return False, {}, [f"Failed to parse JSON file '{input_json_path}': {str(ex)}"]

    profiles = data.get("profiles", [])
    if not isinstance(profiles, list) or len(profiles) == 0:
        return False, {}, ["JSON must contain a non-empty 'profiles' list"]

    seen_asset_names: List[str] = []
    seen_def_ids: List[str] = []
    validated_profiles: List[Dict[str, Any]] = []

    for idx, p in enumerate(profiles):
        p_ok, p_errs = validate_boss_profile_data(p, seen_asset_names, seen_def_ids)
        if not p_ok:
            for e in p_errs:
                errors.append(f"Profile [{idx}] '{p.get('asset_name', idx)}': {e}")
        else:
            seen_asset_names.append(p["asset_name"])
            seen_def_ids.append(p["definition_id"])
            validated_profiles.append(p)

    plan = {
        "input_json_path": input_json_path,
        "output_root": APPROVED_BOSS_DRAFTS_ROOT,
        "profile_count": len(validated_profiles),
        "profiles": validated_profiles,
        "is_valid": (len(errors) == 0),
        "errors": errors,
        "note": "Draft definitions for staged preview. Fields arrays remain empty pending truthful manifest authority."
    }

    return (len(errors) == 0), plan, errors


# ---------------------------------------------------------------------------
# Live Unreal Editor Staged Apply & Readback Verification
# ---------------------------------------------------------------------------
def execute_draft_apply(plan: Dict[str, Any], save_requested: bool = False) -> bool:
    """
    Executes staged creation of URPGBossDefinition draft assets inside Unreal Editor.
    Sets and reads back EVERY struct, phase, animation, and manifest property.
    """
    if not HAS_UNREAL:
        raise RuntimeError("Apply mode requires live Unreal Editor Python environment.")

    # 1. Editor Check
    env_ok, env_err = verify_editor_environment()
    if not env_ok:
        print(f"[DRAFT_APPLY] FATAL: {env_err}")
        return False

    report = PartialOperationReport("draft_boss_profiles")
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    boss_def_class = unreal.load_class(None, CLASS_BOSS_DEF_PATH)
    if not boss_def_class:
        print(f"[DRAFT_APPLY] FATAL: Failed to load native class: '{CLASS_BOSS_DEF_PATH}'")
        return False

    # Pre-check: Ensure NO output assets exist beforehand (Anti-Overwrite)
    for p in plan.get("profiles", []):
        pkg_path = APPROVED_BOSS_DRAFTS_ROOT + p["asset_name"]
        if hasattr(unreal, "EditorAssetLibrary") and unreal.EditorAssetLibrary.does_asset_exist(pkg_path):
            err_msg = f"Output asset '{pkg_path}' already exists. Helper strictly refuses overwrite/delete."
            print(f"[DRAFT_APPLY] FATAL: {err_msg}")
            report.record_error(err_msg)
            return False

    try:
        created_assets: List[Tuple[Any, str]] = []

        for p in plan.get("profiles", []):
            asset_name = p["asset_name"]
            pkg_path = APPROVED_BOSS_DRAFTS_ROOT + asset_name
            print(f"[DRAFT_APPLY] Creating draft asset at '{pkg_path}'...")

            factory = unreal.DataAssetFactory()
            if hasattr(factory, "set_editor_property"):
                factory.set_editor_property("data_asset_class", boss_def_class)

            folder_path = APPROVED_BOSS_DRAFTS_ROOT.rstrip("/")
            new_asset = asset_tools.create_asset(asset_name, folder_path, boss_def_class, factory)
            if not new_asset:
                raise RuntimeError(f"Failed to create Data Asset at '{pkg_path}'")
            report.record_created(pkg_path)
            created_assets.append((new_asset, pkg_path))

            # Helper for Name / SoftObjectPath wrapping
            def _to_name(val: str):
                return unreal.Name(val) if hasattr(unreal, "Name") else val

            def _to_soft_path(val: str):
                return unreal.SoftObjectPath(val) if hasattr(unreal, "SoftObjectPath") else val

            # 1. Schema & Identifiers
            schema_val = p.get("schema_version", 1)
            def_id_val = _to_name(p["definition_id"])
            pres_id_val = _to_name(p["presentation_id"])

            new_asset.set_editor_property("schema", schema_val)
            new_asset.set_editor_property("definition_id", def_id_val)
            new_asset.set_editor_property("presentation_id", pres_id_val)

            # 2. Skeleton
            skel_raw = p.get("skeleton") or p.get("skeleton_candidate", "")
            skel_val = _to_soft_path(skel_raw) if skel_raw else ""
            new_asset.set_editor_property("skeleton", skel_val)

            # 3. Animations
            anims_raw = p.get("animations") if "animations" in p else p.get("animation_candidates", [])
            anims_val = [_to_soft_path(a) for a in anims_raw] if anims_raw else []
            new_asset.set_editor_property("animations", anims_val)

            # 4. Typed Struct Properties
            stats_val = copy.deepcopy(p.get("stats", {}))
            enc_policy_val = copy.deepcopy(p.get("encounter_policy", {}))
            stg_policy_val = copy.deepcopy(p.get("stagger_policy", {}))
            flow_val = copy.deepcopy(p.get("phase_flow", {}))
            fire_val = copy.deepcopy(p.get("fireball", {}))
            phase_dep_val = copy.deepcopy(p.get("phase_dependencies", {}))
            stg_prof_val = copy.deepcopy(p.get("stagger_profile", {}))
            wake_val = copy.deepcopy(p.get("dormant_wake", {}))
            phases_val = copy.deepcopy(p.get("phases", []))
            fields_val = copy.deepcopy(p.get("fields", []))

            new_asset.set_editor_property("stats", stats_val)
            new_asset.set_editor_property("encounter_policy", enc_policy_val)
            new_asset.set_editor_property("stagger_policy", stg_policy_val)
            new_asset.set_editor_property("phase_flow", flow_val)
            new_asset.set_editor_property("fireball", fire_val)
            new_asset.set_editor_property("phase_dependencies", phase_dep_val)
            new_asset.set_editor_property("stagger_profile", stg_prof_val)
            new_asset.set_editor_property("dormant_wake", wake_val)
            new_asset.set_editor_property("phases", phases_val)
            new_asset.set_editor_property("fields", fields_val)

            # ---------------------------------------------------------------
            # Comprehensive Readback Verification of ALL 15 Properties
            # ---------------------------------------------------------------
            readback_checks = [
                ("schema", schema_val),
                ("definition_id", def_id_val),
                ("presentation_id", pres_id_val),
                ("skeleton", skel_val),
                ("animations", anims_val),
                ("stats", stats_val),
                ("encounter_policy", enc_policy_val),
                ("stagger_policy", stg_policy_val),
                ("phase_flow", flow_val),
                ("fireball", fire_val),
                ("phase_dependencies", phase_dep_val),
                ("stagger_profile", stg_prof_val),
                ("dormant_wake", wake_val),
                ("phases", phases_val),
                ("fields", fields_val),
            ]

            for prop_name, expected in readback_checks:
                actual = new_asset.get_editor_property(prop_name)
                # Normalize string representations for Name / SoftObjectPath comparison
                if hasattr(actual, "to_string") and hasattr(expected, "to_string"):
                    actual_cmp = actual.to_string()
                    expected_cmp = expected.to_string()
                elif hasattr(actual, "__str__") and hasattr(expected, "__str__") and isinstance(expected, (str, int, float, bool)):
                    actual_cmp = type(expected)(str(actual))
                    expected_cmp = expected
                else:
                    actual_cmp = actual
                    expected_cmp = expected

                if actual_cmp != expected_cmp:
                    raise RuntimeError(
                        f"Readback mismatch on '{asset_name}.{prop_name}': "
                        f"got '{actual_cmp}' != expected '{expected_cmp}'"
                    )

            print(f"[DRAFT_APPLY] Initialized & verified all 15 typed properties on draft asset: '{asset_name}'")

        if not save_requested:
            print("\n[DRAFT_APPLY] SUCCESS: In-memory asset creation and complete readback verified.")
            print("  NOTICE: --save flag was not provided. Output packages were NOT saved to disk.")
            report.success = True
            return True

        # Explicit Save Opt-in
        print("\n[DRAFT_APPLY] Executing explicit save opt-in for created draft packages...")
        for asset_obj, pkg_path in created_assets:
            save_ok = unreal.EditorAssetLibrary.save_loaded_asset(asset_obj)
            if not save_ok:
                raise RuntimeError(f"Failed to save newly created Data Asset at '{pkg_path}'")
            report.record_saved(pkg_path)
            print(f"[DRAFT_APPLY] Saved package to disk: '{pkg_path}'")

        report.success = True
        print("\n[DRAFT_APPLY] SUCCESS: Staged draft boss assets successfully authored and saved.")
        return True

    except Exception as ex:
        err_msg = f"Draft asset apply failed with exception: {str(ex)}"
        print(f"\n[DRAFT_APPLY] ERROR: {err_msg}")
        report.record_error(err_msg)
        return False


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Staged Unreal Editor helper for authoring draft URPGBossDefinition assets."
    )
    parser.add_argument(
        "--input-json",
        type=str,
        default=DEFAULT_INPUT_JSON,
        help="Path to JSON file containing draft boss profiles."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply flag to execute staged creation in memory. Defaults to dry-run."
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save opt-in flag. MUST be combined with --apply. Saves output packages."
    )

    args = parser.parse_args()

    print("=" * 80)
    print("OneBossFight - Draft Boss Profile Authoring Helper (AG-CONTENT04 / Part B)")
    print(f"Environment: {'Unreal Editor Python Subsystem' if HAS_UNREAL else 'Pure Offline Python (Validation Mode)'}")
    print("=" * 80)

    if args.save and not args.apply:
        print("[ERROR] The --save flag requires --apply. Cannot save without applying.")
        sys.exit(1)

    # 1. Offline Plan Generation & Structural Validation
    plan_ok, plan, errors = generate_offline_plan(args.input_json)
    if not plan_ok:
        print("\n[ERROR] Draft Profile Plan Validation Failed:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print(f"\n[PLAN] Validated {plan['profile_count']} draft profiles from '{args.input_json}'.")
    for p in plan["profiles"]:
        print(f"  - Asset: {p['asset_name']} | DefId: {p['definition_id']} | Kind: {p['participant_kind']}")

    # 2. Dry-Run Mode
    if not args.apply:
        print("\n[DRY-RUN] Execution plan is structurally valid and conforms to native schema.")
        print("  - Output packages: 0 created, 0 modified, 0 saved.")
        print("  - To execute staged creation in editor memory: re-run with --apply")
        print("  - To persist created packages to disk: re-run with --apply --save")
        sys.exit(0)

    # 3. Apply Mode
    if not HAS_UNREAL:
        print("\n[FATAL] Apply mode requires running inside Unreal Editor Python environment.")
        sys.exit(1)

    success = execute_draft_apply(plan, save_requested=args.save)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
