#!/usr/bin/env python3
"""Fixtures for UE Python reflected enum access conventions."""
import importlib.util
from pathlib import Path
import sys
import unittest

MODULE_PATH = Path(__file__).with_name("check_ue_python_enum_conventions.py")
SPEC = importlib.util.spec_from_file_location("check_ue_python_enum_conventions", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class UePythonEnumConventionTests(unittest.TestCase):
    def test_e_prefix_is_flagged_for_reflected_enum(self):
        issues = MODULE.scan_text("unreal.ERPGBossDeathMode.OWN_CLIP", "fixture.py")
        self.assertTrue(any("E-prefixed" in issue for issue in issues))

    def test_canonical_class_member_and_value_pass(self):
        self.assertEqual(MODULE.scan_text("unreal.RPGBossComboOutcome.PARRIED.value"), [])

    def test_noncanonical_member_is_flagged(self):
        issues = MODULE.scan_text("unreal.RPGBossComboOutcome.Parried", "fixture.py")
        self.assertTrue(any("unknown/noncanonical" in issue for issue in issues))

    def test_integer_enum_coercion_is_flagged_but_schema_integer_is_allowed(self):
        issues = MODULE.scan_text("x = int(unreal.RPGBossDeathMode.OWN_CLIP)\ny = int(schema)", "fixture.py")
        self.assertEqual(len(issues), 1)
        self.assertIn("integer coercion", issues[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
