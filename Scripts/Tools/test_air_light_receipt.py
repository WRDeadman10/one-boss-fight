"""Fixtures for Air Light action/frame context without inventing a distance gate."""
import json
import unittest

from Scripts.Tools.air_light_receipt import parse_context


def context(**changes):
    row = {
        "run": "fight-1", "action_id": "fight-1:air_light:3", "action": "air_light",
        "phase": "start", "game_time_s": 12.0, "player_boss_cm": 110.0,
        "player_position": [0.0, 0.0, 90.0], "boss_position": [110.0, 0.0, 150.0],
        "camera_position": [-250.0, 0.0, 140.0], "pivot_position": [0.0, 0.0, 130.0],
        "arm_target_cm": 370.0, "frame_index": 51,
        "frame_marker_id": "fight-1:frame:00051",
    }
    row.update(changes)
    return json.dumps(row)


class AirLightReceiptTests(unittest.TestCase):
    def test_valid_close_and_far_starts_preserve_frame_context(self):
        for distance in (80.0, 110.0, 500.0):
            row = parse_context(context(player_boss_cm=distance), expected_run="fight-1")
            self.assertEqual(row["player_boss_cm"], distance)
            self.assertEqual(row["frame_marker_id"], "fight-1:frame:00051")

    def test_missing_malformed_and_nonfinite_metadata_fail(self):
        with self.assertRaisesRegex(ValueError, "missing fields"):
            parse_context(json.dumps({"run": "fight-1"}))
        with self.assertRaises(json.JSONDecodeError):
            parse_context("bad json")
        with self.assertRaisesRegex(ValueError, "finite number"):
            parse_context(context(player_boss_cm=float("inf")))

    def test_frame_and_run_mismatch_fail(self):
        with self.assertRaisesRegex(ValueError, "frame identity"):
            parse_context(context(frame_marker_id="fight-1:frame:00050"))
        with self.assertRaisesRegex(ValueError, "stale run"):
            parse_context(context(run="old-run"), expected_run="fight-1")


if __name__ == "__main__":
    unittest.main()
