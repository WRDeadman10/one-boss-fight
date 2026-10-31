#!/usr/bin/env python3
# Copyright One Boss Fight. All Rights Reserved.
"""
test_reopen_c3_weapon_design.py
===============================
Offline re-open test verifying that C3_NEW_WEAPON_UTILITY_DESIGN.md exists,
every cited C++ file and symbol exists on disk, and the design document
accurately maps the weapon authoring pipeline, Build <-> Style relationship,
real ERPGAttackKind enum values, -InjectRow PIE proof, and driver REAL_STYLE extension.
"""

import os
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

BASE_DIR = os.path.abspath(os.path.join(_THIS_DIR, "..", "..", "..", "..", ".."))

FILES_TO_CHECK = [
    "Docs/BossCombatReview/Execution/Antigravity/Reviews/C3_NEW_WEAPON_UTILITY_DESIGN.md",
    "Docs/BossCombatReview/Execution/Antigravity/Reviews/C5_WEAPON_DATA_AUDIT.md",
    "Source/OneBossFight/Player/RPGAttackKind.h",
    "Source/OneBossFight/Player/RPGCombatCatalog.h",
    "Source/OneBossFight/Player/RPGCombatCatalog.cpp",
    "Source/OneBossFight/Player/RPGWeaponAttackTable.h",
    "Source/OneBossFight/Player/RPGWeaponAttackTable.cpp",
    "Source/OneBossFight/Player/RPGBuildRules.h",
    "Source/OneBossFight/Player/RPGBuildLoadout.cpp",
    "Source/OneBossFight/Player/RPGHitIntake.cpp",
    "Source/OneBossFight/Player/RPGSwingTracker.cpp",
]

SYMBOLS_TO_VERIFY = [
    ("Source/OneBossFight/Player/RPGAttackKind.h", [
        "ERPGAttackKind",
        "Light",
        "Strong",
        "Charged",
        "JumpLight",
        "JumpHeavy",
        "Knockdown",
    ]),
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
    ]),
    ("Source/OneBossFight/Player/RPGWeaponAttackTable.h", [
        "FRPGWeaponAttackRow",
        "URPGWeaponAttackTable",
        "PostureDamage",
        "StaminaCost",
        "BleedBuildup",
        "HealthDamageMultiplier",
        "HyperArmorStart",
        "HyperArmorEnd",
    ]),
    ("Source/OneBossFight/Player/RPGBuildRules.h", [
        "WeaponSlotEnumerator",
        "BuildOfStyle",
        "StyleOfBuild",
    ]),
]

DESIGN_NEEDLES = [
    "Weapon.Config.Identity",
    "Weapon.Config.Path",
    "Weapon.Config.AttackDomain",
    "Weapon.Config.HyperArmor",
    "Weapon.Config.Build",
    "Weapon.Config.AttackCoverage",
    "Weapon.Config.StyleAlreadyHasRows",
    "Weapon.Config.UnknownUpdateKind",
    "rpg.Build",
    "-RealBuild",
    "-RealSwing",
    "-InjectRow",
    "DA_WeaponAttacks",
    "DA_CombatCatalog",
    "FKismetBytecode",
    "FEpoch::Matches",
    "FEpoch::StyleToBuild",
    "BuildOfStyle",
    "JumpLight",
    "Knockdown",
    "REAL_STYLE",
]


def main():
    print("=== Running test_reopen_c3_weapon_design.py ===")
    total = 0
    passed = 0

    doc_path = os.path.join(BASE_DIR, "Docs", "BossCombatReview", "Execution", "Antigravity", "Reviews", "C3_NEW_WEAPON_UTILITY_DESIGN.md")
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
        print(f"[FAIL] C3 design missing needles: {missing_needles}")
    else:
        print(f"[PASS] C3 design verified all {len(DESIGN_NEEDLES)} design needles")
        passed += 1

    # Negative assertion: check that invalid attack kinds 'Running' and 'Falling' are absent as attack kind names
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
