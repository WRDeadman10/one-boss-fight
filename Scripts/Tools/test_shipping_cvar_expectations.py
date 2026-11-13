"""BQ-73 in-process tests for shipping_cvar_expectations (real Source tree read-only, plus synthetic text). Nothing is run."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shipping_cvar_expectations as S  # noqa: E402
import importlib.util

CHECKER_PATH = Path(__file__).resolve().parents[2] / "Scripts" / "CheckShippingBinary.py"
_spec = importlib.util.spec_from_file_location("check_shipping_binary", CHECKER_PATH)
CHECKER = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(CHECKER)

ROOT = Path(__file__).resolve().parents[2]


class PreprocessorStates(unittest.TestCase):
    def test_guard_shapes(self):
        text = "\n".join([
            "a",                              # 1 included
            "#if !UE_BUILD_SHIPPING", "b",    # 3 excluded
            "#else", "c",                     # 5 included
            "#endif",
            "#if UE_BUILD_SHIPPING", "d",     # 8 included (Shipping-only)
            "#else", "e",                     # 10 excluded
            "#endif",
            "#if WITH_EDITOR", "#if !UE_BUILD_SHIPPING", "f", "#endif", "g", "#endif",  # line 14 excluded, 16 included
            "#if UE_BUILD_SHIPPING || WITH_EDITOR", "h", "#endif",                       # line 19 unknown
        ])
        states = S.shipping_state_per_line(text)
        self.assertEqual(states[0], "included")
        self.assertEqual(states[2], "excluded")
        self.assertEqual(states[4], "included")
        self.assertEqual(states[7], "included")
        self.assertEqual(states[9], "excluded")
        self.assertEqual(states[13], "excluded")
        self.assertEqual(states[15], "included")
        self.assertEqual(states[18], "unknown")
        dev = S.shipping_state_per_line(chr(10).join(["#if UE_BUILD_DEVELOPMENT", "x", "#endif"]))
        self.assertEqual(dev[1], "excluded")
        ifndef_shipping = S.shipping_state_per_line(chr(10).join(["#ifndef UE_BUILD_SHIPPING", "x", "#endif"]))
        self.assertEqual(ifndef_shipping[1], "excluded")
        ifndef_dev = S.shipping_state_per_line(chr(10).join(["#ifndef UE_BUILD_DEVELOPMENT", "x", "#endif"]))
        self.assertEqual(ifndef_dev[1], "included")
        ifdef_unknown = S.shipping_state_per_line(chr(10).join(["#ifdef UE_BUILD_CUSTOM", "x", "#endif"]))
        self.assertEqual(ifdef_unknown[1], "unknown")

    def test_synthetic_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "Source"
            src.mkdir()
            (src / "A.cpp").write_text("\n".join([
                'static TAutoConsoleVariable<int32> CVarA(TEXT("rpg.Visible"), 1, TEXT("x"), ECVF_Default);',
                "#if !UE_BUILD_SHIPPING",
                'static TAutoConsoleVariable<int32> CVarB(TEXT("rpg.DevOnly"), 0, TEXT("x"), ECVF_Default);',
                "#endif",
            ]), encoding="utf-8")
            exp = S.expectations(Path(tmp))
            self.assertEqual(exp["expected_present"], ["rpg.Visible"])
            self.assertEqual(exp["expected_absent"], ["rpg.DevOnly"])
            self.assertEqual(S.violations({"rpg.Visible"}, exp), [])
            self.assertEqual(S.violations({"rpg.DevOnly"}, exp), ["guarded cvar present in Shipping binary: rpg.DevOnly"])


class RealTree(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.exp = S.expectations(ROOT)

    def test_known_dev_only_switches_are_expected_absent(self):
        for name in ("rpg.GreystonePlayerTestPawn", "rpg.Posture.PinPackPoiseTest", "rpg.Perf.FireShadows",
                     "rpg.Perf.FireLights", "rpg.Perf.Embers",          # macro-registered, definition guarded
                     "rpg.Art.Tier1", "rpg.Art.Tier2", "rpg.AttackTracker.A2PreviewClip"):  # UE_BUILD_DEVELOPMENT only
            self.assertIn(name, self.exp["expected_absent"], name)

    def test_ki168_controls_are_expected_present(self):
        # BQ-23 disposition: these are registered unguarded today (guards proposed, not implemented)
        for name in ("rpg.BossOverlay", "rpg.CameraDebug", "rpg.Legend", "rpg.LegendShakeScale", "rpg.Build",
                     "rpg.CloseTelegraph", "rpg.Boss.ProjectHitReaction"):
            self.assertIn(name, self.exp["expected_present"], name)

    def test_exactly_the_seven_ki168_controls_are_shipping_visible(self):
        self.assertEqual(sorted(self.exp["expected_present"]), sorted([
            "rpg.BossOverlay", "rpg.CameraDebug", "rpg.Legend", "rpg.LegendShakeScale", "rpg.Build",
            "rpg.CloseTelegraph", "rpg.Boss.ProjectHitReaction"]))

    def test_no_unclassified_registrations(self):
        self.assertEqual(self.exp["unknown"], [])

    def test_binary_checker_fails_on_guarded_cvar_and_legacy_debug_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "Source"
            source.mkdir()
            (source / "A.cpp").write_text('\n'.join([
                '#if !UE_BUILD_SHIPPING',
                'static TAutoConsoleVariable<int32> CVarA(TEXT("rpg.TestGuarded"), 1, TEXT("x"), ECVF_Default);',
                '#endif',
            ]), encoding="utf-8")
            _, _, problems, debug = CHECKER.scan_binary(b"rpg.TestGuarded", root)
            self.assertEqual(len(problems), 1)
            self.assertEqual(debug, {})
            _, _, problems, debug = CHECKER.scan_binary("rpg.Debug".encode("utf-16-le"), root)
            self.assertEqual(problems, [])
            self.assertIn("rpg.Debug", debug)


if __name__ == "__main__":
    unittest.main()
