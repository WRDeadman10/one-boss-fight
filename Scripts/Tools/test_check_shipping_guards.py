#!/usr/bin/env python3
"""Focused fixtures for the Shipping-only console variable guard checker."""
import importlib.util
from pathlib import Path
import sys
import unittest

MODULE_PATH = Path(__file__).with_name("check_shipping_guards.py")
MODULE_SPEC = importlib.util.spec_from_file_location("check_shipping_guards", MODULE_PATH)
GUARD_MODULE = importlib.util.module_from_spec(MODULE_SPEC)
sys.modules[MODULE_SPEC.name] = GUARD_MODULE
MODULE_SPEC.loader.exec_module(GUARD_MODULE)
scan_text = GUARD_MODULE.scan_text


class ShippingGuardTests(unittest.TestCase):
    def test_project_source_has_no_shipping_visible_guarded_cvar_uses(self):
        source_root = Path(__file__).resolve().parents[2] / "Source"
        declarations, findings = GUARD_MODULE.scan_tree(source_root)
        self.assertGreater(len(declarations), 0)
        self.assertEqual(findings, [])

    def test_guarded_development_use_passes(self):
        source = """#if !UE_BUILD_SHIPPING
static TAutoConsoleVariable<int32> CVarCueMode(TEXT(\"rpg.CueMode\"), 0);
#endif
void Fire()
{
#if !UE_BUILD_SHIPPING
    const int Mode = CVarCueMode.GetValueOnGameThread();
#else
    const int Mode = 0;
#endif
}
"""
        declarations, findings = scan_text(source)
        self.assertEqual([d.name for d in declarations], ["CVarCueMode"])
        self.assertEqual(findings, [])

    def test_unguarded_shipping_reference_fails(self):
        source = """#if !UE_BUILD_SHIPPING
static TAutoConsoleVariable<int32> CVarCueMode(TEXT(\"rpg.CueMode\"), 0);
#endif
void Fire()
{
    const int Mode = CVarCueMode.GetValueOnGameThread();
}
"""
        declarations, findings = scan_text(source, "fixture.cpp")
        self.assertEqual(len(declarations), 1)
        self.assertEqual([(f.declaration.name, f.use_line) for f in findings], [("CVarCueMode", 6)])

    def test_else_shipping_branch_is_checked(self):
        source = """#if !UE_BUILD_SHIPPING
static TAutoConsoleVariable<int32> CVarTest(TEXT(\"rpg.Test\"), 0);
#else
int Use = CVarTest;
#endif
"""
        _, findings = scan_text(source)
        self.assertEqual(len(findings), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
