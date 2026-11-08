"""Static contracts for the Lead-owned KI-192 repeat run handoff."""
from pathlib import Path
import ast
import unittest

from Scripts.Tools import ar_charge_receipt as receipt
from Scripts.Tools import ar_charge_repeat_receipt as repeat

ROOT = Path(__file__).resolve().parents[2]


class ChargeRerunContractTests(unittest.TestCase):
    def test_driver_retains_the_four_existing_game_tick_cases(self):
        source = (ROOT / "Scripts/Editor/pie_er_control_latency.py").read_text(encoding="utf-8")
        for duration in ("0.34", "0.35", "0.36", "0.70"):
            self.assertIn(f"({duration}, \"Gamepad_RightTrigger\", False)", source)
        self.assertIn("observations are game-tick bounded, not device-latency claims", source)
        self.assertIn("time.perf_counter()", source)
        self.assertEqual(len(receipt.EXPECTED_CASES), 4)

    def test_moving_case_uses_unreal_vector_length_not_size(self):
        path = ROOT / "Scripts/Editor/pie_er_control_latency.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)]
        vector_length = any(
            node.func.attr == "length" and isinstance(node.func.value, ast.Call)
            and isinstance(node.func.value.func, ast.Attribute)
            and node.func.value.func.attr == "get_velocity"
            for node in calls
        )
        vector_size = any(
            node.func.attr == "size" and isinstance(node.func.value, ast.Call)
            and isinstance(node.func.value.func, ast.Attribute)
            and node.func.value.func.attr == "get_velocity"
            for node in calls
        )
        self.assertTrue(vector_length)
        self.assertFalse(vector_size)

    def test_warmup_retries_draw_and_fails_before_samples_when_not_ready(self):
        source = (ROOT / "Scripts/Editor/pie_er_control_latency.py").read_text(encoding="utf-8")
        for required in (
            "attempts < 3", "loadout.is_combat_enabled()", "player_montage(pawn)[0] is None",
            'log("draw_ready=%s attempts=%d"', 'if not drawn:',
            "weapon not drawn after 3 warmup presses; samples would be invalid",
        ):
            self.assertIn(required, source)

    def test_canonical_summary_marker_is_used_by_shared_finish_and_receipt_gate(self):
        marker = "SUMMARY finished: all control samples recorded"
        shared = (ROOT / "Scripts/Editor/pie_lead_common.py").read_text(encoding="utf-8")
        receipt_tool = (ROOT / "Scripts/Tools/ar_charge_repeat_receipt.py").read_text(encoding="utf-8")
        driver = (ROOT / "Scripts/Editor/pie_er_control_latency.py").read_text(encoding="utf-8")
        handoff = (ROOT / "Documentation/Boss/AR_C31_C35_KI192_RERUN.md").read_text(encoding="utf-8")
        self.assertIn('log("SUMMARY finished: " + reason)', shared)
        self.assertIn('finish("all control samples recorded")', driver)
        self.assertIn(marker, receipt_tool)
        self.assertIn("[ERControlLatency] SUMMARY finished:", handoff)

    def test_wrapper_enforces_five_trials_per_route_and_canonical_case_order(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as temp:
            log = Path(temp) / "run.log"
            log.write_text("", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "trial index must be 1..5"):
                repeat.stamp(log, build_id="BUILD-269", route="legacy", trial_index=6)
        self.assertEqual(tuple(receipt.EXPECTED_CASES), (
            "R2_hold_0.34s", "R2_hold_0.35s_boundary",
            "R2_hold_0.36s", "R2_hold_0.70s",
        ))

    def test_handoff_has_exact_matrix_stop_rules_and_lead_return_artifacts(self):
        doc = (ROOT / "Documentation/Boss/AR_C31_C35_KI192_RERUN.md").read_text(encoding="utf-8")
        for required in (
            "40 samples", "five independent fresh-process observations", "BUILD-269",
            "input_context_active=True", "draw_ready=True", "SUMMARY finished:", "ten raw logs",
            "aggregate JSON", "physical controller latency", "No threshold adjustment",
        ):
            self.assertIn(required.lower(), doc.lower())
        self.assertNotIn("receipts/legacy_R01.json", doc)

    def test_queue_marks_all_five_rows_as_offline_prepared_with_lead_gate(self):
        queue = (ROOT / "Documentation/Boss/QUEUE_AR.md").read_text(encoding="utf-8")
        for task_id in ("AR-C31", "AR-C32", "AR-C33", "AR-C34", "AR-C35"):
            self.assertIn(f"| {task_id} |", queue)
        self.assertIn("no codex pie", queue.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
