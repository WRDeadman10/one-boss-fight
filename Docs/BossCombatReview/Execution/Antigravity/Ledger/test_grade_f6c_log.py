#!/usr/bin/env python3
"""
test_grade_f6c_log.py
=====================
Unit tests for Antigravity F6c Phase Authority Grader (Lead Orders C-429, C-432).
Runs 100% offline with zero engine dependency.

Verifies all validation checks across pass and targeted failure synthetic logs:
1. Valid phase transition run (Phase 1 -> Phase 2 -> partitioned decisions) (PASS)
2. Valid run with encounter_reset (Phase 1 -> Phase 2 -> Reset -> Gen 2 Phase 1) (PASS)
3. Unhandled ERROR line before RESULT (FAIL)
4. Missing phase_transition event (FAIL)
5. Transition triggered above health threshold (e.g. 80% > 60%) (FAIL)
6. Neutral gate violation (transition during active attack playback) (FAIL)
7. Phase 2 card selected while in Phase 1 (FAIL)
8. Phase 1 card selected while in Phase 2 (FAIL)
9. Duplicate/non-monotonic phase transition in same generation (FAIL)
10. Missing RESULT line (FAIL)
11. Failed RESULT outcome (FAIL)
12. Targeted KI-149 expectation match (gen=1,attack=3,phase=Phase_1) passes (PASS)
13. Targeted KI-149 attack mismatch fails closed (FAIL)
14. Targeted KI-149 phase mismatch fails closed (FAIL)
15. Targeted KI-149 generation mismatch fails closed (FAIL)
16. Malformed KI-149 spec fails closed (FAIL)
17. KI-149 flag fails when NoCandidate error is not emitted (FAIL)
"""

import unittest
from typing import List
from pathlib import Path
import sys

cur_dir = str(Path(__file__).resolve().parent)
if cur_dir not in sys.path:
    sys.path.insert(0, cur_dir)

from grade_f6c_log import grade_f6c_log_lines


def make_valid_phase_transition_log() -> List[str]:
    """Generates a synthetic passing F6c log: Phase 1 -> Phase 2 transition."""
    return [
        "[FrameworkProof] dependencies mesh=Sevarog resolved=1 label=F6c_fixture",
        "[FrameworkProof] boss_health max=250 playerHitDamage=65 label=F6c_fixture",
        "[FrameworkProof] walk start=X=500 rangeCm=165.0 bandMin=150 bandMax=180",
        # Attack 1: in Phase 1, evaluate candidates
        "[FrameworkProof] candidate attack=1 card=Move_Sevarog_SwingSlow_F7 score=0.85",
        "[FrameworkProof] refusal attack=1 card=Move_Sevarog_SwingMedium_F7_P2 reason=MoveModel.Phase",
        "[FrameworkProof] decision attack=1 generation=1 chosen=Move_Sevarog_SwingSlow_F7 score=0.85 range=165.0 phase=Phase_1",
        "[FrameworkProof] playback_start encounter=1 generation=1 instance=1 montage=Montage_0 slot=FullBody rate=1.0",
        "[FrameworkProof] cleanup attack=1 reason=Finished modelIdle=1 ownedMontageStopped=1",
        # Damage applied: Boss HP drops from 250 to 120 (120/250 = 48% <= 60% threshold)
        "[FrameworkProof] boss_hit attack=1 source=injected damage=130.0 healthBefore=250.0 healthAfter=120.0",
        "[FrameworkProof] boss_health_read reader=ReadAttribute value=120.0 max=250.0",
        # Neutral gate: Boss evaluates transition
        "[FrameworkProof] phase_transition started from=Phase_1 to=Phase_2 health=120.0 maxHealth=250.0 threshold=0.60 generation=1",
        # Attack 2: in Phase 2, evaluate candidates
        "[FrameworkProof] candidate attack=2 card=Move_Sevarog_SwingMedium_F7_P2 score=0.92",
        "[FrameworkProof] refusal attack=2 card=Move_Sevarog_SwingSlow_F7 reason=MoveModel.Phase",
        "[FrameworkProof] decision attack=2 generation=1 chosen=Move_Sevarog_SwingMedium_F7_P2 score=0.92 range=165.0 phase=Phase_2",
        "[FrameworkProof] playback_start encounter=1 generation=1 instance=2 montage=Montage_1 slot=FullBody rate=1.0",
        "[FrameworkProof] cleanup attack=2 reason=Finished modelIdle=1 ownedMontageStopped=1",
        "[FrameworkProof] RESULT outcome=CompletedWithDamage acceptedHits=2 attacks=2"
    ]


def make_valid_transition_with_reset_log() -> List[str]:
    """Generates a synthetic passing F6c log with encounter reset."""
    lines = make_valid_phase_transition_log()[:-1]  # Exclude RESULT
    lines.extend([
        # Fixture triggers encounter_reset for generation 2
        "[FrameworkProof] encounter_reset generation=2 oldState=Neutral executorRearmed=1 bossHealth=250 targetHealth=800",
        "[FrameworkProof] walk start=X=500 rangeCm=165.0 bandMin=150 bandMax=180",
        # Generation 2 starts in Phase 1 again
        "[FrameworkProof] candidate attack=1 card=Move_Sevarog_SwingSlow_F7 score=0.85",
        "[FrameworkProof] refusal attack=1 card=Move_Sevarog_SwingMedium_F7_P2 reason=MoveModel.Phase",
        "[FrameworkProof] decision attack=1 generation=2 chosen=Move_Sevarog_SwingSlow_F7 score=0.85 range=165.0 phase=Phase_1",
        "[FrameworkProof] playback_start encounter=1 generation=2 instance=3 montage=Montage_0 slot=FullBody rate=1.0",
        "[FrameworkProof] cleanup attack=1 reason=Finished modelIdle=1 ownedMontageStopped=1",
        "[FrameworkProof] RESULT outcome=CompletedWithReset generation=2"
    ])
    return lines


class TestGradeF6cLog(unittest.TestCase):

    def test_valid_phase_transition_log_passes(self):
        lines = make_valid_phase_transition_log()
        report = grade_f6c_log_lines(lines)
        self.assertTrue(report["passed"], f"Valid log must pass: {report['errors']}")
        self.assertTrue(report["checks"]["no_error_tokens"])
        self.assertTrue(report["checks"]["phase_transition_emitted"])
        self.assertTrue(report["checks"]["threshold_respected"])
        self.assertTrue(report["checks"]["neutral_gate_adherence"])
        self.assertTrue(report["checks"]["phase_partitioning_decisions"])
        self.assertTrue(report["checks"]["monotonicity_and_idempotence"])
        self.assertTrue(report["checks"]["generation_reset_handling"])
        self.assertTrue(report["checks"]["result_validity"])

    def test_valid_transition_with_reset_passes(self):
        lines = make_valid_transition_with_reset_log()
        report = grade_f6c_log_lines(lines)
        self.assertTrue(report["passed"], f"Valid log with reset must pass: {report['errors']}")

    def test_unhandled_error_fails(self):
        lines = make_valid_phase_transition_log()
        lines.insert(2, "[FrameworkProof] ERROR: Null move card reference in selector")
        report = grade_f6c_log_lines(lines)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["no_error_tokens"])

    def test_missing_phase_transition_fails(self):
        lines = [l for l in make_valid_phase_transition_log() if "phase_transition" not in l]
        report = grade_f6c_log_lines(lines)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["phase_transition_emitted"])

    def test_transition_above_threshold_fails(self):
        lines = make_valid_phase_transition_log()
        lines = [
            l.replace("health=120.0", "health=200.0") if "phase_transition" in l else l
            for l in lines
        ]
        report = grade_f6c_log_lines(lines)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["threshold_respected"])
        self.assertTrue(any("threshold" in e for e in report["errors"]))

    def test_neutral_gate_violation_fails(self):
        lines = make_valid_phase_transition_log()
        trans_line = [l for l in lines if "phase_transition" in l][0]
        lines = [l for l in lines if "phase_transition" not in l]
        pb_idx = [i for i, l in enumerate(lines) if "playback_start" in l][0]
        lines.insert(pb_idx + 1, trans_line)
        report = grade_f6c_log_lines(lines)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["neutral_gate_adherence"])
        self.assertTrue(any("neutral gate violation" in e for e in report["errors"]))

    def test_phase2_card_chosen_in_phase1_fails(self):
        lines = make_valid_phase_transition_log()
        lines = [
            l.replace("chosen=Move_Sevarog_SwingSlow_F7", "chosen=Move_Sevarog_SwingMedium_F7_P2")
            if "decision attack=1" in l else l
            for l in lines
        ]
        report = grade_f6c_log_lines(lines)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["phase_partitioning_decisions"])
        self.assertTrue(any("selected Phase 2 card" in e for e in report["errors"]))

    def test_phase1_card_chosen_in_phase2_fails(self):
        lines = make_valid_phase_transition_log()
        lines = [
            l.replace("chosen=Move_Sevarog_SwingMedium_F7_P2", "chosen=Move_Sevarog_SwingSlow_F7")
            if "decision attack=2" in l else l
            for l in lines
        ]
        report = grade_f6c_log_lines(lines)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["phase_partitioning_decisions"])
        self.assertTrue(any("selected Phase 1 card" in e for e in report["errors"]))

    def test_duplicate_phase_transition_fails(self):
        lines = make_valid_phase_transition_log()
        trans_idx = [i for i, l in enumerate(lines) if "phase_transition" in l][0]
        lines.insert(trans_idx + 1, lines[trans_idx])
        report = grade_f6c_log_lines(lines)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["monotonicity_and_idempotence"])
        self.assertTrue(any("logged 2 phase transitions" in e for e in report["errors"]))

    def test_missing_result_line_fails(self):
        lines = [l for l in make_valid_phase_transition_log() if not l.startswith("[FrameworkProof] RESULT")]
        report = grade_f6c_log_lines(lines)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["result_validity"])

    def test_failed_result_line_fails(self):
        lines = make_valid_phase_transition_log()
        lines[-1] = "[FrameworkProof] RESULT outcome=Failed error=MoveModel.Phase"
        report = grade_f6c_log_lines(lines)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["result_validity"])

    def test_targeted_ki149_matches_and_passes(self):
        lines = make_valid_phase_transition_log()
        lines.append("[FrameworkProof] refusal attack=3 card=Move_Sevarog_SwingSlow_F7 reason=Selector.Cooldown")
        lines.append("[FrameworkProof] cleanup reason=Framework.Selector.NoCandidate modelIdle=1 ownedMontageStopped=1")
        lines.append("[FrameworkProof] ERROR token=Framework.Selector.NoCandidate bossInactive=1")
        lines.append("[FrameworkProof] ERROR token=Framework.Fixture.PossessionChanged fixtureInactive=1")

        # In this log, phase transition happened at line index 10, so Attack 3 is in Phase 2, Generation 1
        report = grade_f6c_log_lines(lines, expect_ki149="gen=1,attack=3,phase=Phase_2")
        self.assertTrue(report["passed"], f"Expected targeted KI-149 must pass: {report['errors']}")
        self.assertTrue(report["checks"]["no_error_tokens"])
        self.assertIn("KI-149", report["summary"])

    def test_targeted_ki149_attack_mismatch_fails(self):
        lines = make_valid_phase_transition_log()
        lines.append("[FrameworkProof] refusal attack=3 card=Move_Sevarog_SwingSlow_F7 reason=Selector.Cooldown")
        lines.append("[FrameworkProof] cleanup reason=Framework.Selector.NoCandidate modelIdle=1 ownedMontageStopped=1")
        lines.append("[FrameworkProof] ERROR token=Framework.Selector.NoCandidate bossInactive=1")

        report = grade_f6c_log_lines(lines, expect_ki149="gen=1,attack=4,phase=Phase_2")
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["no_error_tokens"])
        self.assertTrue(any("attack mismatch" in e for e in report["errors"]))

    def test_targeted_ki149_phase_mismatch_fails(self):
        lines = make_valid_phase_transition_log()
        lines.append("[FrameworkProof] refusal attack=3 card=Move_Sevarog_SwingSlow_F7 reason=Selector.Cooldown")
        lines.append("[FrameworkProof] cleanup reason=Framework.Selector.NoCandidate modelIdle=1 ownedMontageStopped=1")
        lines.append("[FrameworkProof] ERROR token=Framework.Selector.NoCandidate bossInactive=1")

        report = grade_f6c_log_lines(lines, expect_ki149="gen=1,attack=3,phase=Phase_1")
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["no_error_tokens"])
        self.assertTrue(any("phase mismatch" in e for e in report["errors"]))

    def test_targeted_ki149_generation_mismatch_fails(self):
        lines = make_valid_phase_transition_log()
        lines.append("[FrameworkProof] refusal attack=3 card=Move_Sevarog_SwingSlow_F7 reason=Selector.Cooldown")
        lines.append("[FrameworkProof] cleanup reason=Framework.Selector.NoCandidate modelIdle=1 ownedMontageStopped=1")
        lines.append("[FrameworkProof] ERROR token=Framework.Selector.NoCandidate bossInactive=1")

        report = grade_f6c_log_lines(lines, expect_ki149="gen=2,attack=3,phase=Phase_2")
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["no_error_tokens"])
        self.assertTrue(any("generation mismatch" in e for e in report["errors"]))

    def test_malformed_ki149_spec_fails(self):
        lines = make_valid_phase_transition_log()
        report = grade_f6c_log_lines(lines, expect_ki149="invalid_no_equals_token")
        self.assertFalse(report["passed"])
        self.assertTrue(any("Invalid --expect-ki149" in e for e in report["errors"]))

    def test_ki149_flag_fails_when_no_candidate_not_emitted(self):
        lines = make_valid_phase_transition_log()
        report = grade_f6c_log_lines(lines, expect_ki149="gen=1,attack=3,phase=Phase_2")
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["no_error_tokens"])
        self.assertTrue(any("was not emitted" in e for e in report["errors"]))


if __name__ == "__main__":
    unittest.main()
