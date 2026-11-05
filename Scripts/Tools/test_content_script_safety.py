"""
Offline unit test for content-script safety rules (V-A036).
Validates that editor content writing scripts implement refuse-if-exists,
pre-save assertions, and project namespace anchoring.
"""

import unittest
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SCRIPTS_TO_CHECK = [
    os.path.join(ROOT, "Scripts", "Editor", "create_tier1_art_assets.py"),
    os.path.join(ROOT, "Scripts", "author_parry_recoil_anim.py"),
]

class ContentScriptSafetyTests(unittest.TestCase):

    def test_scripts_exist(self):
        for script in SCRIPTS_TO_CHECK:
            self.assertTrue(os.path.exists(script), f"Expected script missing: {script}")

    def test_tier1_art_script_has_refuse_if_exists(self):
        path = os.path.join(ROOT, "Scripts", "Editor", "create_tier1_art_assets.py")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("does_asset_exist", content)
        self.assertIn("REFUSE", content)

    def test_tier1_art_script_has_assertions_before_save(self):
        path = os.path.join(ROOT, "Scripts", "Editor", "create_tier1_art_assets.py")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("assert", content)
        self.assertIn("save_loaded_asset", content)
        # Ensure assert appears before save
        first_assert = content.find("assert")
        first_save = content.find("save_loaded_asset")
        self.assertLess(first_assert, first_save)

    def test_tier1_art_script_anchored_in_project_namespace(self):
        path = os.path.join(ROOT, "Scripts", "Editor", "create_tier1_art_assets.py")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("/Game/OneBossFight/", content)

    def test_author_parry_recoil_script_has_dry_run_guard(self):
        path = os.path.join(ROOT, "Scripts", "author_parry_recoil_anim.py")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("dry_run", content)
        self.assertIn("Waiting for Owner approval", content)

if __name__ == "__main__":
    unittest.main()
