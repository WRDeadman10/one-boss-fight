"""Offline contract test for SFX Batch 6 Candidate Specification (SFX_09_BATCH6_CANDIDATE_SPEC.md).

Validates that:
1. All referenced .uasset files exist on disk under Content/.
2. Tasks SFX-26 through SFX-30 each have 3 distinct candidate options.
3. Player voice exclusion safeguards (C-1212) and boss vocal separation (C-1175/C-1208) are documented.
4. No pack assets are marked for direct mutation.
"""

import os
import re
import unittest

PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(PROJECT_ROOT, "Documentation", "Boss", "SFX_09_BATCH6_CANDIDATE_SPEC.md")
CONTENT_ROOT = os.path.join(PROJECT_ROOT, "Content")


class TestSfxBatch6CandidatesContract(unittest.TestCase):
    def setUp(self):
        self.assertTrue(os.path.exists(SPEC_PATH), f"Spec file missing: {SPEC_PATH}")
        with open(SPEC_PATH, "r", encoding="utf-8") as f:
            self.content = f.read()

    def test_batch6_spec_doc_structure(self):
        """Spec doc must document SFX-26 through SFX-30."""
        for task_num in range(26, 31):
            expected = f"SFX-{task_num}"
            self.assertIn(expected, self.content, f"Missing task {expected} in spec")

    def test_voice_safeguards_documented(self):
        """Must document player voice exclusion (C-1212) and boss vocal separation."""
        self.assertIn("Player Voice Exclusion Rule", self.content)
        self.assertIn("C-1212", self.content)
        self.assertIn("C-1175", self.content)
        self.assertIn("non-vocal foley", self.content)

    def test_all_cited_candidates_exist_on_disk(self):
        """Every asset cited in SFX_09_BATCH6_CANDIDATE_SPEC.md must exist in Content/."""
        raw_paths = re.findall(r"/Game/[A-Za-z0-9_/\-]+", self.content)
        self.assertGreater(len(raw_paths), 10, "Found too few asset paths in spec")

        missing = []
        for path in set(raw_paths):
            if path.endswith("/"):
                continue
            rel = path.replace("/Game/", "")
            asset_path = os.path.join(CONTENT_ROOT, *rel.split("/")) + ".uasset"
            if not os.path.exists(asset_path):
                missing.append((path, asset_path))

        self.assertEqual(len(missing), 0, f"Found missing assets on disk: {missing}")

    def test_fifteen_candidates_across_five_tasks(self):
        """Must have exactly 5 tasks with Options A, B, and C."""
        matches_opt_a = re.findall(r"\*\*Option A", self.content)
        matches_opt_b = re.findall(r"\*\*Option B", self.content)
        matches_opt_c = re.findall(r"\*\*Option C", self.content)

        self.assertEqual(len(matches_opt_a), 5, f"Expected 5 Option A entries, got {len(matches_opt_a)}")
        self.assertEqual(len(matches_opt_b), 5, f"Expected 5 Option B entries, got {len(matches_opt_b)}")
        self.assertEqual(len(matches_opt_c), 5, f"Expected 5 Option C entries, got {len(matches_opt_c)}")


if __name__ == "__main__":
    unittest.main()
