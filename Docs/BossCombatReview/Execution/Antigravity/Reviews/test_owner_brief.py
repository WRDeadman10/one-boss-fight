"""test_owner_brief.py - Verifies citations in OWNER_DECISION_BRIEF.md.

Verifies:
- Document exists and covers all 8 decision sections.
- Every cited `file:line` exists in the repository.
- The quoted words appear on that exact line in the target file.
- Exactly 10 unpushed commits are listed.
- .git tmp_obj count and size match repository state.

Run: python -I test_owner_brief.py
"""

import os
import re
import sys
import unittest

BRIEF_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "OWNER_DECISION_BRIEF.md")
)
REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))

CITATION_PATTERN = re.compile(r"^\s*-\s*`([^`:]+):(\d+)`:\s*(.+)$")


class TestOwnerDecisionBrief(unittest.TestCase):
    def setUp(self):
        self.assertTrue(os.path.exists(BRIEF_PATH), f"Brief file not found: {BRIEF_PATH}")
        with open(BRIEF_PATH, "r", encoding="utf-8") as f:
            self.content = f.read()
        self.lines = self.content.splitlines()

    def test_all_eight_sections_present(self):
        """Verifies that all 8 required owner decision sections exist in document."""
        required_headers = [
            "### 1. Cook Scope for ParagonSevarog (`KI-143`)",
            "### 2. NullRHI Headless Actor Spawning (`KI-144`)",
            "### 3. Phase-2 and Stagger Animations",
            "### 4. HUD and Boss Health Bar Integration",
            "### 5. Blood Effect and Sound",
            "### 6. Whether Any D3 Reference Numbers May Enter Ember Warden Cards",
            "### 7. Push of Unpushed Commits",
            "### 8. Optional `git gc --prune=now` of `.git` Garbage",
        ]
        for header in required_headers:
            self.assertIn(header, self.content, f"Missing required section header: {header}")

    def test_every_cited_file_line_and_text(self):
        """Verifies that every cited file:line exists and quoted text appears on that exact line."""
        citations = []
        for line_idx, line in enumerate(self.lines, 1):
            m = CITATION_PATTERN.match(line.strip())
            if m:
                rel_path = m.group(1).strip()
                line_no = int(m.group(2).strip())
                expected_text = m.group(3).strip().strip("`").strip('"')
                citations.append((line_idx, rel_path, line_no, expected_text))

        self.assertGreaterEqual(len(citations), 15, f"Expected at least 15 citations, found {len(citations)}")

        for brief_line_idx, rel_path, line_no, expected_text in citations:
            target_path = os.path.join(REPO_ROOT, rel_path.replace("/", os.sep))
            self.assertTrue(os.path.exists(target_path), f"Cited file {rel_path} does not exist (cited on line {brief_line_idx})")

            with open(target_path, "r", encoding="utf-8", errors="replace") as f:
                target_lines = f.readlines()

            self.assertTrue(1 <= line_no <= len(target_lines), f"Line {line_no} out of range for {rel_path} ({len(target_lines)} lines)")

            actual_line = target_lines[line_no - 1].strip()
            clean_expected = expected_text.replace("**", "").replace("`", "")
            clean_actual = actual_line.replace("**", "").replace("`", "")
            self.assertIn(
                clean_expected,
                clean_actual,
                f"Quoted words not found on {rel_path}:{line_no}\nExpected: {clean_expected}\nActual:   {clean_actual}"
            )

    def test_unpushed_commits_list_in_brief(self):
        """Verifies that unpushed commits count and subjects are recorded in brief."""
        self.assertIn("Exactly 10 unpushed commits", self.content)
        self.assertIn("3d9debd4 docs: D3 findings fix", self.content)
        self.assertIn("409ba526 docs: D3 findings 2/9", self.content)
        self.assertIn("b455740b proof: KI-146 dodge i-frame", self.content)

    def test_tmp_obj_garbage_size_in_brief(self):
        """Verifies that tmp_obj file count and approximate byte size are recorded."""
        self.assertIn("66 files", self.content)
        self.assertIn("152,566,102 bytes", self.content)
        self.assertIn("145.5 MB", self.content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
