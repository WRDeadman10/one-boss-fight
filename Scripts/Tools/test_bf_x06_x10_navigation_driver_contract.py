#!/usr/bin/env python3
"""Offline resilience contracts for Queue BF-X06..X10."""
from __future__ import annotations

import ast
import os
from pathlib import Path
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
DRIVER_PATH = ROOT / "Scripts/Editor/pie_sevarog_framework_live.py"
DRIVER_TEXT = DRIVER_PATH.read_text(encoding="utf-8")
CONTROLLER_PATH = ROOT / "Source/OneBossFight/Boss/RPGFrameworkBossController.cpp"
CONTROLLER_TEXT = CONTROLLER_PATH.read_text(encoding="utf-8")
CHARACTER_PATH = ROOT / "Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp"
CHARACTER_TEXT = CHARACTER_PATH.read_text(encoding="utf-8")
NAV_RULES_PATH = ROOT / "Source/OneBossFight/Boss/RPGBossNavigationDiagnostics.h"
NAV_RULES_TEXT = NAV_RULES_PATH.read_text(encoding="utf-8")


def load_functions(*names):
    tree = ast.parse(DRIVER_TEXT, filename=str(DRIVER_PATH))
    selected = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    if {node.name for node in selected} != set(names):
        raise AssertionError("driver functions missing: " + repr(set(names) - {n.name for n in selected}))
    namespace = {"os": os, "STATE": {"done": False, "reason": "", "shots": 0,
                                             "autonomous_started_at": None, "autonomous_selected": None,
                                             "autonomous_polls": 0},
                 "HANDLE": "tick-handle", "events": [],
                 "log": lambda message: namespace["events"].append(str(message))}

    class EditorSubsystem:
        def editor_request_end_play(self):
            namespace["events"].append("END_PIE")

    class FakeUnreal:
        class LevelEditorSubsystem:
            pass

        @staticmethod
        def unregister_slate_post_tick_callback(handle):
            namespace["events"].append("UNREGISTER " + str(handle))

        @staticmethod
        def get_editor_subsystem(_):
            return EditorSubsystem()

    namespace["unreal"] = FakeUnreal
    module = ast.Module(body=selected, type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), str(DRIVER_PATH), "exec"), namespace)
    return namespace


class AutonomousDriverContract(unittest.TestCase):
    def test_time_cap_default_fallback_and_clamps(self):
        ns = load_functions("autonomous_time_cap")
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(ns["autonomous_time_cap"](), 45)
        for invalid in ("bad", "", "1.5"):
            with patch.dict(os.environ, {"SEVAROG_LIVE_AUTONOMOUS_SECONDS": invalid}):
                self.assertEqual(ns["autonomous_time_cap"](), 45)
        for requested, expected in (("-3", 5), ("5", 5), ("45", 45), ("90", 90), ("120", 90)):
            with self.subTest(requested=requested), patch.dict(os.environ, {"SEVAROG_LIVE_AUTONOMOUS_SECONDS": requested}):
                self.assertEqual(ns["autonomous_time_cap"](), expected)

    def test_missing_selector_result_is_explicit_and_finishes(self):
        ns = load_functions("autonomous_time_cap", "tick_autonomous_selector", "finish")

        class Boss:
            def start_selected_card_for_test(self):
                return "None"

            def get_outcome_for_test(self):
                return "Failed"

        ns["tick_autonomous_selector"](None, Boss(), 10.0)
        self.assertTrue(ns["STATE"]["done"])
        self.assertTrue(any("AUTONOMOUS_RESULT" in item and "refusal=NoSelectionOrStart" in item
                            for item in ns["events"]))
        self.assertIn("UNREGISTER tick-handle", ns["events"])
        self.assertIn("END_PIE", ns["events"])
        self.assertIsNone(ns["HANDLE"])

    def test_navigation_identity_mismatch_and_missing_identity_fail_closed(self):
        validate = load_functions("validate_navigation_identity")["validate_navigation_identity"]
        self.assertEqual(validate("status=TEST_WALK_SKIPPED route=F5 fixture generation=1", "F5 fixture", 1),
                         ("F5 fixture", 1))
        for summary, route, generation in (
                ("route=F5 fixture generation=1 code=Success", "Other route", 1),
                ("route=F5 fixture generation=2 code=Success", "F5 fixture", 1),
                ("PENDING", "F5 fixture", 1),
                ("route=F5 fixture generation=bad", "F5 fixture", 1)):
            with self.subTest(summary=summary), self.assertRaises(RuntimeError):
                validate(summary, route, generation)

    def test_terminal_and_time_cap_each_finish_once(self):
        for outcome, now, expected in (("Succeeded", 12.0, "terminal outcome: Succeeded"),
                                       ("Active", 55.0, "time cap reached")):
            with self.subTest(outcome=outcome):
                ns = load_functions("autonomous_time_cap", "tick_autonomous_selector", "finish")
                with patch.dict(os.environ, {"SEVAROG_LIVE_AUTONOMOUS_SECONDS": "5"}):
                    class Boss:
                        def start_selected_card_for_test(self):
                            return "Move_TestCard"

                        def get_outcome_for_test(self):
                            return outcome

                    ns["tick_autonomous_selector"](None, Boss(), 10.0)
                    ns["tick_autonomous_selector"](None, Boss(), now)
                self.assertTrue(ns["STATE"]["done"])
                self.assertIn(expected, ns["STATE"]["reason"])
                ns["finish"]("duplicate completion")
                self.assertEqual(ns["events"].count("END_PIE"), 1)
                self.assertEqual(sum(item.startswith("UNREGISTER ") for item in ns["events"]), 1)

    def test_navigation_summary_and_completion_are_identity_bounded(self):
        getter = CHARACTER_TEXT[CHARACTER_TEXT.index("FString ARPGFrameworkBossCharacter::GetNavigationResultForTest()"):
                               CHARACTER_TEXT.index("\n}", CHARACTER_TEXT.index("FString ARPGFrameworkBossCharacter::GetNavigationResultForTest()")) + 2]
        completion = CONTROLLER_TEXT[CONTROLLER_TEXT.index("void ARPGFrameworkBossController::OnMoveCompleted"):
                                     CONTROLLER_TEXT.index("void ARPGFrameworkBossController::OnUnPossess")]
        for field in ("route=", "generation=", "request=", "code=", "flags=", "remainingCm="):
            self.assertIn(field, NAV_RULES_TEXT)
        self.assertIn("OwnedRequest==FAIRequestID::InvalidRequest||RequestID!=OwnedRequest", completion)
        self.assertLess(completion.index("OwnedRequest=FAIRequestID::InvalidRequest"), completion.index("WalkArrived()"))
        self.assertIn("controller_pawn_match", DRIVER_TEXT)
        self.assertIn("SPAWN PASS actor=%s", DRIVER_TEXT)
        self.assertIn("validate_navigation_identity(summary", DRIVER_TEXT)
        self.assertIn('controller_match = "UNEXPOSED" if controller else "NO_CONTROLLER"', DRIVER_TEXT)
        self.assertIn('controller_match == "0"', DRIVER_TEXT)
        self.assertIn('controller_match = "GETTER_FAILED"', DRIVER_TEXT)
        self.assertIn("Route=Dependencies&&Dependencies->Profile.IsValid()?Dependencies->Profile->FixtureLabel", getter)
        self.assertIn("GenerationId", getter)
        # The summary is route/generation/request-bound; actor identity is a separate driver log join.
        self.assertNotIn("actor=", getter)

    def test_driver_fail_closed_status_and_cleanup_paths_are_present(self):
        for token in ("PIE world did not start", "player pawn missing", "NoSelectionOrStart",
                      "bounded time cap", "except Exception as error", "finish(\"failed:"):
            self.assertIn(token, DRIVER_TEXT)
        self.assertIn("if STATE[\"done\"]:", DRIVER_TEXT)
        self.assertIn("editor_request_end_play()", DRIVER_TEXT)
        self.assertIn("unregister_slate_post_tick_callback(HANDLE)", DRIVER_TEXT)
        self.assertIn("OwnedRequest=FAIRequestID::InvalidRequest; StopMovement();BossOwner.Reset();", CONTROLLER_TEXT)


if __name__ == "__main__":
    unittest.main(verbosity=2)
