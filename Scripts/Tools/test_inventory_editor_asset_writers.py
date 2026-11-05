#!/usr/bin/env python3
"""Fixtures for source-based Editor writer classification."""
import importlib.util
from pathlib import Path
import sys
import unittest

MODULE_PATH = Path(__file__).with_name("inventory_editor_asset_writers.py")
sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location("inventory_editor_asset_writers", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class EditorWriterInventoryTests(unittest.TestCase):
    def test_map_setup_takes_primary_classification(self):
        category, markers = MODULE.classify('asset_tools.create_asset(name, path)\nunreal.EditorLoadingAndSavingUtils.save_map(world, path)')
        self.assertEqual(category, "map_setup")
        self.assertIn("save_map", markers)

    def test_asset_creation_and_modification_are_separated(self):
        category, markers = MODULE.classify("tools.duplicate_asset(name, folder, source)")
        self.assertEqual((category, markers), ("creates", ["duplicate_asset"]))
        self.assertEqual(MODULE.classify('asset.set_editor_property("field", value)')[0], "modifies")

    def test_non_writer_is_read_only(self):
        self.assertEqual(MODULE.classify("print(asset.get_name())"), ("read-only", []))


if __name__ == "__main__":
    unittest.main(verbosity=2)
