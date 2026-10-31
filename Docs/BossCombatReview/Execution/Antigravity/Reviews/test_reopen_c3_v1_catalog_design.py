#!/usr/bin/env python3
# Copyright One Boss Fight. All Rights Reserved.
"""
test_reopen_c3_v1_catalog_design.py
===================================
Offline re-open test verifying that C3_V1_CATALOG_ENTRY_DESIGN.md exists,
every cited C++ file and symbol exists on disk, and the design document
accurately maps the catalog registration architecture, failure tokens,
engine validation rules, _C generated class requirement, DirectoriesToAlwaysCook
cooked roots, and runtime rpg.Build switch path.
"""

import os
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

BASE_DIR = os.path.abspath(os.path.join(_THIS_DIR, "..", "..", "..", "..", ".."))

FILES_TO_CHECK = [
    "Docs/BossCombatReview/Execution/Antigravity/Reviews/C3_V1_CATALOG_ENTRY_DESIGN.md",
    "Source/OneBossFight/Player/RPGCombatCatalog.h",
    "Source/OneBossFight/Player/RPGCombatCatalog.cpp",
    "Source/OneBossFight/Player/RPGBuildLoadout.cpp",
    "Source/OneBossFight/Player/RPGAttackKind.h",
    "Source/OneBossFight/Player/RPGWeaponAttackTable.h",
]

SYMBOLS_TO_VERIFY = [
    ("Source/OneBossFight/Player/RPGCombatCatalog.h", [
        "FRPGCatalogWeapon",
        "FRPGCatalogBuild",
        "URPGWeaponDefinition",
        "URPGBuildDefinition",
        "URPGCombatCatalog",
        "FEpoch",
        "StyleToBuild",
        "Matches",
        "URPGCombatCatalogSubsystem",
        "bRequireExactRows",
    ]),
    ("Source/OneBossFight/Player/RPGBuildLoadout.cpp", [
        "ReadChoice",
        "CallEquip",
        "Update Equip Slot Item",
        "ReadStyle",
        "GWeaponSlotByte",
    ]),
    ("Source/OneBossFight/Player/RPGCombatCatalog.cpp", [
        "Catalog.Builds/Weapons: empty",
        "Weapons.WeaponId: empty/duplicate",
        "Builds.Id/WeaponId/DisplayName: invalid",
        "Builds.LegacySlot: three compatibility slots required",
        "bRequireExactRows",
    ]),
]

DESIGN_NEEDLES = [
    "URPGWeaponDefinition",
    "URPGBuildDefinition",
    "URPGCombatCatalog",
    "DA_CombatCatalog",
    "LegacySlot",
    "INDEX_NONE",
    "bRequireExactRows",
    "Weapon.Config.Catalog.Structure",
    "Weapon.Config.Catalog.Path",
    "Weapon.Config.Catalog.LegacySlot",
    "Weapon.Config.Catalog.ReservedName",
    "Weapon.Config.Catalog.AliasCollision",
    "Weapon.Config.Catalog.IconPath",
    "Weapon.Config.Catalog.ExactRows",
    "Weapon.Config.ItemBaseClassPath",
    "Weapon.Config.Catalog.IconCookRoot",
    "DirectoriesToAlwaysCook",
    "T_Boss01_Icon_Strength",
    "rpg.Build",
    "FEpoch::Parse",
    "CallEquip",
    "Update Equip Slot Item",
    "BP_EquipmentComponent_C",
    "CurrentCombatStyle",
    "GWeaponSlotByte",
]


def main():
    print("=== Running test_reopen_c3_v1_catalog_design.py ===")
    total = 0
    passed = 0

    doc_path = os.path.join(BASE_DIR, "Docs", "BossCombatReview/Execution/Antigravity/Reviews/C3_V1_CATALOG_ENTRY_DESIGN.md".replace("/", os.sep))
    total += 1
    if os.path.exists(doc_path) and os.path.getsize(doc_path) > 0:
        print(f"[PASS] Doc exists: {doc_path} ({os.path.getsize(doc_path)} bytes)")
        passed += 1
    else:
        print(f"[FAIL] Missing or empty doc: {doc_path}")

    with open(doc_path, "r", encoding="utf-8") as f:
        doc_content = f.read()

    for rel_path in FILES_TO_CHECK:
        total += 1
        full_path = os.path.join(BASE_DIR, rel_path.replace("/", os.sep))
        if os.path.exists(full_path):
            print(f"[PASS] File exists: {rel_path}")
            passed += 1
        else:
            print(f"[FAIL] Missing cited file: {rel_path}")

    for rel_path, tokens in SYMBOLS_TO_VERIFY:
        total += 1
        full_path = os.path.join(BASE_DIR, rel_path.replace("/", os.sep))
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        missing = [t for t in tokens if t not in content]
        if missing:
            print(f"[FAIL] {rel_path} missing tokens: {missing}")
        else:
            print(f"[PASS] {rel_path} verified all {len(tokens)} symbols")
            passed += 1

    total += 1
    missing_needles = [n for n in DESIGN_NEEDLES if n not in doc_content]
    if missing_needles:
        print(f"[FAIL] C3 v1 catalog design missing needles: {missing_needles}")
    else:
        print(f"[PASS] C3 v1 catalog design verified all {len(DESIGN_NEEDLES)} design needles")
        passed += 1

    # Negative assertion: check that invalid attack kinds 'Running' and 'Falling' are absent
    total += 1
    invalid_kinds = [k for k in ['"kind": "Running"', '"kind": "Falling"'] if k in doc_content]
    if invalid_kinds:
        print(f"[FAIL] Invalid attack kinds found in doc: {invalid_kinds}")
    else:
        print("[PASS] Negative assertion verified: invalid attack kinds 'Running' and 'Falling' are absent")
        passed += 1

    print(f"\nResult: {passed}/{total} tests passed.")
    if passed != total:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
