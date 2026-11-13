"""BQ-22 (Queue BQ batch 5; D4): in-process temp-fixture tests for validate_benchmark_run_receipt.

Synthetic data only: every hash, path and value below is made up inside a temporary directory. No engine, no tool CLI,
no real output path. Covers the BI X03 positive fixture and its negative list.
"""
from __future__ import annotations

import copy
import hashlib
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_benchmark_run_receipt as V  # noqa: E402

HASH = "a" * 64


def _receipt() -> dict:
    """The positive fixture: every required identity present, explicit not_validated verdict."""
    return {
        "schema": "onebossfight.benchmark-run-receipt/v1",
        "run_id": "run-0001",
        "started_at_utc": "2026-11-13T05:00:00Z",
        "completed_at_utc": "2026-11-13T05:02:00Z",
        "runner": {"name": "synthetic-runner", "version": "1", "sha256": HASH},
        "authorization": {"task_reference": "BQ-22", "approval_reference": "fixture"},
        "source": {"revision": "0123456789abcdef", "tree_sha256": HASH},
        "build": {"configuration": "Shipping", "build_id": "fixture-build", "binary_sha256": HASH, "package_manifest_sha256": HASH},
        "engine_version": "5.5.4",
        "scenario": {"map": "L_Fixture", "route": "data", "route_witness": "route=data", "fight_mode": True, "phase": "full",
                     "resolution_x": 1920, "resolution_y": 1080, "window_mode": "fullscreen", "vsync": False,
                     "dynamic_resolution": False, "cvars": {"r.Fixture": 1, "r.Name": "x", "r.Flag": True}},
        "device": {"gpu": "Fixture GPU", "gpu_device_id": "0x0000", "gpu_driver": "1.0", "cpu": "Fixture CPU", "ram_gb": 16,
                   "os": "Fixture OS", "session_type": "console", "target_class": "target"},
        "capture": {"warmup_seconds": 10, "measured_seconds": 60, "frame_count": 3600, "percentile_method": "nearest-rank"},
        "artifacts": {},
        "metrics": {"average_fps": 60.0, "average_frame_ms": 16.6, "p95_frame_ms": 16.0, "p99_frame_ms": 16.5, "max_frame_ms": 20.0,
                    "game_thread_p99_ms": 4.0, "render_thread_p99_ms": 4.0, "gpu_p99_ms": 15.0, "frames_over_16_67_ms": 3,
                    "fight_started": True, "terminal_outcome": "boss_dead"},
        "validity": {"verdict": "not_validated", "reasons": []},
    }


class ReceiptValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.receipt = _receipt()
        for name, rel in (("frames_csv", "frames.csv"), ("summary_json", "summary.json"), ("raw_log", "run.log")):
            data = f"synthetic {name}\n".encode()
            (self.root / rel).write_bytes(data)
            self.receipt["artifacts"][name] = {"path": rel, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def assertRefused(self, receipt: dict, fragment: str, root: Path | None = None) -> None:
        errors = V.validate(receipt, root=root if root is not None else self.root)
        self.assertTrue(any(fragment in e for e in errors), f"expected {fragment!r} in {errors}")

    def test_positive_fixture_passes(self) -> None:
        self.assertEqual(V.validate(self.receipt, root=self.root), [])

    def test_missing_binary_hash(self) -> None:
        del self.receipt["build"]["binary_sha256"]
        self.assertRefused(self.receipt, "build.binary_sha256: missing")

    def test_empty_build_id(self) -> None:
        self.receipt["build"]["build_id"] = ""
        self.assertRefused(self.receipt, "build.build_id: shorter than 1")

    def test_malformed_sha256(self) -> None:
        self.receipt["source"]["tree_sha256"] = "XYZ"
        self.assertRefused(self.receipt, "source.tree_sha256: does not match")

    def test_remote_session_for_target_claim(self) -> None:
        self.receipt["device"]["session_type"] = "remote"
        self.assertRefused(self.receipt, "target-class claim needs a console session")

    def test_unknown_session_for_target_claim(self) -> None:
        self.receipt["device"]["session_type"] = "unknown"
        self.assertRefused(self.receipt, "target-class claim needs a console session")

    def test_remote_session_proxy_is_allowed(self) -> None:
        self.receipt["device"].update(session_type="remote", target_class="proxy")
        self.assertEqual(V.validate(self.receipt, root=self.root), [])

    def test_absent_route_witness(self) -> None:
        del self.receipt["scenario"]["route_witness"]
        self.assertRefused(self.receipt, "scenario.route_witness: missing")

    def test_zero_frames(self) -> None:
        self.receipt["capture"]["frame_count"] = 0
        self.assertRefused(self.receipt, "capture.frame_count: below minimum")

    def test_non_utc_timestamp(self) -> None:
        self.receipt["started_at_utc"] = "2026-11-13T05:00:00+05:30"
        self.assertRefused(self.receipt, "started_at_utc")

    def test_time_runs_backwards(self) -> None:
        self.receipt["completed_at_utc"] = "2026-11-13T04:00:00Z"
        self.assertRefused(self.receipt, "earlier than started_at_utc")

    def test_path_traversal(self) -> None:
        self.receipt["artifacts"]["raw_log"]["path"] = "../outside.log"
        self.assertRefused(self.receipt, "without '..'")

    def test_absolute_windows_path(self) -> None:
        self.receipt["artifacts"]["raw_log"]["path"] = "C:/elsewhere/run.log"
        self.assertRefused(self.receipt, "without '..'")

    def test_symlink_escape(self) -> None:
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        target = Path(outside.name) / "x.log"
        target.write_bytes(b"x")
        link = self.root / "link.log"
        try:
            os.symlink(target, link)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks need extra privileges on this host")
        self.receipt["artifacts"]["raw_log"]["path"] = "link.log"
        self.assertRefused(self.receipt, "outside the receipt root")

    def test_hash_and_size_mismatch(self) -> None:
        (self.root / "frames.csv").write_bytes(b"tampered")
        errors = V.validate(self.receipt, root=self.root)
        self.assertIn("artifacts.frames_csv: sha256 mismatch", errors)
        self.assertIn("artifacts.frames_csv: byte count mismatch", errors)

    def test_missing_artifact_file(self) -> None:
        (self.root / "run.log").unlink()
        self.assertRefused(self.receipt, "artifacts.raw_log: file missing")

    def test_valid_verdict_with_reasons(self) -> None:
        self.receipt["validity"] = {"verdict": "valid", "reasons": ["something"]}
        self.assertRefused(self.receipt, "valid verdict cannot carry refusal reasons")

    def test_extra_field_refused(self) -> None:
        self.receipt["device"]["hostname"] = "fixture"
        self.assertRefused(self.receipt, "device.hostname: not allowed")

    def test_bool_is_not_a_number(self) -> None:
        self.receipt["metrics"]["average_fps"] = True
        self.assertRefused(self.receipt, "metrics.average_fps: expected number")

    def test_non_finite_metric(self) -> None:
        self.receipt["metrics"]["p99_frame_ms"] = float("nan")
        self.assertRefused(self.receipt, "metrics.p99_frame_ms: not finite")

    def test_cvar_value_type(self) -> None:
        self.receipt["scenario"]["cvars"]["r.Bad"] = [1]
        self.assertRefused(self.receipt, "scenario.cvars.r.Bad: expected one of")

    def test_unknown_schema_keyword_fails_closed(self) -> None:
        schema = copy.deepcopy(V.load_schema())
        schema["properties"]["run_id"]["maxLength"] = 3
        errors = V.validate(self.receipt, schema=schema, root=self.root)
        self.assertTrue(any("unsupported schema keyword" in e for e in errors), errors)

    def test_not_an_object(self) -> None:
        self.assertEqual(V.validate([1, 2]), ["receipt: expected a JSON object"])


if __name__ == "__main__":
    unittest.main()
