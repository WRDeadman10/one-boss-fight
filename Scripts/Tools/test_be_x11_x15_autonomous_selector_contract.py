#!/usr/bin/env python3
"""Offline source contract for Queue BE selector-driven test start (X11-X15)."""
from pathlib import Path
import ast
import unittest

ROOT = Path(__file__).resolve().parents[2]
CHARACTER_H = (ROOT / "Source/OneBossFight/Boss/RPGFrameworkBossCharacter.h").read_text(encoding="utf-8")
CHARACTER_CPP = (ROOT / "Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp").read_text(encoding="utf-8")
DRIVER = (ROOT / "Scripts/Editor/pie_sevarog_framework_live.py").read_text(encoding="utf-8")
SELECTOR_TESTS = (ROOT / "Source/OneBossFight/Tests/RPGBossMoveSelectorTests.cpp").read_text(encoding="utf-8")
TERMINAL_TESTS = (ROOT / "Source/OneBossFight/Tests/RPGNativeBossHealthTests.cpp").read_text(encoding="utf-8")


def function_source(source: str, name: str) -> str:
    tree = ast.parse(source)
    node = next(n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name)
    return ast.get_source_segment(source, node) or ""


class AutonomousSelectorContract(unittest.TestCase):
    def test_selector_entry_is_id_free_and_uses_production_selector(self):
        self.assertIn("FName StartSelectedCardForTest();", CHARACTER_H)
        self.assertIn("FName ARPGFrameworkBossCharacter::StartSelectedCardForTest()", CHARACTER_CPP)
        method = CHARACTER_CPP.split("FName ARPGFrameworkBossCharacter::StartSelectedCardForTest()", 1)[1]
        method = method.split("bool ARPGFrameworkBossCharacter::GetOutcomeForTest()", 1)[0] if "bool ARPGFrameworkBossCharacter::GetOutcomeForTest()" in method else method.split("FName ARPGFrameworkBossCharacter::GetOutcomeForTest()", 1)[0]
        self.assertIn("Selector.Select(Executor->Model(),Snapshot,Decision,Context)", method)
        self.assertIn("Snapshot.PhaseId", method)
        self.assertIn("GenerationId", method)

    def test_outcome_and_bounded_driver_have_cleanup_and_no_save_receipts(self):
        self.assertIn('FName ARPGFrameworkBossCharacter::GetOutcomeForTest() const', CHARACTER_CPP)
        self.assertIn('return TEXT("BossDefeated")', CHARACTER_CPP)
        self.assertIn('return TEXT("Succeeded")', CHARACTER_CPP)
        self.assertIn('return TEXT("Failed")', CHARACTER_CPP)
        self.assertIn("max(5, min(90, requested))", DRIVER)
        tick = function_source(DRIVER, "tick_autonomous_selector")
        self.assertIn("start_selected_card_for_test", tick)
        self.assertIn("get_outcome_for_test", tick)
        self.assertIn("finish(", tick)
        self.assertIn("saves=0", tick)
        self.assertNotIn("start_card_for_test", tick)

    def test_existing_no_candidate_cooldown_and_terminal_regressions_remain(self):
        self.assertIn('"Selector.Cooldown"', SELECTOR_TESTS)
        self.assertIn('"no choice"', SELECTOR_TESTS)
        self.assertIn("ShouldAccept(7, 7, 0, true, 0.0)", TERMINAL_TESTS)
        self.assertIn("ShouldAccept(7, 7, 7, true, 0.0)", TERMINAL_TESTS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
