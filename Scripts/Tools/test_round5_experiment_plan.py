import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import round4_benchmark_report as report


ROOT = Path(__file__).resolve().parents[2]


def receipt():
    rows = []
    for group, avg_fps in enumerate((60.0, 61.0, 59.0)):
        rows.append({"run_id": f"baseline_{group}", "kind": "baseline", "baseline_group": group,
                     "cvars": {}, "avg_fps": avg_fps, "p99_ms": 16.0, "gpu_avg_ms": 15.0,
                     "build_id": "BUILD-222", "build_sha256": "c" * 64, "build_configuration": "Development",
                     "engine_version": "UE5.5.4", "gpu": "NVIDIA RTX 3060", "gpu_driver": "610.88",
                     "session_type": "console", "resolution_x": 1920, "resolution_y": 1080,
                     "map": "/Game/OneBossFight/Levels/L_SevarogArena", "fight_mode": True, "route": "selected",
                     "summary_path": f"baseline_{group}/summary.json", "summary_sha256": "a" * 64})
        if group < 2:
            rows.append({"run_id": f"trial_{group}", "kind": "treatment", "baseline_group": group,
                         "cvars": {"r.test": 1}, "avg_fps": 62.0, "p99_ms": 15.5, "gpu_avg_ms": 14.5,
                         "build_id": "BUILD-222", "build_sha256": "c" * 64, "build_configuration": "Development",
                         "engine_version": "UE5.5.4", "gpu": "NVIDIA RTX 3060", "gpu_driver": "610.88",
                         "session_type": "console", "resolution_x": 1920, "resolution_y": 1080,
                         "map": "/Game/OneBossFight/Levels/L_SevarogArena", "fight_mode": True, "route": "selected",
                         "summary_path": f"trial_{group}/summary.json", "summary_sha256": "b" * 64})
    return {"schema": report.ROUND5_SCHEMA, "baseline_metric_tolerance_percent": 5, "runs": rows}


class Round5ExperimentPlanTests(unittest.TestCase):
    def test_plan_has_twenty_rows_sixteen_single_variable_trials_and_repeats_baseline_every_four(self):
        plan = json.loads((ROOT / "Scripts/round5_experiments.json").read_text(encoding="utf-8"))
        rows = plan["experiments"]
        self.assertEqual(len(rows), 20)
        baselines = [row for row in rows if row["kind"] == "baseline"]
        treatments = [row for row in rows if row["kind"] == "treatment"]
        self.assertEqual(len(baselines), 4)
        self.assertEqual(len(treatments), 16)
        self.assertEqual([row["baseline_group"] for row in baselines], [0, 1, 2, 3])
        for start in (1, 6, 11, 16):
            self.assertEqual([row["kind"] for row in rows[start:start + 4]], ["treatment"] * 4)
        self.assertEqual([rows[index]["kind"] for index in (0, 5, 10, 15)], ["baseline"] * 4)
        self.assertTrue(all(row["cvar"].count("=") == 1 for row in treatments))

    def test_fire_radius_experiment_is_development_only_and_shipping_falls_back_to_authored_radius(self):
        h = (ROOT / "Source/OneBossFight/Arena/RPGPerfSwitches.h").read_text(encoding="utf-8")
        cpp = (ROOT / "Source/OneBossFight/Arena/RPGPerfSwitches.cpp").read_text(encoding="utf-8")
        source = (ROOT / "Source/OneBossFight/Arena/RPGFireSource.cpp").read_text(encoding="utf-8")
        self.assertIn("rpg.Perf.FireRadiusScale", h)
        self.assertIn("#if !UE_BUILD_SHIPPING", cpp)
        self.assertIn("float RPGPerf::FireRadiusScale() { return 1.f; }", cpp)
        self.assertIn("AttenuationRadius * RPGPerf::FireRadiusScale()", source)

    def test_round5_receipt_accepts_variable_number_of_rows(self):
        self.assertEqual(report.validate_experiment_receipt(receipt()), [])

    def test_repeated_baseline_drift_over_five_percent_quarantines_all_deltas(self):
        value = receipt()
        value["runs"][4]["gpu_avg_ms"] = 15.76
        result = report.analyze_experiments(value)
        self.assertTrue(result["valid"])
        self.assertFalse(result["stable"])
        self.assertTrue(any(row["metric"] == "gpu_avg_ms" and row["group"] == 2 for row in result["baseline_drift"]))
        self.assertTrue(all(row["avg_fps_delta_percent"] is None for row in result["comparisons"]))
        self.assertIn("comparisons usable: NO", report.render_experiment_report(value))

    def test_exactly_five_percent_baseline_delta_is_within_strict_threshold(self):
        value = receipt()
        value["runs"][2]["avg_fps"] = 63.0
        result = report.analyze_experiments(value)
        self.assertTrue(result["stable"])

    def test_treatment_with_multiple_cvars_is_rejected(self):
        value = receipt()
        value["runs"][1]["cvars"]["r.other"] = 0
        self.assertTrue(any("exactly one CVar" in issue for issue in report.validate_experiment_receipt(value)))

    def test_identity_mismatch_quarantines_treatment_deltas(self):
        value = receipt()
        value["runs"][1]["gpu"] = "NVIDIA RTX 2060 Super"
        result = report.analyze_experiments(value)
        self.assertTrue(result["valid"])
        self.assertFalse(result["comparable"])
        self.assertIn("gpu", result["identity_differences"])
        self.assertIsNone(result["comparisons"][0]["p99_ms_delta_percent"])


if __name__ == "__main__":
    unittest.main()
