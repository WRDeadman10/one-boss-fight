#!/usr/bin/env python3
"""Offline contract test (BD-A24) verifying Greystone switch readiness matrix stays fail-closed."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC_PATH = ROOT / "Documentation" / "Boss" / "BD_A24_GREYSTONE_READINESS_MATRIX.md"
CONFIG_INI = ROOT / "Config" / "DefaultGame.ini"


class BdA24GreystoneReadinessContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.doc = DOC_PATH.read_text(encoding="utf-8")

    def test_fail_closed_open_gates_explicitly_documented(self) -> None:
        for required in (
            "SAVED_COUNT=5",
            "15` unique materials",
            "28` resolved textures",
            "OPEN (Fail-Closed)",
            "Default remains Mannequin",
            "KI-052",
        ):
            self.assertIn(required, self.doc)

    def test_project_cook_root_present_without_forcing_greystone_default(self) -> None:
        ini = CONFIG_INI.read_text(encoding="utf-8")
        self.assertIn('/Game/OneBossFight/Player/Greystone', ini)
        self.assertNotIn("BP_GreystoneERPlayer", ini)


if __name__ == "__main__":
    unittest.main()
