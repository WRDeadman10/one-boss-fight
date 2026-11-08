"""Offline contracts for aura capture's brightness-ready manifests."""
import unittest

from Scripts.Tools.aura_warmup_receipt import validate_warmup_receipt


def record(label, phase, brightness, game_time):
    return {"run": "runA", "route": "data", "frame": label, "phase": phase,
            "mean_gray": brightness, "game_time_s": game_time}


class AuraWarmupReceiptTests(unittest.TestCase):
    def test_approved_frame_requires_bright_same_run_warmup_within_bounds(self):
        rows = [record("warmup_discard_1", "warmup", 0.0, 10.0),
                record("warmup_discard_2", "warmup", 6.0, 10.1),
                record("approved", "approved", 7.0, 10.2)]
        result = validate_warmup_receipt(rows, "runA", "data")
        self.assertEqual(result[0]["warmup_frames"], 2)
        self.assertEqual(result[0]["ready_frame"], "warmup_discard_2")

    def test_all_black_too_many_stale_and_candidate_without_warmup_fail(self):
        black = [record("warmup_discard_1", "warmup", 0.0, 1.0),
                 record("approved", "approved", 6.0, 1.1)]
        with self.assertRaisesRegex(ValueError, "no bright warmup"):
            validate_warmup_receipt(black, "runA", "data")
        too_many = [record("warmup_discard_%d" % n, "warmup", 0.0, n / 15) for n in range(1, 22)]
        too_many += [record("warmup_discard_22", "warmup", 6.0, 22 / 15),
                     record("approved", "approved", 6.0, 23 / 15)]
        with self.assertRaisesRegex(ValueError, "20 frames"):
            validate_warmup_receipt(too_many, "runA", "data")
        with self.assertRaisesRegex(ValueError, "run/route mismatch"):
            validate_warmup_receipt([record("warmup_discard_1", "warmup", 6.0, 1.0),
                                     record("approved", "approved", 6.0, 1.1)], "other", "data")


if __name__ == "__main__":
    unittest.main(verbosity=2)
