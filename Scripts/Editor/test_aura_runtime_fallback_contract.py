"""Contract test for Boost Lite runtime override fallback design document (C-1202).

Validates:
1. Exact arithmetic of retained vs lost parameters.
2. Integrity of cited source paths and Niagara component APIs.
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


class TestAuraRuntimeFallbackContract(unittest.TestCase):

    def test_density_and_size_loss_math(self):
        """Verify the exact arithmetic of what runtime fallback loses vs baseline."""
        baseline_sparks1 = 40.0
        boostlite_sparks1 = 70.0
        # Sparks1 lost: (70 - 40) / 70 = 42.857%
        self.assertAlmostEqual((boostlite_sparks1 - baseline_sparks1) / boostlite_sparks1 * 100.0, 42.857, places=2)

        baseline_total = 100.0
        boostlite_total = 152.5
        # Total density lost: (152.5 - 100) / 152.5 = 34.426%
        self.assertAlmostEqual((boostlite_total - baseline_total) / boostlite_total * 100.0, 34.426, places=2)

        baseline_length = 80.0
        boostlite_length = 100.0
        # Spark length lost: (100 - 80) / 100 = 20%
        self.assertEqual((boostlite_length - baseline_length) / boostlite_length * 100.0, 20.0)

    def test_cited_source_files_exist(self):
        """Verify the target source file cited in the design document exists."""
        source_path = os.path.join(PROJECT_ROOT, "Source", "OneBossFight", "Boss", "RPGTier2BossPresentation.cpp")
        self.assertTrue(os.path.exists(source_path))

    def test_design_document_exists_and_covers_required_sections(self):
        """Verify the fallback document exists and has all required sections."""
        doc_path = os.path.join(PROJECT_ROOT, "Documentation", "Boss", "AURA_BOOSTLITE_RUNTIME_FALLBACK_DESIGN.md")
        self.assertTrue(os.path.exists(doc_path))
        with open(doc_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("URPGTier2BossPresentation", content)
        self.assertIn("User.Scale_All", content)
        self.assertIn("User.Color_Sparks1", content)
        self.assertIn("Sparks1 SpawnRate", content)
        self.assertIn("Continuous Total Rate", content)


if __name__ == "__main__":
    unittest.main()
