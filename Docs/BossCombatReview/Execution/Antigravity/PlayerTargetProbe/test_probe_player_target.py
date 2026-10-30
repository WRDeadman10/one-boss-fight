#!/usr/bin/env python3
"""
test_probe_player_target.py
Offline test suite verifying probe_player_target.py syntax, read-only safety, and tag contracts.
"""
import ast
import unittest
from pathlib import Path

PROBE_PATH = Path("Docs/BossCombatReview/Execution/Antigravity/PlayerTargetProbe/probe_player_target.py")


class TestProbePlayerTarget(unittest.TestCase):
    def test_file_exists_and_pure_crlf(self):
        self.assertTrue(PROBE_PATH.is_file(), f"Missing probe script: {PROBE_PATH}")
        raw = PROBE_PATH.read_bytes()
        self.assertNotIn(b"\r\r\n", raw, "Double CRLF detected")
        self.assertIn(b"\r\n", raw, "CRLF missing")
        for idx, b in enumerate(raw):
            if b == 0x0A:
                self.assertTrue(idx > 0 and raw[idx - 1] == 0x0D, f"Bare LF at byte {idx}")

    def test_ast_parse(self):
        text = PROBE_PATH.read_text(encoding="utf-8")
        parsed = ast.parse(text)
        self.assertIsInstance(parsed, ast.Module)

    def test_read_only_contract(self):
        text = PROBE_PATH.read_text(encoding="utf-8")
        forbidden = [
            "save_asset", "save_package", "save_loaded_asset",
            "set_editor_property('health'", "checkout", "delete_asset"
        ]
        for f in forbidden:
            self.assertNotIn(f, text, f"Forbidden mutating call found: {f}")

    def test_expected_target_classes_and_tags(self):
        text = PROBE_PATH.read_text(encoding="utf-8")
        expected_tokens = [
            "BP_CombatPlayerCharacter",
            "BP_BaseCombatCharacter",
            "SKM_CombatMannequin_Simple",
            "capsule_radius",
            "capsule_half_height",
            "[TARGET_PROBE_",
            "[TARGET_PROBE_COMPLETE]",
        ]
        for tok in expected_tokens:
            self.assertIn(tok, text, f"Missing expected token: {tok}")


if __name__ == "__main__":
    unittest.main()
