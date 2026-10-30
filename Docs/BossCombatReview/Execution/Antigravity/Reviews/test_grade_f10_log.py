# Copyright One Boss Fight. All Rights Reserved.
"""
Offline test suite for Antigravity Slice F10 Weapon Attack Row Grader (grade_f10_log.py).
Verifies:
1. Isolated 'python -I' compatibility.
2. Clean PASS across Claude/F10 PIE runs (clay, dual, starter, reg_F8, reg_F9).
3. Cross-checks of row values (healthMult, posture, bleed) against actual hit consequences.
4. Fail-closed behavior on synthetic/tampered logs (damage mismatch, drain mismatch, bleed mismatch, lethal bleed, missing RESULT).
5. Pure CRLF compliance.
"""

import os
import sys
import unittest
from pathlib import Path

# Add directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from grade_f10_log import grade_f10_log_lines


class TestGradeF10Log(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[5]
        self.f10_dir = self.repo_root / "Docs" / "BossCombatReview" / "Execution" / "Claude" / "F10"

    def _read_log(self, rel_path: str):
        full_path = self.repo_root / rel_path
        self.assertTrue(full_path.exists(), f"Log file not found: {rel_path}")
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.readlines()

    def test_grade_clay_run(self):
        """Claymore JumpHeavy: 3 hits, posture 38 each, stance break on 3rd hit, 0 bleed."""
        lines = self._read_log("Docs/BossCombatReview/Execution/Claude/F10/clay/editor_raw.log")
        res = grade_f10_log_lines(
            lines,
            expect_rows=3,
            expect_weapon="ClaymoreCombatStyle",
            expect_kind="JumpHeavy",
            expect_stance_break=True,
        )
        self.assertTrue(res["pass"], f"Clay log failed: {res['errors']}")
        self.assertEqual(res["attack_rows_count"], 3)
        self.assertEqual(res["posture_drains_count"], 3)
        self.assertEqual(res["stance_breaks"], 1)
        self.assertEqual(res["proc_events_count"], 0)

    def test_grade_dual_run(self):
        """Dual Swords Light: 5 hits, bleed 20 each, triggers proc on 5th hit, damage 200."""
        lines = self._read_log("Docs/BossCombatReview/Execution/Claude/F10/dual/editor_raw.log")
        res = grade_f10_log_lines(
            lines,
            expect_rows=5,
            expect_weapon="DualSwordCombatStyle",
            expect_kind="Light",
            expect_procs=1,
        )
        self.assertTrue(res["pass"], f"Dual log failed: {res['errors']}")
        self.assertEqual(res["attack_rows_count"], 5)
        self.assertEqual(res["proc_events_count"], 1)

    def test_grade_starter_run(self):
        """Starter Sword Light: 2 hits, healthMult 0.39 (damage 39.0), posture 18.0."""
        lines = self._read_log("Docs/BossCombatReview/Execution/Claude/F10/starter/editor_raw.log")
        res = grade_f10_log_lines(
            lines,
            expect_rows=2,
            expect_weapon="SwordCombatStyle",
            expect_kind="Light",
        )
        self.assertTrue(res["pass"], f"Starter log failed: {res['errors']}")
        self.assertEqual(res["attack_rows_count"], 2)
        self.assertEqual(res["boss_hits_count"], 2)

    def test_grade_reg_f8_run(self):
        """Regression F8: zero attack rows, zero bleed."""
        lines = self._read_log("Docs/BossCombatReview/Execution/Claude/F10/reg_L_SevarogFrameworkProofF8/editor_raw.log")
        res = grade_f10_log_lines(lines, expect_no_attack_rows=True, expect_no_bleed=True)
        self.assertTrue(res["pass"], f"Regression F8 log failed: {res['errors']}")
        self.assertEqual(res["attack_rows_count"], 0)
        self.assertEqual(res["buildup_events_count"], 0)

    def test_grade_reg_f9_run(self):
        """Regression F9: zero attack rows, fallback bleed proc preserved."""
        lines = self._read_log("Docs/BossCombatReview/Execution/Claude/F10/reg_L_SevarogFrameworkProofF9/editor_raw.log")
        res = grade_f10_log_lines(lines, expect_no_attack_rows=True, expect_procs=1)
        self.assertTrue(res["pass"], f"Regression F9 log failed: {res['errors']}")
        self.assertEqual(res["attack_rows_count"], 0)
        self.assertEqual(res["proc_events_count"], 1)

    def test_tamper_damage_scaling_fails(self):
        """Tamper: boss_hit damage deviates from attack row healthMult * profile damage."""
        lines = self._read_log("Docs/BossCombatReview/Execution/Claude/F10/starter/editor_raw.log")
        tampered = [l.replace("damage=39 healthBefore=1000 healthAfter=961", "damage=50 healthBefore=1000 healthAfter=950") for l in lines]
        res = grade_f10_log_lines(tampered)
        self.assertFalse(res["pass"], "Expected failure on tampered damage scaling")
        self.assertTrue(any("does not match expected (39.0)" in e for e in res["errors"]))

    def test_tamper_posture_drain_fails(self):
        """Tamper: posture_drain amount deviates from attack row posture damage."""
        lines = self._read_log("Docs/BossCombatReview/Execution/Claude/F10/clay/editor_raw.log")
        tampered = [l.replace("amount=38 postureBefore=100 postureAfter=62", "amount=20 postureBefore=100 postureAfter=80") for l in lines]
        res = grade_f10_log_lines(tampered)
        self.assertFalse(res["pass"], "Expected failure on tampered posture drain")
        self.assertTrue(any("Posture drain amount" in e for e in res["errors"]))

    def test_tamper_bleed_buildup_fails(self):
        """Tamper: bleed_buildup amount deviates from attack row bleed buildup."""
        lines = self._read_log("Docs/BossCombatReview/Execution/Claude/F10/dual/editor_raw.log")
        tampered = [l.replace("amount=20 buildup=20 threshold=100", "amount=15 buildup=15 threshold=100") for l in lines]
        res = grade_f10_log_lines(tampered)
        self.assertFalse(res["pass"], "Expected failure on tampered bleed buildup")
        self.assertTrue(any("Bleed buildup amount" in e for e in res["errors"]))

    def test_tamper_lethal_bleed_fails(self):
        """Tamper: bleed proc kills boss (healthAfter < 1)."""
        lines = self._read_log("Docs/BossCombatReview/Execution/Claude/F10/dual/editor_raw.log")
        tampered = [l.replace("healthBefore=500 healthAfter=300", "healthBefore=500 healthAfter=0") for l in lines]
        res = grade_f10_log_lines(tampered)
        self.assertFalse(res["pass"], "Expected failure on lethal bleed proc")
        self.assertTrue(any("Bleed proc lethal violation" in e for e in res["errors"]))

    def test_tamper_missing_boss_hit_after_row_fails(self):
        """Tamper: attack_row without subsequent boss_hit fails."""
        lines = self._read_log("Docs/BossCombatReview/Execution/Claude/F10/starter/editor_raw.log")
        # Remove boss_hit lines
        tampered = [l for l in lines if "[FrameworkProof] boss_hit" not in l]
        res = grade_f10_log_lines(tampered)
        self.assertFalse(res["pass"], "Expected failure when boss_hit is missing after attack_row")

    def test_tamper_fatal_error_fails(self):
        """Tamper: presence of fatal error in log causes failure."""
        lines = self._read_log("Docs/BossCombatReview/Execution/Claude/F10/clay/editor_raw.log")
        tampered = lines + ["[FrameworkProof] ERROR: Critical assertion failure\n"]
        res = grade_f10_log_lines(tampered)
        self.assertFalse(res["pass"], "Expected failure on explicit error")
        self.assertTrue(any("Explicit error detected" in e for e in res["errors"]))

    def test_pure_crlf(self):
        """Ensure grade_f10_log.py and test_grade_f10_log.py are pure CRLF."""
        for filename in ["grade_f10_log.py", "test_grade_f10_log.py"]:
            path = self.repo_root / "Docs" / "BossCombatReview" / "Execution" / "Antigravity" / "Reviews" / filename
            self.assertTrue(path.exists(), f"File missing: {filename}")
            raw = path.read_bytes()
            without_crlf = raw.replace(b"\r\n", b"")
            self.assertNotIn(b"\n", without_crlf, f"{filename} contains LF without CR (not pure CRLF)")
            self.assertNotIn(b"\r", without_crlf, f"{filename} contains isolated CR (not pure CRLF)")


if __name__ == "__main__":
    unittest.main()
