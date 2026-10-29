#!/usr/bin/env python3
"""
test_probe_unreal_api.py - Unit Tests for Read-Only Unreal API Reflection Probe

Authored for Task Order A-206 (C-301).
Tests static AST attribute chain extraction, pythonized struct property extraction,
offline execution fallback, and runtime report formatting with a mock `unreal` module.
"""

import os
import sys
import tempfile
import unittest

# Path independence setup
def setup_path():
    cur = os.path.abspath(os.path.dirname(__file__))
    while cur and cur != os.path.dirname(cur):
        if os.path.exists(os.path.join(cur, "Source", "OneBossFight")) or os.path.exists(os.path.join(cur, ".git")):
            if cur not in sys.path:
                sys.path.insert(0, cur)
            return cur
        cur = os.path.dirname(cur)
    fallback = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
    if fallback not in sys.path:
        sys.path.insert(0, fallback)
    return fallback

REPO_ROOT = setup_path()

from Docs.BossCombatReview.Execution.Antigravity.AuthoringToolkit.probe_unreal_api import (
    extract_static_chains,
    extract_python_property_names,
    resolve_unreal_chain,
    run_probe,
    REFLECTION_CANDIDATES
)

class MockSystemLibrary:
    pass

class MockEditorAssetLibrary:
    @staticmethod
    def does_asset_exist(path):
        return True

class MockBleedConfig:
    initial_threshold = 100.0
    hp_fraction = 0.03
    def _private_func(self):
        pass

class MockDeathModeEnum:
    OwnClip = 0
    PackMontage = 1

class MockUnrealModule:
    """Mock `unreal` module simulating partial engine reflection presence."""
    def __init__(self):
        self.SystemLibrary = MockSystemLibrary()
        self.EditorAssetLibrary = MockEditorAssetLibrary()
        self.RPGBleedConfig = MockBleedConfig
        self.ERPGBossDeathMode = MockDeathModeEnum

    def load_class(self, outer, path):
        return None

class TestProbeUnrealApi(unittest.TestCase):

    def test_static_extraction_not_empty(self):
        """Verify AST extraction retrieves attribute chains across all three toolkit files."""
        chains = extract_static_chains(repo_root=REPO_ROOT)
        self.assertGreater(len(chains), 30, "Should extract more than 30 attribute citations")

        chain_names = set(c[0] for c in chains)
        # Check required core chains
        self.assertIn("unreal.EditorAssetLibrary", chain_names)
        self.assertIn("unreal.EditorAssetLibrary.does_asset_exist", chain_names)
        self.assertIn("unreal.SystemLibrary", chain_names)
        self.assertIn("unreal.SystemLibrary.is_editor", chain_names)
        self.assertIn("unreal.UnrealEditorSubsystem.get_game_world", chain_names)
        self.assertIn("unreal.AssetToolsHelpers.get_asset_tools", chain_names)
        self.assertIn("unreal.load_class", chain_names)
        self.assertIn("unreal.load_package", chain_names)

        # Check citations have valid file:line format
        for chain, fpath, lno in chains:
            self.assertTrue(fpath.endswith(".py"))
            self.assertGreater(lno, 0)

    def test_struct_property_extraction(self):
        """Verify pythonized property mappings are extracted for all 17 structs."""
        py_props = extract_python_property_names()
        self.assertEqual(len(py_props), 17, "Must extract properties for exactly 17 structs")

        # Spot-check critical pythonized property names
        self.assertIn("a1_montage", py_props["close_clip_swap"])
        self.assertIn("a3a_montage", py_props["close_clip_swap"])
        self.assertIn("close_ability_class_name", py_props["close_clip_swap"])
        self.assertIn("death_mode", py_props["death"])
        self.assertIn("guard_pack_death", py_props["death"])
        self.assertIn("initial_threshold", py_props["bleed"])
        self.assertIn("stagger_seconds", py_props["stagger_policy"])
        self.assertIn("use_clips", py_props["stagger_profile"])
        self.assertIn("field_path", py_props["fields"])

    def test_offline_probe_output_format(self):
        """Verify report format when unreal is not importable (offline run)."""
        lines, present, missing = run_probe(unreal_mod=None)
        report_text = "\n".join(lines)

        self.assertIn("=== STATIC UNREAL API CHAINS & CITATIONS ===", report_text)
        self.assertIn("=== PYTHONIZED STRUCT PROPERTY MAPPINGS (STRUCT_SPECS) ===", report_text)
        self.assertIn("[PROBE] unreal not importable: runtime part skipped", report_text)
        self.assertIn("[PROBE] SUMMARY missing=0 present=0", report_text)
        self.assertEqual(present, 0)
        self.assertEqual(missing, 0)

    def test_mock_unreal_probe_runtime(self):
        """Verify runtime probe execution, formatting, and counting with a mock unreal module."""
        mock_unreal = MockUnrealModule()
        lines, present, missing = run_probe(unreal_mod=mock_unreal)
        report_text = "\n".join(lines)

        self.assertIn("=== RUNTIME PROBE EXECUTION (import unreal SUCCEEDED) ===", report_text)
        self.assertIn("[PROBE] unreal.EditorAssetLibrary.does_asset_exist exists=True callable=True type=function", report_text)
        # SystemLibrary exists on mock, but is_editor does not!
        self.assertIn("[PROBE] unreal.SystemLibrary.is_editor exists=False callable=False type=none", report_text)
        # Reflection struct and enum discovery
        self.assertIn("[PROBE] STRUCT RPGBleedConfig properties=['hp_fraction', 'initial_threshold']", report_text)
        self.assertIn("[PROBE] ENUM ERPGBossDeathMode enumerators=", report_text)

        # Summary line
        self.assertGreater(present, 0)
        self.assertGreater(missing, 0)
        self.assertIn(f"[PROBE] SUMMARY missing={missing} present={present}", report_text)

    def test_resolve_unreal_chain_stepwise(self):
        """Verify resolve_unreal_chain accurately handles attribute walks."""
        mock_unreal = MockUnrealModule()
        exists, is_call, type_name = resolve_unreal_chain(mock_unreal, "unreal.EditorAssetLibrary.does_asset_exist")
        self.assertTrue(exists)
        self.assertTrue(is_call)

        exists_missing, is_call_missing, type_missing = resolve_unreal_chain(mock_unreal, "unreal.NonExistentService.action")
        self.assertFalse(exists_missing)
        self.assertFalse(is_call_missing)
        self.assertEqual(type_missing, "none")

if __name__ == "__main__":
    unittest.main()
