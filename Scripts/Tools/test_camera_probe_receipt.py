"""Offline fixtures for camera telemetry and time/frame association."""
import json
import unittest

from Scripts.Tools.camera_probe_receipt import parse_sample


def sample(**changes):
    row = {
        "run": "run-a", "route": "data", "sample_id": "run-a:sample-12",
        "frame_marker_id": "run-a:sample-12", "frame_time_s": 12.0,
        "game_time_s": 12.0, "player_boss_cm": 180.0,
        "camera_distance_cm": 310.0, "arm_target_cm": 370.0,
        "boss_relative_angle_deg": -42.5,
        "camera_inside_mesh_aabb": False, "hide_boss_inside": False,
    }
    row.update(changes)
    return json.dumps(row)


class CameraProbeReceiptTests(unittest.TestCase):
    def test_valid_sample_retains_geometry_and_frame_identity(self):
        row = parse_sample(sample(), expected_run="run-a")
        self.assertEqual(row["camera_distance_cm"], 310.0)
        self.assertEqual(row["boss_relative_angle_deg"], -42.5)
        self.assertFalse(row["camera_inside_mesh_aabb"])
        self.assertEqual(row["frame_marker_id"], row["sample_id"])

    def test_unknown_values_do_not_become_zero_intrusion(self):
        row = parse_sample(sample(camera_distance_cm="UNKNOWN",
                                  boss_relative_angle_deg="UNKNOWN",
                                  camera_inside_mesh_aabb="UNKNOWN",
                                  hide_boss_inside="UNKNOWN"))
        self.assertEqual(row["camera_inside_mesh_aabb"], "UNKNOWN")
        self.assertNotEqual(row["camera_inside_mesh_aabb"], False)

    def test_missing_malformed_and_nonfinite_samples_fail(self):
        with self.assertRaisesRegex(ValueError, "missing fields"):
            parse_sample(json.dumps({"run": "run-a"}))
        with self.assertRaises(json.JSONDecodeError):
            parse_sample("not json")
        with self.assertRaisesRegex(ValueError, "invalid numeric field"):
            parse_sample(sample(arm_target_cm=float("nan")))

    def test_stale_frame_and_run_fail(self):
        with self.assertRaisesRegex(ValueError, "stale frame marker"):
            parse_sample(sample(frame_marker_id="run-a:sample-11"))
        with self.assertRaisesRegex(ValueError, "stale run"):
            parse_sample(sample(run="old-run"), expected_run="run-a")
        with self.assertRaisesRegex(ValueError, "time mismatch"):
            parse_sample(sample(frame_time_s=11.0))


if __name__ == "__main__":
    unittest.main()
