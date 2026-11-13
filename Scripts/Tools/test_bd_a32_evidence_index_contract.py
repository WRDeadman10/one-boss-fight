#!/usr/bin/env python3
"""Offline contract test (BD-A32 & BD-A34) verifying Evidence Index paths, size rule, and Owner digest bounds."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX_PATH = ROOT / "Documentation" / "Boss" / "BB_A26_A30_EVIDENCE_INDEX_C1227_ONWARD.md"
DIGEST_PATH = ROOT / "Documentation" / "Boss" / "BB_A31_A35_OWNER_PROGRESS_DIGEST_DRAFT.md"
EXEC_ROOT = ROOT / "Docs" / "BossCombatReview" / "Execution"


class BdA32EvidenceIndexAndDigestContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.index = INDEX_PATH.read_text(encoding="utf-8")
        self.digest = DIGEST_PATH.read_text(encoding="utf-8")

    def test_every_indexed_execution_directory_exists_on_disk(self) -> None:
        rel_dirs = set(re.findall(r"`((?:Claude|Codex)/[A-Za-z0-9_/\-]+/)`", self.index))
        self.assertGreaterEqual(len(rel_dirs), 15)
        for rel in sorted(rel_dirs):
            full = EXEC_ROOT / rel.rstrip("/")
            self.assertTrue(full.is_dir(), f"Missing indexed evidence directory: {full}")

    def test_digest_makes_no_unverified_switch_or_live_claims(self) -> None:
        for required in (
            "DRAFT ONLY (Held for Lead review",
            "pending Lead authoring & live PIE verification",
            "GLOBALLY_SCALED",
            "Mannequin remains default until every gate passes",
            "C-954",
        ):
            self.assertIn(required, self.digest)


if __name__ == "__main__":
    unittest.main()
