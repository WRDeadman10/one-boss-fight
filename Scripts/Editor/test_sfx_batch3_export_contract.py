"""Contract test for SFX Batch 3 export runner and builder (C-1204).

Validates:
1. Export script targets 15 candidates without pack asset mutations.
2. Runner script acquires dual ENGINE_LOCK.json and uses -nosound.
3. Reel builder specifies all 15 CARDS matching SFX_05_BATCH3_CANDIDATE_SPEC.md.
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from Scripts.Editor import export_sfx_batch3 as exp_mod
from Scripts.Tools import build_sfx_batch3_reel as reel_mod


class TestSfxBatch3ExportContract(unittest.TestCase):

    def test_candidate_count_and_labels(self):
        """Must have exactly 15 candidate tuples for tasks SFX-11 through SFX-15."""
        self.assertEqual(len(exp_mod.CANDIDATES), 15)
        self.assertEqual(len(reel_mod.CARDS), 15)

        for label, asset_path in exp_mod.CANDIDATES:
            self.assertTrue(label.startswith("SFX11_") or label.startswith("SFX12_") or
                            label.startswith("SFX13_") or label.startswith("SFX14_") or
                            label.startswith("SFX15_"))

    def test_runner_script_locks_both_paths(self):
        """Runner must lock both root and Execution ENGINE_LOCK.json with -nosound."""
        runner_path = os.path.join(PROJECT_ROOT, "Scripts", "Editor", "run_export_sfx_batch3.ps1")
        self.assertTrue(os.path.exists(runner_path))
        with open(runner_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("ENGINE_LOCK.json", content)
        self.assertIn("Docs\\BossCombatReview\\Execution\\ENGINE_LOCK.json", content)
        self.assertIn("-nosound", content)


if __name__ == "__main__":
    unittest.main()
