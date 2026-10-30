# Copyright One Boss Fight. All Rights Reserved.
"""
test_reopen_ki151_plan.py
Offline re-open validation test for KI-151 Pack Weapon Swing Implementation Plan.
Authority: Lead Order [C-463]
"""

import os
import sys
import unittest
from pathlib import Path

# Support isolated python -I invocation
sys.path.insert(0, str(Path(__file__).resolve().parent))


class TestReopenKI151Plan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parents[5]
        cls.reviews_dir = Path(__file__).resolve().parent

    def _read_lines(self, rel_path):
        full_path = self.repo_root / rel_path
        self.assertTrue(full_path.exists(), f"File not found: {rel_path}")
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.readlines()

    def test_crlf_line_endings(self):
        """Verifies that all authored KI-151 files use pure CRLF line endings without bare LFs."""
        target_files = [
            self.reviews_dir / "KI151_PACK_WEAPON_SWING_PLAN.md",
            self.reviews_dir / "test_reopen_ki151_plan.py"
        ]
        for tf in target_files:
            if not tf.exists():
                continue
            raw_bytes = tf.read_bytes()
            self.assertNotIn(b"\r\r\n", raw_bytes, f"Corrupted double CR in {tf.name}")
            stripped = raw_bytes.replace(b"\r\n", b"")
            self.assertNotIn(b"\n", stripped, f"Bare LF detected in {tf.name}")
            self.assertNotIn(b"\r", stripped, f"Bare CR detected in {tf.name}")

    def test_cpp_citations_hit_intake(self):
        """Verifies citations in RPGHitIntake.cpp and RPGHitIntake.h."""
        cpp_lines = self._read_lines("Source/OneBossFight/Player/RPGHitIntake.cpp")

        # HandlePackHit definition and native branch
        self.assertIn("void URPGHitIntake::HandlePackHit(FHitResult HitResult)", cpp_lines[438])
        self.assertIn("if (IRPGNativeBossHealth* Native = Cast<IRPGNativeBossHealth>(Target))", cpp_lines[442])
        self.assertIn("Native->ApplyPlayerHit(1.0);", cpp_lines[444])

        # BuildRecord definition
        self.assertIn("FRPGHitRecord URPGHitIntake::BuildRecord(const FHitResult& HitResult, AActor* Target, UObject*& OutActiveTarget) const", cpp_lines[360])
        self.assertIn("BP_CombatComponent_C", cpp_lines[370])
        self.assertIn("CurrentCombatStyle", cpp_lines[372])

        # FinalizePending and SeenMontages
        self.assertIn("void URPGHitIntake::FinalizePending()", cpp_lines[468])
        self.assertIn("TArray<FName> SeenMontages;", cpp_lines[475])
        self.assertIn("SeenMontages.Contains(Record.Montage)", cpp_lines[479])
        self.assertIn("++MergedHitCount;", cpp_lines[481])

        # RPGHitIntake.h struct FPending
        h_lines = self._read_lines("Source/OneBossFight/Player/RPGHitIntake.h")
        self.assertIn("struct FPending", h_lines[150])
        self.assertIn("FRPGHitRecord Record;", h_lines[152])

    def test_cpp_citations_native_boss_health(self):
        """Verifies citations in RPGNativeBossHealth.h."""
        lines = self._read_lines("Source/OneBossFight/Player/RPGNativeBossHealth.h")
        self.assertIn("class ONEBOSSFIGHT_API IRPGNativeBossHealth", lines[16])
        self.assertIn("virtual double ApplyPlayerHit(double Multiplier) = 0;", lines[23])
        self.assertIn("virtual double ApplyPlayerAttackHit(const FRPGWeaponAttackRow& Row, double Multiplier)", lines[25])

    def test_cpp_citations_framework_boss_character(self):
        """Verifies citations in RPGFrameworkBossCharacter.cpp."""
        lines = self._read_lines("Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp")
        self.assertIn("double ARPGFrameworkBossCharacter::ApplyPlayerAttackHit(const FRPGWeaponAttackRow& Row, double Multiplier)", lines[167])
        self.assertIn("return ApplyHit(double(Row.HealthDamageMultiplier)*Multiplier,double(Row.PostureDamage)*Multiplier,double(Row.BleedBuildup)*Multiplier);", lines[170])

    def test_cpp_citations_input_test_utils(self):
        """Verifies citations in RPGInputTestUtils.h."""
        lines = self._read_lines("Source/OneBossFight/Combat/RPGInputTestUtils.h")
        self.assertIn("class ONEBOSSFIGHT_API URPGInputTestUtils : public UBlueprintFunctionLibrary", lines[16])
        self.assertIn("static bool InjectAction(APlayerController* Controller, UInputAction* Action, FVector Value = FVector(1.0, 0.0, 0.0));", lines[24])
        self.assertIn("static bool SetKeyDown(APlayerController* Controller, FName KeyName, bool bDown);", lines[29])

    def test_plan_document_contents(self):
        """Verifies that KI151_PACK_WEAPON_SWING_PLAN.md contains required sections and analysis."""
        doc_path = self.reviews_dir / "KI151_PACK_WEAPON_SWING_PLAN.md"
        self.assertTrue(doc_path.exists(), "Plan document missing")
        text = doc_path.read_text(encoding="utf-8")

        required_tokens = [
            "KI-151",
            "[C-463]",
            "HandlePackHit",
            "BuildRecord",
            "FinalizePending",
            "SeenMontages",
            "IRPGNativeBossHealth",
            "ApplyPlayerAttackHit",
            "InjectBossAttackHitForTest",
            "URPGInputTestUtils",
            "SetKeyDown",
            "One-Frame Delay",
            "Multi-Blade Merging",
            "Proof Map, Profile Bands, & Card Range Calibration"
        ]
        for token in required_tokens:
            self.assertIn(token, text, f"Token '{token}' missing from KI151_PACK_WEAPON_SWING_PLAN.md")


if __name__ == "__main__":
    unittest.main()
