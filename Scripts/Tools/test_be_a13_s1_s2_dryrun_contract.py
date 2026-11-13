#!/usr/bin/env python3
"""Offline contract test (BE-A13) verifying BE_X26_X30 S1/S2 90-120 cm transient dry-run receipt."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATUS_PATH = (
    ROOT
    / "Docs"
    / "BossCombatReview"
    / "Execution"
    / "Codex"
    / "BE_X26_X30_S1_S2_RANGE"
    / "Run_20261110_182845"
    / "status.txt"
)
DOC_PATH = ROOT / "Documentation" / "Boss" / "BE_A11_A15_S1_S2_DRYRUN_RECONCILE.md"


class BeA13S1S2DryrunContractTests(unittest.TestCase):
    def test_be_x26_x30_receipt_confirms_ranges_and_punish_margin(self) -> None:
        status = STATUS_PATH.read_text(encoding="utf-8")
        for line in (
            "APPROVED_BASELINE=True",
            "S1_RANGE=True",
            "S2_RANGE=True",
            "NO_SAVES=True",
            "PASSED=509",
            "NO_ASSETS=1",
        ):
            self.assertIn(line, status)
        doc = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("0.352996 s", doc)
        self.assertIn("37.022 cm", doc)


if __name__ == "__main__":
    unittest.main()
