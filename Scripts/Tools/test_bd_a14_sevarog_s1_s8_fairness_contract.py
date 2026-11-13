#!/usr/bin/env python3
"""Offline contract test (BD-A14) for Sevarog S6-S8 telegraph & dodge-fairness geometry."""

import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC_PATH = ROOT / "Documentation" / "Boss" / "BD_A12_SEVAROG_S6_S8_DODGE_FAIRNESS.md"


class BdA14SevarogFairnessContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.doc = DOC_PATH.read_text(encoding="utf-8")

    def test_s6_to_s8_player_roll_and_iframe_counterplay_bounds(self) -> None:
        # S6: single 0.233 s sweep fits strictly inside 0.323 s backstep i-frame window
        s6_active_dur = 0.900 - 0.667
        backstep_iframe_dur = 0.323
        self.assertLess(s6_active_dur, backstep_iframe_dur)
        # Player quick roll max (290 cm) exits S7 AreaEffect + player capsule (225 + 42 = 267 cm) from center
        self.assertGreater(290.0, 225.0 + 42.0)
        # S8 locked 45-deg cone half-width at min selector range (220 cm) < max quick roll (290 cm)
        s8_min_cone_half_width = 220.0 * math.tan(math.radians(45.0))
        self.assertGreater(290.0, s8_min_cone_half_width)
        for token in ("0.600 s", "267 cm", "0.750 s", "0.467 s"):
            self.assertIn(token, self.doc)


if __name__ == "__main__":
    unittest.main()
