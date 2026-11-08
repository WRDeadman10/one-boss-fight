import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import round6_benchmark_report as r6
from process_test_support import run_test_subprocess


def fixture():
    rows = []
    for i in range(4):
        rows.append({"run_id": f"tsr{i}", "kind": "baseline", "mode": "TSR", "temporal_upscaler": "TSR",
                     "effective_primary_screen_percentage": 100, "anti_aliasing_method": 4, "cvars": {},
                     "avg_fps": 30, "p99_ms": 40, "gpu_avg_ms": 38, "gpu_p99_ms": 39,
                     "predicted_gpu_saving_ms": 0})
        if i < 3:
            rows.append({"run_id": f"q{i}", "kind": "treatment", "mode": "Quality", "temporal_upscaler": "DLSS",
                         "effective_primary_screen_percentage": 66.7, "anti_aliasing_method": 4, "cvars": {"r.NGX.DLSS.Enable": 1},
                         "avg_fps": 40, "p99_ms": 30, "gpu_avg_ms": 28, "gpu_p99_ms": 29,
                         "predicted_gpu_saving_ms": 8, "active_mode_log_line": "LogDLSSNGXRHI: Creating NGX DLSS Feature NGXPerfQuality=MaxQuality(2)",
                         "image_quality_note": "Observed clear edges"})
    # fill other Phase 1 treatments while preserving planned row count
    for mode, token in (("Balanced", "Balanced"), ("Performance", "MaxPerf")):
        for i in range(3):
            rows.append({"run_id": f"{mode}{i}", "kind": "treatment", "mode": mode, "temporal_upscaler": "DLSS",
                         "effective_primary_screen_percentage": 58 if mode == "Balanced" else 50, "anti_aliasing_method": 4,
                         "cvars": {}, "avg_fps": 42, "p99_ms": 30, "gpu_avg_ms": 27, "gpu_p99_ms": 29,
                         "predicted_gpu_saving_ms": 10,
                         "active_mode_log_line": f"Creating NGX DLSS Feature NGXPerfQuality={token}(1)"})
    rows = rows[:13]
    # Ensure fixture has four anchors and exactly 3 trials for each mode.
    rows = [r for r in rows if r["kind"] == "baseline"] + [r for r in rows if r["kind"] == "treatment"]
    return {"schema": r6.SCHEMA, "phase": "phase1", "runs": rows}


class Round6ReportTests(unittest.TestCase):
    def test_valid_receipt_reports_delta_and_prediction_error(self):
        value = fixture()
        self.assertEqual(r6.validate(value), [])
        result = r6.summarize(value)
        quality = next(row for row in result["modes"] if row["mode"] == "Quality")
        self.assertEqual(quality["trials"], 3)
        self.assertAlmostEqual(quality["measured_gpu_saving_ms"], 10)
        self.assertAlmostEqual(quality["prediction_error_ms"], 2)
        self.assertIn("Active DLSS proof", r6.render(result))

    def test_treatment_without_active_upscaler_witness_is_rejected(self):
        value = fixture()
        value["runs"][4]["temporal_upscaler"] = "TSR"
        self.assertTrue(any("treatment temporal_upscaler must be DLSS" in e for e in r6.validate(value)))

    def test_unpredicted_phase1_savings_are_explicit_and_render_as_na(self):
        value = fixture()
        for row in value["runs"]:
            if row["kind"] == "treatment":
                row["predicted_gpu_saving_ms"] = None
                row["prediction_note"] = "No source-backed Phase 1 prediction; this run measures the savings."
        self.assertEqual(r6.validate(value), [])
        quality = next(x for x in r6.summarize(value)["modes"] if x["mode"] == "Quality")
        self.assertIsNone(quality["predicted_gpu_saving_ms"])
        self.assertIsNone(quality["prediction_error_ms"])
        self.assertIn("| n/a |", r6.render(r6.summarize(value)))
        value["runs"][4].pop("prediction_note")
        self.assertTrue(any("prediction_note is required" in e for e in r6.validate(value)))

    def test_round6_nested_logcmds_quoting_fix_is_present(self):
        root = Path(__file__).resolve().parents[2]
        runner = (root / "Scripts/RunPerfExperiments.ps1").read_text(encoding="utf-8")
        self.assertIn("$launchExtra -replace '\"', '\\\"'", runner)

    def test_treatment_missing_active_upscaler_field_is_rejected(self):
        value = fixture()
        del value["runs"][4]["temporal_upscaler"]
        self.assertTrue(any("treatment temporal_upscaler must be DLSS" in e for e in r6.validate(value)))

    def test_missing_creation_log_line_is_rejected(self):
        value = fixture()
        value["runs"][4]["active_mode_log_line"] = "DLSS supported"
        self.assertTrue(any("must prove active DLSS" in e for e in r6.validate(value)))

    def test_creation_log_line_accepts_engine_spacing(self):
        value = fixture()
        next(x for x in value["runs"] if x["run_id"] == "q0")["active_mode_log_line"] = "LogDLSSNGXRHI: Creating   NGX DLSS Feature NGXPerfQuality=MaxQuality(2)"
        self.assertEqual(r6.validate(value), [])

    def test_missing_mode_witness_is_rejected(self):
        value = fixture()
        del value["runs"][4]["active_mode_log_line"]
        self.assertTrue(any("must prove active DLSS" in e for e in r6.validate(value)))

    def test_incomplete_mode_trials_are_rejected(self):
        value = fixture()
        value["runs"] = [x for x in value["runs"] if x["run_id"] != "q2"]
        self.assertTrue(any("Quality requires exactly three treatments" in e for e in r6.validate(value)))

    def test_wrong_dlss_mode_creation_line_is_rejected(self):
        value = fixture()
        next(x for x in value["runs"] if x["run_id"] == "q0")["active_mode_log_line"] = "Creating NGX DLSS Feature NGXPerfQuality=Balanced(1)"
        self.assertTrue(any("does not witness Quality" in e for e in r6.validate(value)))

    def test_round6_script_has_fail_closed_preflight_and_no_invalid_cloud_scale(self):
        root = Path(__file__).resolve().parents[2]
        runner = (root / "Scripts/RunPerfExperiments.ps1").read_text(encoding="utf-8")
        plan = (root / "Scripts/round6_experiments.json").read_text(encoding="utf-8")
        self.assertIn("$s.temporal_upscaler -ne $expectedUpscaler", runner)
        self.assertIn("NGXPerfQuality", runner)
        self.assertIn("UNKNOWN variable", runner)
        plan_json = json.loads(plan)
        requested = {name for row in plan_json["treatments"] for name, _ in
                     __import__("re").findall(r"([A-Za-z][A-Za-z0-9_.]+)=([^;]+)", row.get("cvar", ""))}
        self.assertNotIn("r.VolumetricCloud.ViewRaySampleCountScale", requested)
        readme = (root / "Documentation/BENCHKIT_README.md").read_text(encoding="utf-8")
        for name in requested | {"r.NGX.DLSS.Enable", "r.ScreenPercentage"}:
            self.assertIn(name, readme, f"Round 6 prompt must explicitly preflight {name}")

    def test_phase_dry_runs_keep_planned_row_counts_and_require_measured_inputs(self):
        import subprocess
        root = Path(__file__).resolve().parents[2]
        script = root / "Scripts/RunPerfExperiments.ps1"
        phase1 = run_test_subprocess(self, ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script),
                                "-Round6", "-TsrAnchorScreenPercentage", "100", "-DryRun"],
                               timeout=30, cwd=root, capture_output=True, text=True, check=True)
        phase2 = run_test_subprocess(self, ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script),
                                 "-Round6Tuning", "-TsrAnchorScreenPercentage", "100", "-BestDlssMode", "Performance",
                                 "-BestDlssScreenPercentage", "50", "-Phase1Accepted", "-OwnerImageQualityAccepted", "-DryRun"],
                                timeout=30, cwd=root, capture_output=True, text=True, check=True)
        self.assertEqual(sum("R6M_" in line for line in phase1.stdout.splitlines()), 13)
        self.assertEqual(sum("R6T_" in line for line in phase2.stdout.splitlines()), 16)
        self.assertIn("no game will launch", phase1.stdout)
        self.assertIn("no game will launch", phase2.stdout)


if __name__ == "__main__":
    unittest.main()
