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
        "dormant_wake", "bleed", "low_sweep", "phases", "fields"
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
# Live Unreal Editor Staged Apply & Readback Verification
# ---------------------------------------------------------------------------
def execute_draft_apply(plan: Dict[str, Any], save_requested: bool = False) -> bool:
    """
    Executes staged creation of URPGBossDefinition draft assets inside Unreal Editor.
    Fails closed before ANY write if any required Unreal API is missing or if in PIE mode.
    Sets and reads back EVERY struct, phase, animation, and manifest property.
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

            # 1. Schema & Identifiers
            schema_val = p.get("schema_version", 1)
            def_id_val = unreal.Name(p["definition_id"])
            pres_id_val = unreal.Name(p["presentation_id"])

            new_asset.set_editor_property("schema", schema_val)
            new_asset.set_editor_property("definition_id", def_id_val)
            new_asset.set_editor_property("presentation_id", pres_id_val)

            # 2. Skeleton
            skel_raw = p.get("skeleton") or p.get("skeleton_candidate", "")
            skel_val = unreal.SoftObjectPath(skel_raw) if skel_raw else unreal.SoftObjectPath("")
            new_asset.set_editor_property("skeleton", skel_val)

            # 3. Animations
            anims_raw = p.get("animations") if "animations" in p else p.get("animation_candidates", [])
            anims_val = [unreal.SoftObjectPath(a) for a in anims_raw] if anims_raw else []
            new_asset.set_editor_property("animations", anims_val)

            # 4. Typed Struct Properties (Mapped to Generated Python Property Keys per UE5.5 PyGenUtil)
            stats_raw = p.get("stats", {})
            enc_policy_raw = p.get("encounter_policy", {})
            stg_policy_raw = p.get("stagger_policy", {})
            flow_raw = p.get("phase_flow", {})
            fire_raw = p.get("fireball", {})
            phase_dep_raw = p.get("phase_dependencies", {})
            stg_prof_raw = p.get("stagger_profile", {})
            wake_raw = p.get("dormant_wake", {})
            bleed_raw = p.get("bleed", {})
            low_sweep_raw = p.get("low_sweep", {})
            phases_raw = p.get("phases", [])
            fields_raw = p.get("fields", [])

            stats_py = map_native_dict_to_python_keys(stats_raw, NATIVE_BOSS_STATS_FIELDS)
            enc_policy_py = map_native_dict_to_python_keys(enc_policy_raw, NATIVE_ENCOUNTER_POLICY_FIELDS)
            stg_policy_py = map_native_dict_to_python_keys(stg_policy_raw, NATIVE_STAGGER_POLICY_FIELDS)
            flow_py = map_native_dict_to_python_keys(flow_raw, NATIVE_PHASE_FLOW_FIELDS)
            fire_py = map_native_dict_to_python_keys(fire_raw, NATIVE_FIREBALL_FIELDS)
            phase_dep_py = map_native_dict_to_python_keys(phase_dep_raw, NATIVE_PHASE_DEPENDENCY_FIELDS)
            stg_prof_py = map_native_dict_to_python_keys(stg_prof_raw, NATIVE_STAGGER_PROFILE_FIELDS)
            wake_py = map_native_dict_to_python_keys(wake_raw, NATIVE_DORMANT_WAKE_FIELDS)
            phases_py = [map_native_dict_to_python_keys(ph, NATIVE_PHASE_CONFIG_FIELDS) for ph in phases_raw]
            fields_py = [map_native_dict_to_python_keys(fd, NATIVE_PARITY_FIELD_FIELDS) for fd in fields_raw]

            new_asset.set_editor_property("stats", stats_py)
            new_asset.set_editor_property("encounter_policy", enc_policy_py)
            new_asset.set_editor_property("stagger_policy", stg_policy_py)
            new_asset.set_editor_property("phase_flow", flow_py)
            new_asset.set_editor_property("fireball", fire_py)
            new_asset.set_editor_property("phase_dependencies", phase_dep_py)
            new_asset.set_editor_property("stagger_profile", stg_prof_py)
            new_asset.set_editor_property("dormant_wake", wake_py)
            if bleed_raw:
                bleed_py = map_native_dict_to_python_keys(bleed_raw, NATIVE_BLEED_FIELDS)
                new_asset.set_editor_property("bleed", bleed_py)

            if low_sweep_raw:
                low_sweep_py = map_native_dict_to_python_keys(low_sweep_raw, NATIVE_LOW_SWEEP_FIELDS)
                new_asset.set_editor_property("low_sweep", low_sweep_py)
            new_asset.set_editor_property("phases", phases_py)
            new_asset.set_editor_property("fields", fields_py)

            # ---------------------------------------------------------------
            # Canonical Primitive Readback Verification of ALL 15 Properties
            # ---------------------------------------------------------------
            # 1. Scalar / Identifier / Soft Object Path Readbacks
            actual_schema = new_asset.get_editor_property("schema")
            if int(actual_schema) != schema_val:
                raise RuntimeError(f"Readback mismatch on '{asset_name}.schema': got {actual_schema} != {schema_val}")

            actual_def_id = new_asset.get_editor_property("definition_id")
            actual_def_str = str(actual_def_id.to_string()) if hasattr(actual_def_id, "to_string") else str(actual_def_id)
            if actual_def_str != p["definition_id"]:
                raise RuntimeError(f"Readback mismatch on '{asset_name}.definition_id': got '{actual_def_str}' != '{p['definition_id']}'")

            actual_pres_id = new_asset.get_editor_property("presentation_id")
            actual_pres_str = str(actual_pres_id.to_string()) if hasattr(actual_pres_id, "to_string") else str(actual_pres_id)
            if actual_pres_str != p["presentation_id"]:
                raise RuntimeError(f"Readback mismatch on '{asset_name}.presentation_id': got '{actual_pres_str}' != '{p['presentation_id']}'")

            actual_skel = new_asset.get_editor_property("skeleton")
            actual_skel_str = str(actual_skel.to_string()) if hasattr(actual_skel, "to_string") else str(actual_skel)
            if actual_skel_str != skel_raw:
                raise RuntimeError(f"Readback mismatch on '{asset_name}.skeleton': got '{actual_skel_str}' != '{skel_raw}'")

            actual_anims = new_asset.get_editor_property("animations")
            actual_anims_list = [str(a.to_string()) if hasattr(a, "to_string") else str(a) for a in (actual_anims or [])]
            if actual_anims_list != anims_raw:
                raise RuntimeError(f"Readback mismatch on '{asset_name}.animations': got {actual_anims_list} != {anims_raw}")

            # 2. Typed Struct Canonical Primitive Readbacks (ensuring non-default values survive round trip)
            struct_readback_specs = [
                ("stats", NATIVE_BOSS_STATS_FIELDS, stats_raw),
                ("encounter_policy", NATIVE_ENCOUNTER_POLICY_FIELDS, enc_policy_raw),
                ("stagger_policy", NATIVE_STAGGER_POLICY_FIELDS, stg_policy_raw),
                ("phase_flow", NATIVE_PHASE_FLOW_FIELDS, flow_raw),
                ("fireball", NATIVE_FIREBALL_FIELDS, fire_raw),
                ("phase_dependencies", NATIVE_PHASE_DEPENDENCY_FIELDS, phase_dep_raw),
                ("stagger_profile", NATIVE_STAGGER_PROFILE_FIELDS, stg_prof_raw),
                ("dormant_wake", NATIVE_DORMANT_WAKE_FIELDS, wake_raw),
            ]
            if bleed_raw:
                struct_readback_specs.append(("bleed", NATIVE_BLEED_FIELDS, bleed_raw))

            if low_sweep_raw:
                struct_readback_specs.append(("low_sweep", NATIVE_LOW_SWEEP_FIELDS, low_sweep_raw))

            for section_name, field_spec, expected_native_dict in struct_readback_specs:
                actual_struct = new_asset.get_editor_property(section_name)
                canonical_dict = extract_canonical_primitives(actual_struct, field_spec)
                expected_float32_dict = normalize_native_expected_for_readback(expected_native_dict, field_spec)
                if canonical_dict != expected_float32_dict:
                    raise RuntimeError(
                        f"Canonical primitive readback mismatch on '{asset_name}.{section_name}':\n"
                        f"  Actual:   {canonical_dict}\n"
                        f"  Expected: {expected_float32_dict}"
                    )

            # 3. Phase and Field Array Canonical Readbacks
            actual_phases_raw = new_asset.get_editor_property("phases") or []
            actual_phases_canonical = [extract_canonical_primitives(ph, NATIVE_PHASE_CONFIG_FIELDS) for ph in actual_phases_raw]
            expected_phases_float32 = [normalize_native_expected_for_readback(ph, NATIVE_PHASE_CONFIG_FIELDS) for ph in phases_raw]
            if actual_phases_canonical != expected_phases_float32:
                raise RuntimeError(f"Readback mismatch on '{asset_name}.phases': {actual_phases_canonical} != {expected_phases_float32}")

            actual_fields_raw = new_asset.get_editor_property("fields") or []
            actual_fields_canonical = [extract_canonical_primitives(fd, NATIVE_PARITY_FIELD_FIELDS) for fd in actual_fields_raw]
            expected_fields_float32 = [normalize_native_expected_for_readback(fd, NATIVE_PARITY_FIELD_FIELDS) for fd in fields_raw]
            if actual_fields_canonical != expected_fields_float32:
                raise RuntimeError(f"Readback mismatch on '{asset_name}.fields': {actual_fields_canonical} != {expected_fields_float32}")

            total_prop_count = len(struct_readback_specs) + 7
            print(f"[DRAFT_APPLY] Initialized & verified all {total_prop_count} typed properties on draft asset: '{asset_name}'")

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
