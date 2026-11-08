#!/usr/bin/env python3
"""Fixtures for stable PackagedSmoke receipt-token validation."""
import importlib.util
from pathlib import Path
import sys
import unittest

MODULE_PATH = Path(__file__).with_name("check_packaged_smoke_receipt.py")
SPEC = importlib.util.spec_from_file_location("check_packaged_smoke_receipt", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


SHIPPING = """[Smoke] PASS process 21 remained alive for 20 s
[Smoke] PASS Shipping binary check
[Smoke] VERDICT PASS (Shipping: alive and no debug names)
"""


class PackagedSmokeReceiptTests(unittest.TestCase):
    def test_valid_shipping_receipt(self):
        self.assertEqual(MODULE.validate(SHIPPING, "Shipping", 0), [])

    def test_absent_required_token_fails(self):
        issues = MODULE.validate(SHIPPING.replace("PASS Shipping binary check\n", ""), "Shipping", 0)
        self.assertTrue(any("exactly one Shipping validation result" in item for item in issues))

    def test_duplicate_required_token_fails(self):
        issues = MODULE.validate(SHIPPING.replace("[Smoke] VERDICT", "[Smoke] PASS Shipping binary check\n[Smoke] VERDICT"), "Shipping", 0)
        self.assertTrue(any("exactly one Shipping validation result" in item for item in issues))

    def test_contradictory_token_fails(self):
        text = SHIPPING.replace("PASS Shipping binary check", "FAIL Shipping binary check exit 1")
        issues = MODULE.validate(text, "Shipping", 0)
        self.assertIn("verdict contradicts process and configuration check results", issues)

    def test_wrong_route_token_fails(self):
        text = SHIPPING + "[Smoke] PASS packaged log checker\n"
        issues = MODULE.validate(text, "Shipping", 0)
        self.assertTrue(any("other configuration" in item for item in issues))

    def test_exit_code_must_match_verdict(self):
        issues = MODULE.validate(SHIPPING, "Shipping", 1)
        self.assertIn("process exit code contradicts verdict", issues)

    def test_zero_second_survival_cannot_be_accepted_as_smoke(self):
        text = SHIPPING.replace("remained alive for 20 s", "remained alive for 0 s")
        issues = MODULE.validate(text, "Shipping", 0)
        self.assertIn("process survival duration must be at least one second", issues)


if __name__ == "__main__":
    unittest.main(verbosity=2)
