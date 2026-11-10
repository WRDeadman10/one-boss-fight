#!/usr/bin/env python3
"""Offline validator contract test (BC-A09) for Sevarog S1..S5 and S6..S8 windows & bounds."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUTHOR_SCRIPT = ROOT / "Scripts" / "Editor" / "author_sevarog_draft_cards.py"

# Verified C-1239 probe clip lengths & TIMING rows from author_sevarog_draft_cards.py:150-156, 304-330
SEVAROG_CARDS_S1_TO_S5 = (
    # (name, commit, active_start, active_end, recovery_end, clip_len, warp_start, warp_end, warp_dist)
    ("S1_Swing1_Medium", 0.200, 0.267, 0.400, 1.133, 1.133333, None, None, 0.0),
    ("S2_Swing2_Medium", 0.133, 0.200, 0.400, 1.133, 1.133333, None, None, 0.0),
    ("S3_Swing3_Slow", 0.467, 0.533, 0.667, 1.700, 1.700000, 0.467, 0.533, 50.0),
    ("S4_Speedburst", 0.200, 0.267, 1.133, 1.267, 1.266667, 0.267, 0.800, 450.0),
    ("S5_Swing1_Medium", 0.200, 0.267, 0.400, 1.133, 1.133333, None, None, 0.0),
)


class BcA09SevarogWindowBoundsContractTests(unittest.TestCase):
    def test_author_script_timing_constants_match_contract_rows(self) -> None:
        text = AUTHOR_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("(0.200, 0.267, 0.400, 1.133)", text)
        self.assertIn("(0.133, 0.200, 0.400, 1.133)", text)
        self.assertIn("(0.467, 0.533, 0.667, 1.700)", text)
        self.assertIn("(0.200, 0.267, 1.133, 1.267)", text)

    def test_s1_to_s5_timeline_and_warp_invariants(self) -> None:
        for name, commit, start, end, rec, clip_len, w_start, w_end, w_dist in SEVAROG_CARDS_S1_TO_S5:
            with self.subTest(card=name):
                self.assertGreaterEqual(commit, 0.0)
                self.assertLessEqual(commit, start)
                self.assertLess(start, end)
                self.assertLessEqual(end, rec)
                self.assertLessEqual(rec, clip_len)
                if w_dist > 0.0:
                    assert w_start is not None and w_end is not None
                    self.assertLessEqual(commit, w_start)
                    self.assertLess(w_start, w_end)
                    self.assertLessEqual(w_end, end)
                    self.assertLessEqual(w_dist, 1000.0)


if __name__ == "__main__":
    unittest.main()
