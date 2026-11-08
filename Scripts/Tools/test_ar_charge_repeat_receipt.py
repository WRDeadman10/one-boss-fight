"""Offline contracts for explicit five-trial-per-route charge receipts."""
import json
from pathlib import Path
import tempfile
import unittest

from Scripts.Tools import ar_charge_receipt as base
from Scripts.Tools import ar_charge_repeat_receipt as repeat


def raw_log(route="legacy", context=True, drawn=True, finished=True, cases=None):
    rows = [f"LogPython: [ERControlLatency] route={route}",
            f"LogPython: [ERControlLatency] input_context_active={str(context)}"]
    if drawn:
        rows.append("LogPython: [ERControlLatency] draw_ready=True attempts=1")
    for case in base.EXPECTED_CASES if cases is None else cases:
        rows.append("LogPython: [ERControlLatency] sample case=%s montage=Ability_E_Anim_Montage position=0.029 observed_ms=393.00 tick_s=0.02780" % case)
    if finished:
        rows.append("LogPython: [ERControlLatency] SUMMARY finished: all control samples recorded")
    return "\n".join(rows) + "\n"


class ChargeRepeatReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def write_log(self, route, trial, **kwargs):
        path = self.root / f"{route}_R{trial:02d}.log"
        path.write_text(raw_log(route, **kwargs), encoding="utf-8")
        return path

    def test_stamp_preserves_game_tick_observations_and_adds_trial_identity(self):
        value = repeat.stamp(self.write_log("legacy", 2), build_id="BUILD-269", route="legacy", trial_index=2)
        self.assertEqual(value["trial_id"], "legacy-R02")
        self.assertEqual(value["planned_repetitions_per_route"], 5)
        self.assertTrue(value["observations_are_game_tick_bounded_not_device_latency"])
        self.assertEqual(value["samples"][2]["observed_game_tick_bounded_ms"], 393.0)

    def test_stamp_fails_on_wrong_route_or_missing_context_or_completion(self):
        with self.assertRaisesRegex(ValueError, "does not match"):
            repeat.stamp(self.write_log("data", 1), build_id="B", route="legacy", trial_index=1)
        with self.assertRaisesRegex(ValueError, "input_context_active"):
            repeat.stamp(self.write_log("legacy", 1, context=False), build_id="B", route="legacy", trial_index=1)
        with self.assertRaisesRegex(ValueError, "completion marker"):
            repeat.stamp(self.write_log("legacy", 1, finished=False), build_id="B", route="legacy", trial_index=1)

    def test_stamp_rejects_unconfirmed_or_failed_draw_warmup(self):
        with self.assertRaisesRegex(ValueError, "draw_ready=True"):
            repeat.stamp(self.write_log("legacy", 1, drawn=False), build_id="B", route="legacy", trial_index=1)
        path = self.write_log("legacy", 2)
        text = path.read_text(encoding="utf-8").replace("draw_ready=True", "draw_ready=False")
        path.write_text(text, encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "draw_ready=True"):
            repeat.stamp(path, build_id="B", route="legacy", trial_index=2)

    def test_stamp_requires_exact_five_run_index(self):
        path = self.write_log("legacy", 1)
        with self.assertRaisesRegex(ValueError, "trial index must be 1..5"):
            repeat.stamp(path, build_id="B", route="legacy", trial_index=6)

    def make_runs(self, *, build_id="BUILD-269"):
        paths = []
        for route in ("legacy", "data"):
            for trial in range(1, 6):
                log_path = self.write_log(route, trial)
                receipt = repeat.stamp(log_path, build_id=build_id, route=route, trial_index=trial)
                receipt_path = self.root / f"{route}_R{trial:02d}.json"
                receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
                paths.append(receipt_path)
        return paths

    def test_aggregate_requires_exact_routes_trials_and_summarizes_descriptively(self):
        result = repeat.aggregate(self.make_runs(), build_id="BUILD-269")
        self.assertEqual(result["run_count"], 10)
        self.assertEqual(result["planned_repetitions_per_route"], 5)
        row = result["summary"]["legacy"]["R2_hold_0.36s"]
        self.assertEqual(row["trial_ids"], ["legacy-R01", "legacy-R02", "legacy-R03", "legacy-R04", "legacy-R05"])
        self.assertEqual(row["median_observed_game_tick_bounded_ms"], 393.0)
        self.assertIn("no causality inferred", result["timing_scope"])

    def test_aggregate_rejects_duplicate_identity_and_missing_run(self):
        paths = self.make_runs()
        with self.assertRaisesRegex(ValueError, "duplicate route/trial"):
            repeat.aggregate(paths[:-1] + [paths[0]], build_id="BUILD-269")
        with self.assertRaisesRegex(ValueError, "exactly ten"):
            repeat.aggregate(paths[:-1], build_id="BUILD-269")

    def test_aggregate_rejects_mixed_build_and_incomplete_samples(self):
        paths = self.make_runs()
        with self.assertRaisesRegex(ValueError, "build ID does not match"):
            repeat.aggregate(paths, build_id="OTHER")
        value = json.loads(paths[0].read_text(encoding="utf-8"))
        value["samples"].pop()
        paths[0].write_text(json.dumps(value), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "sample cases are missing"):
            repeat.aggregate(paths, build_id="BUILD-269")


if __name__ == "__main__":
    unittest.main(verbosity=2)
