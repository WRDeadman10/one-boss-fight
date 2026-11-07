import sys
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import round6_benchmark_report as report
import round6_phase2_intake as phase2


def phase1_shape_fixture():
    rows = []
    for index in range(4):
        rows.append({"run_id": f"anchor{index}", "kind": "baseline", "mode": "TSR",
                     "temporal_upscaler": "TSR", "effective_primary_screen_percentage": 72.9,
                     "anti_aliasing_method": 4, "cvars": {"r.NGX.DLSS.Enable": 0},
                     "avg_fps": 26.0, "p99_ms": 45.0, "gpu_avg_ms": 36.0, "gpu_p99_ms": 44.0,
                     "predicted_gpu_saving_ms": 0})
    for mode, token, index in (("Quality", "MaxQuality", 0), ("Balanced", "Balanced", 1),
                               ("Performance", "MaxPerf", 2)):
        for trial in range(3):
            rows.append({"run_id": f"{mode}{trial}", "kind": "treatment", "mode": mode,
                         "temporal_upscaler": "DLSS", "effective_primary_screen_percentage": 66.7,
                         "anti_aliasing_method": 4, "cvars": {"r.NGX.DLSS.Enable": 1},
                         "avg_fps": 30.0 + index, "p99_ms": 40.0 - index,
                         "gpu_avg_ms": 32.0 - index, "gpu_p99_ms": 40.0 - index,
                         "predicted_gpu_saving_ms": None,
                         "prediction_note": "Fixture has no sourced prediction.",
                         "active_mode_log_line": f"Creating NGX DLSS Feature NGXPerfQuality={token}(1)"})
    return {"schema": report.SCHEMA, "phase": "phase1",
            "build_id": "OBF-DEVELOPMENT-20261106T071240Z-ed06b4d6", "runs": rows}


def phase2_fixture_from_phase1_shape():
    value = phase1_shape_fixture()
    value["phase"] = "phase2"
    value["selected_mode"] = "Performance"
    value["selected_primary_screen_percentage"] = 50
    value["runs"] = value["runs"][:4]
    for index in range(12):
        value["runs"].append({"run_id": f"phase2_{index}", "kind": "treatment", "mode": "best",
                              "temporal_upscaler": "DLSS", "effective_primary_screen_percentage": 50.0,
                              "anti_aliasing_method": 4, "cvars": {"r.NGX.DLSS.Enable": 1},
                              "avg_fps": 35.0, "p99_ms": 36.0, "gpu_avg_ms": 27.0, "gpu_p99_ms": 33.0,
                              "predicted_gpu_saving_ms": None,
                              "prediction_note": "Fixture has no sourced prediction.",
                              "active_mode_log_line": "Creating NGX DLSS Feature NGXPerfQuality=MaxPerf(0)"})
    return value


class Phase2IntakeTests(unittest.TestCase):
    def test_phase2_fixture_from_phase1_shape_passes(self):
        receipt = phase2_fixture_from_phase1_shape()
        self.assertEqual(phase2.validate_phase2(receipt), [])
        self.assertEqual(len(receipt["runs"]), 16)

    def test_phase1_receipt_is_not_accepted_as_phase2(self):
        self.assertTrue(any("phase must be phase2" in issue
                            for issue in phase2.validate_phase2(phase1_shape_fixture())))

    def test_wrong_mode_witness_in_each_treatment_is_rejected(self):
        receipt = phase2_fixture_from_phase1_shape()
        receipt["runs"][4]["active_mode_log_line"] = "Creating NGX DLSS Feature NGXPerfQuality=Balanced(1)"
        self.assertTrue(any("must witness Performance" in issue
                            for issue in phase2.validate_phase2(receipt)))

    def test_missing_build_id_is_rejected(self):
        receipt = phase2_fixture_from_phase1_shape()
        del receipt["build_id"]
        self.assertTrue(any("build_id must match" in issue
                            for issue in phase2.validate_phase2(receipt)))

    def test_shipping_or_malformed_build_id_is_rejected(self):
        for build_id in ("OBF-SHIPPING-20261106T071240Z-ac05f0da", "OBF-DEVELOPMENT-old",
                         "OBF-DEVELOPMENT-20261107T071240Z-ed06b4d6"):
            with self.subTest(build_id=build_id):
                receipt = phase2_fixture_from_phase1_shape()
                receipt["build_id"] = build_id
                self.assertTrue(any("build_id must match" in issue
                                    for issue in phase2.validate_phase2(receipt)))

    def test_wrong_owner_selected_mode_or_fraction_is_rejected(self):
        receipt = phase2_fixture_from_phase1_shape()
        receipt["selected_mode"] = "Quality"
        receipt["selected_primary_screen_percentage"] = 66.7
        issues = phase2.validate_phase2(receipt)
        self.assertTrue(any("selected_mode must match" in issue for issue in issues))
        self.assertTrue(any("selected_primary_screen_percentage must be 50" in issue for issue in issues))

    def test_missing_treatment_is_rejected_by_v1_contract(self):
        receipt = phase2_fixture_from_phase1_shape()
        receipt["runs"].pop()
        self.assertTrue(any("phase2 requires 16 rows" in issue
                            for issue in phase2.validate_phase2(receipt)))

    def test_cli_accepts_phase2_receipt_and_renders_owner_mode(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            receipt_path = Path(temp_dir) / "receipt.json"
            receipt_path.write_text(json.dumps(phase2_fixture_from_phase1_shape()), encoding="utf-8")
            result = subprocess.run([sys.executable, str(Path(phase2.__file__)), str(receipt_path)],
                                    capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("VALID Phase 2 receipt", result.stdout)
        self.assertIn("Performance base", result.stdout)


if __name__ == "__main__":
    unittest.main()
