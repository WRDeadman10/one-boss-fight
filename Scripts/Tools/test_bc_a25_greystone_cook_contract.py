#!/usr/bin/env python3
"""Offline contract test (BC-A25) verifying Greystone ER wrapper paths and DefaultGame.ini cook roots."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GAME_INI = ROOT / "Config" / "DefaultGame.ini"
WRAPPER_CPP = ROOT / "Source" / "OneBossFightEditor" / "Private" / "RPGMontageWrapperLibrary.cpp"
SWITCH_PLAN = ROOT / "Documentation" / "Boss" / "SWITCH_PLAN.md"


class BcA25GreystoneCookContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ini = DEFAULT_GAME_INI.read_text(encoding="utf-8")
        self.wrapper_cpp = WRAPPER_CPP.read_text(encoding="utf-8")
        self.switch_plan = SWITCH_PLAN.read_text(encoding="utf-8")

    def test_greystone_project_cook_root_present_and_pack_root_excluded(self) -> None:
        self.assertIn(
            '+DirectoriesToAlwaysCook=(Path="/Game/OneBossFight/Player/Greystone")',
            self.ini,
        )
        # Keep raw third-party ParagonGreystone pack excluded from wholesale cook roots (C-1259 trimmed footprint)
        self.assertNotIn(
            '+DirectoriesToAlwaysCook=(Path="/Game/ParagonGreystone")',
            self.ini,
        )

    def test_wrapper_allowlist_matches_project_cook_root(self) -> None:
        self.assertIn('TEXT("/Game/OneBossFight/Player/Greystone/")', self.wrapper_cpp)
        self.assertIn("/Game/OneBossFight/Player/Greystone/", self.switch_plan)


if __name__ == "__main__":
    unittest.main()
