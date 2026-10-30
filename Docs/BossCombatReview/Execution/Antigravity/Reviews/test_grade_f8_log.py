#!/usr/bin/env python3
"""
test_grade_f8_log.py
====================
Unit test suite for Antigravity F8 Posture and Stance Break Grader (grade_f8_log.py).
Verifies positive and fail-closed negative tamper test cases per Lead Orders C-447, C-448, C-449, C-450.
"""

import sys
from pathlib import Path

# Ensure directory is in sys.path for isolated 'python -I' invocations
sys.path.insert(0, str(Path(__file__).resolve().parent))

import unittest
from typing import List

from grade_f8_log import grade_f8_log_lines, grade_f8_file


class TestGradeF8Log(unittest.TestCase):
    """Test suite for grade_f8_log.py verification rules."""

    def make_baseline_log(self) -> List[str]:
        return [
            "[FrameworkProof] boss_health max=250 playerHitDamage=100",
            "[FrameworkProof] walk start=X=500 Y=0 Z=167 end=X=129 Y=0 Z=167",
            "[FrameworkProof] decision attack=1 chosen=Move_HeavySlam phase=Phase_1",
            "[FrameworkProof] playback_start encounter=1 generation=1 instance=1",
            "[FrameworkProof] boss_hit damage=100 healthBefore=250 healthAfter=150",
            "[FrameworkProof] posture_drain amount=60 postureBefore=100 postureAfter=40 max=100",
            "[FrameworkProof] boss_hit damage=100 healthBefore=150 healthAfter=50",
            "[FrameworkProof] posture_drain amount=40 postureBefore=40 postureAfter=0 max=100",
            "[FrameworkProof] cleanup reason=StanceBreak modelIdle=1 ownedMontageStopped=1",
            "[FrameworkProof] stance_break state=MidAttack duration=1 generation=1 phase=Phase_1",
            "[FrameworkProof] stagger_recovery postureRefilled=100 generation=1",
            "[FrameworkProof] phase_transition attack=1 from=Phase_1 to=Phase_2 health=50 max=250 fraction=0.5",
            "[FrameworkProof] decision attack=2 chosen=Move_SwingMedium phase=Phase_2",
            "[FrameworkProof] playback_start encounter=1 generation=1 instance=2",
            "[FrameworkProof] RESULT outcome=CompletedWithDamage acceptedHits=1 attacks=2"
        ]

    def test_01_baseline_passes(self):
        lines = self.make_baseline_log()
        res = grade_f8_log_lines(lines)
        self.assertTrue(res["passed"], f"Expected baseline to pass, got: {res['errors']}")
        self.assertEqual(len(res["errors"]), 0)
        self.assertEqual(len(res["parsed_data"]["stance_breaks"]), 1)
        self.assertEqual(len(res["parsed_data"]["stagger_recoveries"]), 1)

    def test_02_posture_drain_math_mismatch_fails(self):
        lines = self.make_baseline_log()
        # Corrupt before - amount != after: 100 - 60 != 50
        lines[5] = "[FrameworkProof] posture_drain amount=60 postureBefore=100 postureAfter=50 max=100"
        res = grade_f8_log_lines(lines)
        self.assertFalse(res["passed"])
        self.assertTrue(any("math mismatch" in err for err in res["errors"]))

    def test_03_incomplete_drain_before_break_fails(self):
        lines = self.make_baseline_log()
        # Only 60 drained, but break triggered (sum 60 != max 100)
        del lines[6:8]  # remove second hit and second drain
        res = grade_f8_log_lines(lines)
        self.assertFalse(res["passed"])
        self.assertTrue(any("does not equal max posture" in err for err in res["errors"]))

    def test_04_break_without_reaching_zero_fails(self):
        lines = self.make_baseline_log()
        # Second drain only drains 30 so postureAfter=10 != 0
        lines[7] = "[FrameworkProof] posture_drain amount=30 postureBefore=40 postureAfter=10 max=100"
        res = grade_f8_log_lines(lines)
        self.assertFalse(res["passed"])
        self.assertTrue(any("without prior posture drain reaching 0" in err for err in res["errors"]))

    def test_05_break_after_boss_dead_fails(self):
        lines = self.make_baseline_log()
        # Insert boss_dead before stance_break
        lines.insert(8, "[FrameworkProof] boss_dead generation=1")
        res = grade_f8_log_lines(lines)
        self.assertFalse(res["passed"])
        self.assertTrue(any("while boss is dead" in err for err in res["errors"]))

    def test_06_midattack_break_without_preceding_cleanup_fails(self):
        lines = self.make_baseline_log()
        # Remove cleanup reason=StanceBreak
        del lines[8]
        res = grade_f8_log_lines(lines)
        self.assertFalse(res["passed"])
        self.assertTrue(any("cleanup reason=StanceBreak" in err for err in res["errors"]))

    def test_07_neutral_break_without_cleanup_passes(self):
        lines = self.make_baseline_log()
        # Neutral break after walk has already started
        lines[9] = "[FrameworkProof] stance_break state=Neutral duration=1 generation=1 phase=Phase_1"
        del lines[8]
        res = grade_f8_log_lines(lines)
        self.assertTrue(res["passed"], f"Neutral break without cleanup should pass, got: {res['errors']}")

    def test_08_decision_during_stagger_fails(self):
        lines = self.make_baseline_log()
        # Insert decision between stance_break (idx 9) and stagger_recovery (idx 10)
        lines.insert(10, "[FrameworkProof] decision attack=1 chosen=Move_HeavySlam phase=Phase_1")
        res = grade_f8_log_lines(lines)
        self.assertFalse(res["passed"])
        self.assertTrue(any("while boss is staggered" in err for err in res["errors"]))

    def test_09_playback_during_stagger_fails(self):
        lines = self.make_baseline_log()
        # Insert playback_start between stance_break (idx 9) and stagger_recovery (idx 10)
        lines.insert(10, "[FrameworkProof] playback_start encounter=1 generation=1 instance=2")
        res = grade_f8_log_lines(lines)
        self.assertFalse(res["passed"])
        self.assertTrue(any("playback_start emitted while boss is staggered" in err for err in res["errors"]))

    def test_10_recovery_wrong_refill_amount_fails(self):
        lines = self.make_baseline_log()
        # Refilled 80 instead of max 100
        lines[10] = "[FrameworkProof] stagger_recovery postureRefilled=80 generation=1"
        res = grade_f8_log_lines(lines)
        self.assertFalse(res["passed"])
        self.assertTrue(any("does not match max posture" in err for err in res["errors"]))

    def test_11_phase_transition_while_staggered_fails(self):
        lines = self.make_baseline_log()
        # Move phase_transition to BEFORE stagger_recovery
        pt = lines.pop(11)
        lines.insert(10, pt)
        res = grade_f8_log_lines(lines)
        self.assertFalse(res["passed"])
        self.assertTrue(any("phase_transition fired while boss was staggered" in err for err in res["errors"]))

    def test_12_stagger_leak_across_encounter_reset_fails(self):
        lines = self.make_baseline_log()
        # Replace stagger_recovery with encounter_reset while still alive and staggered
        lines[10] = "[FrameworkProof] encounter_reset generation=2 oldState=Idle"
        res = grade_f8_log_lines(lines)
        self.assertFalse(res["passed"])
        self.assertTrue(any("actively staggered without prior death" in err for err in res["errors"]))

    def test_13_death_during_stagger_closes_cleanly(self):
        # Lethal hit during stagger terminates stagger cleanly
        lines = [
            "[FrameworkProof] boss_health max=250 playerHitDamage=100",
            "[FrameworkProof] decision attack=1 chosen=Move_HeavySlam phase=Phase_1",
            "[FrameworkProof] playback_start encounter=1 generation=1 instance=1",
            "[FrameworkProof] boss_hit damage=100 healthBefore=250 healthAfter=150",
            "[FrameworkProof] posture_drain amount=60 postureBefore=100 postureAfter=40 max=100",
            "[FrameworkProof] boss_hit damage=100 healthBefore=150 healthAfter=50",
            "[FrameworkProof] posture_drain amount=40 postureBefore=40 postureAfter=0 max=100",
            "[FrameworkProof] cleanup reason=StanceBreak modelIdle=1 ownedMontageStopped=1",
            "[FrameworkProof] stance_break state=MidAttack duration=1 generation=1 phase=Phase_1",
            "[FrameworkProof] boss_hit damage=50 healthBefore=50 healthAfter=0",
            "[FrameworkProof] boss_dead generation=1 executorAborted=1",
            "[FrameworkProof] RESULT outcome=BossDefeated acceptedHits=0 attacks=1",
            "[FrameworkProof] encounter_reset generation=2 oldState=Dead executorRearmed=1",
            "[FrameworkProof] decision attack=1 chosen=Move_HeavySlam phase=Phase_1",
            "[FrameworkProof] playback_start encounter=1 generation=2 instance=2",
            "[FrameworkProof] RESULT outcome=CompletedWithDamage acceptedHits=1 attacks=1"
        ]
        res = grade_f8_log_lines(lines)
        self.assertTrue(res["passed"], f"Death during stagger should pass, got: {res['errors']}")
        self.assertEqual(len(res["parsed_data"]["stance_breaks"]), 1)
        self.assertEqual(len(res["parsed_data"]["deaths"]), 1)

    def test_14_expect_no_posture_mode(self):
        near_lines = [
            "[FrameworkProof] boss_health max=250 playerHitDamage=100",
            "[FrameworkProof] decision attack=1 chosen=Move_HeavySlam phase=Phase_1",
            "[FrameworkProof] playback_start encounter=1 generation=1 instance=1",
            "[FrameworkProof] RESULT outcome=CompletedWithDamage acceptedHits=1 attacks=1"
        ]
        res_ok = grade_f8_log_lines(near_lines, expect_no_posture=True)
        self.assertTrue(res_ok["passed"])

        # Tamper: add a posture line in expect_no_posture mode
        tamper_lines = list(near_lines)
        tamper_lines.insert(2, "[FrameworkProof] posture_drain amount=60 postureBefore=100 postureAfter=40 max=100")
        res_fail = grade_f8_log_lines(tamper_lines, expect_no_posture=True)
        self.assertFalse(res_fail["passed"])
        self.assertTrue(any("Expected no posture lines" in err for err in res_fail["errors"]))

    def test_15_error_token_fails(self):
        lines = self.make_baseline_log()
        lines.append("[FrameworkProof] ERROR token=Framework.Fatal")
        res = grade_f8_log_lines(lines)
        self.assertFalse(res["passed"])
        self.assertFalse(res["checks"]["no_error_tokens"])

    def test_16_neutral_break_walk_resumed_rule(self):
        # Neutral break before walk start: must be followed by stagger_recovery, walk_resumed, then walk start
        valid_neutral = [
            "[FrameworkProof] boss_health max=250 playerHitDamage=100",
            "[FrameworkProof] boss_hit damage=100 healthBefore=250 healthAfter=150",
            "[FrameworkProof] posture_drain amount=60 postureBefore=100 postureAfter=40 max=100",
            "[FrameworkProof] boss_hit damage=100 healthBefore=150 healthAfter=50",
            "[FrameworkProof] posture_drain amount=40 postureBefore=40 postureAfter=0 max=100",
            "[FrameworkProof] stance_break state=Neutral duration=1 generation=1 phase=Phase_1",
            "[FrameworkProof] stagger_recovery postureRefilled=100 generation=1",
            "[FrameworkProof] walk_resumed generation=1",
            "[FrameworkProof] walk start=X=500 Y=0 Z=167 end=X=129 Y=0 Z=167",
            "[FrameworkProof] phase_transition attack=1 from=Phase_1 to=Phase_2 health=50 max=250 fraction=0.5",
            "[FrameworkProof] decision attack=1 chosen=Move_SwingMedium phase=Phase_2",
            "[FrameworkProof] playback_start encounter=1 generation=1 instance=1",
            "[FrameworkProof] RESULT outcome=CompletedWithDamage acceptedHits=1 attacks=1"
        ]
        res = grade_f8_log_lines(valid_neutral)
        self.assertTrue(res["passed"], f"Neutral break with walk_resumed should pass, got: {res['errors']}")

        # Tamper: missing walk_resumed
        missing_resumed = [l for l in valid_neutral if not l.startswith("[FrameworkProof] walk_resumed")]
        res_fail = grade_f8_log_lines(missing_resumed)
        self.assertFalse(res_fail["passed"])
        self.assertTrue(any("without preceding walk_resumed" in err for err in res_fail["errors"]))

    def test_17_all_live_claude_f8_runs(self):
        repo_root = Path(__file__).resolve().parents[5]
        base = repo_root / "Docs" / "BossCombatReview" / "Execution" / "Claude" / "F8"

        test_runs = [
            (base / "pie_run1" / "editor_raw.log", False, True),
            (base / "pie_run2" / "editor_raw.log", False, True),
            (base / "pie_run3" / "editor_raw.log", False, True),
            (base / "death_restart" / "editor_raw.log", False, True),
            (base / "neutral_run1" / "editor_raw.log", False, True),
            (base / "neutral_run2" / "editor_raw.log", False, True),
            (base / "neutral_run3" / "editor_raw.log", False, True),
            (base / "midattack_after_walkfix" / "editor_raw.log", False, True),
            (base / "reg_near" / "editor_raw.log", True, True),
            # Failure runs (contain ERROR / failure tokens)
            (base / "neutral_before_fix" / "editor_raw.log", False, False),
            (base / "diag_neutral" / "editor_raw.log", False, False),
        ]

        for path, no_posture, expect_pass in test_runs:
            if not path.is_file():
                continue
            res = grade_f8_file(path, expect_no_posture=no_posture)
            if expect_pass:
                self.assertTrue(res["passed"], f"Expected PASS for {path.parent.name}, got FAIL: {res['errors']}")
            else:
                self.assertFalse(res["passed"], f"Expected FAIL for {path.parent.name}, but it passed")


if __name__ == "__main__":
    unittest.main()
