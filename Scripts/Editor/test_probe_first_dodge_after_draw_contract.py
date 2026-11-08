"""Offline contracts for the first-dodge observation snapshot boundary."""
import ast
from pathlib import Path
import unittest

PROBE = Path(__file__).with_name("probe_first_dodge_after_draw.py")


class FirstDodgeObservationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = PROBE.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)
        cls.functions = {node.name: node for node in cls.tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}

    def test_snapshot_reads_reported_fields_without_input_or_dispatch_mutators(self):
        node = self.functions["first_dodge_snapshot"]
        calls = {item.func.id for item in ast.walk(node) if isinstance(item, ast.Call) and isinstance(item.func, ast.Name)}
        attributes = {item.func.attr for item in ast.walk(node) if isinstance(item, ast.Call) and isinstance(item.func, ast.Attribute)}
        forbidden = {
            "set_key_down", "add_movement_input", "consume_buffered_input", "try_activate_ability",
            "activate_ability", "dispatch_input", "set_input_action", "enter_combat", "end_play",
        }
        self.assertFalse((calls | attributes) & forbidden)
        self.assertTrue({"player_montage", "get_press_count", "get_backstep_count", "get_stage_name"} <= attributes)
        self.assertIn("buffered_input_tag", calls)

    def test_post_press_observation_label_does_not_reorder_input_edges(self):
        source = self.source
        press = source.index("key(pc, DODGE, True)")
        tick = source.index("yield 0.0", press)
        release = source.index("key(pc, DODGE, False)", tick)
        observed = source.index("first_dodge_snapshot(pawn, dodge, CASE, attempt)", release)
        self.assertLess(press, tick)
        self.assertLess(tick, release)
        self.assertLess(release, observed)
        self.assertIn("stage_label=post_press_observation", source)

    def test_snapshot_is_explicitly_limited_to_first_attempt_samples(self):
        source = self.source
        self.assertIn("if attempt == 1 and now >= next_sample_time:", source)
        self.assertIn('"first_standing_result" if CASE == "standing"', source)
        self.assertIn('"first_moving_result") if attempt == 1', source)
        self.assertIn('"repeat_dodge_result_%d" % attempt', source)

    def test_probe_is_not_mislabeled_as_read_only_or_root_cause_proof(self):
        self.assertIn("RPGInputTestUtils.set_key_down", self.source)
        self.assertIn("pawn.add_movement_input", self.source)
        self.assertIn("runtime_assignment=none", self.source)
        self.assertNotIn("root_cause_proven", self.source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
