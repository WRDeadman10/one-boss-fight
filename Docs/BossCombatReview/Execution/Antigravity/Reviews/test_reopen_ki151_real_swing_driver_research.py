#!/usr/bin/env python3
# Copyright One Boss Fight. All Rights Reserved.
"""
test_reopen_ki151_real_swing_driver_research.py

Offline re-open test verifying that every file, symbol, and citation referenced
in KI151_REAL_SWING_DRIVER_RESEARCH.md exists and matches expectations.
"""

import os
import re
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))

CHECKS = [
    # 1. RPGInputTestUtils location and methods
    ("Source/OneBossFight/Combat/RPGInputTestUtils.h", [
        "URPGInputTestUtils",
        "InjectAction",
        "SetKeyDown",
    ]),
    ("Source/OneBossFight/Combat/RPGInputTestUtils.cpp", [
        "InjectAction",
        "SetKeyDown",
    ]),

    # 2. RPGFrameworkBossCharacter mesh NoCollision & capsule setup
    ("Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp", [
        "GetMesh()->SetCollisionEnabled(ECollisionEnabled::NoCollision);",
        "GetCapsuleComponent()->SetCapsuleSize(P.CapsuleRadiusCm,P.CapsuleHalfHeightCm);",
    ]),

    # 3. RPGHitIntake TryBind, HandlePackHit, BuildRecord, and FinalizePending via=pending
    ("Source/OneBossFight/Player/RPGHitIntake.cpp", [
        "bool URPGHitIntake::TryBind()",
        "FindComponentByClassName(GetOwner(), TEXT(\"BP_CollisionComponent_C\"))",
        "BuildRecord(HitResult, Target, Probe);",
        "bNativeBoss = true;",
        "[FrameworkProof] attack_row weapon=%s kind=%s found=%d posture=%g bleed=%g healthMult=%g via=pending",
        "Native->ApplyPlayerAttackHit(Record.Row, 1.0);",
    ]),

    # 4. Existing driver citations
    ("Scripts/Editor/pie_hit_intake.py", [
        "IA_NormalAttack",
        "Ability.EnterCombat",
        "inject_action",
    ]),
    ("Scripts/Editor/pie_build_fight.py", [
        "IA_NormalAttack",
        "HIT_DELAY",
        "Ability.EnterCombat",
        "SwordCombatStyle",
    ]),

    # 5. Tough sword export reference
    ("Docs/BossCombatReview/Execution/Claude/Evidence/exports/PR5_BP_ToughSword.txt", [
        "BP_WeaponTraceTarget.BP_WeaponTraceTarget_C",
        "WeaponStartSocket kind=NameProperty constraint=NameProperty edit=1 value=WeaponStart",
        "WeaponEndSocket kind=NameProperty constraint=NameProperty edit=1 value=WeaponEnd",
    ]),
]

def main():
    print("=== Running test_reopen_ki151_real_swing_driver_research.py ===")
    total_checks = 0
    passed_checks = 0

    # Check 1: Review document existence
    doc_path = os.path.join(os.path.dirname(__file__), "KI151_REAL_SWING_DRIVER_RESEARCH.md")
    total_checks += 1
    if os.path.exists(doc_path):
        print(f"[PASS] Review doc exists: {doc_path}")
        passed_checks += 1
    else:
        print(f"[FAIL] Review doc missing: {doc_path}")

    # Check 2: Citations across codebase
    for rel_path, needles in CHECKS:
        full_path = os.path.join(BASE_DIR, rel_path.replace("/", os.sep))
        total_checks += 1
        if not os.path.exists(full_path):
            print(f"[FAIL] Missing file: {rel_path}")
            continue

        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        missing = [needle for needle in needles if needle not in content]
        if missing:
            print(f"[FAIL] In {rel_path}, missing needles: {missing}")
        else:
            print(f"[PASS] {rel_path} contains all {len(needles)} needles")
            passed_checks += 1

    print(f"\nResult: {passed_checks}/{total_checks} checks passed.")
    if passed_checks == total_checks:
        print("ALL CHECKS PASSED.")
        sys.exit(0)
    else:
        print("SOME CHECKS FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    main()
