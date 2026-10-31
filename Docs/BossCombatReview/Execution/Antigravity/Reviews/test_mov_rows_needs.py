#!/usr/bin/env python3
# Copyright One Boss Fight. All Rights Reserved.
"""
test_mov_rows_needs.py

Verifies Docs/BossCombatReview/Execution/Antigravity/Reviews/MOV_ROWS_NEEDS.md:
1. Pure LF line endings, valid utf-8.
2. Covers exactly the 12 requested NOT YET rows from C-544:
   MOV-002, MOV-003, MOV-004, MOV-005, MOV-006,
   PAC-003, PAC-005, SEL-009, EXE-005,
   DEF-004, DEF-005, PHS-005.
3. Each row description is bounded to <= 5 content lines.
4. Every file:line citation in the document exists on disk and is within file line bounds.
"""

import unittest
from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
DOC_PATH = REPO_ROOT / "Docs/BossCombatReview/Execution/Antigravity/Reviews/MOV_ROWS_NEEDS.md"

EXPECTED_ROWS = [
    "BOSS-MOV-002", "BOSS-MOV-003", "BOSS-MOV-004", "BOSS-MOV-005", "BOSS-MOV-006",
    "BOSS-PAC-003", "BOSS-PAC-005", "BOSS-SEL-009", "BOSS-EXE-005",
    "BOSS-DEF-004", "BOSS-DEF-005", "BOSS-PHS-005"
]

class TestMovRowsNeeds(unittest.TestCase):

    def test_file_exists_and_line_endings(self):
        self.assertTrue(DOC_PATH.exists(), f"Missing file: {DOC_PATH}")
        with open(DOC_PATH, "rb") as f:
            raw = f.read()
        self.assertNotIn(b"\r", raw, "MOV_ROWS_NEEDS.md contains CR! Must be pure LF.")

    def test_expected_rows_and_line_limits(self):
        with open(DOC_PATH, "r", encoding="utf-8") as f:
            text = f.read()

        sections = re.split(r"### `(BOSS-[A-Za-z0-9\-]+)`", text)
        found_rows = sections[1::2]
        self.assertEqual(found_rows, EXPECTED_ROWS, f"Rows mismatch! Expected {EXPECTED_ROWS}, got {found_rows}")

        for i in range(1, len(sections), 2):
            row_id = sections[i]
            body = sections[i+1].strip()
            lines = [l for l in body.split("\n") if l.strip()]
            self.assertLessEqual(len(lines), 5, f"{row_id} has {len(lines)} content lines, expected <= 5!")

    def test_citations_exist_and_in_bounds(self):
        with open(DOC_PATH, "r", encoding="utf-8") as f:
            text = f.read()

        citation_pattern = re.compile(r"([A-Za-z0-9_\-\./]+(?:\.cpp|\.h|\.json|\.umap|\.log|\.md)):([0-9]+)")
        citations = citation_pattern.findall(text)
        self.assertGreaterEqual(len(citations), 20, "Expected at least 20 verified citations in review.")

        for file_ref, line_str in citations:
            p = REPO_ROOT / file_ref
            self.assertTrue(p.exists(), f"Cited file does not exist on disk: {file_ref}")
            line_no = int(line_str)
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                file_lines = f.readlines()
            self.assertLessEqual(
                line_no, len(file_lines),
                f"Line {line_no} out of range for {file_ref} (total lines: {len(file_lines)})"
            )

if __name__ == "__main__":
    unittest.main()
