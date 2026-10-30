#!/usr/bin/env python3
# Copyright One Boss Fight. All Rights Reserved.
"""
test_reopen_ki151_loadout_switch_research.py

Offline re-open test verifying that every citation, constant, and formula
in KI151_LOADOUT_SWITCH_AND_ACTIONS_RESEARCH.md exists and matches expectations.
"""

import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))

CHECKS = [
    # 1. RPGBuildLoadout style getters and commands
    ("Source/OneBossFight/Player/RPGBuildLoadout.h", [
        "GetActualStyleName",
        "GetStateName",
        "SetBuild",
    ]),

    # 2. RPGWeaponAttackTable rows and values
    ("Source/OneBossFight/Player/RPGWeaponAttackTable.cpp", [
        "ClaymoreCombatStyle",
        "SwordCombatStyle",
        "DualSwordCombatStyle",
        "Row.HealthDamageMultiplier = 0.39f;",
        "Make(Weapon, ERPGAttackKind::Light, 18.f, -1.f, 0.f",
        "Make(Weapon, ERPGAttackKind::Light, 6.f, 10.f, 20.f",
        "WithWindow(Strong, 0.352f, 0.618f, TEXT(\"Ability_E_Anim_Montage\"))",
    ]),

    # 3. Driver build constants in pie_builds.py
    ("Scripts/Editor/pie_builds.py", [
        "\"Starter\": \"SwordCombatStyle\"",
        "\"Strength\": \"ClaymoreCombatStyle\"",
        "\"Dex\": \"DualSwordCombatStyle\"",
        "\"Dex\": {\"Light\": True, \"Strong\": True, \"Charged\": False, \"JumpLight\": True, \"JumpHeavy\": True}",
        "ACTIONS = {",
        "\"Charged\": (\"IA_ChargedAttack\", 1.6, False)",
    ]),

    # 4. Driver build flow in pie_build_fight.py
    ("Scripts/Editor/pie_build_fight.py", [
        "HIT_DELAY = {\"Light\": 0.34, \"Strong\": 0.69, \"Charged\": 1.9, \"JumpLight\": 0.55, \"JumpHeavy\": 0.85}",
        "parts()[\"ld\"].get_actual_style_name() == want",
        "parts()[\"ld\"].get_state_name() == \"Idle\"",
        "Ability.EnterCombat",
    ]),
]

def main():
    print("=== Running test_reopen_ki151_loadout_switch_research.py ===")
    total = 0
    passed = 0

    doc_path = os.path.join(os.path.dirname(__file__), "KI151_LOADOUT_SWITCH_AND_ACTIONS_RESEARCH.md")
    total += 1
    if os.path.exists(doc_path):
        print(f"[PASS] Doc exists: {doc_path}")
        passed += 1
    else:
        print(f"[FAIL] Missing doc: {doc_path}")

    for rel_path, needles in CHECKS:
        total += 1
        full_path = os.path.join(BASE_DIR, rel_path.replace("/", os.sep))
        if not os.path.exists(full_path):
            print(f"[FAIL] Missing file: {rel_path}")
            continue

        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        missing = [n for n in needles if n not in content]
        if missing:
            print(f"[FAIL] In {rel_path}, missing: {missing}")
        else:
            print(f"[PASS] {rel_path} has all {len(needles)} needles")
            passed += 1

    print(f"\nResult: {passed}/{total} passed.")
    if passed == total:
        print("ALL CHECKS PASSED.")
        sys.exit(0)
    else:
        print("SOME CHECKS FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    main()
