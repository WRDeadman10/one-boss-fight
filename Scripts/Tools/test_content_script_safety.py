"""
Offline unit test for content-script safety rules (V-A036).
Validates that editor content writing scripts implement refuse-if-exists,
pre-save assertions, and project namespace anchoring.
"""

import unittest
import os
import re
import ast

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
        # Require an assertion between each save, rather than one unrelated
        # assertion somewhere earlier in the file.
        save_positions = [m.start() for m in re.finditer(r"save_loaded_asset\s*\(", content)]
        self.assertTrue(save_positions)
        prior_save = -1
        for save in save_positions:
            self.assertGreater(content.rfind("assert ", prior_save + 1, save), prior_save)
            prior_save = save

    def test_tier1_writer_is_dry_run_by_default(self):
        path = os.path.join(ROOT, "Scripts", "Editor", "create_tier1_art_assets.py")
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)
        main = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main")
        gate_index = next(i for i, node in enumerate(main.body)
                          if isinstance(node, ast.If) and "ONEBOSSFIGHT_EXECUTE_TIER1_ASSET_WRITES" in ast.get_source_segment(source, node))
        gate = main.body[gate_index]
        self.assertTrue(any(isinstance(node, ast.Return) for node in gate.body), "dry-run branch must return before writes")
        following_calls = [node for statement in main.body[gate_index + 1:]
                           for node in ast.walk(statement)
                           if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)]
        call_names = [node.func.id for node in following_calls]
        self.assertIn("create_vfx_assets", call_names)
        self.assertIn("create_a2_montage", call_names)

    def test_incomplete_a2_factory_path_fails_closed(self):
        path = os.path.join(ROOT, "Scripts", "Editor", "create_tier1_art_assets.py")
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)
        create_a2 = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "create_a2_montage")
        body = ast.get_source_segment(source, create_a2)
        self.assertIn("REFUSE T1c", body)
        self.assertNotIn("create_asset", body)
        self.assertNotIn("save_loaded_asset", body)

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
