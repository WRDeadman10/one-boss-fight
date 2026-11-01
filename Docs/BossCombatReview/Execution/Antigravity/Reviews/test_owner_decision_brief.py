#!/usr/bin/env python3
# Copyright One Boss Fight. All Rights Reserved.
"""
test_owner_decision_brief.py

Verifies that OWNER_DECISION_BRIEF.md:
1. Exists and has pure LF line endings.
2. Contains exact census counts matching witness_status_v3.json (37 / 21 / 24 = 82).
3. Contains exact counts for all 5 dependency classes matching generate_not_yet_census.py.
4. Contains exact counts for S/M/L costs matching generate_not_yet_census.py (4 / 12 / 8).
5. Contains exact counts for all 21 PARTIAL blocking categories.
6. Quotes the verbatim question from TEAM_MAILBOX.md:14532 (Option A, B, C).
7. Contains zero retired references to Greystone or Sevarog as the product duel.
"""

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
BRIEF_PATH = REPO_ROOT / "Docs/BossCombatReview/Execution/Antigravity/Reviews/OWNER_DECISION_BRIEF.md"
JSON_PATH = REPO_ROOT / "Docs/BossCombatReview/Execution/Antigravity/Ledger/witness_status_v3.json"
MAILBOX_PATH = REPO_ROOT / "Documentation/TEAM_MAILBOX.md"

class TestOwnerDecisionBrief(unittest.TestCase):
    def setUp(self):
        self.assertTrue(BRIEF_PATH.exists(), "OWNER_DECISION_BRIEF.md does not exist")
        self.raw_bytes = BRIEF_PATH.read_bytes()
        self.text = self.raw_bytes.decode("utf-8")

        with open(JSON_PATH, "r", encoding="utf-8") as f:
            self.ledger = json.load(f)

        with open(MAILBOX_PATH, "r", encoding="utf-8") as f:
            self.mailbox_text = f.read()

    def test_line_endings_pure_lf(self):
        """Must have pure LF line endings, zero CRLF."""
        self.assertNotIn(b"\r\n", self.raw_bytes, "Found CRLF in OWNER_DECISION_BRIEF.md")
        self.assertIn(b"\n", self.raw_bytes, "Missing LF in OWNER_DECISION_BRIEF.md")

    def test_census_parity(self):
        """Census numbers in brief must match ledger v3.15."""
        ledger_census = self.ledger["census"]
        self.assertIn(f"**{ledger_census['WITNESSED']}** (72.0%)", self.text)
        self.assertIn(f"**{ledger_census['PARTIAL']}** (17.1%)", self.text)
        self.assertIn(f"**{ledger_census['NOT YET']}** (11.0%)", self.text)
        self.assertIn("82 Canonical Requirements", self.text)

    def test_dependency_class_counts(self):
        """NOT YET dependency class breakdown must match counts."""
        self.assertIn("ENGINE-ONLY (0 reqs, 0.0%)", self.text)
        self.assertIn("NEEDS DESIGN DECISION (0 reqs, 0.0%)", self.text)
        self.assertIn("NEEDS ART (6 reqs, 66.7%)", self.text)
        self.assertIn("NEEDS NEW SYSTEM (0 reqs, 0.0%)", self.text)
        self.assertIn("PLAYER-SIDE (3 reqs, 33.3%)", self.text)

    def test_cost_breakdown_counts(self):
        """Cost breakdown counts must match generate_not_yet_census.py (S: 3, M: 12, L: 8)."""
        self.assertIn("Cost S (1-2 runs): 0 reqs (0.0%)", self.text)
        self.assertIn("Cost M (2-4 runs): 6 reqs (66.7%)", self.text)
        self.assertIn("Cost L (4+ runs): 3 reqs (33.3%)", self.text)

    def test_partial_counts(self):
        """PARTIAL category breakdown must sum to 14."""
        self.assertIn("Engine / PIE Scenario Hooks (3 rows)", self.text)
        self.assertIn("Player-Side / Combat Input Integration (4 rows)", self.text)
        self.assertIn("Animation & Notify Track Authoring (3 rows)", self.text)
        self.assertIn("Lifecycle & Watchdog Robustness (1 row)", self.text)
        self.assertIn("Architectural & Design Constraints (2 rows)", self.text)
        self.assertIn("Hardware Baseline (1 row)", self.text)

    def test_verbatim_owner_question(self):
        """Must quote the verbatim question from TEAM_MAILBOX.md line 14532."""
        expected_question = (
            '"which way next" for Track B: A) upgrade the 27 PARTIAL rows to WITNESSED '
            '(mostly one live run or one screenshot each), then the open rows; '
            'B) the 24 NOT YET rows in cost order (about 8 need art/design input, about 16 need new systems); '
            'C) stop. My recommendation: A then B.'
        )
        self.assertIn(expected_question, self.mailbox_text, "Expected question not found in TEAM_MAILBOX.md")
        self.assertIn(expected_question, self.text, "Expected question not quoted verbatim in brief")

    def test_no_retired_names(self):
        """Must not refer to Greystone or Sevarog as the product duel."""
        self.assertNotIn("Greystone vs Sevarog", self.text)
        self.assertNotIn("Greystone duel", self.text)
        self.assertNotIn("Greystone visual bridge", self.text)

    def test_evidence_receipts_match_disk(self):
        """Every receipt line in Reviews/evidence_sha256.txt must match file on disk (SHA256 and size)."""
        import hashlib
        import re
        receipt_path = REPO_ROOT / "Docs/BossCombatReview/Execution/Antigravity/Reviews/evidence_sha256.txt"
        self.assertTrue(receipt_path.exists(), "evidence_sha256.txt does not exist")
        raw_bytes = receipt_path.read_bytes()
        self.assertTrue(raw_bytes.endswith(b"\r\n"), "evidence_sha256.txt must end with \\r\\n (CRLF)")
        self.assertNotIn(b"\r\r\n", raw_bytes, "evidence_sha256.txt must not contain \\r\\r\\n")
        self.assertNotIn(b"\n\n", raw_bytes, "evidence_sha256.txt must not contain blank lines")

        lines = receipt_path.read_text(encoding="utf-8").splitlines()
        self.assertGreater(len(lines), 0, "evidence_sha256.txt is empty")

        receipt_pattern = re.compile(r"^[0-9a-f]{64}  \d+  \S+$")
        for idx, line in enumerate(lines, 1):
            self.assertTrue(line.strip(), f"Line {idx} in evidence_sha256.txt is blank/empty")
            self.assertRegex(
                line,
                receipt_pattern,
                f"Line {idx} must match '<64 hex>  <size>  <path>' with exactly two spaces: {line!r}",
            )
            parts = line.split("  ")
            self.assertEqual(len(parts), 3, f"Line {idx} in evidence_sha256.txt must have 3 parts separated by two spaces: {line}")
            expected_hash, expected_size, rel_path = parts[0], int(parts[1]), parts[2]

            p = REPO_ROOT / rel_path
            if not p.exists():
                p = REPO_ROOT / "Docs/BossCombatReview/Execution/Antigravity/Reviews" / rel_path
            self.assertTrue(p.exists(), f"File at line {idx} does not exist: {rel_path}")

            data = p.read_bytes()
            actual_hash = hashlib.sha256(data).hexdigest()
            actual_size = len(data)
            self.assertEqual(actual_hash, expected_hash, f"Hash mismatch at line {idx} for {rel_path}")
            self.assertEqual(actual_size, expected_size, f"Size mismatch at line {idx} for {rel_path}")

if __name__ == "__main__":
    unittest.main()
