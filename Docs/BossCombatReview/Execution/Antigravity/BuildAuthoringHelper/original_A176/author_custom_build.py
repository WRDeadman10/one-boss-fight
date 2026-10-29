#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
author_custom_build.py
======================
Staged Unreal Editor Python helper for authoring an additive custom build Data Asset
and generating a cloned combat catalog with the new custom build registered.

Target Custom Build:
    - Asset Name:   DA_Build_Custom_Vanguard
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
    - Asset Name:   DA_CombatCatalog_VanguardCloned
    - Class:        URPGCombatCatalog (/Script/OneBossFight.RPGCombatCatalog)
    - Source:       /Game/OneBossFight/Data/Catalog/DA_CombatCatalog
    - Retains:      All 3 existing weapons (DA_Weapon_Sword, DA_Weapon_Claymore, DA_Weapon_DualSwords)
    - Retains:      All 3 pinned legacy builds (Starter [0], Strength [1], Dex [2])
    - Appends:      DA_Build_Custom_Vanguard (1 custom build record)
    - Weapons:      ZERO new weapons added; zero style name collisions.

Execution Modes:
    1. Dry-Run Mode (DEFAULT):
       Loads and inspects source catalog, weapons, and builds.
       Performs full structural pre-flight and namespace collision validation.
       Verifies output package paths do not exist.
       Outputs a formatted Proposed Output Plan.
       Zero writes, zero saves, zero mutations.
    2. Apply Mode (--apply):
       Performs full dry-run plan validation first.
       Snapshots source package dirty states.
       Creates DA_Build_Custom_Vanguard and populates struct definition.
       Duplicates source catalog to DA_CombatCatalog_VanguardCloned and appends new build.
       Saves ONLY the two newly created output packages.
       Verifies source catalog was not dirtied.
       Guards partial failures: reports newly created objects and halts without auto-deletion.

DISCLAIMER & LIMITATIONS:
    Python structural checks validate asset presence, property definitions, and namespace
    collisions inside the Unreal Editor Python environment. They do NOT constitute C++
    FEpoch compilation or ABI validation. Full compilation and verification is conducted
    by the native C++ engine test suite (OneBossFight.Binding.CatalogTests / RPGCombatCatalog::Compile).

Usage in Unreal Editor Python:
    py "Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/author_custom_build.py"
    py "Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/author_custom_build.py" --apply
"""

import sys
import os
import argparse
import json
from typing import Dict, List, Tuple, Any, Optional

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
# Strict Paths & Constants (Per Work Order AG_CONTENT03 & C++ Architecture)
# ---------------------------------------------------------------------------
SOURCE_CATALOG_DEFAULT = "/Game/OneBossFight/Data/Catalog/DA_CombatCatalog"
OUTPUT_PACKAGE_ROOT = "/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/"

TARGET_BUILD_ASSET_NAME = "DA_Build_Custom_Vanguard"
TARGET_BUILD_PATH = OUTPUT_PACKAGE_ROOT + TARGET_BUILD_ASSET_NAME

TARGET_CATALOG_ASSET_NAME = "DA_CombatCatalog_VanguardCloned"
TARGET_CATALOG_PATH = OUTPUT_PACKAGE_ROOT + TARGET_CATALOG_ASSET_NAME

# Pinned Native Class Paths in /Script/OneBossFight
CLASS_CATALOG_PATH = "/Script/OneBossFight.RPGCombatCatalog"
CLASS_BUILD_DEF_PATH = "/Script/OneBossFight.RPGBuildDefinition"
CLASS_WEAPON_DEF_PATH = "/Script/OneBossFight.RPGWeaponDefinition"

# Pinned 3-Build Legacy Contract (Source: RPGCombatCatalog.cpp:158-172)
PINNED_LEGACY_SLOTS = {
    0: "Starter",
    1: "Strength",
    2: "Dex"
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
# C++ Parity Normalization & Validation Helper Functions
# ---------------------------------------------------------------------------
def normalize_key(text: str) -> str:
    """
    Exact parity with RPGCombatRegistry::Normalize(const FString& Text):
    Text.TrimStartAndEnd().TrimQuotes().TrimStartAndEnd().ToLower()
    Source: Source/OneBossFight/Player/RPGCombatCatalog.cpp:25
    """
    if not text:
        return ""
    t = text.strip()
    if (t.startswith('"') and t.endswith('"')) or (t.startswith("'") and t.endswith("'")):
        t = t[1:-1]
    return t.strip().lower()


def validate_namespace_keys(build_id: str, console_name: str, aliases: List[str],
                            existing_names: Dict[str, str]) -> Tuple[bool, str, Dict[str, str]]:
    """
    Validates namespace keys for a build against collision and reserved keywords.
    Source: Source/OneBossFight/Player/RPGCombatCatalog.cpp:150-156
    """
    keys_to_check = list(aliases) + [console_name, build_id]
    updated_names = dict(existing_names)

    for raw in keys_to_check:
        key = normalize_key(raw)
        if not key:
            return False, f"Build '{build_id}' has empty key in Aliases/ConsoleName/BuildId", existing_names
        if key in RESERVED_KEYWORDS:
            return False, f"Build '{build_id}' uses reserved keyword '{key}'", existing_names
        if key in updated_names and updated_names[key] != build_id:
            return False, (f"Namespace collision: Key '{key}' from build '{build_id}' "
                           f"collides with existing build '{updated_names[key]}'"), existing_names
        updated_names[key] = build_id

    return True, "", updated_names


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
            "target_custom_build": self.target_custom_build,
            "cloned_catalog_projected_builds_count": len(self.source_builds) + 1,
            "is_valid": self.is_valid,
            "validation_errors": self.validation_errors,
            "validation_warnings": self.validation_warnings
        }


# ---------------------------------------------------------------------------
# Offline Structural Validator (Runs in Pure Python without Unreal Module)
# ---------------------------------------------------------------------------
def run_offline_specification_check(source_catalog_path: str, output_root: str) -> StagedBuildPlan:
    """
    Validates the authoring plan specification statically when outside Unreal Editor.
    Verifies output paths, naming rules, custom build record invariants, and namespace rules.
    """
    plan = StagedBuildPlan(source_catalog_path, output_root)

    # 1. Output Root Verification
    if not plan.output_root.startswith(OUTPUT_PACKAGE_ROOT):
        plan.validation_errors.append(
            f"Output root '{plan.output_root}' must strictly begin with approved root '{OUTPUT_PACKAGE_ROOT}'"
        )

    # 2. Custom Build Specification Verification
    b = plan.target_custom_build
    if not b["BuildId"] or b["BuildId"] == "None":
        plan.validation_errors.append("Custom BuildId cannot be empty or 'None'")
    if not b["DisplayName"]:
        plan.validation_errors.append("Custom DisplayName cannot be empty")
    if b["LegacySlot"] != -1:
        plan.validation_errors.append(f"Custom build LegacySlot must be -1 (INDEX_NONE); got {b['LegacySlot']}")
    if b["WeaponId"] != "Strength":
        plan.validation_errors.append(f"Expected custom build to reuse 'Strength' weapon; got '{b['WeaponId']}'")

    # 3. Namespace Invariants
    simulated_existing = {
        "starter": "Starter",
        "strength": "Strength",
        "dex": "Dex"
    }
    valid_ns, ns_err, updated_ns = validate_namespace_keys(
        b["BuildId"], b["ConsoleName"], b["Aliases"], simulated_existing
    )
    if not valid_ns:
        plan.validation_errors.append(ns_err)

    # 4. Mock Source Inventory for Plan Documentation
    plan.source_weapons = [
        {"WeaponId": "Sword", "StyleName": "SwordCombatStyle", "Item": "Weapon_Sword"},
        {"WeaponId": "Strength", "StyleName": "ClaymoreCombatStyle", "Item": "Weapon_Claymore"},
        {"WeaponId": "Dex", "StyleName": "DualSwordsCombatStyle", "Item": "Weapon_DualSwords"}
    ]
    plan.source_builds = [
        {"BuildId": "Starter", "ConsoleName": "starter", "LegacySlot": 0, "WeaponId": "Sword"},
        {"BuildId": "Strength", "ConsoleName": "strength", "LegacySlot": 1, "WeaponId": "Strength"},
        {"BuildId": "Dex", "ConsoleName": "dex", "LegacySlot": 2, "WeaponId": "Strength"},
    ]

    plan.is_valid = (len(plan.validation_errors) == 0)
    return plan


# ---------------------------------------------------------------------------
# Live Unreal Editor Inspection & Validation
# ---------------------------------------------------------------------------
def inspect_and_validate_live(source_catalog_path: str, output_root: str) -> StagedBuildPlan:
    """
    Executes live Unreal Editor asset inspection using Unreal reflection APIs.
    Performs full structural validation of source catalog, weapons, and builds.
    """
    if not HAS_UNREAL:
        raise RuntimeError("Live inspection requires Unreal Editor Python environment (import unreal failed).")

    plan = StagedBuildPlan(source_catalog_path, output_root)

    # 1. Output Root & Existence Guard
    if not plan.output_root.startswith(OUTPUT_PACKAGE_ROOT):
        plan.validation_errors.append(
            f"Output root '{plan.output_root}' must strictly begin with '{OUTPUT_PACKAGE_ROOT}'"
        )

    # Refuse existing output packages (Never overwrite/delete)
    if unreal.EditorAssetLibrary.does_asset_exist(plan.output_build_path):
        plan.validation_errors.append(
            f"Output build asset already exists: '{plan.output_build_path}'. "
            "Helper strictly refuses overwrite/delete/repair. Remove or change destination before running."
        )
    if unreal.EditorAssetLibrary.does_asset_exist(plan.output_catalog_path):
        plan.validation_errors.append(
            f"Output catalog asset already exists: '{plan.output_catalog_path}'. "
            "Helper strictly refuses overwrite/delete/repair. Remove or change destination before running."
        )

    # 2. Class Validations
    catalog_class = unreal.load_class(None, CLASS_CATALOG_PATH)
    if not catalog_class:
        plan.validation_errors.append(f"Failed to load native catalog class: '{CLASS_CATALOG_PATH}'")
    build_def_class = unreal.load_class(None, CLASS_BUILD_DEF_PATH)
    if not build_def_class:
        plan.validation_errors.append(f"Failed to load native build definition class: '{CLASS_BUILD_DEF_PATH}'")

    # 3. Source Catalog Asset Loading & Inspection
    if not unreal.EditorAssetLibrary.does_asset_exist(plan.source_catalog_path):
        plan.validation_errors.append(f"Source catalog asset does not exist: '{plan.source_catalog_path}'")
        plan.is_valid = False
        return plan

    catalog_asset = unreal.EditorAssetLibrary.load_asset(plan.source_catalog_path)
    if not catalog_asset:
        plan.validation_errors.append(f"Failed to load source catalog asset: '{plan.source_catalog_path}'")
        plan.is_valid = False
        return plan

    # Validate Schema Version
    plan.source_schema_version = getattr(catalog_asset, "schema_version", 0)
    if plan.source_schema_version != 1:
        plan.validation_errors.append(
            f"Unexpected schema_version in source catalog: {plan.source_schema_version} (expected 1)"
        )

    # 4. Weapons Array Inspection & Strength Weapon Check
    weapons_array = getattr(catalog_asset, "weapons", [])
    if len(weapons_array) == 0:
        plan.validation_errors.append("Source catalog has empty Weapons array")

    strength_weapon_count = 0
    seen_weapon_ids = set()

    for w_entry in weapons_array:
        w_asset = w_entry.get_asset() if hasattr(w_entry, "get_asset") else None
        if not w_asset:
            # Attempt load via path
            w_path = str(w_entry)
            w_asset = unreal.EditorAssetLibrary.load_asset(w_path)

        if not w_asset:
            plan.validation_errors.append(f"Failed to resolve weapon definition entry: {w_entry}")
            continue

        w_def = getattr(w_asset, "definition", None)
        if not w_def:
            plan.validation_errors.append(f"Weapon asset '{w_asset.get_path_name()}' missing Definition struct")
            continue

        w_id = str(getattr(w_def, "weapon_id", ""))
        style_name = str(getattr(w_def, "style_name", ""))
        item_path = str(getattr(w_def, "item_path", ""))

        plan.source_weapons.append({
            "WeaponId": w_id,
            "StyleName": style_name,
            "ItemPath": item_path,
            "AssetPath": w_asset.get_path_name()
        })

        if w_id in seen_weapon_ids:
            plan.validation_errors.append(f"Duplicate WeaponId in catalog: '{w_id}'")
        seen_weapon_ids.add(w_id)

        if w_id == "Strength":
            strength_weapon_count += 1

    if strength_weapon_count != 1:
        plan.validation_errors.append(
            f"Catalog must contain exactly 1 'Strength' weapon; found {strength_weapon_count}"
        )

    # 5. Builds Array Inspection & Pinned Legacy Slots Check
    builds_array = getattr(catalog_asset, "builds", [])
    if len(builds_array) < 3:
        plan.validation_errors.append(f"Catalog has only {len(builds_array)} builds (expected at least 3)")

    seen_build_ids = set()
    seen_legacy_slots = set()
    registered_names: Dict[str, str] = {}

    for b_entry in builds_array:
        b_asset = b_entry.get_asset() if hasattr(b_entry, "get_asset") else None
        if not b_asset:
            b_path = str(b_entry)
            b_asset = unreal.EditorAssetLibrary.load_asset(b_path)

        if not b_asset:
            plan.validation_errors.append(f"Failed to resolve build definition entry: {b_entry}")
            continue

        b_def = getattr(b_asset, "definition", None)
        if not b_def:
            plan.validation_errors.append(f"Build asset '{b_asset.get_path_name()}' missing Definition struct")
            continue

        b_id = str(getattr(b_def, "build_id", ""))
        console_name = str(getattr(b_def, "console_name", ""))
        aliases = [str(a) for a in getattr(b_def, "aliases", [])]
        display_name = str(getattr(b_def, "display_name", ""))
        legacy_slot = int(getattr(b_def, "legacy_slot", -1))
        weapon_id = str(getattr(b_def, "weapon_id", ""))

        plan.source_builds.append({
            "BuildId": b_id,
            "ConsoleName": console_name,
            "Aliases": aliases,
            "DisplayName": display_name,
            "LegacySlot": legacy_slot,
            "WeaponId": weapon_id,
            "AssetPath": b_asset.get_path_name()
        })

        if b_id in seen_build_ids:
            plan.validation_errors.append(f"Duplicate BuildId in catalog: '{b_id}'")
        seen_build_ids.add(b_id)

        if legacy_slot != -1:
            if legacy_slot in seen_legacy_slots:
                plan.validation_errors.append(f"Duplicate LegacySlot in catalog: {legacy_slot}")
            seen_legacy_slots.add(legacy_slot)

        # Register and check namespace keys
        valid_ns, ns_err, updated_names = validate_namespace_keys(
            b_id, console_name, aliases, registered_names
        )
        if not valid_ns:
            plan.validation_errors.append(ns_err)
        registered_names = updated_names

    plan.registered_names = registered_names

    # Verify Pinned 3-Build Legacy Contract
    for slot_idx, expected_name in PINNED_LEGACY_SLOTS.items():
        matching = [b for b in plan.source_builds if b["LegacySlot"] == slot_idx]
        if len(matching) != 1:
            plan.validation_errors.append(
                f"Missing or duplicate build for LegacySlot {slot_idx} (expected '{expected_name}')"
            )
        elif matching[0]["BuildId"] != expected_name:
            plan.validation_errors.append(
                f"LegacySlot {slot_idx} has BuildId '{matching[0]['BuildId']}' (expected '{expected_name}')"
            )

    # 6. Validate Proposed Custom Build against Live Catalog
    custom_spec = plan.target_custom_build
    if custom_spec["BuildId"] in seen_build_ids:
        plan.validation_errors.append(
            f"Custom BuildId '{custom_spec['BuildId']}' already exists in source catalog"
        )
    if custom_spec["WeaponId"] not in seen_weapon_ids:
        plan.validation_errors.append(
            f"Custom build WeaponId '{custom_spec['WeaponId']}' does not exist in catalog weapons"
        )

    # Namespace collision check for proposed custom build
    valid_custom_ns, custom_ns_err, _ = validate_namespace_keys(
        custom_spec["BuildId"], custom_spec["ConsoleName"], custom_spec["Aliases"], registered_names
    )
    if not valid_custom_ns:
        plan.validation_errors.append(f"Custom build namespace error: {custom_ns_err}")

    plan.is_valid = (len(plan.validation_errors) == 0)
    return plan


# ---------------------------------------------------------------------------
# Apply Execution (Creates and Saves Assets inside Unreal Editor)
# ---------------------------------------------------------------------------
def execute_staged_apply(plan: StagedBuildPlan) -> bool:
    """
    Executes staged creation of custom build and cloned catalog.
    Adheres strictly to the following transaction safety rules:
    - Pre-apply whole plan validation.
    - Snapshot dirty states of source packages.
    - Save ONLY newly created output packages.
    - If any error occurs, reports exact created assets and halts without silent deletion.
    """
    if not HAS_UNREAL:
        raise RuntimeError("Apply mode requires live Unreal Editor Python environment.")

    print("\n[STAGED_APPLY] Starting staged execution...")
    created_objects: List[str] = []

    try:
        # Pre-check 1: Validate plan
        if not plan.is_valid:
            print("[STAGED_APPLY] FATAL: Pre-apply plan validation failed:")
            for err in plan.validation_errors:
                print(f"  - ERROR: {err}")
            return False

        # Pre-check 2: Snapshot source package dirty state
        source_pkg = unreal.load_package(None, plan.source_catalog_path)
        if source_pkg and source_pkg.is_dirty():
            print(f"[STAGED_APPLY] FATAL: Source catalog package '{plan.source_catalog_path}' is dirty. Aborting.")
            return False

        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        build_def_class = unreal.load_class(None, CLASS_BUILD_DEF_PATH)

        # -------------------------------------------------------------------
        # Step 1: Create Custom Build Data Asset
        # -------------------------------------------------------------------
        print(f"[STAGED_APPLY] Step 1: Creating custom build Data Asset at '{plan.output_build_path}'...")
        package_path, asset_name = plan.output_build_path.rsplit("/", 1)
        
        factory = unreal.DataAssetFactory()
        factory.data_asset_class = build_def_class

        new_build_asset = asset_tools.create_asset(asset_name, package_path, build_def_class, factory)
        if not new_build_asset:
            raise RuntimeError(f"Failed to create build Data Asset at '{plan.output_build_path}'")
        created_objects.append(plan.output_build_path)

        # Populate Definition struct fields
        # URPGBuildDefinition::Definition (FRPGCatalogBuild)
        b_spec = plan.target_custom_build
        new_build_asset.definition.build_id = unreal.Name(b_spec["BuildId"])
        new_build_asset.definition.console_name = b_spec["ConsoleName"]
        new_build_asset.definition.aliases = b_spec["Aliases"]
        new_build_asset.definition.display_name = b_spec["DisplayName"]
        new_build_asset.definition.ui_order = b_spec["UiOrder"]
        new_build_asset.definition.legacy_slot = b_spec["LegacySlot"]
        new_build_asset.definition.weapon_id = unreal.Name(b_spec["WeaponId"])
        print(f"[STAGED_APPLY] Step 1 complete: Initialized fields for '{b_spec['BuildId']}'")

        # -------------------------------------------------------------------
        # Step 2: Clone Source Catalog Data Asset
        # -------------------------------------------------------------------
        print(f"[STAGED_APPLY] Step 2: Duplicating catalog from '{plan.source_catalog_path}' to '{plan.output_catalog_path}'...")
        clone_success = unreal.EditorAssetLibrary.duplicate_asset(
            plan.source_catalog_path, plan.output_catalog_path
        )
        if not clone_success:
            raise RuntimeError(f"Failed to duplicate catalog to '{plan.output_catalog_path}'")
        created_objects.append(plan.output_catalog_path)

        cloned_catalog_asset = unreal.EditorAssetLibrary.load_asset(plan.output_catalog_path)
        if not cloned_catalog_asset:
            raise RuntimeError(f"Failed to load newly duplicated catalog at '{plan.output_catalog_path}'")

        # Append new custom build reference to Builds array
        # URPGCombatCatalog::Builds is TArray<TSoftObjectPtr<URPGBuildDefinition>>
        cloned_catalog_asset.builds.append(new_build_asset)
        print(f"[STAGED_APPLY] Step 2 complete: Appended custom build. Cloned catalog build count: {len(cloned_catalog_asset.builds)}")

        # -------------------------------------------------------------------
        # Step 3: Save ONLY Newly Created Output Packages
        # -------------------------------------------------------------------
        print("[STAGED_APPLY] Step 3: Saving newly created assets...")
        save_build = unreal.EditorAssetLibrary.save_loaded_asset(new_build_asset, only_if_dirty=True)
        if not save_build:
            raise RuntimeError(f"Failed to save newly created build asset '{plan.output_build_path}'")

        save_catalog = unreal.EditorAssetLibrary.save_loaded_asset(cloned_catalog_asset, only_if_dirty=True)
        if not save_catalog:
            raise RuntimeError(f"Failed to save cloned catalog asset '{plan.output_catalog_path}'")

        # Post-check: Verify source catalog was untouched
        if source_pkg and source_pkg.is_dirty():
            print("[STAGED_APPLY] WARNING: Source catalog package was dirtied! Needs reversion.")

        print("\n[STAGED_APPLY] SUCCESS: Staged creation complete.")
        print(f"  Created & Saved Build:   {plan.output_build_path}")
        print(f"  Created & Saved Catalog: {plan.output_catalog_path}")
        print("  Next Step: Sole engine operator runs focused C++ tests to verify FEpoch compilation:")
        print("    OneBossFight.Binding.CatalogTests / RPGCombatCatalog::Compile")
        return True

    except Exception as ex:
        print("\n[STAGED_APPLY] FATAL ERROR during apply execution!")
        print(f"  Exception: {str(ex)}")
        print("  PARTIAL CREATION REPORT (Artifacts created before failure):")
        for obj in created_objects:
            print(f"    - Partial Object: {obj}")
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
        help="Execute staged creation and save of Data Assets (Default is read-only dry-run)."
    )
    parser.add_argument(
        "--source-catalog",
        type=str,
        default=SOURCE_CATALOG_DEFAULT,
        help=f"Source catalog asset path (default: '{SOURCE_CATALOG_DEFAULT}')"
    )
    parser.add_argument(
        "--output-root",
        type=str,
        default=OUTPUT_PACKAGE_ROOT,
        help=f"Output package root (default: '{OUTPUT_PACKAGE_ROOT}')"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print plan and results in JSON format."
    )

    args = parser.parse_args()

    print("=" * 80)
    print("OneBossFight - Staged Custom Build Authoring Helper (AG-CONTENT03)")
    print(f"Environment: {'Unreal Editor Python Subsystem' if HAS_UNREAL else 'Pure Offline Python (Syntax/Spec Check)'}")
    print(f"Execution Mode: {'APPLY (Creation & Save)' if args.apply else 'DRY-RUN (Inspection & Plan Only)'}")
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
        print(f"Retained Source Builds: {len(plan.source_builds)}")
        for b in plan.source_builds:
            print(f"  - [{b.get('LegacySlot', -1)}] {b['BuildId']} (Weapon: {b['WeaponId']})")
        print(f"Projected Cloned Catalog Total Builds: {len(plan.source_builds) + 1}")
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
        print("To create and save assets inside Unreal Editor, execute with --apply flag.")
        sys.exit(0)

    # Apply Mode
    if not HAS_UNREAL:
        print("\n[RESULT] Cannot execute --apply outside Unreal Editor. Please run inside the Unreal Editor Python environment.")
        sys.exit(2)

    success = execute_staged_apply(plan)
    if not success:
        sys.exit(3)

    sys.exit(0)


if __name__ == "__main__":
    main()
