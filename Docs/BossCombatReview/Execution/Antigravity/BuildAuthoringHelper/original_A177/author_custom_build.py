#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
author_custom_build.py
======================
Staged Unreal Editor Python helper for authoring an additive custom build Data Asset
and generating a cloned combat catalog with the new custom build registered.

Target Custom Build:
    - Asset Path:   /Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/DA_Build_Custom_Vanguard
    - Class:        URPGBuildDefinition (/Script/OneBossFight.RPGBuildDefinition)
    - BuildId:      Build_Custom_Vanguard (FName)
    - ConsoleName:  vanguard (FString)
    - Aliases:      ["vanguard_alt"] (TArray<FString>)
    - DisplayName:  "Vanguard Claymore" (FString)
    - UiOrder:      3 (int32)
    - LegacySlot:   -1 (INDEX_NONE, int32)
    - WeaponId:     Strength (FName - reuses existing Strength weapon)
    - Icon:         None / empty (FSoftObjectPath)

Target Cloned Catalog:
    - Asset Path:   /Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/DA_CombatCatalog_VanguardCloned
    - Class:        URPGCombatCatalog (/Script/OneBossFight.RPGCombatCatalog)
    - Source:       /Game/OneBossFight/Data/Catalog/DA_CombatCatalog
    - Retains:      All 3 existing weapons (DA_Weapon_Sword, DA_Weapon_Claymore, DA_Weapon_DualSwords)
    - Retains:      All 3 pinned legacy builds (Starter [0], Strength [1], Dex [2])
    - Appends:      DA_Build_Custom_Vanguard (1 custom build record, LegacySlot = -1)
    - Weapons:      ZERO new weapons added; zero style name collisions.

Execution Modes & Safety Gates:
    1. Dry-Run Mode (DEFAULT):
       - Read-only inspection of source catalog, weapons, and builds.
       - Whole-input contract check: Rejects if ANY involved source package is dirty.
       - Verifies native classes, editor state, and non-PIE mode.
       - Verifies output package paths do not exist.
       - Prints explicit Proposed Output Plan and static invariants.
       - ZERO writes, zero saves, zero mutations.
    2. Apply Mode (--apply):
       - Requires explicit --apply flag.
       - Pre-apply whole-plan validation, output non-existence check, and source dirty checks.
       - Populates struct definition and appends soft reference using explicit UE5.5 properties.
       - Verifies read-back before proceeding.
       - DOES NOT SAVE by default.
    3. Save Opt-in (--save):
       - Separate opt-in flag. MUST be combined with --apply (--apply --save).
       - Saves ONLY the two newly created output packages.
       - Verifies source packages remain clean. Drift causes failure and blocks saves.
       - Partial-failure reporting: If create/save fails halfway, reports exact created packages
         and halts immediately. Does NOT auto-delete assets, does NOT auto-clean, does NOT claim rollback.

DISCLAIMER & LIMITATIONS:
    Python reflection checks validate asset presence, property definitions, and namespace
    collisions inside the Unreal Editor environment. They do NOT constitute native C++
    FEpoch compilation or ABI validation. Full compilation and verification is conducted
    by the native C++ engine test seam (OneBossFight.Catalog.TestPathSeam / RPGCombatCatalog::Compile).
    Existing automation tests do not automatically compile newly authored preview outputs.

Usage in Unreal Editor Python:
    # 1. Dry-Run (Plan & Invariant Inspection Only)
    py "Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/author_custom_build.py"
    # 2. In-Memory Staged Apply (No Saves)
    py "Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/author_custom_build.py" --apply
    # 3. Staged Apply with Explicit Save Opt-in
    py "Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/author_custom_build.py" --apply --save
"""

import sys
import os
import re
import argparse
import json
from typing import Dict, List, Tuple, Any, Optional, Set

# ---------------------------------------------------------------------------
# Unreal Module Import Handling (Safe for Offline Compilation & Inspection)
# ---------------------------------------------------------------------------
try:
    import unreal
    HAS_UNREAL = True
except ImportError:
    unreal = None
    HAS_UNREAL = False

# ---------------------------------------------------------------------------
# Strict Canonical Paths & Invariants (Work Order AG_CONTENT03 & Source Contracts)
# ---------------------------------------------------------------------------
APPROVED_SOURCE_CATALOG = "/Game/OneBossFight/Data/Catalog/DA_CombatCatalog"
APPROVED_OUTPUT_ROOT = "/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/"

TARGET_BUILD_ASSET_NAME = "DA_Build_Custom_Vanguard"
TARGET_BUILD_PATH = APPROVED_OUTPUT_ROOT + TARGET_BUILD_ASSET_NAME

TARGET_CATALOG_ASSET_NAME = "DA_CombatCatalog_VanguardCloned"
TARGET_CATALOG_PATH = APPROVED_OUTPUT_ROOT + TARGET_CATALOG_ASSET_NAME

# Pinned Native Class Paths in /Script/OneBossFight
CLASS_CATALOG_PATH = "/Script/OneBossFight.RPGCombatCatalog"
CLASS_BUILD_DEF_PATH = "/Script/OneBossFight.RPGBuildDefinition"
CLASS_WEAPON_DEF_PATH = "/Script/OneBossFight.RPGWeaponDefinition"

# Pinned 3-Build Legacy Contract (Source: RPGCombatCatalog.cpp:158-172)
PINNED_LEGACY_CONTRACT = {
    0: {
        "BuildId": "Starter",
        "ConsoleName": "Starter",
        "DisplayName": "Starter",
        "UiOrder": 0,
        "WeaponId": "Sword",
        "ExpectedStyle": "SwordCombatStyle"
    },
    1: {
        "BuildId": "Strength",
        "ConsoleName": "Strength",
        "DisplayName": "Strength",
        "UiOrder": 1,
        "WeaponId": "Strength",
        "ExpectedStyle": "ClaymoreCombatStyle"
    },
    2: {
        "BuildId": "Dex",
        "ConsoleName": "Dex",
        "DisplayName": "Dex",
        "UiOrder": 2,
        "WeaponId": "Dex",
        "ExpectedStyle": "DualSwordsCombatStyle"
    }
}

# Reserved Console/Alias Keywords (Source: RPGCombatCatalog.cpp:154)
RESERVED_KEYWORDS = {"none", "off"}

# Target Custom Build Definition Specifications
CUSTOM_BUILD_SPEC = {
    "BuildId": "Build_Custom_Vanguard",
    "ConsoleName": "vanguard",
    "Aliases": ["vanguard_alt"],
    "DisplayName": "Vanguard Claymore",
    "UiOrder": 3,
    "LegacySlot": -1,  # INDEX_NONE
    "WeaponId": "Strength",
    "Icon": ""
}


# ---------------------------------------------------------------------------
# Exact Native Parity Normalization & Case-Insensitive Functions
# ---------------------------------------------------------------------------
def exact_native_normalize(text: str) -> str:
    """
    Exact parity with Unreal Engine 5.5 String.cpp.inl:971-974 TrimQuotesInline
    and RPGCombatRegistry::Normalize(const FString& Text):
        FString Normalize(const FString& Text) {
            return Text.TrimStartAndEnd().TrimQuotes().TrimStartAndEnd().ToLower();
        }
    In UE5, TrimQuotes trims double quotes (") ONLY. Single quotes (') are preserved.
    """
    if not text:
        return ""
    # 1. TrimStartAndEnd (whitespace)
    t = text.strip()
    # 2. TrimQuotes (double quotes only, matching TrimQuotesInline)
    if t.startswith('"') and t.endswith('"') and len(t) >= 2:
        t = t[1:-1]
    # 3. TrimStartAndEnd (whitespace after trimming double quotes)
    # 4. ToLower
    return t.strip().lower()


def case_insensitive_fname_eq(name1: str, name2: str) -> bool:
    """
    Exact parity with Unreal Engine FName equality (case-insensitive comparison).
    Source: Runtime/Core/Public/UObject/NameTypes.h
    """
    return name1.strip().lower() == name2.strip().lower()


def validate_canonical_path(path: str, expected_root: str) -> Tuple[bool, str]:
    """
    Validates that a package or asset path is strictly canonical:
    - Must start with expected_root
    - No path traversal ('..')
    - No double slashes ('//')
    - No backslashes ('\\')
    - No sub-object colons (':')
    - Matches strict alphanumeric / underscore package format
    """
    if not path:
        return False, "Path is empty"
    if not path.startswith(expected_root):
        return False, f"Path '{path}' does not start with expected root '{expected_root}'"
    if ".." in path:
        return False, f"Path traversal ('..') rejected: '{path}'"
    if "//" in path:
        return False, f"Double slashes ('//') rejected: '{path}'"
    if "\\" in path:
        return False, f"Backslashes rejected: '{path}'"
    if ":" in path:
        return False, f"Sub-object colon (':') rejected: '{path}'"

    # Strict pattern check for package/asset name
    pattern = r"^/Game/OneBossFight/Data/[A-Za-z0-9_/]+$"
    if not re.match(pattern, path):
        return False, f"Path '{path}' contains invalid characters or format"

    return True, ""


def validate_namespace_keys(build_id: str, console_name: str, aliases: List[str],
                            existing_names: Dict[str, str]) -> Tuple[bool, str, Dict[str, str]]:
    """
    Validates namespace keys for a build against collision and reserved keywords.
    Mirrors C++ loop in RPGCombatCatalog.cpp:150-156 using exact_native_normalize.
    """
    keys_to_check = list(aliases) + [console_name, build_id]
    updated_names = dict(existing_names)

    for raw in keys_to_check:
        key = exact_native_normalize(raw)
        if not key:
            return False, f"Build '{build_id}' has empty key in Aliases/ConsoleName/BuildId", existing_names
        if key in RESERVED_KEYWORDS:
            return False, f"Build '{build_id}' uses reserved keyword '{key}'", existing_names
        if key in updated_names and not case_insensitive_fname_eq(updated_names[key], build_id):
            return False, (f"Namespace collision: Key '{key}' from build '{build_id}' "
                           f"collides with existing build '{updated_names[key]}'"), existing_names
        updated_names[key] = build_id

    return True, "", updated_names


# ---------------------------------------------------------------------------
# Editor State & Non-PIE Guard
# ---------------------------------------------------------------------------
def verify_editor_environment() -> Tuple[bool, str]:
    """
    Verifies that the script is running inside the Unreal Editor and NOT in PIE or standalone game.
    """
    if not HAS_UNREAL:
        return False, "Unreal module not available (running in pure offline Python)"

    try:
        if not unreal.SystemLibrary.is_editor():
            return False, "Not running in Unreal Editor environment (is_editor() == False)"

        # Verify not running in Play In Editor (PIE) / simulated world
        editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        if editor_subsystem:
            game_world = editor_subsystem.get_game_world()
            if game_world is not None:
                return False, "Unreal Editor is currently running in PIE / Simulation mode. Execution prohibited."
    except Exception as ex:
        return False, f"Editor environment check failed with exception: {str(ex)}"

    return True, ""


# ---------------------------------------------------------------------------
# Staged Plan Data Structure
# ---------------------------------------------------------------------------
class StagedBuildPlan:
    def __init__(self, source_catalog_path: str, output_root: str):
        self.source_catalog_path = source_catalog_path
        self.output_root = output_root
        self.output_build_path = output_root + TARGET_BUILD_ASSET_NAME
        self.output_catalog_path = output_root + TARGET_CATALOG_ASSET_NAME

        self.source_schema_version: int = 1
        self.source_weapons: List[Dict[str, Any]] = []
        self.source_builds: List[Dict[str, Any]] = []
        self.source_packages: List[str] = []
        self.registered_names: Dict[str, str] = {}

        self.target_custom_build = dict(CUSTOM_BUILD_SPEC)
        self.validation_errors: List[str] = []
        self.validation_warnings: List[str] = []
        self.is_valid: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_catalog_path": self.source_catalog_path,
            "output_root": self.output_root,
            "output_build_path": self.output_build_path,
            "output_catalog_path": self.output_catalog_path,
            "source_schema_version": self.source_schema_version,
            "source_weapons_count": len(self.source_weapons),
            "source_weapons": self.source_weapons,
            "source_builds_count": len(self.source_builds),
            "source_builds": self.source_builds,
            "source_packages_checked": self.source_packages,
            "target_custom_build": self.target_custom_build,
            "cloned_catalog_projected_builds_count": len(self.source_builds) + 1,
            "is_valid": self.is_valid,
            "validation_errors": self.validation_errors,
            "validation_warnings": self.validation_warnings
        }


# ---------------------------------------------------------------------------
# Whole-Input Package Dirty Inspection
# ---------------------------------------------------------------------------
def check_source_packages_clean(packages_to_check: List[str]) -> Tuple[bool, List[str]]:
    """
    Inspects all source packages involved in the authoring plan.
    Fails closed if any package cannot be loaded or is currently dirty in memory.
    """
    if not HAS_UNREAL:
        return True, []

    dirty_or_missing: List[str] = []
    for pkg_path in packages_to_check:
        pkg = unreal.load_package(None, pkg_path)
        if pkg is None:
            dirty_or_missing.append(f"Missing / unloadable package: '{pkg_path}'")
        elif pkg.is_dirty():
            dirty_or_missing.append(f"Package is dirty in memory: '{pkg_path}'")

    return (len(dirty_or_missing) == 0), dirty_or_missing


# ---------------------------------------------------------------------------
# Offline Specification Check (Pure Python Validation)
# ---------------------------------------------------------------------------
def run_offline_specification_check(source_catalog_path: str, output_root: str) -> StagedBuildPlan:
    """
    Validates the authoring plan specification statically when outside Unreal Editor.
    Validates canonical paths, custom build record invariants, normalization parity,
    and namespace collision rules without synthetic inventories or live claims.
    """
    plan = StagedBuildPlan(source_catalog_path, output_root)

    # 1. Source Path Canonical Verification
    if source_catalog_path != APPROVED_SOURCE_CATALOG:
        plan.validation_errors.append(
            f"Source catalog path '{source_catalog_path}' must strictly equal approved '{APPROVED_SOURCE_CATALOG}'"
        )

    # 2. Output Paths Canonical Verification
    valid_b_path, b_path_err = validate_canonical_path(plan.output_build_path, APPROVED_OUTPUT_ROOT)
    if not valid_b_path:
        plan.validation_errors.append(f"Invalid output build path: {b_path_err}")

    valid_c_path, c_path_err = validate_canonical_path(plan.output_catalog_path, APPROVED_OUTPUT_ROOT)
    if not valid_c_path:
        plan.validation_errors.append(f"Invalid output catalog path: {c_path_err}")

    # 3. Custom Build Specification Verification
    b = plan.target_custom_build
    if not b["BuildId"] or b["BuildId"] == "None":
        plan.validation_errors.append("Custom BuildId cannot be empty or 'None'")
    if not b["DisplayName"]:
        plan.validation_errors.append("Custom DisplayName cannot be empty")
    if b["LegacySlot"] != -1:
        plan.validation_errors.append(f"Custom build LegacySlot must be -1 (INDEX_NONE); got {b['LegacySlot']}")
    if b["WeaponId"] != "Strength":
        plan.validation_errors.append(f"Expected custom build to reuse 'Strength' weapon; got '{b['WeaponId']}'")

    # 4. Normalization Parity Test Vectors
    test_vectors = [
        ("  \"vanguard\"  ", "vanguard"),
        ("\"none\"", "none"),
        ("'off'", "'off'"),  # Single quotes preserved per TrimQuotesInline
        ("off", "off")
    ]
    for raw_in, expected_out in test_vectors:
        actual_out = exact_native_normalize(raw_in)
        if actual_out != expected_out:
            plan.validation_errors.append(
                f"Normalization parity mismatch: '{raw_in}' -> '{actual_out}' (expected '{expected_out}')"
            )

    # 5. Namespace Collision Verification
    simulated_pinned = {
        "starter": "Starter",
        "strength": "Strength",
        "dex": "Dex"
    }
    valid_ns, ns_err, _ = validate_namespace_keys(
        b["BuildId"], b["ConsoleName"], b["Aliases"], simulated_pinned
    )
    if not valid_ns:
        plan.validation_errors.append(ns_err)

    plan.is_valid = (len(plan.validation_errors) == 0)
    return plan


# ---------------------------------------------------------------------------
# Live Unreal Editor Inspection & Validation
# ---------------------------------------------------------------------------
def inspect_and_validate_live(source_catalog_path: str, output_root: str) -> StagedBuildPlan:
    """
    Executes live Unreal Editor asset inspection using explicit Unreal reflection APIs.
    Validates native classes, source package dirty states, pinned 3-build contracts,
    weapons array invariants, and output non-existence.
    """
    if not HAS_UNREAL:
        raise RuntimeError("Live inspection requires Unreal Editor Python environment.")

    # 1. Editor Environment Check
    env_ok, env_err = verify_editor_environment()
    plan = StagedBuildPlan(source_catalog_path, output_root)
    if not env_ok:
        plan.validation_errors.append(f"Editor environment check failed: {env_err}")
        plan.is_valid = False
        return plan

    # 2. Strict Canonical Path Verifications
    if source_catalog_path != APPROVED_SOURCE_CATALOG:
        plan.validation_errors.append(
            f"Source catalog path '{source_catalog_path}' must strictly equal approved '{APPROVED_SOURCE_CATALOG}'"
        )

    valid_b_path, b_path_err = validate_canonical_path(plan.output_build_path, APPROVED_OUTPUT_ROOT)
    if not valid_b_path:
        plan.validation_errors.append(f"Invalid output build path: {b_path_err}")

    valid_c_path, c_path_err = validate_canonical_path(plan.output_catalog_path, APPROVED_OUTPUT_ROOT)
    if not valid_c_path:
        plan.validation_errors.append(f"Invalid output catalog path: {c_path_err}")

    # 3. Refuse Existing Output Packages (Never overwrite/delete)
    if unreal.EditorAssetLibrary.does_asset_exist(plan.output_build_path):
        plan.validation_errors.append(
            f"Output build asset already exists: '{plan.output_build_path}'. "
            "Helper strictly refuses overwrite/delete/repair. Must be manually inspected and resolved."
        )
    if unreal.EditorAssetLibrary.does_asset_exist(plan.output_catalog_path):
        plan.validation_errors.append(
            f"Output catalog asset already exists: '{plan.output_catalog_path}'. "
            "Helper strictly refuses overwrite/delete/repair. Must be manually inspected and resolved."
        )

    # 4. Strict Native Class Loading & Verification
    catalog_class = unreal.load_class(None, CLASS_CATALOG_PATH)
    if not catalog_class:
        plan.validation_errors.append(f"Failed to load native catalog class: '{CLASS_CATALOG_PATH}'")

    build_def_class = unreal.load_class(None, CLASS_BUILD_DEF_PATH)
    if not build_def_class:
        plan.validation_errors.append(f"Failed to load native build definition class: '{CLASS_BUILD_DEF_PATH}'")

    weapon_def_class = unreal.load_class(None, CLASS_WEAPON_DEF_PATH)
    if not weapon_def_class:
        plan.validation_errors.append(f"Failed to load native weapon definition class: '{CLASS_WEAPON_DEF_PATH}'")

    if not (catalog_class and build_def_class and weapon_def_class):
        plan.is_valid = False
        return plan

    # 5. Source Catalog Asset Loading & Class Check
    if not unreal.EditorAssetLibrary.does_asset_exist(plan.source_catalog_path):
        plan.validation_errors.append(f"Source catalog asset does not exist: '{plan.source_catalog_path}'")
        plan.is_valid = False
        return plan

    catalog_asset = unreal.EditorAssetLibrary.load_asset(plan.source_catalog_path)
    if not catalog_asset:
        plan.validation_errors.append(f"Failed to load source catalog asset: '{plan.source_catalog_path}'")
        plan.is_valid = False
        return plan

    # Verify Source Catalog Class
    if catalog_asset.get_class() != catalog_class:
        plan.validation_errors.append(
            f"Source catalog class mismatch: '{catalog_asset.get_class().get_path_name()}' "
            f"(expected '{CLASS_CATALOG_PATH}')"
        )

    # 6. Schema Version Verification
    plan.source_schema_version = int(catalog_asset.get_editor_property("schema_version"))
    if plan.source_schema_version != 1:
        plan.validation_errors.append(
            f"Unexpected schema_version in source catalog: {plan.source_schema_version} (expected 1)"
        )

    # Track all involved packages for dirty checking
    involved_packages: List[str] = [plan.source_catalog_path]

    # 7. Weapons Array Inspection & Strength Weapon Check
    weapons_array = catalog_asset.get_editor_property("weapons")
    if len(weapons_array) == 0:
        plan.validation_errors.append("Source catalog has empty Weapons array")

    strength_weapon_count = 0
    seen_weapon_ids: Set[str] = set()

    for w_soft in weapons_array:
        w_path = w_soft.to_string() if hasattr(w_soft, "to_string") else str(w_soft)
        involved_packages.append(w_path)

        w_asset = unreal.EditorAssetLibrary.load_asset(w_path)
        if not w_asset:
            plan.validation_errors.append(f"Failed to load weapon asset at path: '{w_path}'")
            continue

        if w_asset.get_class() != weapon_def_class:
            plan.validation_errors.append(
                f"Weapon asset '{w_path}' has class '{w_asset.get_class().get_path_name()}' "
                f"(expected '{CLASS_WEAPON_DEF_PATH}')"
            )
            continue

        w_def = w_asset.get_editor_property("definition")
        w_id = str(w_def.get_editor_property("weapon_id"))
        style_name = str(w_def.get_editor_property("style_name"))
        item_path = str(w_def.get_editor_property("item_path"))

        plan.source_weapons.append({
            "WeaponId": w_id,
            "StyleName": style_name,
            "ItemPath": item_path,
            "AssetPath": w_path
        })

        # Check duplicate weapon IDs (case-insensitive FName)
        for seen in seen_weapon_ids:
            if case_insensitive_fname_eq(seen, w_id):
                plan.validation_errors.append(f"Duplicate WeaponId in catalog: '{w_id}'")
        seen_weapon_ids.add(w_id)

        if case_insensitive_fname_eq(w_id, "Strength"):
            strength_weapon_count += 1

    if strength_weapon_count != 1:
        plan.validation_errors.append(
            f"Catalog must contain exactly 1 'Strength' weapon; found {strength_weapon_count}"
        )

    # 8. Builds Array Inspection & Pinned Legacy Contract Check
    builds_array = catalog_asset.get_editor_property("builds")
    if len(builds_array) < 3:
        plan.validation_errors.append(f"Catalog has only {len(builds_array)} builds (expected at least 3)")

    seen_build_ids: Set[str] = set()
    seen_legacy_slots: Set[int] = set()
    registered_names: Dict[str, str] = {}

    for b_soft in builds_array:
        b_path = b_soft.to_string() if hasattr(b_soft, "to_string") else str(b_soft)
        involved_packages.append(b_path)

        b_asset = unreal.EditorAssetLibrary.load_asset(b_path)
        if not b_asset:
            plan.validation_errors.append(f"Failed to load build asset at path: '{b_path}'")
            continue

        if b_asset.get_class() != build_def_class:
            plan.validation_errors.append(
                f"Build asset '{b_path}' has class '{b_asset.get_class().get_path_name()}' "
                f"(expected '{CLASS_BUILD_DEF_PATH}')"
            )
            continue

        b_def = b_asset.get_editor_property("definition")
        b_id = str(b_def.get_editor_property("build_id"))
        console_name = str(b_def.get_editor_property("console_name"))
        aliases = [str(a) for a in b_def.get_editor_property("aliases")]
        display_name = str(b_def.get_editor_property("display_name"))
        legacy_slot = int(b_def.get_editor_property("legacy_slot"))
        weapon_id = str(b_def.get_editor_property("weapon_id"))

        plan.source_builds.append({
            "BuildId": b_id,
            "ConsoleName": console_name,
            "Aliases": aliases,
            "DisplayName": display_name,
            "LegacySlot": legacy_slot,
            "WeaponId": weapon_id,
            "AssetPath": b_path
        })

        # Check duplicate BuildId (case-insensitive FName)
        for seen in seen_build_ids:
            if case_insensitive_fname_eq(seen, b_id):
                plan.validation_errors.append(f"Duplicate BuildId in catalog: '{b_id}'")
        seen_build_ids.add(b_id)

        # Check legacy slot rules (only 0, 1, 2 permitted; all others must be -1)
        if legacy_slot != -1:
            if legacy_slot < 0 or legacy_slot > 2:
                plan.validation_errors.append(f"Invalid LegacySlot {legacy_slot} on build '{b_id}'")
            elif legacy_slot in seen_legacy_slots:
                plan.validation_errors.append(f"Duplicate LegacySlot {legacy_slot} on build '{b_id}'")
            seen_legacy_slots.add(legacy_slot)

        # Validate and register namespace keys
        valid_ns, ns_err, updated_names = validate_namespace_keys(
            b_id, console_name, aliases, registered_names
        )
        if not valid_ns:
            plan.validation_errors.append(ns_err)
        registered_names = updated_names

    plan.registered_names = registered_names
    plan.source_packages = involved_packages

    # Verify Pinned 3-Build Legacy Contract Details
    for slot_idx, expected in PINNED_LEGACY_CONTRACT.items():
        matching = [b for b in plan.source_builds if b["LegacySlot"] == slot_idx]
        if len(matching) != 1:
            plan.validation_errors.append(
                f"Missing or duplicate build for LegacySlot {slot_idx} (expected '{expected['BuildId']}')"
            )
            continue

        b_entry = matching[0]
        if not case_insensitive_fname_eq(b_entry["BuildId"], expected["BuildId"]):
            plan.validation_errors.append(
                f"LegacySlot {slot_idx} BuildId '{b_entry['BuildId']}' mismatch (expected '{expected['BuildId']}')"
            )
        if b_entry["ConsoleName"] != expected["ConsoleName"]:
            plan.validation_errors.append(
                f"LegacySlot {slot_idx} ConsoleName '{b_entry['ConsoleName']}' mismatch (expected '{expected['ConsoleName']}')"
            )
        if b_entry["DisplayName"] != expected["DisplayName"]:
            plan.validation_errors.append(
                f"LegacySlot {slot_idx} DisplayName '{b_entry['DisplayName']}' mismatch (expected '{expected['DisplayName']}')"
            )
        if b_entry["UiOrder"] != expected["UiOrder"]:
            plan.validation_errors.append(
                f"LegacySlot {slot_idx} UiOrder {b_entry['UiOrder']} mismatch (expected {expected['UiOrder']})"
            )
        if not case_insensitive_fname_eq(b_entry["WeaponId"], expected["WeaponId"]):
            plan.validation_errors.append(
                f"LegacySlot {slot_idx} WeaponId '{b_entry['WeaponId']}' mismatch (expected '{expected['WeaponId']}')"
            )

    # 9. Whole-Input Package Dirty Verification (Involved Source Packages)
    packages_clean, dirty_errors = check_source_packages_clean(involved_packages)
    if not packages_clean:
        for d_err in dirty_errors:
            plan.validation_errors.append(f"Source package validation error: {d_err}")

    # 10. Validate Proposed Custom Build against Catalog
    custom_spec = plan.target_custom_build
    for b_seen in seen_build_ids:
        if case_insensitive_fname_eq(b_seen, custom_spec["BuildId"]):
            plan.validation_errors.append(f"Custom BuildId '{custom_spec['BuildId']}' already exists in catalog")

    weapon_exists = any(case_insensitive_fname_eq(w, custom_spec["WeaponId"]) for w in seen_weapon_ids)
    if not weapon_exists:
        plan.validation_errors.append(
            f"Custom build WeaponId '{custom_spec['WeaponId']}' does not exist in catalog weapons"
        )

    # Check proposed custom build namespace keys
    valid_c_ns, c_ns_err, _ = validate_namespace_keys(
        custom_spec["BuildId"], custom_spec["ConsoleName"], custom_spec["Aliases"], registered_names
    )
    if not valid_c_ns:
        plan.validation_errors.append(f"Custom build namespace error: {c_ns_err}")

    plan.is_valid = (len(plan.validation_errors) == 0)
    return plan


# ---------------------------------------------------------------------------
# Apply Execution (Creates and Optionally Saves Assets inside Unreal Editor)
# ---------------------------------------------------------------------------
def execute_staged_apply(plan: StagedBuildPlan, save_requested: bool = False) -> bool:
    """
    Executes staged creation of custom build and cloned catalog.
    Adheres strictly to the following transaction safety rules:
    - Pre-apply whole plan validation and output absence checks.
    - Whole-input dirty checking across all source packages before mutation.
    - Populates structs via get_editor_property / set_editor_property.
    - Reads back both created assets and asserts property parity before proceeding.
    - Saves ONLY newly created output packages, and ONLY if save_requested is True.
    - Re-checks source package cleanliness; fails if any source drift occurred.
    - If any error occurs, reports exact created packages and halts without silent deletion.
    """
    if not HAS_UNREAL:
        raise RuntimeError("Apply mode requires live Unreal Editor Python environment.")

    print("\n[STAGED_APPLY] Starting staged execution...")
    created_packages: List[str] = []

    try:
        # Pre-check 1: Validate plan
        if not plan.is_valid:
            print("[STAGED_APPLY] FATAL: Pre-apply plan validation failed:")
            for err in plan.validation_errors:
                print(f"  - ERROR: {err}")
            return False

        # Pre-check 2: Re-check output packages do NOT exist immediately before first mutation
        if unreal.EditorAssetLibrary.does_asset_exist(plan.output_build_path):
            print(f"[STAGED_APPLY] FATAL: Output build asset '{plan.output_build_path}' exists. Aborting.")
            return False
        if unreal.EditorAssetLibrary.does_asset_exist(plan.output_catalog_path):
            print(f"[STAGED_APPLY] FATAL: Output catalog asset '{plan.output_catalog_path}' exists. Aborting.")
            return False

        # Pre-check 3: Re-verify whole-input source packages clean
        clean_ok, dirty_list = check_source_packages_clean(plan.source_packages)
        if not clean_ok:
            print("[STAGED_APPLY] FATAL: Source packages dirty before apply:")
            for d in dirty_list:
                print(f"  - {d}")
            return False

        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        build_def_class = unreal.load_class(None, CLASS_BUILD_DEF_PATH)
        catalog_class = unreal.load_class(None, CLASS_CATALOG_PATH)

        # -------------------------------------------------------------------
        # Step 1: Create Custom Build Data Asset
        # -------------------------------------------------------------------
        print(f"[STAGED_APPLY] Step 1: Creating custom build Data Asset at '{plan.output_build_path}'...")
        pkg_path, asset_name = plan.output_build_path.rsplit("/", 1)

        factory = unreal.DataAssetFactory()
        factory.set_editor_property("data_asset_class", build_def_class)

        new_build_asset = asset_tools.create_asset(asset_name, pkg_path, build_def_class, factory)
        if not new_build_asset:
            raise RuntimeError(f"Failed to create build Data Asset at '{plan.output_build_path}'")
        created_packages.append(plan.output_build_path)

        # Populate Definition struct via explicit set_editor_property
        b_spec = plan.target_custom_build
        def_struct = new_build_asset.get_editor_property("definition")
        def_struct.set_editor_property("build_id", unreal.Name(b_spec["BuildId"]))
        def_struct.set_editor_property("console_name", b_spec["ConsoleName"])
        def_struct.set_editor_property("aliases", b_spec["Aliases"])
        def_struct.set_editor_property("display_name", b_spec["DisplayName"])
        def_struct.set_editor_property("ui_order", b_spec["UiOrder"])
        def_struct.set_editor_property("legacy_slot", b_spec["LegacySlot"])
        def_struct.set_editor_property("weapon_id", unreal.Name(b_spec["WeaponId"]))
        new_build_asset.set_editor_property("definition", def_struct)

        # Read back and verify Definition struct
        rb_def = new_build_asset.get_editor_property("definition")
        if str(rb_def.get_editor_property("build_id")) != b_spec["BuildId"]:
            raise RuntimeError("Read-back verification failed for build_id")
        if int(rb_def.get_editor_property("legacy_slot")) != b_spec["LegacySlot"]:
            raise RuntimeError("Read-back verification failed for legacy_slot")
        print(f"[STAGED_APPLY] Step 1 complete: Initialized & verified fields for '{b_spec['BuildId']}'")

        # -------------------------------------------------------------------
        # Step 2: Duplicate Source Catalog Data Asset
        # -------------------------------------------------------------------
        print(f"[STAGED_APPLY] Step 2: Duplicating catalog from '{plan.source_catalog_path}' to '{plan.output_catalog_path}'...")
        clone_success = unreal.EditorAssetLibrary.duplicate_asset(
            plan.source_catalog_path, plan.output_catalog_path
        )
        if not clone_success:
            raise RuntimeError(f"Failed to duplicate catalog to '{plan.output_catalog_path}'")
        created_packages.append(plan.output_catalog_path)

        cloned_catalog_asset = unreal.EditorAssetLibrary.load_asset(plan.output_catalog_path)
        if not cloned_catalog_asset:
            raise RuntimeError(f"Failed to load newly duplicated catalog at '{plan.output_catalog_path}'")

        if cloned_catalog_asset.get_class() != catalog_class:
            raise RuntimeError("Cloned catalog asset class mismatch")

        # Append new custom build soft reference to Builds array
        builds_array = list(cloned_catalog_asset.get_editor_property("builds"))
        initial_builds_count = len(builds_array)
        new_build_soft = unreal.SoftObjectPath(new_build_asset.get_path_name())
        builds_array.append(new_build_soft)
        cloned_catalog_asset.set_editor_property("builds", builds_array)

        # Read back and verify Builds array
        rb_builds = list(cloned_catalog_asset.get_editor_property("builds"))
        if len(rb_builds) != initial_builds_count + 1:
            raise RuntimeError("Read-back verification failed for cloned catalog builds count")
        print(f"[STAGED_APPLY] Step 2 complete: Appended custom build. Cloned catalog builds count: {len(rb_builds)}")

        # -------------------------------------------------------------------
        # Step 3: Post-Mutation Source Cleanliness Verification
        # -------------------------------------------------------------------
        clean_after, dirty_after = check_source_packages_clean(plan.source_packages)
        if not clean_after:
            print("[STAGED_APPLY] FATAL: Source package drift detected after asset generation:")
            for d in dirty_after:
                print(f"  - {d}")
            print("  Halting without saving. Output packages will not be saved.")
            return False

        # -------------------------------------------------------------------
        # Step 4: Save Newly Created Output Packages (Only with --save)
        # -------------------------------------------------------------------
        if not save_requested:
            print("\n[STAGED_APPLY] SUCCESS: In-memory asset creation and validation completed.")
            print("  NOTICE: --save flag was not provided. Output packages were NOT saved to disk.")
            print("  To save newly created packages, execute with: --apply --save")
            return True

        print("[STAGED_APPLY] Step 4: Saving newly created assets (--save requested)...")
        save_build = unreal.EditorAssetLibrary.save_loaded_asset(new_build_asset, only_if_dirty=True)
        if not save_build:
            raise RuntimeError(f"Failed to save newly created build asset '{plan.output_build_path}'")

        save_catalog = unreal.EditorAssetLibrary.save_loaded_asset(cloned_catalog_asset, only_if_dirty=True)
        if not save_catalog:
            raise RuntimeError(f"Failed to save cloned catalog asset '{plan.output_catalog_path}'")

        # Final verification: Confirm source packages still clean
        final_clean, final_dirty = check_source_packages_clean(plan.source_packages)
        if not final_clean:
            print("[STAGED_APPLY] FATAL: Source packages dirtied during save operation!")
            return False

        print("\n[STAGED_APPLY] SUCCESS: Staged creation and save complete.")
        print(f"  Created & Saved Build:   {plan.output_build_path}")
        print(f"  Created & Saved Catalog: {plan.output_catalog_path}")
        return True

    except Exception as ex:
        print("\n[STAGED_APPLY] FATAL ERROR during apply execution!")
        print(f"  Exception: {str(ex)}")
        print("  PARTIAL CREATION REPORT (Packages created before failure):")
        for pkg in created_packages:
            print(f"    - Partial Package: {pkg}")
        print("  POLICY: Halting immediately without auto-deletion. Assets remain on disk for inspection.")
        return False


# ---------------------------------------------------------------------------
# CLI Entry Point & Plan Formatting
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Staged Unreal Editor Python helper for authoring custom build Data Assets and cloned catalogs."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Execute in-memory staged creation of Data Assets (Default is read-only dry-run)."
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Opt-in to save newly created packages to disk (Requires --apply)."
    )
    parser.add_argument(
        "--source-catalog",
        type=str,
        default=APPROVED_SOURCE_CATALOG,
        help=f"Source catalog asset path (default: '{APPROVED_SOURCE_CATALOG}')"
    )
    parser.add_argument(
        "--output-root",
        type=str,
        default=APPROVED_OUTPUT_ROOT,
        help=f"Output package root (default: '{APPROVED_OUTPUT_ROOT}')"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print plan and results in JSON format."
    )

    args = parser.parse_args()

    # CLI Flag Guard: --save requires --apply
    if args.save and not args.apply:
        print("[ERROR] The --save option requires --apply. To dry-run without saving, omit --save.")
        sys.exit(1)

    print("=" * 80)
    print("OneBossFight - Staged Custom Build Authoring Helper (AG-CONTENT03 REV2)")
    print(f"Environment:    {'Unreal Editor Python Subsystem' if HAS_UNREAL else 'Pure Offline Python (Spec/Syntax Check)'}")
    print(f"Execution Mode: {'APPLY' if args.apply else 'DRY-RUN'} | Save: {'ENABLED' if args.save else 'DISABLED'}")
    print("=" * 80)

    # 1. Run Validation / Inspection
    if HAS_UNREAL:
        plan = inspect_and_validate_live(args.source_catalog, args.output_root)
    else:
        plan = run_offline_specification_check(args.source_catalog, args.output_root)

    # 2. Output Plan Summary
    if args.json:
        print(json.dumps(plan.to_dict(), indent=2))
    else:
        print("\n--- PROPOSED OUTPUT PLAN ---")
        print(f"Source Catalog:        {plan.source_catalog_path}")
        print(f"Output Root:           {plan.output_root}")
        print(f"Proposed Build Asset:  {plan.output_build_path}")
        print(f"Proposed Cloned Cat:   {plan.output_catalog_path}")
        print(f"Custom BuildId:        {plan.target_custom_build['BuildId']}")
        print(f"Custom ConsoleName:    {plan.target_custom_build['ConsoleName']}")
        print(f"Custom Aliases:        {plan.target_custom_build['Aliases']}")
        print(f"Custom DisplayName:    {plan.target_custom_build['DisplayName']}")
        print(f"Custom UiOrder:        {plan.target_custom_build['UiOrder']}")
        print(f"Custom LegacySlot:     {plan.target_custom_build['LegacySlot']} (INDEX_NONE)")
        print(f"Reused WeaponId:       {plan.target_custom_build['WeaponId']} (Existing Strength Weapon)")
        print(f"Plan Validity:         {'VALID' if plan.is_valid else 'INVALID'}")

        if plan.validation_errors:
            print("\nValidation Errors:")
            for err in plan.validation_errors:
                print(f"  [ERROR] {err}")

        if plan.validation_warnings:
            print("\nValidation Warnings:")
            for warn in plan.validation_warnings:
                print(f"  [WARN]  {warn}")

    # 3. Handle Execution Branches
    if not plan.is_valid:
        print("\n[RESULT] Plan validation FAILED. Halting.")
        sys.exit(1)

    if not args.apply:
        print("\n[RESULT] Dry-run completed successfully. Zero modifications made.")
        print("To execute in-memory staged creation, use: --apply")
        print("To execute creation and save output packages, use: --apply --save")
        sys.exit(0)

    # Apply Mode Execution
    if not HAS_UNREAL:
        print("\n[RESULT] Cannot execute --apply outside Unreal Editor. Please run inside the Unreal Editor Python environment.")
        sys.exit(2)

    success = execute_staged_apply(plan, save_requested=args.save)
    if not success:
        sys.exit(3)

    sys.exit(0)


if __name__ == "__main__":
    main()
