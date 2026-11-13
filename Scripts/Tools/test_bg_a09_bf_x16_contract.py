#!/usr/bin/env python3
"""Offline contract test (BG-A09) verifying Codex BF_X16_X20 receipt & Evidence Index linkage."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATUS_PATH = (
    ROOT
    / "Docs"
    / "BossCombatReview"
    / "Execution"
    / "Codex"
    / "BF_X16_X20_MOVE_CARD_VALIDATION"
    / "Run_20261110_192136"
    / "status.txt"
)
INDEX_PATH = ROOT / "Documentation" / "Boss" / "BB_A26_A30_EVIDENCE_INDEX_C1227_ONWARD.md"


class BgA09BfX16ContractTests(unittest.TestCase):
    def test_bf_x16_x20_status_and_evidence_index_entry_match(self) -> None:
        status = STATUS_PATH.read_text(encoding="utf-8")
        for line in ("BUILD_EXIT=0", "SUITE_EXIT=0", "PASSED=509", "FAILED=0", "NO_ASSETS=1"):
            self.assertIn(line, status)
        index = INDEX_PATH.read_text(encoding="utf-8")
        self.assertIn("Codex/BF_X16_X20_MOVE_CARD_VALIDATION/Run_20261110_192136/", index)
        self.assertIn("`[X-1887]`", index)


if __name__ == "__main__":
    unittest.main()
