#!/usr/bin/env python3
"""
test_grade_f6a_log.py
=====================
Unit tests for Antigravity F6a Boss Target Proof Grader (Order A-295 / Lead C-416).
Runs 100% offline with zero engine dependency.

Verifies all validation checks across pass and targeted failure synthetic logs:
1. Valid lethal run (hits -> death -> clean end) (PASS)
2. Valid non-lethal run (boss damaged but alive) (PASS)
3. Unhandled ERROR line before RESULT (FAIL)
4. Damage arithmetic mismatch (damage != before - after) (FAIL)
5. Non-positive damage (FAIL)
6. Non-monotonic health decrease (after >= before) (FAIL)
7. Health continuity gap across sequential hits (FAIL)
8. ReadAttribute value mismatch (FAIL)
9. Missing ReadAttribute line after hit (FAIL)
10. ReadAttribute non-positive max (FAIL)
11. Duplicate boss_dead events (FAIL)
12. Executor not aborted on death (executorAborted=0) (FAIL)
13. Post-mortem decision violation (decision after boss_dead) (FAIL)
14. Post-mortem playback violation (playback_start after boss_dead) (FAIL)
15. Post-mortem player damage violation (damage after boss_dead) (FAIL)
16. Post-mortem hit violation (hit after boss_dead) (FAIL)
17. Zero boss_hit lines found (FAIL)
"""

import unittest
from typing import List
from pathlib import Path
import sys

cur_dir = str(Path(__file__).resolve().parent)
if cur_dir not in sys.path:
    sys.path.insert(0, cur_dir)

from grade_f6a_log import grade_f6a_log_lines


def make_valid_lethal_log() -> List[str]:
    """Generates a synthetic passing lethal F6a log with 2 hits ending in death."""
    return [
        "[FrameworkProof] dependencies mesh=Sevarog resolved=1 label=F6a_fixture",
        "[FrameworkProof] walk start=X=500 rangeCm=165.0 bandMin=150 bandMax=180",
        "[FrameworkProof] decision attack=1 chosen=Move_Sevarog_SwingSlow_F5 score=1.85 range=165.0",
        "[FrameworkProof] playback_start encounter=1 generation=1 instance=1 montage=Montage_0 slot=FullBody rate=1.0",
        # Hit 1 on framework boss: 35 damage, 800 -> 765
        "[FrameworkProof] boss_hit attack=1 source=injected damage=35.0 healthBefore=800.0 healthAfter=765.0",
        "[FrameworkProof] boss_health_read reader=ReadAttribute value=765.0 max=800.0",
        "[FrameworkProof] move_cleanup attack=1 reason=Finished modelIdle=1 ownedMontageStopped=1",
        # Hit 2 on framework boss: lethal blow 765 damage, 765 -> 0.0
        "[FrameworkProof] boss_hit attack=2 source=injected damage=765.0 healthBefore=765.0 healthAfter=0.0",
        "[FrameworkProof] boss_health_read reader=ReadAttribute value=0.0 max=800.0",
        "[FrameworkProof] boss_dead generation=1 executorAborted=1",
        "[FrameworkProof] RESULT PASS hits=2 boss_dead=1"
    ]


def make_valid_non_lethal_log() -> List[str]:
    """Generates a synthetic passing non-lethal F6a log with 1 hit."""
    return [
        "[FrameworkProof] dependencies mesh=Sevarog resolved=1 label=F6a_fixture",
        "[FrameworkProof] walk start=X=500 rangeCm=165.0 bandMin=150 bandMax=180",
        "[FrameworkProof] decision attack=1 chosen=Move_Sevarog_SwingSlow_F5 score=1.85 range=165.0",
        "[FrameworkProof] playback_start encounter=1 generation=1 instance=1 montage=Montage_0 slot=FullBody rate=1.0",
        "[FrameworkProof] boss_hit attack=1 source=injected damage=45.0 healthBefore=800.0 healthAfter=755.0",
        "[FrameworkProof] boss_health_read reader=ReadAttribute value=755.0 max=800.0",
        "[FrameworkProof] move_cleanup attack=1 reason=Finished modelIdle=1 ownedMontageStopped=1",
        "[FrameworkProof] RESULT PASS hits=1 boss_dead=0"
    ]


class TestGradeF6aLog(unittest.TestCase):

    def test_valid_lethal_run(self):
        log = make_valid_lethal_log()
        report = grade_f6a_log_lines(log)
        self.assertTrue(report["passed"], f"Expected PASS, errors: {report['errors']}")
        self.assertEqual(len(report["errors"]), 0)
        self.assertTrue(report["checks"]["has_boss_hits"])
        self.assertTrue(report["checks"]["hits_arithmetic"])
        self.assertTrue(report["checks"]["read_attribute_bridge"])
        self.assertTrue(report["checks"]["single_boss_dead"])
        self.assertTrue(report["checks"]["no_activity_after_death"])
        self.assertTrue(report["checks"]["no_error_tokens"])

    def test_valid_non_lethal_run(self):
        log = make_valid_non_lethal_log()
        report = grade_f6a_log_lines(log)
        self.assertTrue(report["passed"], f"Expected PASS, errors: {report['errors']}")
        self.assertEqual(len(report["errors"]), 0)
        self.assertTrue(report["checks"]["single_boss_dead"])

    def test_error_line_before_result(self):
        log = make_valid_lethal_log()
        log.insert(2, "[FrameworkProof] ERROR: Fatal assertion in HitIntake")
        report = grade_f6a_log_lines(log)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["no_error_tokens"])

    def test_damage_arithmetic_mismatch(self):
        log = make_valid_lethal_log()
        # damage=50 but 800 - 765 = 35
        log[4] = "[FrameworkProof] boss_hit attack=1 source=injected damage=50.0 healthBefore=800.0 healthAfter=765.0"
        report = grade_f6a_log_lines(log)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["hits_arithmetic"])

    def test_non_positive_damage(self):
        log = make_valid_lethal_log()
        log[4] = "[FrameworkProof] boss_hit attack=1 source=injected damage=0.0 healthBefore=800.0 healthAfter=800.0"
        report = grade_f6a_log_lines(log)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["hits_arithmetic"])

    def test_non_monotonic_health(self):
        log = make_valid_lethal_log()
        # after > before
        log[4] = "[FrameworkProof] boss_hit attack=1 source=injected damage=35.0 healthBefore=700.0 healthAfter=735.0"
        report = grade_f6a_log_lines(log)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["hits_arithmetic"])

    def test_continuity_gap(self):
        log = make_valid_lethal_log()
        # hit 1 ends at 765, but hit 2 starts at 750
        log[7] = "[FrameworkProof] boss_hit attack=2 source=injected damage=750.0 healthBefore=750.0 healthAfter=0.0"
        report = grade_f6a_log_lines(log)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["hits_arithmetic"])

    def test_read_attribute_mismatch(self):
        log = make_valid_lethal_log()
        # read reports 700 instead of 765
        log[5] = "[FrameworkProof] boss_health_read reader=ReadAttribute value=700.0 max=800.0"
        report = grade_f6a_log_lines(log)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["read_attribute_bridge"])

    def test_missing_read_attribute(self):
        log = make_valid_lethal_log()
        # remove all read lines
        log = [l for l in log if "boss_health_read" not in l]
        report = grade_f6a_log_lines(log)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["read_attribute_bridge"])

    def test_read_attribute_non_positive_max(self):
        log = make_valid_lethal_log()
        log[5] = "[FrameworkProof] boss_health_read reader=ReadAttribute value=765.0 max=0.0"
        report = grade_f6a_log_lines(log)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["read_attribute_bridge"])

    def test_duplicate_boss_dead(self):
        log = make_valid_lethal_log()
        log.insert(10, "[FrameworkProof] boss_dead generation=1 executorAborted=1")
        report = grade_f6a_log_lines(log)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["single_boss_dead"])

    def test_executor_not_aborted(self):
        log = make_valid_lethal_log()
        log[9] = "[FrameworkProof] boss_dead generation=1 executorAborted=0"
        report = grade_f6a_log_lines(log)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["single_boss_dead"])

    def test_post_mortem_decision(self):
        log = make_valid_lethal_log()
        log.insert(10, "[FrameworkProof] decision attack=3 chosen=Move_Sevarog_SwingSlow_F5 score=1.85 range=165.0")
        report = grade_f6a_log_lines(log)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["no_activity_after_death"])

    def test_post_mortem_playback(self):
        log = make_valid_lethal_log()
        log.insert(10, "[FrameworkProof] playback_start encounter=1 generation=1 instance=3 montage=Montage_0 slot=FullBody rate=1.0")
        report = grade_f6a_log_lines(log)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["no_activity_after_death"])

    def test_post_mortem_player_damage(self):
        log = make_valid_lethal_log()
        log.insert(10, "[FrameworkProof] damage outcome=Accepted move=Move_Sevarog_SwingSlow_F5 instance=3 hpApplied=35.0")
        report = grade_f6a_log_lines(log)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["no_activity_after_death"])

    def test_post_mortem_boss_hit(self):
        log = make_valid_lethal_log()
        log.insert(10, "[FrameworkProof] boss_hit attack=3 source=injected damage=10.0 healthBefore=0.0 healthAfter=-10.0")
        report = grade_f6a_log_lines(log)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["no_activity_after_death"])

    def test_zero_hits_found(self):
        log = [
            "[FrameworkProof] dependencies mesh=Sevarog resolved=1 label=F6a_fixture",
            "[FrameworkProof] RESULT PASS hits=0"
        ]
        report = grade_f6a_log_lines(log)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["has_boss_hits"])


    def test_claude_live_format_run(self):
        """Tests the exact format emitted by Claude's C++ implementation in RPGFrameworkBossCharacter."""
        log = [
            "[FrameworkProof] dependencies mesh=Sevarog resolved=1 label=F6a_fixture",
            "[FrameworkProof] boss_health max=800 playerHitDamage=35 label=F6a_fixture",
            "[FrameworkProof] boss_hit damage=35.0 healthBefore=800.0 healthAfter=765.0",
            "[FrameworkProof] boss_health_read reader=ReadAttribute ok=1 value=765.0 max=800.0",
            "[FrameworkProof] boss_hit damage=765.0 healthBefore=765.0 healthAfter=0.0",
            "[FrameworkProof] boss_health_read reader=ReadAttribute ok=1 value=0.0 max=800.0",
            "[FrameworkProof] boss_dead generation=1 executorAborted=1",
            "[FrameworkProof] RESULT outcome=BossDefeated acceptedHits=0 attacks=1"
        ]
        report = grade_f6a_log_lines(log)
        self.assertTrue(report["passed"], f"Expected PASS for Claude live format, errors: {report['errors']}")
        self.assertEqual(len(report["parsed_data"]["boss_hits"]), 2)
        self.assertEqual(report["parsed_data"]["boss_hits"][0]["attack"], 1)
        self.assertEqual(report["parsed_data"]["boss_hits"][1]["attack"], 2)


if __name__ == "__main__":
    unittest.main()
