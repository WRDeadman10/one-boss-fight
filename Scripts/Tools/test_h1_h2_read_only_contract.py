#!/usr/bin/env python3
"""Offline syntax/scope checks for the H1 and H2 Lead-run Editor scripts."""
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


class G044ReadOnlyEditorToolTests(unittest.TestCase):
    def script(self, name):
        path = ROOT / "Scripts" / "Editor" / name
        source = path.read_text(encoding="utf-8")
        ast.parse(source, filename=str(path))
        return source

    def test_h1_caller_scan_targets_setter_and_does_not_save(self):
        source = self.script("report_selector_setter_callers.py")
        self.assertIn('TARGET = "SetSelectedDefinition"', source)
        self.assertIn('"ubergraph_pages", "function_graphs", "macro_graphs"', source)
        self.assertIn("level_script_blueprint", source)
        self.assertIn('graph_verdict =', source)
        self.assertIn('else "INCONCLUSIVE"', source)
        self.assertIn('"utf16_le"', source)
        self.assertIn('"utf16_be"', source)
        self.assertIn('"byte_search"', source)
        self.assertNotIn('SUMMARY callers=', source)
        self.assertIn("read_only", source)
        self.assertNotRegex(source, r"save_loaded_asset|save_asset|save_package|delete_asset")

    def test_h2_roots_and_dependency_modes_are_explicit(self):
        source = self.script("report_g044_dependency_census.py")
        for root in ("DA_Sevarog_G044_Encounter", "DA_Boss_EmberWarden_Draft",
                     "DA_Player_Hero_Draft_V3"):
            self.assertIn(root, source)
        self.assertIn("include_hard_package_references=True", source)
        self.assertIn("include_soft_package_references=True", source)
        self.assertIn("DirectoriesToAlwaysCook", source)
        self.assertIn("combined_closure", source)
        self.assertNotRegex(source, r"save_loaded_asset|save_asset|save_package|delete_asset")


if __name__ == "__main__":
    unittest.main(verbosity=2)
