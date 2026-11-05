import json
import tempfile
import unittest
from pathlib import Path

import round4_benchmark_report as report


def receipt():
    runs = []
    for route, base in (("legacy", 70.0), ("selected", 65.0)):
        for index, rep in enumerate(("a", "b", "c")):
            runs.append({
                "route": route, "replicate": rep, "build_id": "BUILD-222",
                "build_sha256": "a" * 64, "build_configuration": "Development",
                "engine_version": "UE5.5.4", "gpu": "NVIDIA RTX 3060", "gpu_driver": "610.88",
                "session_type": "console", "resolution_x": 1920, "resolution_y": 1080,
                "map": "/Game/OneBossFight/Levels/L_SevarogArena", "fight_mode": True,
                "fight_started": True, "warmup_seconds": 5, "duration_seconds": 60,
                "avg_fps": base + index, "p99_ms": (15.0 if route == "legacy" else 15.2) + index * .1,
                "summary_path": f"{route}_{rep}_summary.json", "summary_sha256": "c" * 64,
                "frames_path": f"{route}_{rep}_frames.csv", "frames_sha256": "d" * 64,
            })
    return {"schema": report.SCHEMA, "owner": "owner", "capture_date": "2026-11-05",
            "gpu": "NVIDIA RTX 3060", "gpu_driver": "610.88", "session_type": "console",
            "gpu_utilization_before_pct": 4, "kit_version": "BUILD-222", "runs": runs}


class Round4BenchmarkTests(unittest.TestCase):
    def test_inventory_hashes_files_and_reports_missing_artifacts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run = root / "r4_legacy_a_20261105"
            run.mkdir()
            (run / "summary.json").write_text(json.dumps({"label": "r4_legacy_a"}), encoding="utf-8")
            result = report.inventory(root)
            self.assertEqual(result["expected_labels"], 8)
            self.assertEqual(result["files_hashed"], 1)
            self.assertTrue(any("missing frames.csv" in item for item in result["issues"]))
            self.assertEqual(len(result["missing_labels"]), 7)
            self.assertEqual(len(result["runs"][0]["files"][0]["sha256"]), 64)

    def test_inventory_detects_changed_files_against_prior_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run = root / "r4_legacy_a_20261105"
            run.mkdir()
            summary = run / "summary.json"
            summary.write_text(json.dumps({"label": "r4_legacy_a"}), encoding="utf-8")
            (run / "frames.csv").write_text("frame_ms\n10.0\n", encoding="utf-8")
            prior = report.inventory(root)
            (run / "frames.csv").write_text("frame_ms\n99.0\n", encoding="utf-8")
            current = report.inventory(root, prior)
            self.assertTrue(any("changed since expected inventory" in issue for issue in current["issues"]))

    def test_validation_requires_each_measured_route_replicate_once(self):
        value = receipt()
        self.assertEqual(report.validate_receipt(value), [])
        value["runs"].pop()
        self.assertTrue(any("exactly six" in issue for issue in report.validate_receipt(value)))

    def test_comparability_flags_identity_mismatch(self):
        value = receipt()
        value["runs"][0]["resolution_x"] = 1600
        result = report.compare_runs(value)
        self.assertFalse(result["comparable"])
        self.assertIn("resolution_x", result["identity_differences"])

    def test_report_aggregates_metrics_and_marks_missing_values_unknown(self):
        value = receipt()
        text = report.render_report(value)
        self.assertIn("71.00", text)
        self.assertIn("66.00", text)
        self.assertIn("15.30", text)
        value["runs"][0]["avg_fps"] = None
        text = report.render_report(value)
        self.assertIn("| legacy | UNKNOWN | 15.10 |", text)
        self.assertIn("Average >= 60 FPS: PASS", text)

    def test_incomparable_run_identity_makes_relative_p99_gate_unknown(self):
        value = receipt()
        value["runs"][0]["build_sha256"] = "b" * 64
        text = report.render_report(value)
        self.assertIn("Comparable setup: FAIL", text)
        self.assertIn("Selected p99 <= legacy p99 + 0.5 ms: UNKNOWN", text)


if __name__ == "__main__":
    unittest.main()
