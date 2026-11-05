"""Offline source/test map checks for selector, executor, and restart audits."""
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_project_file(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8", errors="replace")


class QueueESelectorAuditFixtures(unittest.TestCase):
    def test_e81_zero_weight_refusal_and_underflowed_eligible_score_are_distinct(self):
        selector_tests = read_project_file("Source/OneBossFight/Tests/RPGBossMoveSelectorTests.cpp")
        implementation = read_project_file("Source/OneBossFight/Player/RPGBossMoveSelector.cpp")
        self.assertIn("Cand(TEXT(\"A\"),50,150,0.f,0.f)", selector_tests)
        self.assertIn("FBossMoveSelectorSubnormalScore", selector_tests)
        self.assertIn("sole eligible zero-score candidate is selected", selector_tests)
        self.assertIn("T.Score>Out.Score", implementation)

    def test_e82_tie_contract_pins_input_order_and_seeded_repeatability(self):
        selector_tests = read_project_file("Source/OneBossFight/Tests/RPGBossMoveSelectorTests.cpp")
        implementation = read_project_file("Source/OneBossFight/Player/RPGBossMoveSelector.cpp")
        self.assertIn("tie goes to the lowest index", selector_tests)
        self.assertIn("same seed, same sequence", selector_tests)
        self.assertIn("Config.TieSeed+StartedCount", implementation)
        self.assertIn("T.Score>Out.Score", implementation)

    def test_e83_double_reset_replays_fresh_seeded_tie_choice(self):
        selector_tests = read_project_file("Source/OneBossFight/Tests/RPGBossMoveSelectorTests.cpp")
        self.assertIn("FBossMoveSelectorRepeatedResetTieReplay", selector_tests)
        self.assertIn("Resettable.Reset(); Resettable.Reset();", selector_tests)
        self.assertIn("repeated reset restores fresh first tie choice", selector_tests)

    def test_e84_open_window_counter_is_zero_after_terminal_model_paths(self):
        model_tests = read_project_file("Source/OneBossFight/Tests/RPGBossMoveModelTests.cpp")
        self.assertIn("normal finish clears all open windows", model_tests)
        self.assertIn("abort clears every open window", model_tests)
        self.assertIn("generation reset leaves no open windows", model_tests)
        self.assertIn("clock refusal clears every open window", model_tests)

    def test_e85_restart_matrix_allows_success_or_death_but_rejects_failure(self):
        header = read_project_file("Source/OneBossFight/Boss/RPGFrameworkBossCharacter.h")
        source = read_project_file("Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp")
        matrix = read_project_file("Documentation/Boss/ENCOUNTER_COMPLETION_RESTART_MATRIX_D110.md")
        self.assertIn("!bFailed&&(bDead||bSucceeded)&&NewGeneration>GenerationId", header)
        self.assertIn("bSucceeded=false; bDead=false", source)
        self.assertIn("if(bFailed)return;bFailed=true", source)
        self.assertIn("Restart is allowed for newer generation", matrix)
        self.assertIn("CanRestart` rejects failures", matrix)


if __name__ == "__main__":
    unittest.main()
