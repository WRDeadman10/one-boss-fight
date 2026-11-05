#!/usr/bin/env python3
"""Offline contract checks for the G2 PIE recovery-driver registration."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]


class SelectionRefusalDriverTests(unittest.TestCase):
    def test_registered_with_bounded_result_gate(self):
        runner = (ROOT / "Scripts" / "RunDrivers.ps1").read_text(encoding="utf-8")
        self.assertRegex(runner, r"\{\s*N\s*=\s*'pie_selection_refusal';\s*K\s*=\s*'R';\s*Min\s*=\s*\d+;\s*T\s*=\s*\d+")

    def test_driver_covers_refusal_and_recovery_without_asset_save(self):
        driver = (ROOT / "Scripts" / "Editor" / "pie_selection_refusal.py").read_text(encoding="utf-8")
        for token in ("missing", "corrupt_hash", "clear_legacy", "unreal.new_object",
                      "stable_manifest_hash", "build_encounter_parity_snapshot", "HardError",
                      "EncounterDefinition.ManifestShape", "Shot ShowUI", "editor_request_begin_play",
                      "editor_request_end_play", "RESULT %d/%d passed"):
            self.assertIn(token, driver)
        self.assertNotRegex(driver, r"save_loaded_asset|save_asset|save_package")
        self.assertIn('"rpg.EncounterDefinition " + selection', driver)
        self.assertIn("selection = '\"\"'", driver)

    def test_registration_is_unique(self):
        runner = (ROOT / "Scripts" / "RunDrivers.ps1").read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r"N\s*=\s*'pie_selection_refusal'", runner)), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
