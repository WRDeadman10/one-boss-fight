"""Offline evidence-map checks for graph, selector, and window audits."""
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_project_file(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8", errors="replace")


class QueueEGraphAuditFixtures(unittest.TestCase):
    def test_e86_malformed_unreachable_combo_node_is_still_validated(self):
        source = read_project_file("Source/OneBossFight/Tests/RPGBossComboTests.cpp")
        self.assertIn("invalid orphan MoveId is rejected despite being unreachable", source)
        self.assertIn("Combo.UnknownNode", source)

    def test_e87_well_formed_orphan_and_unreachable_cycle_contracts_are_separate(self):
        source = read_project_file("Source/OneBossFight/Tests/RPGBossComboTests.cpp")
        self.assertIn("an orphan node without a cycle stays valid", source)
        self.assertIn("cycle between two nodes the root cannot reach", source)
        self.assertIn("Combo.Cycle", source)

    def test_e88_combo_refusal_precedence_and_move_model_precedence_are_pinned(self):
        combo = read_project_file("Source/OneBossFight/Tests/RPGBossComboTests.cpp")
        model = read_project_file("Source/OneBossFight/Tests/RPGBossMoveModelTests.cpp")
        self.assertIn("invalid MaxDepth precedes unknown root when both are present", combo)
        self.assertIn("card failure has precedence over target failure", model)
        self.assertIn("vertical refusal precedes stale decision", model)

    def test_e89_underflowed_selector_score_remains_eligible_and_selectable(self):
        source = read_project_file("Source/OneBossFight/Tests/RPGBossMoveSelectorTests.cpp")
        self.assertIn("positive subnormal weight is accepted", source)
        self.assertIn("trace keeps subnormal-weight candidate eligible", source)
        self.assertIn("range factor underflows stored score to zero", source)
        self.assertIn("sole eligible zero-score candidate is selected", source)

    def test_e90_reset_replay_and_open_window_terminal_cleanup_are_covered(self):
        selector = read_project_file("Source/OneBossFight/Tests/RPGBossMoveSelectorTests.cpp")
        model = read_project_file("Source/OneBossFight/Tests/RPGBossMoveModelTests.cpp")
        self.assertIn("Resettable.Reset(); Resettable.Reset();", selector)
        self.assertIn("repeated reset restores fresh first tie choice", selector)
        for assertion in (
            "normal finish clears all open windows",
            "abort clears every open window",
            "generation reset leaves no open windows",
            "clock refusal clears every open window",
        ):
            with self.subTest(assertion=assertion):
                self.assertIn(assertion, model)


if __name__ == "__main__":
    unittest.main()
