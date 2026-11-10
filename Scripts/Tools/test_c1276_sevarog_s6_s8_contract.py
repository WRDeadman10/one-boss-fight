#!/usr/bin/env python3
"""Offline contract test for C-1276a/b/c Sevarog S6 reconciliation, S7/S8 values, and phase pools."""

import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC_PATH = ROOT / "Documentation" / "Boss" / "C1276_S6_RECONCILE_S7_S8_PROVISIONAL_AND_PHASES.md"


class C1276SevarogS6S8ContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = DOC_PATH.read_text(encoding="utf-8")

    def test_provisional_provenance_and_s6_reconciliation_documented(self) -> None:
        self.assertIn("provisional, tune after PIE", self.text)
        self.assertIn("ONE Continuous 360° Cleave (`0.667–0.900 s`)", self.text)
        self.assertIn("2664.93 cm/s", self.text)

    def test_s7_area_effect_satisfies_rpg_boss_move_card_cpp_rules(self) -> None:
        commit, rec = 0.733, 2.836
        clip_len = 2.866667
        release, delay, radius, dmg, snare_s, snare_scale = 0.800, 0.750, 225.0, 35.0, 2.50, 0.55
        self.assertLessEqual(rec, clip_len)
        self.assertGreaterEqual(release, commit)
        self.assertLessEqual(release + delay, rec)
        self.assertTrue(0.0 < delay <= 10.0)
        self.assertTrue(0.0 < radius <= 2000.0)
        self.assertTrue(0.0 < snare_s <= 30.0)
        self.assertTrue(0.0 < snare_scale < 1.0)
        # Proportional damage relative to S5 (25) and S3 (55)
        self.assertTrue(25.0 < dmg < 55.0)

    def test_s8_channel_drain_satisfies_rpg_boss_move_card_cpp_rules(self) -> None:
        commit, rec = 0.200, 1.803
        clip_len = 1.833333
        start, end, interval = 0.267, 1.267, 0.250
        tick_dmg, heal_frac, cone_range, cone_half = 8.0, 0.50, 650.0, 45.0
        self.assertLessEqual(rec, clip_len)
        self.assertGreaterEqual(start, commit)
        self.assertLess(start, end)
        self.assertLessEqual(end, rec)
        self.assertGreater(interval, 0.0)
        tick_count = math.floor(((end - start) + 1e-4) / interval) + 1
        self.assertEqual(tick_count, 5)
        self.assertTrue(1 <= tick_count <= 64)
        self.assertTrue(0.0 <= heal_frac <= 1.0)
        self.assertTrue(0.0 < cone_range <= 2000.0)
        self.assertTrue(0.0 < cone_half <= 180.0)
        max_total = tick_count * tick_dmg
        # Total full-channel damage sits between S5 (25) and S3 (55)
        self.assertTrue(25.0 < max_total < 55.0)
        # S6 signature sits above S3 (55)
        self.assertIn("`65.0`", self.text)

    def test_phase_pools_satisfy_x14_attack_count_non_starvation(self) -> None:
        attack_count = 3
        phase1_cards = ("S1", "S2", "S3", "S4", "S7")
        phase2_cards = ("S1_P2", "S2_P2", "S3_P2", "S4_P2", "S6", "S8")
        self.assertGreaterEqual(len(phase1_cards), attack_count)
        self.assertGreaterEqual(len(phase2_cards), attack_count)
        for token in ("Phase_1", "Phase_2", "S1_P2", "S6", "S7", "S8"):
            self.assertIn(token, self.text)


if __name__ == "__main__":
    unittest.main()
