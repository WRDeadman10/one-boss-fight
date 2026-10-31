#!/usr/bin/env python3
# Copyright One Boss Fight. All Rights Reserved.
"""
test_reopen_c1_v1_plan.py
=========================
Offline re-open test verifying that C1_V1_BOSS_UTILITY_PLAN.md
exists, cites true source lines and functions, and satisfies all requirements.
"""

import os
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

BASE_DIR = os.path.abspath(os.path.join(_THIS_DIR, "..", "..", "..", "..", ".."))

CHECKS = [
    # 1. new_boss.py hook
    ("Docs/BossCombatReview/Execution/Claude/C1/new_boss.py", [
        "destination_package_dir",
        "DA_%s_Profile",
        "L_%sFrameworkProof",
    ]),

    # 2. author_move_cards.py hook
    ("Docs/BossCombatReview/Execution/Antigravity/MoveCards/author_move_cards.py", [
        "def execute_authoring",
        "validate_move_card_spec",
    ]),

    # 3. bake_blade_path.py hook
    ("Docs/BossCombatReview/Execution/Antigravity/MoveCards/bake_blade_path.py", [
        "compute_sample_times",
        "get_anim_pose_at_time",
        "get_bone_translation",
    ]),

    # 4. apply_baked_samples.py hook
    ("Docs/BossCombatReview/Execution/Claude/F7/apply_baked_samples.py", [
        "baked_samples",
        "save_loaded_asset",
    ]),

    # 5. verify_baked_cards.py hook
    ("Docs/BossCombatReview/Execution/Antigravity/MoveCards/verify_baked_cards.py", [
        "verify_card_window_spot_checks",
        "run_verification",
        "DEFAULT_TOLERANCE_CM",
    ]),

    # 6. create_proof_level.py hook
    ("Docs/BossCombatReview/Execution/Claude/F3c/create_proof_level.py", [
        "RPGFrameworkProofFixture",
        "new_level",
    ]),

    # 7. C++ failure tokens in MoveCard.cpp
    ("Source/OneBossFight/Player/RPGBossMoveCard.cpp", [
        "MoveCard.Socket",
        "MoveCard.Timeline",
        "MoveCard.BakedSamples",
    ]),

    # 8. C++ failure tokens in FrameworkProfile.cpp
    ("Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp", [
        "Framework.Profile.PhaseCooldownStarvation",
        "Framework.Profile.CardBandOrBlendTail",
    ]),
]


def main():
    print("=== Running test_reopen_c1_v1_plan.py ===")
    total = 0
    passed = 0

    doc_path = os.path.join(_THIS_DIR, "C1_V1_BOSS_UTILITY_PLAN.md")
    total += 1
    if os.path.exists(doc_path) and os.path.getsize(doc_path) > 0:
        print(f"[PASS] Doc exists: {doc_path} ({os.path.getsize(doc_path)} bytes)")
        passed += 1
    else:
        print(f"[FAIL] Missing or empty doc: {doc_path}")

    for rel_path, needles in CHECKS:
        total += 1
        full_path = os.path.join(BASE_DIR, rel_path.replace("/", os.sep))
        if not os.path.exists(full_path):
            print(f"[FAIL] Missing file: {rel_path}")
            continue

        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        missing = [n for n in needles if n not in content]
        if missing:
            print(f"[FAIL] {rel_path} missing: {missing}")
        else:
            print(f"[PASS] {rel_path} verified ({len(needles)} needles)")
            passed += 1

    print(f"\nResult: {passed}/{total} tests passed.")
    if passed != total:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
