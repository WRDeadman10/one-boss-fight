"""Offline game-time and opt-in checks for the shared-helper full-fight port."""

import importlib.util
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch


DRIVER = Path(__file__).with_name("pie_full_fight.py")
RETAINED = Path(__file__).parents[2] / "Docs/BossCombatReview/Execution/Claude/P_FIGHTVIDEO/pie_full_fight.py"


class FightPortTests(unittest.TestCase):
    def setUp(self):
        self.commands = []
        self.logs = []
        self.game_seconds = 1.0
        editor = types.SimpleNamespace(editor_request_begin_play=lambda: None, editor_request_end_play=lambda: None)
        self.ue = types.SimpleNamespace(
            Paths=types.SimpleNamespace(project_dir=lambda: str(DRIVER.parents[2])),
            GameplayStatics=types.SimpleNamespace(get_time_seconds=lambda world: self.game_seconds),
            SystemLibrary=types.SimpleNamespace(execute_console_command=lambda world, command: self.commands.append(command)),
            LevelEditorSubsystem=type("LevelEditorSubsystem", (), {}),
            get_editor_subsystem=lambda subsystem: editor,
            register_slate_post_tick_callback=lambda callback: object(),
            log=self.logs.append,
        )
        spec = importlib.util.spec_from_file_location("pie_full_fight_under_test", DRIVER)
        self.driver = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"unreal": self.ue}):
            spec.loader.exec_module(self.driver)
        self.unreal_patch = patch.dict(sys.modules, {"unreal": self.ue})
        self.unreal_patch.start()

    def tearDown(self):
        self.unreal_patch.stop()

    def test_action_schedule_and_frame_rate_match_retained(self):
        retained = RETAINED.read_text(encoding="utf-8")
        self.assertIn('FRAME_FPS = 15.0', retained)
        self.assertEqual(self.driver.FRAME_FPS, 15.0)
        self.assertEqual(self.driver.CYCLE, ["light", "light", "strong", "backstep", "air_light", "guard", "light", "air_heavy", "backstep", "guard", "strong"])

    def test_capture_uses_game_time_and_waits_for_png(self):
        with tempfile.TemporaryDirectory() as root:
            self.driver.FRAMES = root
            self.driver.capture(object())
            self.assertIn("FRAME 0 g=1.000", self.logs[-1])
            self.game_seconds = 1.08
            self.driver.capture(object())  # pending PNG has not appeared yet
            self.assertEqual(self.driver.S["frame"], 1)
            Path(self.driver.S["pending"]).write_bytes(b"png")
            self.driver.capture(object())
            self.assertEqual(self.driver.S["frame"], 2)

    def test_tier2_defaults_off_and_opt_in_before_pie(self):
        for value, expected in ((None, "rpg.Art.Tier2 0"), ("1", "rpg.Art.Tier2 1")):
            self.commands.clear()
            self.driver.S.update(phase="start", elapsed=0.0)
            env = {} if value is None else {"ER_FIGHT_TIER2": value}
            with patch.dict(os.environ, env, clear=True):
                self.driver._tick(0.6)
            self.assertIn(expected, self.commands)

    def test_refill_threshold_and_markers_retained(self):
        source = DRIVER.read_text(encoding="utf-8")
        for marker in ("hp < 35.0", 'log("FRAME ', 'log("ACTION ', 'log("COUNTER ', 'log("BOSS_DEAD ', 'log("finished: '):
            self.assertIn(marker, source)
        self.assertIn("plc.refill_player(boss)", source)
        self.assertIn("slomo 0.5", source)

    def test_player_death_or_sustained_missing_pawn_aborts_capture(self):
        self.assertEqual(self.driver.player_failure(object(), 0.0, 10.0), "player dead")
        self.assertIsNone(self.driver.player_failure(None, None, 10.0))
        self.assertIsNone(self.driver.player_failure(None, None, 12.0))
        self.assertEqual(self.driver.player_failure(None, None, 13.1), "player missing for 3 s")
        self.assertIsNone(self.driver.player_failure(object(), 60.0, 14.0))

    def test_video_tool_accepts_every_fixture_marker(self):
        tool = DRIVER.parents[1] / "Tools" / "make_fight_video.py"
        fixture = tool.parent / "fixtures" / "full_fight_sample.log"
        spec = importlib.util.spec_from_file_location("fight_video_tool_under_test", tool)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        frames, events = module.parse_log(fixture.read_text(encoding="utf-8"))
        self.assertEqual(len(frames), 3)
        self.assertEqual([name for _, name in events], ["Light attack", "Guard counter", "Boss defeated"])

    def test_guard_polls_one_second_after_block_injection_stops(self):
        pawn, boss, pc = object(), object(), object()
        self.driver.S.update(phase="fight", action="guard", action_t=2.55,
                             guard_armed_at=None, g_last=1.0, fight_time=10.0,
                             beat=0.0, counts={"guard": 1})
        self.game_seconds = 1.1
        self.ue.RPGInputTestUtils = types.SimpleNamespace(inject_action=lambda *args: self.fail("block injected after 2.5 s"))
        self.ue.load_asset = lambda path: object()
        self.ue.Vector = lambda *args: args
        keys = []
        dodge = types.SimpleNamespace(is_guard_counter_armed=lambda: True)
        with patch.object(self.driver, "actors", return_value=(object(), pc, pawn, boss)), \
             patch.object(self.driver, "capture"), \
             patch.object(self.driver, "attr", return_value=100.0), \
             patch.object(self.driver, "face", return_value=100.0), \
             patch.object(self.driver, "comp", return_value=dodge), \
             patch.object(self.driver, "key", side_effect=lambda *args: keys.append(args)):
            self.driver._tick(0.1)
        self.assertEqual(self.driver.S["counts"]["counter"], 1)
        self.assertIn((pc, self.driver.R2, True), keys)

        self.driver.S.update(action="guard", action_t=3.45, guard_armed_at=None, g_last=1.1)
        dodge.is_guard_counter_armed = lambda: False
        self.game_seconds = 1.2
        with patch.object(self.driver, "actors", return_value=(object(), pc, pawn, boss)), \
             patch.object(self.driver, "capture"), \
             patch.object(self.driver, "attr", return_value=100.0), \
             patch.object(self.driver, "face", return_value=100.0), \
             patch.object(self.driver, "comp", return_value=dodge):
            self.driver._tick(0.1)
        self.assertIsNone(self.driver.S["action"])


if __name__ == "__main__":
    unittest.main()
