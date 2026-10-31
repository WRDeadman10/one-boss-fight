#!/usr/bin/env python3
# Copyright One Boss Fight. All Rights Reserved.
"""
test_validate_boss_config.py
============================
Offline unit tests for validate_boss_config.py (Track C1).
Zero engine dependency.

Tests:
1. Positive Sevarog F10 baseline config (PASS, 0 errors).
2. 10 Negative cases testing exact failure tokens:
   - Negative 1: Framework.BossConfig.DestinationExists (unsafe overwrite)
   - Negative 2: Framework.Profile.Identity (F5 with empty cards)
   - Negative 3: Framework.Profile.Geometry (BandMin >= BandMax)
   - Negative 4: Framework.Profile.Geometry (Acceptance >= 0.5 * BandThickness)
   - Negative 5: Framework.Profile.Alignment (Unauthored transform)
   - Negative 6: Framework.Profile.Posture (Incoherent posture parameters)
   - Negative 7: Framework.Profile.Bleed (Incoherent bleed parameters)
   - Negative 8: Framework.Profile.CardBandOrBlendTail (Band outside card limits)
   - Negative 9: Framework.Profile.PhaseCards (Phase Two has zero cards)
   - Negative 10: Framework.Profile.PhaseCooldownStarvation (KI-149 Starvation Rule)
"""

import os
import sys
import copy

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from validate_boss_config import validate_boss_config


def get_sevarog_f10_valid_config():
    """Returns a completely valid Sevarog F10 equivalent configuration."""
    return {
        "boss_name": "Sevarog",
        "destination_package_dir": "/Game/OneBossFight/FrameworkProof",
        "fixture_label": "F5 fixture",
        "damage_enabled": True,
        "mesh_path": "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog.Sevarog",
        "anim_class_path": "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sevarog_AnimBlueprint.Sevarog_AnimBlueprint_C",
        "target_pawn_class_path": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter.BP_CombatPlayerCharacter_C",
        "band_min_cm": 150.0,
        "band_max_cm": 180.0,
        "walk_speed_cm_per_second": 180.0,
        "acceptance_cm": 5.0,
        "walk_timeout_seconds": 10.0,
        "blend_in_seconds": 0.1,
        "blend_out_seconds": 0.04,
        "capsule_radius_cm": 60.0,
        "capsule_half_height_cm": 165.0,
        "target_health": 800.0,
        "hit_step_cm": 15.0,
        "hit_max_substeps": 8,
        "repeat_penalty": 0.2,
        "repeat_memory": 2,
        "attack_count": 2,
        "boss_max_health": 1000.0,
        "player_hit_damage": 100.0,
        "phase_two_fraction": 0.5,
        "phase_two_id": "Phase_Two",
        "posture_max": 100.0,
        "player_posture_hit_amount": 25.0,
        "stagger_seconds": 3.0,
        "posture_regen_delay_seconds": 5.0,
        "posture_regen_per_second": 10.0,
        "bleed_buildup_per_hit": 25.0,
        "bleed_initial_threshold": 100.0,
        "bleed_threshold_increase": 50.0,
        "bleed_threshold_max": 300.0,
        "bleed_hp_fraction": 0.15,
        "alignment_authored": True,
        "mesh_relative_transform": {
            "location": [0.0, 0.0, -165.0],
            "rotation": [0.0, 0.0, -90.0],
            "scale": [1.0, 1.0, 1.0]
        },
        "cards": [
            {
                "move_id": "Move_Sevarog_SwingSlow_F5",
                "cooldown_seconds": 3.0,
                "weight": 1.0,
                "spec": {
                    "MoveId": "Move_Sevarog_SwingSlow_F5",
                    "PhaseId": "Phase_One",
                    "MinRangeCm": 100.0,
                    "MaxRangeCm": 200.0,
                    "ActiveStartSeconds": 0.45,
                    "RecoveryEndSeconds": 1.5,
                    "ClipLengthSeconds": 2.2,
                    "HPDamage": 100.0
                }
            },
            {
                "move_id": "Move_Sevarog_SwingMedium_F5",
                "cooldown_seconds": 1.0,
                "weight": 1.0,
                "spec": {
                    "MoveId": "Move_Sevarog_SwingMedium_F5",
                    "PhaseId": "Phase_One",
                    "MinRangeCm": 90.0,
                    "MaxRangeCm": 180.0,
                    "ActiveStartSeconds": 0.40,
                    "RecoveryEndSeconds": 1.3,
                    "ClipLengthSeconds": 1.8,
                    "HPDamage": 100.0
                }
            },
            {
                "move_id": "Move_Sevarog_AntiGreed_F5",
                "cooldown_seconds": 2.5,
                "weight": 1.0,
                "spec": {
                    "MoveId": "Move_Sevarog_AntiGreed_F5",
                    "PhaseId": "Phase_Two",
                    "MinRangeCm": 90.0,
                    "MaxRangeCm": 185.0,
                    "ActiveStartSeconds": 0.35,
                    "RecoveryEndSeconds": 1.4,
                    "ClipLengthSeconds": 1.9,
                    "HPDamage": 120.0
                }
            },
            {
                "move_id": "Move_Sevarog_HeavySlam_F5",
                "cooldown_seconds": 3.5,
                "weight": 1.0,
                "spec": {
                    "MoveId": "Move_Sevarog_HeavySlam_F5",
                    "PhaseId": "Phase_Two",
                    "MinRangeCm": 90.0,
                    "MaxRangeCm": 180.0,
                    "ActiveStartSeconds": 0.50,
                    "RecoveryEndSeconds": 1.6,
                    "ClipLengthSeconds": 2.0,
                    "HPDamage": 150.0
                }
            }
        ]
    }


def main():
    print("=== Running test_validate_boss_config.py ===")
    total = 0
    passed = 0

    # 1. Positive Baseline Test
    total += 1
    base_cfg = get_sevarog_f10_valid_config()
    errs = validate_boss_config(base_cfg)
    if not errs:
        print("[PASS] Test 1: Positive Baseline (Sevarog F10 equivalent) -> 0 errors")
        passed += 1
    else:
        print(f"[FAIL] Test 1: Positive Baseline failed with errors: {errs}")

    # Negative 1: Framework.BossConfig.DestinationExists
    total += 1
    dest_set = {"/Game/OneBossFight/FrameworkProof/DA_Sevarog_Profile"}
    errs = validate_boss_config(base_cfg, existing_destinations=dest_set)
    if any("Framework.BossConfig.DestinationExists" in e for e in errs):
        print("[PASS] Negative 1: Framework.BossConfig.DestinationExists detected")
        passed += 1
    else:
        print(f"[FAIL] Negative 1 expected DestinationExists, got: {errs}")

    # Negative 2: Framework.Profile.Identity
    total += 1
    cfg2 = copy.deepcopy(base_cfg)
    cfg2["cards"] = []
    errs = validate_boss_config(cfg2)
    if any("Framework.Profile.Identity" in e for e in errs):
        print("[PASS] Negative 2: Framework.Profile.Identity detected (empty F5 cards)")
        passed += 1
    else:
        print(f"[FAIL] Negative 2 expected Identity, got: {errs}")

    # Negative 3: Framework.Profile.Geometry (BandMin >= BandMax)
    total += 1
    cfg3 = copy.deepcopy(base_cfg)
    cfg3["band_min_cm"] = 200.0
    cfg3["band_max_cm"] = 100.0
    errs = validate_boss_config(cfg3)
    if any("Framework.Profile.Geometry" in e for e in errs):
        print("[PASS] Negative 3: Framework.Profile.Geometry detected (BandMin >= BandMax)")
        passed += 1
    else:
        print(f"[FAIL] Negative 3 expected Geometry, got: {errs}")

    # Negative 4: Framework.Profile.Geometry (Acceptance >= 0.5 * thickness)
    total += 1
    cfg4 = copy.deepcopy(base_cfg)
    cfg4["acceptance_cm"] = 25.0  # Band thickness is 30.0, 0.5*30 = 15.0
    errs = validate_boss_config(cfg4)
    if any("Framework.Profile.Geometry" in e for e in errs):
        print("[PASS] Negative 4: Framework.Profile.Geometry detected (Acceptance >= half thickness)")
        passed += 1
    else:
        print(f"[FAIL] Negative 4 expected Geometry, got: {errs}")

    # Negative 5: Framework.Profile.Alignment
    total += 1
    cfg5 = copy.deepcopy(base_cfg)
    cfg5["alignment_authored"] = False
    errs = validate_boss_config(cfg5)
    if any("Framework.Profile.Alignment" in e for e in errs):
        print("[PASS] Negative 5: Framework.Profile.Alignment detected (Unauthored)")
        passed += 1
    else:
        print(f"[FAIL] Negative 5 expected Alignment, got: {errs}")

    # Negative 6: Framework.Profile.Posture
    total += 1
    cfg6 = copy.deepcopy(base_cfg)
    cfg6["posture_max"] = 0.0
    cfg6["player_posture_hit_amount"] = 25.0  # Incoherent
    errs = validate_boss_config(cfg6)
    if any("Framework.Profile.Posture" in e for e in errs):
        print("[PASS] Negative 6: Framework.Profile.Posture detected (Incoherent posture)")
        passed += 1
    else:
        print(f"[FAIL] Negative 6 expected Posture, got: {errs}")

    # Negative 7: Framework.Profile.Bleed
    total += 1
    cfg7 = copy.deepcopy(base_cfg)
    cfg7["bleed_initial_threshold"] = 0.5  # must be >= 1.0
    errs = validate_boss_config(cfg7)
    if any("Framework.Profile.Bleed" in e for e in errs):
        print("[PASS] Negative 7: Framework.Profile.Bleed detected (Initial threshold < 1.0)")
        passed += 1
    else:
        print(f"[FAIL] Negative 7 expected Bleed, got: {errs}")

    # Negative 8: Framework.Profile.CardBandOrBlendTail
    total += 1
    cfg8 = copy.deepcopy(base_cfg)
    cfg8["band_min_cm"] = 80.0  # Card 0 MinRangeCm is 100.0 -> band extends below card range!
    errs = validate_boss_config(cfg8)
    if any("Framework.Profile.CardBandOrBlendTail" in e for e in errs):
        print("[PASS] Negative 8: Framework.Profile.CardBandOrBlendTail detected (BandMin < CardMin)")
        passed += 1
    else:
        print(f"[FAIL] Negative 8 expected CardBandOrBlendTail, got: {errs}")

    # Negative 9: Framework.Profile.PhaseCards
    total += 1
    cfg9 = copy.deepcopy(base_cfg)
    cfg9["phase_two_id"] = "Phase_Three_Uncovered"  # No cards tagged with this phase!
    errs = validate_boss_config(cfg9)
    if any("Framework.Profile.PhaseCards" in e for e in errs):
        print("[PASS] Negative 9: Framework.Profile.PhaseCards detected (Phase Two uncovered)")
        passed += 1
    else:
        print(f"[FAIL] Negative 9 expected PhaseCards, got: {errs}")

    # Negative 10: Framework.Profile.PhaseCooldownStarvation (KI-149)
    total += 1
    cfg10 = copy.deepcopy(base_cfg)
    cfg10["attack_count"] = 3
    # Phase Two currently has 2 cards with cooldowns 2.5 and 3.5 (> 0.0).
    # Since 2 cards < attack_count (3) and neither has cd <= 0, pool can starve!
    errs = validate_boss_config(cfg10)
    if any("Framework.Profile.PhaseCooldownStarvation" in e for e in errs):
        print("[PASS] Negative 10: Framework.Profile.PhaseCooldownStarvation detected (KI-149 Starvation)")
        passed += 1
    else:
        print(f"[FAIL] Negative 10 expected PhaseCooldownStarvation, got: {errs}")

    print(f"\nResult: {passed}/{total} tests passed.")
    if passed != total:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
