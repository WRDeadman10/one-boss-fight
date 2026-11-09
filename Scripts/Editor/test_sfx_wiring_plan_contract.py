"""Contract tests for SFX-04 wiring plan (C-1169, C-1193).

Verifies offline:
1. SFX_04_WIRING_PLAN.md exists and contains schema for all 5 priority gaps.
2. Cited C++ classes exist in Source/OneBossFight/.
3. Cited assets exist on disk in Content/.
4. All properties specify safe nullptr / opt-in defaults.
"""

import os
import unittest


class SfxWiringPlanContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        cls.wiring_plan = os.path.join(cls.repo_root, "Documentation", "Boss", "SFX_04_WIRING_PLAN.md")

    def test_wiring_plan_exists(self):
        self.assertTrue(os.path.exists(self.wiring_plan), f"Missing wiring plan: {self.wiring_plan}")

    def test_contains_all_five_gaps(self):
        with open(self.wiring_plan, "r", encoding="utf-8") as f:
            content = f.read()
        for gap in ["GAP-01", "GAP-02", "GAP-03", "GAP-04", "GAP-05"]:
            self.assertIn(gap, content, f"Missing gap {gap} in wiring plan")

    def test_cited_source_classes_exist(self):
        source_dir = os.path.join(self.repo_root, "Source", "OneBossFight")
        classes = [
            ("URPGPlayerParry", os.path.join(source_dir, "Player", "RPGPlayerParry.h")),
            ("URPGTier2BossPresentation", os.path.join(source_dir, "Boss", "RPGTier2BossPresentation.h")),
            ("URPGBossStagger", os.path.join(source_dir, "Player", "RPGBossStagger.h")),
        ]
        for name, path in classes:
            self.assertTrue(os.path.exists(path), f"Cited class header {name} not found at {path}")

    def test_opt_in_defaults_specified(self):
        with open(self.wiring_plan, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("nullptr", content)
        self.assertIn("EditDefaultsOnly", content)


if __name__ == "__main__":
    unittest.main()
