#!/usr/bin/env python3
# Copyright One Boss Fight. All Rights Reserved.
"""
test_reopen_c1_utility_design.py

Offline re-open test verifying that every citation, struct field, C++ validation token,
and script reference in C1_NEW_BOSS_UTILITY_DESIGN.md exists and is valid.
"""

import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))

CHECKS = [
    # 1. Profile header fields
    ("Source/OneBossFight/Player/RPGBossFrameworkProfile.h", [
        "FixtureLabel",
        "Mesh",
        "AnimClass",
        "TargetPawnClass",
        "Card",
        "Cards",
        "bDamageEnabled",
        "BandMinCm",
        "BandMaxCm",
        "WalkSpeedCmPerSecond",
        "AcceptanceCm",
        "WalkTimeoutSeconds",
        "BlendInSeconds",
        "BlendOutSeconds",
        "CapsuleRadiusCm",
        "CapsuleHalfHeightCm",
        "TargetHealth",
        "HitStepCm",
        "HitMaxSubsteps",
        "RepeatPenalty",
        "RepeatMemory",
        "AttackCount",
        "BossMaxHealth",
        "PlayerHitDamage",
        "PhaseTwoFraction",
        "PhaseTwoId",
        "PostureMax",
        "PlayerPostureHitAmount",
        "StaggerSeconds",
        "PostureRegenDelaySeconds",
        "PostureRegenPerSecond",
        "BleedBuildupPerHit",
        "BleedInitialThreshold",
        "BleedThresholdIncrease",
        "BleedThresholdMax",
        "BleedHpFraction",
        "MeshRelativeTransform",
        "bAlignmentAuthored",
    ]),

    # 2. Profile cpp validation tokens
    ("Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp", [
        "Framework.Profile.Identity",
        "Framework.Profile.Domain",
        "Framework.Profile.Phase",
        "Framework.Profile.Posture",
        "Framework.Profile.Bleed",
        "Framework.Profile.Geometry",
        "Framework.Profile.Alignment",
        "Framework.Profile.ObjectOrThread",
        "Framework.Profile.Dependency",
        "Framework.Profile.SequenceTelemetryOnly",
        "Framework.Profile.DamageCard",
        "Framework.Profile.AnimSkeleton",
        "Framework.Profile.CardBandOrBlendTail",
        "Framework.Profile.PhaseCards",
        "Framework.Profile.PhaseCooldownStarvation",
        "Framework.Profile.DamageBudget",
        "HasSlotNode",
        "/Script/AnimGraphRuntime.AnimNode_Slot",
    ]),

    # 3. MoveCard header fields
    ("Source/OneBossFight/Player/RPGBossMoveCard.h", [
        "Schema",
        "MoveId",
        "FamilyId",
        "PhaseId",
        "Skeleton",
        "Sequence",
        "Montage",
        "SlotName",
        "SectionName",
        "PlayRate",
        "CommitSeconds",
        "ActiveStartSeconds",
        "ActiveEndSeconds",
        "RecoveryEndSeconds",
        "TrackDegreesPerSecond",
        "MinRangeCm",
        "MaxRangeCm",
        "FrontConeDegrees",
        "HPDamage",
        "bUsesRootMotion",
        "Windows",
        "WindowId",
        "HitGroup",
        "StartSeconds",
        "EndSeconds",
        "SocketA",
        "SocketB",
        "RadiusCm",
        "BakedSamples",
        "TimeSeconds",
        "BaseCS",
        "TipCS",
    ]),

    # 4. MoveCard cpp validation tokens
    ("Source/OneBossFight/Player/RPGBossMoveCard.cpp", [
        "MoveCard.Identity",
        "MoveCard.AnimationSource",
        "MoveCard.AnimationIdentity",
        "MoveCard.SkeletonIdentity",
        "MoveCard.Slot",
        "MoveCard.Section",
        "MoveCard.UnsupportedRootMotion",
        "MoveCard.Domain",
        "MoveCard.Eligibility",
        "MoveCard.Timeline",
        "MoveCard.Window",
        "MoveCard.WindowIdentity",
        "MoveCard.Socket",
        "MoveCard.BakedSamples",
        "MoveCard.NotGameThread",
        "MoveCard.ResolvedObject",
        "MoveCard.AnimationType",
    ]),

    # 5. Pipeline script hooks
    ("Docs/BossCombatReview/Execution/Antigravity/MoveCards/bake_blade_path.py", [
        "NOMINAL_RATE_HZ = 120.0",
        "get_anim_pose_at_time",
    ]),
    ("Docs/BossCombatReview/Execution/Antigravity/MoveCards/author_move_cards.py", [
        "validate_move_card_spec",
        "execute_authoring",
    ]),
    ("Docs/BossCombatReview/Execution/Claude/F3c/create_proof_level.py", [
        "RPGFrameworkProofFixture",
        "new_level",
    ]),
    ("Docs/BossCombatReview/Execution/Claude/F5/create_f5_content.py", [
        "RPGBossProfileCard",
        "DA_Sevarog_SelectorProof_F5",
    ]),
    ("Docs/BossCombatReview/Execution/Antigravity/Reviews/grade_f10_log.py", [
        "grade_f10_log_lines",
    ]),
]

def main():
    print("=== Running test_reopen_c1_utility_design.py ===")
    total = 0
    passed = 0

    doc_path = os.path.join(os.path.dirname(__file__), "C1_NEW_BOSS_UTILITY_DESIGN.md")
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
