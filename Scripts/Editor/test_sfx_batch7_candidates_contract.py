"""Offline contract test for SFX Batch 7 & Ambience Candidate Specification (SFX_10_BATCH7_CANDIDATE_SPEC.md).

Validates that:
1. All referenced .uasset files exist on disk under Content/.
2. Tasks SFX-31..35 (Boss Movement) and SFX-41..45 (Arena Ambience) each have 3 distinct candidate options.
3. Acoustic boundaries, spatialization, and zero-pack rules are documented.
"""

import os
import re
import unittest

PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(PROJECT_ROOT, "Documentation", "Boss", "SFX_10_BATCH7_CANDIDATE_SPEC.md")
CONTENT_ROOT = os.path.join(PROJECT_ROOT, "Content")


class TestSfxBatch7CandidatesContract(unittest.TestCase):
    def setUp(self):
        self.assertTrue(os.path.exists(SPEC_PATH), f"Spec file missing: {SPEC_PATH}")
        with open(SPEC_PATH, "r", encoding="utf-8") as f:
            self.content = f.read()

    def test_batch7_and_batch9_tasks_covered(self):
        """Spec doc must document SFX-31..35 and SFX-41..45."""
        for task_num in list(range(31, 36)) + list(range(41, 46)):
            expected = f"SFX-{task_num}"
            self.assertIn(expected, self.content, f"Missing task {expected} in spec")

    def test_spatialization_and_pack_rules_documented(self):
        """Must document spatialization, attenuation, and zero-pack mutation rules."""
        self.assertIn("Acoustic Boundaries & Spatialization Guidelines", self.content)
        self.assertIn("Zero-Pack Mutation Guarantee", self.content)
        self.assertIn("C-1213", self.content)

    def test_all_cited_candidates_exist_on_disk(self):
        """Every asset cited in SFX_10_BATCH7_CANDIDATE_SPEC.md must exist in Content/."""
        raw_paths = re.findall(r"/Game/[A-Za-z0-9_/\-]+", self.content)
        self.assertGreater(len(raw_paths), 15, "Found too few asset paths in spec")

        missing = []
        for path in set(raw_paths):
            if path.endswith("/"):
                continue
            rel = path.replace("/Game/", "")
            asset_path = os.path.join(CONTENT_ROOT, *rel.split("/")) + ".uasset"
            if not os.path.exists(asset_path):
                missing.append((path, asset_path))

        self.assertEqual(len(missing), 0, f"Found missing assets on disk: {missing}")

    def test_thirty_candidates_across_ten_tasks(self):
        """Must have exactly 10 tasks with Options A, B, and C (30 total options)."""
        matches_opt_a = re.findall(r"\*\*Option A", self.content)
        matches_opt_b = re.findall(r"\*\*Option B", self.content)
        matches_opt_c = re.findall(r"\*\*Option C", self.content)

        self.assertEqual(len(matches_opt_a), 10, f"Expected 10 Option A entries, got {len(matches_opt_a)}")
        self.assertEqual(len(matches_opt_b), 10, f"Expected 10 Option B entries, got {len(matches_opt_b)}")
        self.assertEqual(len(matches_opt_c), 10, f"Expected 10 Option C entries, got {len(matches_opt_c)}")


if __name__ == "__main__":
    unittest.main()
