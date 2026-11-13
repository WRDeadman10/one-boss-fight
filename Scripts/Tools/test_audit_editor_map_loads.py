#!/usr/bin/env python3
"""Fixtures for the static editor-script known-map load audit."""
import importlib.util
from pathlib import Path
import sys
import unittest

MODULE_PATH = Path(__file__).with_name("audit_editor_map_loads.py")
SPEC = importlib.util.spec_from_file_location("audit_editor_map_loads", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class EditorMapLoadAuditTests(unittest.TestCase):
    def setUp(self):
        self.known = {"/Game/OneBossFight/Maps/L_SevarogArena"}

    def test_known_map_load_is_flagged(self):
        findings = MODULE.scan_text('unreal.load_asset("/Game/OneBossFight/Maps/L_SevarogArena")', self.known, "map.py")
        self.assertEqual(len(findings), 1)
        self.assertIn("map package", findings[0])

    def test_normal_asset_load_is_allowed(self):
        findings = MODULE.scan_text('unreal.load_asset("/Game/OneBossFight/Data/DA_Encounter")', self.known, "asset.py")
        self.assertEqual(findings, [])

    def test_constant_concatenated_map_path_is_flagged(self):
        source = 'unreal.EditorAssetLibrary.load_asset("/Game/OneBossFight/Levels/" + "L_SevarogArena")'
        self.assertEqual(len(MODULE.scan_text(source, self.known)), 1)

    def test_dynamic_path_is_outside_static_audit_scope(self):
        self.assertEqual(MODULE.scan_text("unreal.load_asset(path)", self.known), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
