import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import round4_benchmark_report as report
from process_test_support import run_test_subprocess


ROOT = Path(__file__).resolve().parents[2]


def receipt():
    rows = []
    for group, avg_fps in enumerate((60.0, 61.0, 59.0)):
        rows.append({"run_id": f"baseline_{group}", "kind": "baseline", "baseline_group": group,
                     "mode": "TSR", "cvars": {}, "avg_fps": avg_fps, "p99_ms": 16.0, "gpu_avg_ms": 15.0, "gpu_p99_ms": 15.8,
                     "build_id": "BUILD-222", "build_sha256": "c" * 64, "build_configuration": "Development",
                     "engine_version": "UE5.5.4", "gpu": "NVIDIA RTX 3060", "gpu_driver": "610.88",
                     "session_type": "console", "resolution_x": 1920, "resolution_y": 1080,
                     "map": "/Game/OneBossFight/Levels/L_SevarogArena", "fight_mode": True, "route": "selected",
                     "summary_path": f"baseline_{group}/summary.json", "summary_sha256": "a" * 64,
                     "active_mode_log_token": "TSR", "active_mode_log_line": "", "image_quality_note": "Native TSR reference"})
        rows.append({"run_id": f"trial_{group}", "kind": "treatment", "baseline_group": group,
                         "mode": "Quality", "cvars": {"r.NGX.DLSS.Enable": 1, "r.ScreenPercentage": 66.7},
                         "avg_fps": 62.0, "p99_ms": 15.5, "gpu_avg_ms": 14.5, "gpu_p99_ms": 14.9,
                         "build_id": "BUILD-222", "build_sha256": "c" * 64, "build_configuration": "Development",
                         "engine_version": "UE5.5.4", "gpu": "NVIDIA RTX 3060", "gpu_driver": "610.88",
                         "session_type": "console", "resolution_x": 1920, "resolution_y": 1080,
                         "map": "/Game/OneBossFight/Levels/L_SevarogArena", "fight_mode": True, "route": "selected",
                         "summary_path": f"trial_{group}/summary.json", "summary_sha256": "b" * 64,
                         "active_mode_log_token": "MaxQuality",
                         "active_mode_log_line": "LogDLSSNGXRHI: Creating NGX DLSS Feature NGXPerfQuality=MaxQuality(3), DenoiseMode=Off",
                         "image_quality_note": "No visible ghosting in this synthetic fixture"})
    return {"schema": report.ROUND5_SCHEMA, "baseline_metric_tolerance_percent": 5, "runs": rows}


class Round5ExperimentPlanTests(unittest.TestCase):
    def test_round3_cloud_shadow_sample_cvar_matches_ue55_source_name(self):
        runner = (ROOT / "Scripts/RunPerfExperiments.ps1").read_text(encoding="utf-8")
        self.assertIn("r.VolumetricCloud.Shadow.ViewRaySampleMaxCount=64", runner)
        self.assertNotIn("r.VolumetricCloud.ShadowViewRaySampleMaxCount", runner)

    def test_plan_has_four_anchors_and_three_replicates_for_each_dlss_mode(self):
        plan = json.loads((ROOT / "Scripts/round5_experiments.json").read_text(encoding="utf-8"))
        rows = plan["experiments"]
        self.assertEqual(len(rows), 16)
        baselines = [row for row in rows if row["kind"] == "baseline"]
        treatments = [row for row in rows if row["kind"] == "treatment"]
        self.assertEqual(len(baselines), 4)
        self.assertEqual(len(treatments), 12)
        self.assertEqual([row["baseline_group"] for row in baselines], [0, 1, 2, 3])
        for start in (1, 6, 11):
            self.assertEqual([row["kind"] for row in rows[start:start + 4]], ["treatment"] * 4)
        self.assertEqual([rows[index]["kind"] for index in (0, 5, 10, 15)], ["baseline"] * 4)
        for mode in ("DLAA", "Quality", "Balanced", "Performance"):
            selected = [row for row in treatments if row["mode"] == mode]
            self.assertEqual(len(selected), 3)
            self.assertTrue(all(row["cvar"].startswith("r.NGX.DLSS.Enable=1;r.ScreenPercentage=")
                                for row in selected))
        phase2 = plan["conditional_block"]
        self.assertEqual(phase2["status"], "deferred_until_phase_1_receipt")
        self.assertIn("rpg.Perf.FireShadows=0", phase2["baseline_cvar"])
        self.assertIn("<selected mode percentage>", phase2["extra_args_template"])

    def test_dlss_dry_run_lists_planned_rows_without_launching(self):
        import subprocess
        result = run_test_subprocess(self,
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
             str(ROOT / "Scripts/RunPerfExperiments.ps1"), "-Round5", "-DryRun"],
            timeout=30, cwd=ROOT, capture_output=True, text=True, check=True,
        )
        self.assertIn("Stage: not used in dry-run; no game will launch.", result.stdout)
        self.assertEqual(sum("R5_" in line for line in result.stdout.splitlines()), 16)
        self.assertIn("R5_15_TSR_anchor_g3", result.stdout)

    def test_round5_runner_stops_after_unknown_console_variable(self):
        script = (ROOT / "Scripts/RunPerfExperiments.ps1").read_text(encoding="utf-8")
        self.assertIn("($Round5 -or $Round6 -or $Round6Tuning) -and $e.C -and $s.cvars -match", script)
        self.assertIn(r"\(UNKNOWN variable\)", script)
        self.assertIn("experiment series is stopped", script)

    def test_fire_radius_experiment_is_development_only_and_shipping_falls_back_to_authored_radius(self):
        h = (ROOT / "Source/OneBossFight/Arena/RPGPerfSwitches.h").read_text(encoding="utf-8")
        cpp = (ROOT / "Source/OneBossFight/Arena/RPGPerfSwitches.cpp").read_text(encoding="utf-8")
        source = (ROOT / "Source/OneBossFight/Arena/RPGFireSource.cpp").read_text(encoding="utf-8")
        self.assertIn("rpg.Perf.FireRadiusScale", h)
        self.assertIn("#if !UE_BUILD_SHIPPING", cpp)
        self.assertIn("FMath::Clamp(Value, 0.25f, 1.25f)", cpp)
        self.assertIn("float RPGPerf::FireRadiusScale() { return 1.f; }", cpp)
        self.assertIn("AttenuationRadius * RPGPerf::FireRadiusScale()", source)
        self.assertIn("TargetRadius = AttenuationRadius * RPGPerf::FireRadiusScale()", source)

    def test_round5_receipt_accepts_variable_number_of_rows(self):
        self.assertEqual(report.validate_experiment_receipt(receipt()), [])

    def test_round5_json_schema_declares_identity_and_variable_length_runs(self):
        schema = json.loads((ROOT / "Scripts/Tools/round5_benchmark.schema.json").read_text(encoding="utf-8"))
        run = schema["$defs"]["run"]
        self.assertEqual(schema["$id"], report.ROUND5_SCHEMA)
        self.assertEqual(schema["properties"]["runs"]["minItems"], 2)
        self.assertIn("gpu", run["required"])
        self.assertIn("gpu_p99_ms", run["required"])
        self.assertIn("active_mode_log_line", run["required"])
        self.assertIn("route", run["required"])
        self.assertEqual(run["properties"]["build_sha256"]["pattern"], "^[0-9a-f]{64}$")

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
        value["runs"][1]["cvars"].update({"rpg.Perf.FireShadows": 0, "r.other": 1})
        self.assertTrue(any("unsupported Round 5 CVar" in issue for issue in report.validate_experiment_receipt(value)))

    def test_three_run_mode_summary_has_means_deltas_and_image_quality_slot(self):
        value = receipt()
        result = report.analyze_experiments(value)
        self.assertTrue(result["valid"])
        self.assertEqual(len(result["mode_summaries"]), 1)
        mode = result["mode_summaries"][0]
        self.assertEqual(mode["mode"], "Quality")
        self.assertEqual(mode["run_count"], 3)
        self.assertEqual(mode["avg_fps_mean"], 62.0)
        self.assertAlmostEqual(mode["avg_fps_delta_vs_tsr_percent"], (62.0 - 60.0) / 60.0 * 100)
        self.assertEqual(len(mode["image_quality_notes"]), 3)

    def test_round5_report_renders_per_mode_gpu_p99_and_run_cvars(self):
        rendered = report.render_experiment_report(receipt())
        self.assertIn("TSR reference mean", rendered)
        self.assertIn("Mean GPU p99 ms", rendered)
        self.assertIn("Δ GPU p99 vs TSR", rendered)
        self.assertIn("r.NGX.DLSS.Enable=1", rendered)
        self.assertIn("MaxQuality", rendered)
        self.assertIn("No visible ghosting", rendered)

    def test_active_mode_log_token_mismatch_invalidates_receipt(self):
        value = receipt()
        value["runs"][1]["active_mode_log_token"] = "Balanced"
        self.assertTrue(any("active mode token must be 'MaxQuality'" in issue
                            for issue in report.validate_experiment_receipt(value)))

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
