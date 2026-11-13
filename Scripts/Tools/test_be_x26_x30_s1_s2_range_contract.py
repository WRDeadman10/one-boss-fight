#!/usr/bin/env python3
"""Offline bounds/source contract for C-1274-approved Sevarog S1/S2 ranges."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODULE_SPEC = spec_from_file_location("author_sevarog_draft_cards", ROOT / "Scripts/Editor/author_sevarog_draft_cards.py")
AUTHOR = module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(AUTHOR)


def analog(minimum=90.0, maximum=180.0):
    return {"DamageStatus": "design value, proposed", "CooldownStatus": "design value, proposed",
            "MinRangeCm": minimum, "MaxRangeCm": maximum, "TrackDegreesPerSecond": 120.0,
            "FrontConeDegrees": 120.0, "HPDamage": 25.0, "CooldownSeconds": 2.0, "BaseUtility": 1.0}


class ApprovedS1S2RangeContract(unittest.TestCase):
    def test_only_approved_s1_s2_rows_are_overridden_and_windows_are_preserved(self):
        cards = {move: analog() for move in AUTHOR.F5_ANALOG_IDS if move}
        rows = AUTHOR.build_candidate_specs(cards)
        by_id = {row["move_id"]: row for row in rows}
        for move in AUTHOR.APPROVED_S1_S2_RANGE_CM:
            row = by_id[move]
            self.assertEqual((row["min_range_cm"], row["max_range_cm"]), (90.0, 120.0))
            self.assertEqual(row["windows"][0]["start_seconds"], row["active_start_seconds"])
            self.assertEqual(row["windows"][0]["end_seconds"], row["active_end_seconds"])
        self.assertEqual((by_id["Move_Sevarog_Swing3_Slow"]["min_range_cm"],
                          by_id["Move_Sevarog_Swing3_Slow"]["max_range_cm"]), (90.0, 180.0))

    def test_range_validator_has_inclusive_bounds_and_exact_scope(self):
        valid = AUTHOR.is_within_approved_s1_s2_range
        move = "Move_Sevarog_Swing1_Medium"
        self.assertTrue(valid(move, 90.0, 120.0))
        self.assertTrue(valid(move, 120.0, 120.0))
        self.assertFalse(valid(move, 89.999, 120.0))
        self.assertFalse(valid(move, 90.0, 120.001))
        self.assertFalse(valid(move, 90.0, 89.0))
        self.assertTrue(valid("Move_Sevarog_Swing3_Slow", 1.0, 999.0))

    def test_c1269_baseline_recalculates_to_approved_plus_0353(self):
        margin = AUTHOR.approved_s1_s2_light_margin(120.0)
        self.assertAlmostEqual(margin, 0.352996, places=6)
        self.assertGreaterEqual(margin, 0.300000)


if __name__ == "__main__":
    unittest.main(verbosity=2)
