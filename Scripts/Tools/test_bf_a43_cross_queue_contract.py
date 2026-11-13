#!/usr/bin/env python3
"""Offline cross-queue contract test (BF-A43) verifying Queue BC..BG files, closeouts, and safety rules."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BOSS_DOCS = ROOT / "Documentation" / "Boss"


class BfA43CrossQueueContractTests(unittest.TestCase):
    def test_all_ag_queues_and_closeouts_exist_with_no_commit_policy(self) -> None:
        required_docs = (
            "QUEUE_BC_AG.md",
            "QUEUE_BC_AG_CLOSEOUT.md",
            "QUEUE_BD_AG.md",
            "QUEUE_BD_AG_CLOSEOUT.md",
            "QUEUE_BE_AG.md",
            "QUEUE_BE_AG_CLOSEOUT.md",
            "QUEUE_BF_AG.md",
            "QUEUE_BF_AG_CLOSEOUT.md",
            "QUEUE_BG_AG.md",
        )
        for name in required_docs:
            path = BOSS_DOCS / name
            self.assertTrue(path.is_file(), f"Missing queue doc: {path}")
        for qname in ("QUEUE_BD_AG.md", "QUEUE_BE_AG.md", "QUEUE_BF_AG.md", "QUEUE_BG_AG.md"):
            text = (BOSS_DOCS / qname).read_text(encoding="utf-8")
            self.assertIn("0` remote push", text)
            self.assertIn("broken_links=0", text)


if __name__ == "__main__":
    unittest.main()
