#!/usr/bin/env python3
"""
test_grade_f9_log.py
====================
Unit test suite for Antigravity F9 Bleed / Ailment Grader (grade_f9_log.py).
Verifies positive and fail-closed negative tamper test cases per Lead Order C-453.
"""

import sys
from pathlib import Path

# Ensure directory is in sys.path for isolated 'python -I' invocations
sys.path.insert(0, str(Path(__file__).resolve().parent))

import unittest
from typing import List

from grade_f9_log import grade_f9_log_lines, grade_f9_file


class TestGradeF9Log(unittest.TestCase):
    """Test suite for grade_f9_log.py verification rules."""

    def make_baseline_log(self) -> List[str]:
        return [
            "[FrameworkProof] boss_health max=250 playerHitDamage=100",
            "[FrameworkProof] walk start=X=500 Y=0 Z=167 end=X=129 Y=0 Z=167",
            "[FrameworkProof] decision attack=1 chosen=Move_HeavySlam phase=Phase_1",
            "[FrameworkProof] playback_start encounter=1 generation=1 instance=1",
            "[FrameworkProof] boss_hit damage=100 healthBefore=250 healthAfter=150",
            "[FrameworkProof] bleed_buildup amount=60 buildup=60 threshold=100 result=added",
            "[FrameworkProof] boss_hit damage=100 healthBefore=150 healthAfter=50",
            "[FrameworkProof] bleed_buildup amount=60 buildup=0 threshold=120 result=proc",
            "[FrameworkProof] bleed_proc procs=1 damage=49 healthBefore=50 healthAfter=1 nextThreshold=120",
            "[FrameworkProof] phase_transition attack=2 from=Phase_1 to=Phase_2 health=1 max=250 fraction=0.5",
            "[FrameworkProof] decision attack=2 chosen=Move_SwingMedium phase=Phase_2",
            "[FrameworkProof] playback_start encounter=1 generation=1 instance=2",
            "[FrameworkProof] RESULT outcome=CompletedWithDamage acceptedHits=1 attacks=2"
        ]

    def test_01_baseline_passes(self):
        lines = self.make_baseline_log()
        res = grade_f9_log_lines(lines)
        self.assertTrue(res["passed"], f"Expected baseline to pass, got: {res['errors']}")
        self.assertEqual(len(res["errors"]), 0)
        self.assertEqual(res["parsed_data"]["procs_total"], 1)
        self.assertEqual(res["parsed_data"]["buildup_event_count"], 2)

    def test_02_restart_lifecycle_passes(self):
        lines = self.make_baseline_log()[:-1] + [
            "[FrameworkProof] boss_hit damage=1 healthBefore=1 healthAfter=0",
            "[FrameworkProof] boss_dead generation=1 executorAborted=1",
            "[FrameworkProof] RESULT outcome=BossDefeated acceptedHits=1 attacks=2",
            "[FrameworkProof] encounter_reset generation=2 oldState=Dead executorRearmed=1 bossHealth=250 targetHealth=800",
            "[FrameworkProof] boss_hit damage=100 healthBefore=250 healthAfter=150",
            "[FrameworkProof] bleed_buildup amount=60 buildup=60 threshold=100 result=added",
            "[FrameworkProof] RESULT outcome=CompletedWithDamage acceptedHits=2 attacks=2"
        ]
        res = grade_f9_log_lines(lines)
        self.assertTrue(res["passed"], f"Expected lifecycle restart to pass, got: {res['errors']}")
        self.assertEqual(res["parsed_data"]["buildup_event_count"], 3)
        self.assertEqual(res["parsed_data"]["final_threshold"], 100.0)

    def test_03_expect_no_bleed_clean_log(self):
        lines = [
            "[FrameworkProof] boss_health max=250 playerHitDamage=100",
            "[FrameworkProof] boss_hit damage=100 healthBefore=250 healthAfter=150",
            "[FrameworkProof] RESULT outcome=CompletedWithDamage acceptedHits=1 attacks=1"
        ]
        res = grade_f9_log_lines(lines, expect_no_bleed=True)
        self.assertTrue(res["passed"], f"Expected clean log without bleed to pass, got: {res['errors']}")

    def test_04_tamper_expect_no_bleed_fails_on_bleed(self):
        lines = self.make_baseline_log()
        res = grade_f9_log_lines(lines, expect_no_bleed=True)
        self.assertFalse(res["passed"])
        self.assertTrue(any("Found unexpected bleed" in err for err in res["errors"]))

    def test_05_tamper_missing_proc_after_result_proc(self):
        # Remove the bleed_proc line following result=proc
        lines = [l for l in self.make_baseline_log() if "bleed_proc" not in l]
        res = grade_f9_log_lines(lines)
        self.assertFalse(res["passed"])
        self.assertTrue(any("was not followed immediately by bleed_proc" in err for err in res["errors"]))

    def test_06_tamper_buildup_math_mismatch(self):
        lines = self.make_baseline_log()
        # Tamper buildup=60 to buildup=70 on added
        lines = [l.replace("buildup=60", "buildup=70") if "result=added" in l else l for l in lines]
        res = grade_f9_log_lines(lines)
        self.assertFalse(res["passed"])
        self.assertTrue(any("has buildup=70.0, expected 60.0" in err for err in res["errors"]))

    def test_07_tamper_bleed_proc_kills_boss(self):
        lines = self.make_baseline_log()
        # Tamper bleed_proc to deal 50 damage leaving 0 health (lethal proc violation)
        lines = [
            l.replace("damage=49 healthBefore=50 healthAfter=1", "damage=50 healthBefore=50 healthAfter=0")
            if "bleed_proc" in l else l
            for l in lines
        ]
        res = grade_f9_log_lines(lines)
        self.assertFalse(res["passed"])
        self.assertTrue(any("violates non-lethal contract" in err for err in res["errors"]))

    def test_08_tamper_threshold_math_mismatch(self):
        lines = self.make_baseline_log()
        # Tamper nextThreshold=120 to nextThreshold=150
        lines = [l.replace("nextThreshold=120", "nextThreshold=150") if "bleed_proc" in l else l for l in lines]
        res = grade_f9_log_lines(lines)
        self.assertFalse(res["passed"])
        self.assertTrue(any("does not match expected 120.0" in err for err in res["errors"]))

    def test_09_tamper_dead_boss_buildup(self):
        lines = self.make_baseline_log()[:-1] + [
            "[FrameworkProof] boss_dead generation=1 executorAborted=1",
            "[FrameworkProof] bleed_buildup amount=60 buildup=60 threshold=100 result=added",
            "[FrameworkProof] RESULT outcome=BossDefeated"
        ]
        res = grade_f9_log_lines(lines)
        self.assertFalse(res["passed"])
        self.assertTrue(any("bleed_buildup on dead boss" in err for err in res["errors"]))

    def test_10_tamper_explicit_error_in_log(self):
        lines = self.make_baseline_log() + [
            "[FrameworkProof] ERROR: Token verification failed"
        ]
        res = grade_f9_log_lines(lines)
        self.assertFalse(res["passed"])
        self.assertTrue(any("Explicit error detected" in err for err in res["errors"]))

    def test_11_tamper_missing_result(self):
        lines = [l for l in self.make_baseline_log() if "RESULT" not in l]
        res = grade_f9_log_lines(lines)
        self.assertFalse(res["passed"])
        self.assertTrue(any("No valid [FrameworkProof] RESULT line found" in err for err in res["errors"]))


if __name__ == "__main__":
    unittest.main()
