#!/usr/bin/env python3
# Copyright One Boss Fight. All Rights Reserved.
"""
test_awr004_proposal.py

Automated verification suite for AWR004_TEST_PROPOSAL.md (v2.0):
1. Pure LF line endings, valid utf-8.
2. File exists and contains all required sections.
3. Quotes requirements.json behavior/verify and ledger notes for BOSS-AWR-004.
4. Contains verified runtime call chain with line citations.
5. Contains minimal design in FRPGBossMoveSelector with null safety and hand-computed values.
6. Contains recommendation to retain PARTIAL status.
7. All file:line citations exist on disk and are within file line bounds.
"""

import unittest
from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
DOC_PATH = REPO_ROOT / "Docs/BossCombatReview/Execution/Antigravity/Reviews/AWR004_TEST_PROPOSAL.md"

class TestAWR004Proposal(unittest.TestCase):

    def test_file_exists_and_pure_lf(self):
        self.assertTrue(DOC_PATH.exists(), f"Missing file: {DOC_PATH}")
        raw = DOC_PATH.read_bytes()
        self.assertNotIn(b"\r", raw, "AWR004_TEST_PROPOSAL.md contains CR! Must be pure LF.")

    def test_required_sections_present(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("## 1. Requirement & Ledger Context", text)
        self.assertIn("## 2. Call Chain Analysis: Can a Discrete-Attack Boss Show Hysteresis?", text)
        self.assertIn("## 3. Minimal Design (If Implemented in Selector)", text)
        self.assertIn("## 4. Engineering Recommendation: Retain PARTIAL", text)

    def test_quotes_requirements_and_ledger(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Tail swipes answer positions behind him", text)
        self.assertIn("Orbit across front/side/rear boundaries while an attack finishes", text)
        self.assertIn("TestMoveModelSelectsBestMatchingCandidate evaluates FrontConeDegrees", text)
        self.assertIn("MoveModel tests (model_tests:60) verify FrontConeDegrees evaluation", text)

    def test_call_chain_and_design_details(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("FRPGBossMoveSelector", text)
        self.assertIn("RPGBossMoveModel.cpp:82", text)
        self.assertIn("RPGBossMoveModel.cpp:128", text)
        self.assertIn("Hand-Computed Verification Values", text)
        self.assertIn("We recommend leaving `BOSS-AWR-004` as PARTIAL in the ledger.", text)

    def test_citations_exist_and_in_bounds(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        citation_pattern = re.compile(r"([A-Za-z0-9_\-\./]+(?:\.cpp|\.h|\.json|\.umap|\.log|\.md)):([0-9]+)(?:-([0-9]+))?")
        citations = citation_pattern.findall(text)
        self.assertGreaterEqual(len(citations), 5, f"Expected at least 5 verified citations, got {len(citations)}")

        for file_ref, start_line_str, end_line_str in citations:
            p = REPO_ROOT / file_ref
            self.assertTrue(p.exists(), f"Cited file does not exist on disk: {file_ref}")
            max_line = int(end_line_str) if end_line_str else int(start_line_str)
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                file_lines = f.readlines()
            self.assertLessEqual(
                max_line, len(file_lines),
                f"Line {max_line} out of range for {file_ref} (total lines: {len(file_lines)})"
            )

if __name__ == "__main__":
    unittest.main()
