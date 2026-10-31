#!/usr/bin/env python3
# Copyright One Boss Fight. All Rights Reserved.
"""
test_reopen_c3_howto.py
=======================
Offline re-open test verifying that Documentation/Boss/C3_NEW_WEAPON_HOWTO.md
exists, every cited script and file exists on disk, every troubleshooting
token is authentic, and command syntax / negative assertions satisfy review standards.
"""

import os
import re
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

BASE_DIR = os.path.abspath(os.path.join(_THIS_DIR, "..", "..", "..", "..", ".."))

FILES_TO_CHECK = [
    "Docs/BossCombatReview/Execution/Claude/C3/new_weapon.py",
    "Docs/BossCombatReview/Execution/Claude/run_editor_script.ps1",
    "Docs/BossCombatReview/Execution/Claude/F4/run_pie.ps1",
    "Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_weapon_config.py",
    "Source/OneBossFight/Player/RPGCombatCatalog.cpp",
    "Source/OneBossFight/Player/RPGWeaponAttackTable.h",
    "Config/DefaultGame.ini",
]

TOKENS_TO_VERIFY = [
    ("Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_weapon_config.py", [
        "[Weapon.Config.Structure]",
        "[Weapon.Config.Mode]",
        "[Weapon.Config.Identity]",
        "[Weapon.Config.EnemyCombatStyle]",
        "[Weapon.Config.StyleAlreadyHasRows",
        "[Weapon.Config.UnknownCombatStyle]",
        "[Weapon.Config.Path]",
        "[Weapon.Config.PathMissing",
        "[Weapon.Config.ItemBaseClassPath]",
        "[Weapon.Config.Build]",
        "[Weapon.Config.Catalog.Structure]",
        "[Weapon.Config.Catalog.Path]",
        "[Weapon.Config.Catalog.LegacySlot]",
        "[Weapon.Config.Catalog.ReservedName]",
        "[Weapon.Config.Catalog.AliasCollision",
        "[Weapon.Config.Catalog.IconPath]",
        "[Weapon.Config.Catalog.IconCookRoot]",
        "[Weapon.Config.AttackCoverage]",
        "[Weapon.Config.InvalidAttackKind]",
        "[Weapon.Config.AttackDomain]",
        "[Weapon.Config.HyperArmor]",
    ]),
    ("Source/OneBossFight/Player/RPGCombatCatalog.cpp", [
        "Catalog.Builds/Weapons: empty",
        "Weapons.WeaponId: empty/duplicate",
        ".Style/Item/HudWord/Actions: required",
        ".StyleAliases: empty/conflict",
        "Builds.Id/WeaponId/DisplayName: invalid",
        ".LegacySlot: invalid/duplicate",
        ".Aliases: empty/reserved/collision",
        "Builds.LegacySlot: three compatibility slots required",
        "Builds.LegacySlot: pinned three-build contract changed",
        ".References: unresolved/wrong type/cook policy",
        "outside the cooked roots",
        "icon broken (%s)",
        ".Actions: required exact row missing",
    ]),
]

DOC_NEEDLES = [
    "## 1. Pack-Side Prerequisites (Unscriptable Assets)",
    "## 2. Configuration File Reference (`weapon_config.json`)",
    "## 3. Tool Command Lines",
    "## 4. PIE Proof & Verification (`-RealBuild <name>`)",
    "## 5. Restoring Repository State (Content Cleanliness)",
    "## 6. Complete Validation Tokens & Troubleshooting",
    "DirectoriesToAlwaysCook",
    "_C",
    "legacy_slot",
    "-RealBuild",
    "git checkout Content/OneBossFight/Data/DA_WeaponAttacks.uasset Content/OneBossFight/Data/Catalog/DA_CombatCatalog.uasset",
    "DA_WeaponAttacks.uasset",
    "DA_CombatCatalog.uasset",
    "URPGWeaponDefinition",
    "URPGBuildDefinition",
    "INDEX_NONE",
    "10-Second Pack-Style Warmup",
    'CLAUDE.md: "Never delete and recreate assets that other assets reference"',
]


def main():
    print("=== Running test_reopen_c3_howto.py ===")
    total = 0
    passed = 0

    doc_path = os.path.join(BASE_DIR, "Documentation", "Boss", "C3_NEW_WEAPON_HOWTO.md")
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

    for rel_path, tokens in TOKENS_TO_VERIFY:
        total += 1
        full_path = os.path.join(BASE_DIR, rel_path.replace("/", os.sep))
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        missing = [t for t in tokens if t not in content]
        if missing:
            print(f"[FAIL] {rel_path} missing tokens: {missing}")
        else:
            print(f"[PASS] {rel_path} verified all {len(tokens)} tokens")
            passed += 1

    # Check (1): Every -OutDir argument starts with a drive letter
    total += 1
    outdir_matches = re.findall(r'-OutDir\s+"([^"]+)"', doc_content)
    if outdir_matches and all(re.match(r'^[A-Za-z]:[\\/]', p) for p in outdir_matches):
        print(f"[PASS] All {len(outdir_matches)} -OutDir paths are absolute drive paths: {outdir_matches}")
        passed += 1
    else:
        print(f"[FAIL] Relative or missing -OutDir detected: {outdir_matches}")

    # Check (2): Strict documentation needles
    total += 1
    missing_needles = [n for n in DOC_NEEDLES if n not in doc_content]
    if missing_needles:
        print(f"[FAIL] Missing doc needles: {missing_needles}")
    else:
        print(f"[PASS] All {len(DOC_NEEDLES)} required doc needles present")
        passed += 1

    # Negative assertion: ensure broken catalog restore path is strictly absent
    total += 1
    if "git checkout Content/OneBossFight/Data/DA_WeaponAttacks.uasset Content/OneBossFight/Data/DA_CombatCatalog.uasset" in doc_content:
        print("[FAIL] Broken restore path detected: Data/DA_CombatCatalog.uasset without Catalog/ subfolder")
    else:
        print("[PASS] Broken restore path correctly absent")
        passed += 1

    print(f"\nResult: {passed}/{total} tests passed.")
    if passed != total:
        sys.exit(1)


if __name__ == "__main__":
    main()
