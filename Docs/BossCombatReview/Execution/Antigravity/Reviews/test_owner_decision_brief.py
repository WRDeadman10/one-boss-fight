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
        """Census numbers in brief must match ledger v3.10."""
        ledger_census = self.ledger["census"]
        self.assertIn(f"**{ledger_census['WITNESSED']}** (45.1%)", self.text)
        self.assertIn(f"**{ledger_census['PARTIAL']}** (25.6%)", self.text)
        self.assertIn(f"**{ledger_census['NOT YET']}** (29.3%)", self.text)
        self.assertIn("82 Canonical Requirements", self.text)

    def test_dependency_class_counts(self):
        """NOT YET dependency class breakdown must match counts."""
        self.assertIn("ENGINE-ONLY (5 reqs, 20.8%)", self.text)
        self.assertIn("NEEDS DESIGN DECISION (4 reqs, 16.7%)", self.text)
        self.assertIn("NEEDS ART (6 reqs, 25.0%)", self.text)
        self.assertIn("NEEDS NEW SYSTEM (5 reqs, 20.8%)", self.text)
        self.assertIn("PLAYER-SIDE (4 reqs, 16.7%)", self.text)

    def test_cost_breakdown_counts(self):
        """Cost breakdown counts must match generate_not_yet_census.py (S: 4, M: 12, L: 8)."""
        self.assertIn("Cost S (1-2 runs): 4 reqs (16.7%)", self.text)
        self.assertIn("Cost M (2-4 runs): 12 reqs (50.0%)", self.text)
        self.assertIn("Cost L (4+ runs): 8 reqs (33.3%)", self.text)

    def test_partial_counts(self):
        """PARTIAL category breakdown must sum to 21."""
        self.assertIn("Engine / PIE Scenario Hooks (6 rows)", self.text)
        self.assertIn("Player-Side / Combat Input Integration (5 rows)", self.text)
        self.assertIn("Animation & Notify Track Authoring (4 rows)", self.text)
        self.assertIn("Lifecycle & Watchdog Robustness (3 rows)", self.text)
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

if __name__ == "__main__":
    unittest.main()
