# Copyright One Boss Fight. All Rights Reserved.
"""
Offline validation test for Slice F10 Weapon Attack Row Implementation Plan.
Verifies all source file line citations, pure helper math, and pure CRLF compliance.
"""

import os
import sys
import unittest
from pathlib import Path

# Ensure directory is in sys.path for isolated 'python -I' invocations
sys.path.insert(0, str(Path(__file__).resolve().parent))


class TestF10AttackRowPlan(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[5]

    def _read_lines(self, rel_path):
        full_path = self.repo_root / rel_path
        self.assertTrue(full_path.exists(), f"File not found: {rel_path}")
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.readlines()

    def test_native_boss_health_citations(self):
        """Verify citations in RPGNativeBossHealth.h."""
        lines = self._read_lines("Source/OneBossFight/Player/RPGNativeBossHealth.h")
        self.assertTrue(any("class ONEBOSSFIGHT_API IRPGNativeBossHealth" in l for l in lines[14:20]))
        self.assertTrue(any("virtual double ApplyPlayerHit(double Multiplier) = 0;" in l for l in lines[20:25]))

    def test_hit_intake_citations(self):
        """Verify citations in RPGHitIntake.cpp."""
        lines = self._read_lines("Source/OneBossFight/Player/RPGHitIntake.cpp")
        self.assertTrue(any("void URPGHitIntake::InjectBossHitForTest(AActor* Boss)" in l for l in lines[395:415]))
        self.assertTrue(any("void URPGHitIntake::HandlePackHit(FHitResult HitResult)" in l for l in lines[410:450]))
        self.assertTrue(any("Native->ApplyPlayerHit(1.0);" in l for l in lines[415:455]))
        self.assertTrue(any("Posture->ApplyPostureDamage(Record.Row.PostureDamage" in l for l in lines[534:575]))
        self.assertTrue(any("Bleed->AddBuildup(BleedOverride >= 0.f ? BleedOverride : Record.Row.BleedBuildup" in l for l in lines[542:585]))

    def test_framework_boss_character_citations(self):
        """Verify citations in RPGFrameworkBossCharacter.cpp."""
        lines = self._read_lines("Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp")
        self.assertTrue(any("double ARPGFrameworkBossCharacter::ApplyPlayerHit(double Multiplier)" in l for l in lines[160:175]))
        self.assertTrue(any("Drain=FMath::Min(Posture," in l for l in lines[170:195]))
        self.assertTrue(any("if (BleedEnabled()) ApplyBleed(" in l for l in lines[175:198]))

    def test_weapon_attack_table_citations(self):
        """Verify citations in RPGWeaponAttackTable.h."""
        lines = self._read_lines("Source/OneBossFight/Player/RPGWeaponAttackTable.h")
        self.assertTrue(any("struct ONEBOSSFIGHT_API FRPGWeaponAttackRow" in l for l in lines[13:17]))

    def test_pure_math_simulation(self):
        """Verify the pure calculation logic proposed for RPGBossMath::ResolveHitImpact."""
        def resolve_hit_impact(multiplier, b_has_row, row_posture, row_bleed, row_health_mult,
                               profile_hit_dmg, profile_posture_fb, profile_bleed_fb,
                               current_hp, current_posture):
            nominal_dmg = profile_hit_dmg * (row_health_mult if b_has_row else 1.0) * multiplier
            health_loss = min(nominal_dmg, current_hp)
            base_posture = row_posture if b_has_row else profile_posture_fb
            posture_drain = min(base_posture * multiplier, current_posture)
            base_bleed = row_bleed if b_has_row else profile_bleed_fb
            bleed_buildup = max(0.0, base_bleed * multiplier)
            return health_loss, posture_drain, bleed_buildup

        # Case 1: Claymore JumpHeavy (has row: posture 38.0, bleed 0.0, health mult 1.0)
        h_loss, p_drain, b_bld = resolve_hit_impact(
            multiplier=1.0, b_has_row=True, row_posture=38.0, row_bleed=0.0, row_health_mult=1.0,
            profile_hit_dmg=100.0, profile_posture_fb=40.0, profile_bleed_fb=60.0,
            current_hp=250.0, current_posture=100.0
        )
        self.assertEqual(h_loss, 100.0)
        self.assertEqual(p_drain, 38.0)
        self.assertEqual(b_bld, 0.0)

        # Case 2: Dual Swords Light (has row: posture 6.0, bleed 20.0, health mult 1.0)
        h_loss, p_drain, b_bld = resolve_hit_impact(
            multiplier=1.0, b_has_row=True, row_posture=6.0, row_bleed=20.0, row_health_mult=1.0,
            profile_hit_dmg=100.0, profile_posture_fb=40.0, profile_bleed_fb=60.0,
            current_hp=250.0, current_posture=100.0
        )
        self.assertEqual(h_loss, 100.0)
        self.assertEqual(p_drain, 6.0)
        self.assertEqual(b_bld, 20.0)

        # Case 3: Starter Sword Light (has row: posture 18.0, bleed 0.0, health mult 0.39)
        h_loss, p_drain, b_bld = resolve_hit_impact(
            multiplier=1.0, b_has_row=True, row_posture=18.0, row_bleed=0.0, row_health_mult=0.39,
            profile_hit_dmg=100.0, profile_posture_fb=40.0, profile_bleed_fb=60.0,
            current_hp=250.0, current_posture=100.0
        )
        self.assertAlmostEqual(h_loss, 39.0, places=2)
        self.assertEqual(p_drain, 18.0)
        self.assertEqual(b_bld, 0.0)

        # Case 4: Fallback / Synthetic Injection (no row: uses profile defaults)
        h_loss, p_drain, b_bld = resolve_hit_impact(
            multiplier=1.0, b_has_row=False, row_posture=0.0, row_bleed=0.0, row_health_mult=1.0,
            profile_hit_dmg=100.0, profile_posture_fb=40.0, profile_bleed_fb=60.0,
            current_hp=250.0, current_posture=100.0
        )
        self.assertEqual(h_loss, 100.0)
        self.assertEqual(p_drain, 40.0)  # profile fallback
        self.assertEqual(b_bld, 60.0)    # profile fallback

    def test_pure_crlf_and_non_empty(self):
        """Verify deliverables exist, are non-empty, and maintain pure CRLF line endings."""
        docs_to_check = [
            "Docs/BossCombatReview/Execution/Antigravity/Reviews/F10_ATTACK_ROW_PLAN.md",
            "Docs/BossCombatReview/Execution/Antigravity/Reviews/test_reopen_f10_attack_row_plan.py",
        ]
        for rel in docs_to_check:
            raw = (self.repo_root / rel).read_bytes()
            self.assertGreater(len(raw), 500, f"{rel} is unexpectedly small")
            without_crlf = raw.replace(b"\r\n", b"")
            self.assertNotIn(b"\n", without_crlf, f"{rel} contains LF without CR (not pure CRLF)")
            self.assertNotIn(b"\r", without_crlf, f"{rel} contains standalone CR (not pure CRLF)")


if __name__ == "__main__":
    unittest.main()
