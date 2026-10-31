#!/usr/bin/env python3
# Copyright One Boss Fight. All Rights Reserved.
"""
test_reopen_c3_weapon_config.py
===============================
Offline re-open test verifying that validate_weapon_config.py,
test_validate_weapon_config.py, and example_new_weapon.json exist,
pass all unit tests, and faithfully implement the C3 weapon schema.
"""

import json
import os
import subprocess
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

BASE_DIR = os.path.abspath(os.path.join(_THIS_DIR, "..", "..", "..", "..", ".."))

from validate_weapon_config import validate_weapon_config
from test_validate_weapon_config import _build_content_asset_set

CHECKS = [
    ("Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_weapon_config.py", [
        "def validate_weapon_config",
        "Weapon.Config.Identity",
        "Weapon.Config.Path",
        "Weapon.Config.PathMissing",
        "Weapon.Config.UnknownCombatStyle",
        "Weapon.Config.EnemyCombatStyle",
        "Weapon.Config.StyleAlreadyHasRows",
        "Weapon.Config.UnknownUpdateKind",
        "Weapon.Config.AttackDomain",
        "Weapon.Config.HyperArmor",
        "Weapon.Config.Build",
        "Weapon.Config.AttackCoverage",
        "Weapon.Config.InvalidAttackKind",
        "DEFAULT_EXISTING_ROWS",
        "KNOWN_PACK_COMBAT_STYLES",
        "REQUIRED_ATTACK_KINDS",
    ]),
    ("Docs/BossCombatReview/Execution/Antigravity/Reviews/test_validate_weapon_config.py", [
        "test_00_valid_example_offline",
        "test_00b_valid_example_with_real_content_assets",
        "test_00c_valid_update_existing_style",
        "test_01_negative_structure_not_dict",
        "test_02_negative_missing_identity",
        "test_03_negative_unknown_combat_style",
        "test_04_negative_invalid_asset_path",
        "test_05_negative_style_path_mismatch",
        "test_06_negative_build_block",
        "test_07_negative_missing_required_attack_coverage",
        "test_08_negative_duplicate_attack_kind",
        "test_09_negative_invalid_attack_kind",
        "test_10_negative_attack_domain_values",
        "test_11_negative_hyperarmor_window",
        "test_12_negative_missing_asset_on_disk",
        "test_13_negative_enemy_combat_style",
        "test_14_negative_boss_combat_style",
        "test_15_negative_style_already_has_rows",
        "test_16_negative_update_mode_unknown_kind",
        "test_17_negative_unknown_mode",
    ]),
]


def main():
    print("=== Running test_reopen_c3_weapon_config.py ===")
    total = 0
    passed = 0

    # 1. Check example json exists and validates cleanly against real physical Content/ assets
    example_path = os.path.join(_THIS_DIR, "example_new_weapon.json")
    total += 1
    if os.path.exists(example_path):
        with open(example_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        content_assets = _build_content_asset_set()
        errors = validate_weapon_config(cfg, asset_exists=content_assets)
        if errors == []:
            print(f"[PASS] example_new_weapon.json validates with 0 errors against {len(content_assets)} physical assets")
            passed += 1
        else:
            print(f"[FAIL] example_new_weapon.json failed validation: {errors}")
    else:
        print(f"[FAIL] Missing example_new_weapon.json")

    # 2. Check source needles
    for rel_path, needles in CHECKS:
        total += 1
        full_path = os.path.join(BASE_DIR, rel_path.replace("/", os.sep))
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        missing = [n for n in needles if n not in content]
        if missing:
            print(f"[FAIL] {rel_path} missing needles: {missing}")
        else:
            print(f"[PASS] {rel_path} verified ({len(needles)} needles)")
            passed += 1

    # 3. Run test_validate_weapon_config.py via subprocess with python -I
    total += 1
    unit_test_script = os.path.join(_THIS_DIR, "test_validate_weapon_config.py")
    res = subprocess.run([sys.executable, "-I", unit_test_script], capture_output=True, text=True)
    if res.returncode == 0:
        print("[PASS] test_validate_weapon_config.py passed (20/20)")
        passed += 1
    else:
        print(f"[FAIL] test_validate_weapon_config.py failed:\n{res.stderr}\n{res.stdout}")

    print(f"\nResult: {passed}/{total} tests passed.")
    if passed != total:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
