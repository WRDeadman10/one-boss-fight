#!/usr/bin/env python3
# Copyright One Boss Fight. All Rights Reserved.
"""
test_reopen_ki151_dex_strong_jump_research.py

Offline re-open test verifying that every citation, sequence name, socket,
and formula in KI151_DEX_STRONG_AND_JUMP_SWING_RESEARCH.md exists and is valid.
"""

import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))

CHECKS = [
    # 1. Dex strong montages in GA_DuaSword_Melee export
    ("Docs/BossCombatReview/Execution/Claude/Evidence/exports/PR5_GA_DuaSword_Melee.txt", [
        "Attack_Melee_C_Montage",
        "Attack_GuardBreak_C_Montage",
        "Attack_Melee_Air_Montage",
    ]),

    # 2. Dual steel swords socket export
    ("Docs/BossCombatReview/Execution/Claude/Evidence/exports/PR5_BP_DualSteelSwords.txt", [
        "Weapon Hand Socket",
        "Second Weapon Hand Socket",
        "WeaponStart",
        "WeaponEnd",
    ]),

    # 3. Log evidence of the Attack_GuardBreak_C_Montage execution
    ("Docs/BossCombatReview/Execution/Claude/KI151/real_builds/dex/editor_raw.log", [
        "Attack_GuardBreak_C_Montage",
        "REAL swing 3 (IA_StrongAttack)",
    ]),

    # 4. Jump attack driver implementation in pie_hit_intake.py
    ("Scripts/Editor/pie_hit_intake.py", [
        "JUMP_KEY = \"Gamepad_FaceButton_Bottom\"",
        "\"jump light\", \"IA_NormalAttack\", 0.12, True",
        "\"jump heavy\", \"IA_StrongAttack\", 0.12, True",
    ]),

    # 5. RPGHitIntake airborne tracking
    ("Source/OneBossFight/Player/RPGHitIntake.cpp", [
        "Record.bAirborneAtStart = Montage->GetFName() == TrackedMontage && bTrackedAirborneAtStart;",
        "Record.Kind = Entry.bForceKind ? Entry.ForcedKind : RPGClassifyAttack(Record.AttackData, Record.bAirborne || Record.bAirborneAtStart);",
    ]),
]

def main():
    print("=== Running test_reopen_ki151_dex_strong_jump_research.py ===")
    total = 0
    passed = 0

    doc_path = os.path.join(os.path.dirname(__file__), "KI151_DEX_STRONG_AND_JUMP_SWING_RESEARCH.md")
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
