#!/usr/bin/env python3
"""Offline contract test (BD-A28..A29) verifying S1-S8 Cues=[] default and aura/SFX precheck invariants."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUTHOR_PATH = ROOT / "Scripts" / "Editor" / "author_sevarog_draft_cards.py"
DOC_PATH = ROOT / "Documentation" / "Boss" / "BD_A28_A29_SFX_AURA_PREWIRING_CHECK.md"


class BdA28SfxAuraPrecheckContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.author = AUTHOR_PATH.read_text(encoding="utf-8")
        self.doc = DOC_PATH.read_text(encoding="utf-8")

    def test_s6_to_s8_keep_cues_empty_and_doc_records_bounds(self) -> None:
        self.assertGreaterEqual(self.author.count('"cues": []'), 3)
        for token in ("[-220.0, 220.0] cm", "<= 120", "16.67 ms", "User.Opacity"):
            self.assertIn(token, self.doc)


if __name__ == "__main__":
    unittest.main()
