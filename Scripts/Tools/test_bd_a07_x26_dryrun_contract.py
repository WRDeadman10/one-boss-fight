#!/usr/bin/env python3
"""Offline contract test (BD-A07) verifying Codex X26 dry-run receipt & author_sevarog_draft_cards specs."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUTHOR_PATH = ROOT / "Scripts" / "Editor" / "author_sevarog_draft_cards.py"
STATUS_PATH = (
    ROOT
    / "Docs"
    / "BossCombatReview"
    / "Execution"
    / "Codex"
    / "C1280_X26_PHASE_ELIGIBILITY"
    / "Run_20261110_165108"
    / "status.txt"
)
DOC_PATH = ROOT / "Documentation" / "Boss" / "BD_A07_X26_DRYRUN_RECONCILE.md"


class BdA07X26DryrunContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.author = AUTHOR_PATH.read_text(encoding="utf-8")
        self.status = STATUS_PATH.read_text(encoding="utf-8")
        self.doc = DOC_PATH.read_text(encoding="utf-8")

    def test_x26_receipt_metrics_all_green_zero_saves(self) -> None:
        for line in (
            "BUILD_EXIT=0",
            "EDITOR_EXIT=0",
            "DRYRUN_PASS=True",
            "NO_SAVES=True",
            "SUITE_EXIT=0",
            "PASSED=507",
            "FAILED=0",
            "MOVE_CARD_PHASE_TEST=True",
            "MOVE_MODEL_PHASE_TEST=True",
            "PROFILE_PHASE_POOL_TEST=True",
            "NO_ASSETS=1",
        ):
            self.assertIn(line, self.status)

    def test_author_script_matches_c1277_and_c1280_decisions(self) -> None:
        for token in (
            '"max_range_cm": 150.0, "front_cone_degrees": 360.0',
            '"hp_damage": 65.0',
            '"release_seconds": 0.800, "delay_seconds": 0.750, "radius_cm": 225.0',
            '"damage": 35.0, "snare_seconds": 2.50, "snare_speed_scale": 0.55',
            '"tick_interval_seconds": 0.200, "tick_damage": 8.0',
            '"heal_fraction": 0.50, "cone_range_cm": 650.0',
            '"cone_half_angle_degrees": 45.0, "track_facing_each_tick": False',
        ):
            self.assertIn(token, self.author)
        self.assertIn("`PASSED=507`", self.doc)


if __name__ == "__main__":
    unittest.main()
