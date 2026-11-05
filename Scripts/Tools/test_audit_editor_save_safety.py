#!/usr/bin/env python3
"""Fixtures for Editor content first-save and pre-save guard auditing."""
import importlib.util
from pathlib import Path
import sys
import unittest

MODULE_PATH = Path(__file__).with_name("audit_editor_save_safety.py")
sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location("audit_editor_save_safety", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class EditorSaveSafetyTests(unittest.TestCase):
    def test_first_save_and_prior_assertions_and_guard_are_reported(self):
        source = '''
assert asset is not None
if unreal.EditorAssetLibrary.does_asset_exist(PATH):
    raise RuntimeError("destination already exists")
unreal.EditorAssetLibrary.save_loaded_asset(asset)
'''
        result = MODULE.analyze(source)
        self.assertEqual(result["first_save"], 5)
        self.assertEqual(result["save_api"], "save_loaded_asset")
        self.assertEqual(result["assertions"], [2, 4])
        self.assertEqual(result["guards"], [3, 4])

    def test_no_explicit_save_is_not_invented(self):
        result = MODULE.analyze("asset.set_editor_property('x', 1)\n")
        self.assertIsNone(result["first_save"])
        self.assertEqual(result["assertions"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
