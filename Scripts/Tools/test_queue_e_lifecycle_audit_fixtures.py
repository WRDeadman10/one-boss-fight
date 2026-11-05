"""Offline checks that D99-D104 lifecycle/boundary claims map to code tests."""
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BOUNDARIES = "Source/OneBossFight/Tests/RPGBossQueueEBoundaryTests.cpp"


def read_project_file(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8", errors="replace")


class QueueELifecycleAuditFixtures(unittest.TestCase):
    def test_e76_fatigue_start_finish_phase_and_restart_lifecycle_map(self):
        source = read_project_file("Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp")
        self.assertIn("if(!bFatigueFinishedCardSeen)", source)
        self.assertIn("if(Executor->CurrentCardHadContact()) FatigueWhiffs=0; else ++FatigueWhiffs", source)
        self.assertIn("FatigueWhiffs=0;bFatigueFinishedCardSeen=false", source)
        self.assertIn('TEXT("[FrameworkProof] fatigue whiffs=%d scale=%g"),FatigueWhiffs', source)

    def test_e77_punish_use_count_and_defense_clock_gate_are_distinct(self):
        limiter = read_project_file("Source/OneBossFight/Player/RPGBossPunishLimiterRules.h")
        source = read_project_file(BOUNDARIES)
        self.assertIn("struct FState { int32 Uses=0; }", limiter)
        self.assertIn("RecordUse", limiter)
        self.assertNotIn("Cooldown", limiter)
        self.assertIn("immediately below minimum cooldown is rejected", source)
        self.assertIn("exact minimum cooldown is accepted", source)

    def test_e78_reactive_dodge_hit_arithmetic_is_widened_not_an_attempt_budget(self):
        rules = read_project_file("Source/OneBossFight/Player/RPGBossReactiveDodgeRules.h")
        source = read_project_file(BOUNDARIES)
        self.assertIn("int64 HitsSinceThreshold=int64(RecentHits)-int64(C.HitsToStart)+1", rules)
        self.assertIn("Unwired by design", rules)
        self.assertNotIn("struct FState", rules)
        self.assertIn("maximum hit count saturates at configured cap", source)

    def test_e79_retreat_exact_range_and_threat_equality_are_covered(self):
        source = read_project_file(BOUNDARIES)
        self.assertIn("exact close range does not retreat", source)
        self.assertIn("threat exactly at configured threshold retreats", source)
        self.assertIn("immediately inside strict close range retreats", source)

    def test_e80_gap_adjacent_edges_and_cue_seed_index_evidence_are_covered(self):
        source = read_project_file(BOUNDARIES)
        for assertion in (
            "active gap closer stops at exact enter edge",
            "new gap closer starts immediately above exit edge",
            "at least one alternate seed changes the deterministic sample",
            "at least one alternate cue index changes the deterministic sample",
            "cue jitter remains inside authored safe interval",
            "zero jitter above safe range clamps exactly to maximum",
        ):
            with self.subTest(assertion=assertion):
                self.assertIn(assertion, source)


if __name__ == "__main__":
    unittest.main()
