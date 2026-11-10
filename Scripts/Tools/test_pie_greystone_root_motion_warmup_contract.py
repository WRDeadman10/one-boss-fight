#!/usr/bin/env python3
"""Offline AST contract test (C-1283) for pie_greystone_root_motion.py warm-up before dodge key injection."""

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DRIVER_PATH = ROOT / "Scripts" / "Editor" / "pie_greystone_root_motion.py"
KNOWN_ISSUES_PATH = ROOT / "Documentation" / "KNOWN_ISSUES.md"


class PieGreystoneRootMotionWarmupContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = DRIVER_PATH.read_text(encoding="utf-8")
        self.tree = ast.parse(self.source, filename=str(DRIVER_PATH))
        self.known_issues = KNOWN_ISSUES_PATH.read_text(encoding="utf-8")

    def _get_function(self, name: str) -> ast.FunctionDef:
        for node in self.tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == name:
                return node
        self.fail(f"Missing function definition: {name}")

    @staticmethod
    def _phase_if_branch(tick_fn: ast.FunctionDef, phase_name: str) -> ast.If:
        """Return top-level `if S['phase'] == phase_name:` branch inside `_tick`."""
        for stmt in tick_fn.body:
            if not isinstance(stmt, ast.If):
                continue
            test = stmt.test
            if (
                isinstance(test, ast.Compare)
                and len(test.comparators) == 1
                and isinstance(test.comparators[0], ast.Constant)
                and test.comparators[0].value == phase_name
                and isinstance(test.left, ast.Subscript)
                and isinstance(test.left.value, ast.Name)
                and test.left.value.id == "S"
            ):
                return stmt
        raise AssertionError(f"Missing phase branch S['phase'] == {phase_name!r} in _tick")

    @staticmethod
    def _next_phase_transitions(branch: ast.If) -> list[str]:
        """Extract `S.update(phase=...)` target phase strings within an AST branch."""
        targets: list[str] = []
        for node in ast.walk(branch):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "update"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "S"
            ):
                for kw in node.keywords:
                    if kw.arg == "phase" and isinstance(kw.value, ast.Constant):
                        targets.append(str(kw.value.value))
        return targets

    @staticmethod
    def _contains_string(node: ast.AST, text: str) -> bool:
        return any(
            isinstance(n, ast.Constant) and n.value == text
            for n in ast.walk(node)
        )

    @staticmethod
    def _contains_key_call(node: ast.AST) -> bool:
        return any(
            isinstance(n, ast.Call)
            and isinstance(n.func, ast.Name)
            and n.func.id == "key"
            for n in ast.walk(node)
        )

    def test_enter_combat_settle_warmup_phases_precede_face_button_right_press(self) -> None:
        enter_fn = self._get_function("enter_combat_tag")
        self.assertTrue(
            self._contains_string(enter_fn, '(GameplayTags=((TagName="Ability.EnterCombat")))'),
            "enter_combat_tag must request Ability.EnterCombat",
        )

        tick_fn = self._get_function("_tick")
        setup_branch = self._phase_if_branch(tick_fn, "setup")
        settle_branch = self._phase_if_branch(tick_fn, "settle")
        warmup_branch = self._phase_if_branch(tick_fn, "warmup")
        trial_wait_branch = self._phase_if_branch(tick_fn, "trial_wait")
        input_branch = self._phase_if_branch(tick_fn, "input")

        # Exact phase state machine chain before first dodge press:
        # start -> setup (Ability.EnterCombat) -> settle (>12s) -> warmup (R2 draw + >3.7s) -> trial_wait -> input
        self.assertIn("settle", self._next_phase_transitions(setup_branch))
        self.assertTrue(
            any(
                isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "enter_combat_tag"
                for n in ast.walk(setup_branch)
            ),
            "setup phase must trigger enter_combat_tag before entering settle",
        )
        self.assertFalse(self._contains_string(setup_branch, "Gamepad_FaceButton_Right"))
        self.assertFalse(self._contains_key_call(setup_branch))

        self.assertIn("warmup", self._next_phase_transitions(settle_branch))
        self.assertFalse(self._contains_string(settle_branch, "Gamepad_FaceButton_Right"))
        self.assertFalse(self._contains_key_call(settle_branch))

        self.assertIn("trial_wait", self._next_phase_transitions(warmup_branch))
        self.assertTrue(self._contains_string(warmup_branch, "Gamepad_RightTrigger"))
        self.assertTrue(self._contains_key_call(warmup_branch))
        self.assertFalse(
            self._contains_string(warmup_branch, "Gamepad_FaceButton_Right"),
            "warmup must only press Gamepad_RightTrigger, never Gamepad_FaceButton_Right",
        )

        self.assertIn("input", self._next_phase_transitions(trial_wait_branch))
        self.assertTrue(self._contains_string(trial_wait_branch, "Gamepad_FaceButton_Right"))
        self.assertFalse(
            self._contains_key_call(trial_wait_branch),
            "trial_wait prepares events but must defer pressing until input phase",
        )
        self.assertTrue(self._contains_key_call(input_branch))

    def test_known_issues_documents_setkeydown_input_chain(self) -> None:
        for required in (
            "RPGInputTestUtils.cpp",
            "SetKeyDown -> APlayerController::InputKey -> UPlayerInput::InputKey",
            "UEnhancedPlayerInput::IsKeyHandledByAction",
            "Ability.EnterCombat",
        ):
            self.assertIn(required, self.known_issues)


if __name__ == "__main__":
    unittest.main()
