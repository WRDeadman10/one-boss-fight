#!/usr/bin/env python3
"""Tests for the A5 scheduled-driver registration audit."""
import importlib.util
from pathlib import Path
import sys
import unittest

MODULE_PATH = Path(__file__).with_name("audit_a5_driver_registration.py")
SPEC = importlib.util.spec_from_file_location("audit_a5_driver_registration", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
ROOT = Path(__file__).resolve().parents[2]


class A5RegistrationAuditTests(unittest.TestCase):
    def test_project_registration_has_no_missing_or_extra_a5_rows(self):
        expected = MODULE.literal_assignment(ROOT / "Scripts/Tools/write_a4_parity_receipt.py", "DRIVERS")
        allowed = MODULE.literal_assignment(ROOT / "Scripts/Editor/run_a5_parity_driver_and_quit.py", "ALLOWED")
        scheduled = MODULE.run_driver_rows((ROOT / "Scripts/RunDrivers.ps1").read_text(encoding="utf-8"))
        rows, issues = MODULE.audit(expected, scheduled, allowed, a4_registered=True)
        self.assertEqual(len(rows), len(expected))
        self.assertEqual(issues, [])
        self.assertTrue(all(timeout > 0 for *_prefix, timeout in rows))

    def test_missing_expected_driver_is_reported(self):
        rows, issues = MODULE.audit({"pie_one": ("One", 3)}, {}, {})
        self.assertEqual(rows, [])
        self.assertIn("MISSING RunDrivers registration: pie_one", issues)
        self.assertIn("MISSING A5 runner registration: pie_one", issues)

    def test_wrong_minimum_is_reported(self):
        _, issues = MODULE.audit({"pie_one": ("One", 3)}, {"pie_one": ("R", 4, 90)}, {"pie_one": 90})
        self.assertIn("MISMATCH pie_one: receipt minimum 3, RunDrivers minimum 4", issues)

    def test_unexpected_a5_runner_is_reported(self):
        _, issues = MODULE.audit({}, {}, {"pie_unexpected": 30})
        self.assertIn("EXTRA A5 runner registration: pie_unexpected", issues)

    def test_standalone_memory_soak_is_not_a_parity_receipt_row(self):
        _, issues = MODULE.audit({}, {}, {"pie_memory_soak": 1200})
        self.assertNotIn("EXTRA A5 runner registration: pie_memory_soak", issues)


if __name__ == "__main__":
    unittest.main(verbosity=2)
