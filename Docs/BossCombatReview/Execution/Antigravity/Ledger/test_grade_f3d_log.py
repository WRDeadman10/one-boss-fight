#!/usr/bin/env python3
"""
test_grade_f3d_log.py
=====================
Offline unit test suite for F3d log grader (Order A-264).
Tests golden log fixtures, individual failure tokens, timing tolerance boundaries,
band violations, and health invariant guards.
"""

import unittest
import os
import sys
from pathlib import Path

# Ensure import of grade_f3d_log
sys.path.insert(0, str(Path(__file__).resolve().parent))
from grade_f3d_log import grade_log_lines, parse_framework_log, DEFAULT_CARD_SPEC

GOLDEN_LOG = """
LogTemp: Display: [FrameworkProof] dependencies mesh=/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog.Sevarog skeleton=/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog_Skeleton.Sevarog_Skeleton animClass=/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sevarog_AnimBlueprint.Sevarog_AnimBlueprint_C sequence=/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing1_Slow.Swing1_Slow slot=FullBody resolved=1 label=F3_fixture
LogTemp: Display: [FrameworkProof] slot_graph name=FullBody nodeClass=AnimNode_Slot verified=1 label=F3_fixture
LogTemp: Display: [FrameworkProof] nav request=1 projected=X=300.000 Y=0.000 Z=100.000 fullPath=1 result=0
LogTemp: Display: [FrameworkProof] walk start=X=500.000 Y=0.000 Z=100.000 end=X=300.000 Y=0.000 Z=100.000 distanceCm=200.000 rangeCm=300.000 bandMin=250.000 bandMax=350.000 capsule=X=300.000 Y=0.000 Z=100.000 mesh=X=300.000 Y=0.000 Z=0.000
LogTemp: Display: [FrameworkProof] playback_start encounter=1 generation=1 instance=1 montage=/Engine/Transient.OwnedMontage slot=FullBody rate=1 label=F3_fixture
LogTemp: Display: [FrameworkProof] playback instance=1 position=0.1000 nodeWeight=1.0 montageWeight=1.0 base=X=43.0 Y=-70.0 Z=247.0 tip=X=-22.0 Y=-55.0 Z=252.0
LogTemp: Display: [FrameworkProof] playback instance=1 position=0.3500 nodeWeight=1.0 montageWeight=1.0 base=X=40.0 Y=-60.0 Z=250.0 tip=X=-10.0 Y=-40.0 Z=260.0
LogTemp: Display: [FrameworkProof] event encounter=1 generation=1 instance=1 kind=Open window=Window_SwingSlow_Primary group=HitGroup_ScytheBlade localSeconds=0.3500 label=F3_fixture
LogTemp: Display: [FrameworkProof] playback instance=1 position=0.4900 nodeWeight=1.0 montageWeight=1.0 base=X=30.0 Y=-20.0 Z=220.0 tip=X=10.0 Y=10.0 Z=230.0
LogTemp: Display: [FrameworkProof] event encounter=1 generation=1 instance=1 kind=Close window=Window_SwingSlow_Primary group=HitGroup_ScytheBlade localSeconds=0.4917 label=F3_fixture
LogTemp: Display: [FrameworkProof] playback instance=1 position=1.6500 nodeWeight=0.5 montageWeight=0.5 base=X=43.0 Y=-70.0 Z=247.0 tip=X=-22.0 Y=-55.0 Z=252.0
LogTemp: Display: [FrameworkProof] event encounter=1 generation=1 instance=1 kind=Recovery window=None group=None localSeconds=1.6500 label=F3_fixture
LogTemp: Display: [FrameworkProof] playback instance=1 position=1.7000 nodeWeight=0.1 montageWeight=0.1 base=X=43.0 Y=-70.0 Z=247.0 tip=X=-22.0 Y=-55.0 Z=252.0
LogTemp: Display: [FrameworkProof] event encounter=1 generation=1 instance=1 kind=Finished window=None group=None localSeconds=1.6500 label=F3_fixture
LogTemp: Display: [FrameworkProof] cleanup reason=Finished modelIdle=1 ownedMontageStopped=1
LogTemp: Display: [FrameworkProof] invariant targetHPBefore=100 targetHPAfter=100 damageAPIInvocationsByThisExecutor=0
LogTemp: Display: [FrameworkProof] RESULT outcome=CompletedTelemetryOnly
"""

class TestGradeF3dLog(unittest.TestCase):

    def get_lines(self, text: str):
        return parse_framework_log(text)

    def test_golden_log_passes_all_checks(self):
        lines = self.get_lines(GOLDEN_LOG)
        res = grade_log_lines(lines)
        self.assertTrue(res["passed"], f"Golden log should pass: {res['errors']}")
        self.assertEqual(len(res["errors"]), 0)
        self.assertTrue(res["checks"]["no_error_tokens"])
        self.assertTrue(res["checks"]["dependencies_resolved"])
        self.assertTrue(res["checks"]["slot_graph_verified"])
        self.assertTrue(res["checks"]["nav_path_valid"])
        self.assertTrue(res["checks"]["walk_arrival_band"])
        self.assertTrue(res["checks"]["playback_start"])
        self.assertTrue(res["checks"]["playback_frames_observed"])
        self.assertTrue(res["checks"]["events_sequence"])
        self.assertTrue(res["checks"]["cleanup_exact_once"])
        self.assertTrue(res["checks"]["invariant_zero_damage"])
        self.assertTrue(res["checks"]["result_outcome_telemetry"])

    def test_error_token_causes_failure(self):
        # Error occurring during execution (before/without successful RESULT)
        bad_text = GOLDEN_LOG.replace("[FrameworkProof] RESULT outcome=CompletedTelemetryOnly",
                                      "[FrameworkProof] ERROR token=Framework.Playback.EarlyStop bossInactive=1")
        res = grade_log_lines(self.get_lines(bad_text))
        self.assertFalse(res["passed"])
        self.assertFalse(res["checks"]["no_error_tokens"])
        self.assertTrue(any("EarlyStop" in e for e in res["errors"]))

    def test_out_of_band_arrival_causes_failure(self):
        bad_text = GOLDEN_LOG.replace("rangeCm=300.000", "rangeCm=420.000")
        res = grade_log_lines(self.get_lines(bad_text))
        self.assertFalse(res["passed"])
        self.assertFalse(res["checks"]["walk_arrival_band"])
        self.assertTrue(any("outside band" in e for e in res["errors"]))

    def test_zero_walk_distance_causes_failure(self):
        bad_text = GOLDEN_LOG.replace("distanceCm=200.000", "distanceCm=0.000")
        res = grade_log_lines(self.get_lines(bad_text))
        self.assertFalse(res["passed"])
        self.assertFalse(res["checks"]["walk_arrival_band"])

    def test_missing_slot_graph_verification_fails(self):
        bad_text = GOLDEN_LOG.replace("slot_graph name=FullBody nodeClass=AnimNode_Slot verified=1", "slot_graph name=UpperBody nodeClass=None verified=0")
        res = grade_log_lines(self.get_lines(bad_text))
        self.assertFalse(res["passed"])
        self.assertFalse(res["checks"]["slot_graph_verified"])

    def test_event_timing_violation_fails(self):
        # Open at 0.10s instead of 0.35s
        bad_text = GOLDEN_LOG.replace("kind=Open window=Window_SwingSlow_Primary group=HitGroup_ScytheBlade localSeconds=0.3500",
                                      "kind=Open window=Window_SwingSlow_Primary group=HitGroup_ScytheBlade localSeconds=0.1000")
        res = grade_log_lines(self.get_lines(bad_text))
        self.assertFalse(res["passed"])
        self.assertFalse(res["checks"]["events_sequence"])
        self.assertTrue(any("exceeds tolerance" in e for e in res["errors"]))

    def test_missing_finished_event_fails(self):
        bad_text = "\n".join(l for l in GOLDEN_LOG.splitlines() if "kind=Finished" not in l)
        res = grade_log_lines(self.get_lines(bad_text))
        self.assertFalse(res["passed"])
        self.assertFalse(res["checks"]["events_sequence"])

    def test_double_cleanup_or_abort_fails(self):
        bad_text = GOLDEN_LOG + "\nLogTemp: Display: [FrameworkProof] cleanup reason=EndPlay modelIdle=1 ownedMontageStopped=1"
        res = grade_log_lines(self.get_lines(bad_text))
        self.assertFalse(res["passed"])
        self.assertFalse(res["checks"]["cleanup_exact_once"])

    def test_target_health_changed_invariant_fails(self):
        bad_text = GOLDEN_LOG.replace("targetHPBefore=100 targetHPAfter=100", "targetHPBefore=100 targetHPAfter=75")
        res = grade_log_lines(self.get_lines(bad_text))
        self.assertFalse(res["passed"])
        self.assertFalse(res["checks"]["invariant_zero_damage"])

    def test_damage_invocations_greater_than_zero_fails(self):
        bad_text = GOLDEN_LOG.replace("damageAPIInvocationsByThisExecutor=0", "damageAPIInvocationsByThisExecutor=1")
        res = grade_log_lines(self.get_lines(bad_text))
        self.assertFalse(res["passed"])
        self.assertFalse(res["checks"]["invariant_zero_damage"])

    def test_nav_path_invalid_fails(self):
        bad_text = GOLDEN_LOG.replace("fullPath=1", "fullPath=0")
        res = grade_log_lines(self.get_lines(bad_text))
        self.assertFalse(res["passed"])
        self.assertFalse(res["checks"]["nav_path_valid"])

    def test_missing_result_token_fails(self):
        bad_text = "\n".join(l for l in GOLDEN_LOG.splitlines() if "RESULT" not in l)
        res = grade_log_lines(self.get_lines(bad_text))
        self.assertFalse(res["passed"])
        self.assertFalse(res["checks"]["result_outcome_telemetry"])

    def test_montage_natural_end_optional_accepted(self):
        log_with_natural = GOLDEN_LOG.replace("[FrameworkProof] cleanup reason=Finished",
                                              "[FrameworkProof] montage_natural_end position=1.6600 threshold=1.6600\nLogTemp: Display: [FrameworkProof] cleanup reason=Finished")
        res = grade_log_lines(self.get_lines(log_with_natural))
        self.assertTrue(res["passed"])
        self.assertIn("montage_natural_end", res["parsed_data"])

    def test_post_success_teardown_error_ignored(self):
        # Post-result teardown errors (e.g. PossessionChanged during PIE exit) should not fail the test
        log_with_teardown = GOLDEN_LOG + "\nLogTemp: Error: [FrameworkProof] ERROR token=Framework.Fixture.PossessionChanged fixtureInactive=1"
        res = grade_log_lines(self.get_lines(log_with_teardown))
        self.assertTrue(res["passed"], f"Post-RESULT teardown error should be ignored: {res['errors']}")

if __name__ == "__main__":
    unittest.main()
