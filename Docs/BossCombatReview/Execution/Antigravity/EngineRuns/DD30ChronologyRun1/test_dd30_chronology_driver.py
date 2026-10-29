# Copyright One Boss Fight. All Rights Reserved.
"""Offline unit test for DD30 Chronology PIE Driver."""

import unittest
from unittest.mock import MagicMock, patch
import sys
import types

class TestDD30ChronologyDriver(unittest.TestCase):
    def setUp(self):
        # Create a mock unreal module
        self.mock_unreal = types.ModuleType("unreal")
        self.mock_unreal.log = MagicMock()
        self.mock_unreal.log_error = MagicMock()
        self.mock_unreal.log_warning = MagicMock()

        self.mock_system_lib = MagicMock()
        self.mock_unreal.SystemLibrary = self.mock_system_lib

        self.mock_level_editor_subsystem = MagicMock()
        self.mock_unreal_editor_subsystem = MagicMock()

        self.mock_unreal.LevelEditorSubsystem = MagicMock()
        self.mock_unreal.UnrealEditorSubsystem = MagicMock()

        def get_editor_subsystem(subsystem_cls):
            if subsystem_cls == self.mock_unreal.LevelEditorSubsystem:
                return self.mock_level_editor_subsystem
            if subsystem_cls == self.mock_unreal.UnrealEditorSubsystem:
                return self.mock_unreal_editor_subsystem
            return MagicMock()

        self.mock_unreal.get_editor_subsystem = get_editor_subsystem

        self.registered_callbacks = []
        def register_slate_post_tick_callback(cb):
            self.registered_callbacks.append(cb)
            return len(self.registered_callbacks)

        def unregister_slate_post_tick_callback(handle):
            pass

        self.mock_unreal.register_slate_post_tick_callback = register_slate_post_tick_callback
        self.mock_unreal.unregister_slate_post_tick_callback = unregister_slate_post_tick_callback

        # Mock editor world
        self.mock_editor_world = MagicMock()
        self.mock_editor_world.get_path_name.return_value = "/Game/OneBossFight/Levels/L_SevarogArena.L_SevarogArena"
        self.mock_unreal_editor_subsystem.get_editor_world.return_value = self.mock_editor_world
        self.mock_unreal_editor_subsystem.get_game_world.return_value = None

        # Insert mock unreal into sys.modules
        sys.modules["unreal"] = self.mock_unreal

    def tearDown(self):
        if "unreal" in sys.modules:
            del sys.modules["unreal"]

    def test_driver_lifecycle(self):
        # Import or execute driver
        driver_scope = {}
        with open("Docs/BossCombatReview/Execution/Antigravity/EngineRuns/DD30ChronologyRun1/dd30_chronology_pie.py", "r", encoding="utf-8") as f:
            code = f.read()

        exec(code, driver_scope)

        # 1. Main tick callback registered
        self.assertTrue(len(self.registered_callbacks) >= 1)
        tick_fn = driver_scope["tick"]
        quit_tick_fn = driver_scope["quit_tick"]

        # 2. Tick 1: Requests fresh PIE
        tick_fn(0.1)
        self.assertTrue(driver_scope["s"]["requested"])
        self.mock_level_editor_subsystem.editor_request_begin_play.assert_called_once()

        # 3. Game world appears
        mock_game_world = MagicMock()
        mock_game_world.get_path_name.return_value = "/Game/OneBossFight/Levels/UEDPIE_0_L_SevarogArena.L_SevarogArena"
        self.mock_unreal_editor_subsystem.get_game_world.return_value = mock_game_world

        # Tick 2: Observes game world
        tick_fn(0.1)
        self.assertTrue(driver_scope["s"]["started"])

        # 4. Advance time past 10 seconds -> calls finish()
        tick_fn(10.0)
        self.mock_level_editor_subsystem.editor_request_end_play.assert_called_once()

        # 5. Advance quit ticks -> calls QUIT_EDITOR
        for _ in range(60):
            quit_tick_fn(0.016)

        self.assertTrue(driver_scope["s"]["quit_requested"])
        self.mock_system_lib.execute_console_command.assert_called_with(None, "QUIT_EDITOR")
        print("PASS: test_driver_lifecycle verified all states and QUIT_EDITOR execution.")

    def test_wrong_map_fails(self):
        driver_scope = {}
        self.mock_editor_world.get_path_name.return_value = "/Game/SomeOtherMap"
        with open("Docs/BossCombatReview/Execution/Antigravity/EngineRuns/DD30ChronologyRun1/dd30_chronology_pie.py", "r", encoding="utf-8") as f:
            code = f.read()

        exec(code, driver_scope)
        tick_fn = driver_scope["tick"]
        tick_fn(0.1)

        # Should NOT request begin play
        self.assertFalse(driver_scope["s"]["requested"])
        self.mock_level_editor_subsystem.editor_request_begin_play.assert_not_called()
        print("PASS: test_wrong_map_fails verified fail-closed on wrong map.")

if __name__ == "__main__":
    unittest.main()
