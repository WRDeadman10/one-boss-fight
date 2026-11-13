#!/usr/bin/env python3
"""Offline contract for Queue BE navigation diagnostics (X16-X20)."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
CONTROLLER = (ROOT / "Source/OneBossFight/Boss/RPGFrameworkBossController.cpp").read_text(encoding="utf-8")
RULES = (ROOT / "Source/OneBossFight/Boss/RPGBossNavigationDiagnostics.h").read_text(encoding="utf-8")
CHARACTER_H = (ROOT / "Source/OneBossFight/Boss/RPGFrameworkBossCharacter.h").read_text(encoding="utf-8")
CHARACTER_CPP = (ROOT / "Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp").read_text(encoding="utf-8")
DRIVER = (ROOT / "Scripts/Editor/pie_sevarog_framework_live.py").read_text(encoding="utf-8")
NATIVE = (ROOT / "Source/OneBossFight/Tests/RPGFrameworkRuntimeTests.cpp").read_text(encoding="utf-8")
CHECKLIST = (ROOT / "Documentation/Boss/BE_X16_X20_NAVIGATION_DIAGNOSIS.md").read_text(encoding="utf-8")


class NavigationDiagnosticsContract(unittest.TestCase):
    def test_owned_completion_captures_code_flags_and_terminal_geometry(self):
        self.assertIn("Result.Code.GetValue(),Result.Flags", CONTROLLER)
        self.assertIn("Error.Reset();LastDiagnostic.Reset();", CONTROLLER)
        self.assertIn("nav_terminal %s", CONTROLLER)
        self.assertIn("remainingCm=%.1f", RULES)
        self.assertIn("OwnedGeneration=Boss->NativeEncounterGeneration()", CONTROLLER)

    def test_lead_driver_requires_explicit_navigation_summary(self):
        self.assertIn("GetNavigationResultForTest", CHARACTER_H)
        self.assertIn("status=TEST_WALK_SKIPPED", CHARACTER_CPP)
        self.assertIn('if not summary or summary in ("PENDING", "Unavailable", "None"):', DRIVER)
        self.assertIn('validate_navigation_identity(summary,', DRIVER)
        self.assertIn('log("NAV_RESULT " + summary)', DRIVER)

    def test_native_formatting_cases_and_one_run_checklist_exist(self):
        for code in ("Success", "Invalid", "Blocked", "Aborted"):
            self.assertIn("code=%s" % code, NATIVE)
        for required in ("Recast", "projection", "request", "terminal", "unique IDs"):
            self.assertIn(required, CHECKLIST)


if __name__ == "__main__":
    unittest.main(verbosity=2)
