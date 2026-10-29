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
       - Enforces native capability and backend arithmetic constraints (health override > 1.0,
         damage scale floor >= 1.0, entry health fraction strictly above 0.0 and at most 1.0).
       - Validates canonical output paths and verifies assets do not exist.
       - Prints explicit Proposed Creation Plan.
       - Zero writes, zero saves, zero mutations.
    2. Apply Mode (--apply):
       - Requires explicit --apply flag.
       - Fail-closed editor environment guard: fails closed before ANY write if any required Unreal
         API or subsystem is missing or if in PIE mode.
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

OFFLINE FLOAT64 QUALIFICATION:
    All offline tests and validators run in CPython float64, which does NOT certify
    native float32 conversion or input-mode parity. The authoring toolkit uses
    struct.pack('f') / struct.unpack('f') to simulate native float32 truncation and verify
    that valid float32 values survive round-trip, but offline execution does not execute
    native UE5.5 C++ serialization, memory layouts, or input-mode controller parity.
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
    create_empty_struct_instance,
    APPROVED_BOSS_DRAFTS_ROOT,
    CLASS_BOSS_DEF_PATH,
    NATIVE_HEALTH_OVERRIDE_FLOOR,
    NATIVE_DAMAGE_SCALE_FLOOR,
    NATIVE_CRITICAL_MULTIPLIER_FLOOR,
    NATIVE_BOSS_STATS_FIELDS,
    NATIVE_ENCOUNTER_POLICY_FIELDS,
    NATIVE_STAGGER_POLICY_FIELDS,
    NATIVE_PHASE_FLOW_FIELDS,
    NATIVE_FIREBALL_FIELDS,
    NATIVE_PHASE_DEPENDENCY_FIELDS,
    NATIVE_STAGGER_PROFILE_FIELDS,
    NATIVE_DORMANT_WAKE_FIELDS,
    NATIVE_BLEED_FIELDS,
    NATIVE_LOW_SWEEP_FIELDS,
    NATIVE_PHASE_CONFIG_FIELDS,
    NATIVE_PARITY_FIELD_FIELDS,
    pythonize_property_name,
    map_native_dict_to_python_keys,
    extract_canonical_primitives,
    to_float32,
    normalize_native_expected_for_readback,
    validate_boss_stats_domain,
    validate_bleed_domain,
    validate_low_sweep_domain,
    NATIVE_SHOCKWAVE_FIELDS,
    SHOCKWAVE_NATIVE_TO_PY,
    validate_shockwave_domain,
    NATIVE_HEAL_PUNISH_FIELDS,
    HEAL_PUNISH_NATIVE_TO_PY,
    validate_heal_punish_domain,
    NATIVE_LOOK_FIELDS,
    LOOK_NATIVE_TO_PY,
    validate_look_domain,
    NATIVE_CLOSE_CLIP_SWAP_FIELDS,
    CLOSE_CLIP_SWAP_NATIVE_TO_PY,
    validate_close_clip_swap_domain,
    NATIVE_DEATH_FIELDS,
    DEATH_NATIVE_TO_PY,
    validate_death_domain,
    validate_encounter_policy_domain,
    validate_stagger_policy_domain,
    validate_phase_flow_domain,
    validate_fireball_domain,
    validate_phase_config_domain,
    exact_native_normalize,
    exact_fname_equal,
    exact_fname_in,
    validate_package_path,
    validate_finite_integer,
    validate_finite_float,
    PartialOperationReport,
    SPEC_TO_STRUCT_MAP,
    FNAME_PROPERTIES,
    to_soft_ref,
    to_fname,
    to_death_mode,
    convert_property_for_engine,
    create_struct_instance,
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
# Strict Fail-Closed Editor Environment Guard
# ---------------------------------------------------------------------------
def verify_editor_environment() -> Tuple[bool, str]:
    """
    Strict fail-closed editor environment guard.
    Requires:
    1. HAS_UNREAL is True.
    2. unreal.is_editor exists, is callable, and unreal.is_editor() is True (verified in DD27c).
    3. unreal.get_editor_subsystem exists and is callable.
    4. unreal.UnrealEditorSubsystem exists.
    5. unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem) returns non-null subsystem.
    6. editor_subsystem has callable get_game_world, and get_game_world() is None (not in PIE).
    Absence of ANY required API fails closed immediately.
    """
    if not HAS_UNREAL or unreal is None:
        return False, "Unreal module not available (running in pure offline Python)"

    # 1. Module-level unreal.is_editor check (callable, verified in DD27c)
    if not hasattr(unreal, "is_editor") or not callable(getattr(unreal, "is_editor")):
        return False, "Missing required Unreal API: unreal.is_editor"
    try:
        if not unreal.is_editor():
            return False, "Not running in Unreal Editor environment (is_editor() == False)"
    except Exception as ex:
        return False, f"Failed executing unreal.is_editor(): {str(ex)}"

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
# Structural Profile Validator (Pure Python)
# ---------------------------------------------------------------------------
def validate_boss_profile_data(profile: Dict[str, Any], seen_asset_names: List[str],
                               seen_def_ids: List[str]) -> Tuple[bool, List[str]]:
    """
    Validates the structure, exact native schema, and domain boundaries of a single
    boss/player draft profile. Enforces backend capability constraints from
    RPGBossPhaseAdapters.cpp and RPGBossStatsAdapters.cpp.
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
        "dormant_wake", "bleed", "low_sweep", "shockwave", "heal_punish", "look", "close_clip_swap", "death", "phases", "fields"
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

    # 1. Stats (RPGBossStatsAdapters.cpp:73-99: health floor > 1.0, posture > 0.0)
    stats_data = profile.get("stats")
    errors.extend(_validate_dict_section("stats", stats_data, NATIVE_BOSS_STATS_FIELDS))
    if isinstance(stats_data, dict):
        errors.extend(validate_boss_stats_domain(stats_data))

    # 2. Encounter Policy (RPGBossEncounterPolicyAdapters.cpp:57-65)
    enc_data = profile.get("encounter_policy")
    errors.extend(_validate_dict_section("encounter_policy", enc_data, NATIVE_ENCOUNTER_POLICY_FIELDS))
    if isinstance(enc_data, dict):
        errors.extend(validate_encounter_policy_domain(enc_data))

    # 3. Stagger Policy (RPGBossStaggerPolicyAdapters.h:20-28)
    stg_data = profile.get("stagger_policy")
    errors.extend(_validate_dict_section("stagger_policy", stg_data, NATIVE_STAGGER_POLICY_FIELDS))
    if isinstance(stg_data, dict):
        errors.extend(validate_stagger_policy_domain(stg_data))

    # 4. Phase Flow
    flow_data = profile.get("phase_flow")
    errors.extend(_validate_dict_section("phase_flow", flow_data, NATIVE_PHASE_FLOW_FIELDS))
    if isinstance(flow_data, dict):
        errors.extend(validate_phase_flow_domain(flow_data))

    # 5. Fireball
    fire_data = profile.get("fireball")
    errors.extend(_validate_dict_section("fireball", fire_data, NATIVE_FIREBALL_FIELDS))
    if isinstance(fire_data, dict):
        errors.extend(validate_fireball_domain(fire_data))

    # 6. Phase Dependencies
    errors.extend(_validate_dict_section("phase_dependencies", profile.get("phase_dependencies"), NATIVE_PHASE_DEPENDENCY_FIELDS))

    # 7. Stagger Profile
    errors.extend(_validate_dict_section("stagger_profile", profile.get("stagger_profile"), NATIVE_STAGGER_PROFILE_FIELDS))

    # 8. Dormant Wake
    errors.extend(_validate_dict_section("dormant_wake", profile.get("dormant_wake"), NATIVE_DORMANT_WAKE_FIELDS))

    # 8b. Bleed Status Policy (DD19)
    if "bleed" in profile:
        errors.extend(_validate_dict_section("bleed", profile.get("bleed"), NATIVE_BLEED_FIELDS))
        if isinstance(profile.get("bleed"), dict):
            errors.extend(validate_bleed_domain(profile["bleed"]))

    # 8c. Low Sweep Profile (DD20)
    if "low_sweep" in profile:
        errors.extend(_validate_dict_section("low_sweep", profile.get("low_sweep"), NATIVE_LOW_SWEEP_FIELDS))
        if isinstance(profile.get("low_sweep"), dict):
            errors.extend(validate_low_sweep_domain(profile["low_sweep"]))

    # 8d. Shockwave Profile (DD21)
    if "shockwave" in profile:
        errors.extend(_validate_dict_section("shockwave", profile.get("shockwave"), NATIVE_SHOCKWAVE_FIELDS))
        if isinstance(profile.get("shockwave"), dict):
            errors.extend(validate_shockwave_domain(profile["shockwave"]))

    # 8e. Heal Punish Profile (DD22)
    if "heal_punish" in profile:
        errors.extend(_validate_dict_section("heal_punish", profile.get("heal_punish"), NATIVE_HEAL_PUNISH_FIELDS))
        if isinstance(profile.get("heal_punish"), dict):
            errors.extend(validate_heal_punish_domain(profile["heal_punish"]))

    # 8f. Look Profile (DD23)
    if "look" in profile:
        errors.extend(_validate_dict_section("look", profile.get("look"), NATIVE_LOOK_FIELDS))
        if isinstance(profile.get("look"), dict):
            errors.extend(validate_look_domain(profile["look"]))

    # 8g. Close Clip Swap Profile (DD24)
    if "close_clip_swap" in profile:
        errors.extend(_validate_dict_section("close_clip_swap", profile.get("close_clip_swap"), NATIVE_CLOSE_CLIP_SWAP_FIELDS))
        if isinstance(profile.get("close_clip_swap"), dict):
            errors.extend(validate_close_clip_swap_domain(profile["close_clip_swap"]))

    # 8h. Death Profile (DD25)
    if "death" in profile:
        errors.extend(_validate_dict_section("death", profile.get("death"), NATIVE_DEATH_FIELDS))
        if isinstance(profile.get("death"), dict):
            errors.extend(validate_death_domain(profile["death"]))

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

    # 10. Phases Array Verification (RPGBossPhaseAdapters.cpp:115-154)
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
                    errors.extend(validate_phase_config_domain(p0, idx))
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
# Diagnostic Failure Collector (Order A-212 / Diagnostic In-Memory Mode)
# ---------------------------------------------------------------------------
def _extract_prop_val(struct_obj: Any, py_key: str) -> Any:
    """Extracts property value supporting real Unreal struct wrapper, dict, or test mock."""
    if hasattr(struct_obj, "get_editor_property") and callable(getattr(struct_obj, "get_editor_property")):
        return struct_obj.get_editor_property(py_key)
    if isinstance(struct_obj, dict):
        return struct_obj.get(py_key)
    if hasattr(struct_obj, py_key):
        return getattr(struct_obj, py_key)
    return None


class DiagnosticFailureCollector:
    """
    Collects all property assignment and readback failures during in-memory apply mode.
    In diagnostic mode (--apply without --save), does not stop at the first failure;
    records every failure, prints a complete summary table, and prints an untruncated
    diagnostic failure line for each failure before exiting nonzero.
    In save mode (--apply with --save), fails fast immediately upon the first failure.
    """
    def __init__(self, fail_fast: bool = False):
        self.fail_fast = fail_fast
        self.failures: List[Dict[str, Any]] = []

    def record_failure(self, asset: str, struct_or_section: str, property_name: str,
                       expected: Any, actual: Any, error_ex: Optional[Exception] = None,
                       mismatch_msg: str = "", step: str = ""):
        prop_label = property_name
        if prop_label in ("(constructor)", "constructor"):
            prop_label = step if step else "construct"
        elif step and prop_label in ("(set_editor_property)", "(get_editor_property)", "(array_set)"):
            prop_label = step

        entry = {
            "asset": asset,
            "section": struct_or_section,
            "property": prop_label,
            "step": step,
            "expected": expected,
            "actual_type": type(actual).__name__ if actual is not None else "NoneType",
            "actual_repr": repr(actual) if actual is not None else "None",
            "error_class": error_ex.__class__.__name__ if error_ex else "ReadbackMismatch",
            "error_message": str(error_ex) if error_ex else mismatch_msg,
        }
        self.failures.append(entry)
        if self.fail_fast:
            raise RuntimeError(
                f"Fail-fast failure on '{asset}.{struct_or_section}.{prop_label}': "
                f"{entry['error_class']}: {entry['error_message']} "
                f"(expected={expected!r}, actual={actual!r})"
            )

    @property
    def has_failures(self) -> bool:
        return len(self.failures) > 0

    def failure_count_for_asset(self, asset_name: str) -> int:
        return sum(1 for f in self.failures if f.get("asset") == asset_name)

    def print_summary_table(self):
        if not self.failures:
            return
        print("\n" + "=" * 90)
        print(f"[DIAGNOSTIC SUMMARY] Collected {len(self.failures)} failure(s) during in-memory apply:")
        print("=" * 90)
        fmt = "{:<26} {:<16} {:<18} {:<14} {:<12} {:<24} {:<26}"
        print(fmt.format("Asset", "Section", "Property", "Expected", "Actual Type", "Actual Repr", "Error"))
        print("-" * 136)
        for f in self.failures:
            print(fmt.format(
                str(f["asset"])[:25],
                str(f["section"])[:15],
                str(f["property"])[:17],
                str(f["expected"])[:13],
                str(f["actual_type"])[:11],
                str(f["actual_repr"])[:23],
                f"{f['error_class']}: {f['error_message']}"[:25]
            ))
        print("=" * 90)
        print("\n[DIAGNOSTIC SUMMARY DETAILS (UNTRUNCATED)]")
        for f in self.failures:
            print(
                f"[DRAFT_APPLY][FAILURE] {f['asset']} {f['section']} {f['property']} "
                f"expected={f['expected']!r} actual_type={f['actual_type']} "
                f"actual_repr={f['actual_repr']} exception={f['error_class']}: {f['error_message']}"
            )
        print("=" * 90 + "\n")


# ---------------------------------------------------------------------------
# Live Unreal Editor Staged Apply & Readback Verification
# ---------------------------------------------------------------------------
def execute_draft_apply(plan: Dict[str, Any], save_requested: bool = False) -> bool:
    """
    Executes staged creation of URPGBossDefinition draft assets inside Unreal Editor.
    Fails closed before ANY write if any required Unreal API is missing or if in PIE mode.
    Sets and reads back EVERY struct, phase, animation, and manifest property.
    In in-memory diagnostic mode (--apply without --save), collects ALL failures across
    properties/structs/assets and displays a diagnostic summary table before exiting nonzero.
    """
    if not HAS_UNREAL or unreal is None:
        raise RuntimeError("Apply mode requires live Unreal Editor Python environment.")

    # 1. Editor Check (Fail Closed)
    env_ok, env_err = verify_editor_environment()
    if not env_ok:
        print(f"[DRAFT_APPLY] FATAL: {env_err}")
        return False

    # 2. Strict API Availability Check (Fail Closed before ANY write)
    if not hasattr(unreal, "AssetToolsHelpers") or not hasattr(unreal.AssetToolsHelpers, "get_asset_tools"):
        print("[DRAFT_APPLY] FATAL: Missing required Unreal API: unreal.AssetToolsHelpers.get_asset_tools")
        return False
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    if asset_tools is None or not hasattr(asset_tools, "create_asset"):
        print("[DRAFT_APPLY] FATAL: AssetTools is not available or missing create_asset")
        return False

    if not hasattr(unreal, "EditorAssetLibrary") or not hasattr(unreal.EditorAssetLibrary, "does_asset_exist"):
        print("[DRAFT_APPLY] FATAL: Missing required Unreal API: unreal.EditorAssetLibrary.does_asset_exist")
        return False

    if not hasattr(unreal, "DataAssetFactory"):
        print("[DRAFT_APPLY] FATAL: Missing required Unreal API: unreal.DataAssetFactory")
        return False

    if not hasattr(unreal, "load_class") or not callable(getattr(unreal, "load_class")):
        print("[DRAFT_APPLY] FATAL: Missing required Unreal API: unreal.load_class")
        return False

    if not hasattr(unreal, "Name"):
        print("[DRAFT_APPLY] FATAL: Missing required Unreal API: unreal.Name")
        return False

    if not hasattr(unreal, "SoftObjectPath"):
        print("[DRAFT_APPLY] FATAL: Missing required Unreal API: unreal.SoftObjectPath")
        return False

    report = PartialOperationReport("draft_boss_profiles")
    boss_def_class = unreal.load_class(None, CLASS_BOSS_DEF_PATH)
    if not boss_def_class:
        print(f"[DRAFT_APPLY] FATAL: Failed to load native class: '{CLASS_BOSS_DEF_PATH}'")
        return False

    # Pre-check: Ensure NO output assets exist beforehand (Anti-Overwrite)
    for p in plan.get("profiles", []):
        pkg_path = APPROVED_BOSS_DRAFTS_ROOT + p["asset_name"]
        if unreal.EditorAssetLibrary.does_asset_exist(pkg_path):
            err_msg = f"Output asset '{pkg_path}' already exists. Helper strictly refuses overwrite/delete."
            print(f"[DRAFT_APPLY] FATAL: {err_msg}")
            report.record_error(err_msg)
            return False

    collector = DiagnosticFailureCollector(fail_fast=save_requested)
    ALWAYS_PRESENT_STRUCTS = {
        "stats", "encounter_policy", "stagger_policy", "phase_flow",
        "fireball", "phase_dependencies", "stagger_profile", "dormant_wake"
    }

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

            # ---------------------------------------------------------------
            # 1. Schema & Identifiers (Top-Level)
            # ---------------------------------------------------------------
            schema_val = p.get("schema_version", 1)
            try:
                new_asset.set_editor_property("schema", schema_val)
                actual_schema = new_asset.get_editor_property("schema")
                if int(actual_schema) != schema_val:
                    collector.record_failure(asset_name, "top", "schema", schema_val, actual_schema, mismatch_msg=f"got {actual_schema} != {schema_val}")
            except Exception as ex:
                collector.record_failure(asset_name, "top", "schema", schema_val, None, error_ex=ex)

            try:
                def_id_val, _ = to_fname(p["definition_id"], unreal)
                new_asset.set_editor_property("definition_id", def_id_val)
                actual_def = new_asset.get_editor_property("definition_id")
                actual_def_str = str(actual_def.to_string()) if hasattr(actual_def, "to_string") else str(actual_def)
                if actual_def_str != p["definition_id"]:
                    collector.record_failure(asset_name, "top", "definition_id", p["definition_id"], actual_def, mismatch_msg=f"got '{actual_def_str}' != '{p['definition_id']}'")
            except Exception as ex:
                collector.record_failure(asset_name, "top", "definition_id", p["definition_id"], None, error_ex=ex)

            try:
                pres_id_val, _ = to_fname(p["presentation_id"], unreal)
                new_asset.set_editor_property("presentation_id", pres_id_val)
                actual_pres = new_asset.get_editor_property("presentation_id")
                actual_pres_str = str(actual_pres.to_string()) if hasattr(actual_pres, "to_string") else str(actual_pres)
                if actual_pres_str != p["presentation_id"]:
                    collector.record_failure(asset_name, "top", "presentation_id", p["presentation_id"], actual_pres, mismatch_msg=f"got '{actual_pres_str}' != '{p['presentation_id']}'")
            except Exception as ex:
                collector.record_failure(asset_name, "top", "presentation_id", p["presentation_id"], None, error_ex=ex)

            # ---------------------------------------------------------------
            # 2. Skeleton & Animations (Top-Level Soft Object References)
            # ---------------------------------------------------------------
            skel_raw = p.get("skeleton") or p.get("skeleton_candidate", "")
            try:
                skel_val, _ = to_soft_ref(skel_raw, unreal)
                new_asset.set_editor_property("skeleton", skel_val)
                actual_skel = new_asset.get_editor_property("skeleton")
                actual_skel_str = str(actual_skel.to_string()) if hasattr(actual_skel, "to_string") else str(actual_skel)
                if actual_skel_str != (skel_raw or ""):
                    collector.record_failure(asset_name, "top", "skeleton", skel_raw or "", actual_skel, mismatch_msg=f"got '{actual_skel_str}' != '{skel_raw}'")
            except Exception as ex:
                collector.record_failure(asset_name, "top", "skeleton", skel_raw or "", None, error_ex=ex)

            anims_raw = p.get("animations") if "animations" in p else p.get("animation_candidates", [])
            try:
                anims_val = [to_soft_ref(a, unreal)[0] for a in anims_raw] if anims_raw else []
                new_asset.set_editor_property("animations", anims_val)
                actual_anims = new_asset.get_editor_property("animations")
                actual_anims_list = [str(a.to_string()) if hasattr(a, "to_string") else str(a) for a in (actual_anims or [])]
                if actual_anims_list != (anims_raw or []):
                    collector.record_failure(asset_name, "top", "animations", anims_raw or [], actual_anims, mismatch_msg=f"got {actual_anims_list} != {anims_raw}")
            except Exception as ex:
                collector.record_failure(asset_name, "top", "animations", anims_raw or [], None, error_ex=ex)

            # ---------------------------------------------------------------
            # 3. Typed Struct Properties (Real UStruct Instances per A-212)
            # ---------------------------------------------------------------
            struct_specs = [
                ("stats", NATIVE_BOSS_STATS_FIELDS, p.get("stats", {})),
                ("encounter_policy", NATIVE_ENCOUNTER_POLICY_FIELDS, p.get("encounter_policy", {})),
                ("stagger_policy", NATIVE_STAGGER_POLICY_FIELDS, p.get("stagger_policy", {})),
                ("phase_flow", NATIVE_PHASE_FLOW_FIELDS, p.get("phase_flow", {})),
                ("fireball", NATIVE_FIREBALL_FIELDS, p.get("fireball", {})),
                ("phase_dependencies", NATIVE_PHASE_DEPENDENCY_FIELDS, p.get("phase_dependencies", {})),
                ("stagger_profile", NATIVE_STAGGER_PROFILE_FIELDS, p.get("stagger_profile", {})),
                ("dormant_wake", NATIVE_DORMANT_WAKE_FIELDS, p.get("dormant_wake", {})),
                ("bleed", NATIVE_BLEED_FIELDS, p.get("bleed", {})),
                ("low_sweep", NATIVE_LOW_SWEEP_FIELDS, p.get("low_sweep", {})),
                ("shockwave", NATIVE_SHOCKWAVE_FIELDS, p.get("shockwave", {})),
                ("heal_punish", NATIVE_HEAL_PUNISH_FIELDS, p.get("heal_punish", {})),
                ("look", NATIVE_LOOK_FIELDS, p.get("look", {})),
                ("close_clip_swap", NATIVE_CLOSE_CLIP_SWAP_FIELDS, p.get("close_clip_swap", {})),
                ("death", NATIVE_DEATH_FIELDS, p.get("death", {})),
            ]

            verified_struct_count = 0
            for section_name, field_spec, raw_data in struct_specs:
                if not raw_data and section_name not in ALWAYS_PRESENT_STRUCTS:
                    continue

                struct_had_property_failure = False

                # 1. Step: construct empty UStruct wrapper via default constructor
                try:
                    struct_inst = create_empty_struct_instance(section_name, unreal)
                except Exception as ex:
                    collector.record_failure(asset_name, section_name, "construct", "struct instance", None, error_ex=ex, step="construct")
                    continue

                # 2. Step: convert & set_editor_property per property on struct instance
                for native_k, expected_type in field_spec.items():
                    py_k = pythonize_property_name(native_k)
                    if native_k in raw_data:
                        raw_val = raw_data[native_k]
                        try:
                            converted_val, _ = convert_property_for_engine(native_k, raw_val, expected_type, unreal)
                        except Exception as ex:
                            collector.record_failure(asset_name, section_name, py_k, raw_val, None, error_ex=ex, step="convert")
                            struct_had_property_failure = True
                            continue

                        try:
                            if hasattr(struct_inst, "set_editor_property") and callable(getattr(struct_inst, "set_editor_property")):
                                struct_inst.set_editor_property(py_k, converted_val)
                            elif isinstance(struct_inst, dict):
                                struct_inst[py_k] = converted_val
                            else:
                                setattr(struct_inst, py_k, converted_val)
                        except Exception as ex:
                            collector.record_failure(asset_name, section_name, py_k, raw_val, None, error_ex=ex, step="set_editor_property")
                            struct_had_property_failure = True
                            continue

                # 3. Step: set_editor_property on top-level asset
                try:
                    new_asset.set_editor_property(section_name, struct_inst)
                except Exception as ex:
                    collector.record_failure(asset_name, section_name, "set_editor_property", "assigned", None, error_ex=ex, step="set_editor_property")
                    continue

                # 4. Step: get_editor_property (readback) from top-level asset
                try:
                    actual_struct = new_asset.get_editor_property(section_name)
                except Exception as ex:
                    collector.record_failure(asset_name, section_name, "readback", "readback", None, error_ex=ex, step="readback")
                    continue

                # 5. Step: readback verification per property
                expected_norm = normalize_native_expected_for_readback(raw_data, field_spec)
                for native_k, expected_type in field_spec.items():
                    py_k = pythonize_property_name(native_k)
                    expected_v = expected_norm.get(native_k)
                    try:
                        actual_v = _extract_prop_val(actual_struct, py_k)

                        single_canonical = extract_canonical_primitives(
                            {py_k: actual_v} if isinstance(actual_struct, dict) else actual_struct,
                            {native_k: expected_type}
                        )
                        actual_canon = single_canonical.get(native_k)

                        if actual_canon != expected_v:
                            collector.record_failure(
                                asset_name, section_name, py_k, expected_v, actual_v,
                                mismatch_msg=f"got {actual_canon!r} != {expected_v!r} (type={type(actual_v).__name__})",
                                step="readback"
                            )
                            struct_had_property_failure = True
                    except Exception as ex:
                        collector.record_failure(asset_name, section_name, py_k, expected_v, None, error_ex=ex, step="readback")
                        struct_had_property_failure = True

                if not struct_had_property_failure:
                    verified_struct_count += 1

            # ---------------------------------------------------------------
            # 4. Phase Array (List of RPGPhaseConfig Instances)
            # ---------------------------------------------------------------
            phases_raw = p.get("phases", [])
            try:
                phase_instances = []
                for idx, ph in enumerate(phases_raw):
                    ph_inst = create_empty_struct_instance("phases", unreal)
                    for native_k, expected_type in NATIVE_PHASE_CONFIG_FIELDS.items():
                        py_k = pythonize_property_name(native_k)
                        if native_k in ph:
                            raw_val = ph[native_k]
                            try:
                                converted_val, _ = convert_property_for_engine(native_k, raw_val, expected_type, unreal)
                            except Exception as ex:
                                collector.record_failure(asset_name, f"phases[{idx}]", py_k, raw_val, None, error_ex=ex, step="convert")
                                continue
                            try:
                                if hasattr(ph_inst, "set_editor_property") and callable(getattr(ph_inst, "set_editor_property")):
                                    ph_inst.set_editor_property(py_k, converted_val)
                                elif isinstance(ph_inst, dict):
                                    ph_inst[py_k] = converted_val
                                else:
                                    setattr(ph_inst, py_k, converted_val)
                            except Exception as ex:
                                collector.record_failure(asset_name, f"phases[{idx}]", py_k, raw_val, None, error_ex=ex, step="set_editor_property")
                    phase_instances.append(ph_inst)

                new_asset.set_editor_property("phases", phase_instances)
                actual_phases_raw = new_asset.get_editor_property("phases") or []
                if len(actual_phases_raw) != len(phases_raw):
                    collector.record_failure(asset_name, "phases", "count", len(phases_raw), len(actual_phases_raw), mismatch_msg=f"Count mismatch {len(actual_phases_raw)} != {len(phases_raw)}", step="readback")
                else:
                    for idx, (ph_expected_raw, ph_actual) in enumerate(zip(phases_raw, actual_phases_raw)):
                        expected_ph_norm = normalize_native_expected_for_readback(ph_expected_raw, NATIVE_PHASE_CONFIG_FIELDS)
                        for native_k, expected_type in NATIVE_PHASE_CONFIG_FIELDS.items():
                            py_k = pythonize_property_name(native_k)
                            expected_v = expected_ph_norm.get(native_k)
                            try:
                                actual_v = _extract_prop_val(ph_actual, py_k)
                                single_canonical = extract_canonical_primitives(
                                    {py_k: actual_v} if isinstance(ph_actual, dict) else ph_actual,
                                    {native_k: expected_type}
                                )
                                actual_canon = single_canonical.get(native_k)
                                if actual_canon != expected_v:
                                    collector.record_failure(asset_name, f"phases[{idx}]", py_k, expected_v, actual_v, mismatch_msg=f"got {actual_canon!r} != {expected_v!r}", step="readback")
                            except Exception as ex:
                                collector.record_failure(asset_name, f"phases[{idx}]", py_k, expected_v, None, error_ex=ex, step="readback")
            except Exception as ex:
                collector.record_failure(asset_name, "phases", "set_editor_property", "phase instances", None, error_ex=ex, step="set_editor_property")

            # ---------------------------------------------------------------
            # 5. Field Array (List of RPGParityField Instances)
            # ---------------------------------------------------------------
            fields_raw = p.get("fields", [])
            try:
                field_instances = []
                for idx, fd in enumerate(fields_raw):
                    fd_inst = create_empty_struct_instance("fields", unreal)
                    for native_k, expected_type in NATIVE_PARITY_FIELD_FIELDS.items():
                        py_k = pythonize_property_name(native_k)
                        if native_k in fd:
                            raw_val = fd[native_k]
                            try:
                                converted_val, _ = convert_property_for_engine(native_k, raw_val, expected_type, unreal)
                            except Exception as ex:
                                collector.record_failure(asset_name, f"fields[{idx}]", py_k, raw_val, None, error_ex=ex, step="convert")
                                continue
                            try:
                                if hasattr(fd_inst, "set_editor_property") and callable(getattr(fd_inst, "set_editor_property")):
                                    fd_inst.set_editor_property(py_k, converted_val)
                                elif isinstance(fd_inst, dict):
                                    fd_inst[py_k] = converted_val
                                else:
                                    setattr(fd_inst, py_k, converted_val)
                            except Exception as ex:
                                collector.record_failure(asset_name, f"fields[{idx}]", py_k, raw_val, None, error_ex=ex, step="set_editor_property")
                    field_instances.append(fd_inst)

                new_asset.set_editor_property("fields", field_instances)
                actual_fields_raw = new_asset.get_editor_property("fields") or []
                actual_count = len(actual_fields_raw)
                expected_count = len(fields_raw)
                print(f"[DRAFT_APPLY] fields rows read back: {actual_count} of {expected_count} expected")

                if actual_count != expected_count:
                    collector.record_failure(asset_name, "fields", "count", expected_count, actual_count, mismatch_msg=f"Count mismatch {actual_count} != {expected_count}", step="readback")
                else:
                    for idx, (fd_expected_raw, fd_actual) in enumerate(zip(fields_raw, actual_fields_raw)):
                        expected_fd_norm = normalize_native_expected_for_readback(fd_expected_raw, NATIVE_PARITY_FIELD_FIELDS)
                        for native_k, expected_type in NATIVE_PARITY_FIELD_FIELDS.items():
                            py_k = pythonize_property_name(native_k)
                            expected_v = expected_fd_norm.get(native_k)
                            try:
                                actual_v = _extract_prop_val(fd_actual, py_k)
                                single_canonical = extract_canonical_primitives(
                                    {py_k: actual_v} if isinstance(fd_actual, dict) else fd_actual,
                                    {native_k: expected_type}
                                )
                                actual_canon = single_canonical.get(native_k)
                                if actual_canon != expected_v:
                                    collector.record_failure(asset_name, f"fields[{idx}]", py_k, expected_v, actual_v, mismatch_msg=f"got {actual_canon!r} != {expected_v!r}", step="readback")
                            except Exception as ex:
                                collector.record_failure(asset_name, f"fields[{idx}]", py_k, expected_v, None, error_ex=ex, step="readback")
            except Exception as ex:
                collector.record_failure(asset_name, "fields", "set_editor_property", "field instances", None, error_ex=ex, step="set_editor_property")

            total_prop_count = verified_struct_count + 7
            asset_fails = collector.failure_count_for_asset(asset_name)
            if asset_fails == 0:
                print(f"[DRAFT_APPLY] Initialized & verified all {total_prop_count} typed properties on draft asset: '{asset_name}'")
            else:
                print(f"[DRAFT_APPLY] Draft asset '{asset_name}': {total_prop_count} properties set, {asset_fails} failed")

        if collector.has_failures:
            collector.print_summary_table()
            print(f"\n[DRAFT_APPLY] FATAL: {len(collector.failures)} property failure(s) detected during in-memory authoring.")
            report.success = False
            return False

        if not save_requested:
            print("\n[DRAFT_APPLY] SUCCESS: In-memory asset creation and complete readback verified.")
            print("  NOTICE: --save flag was not provided. Output packages were NOT saved to disk.")
            report.success = True
            return True

        # Explicit Save Opt-in
        if not hasattr(unreal.EditorAssetLibrary, "save_loaded_asset"):
            raise RuntimeError("Missing required Unreal API: unreal.EditorAssetLibrary.save_loaded_asset")

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
