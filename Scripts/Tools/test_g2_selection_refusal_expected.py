#!/usr/bin/env python3
"""Offline tests for expected-sheet coverage of the G2 refusal driver."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

MODULE_PATH = Path(__file__).with_name("check_g2_selection_refusal_expected.py")
SPEC = importlib.util.spec_from_file_location("check_g2_selection_refusal_expected", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
ROOT = Path(__file__).resolve().parents[2]


class G2ExpectedSheetTests(unittest.TestCase):
    def setUp(self):
        self.sheet = json.loads((Path(__file__).with_name("g2_selection_refusal_expected.json")).read_text(encoding="utf-8"))
        self.driver = (ROOT / "Scripts/Editor/pie_selection_refusal.py").read_text(encoding="utf-8")

    def test_real_driver_covers_expected_sheet(self):
        self.assertEqual(MODULE.audit(self.sheet, self.driver), [])

    def test_omitted_token_is_detected(self):
        self.sheet["required_log_tokens"].append("[SelectionRefusal] MISSING_FIXTURE")
        issues = MODULE.audit(self.sheet, self.driver)
        self.assertTrue(any("MISSING_FIXTURE" in issue for issue in issues))

    def test_duplicate_expected_case_is_rejected(self):
        self.sheet["cases"].append("missing")
        self.assertTrue(any("unique list" in issue for issue in MODULE.audit(self.sheet, self.driver)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
