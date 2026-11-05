"""Offline checks that D94-D98 boundary findings retain focused evidence."""
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BOUNDARIES = "Source/OneBossFight/Tests/RPGBossQueueEBoundaryTests.cpp"


def read_project_file(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8", errors="replace")


class QueueERuleAuditFixtures(unittest.TestCase):
    def test_e71_poise_exact_ramp_endpoint_is_named_and_asserted(self):
        source = read_project_file(BOUNDARIES)
        self.assertIn("exact delay plus ramp reaches cap", source)
        self.assertIn("std::nextafter(End", source)
        self.assertIn("zero elapsed at zero delay returns base rate", source)

    def test_e72_unknown_stagger_phase_covers_integer_extremes(self):
        source = read_project_file(BOUNDARIES)
        self.assertIn("FBossStaggerResistUnknownExtremePhases", source)
        self.assertIn("negative unknown phase", source)
        self.assertIn("maximum integer unknown phase", source)
        self.assertIn("minimum integer unknown phase", source)

    def test_e73_aggro_exact_entry_and_exit_edges_are_pinned(self):
        source = read_project_file(BOUNDARIES)
        for assertion in (
            "exact close entry equality remains balanced",
            "exact close exit equality returns balanced",
            "exact far entry equality remains balanced",
            "exact far exit equality returns balanced",
        ):
            with self.subTest(assertion=assertion):
                self.assertIn(assertion, source)
        self.assertIn("std::nextafter(250.", source)

    def test_e74_difficulty_endpoint_and_equal_config_evidence_exists(self):
        boundaries = read_project_file(BOUNDARIES)
        equal = read_project_file("Source/OneBossFight/Tests/RPGBossDifficultyEqualEndpointsMutationTests.cpp")
        self.assertIn("difficulty above one returns neutral", boundaries)
        self.assertIn("negative difficulty returns neutral", boundaries)
        self.assertIn("equal speed endpoints remain constant", boundaries)
        self.assertIn("equal telegraph endpoints remain constant", boundaries)
        self.assertIn("EqualEndpoints", equal)

    def test_e75_enrage_endpoint_invalid_elapsed_and_stateless_repeat_are_distinct(self):
        source = read_project_file(BOUNDARIES)
        rules = read_project_file("Source/OneBossFight/Player/RPGBossEnrageRules.h")
        self.assertIn("exact ramp endpoint reaches configured damage cap", source)
        self.assertIn("NaN elapsed returns baseline", source)
        self.assertIn("repeated equal inputs are deterministic", source)
        self.assertIn("Unwired by design", rules)
        self.assertNotIn("Reset(", rules)


if __name__ == "__main__":
    unittest.main()
