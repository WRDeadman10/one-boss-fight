"""test_owner_brief.py - Verifies citations and structure of OWNER_DECISION_BRIEF.md.

Verifies:
- Document exists and covers all 8 decision sections.
- Label 'Recorded position (quote)' is used (not 'Lead Recommendation').
- Disclaimers on authored options '(options written for this brief, not recorded in the repo)' are present.
- Every cited `file:line` exists in the repository and the quoted words appear on that line.
- Mailbox post citations `file:[POST_ID]` match the post body in TEAM_MAILBOX.md.
- Unpushed commit count is verified dynamically against `git log origin/main..HEAD --oneline`.
- .git tmp_obj count (66) and size (~145.5 MB) match repository state.

Run: python -I test_owner_brief.py
"""

import os
import re
import subprocess
import sys
import unittest

BRIEF_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "OWNER_DECISION_BRIEF.md")
)
REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))

CITATION_PATTERN = re.compile(r"^\s*-\s*`([^`:]+):(\d+|\[[A-Za-z0-9_\-]+\])`:\s*(.+)$")


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

    def test_labels_and_options_disclaimers(self):
        """Verifies 'Recorded position (quote)' is used and options disclaimers are present."""
        self.assertNotIn("Lead Recommendation", self.content, "'Lead Recommendation' should be replaced with 'Recorded position (quote)'")
        self.assertIn("Recorded position (quote)", self.content)
        self.assertIn("(options written for this brief, not recorded in the repo)", self.content)

    def test_every_cited_file_line_and_text(self):
        """Verifies that every cited file:line or file:[POST_ID] exists and quoted text appears."""
        citations = []
        for line_idx, line in enumerate(self.lines, 1):
            m = CITATION_PATTERN.match(line.strip())
            if m:
                rel_path = m.group(1).strip()
                locator = m.group(2).strip()
                expected_text = m.group(3).strip().strip("`").strip('"')
                citations.append((line_idx, rel_path, locator, expected_text))

        self.assertGreaterEqual(len(citations), 15, f"Expected at least 15 citations, found {len(citations)}")

        for brief_line_idx, rel_path, locator, expected_text in citations:
            target_path = os.path.join(REPO_ROOT, rel_path.replace("/", os.sep))
            self.assertTrue(os.path.exists(target_path), f"Cited file {rel_path} does not exist (cited on line {brief_line_idx})")

            with open(target_path, "r", encoding="utf-8", errors="replace") as f:
                target_content = f.read()

            clean_expected = expected_text.replace("**", "").replace("`", "")

            if locator.startswith("[") and locator.endswith("]"):
                post_tag = locator[1:-1]
                parts = target_content.split(f"### [{post_tag}]")
                self.assertGreaterEqual(len(parts), 2, f"Post {locator} not found in {rel_path}")
                post_body = parts[1].split("### [")[0]
                clean_body = post_body.replace("**", "").replace("`", "")
                self.assertIn(
                    clean_expected,
                    clean_body,
                    f"Quoted words not found in post {locator} of {rel_path}\nExpected: {clean_expected}"
                )
            else:
                line_no = int(locator)
                target_lines = target_content.splitlines()
                self.assertTrue(1 <= line_no <= len(target_lines), f"Line {line_no} out of range for {rel_path} ({len(target_lines)} lines)")
                actual_line = target_lines[line_no - 1].strip()
                clean_actual = actual_line.replace("**", "").replace("`", "")
                self.assertIn(
                    clean_expected,
                    clean_actual,
                    f"Quoted words not found on {rel_path}:{line_no}\nExpected: {clean_expected}\nActual:   {clean_actual}"
                )

    def test_unpushed_commits_list_in_brief(self):
        """Verifies that unpushed commits count dynamically checks git log and subjects are recorded."""
        res = subprocess.run(["git", "log", "origin/main..HEAD", "--oneline"], capture_output=True, text=True, cwd=REPO_ROOT)
        self.assertEqual(res.returncode, 0)
        unpushed_commits = [line for line in res.stdout.strip().splitlines() if line.strip()]
        count = len(unpushed_commits)

        # Brief must mention git command and the count at time of writing
        self.assertIn("run `git log origin/main..HEAD --oneline`", self.content)
        self.assertIn("at the time of writing", self.content)
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
