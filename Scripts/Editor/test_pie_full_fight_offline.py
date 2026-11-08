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
            CameraComponent=object,
            PrimitiveComponent=object,
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

    def test_natural_a4_montage_and_live_sweep_are_tracker_independent_witness(self):
        state = self.driver.parry_window_state("A1b", False, 44, "GS_Attack04_Montage", True, 3)
        self.assertEqual(state, (True, 3, "boss_montage_sweep"))
        self.assertEqual(self.driver.parry_window_state("A1b", False, 44,
                         "GS_Attack04_Montage", False, 3), (False, 44, "tracker"))
        self.assertEqual(self.driver.parry_window_state("A4", True, 45,
                         "OtherMontage", True, 4), (True, 45, "tracker"))

    def test_parry_timeout_marker_is_once_per_slot(self):
        source = DRIVER.read_text(encoding="utf-8")
        self.assertIn('"parry_timeout_action_ids": set()', source)
        self.assertIn('outcome=timeout_no_live_a4 slot=%s', source)
        self.assertIn('PARRY_DIAG montage=%s', source)

    def test_action_schedule_and_frame_rate_match_retained(self):
        retained = RETAINED.read_text(encoding="utf-8")
        self.assertIn('FRAME_FPS = 15.0', retained)
        self.assertEqual(self.driver.FRAME_FPS, 15.0)
        self.assertEqual(self.driver.CYCLE, ["light", "light", "strong", "backstep", "air_light", "guard", "light", "air_heavy", "backstep", "guard", "strong", "parry_watch"])

    def test_frame_context_binds_projection_and_occlusion_limits_to_action_frame(self):
        vector = lambda x, y, z: types.SimpleNamespace(x=x, y=y, z=z)
        camera = types.SimpleNamespace(get_name=lambda: "FollowCamera", get_world_location=lambda: vector(0, 0, 0),
                                       get_world_rotation=lambda: types.SimpleNamespace(pitch=0, yaw=0),
                                       get_editor_property=lambda name: 90.0)
        pawn = types.SimpleNamespace(get_components_by_class=lambda _kind: [camera],
                                     get_actor_location=lambda: vector(100, 0, 0))
        boss = types.SimpleNamespace(get_components_by_class=lambda _kind: [],
                                     get_actor_location=lambda: vector(200, 0, 0))
        self.driver.S["action_id"] = "run:action:00003"
        with patch.object(self.driver.plc, "game_time", return_value=4.2):
            row = self.driver.frame_camera_context(object(), object(), pawn, boss, 9)
        self.assertEqual(row["frame_marker_id"], "fight:frame:00009")
        self.assertEqual(row["action_id"], "run:action:00003")
        self.assertTrue(row["player_in_camera_frame_estimate"])
        self.assertEqual(row["world_occlusion"], "UNMEASURED")
        self.assertEqual(row["camera_inside_boss_component_bounds"], "UNKNOWN")

    def test_projection_and_bounds_helpers_return_unknown_for_invalid_geometry(self):
        self.assertTrue(self.driver.point_in_camera_frame((0, 0, 0), (0, 0), 90, (100, 0, 0)))
        self.assertFalse(self.driver.point_in_camera_frame((0, 0, 0), (0, 0), 90, (-100, 0, 0)))
        self.assertIsNone(self.driver.point_in_camera_frame((0, 0, 0), (0, 0), float("nan"), (1, 0, 0)))
        self.assertTrue(self.driver.point_in_bounds((1, 1, 1), (0, 0, 0), (2, 2, 2)))
        self.assertFalse(self.driver.point_in_bounds((3, 0, 0), (0, 0, 0), (2, 2, 2)))
        self.assertIsNone(self.driver.point_in_bounds((float("nan"), 0, 0), (0, 0, 0), (2, 2, 2)))

    def test_air_light_context_is_time_and_frame_linked_without_distance_gate(self):
        source = DRIVER.read_text(encoding="utf-8")
        for marker in ('"AIR_LIGHT_CONTEXT "', '"player_boss_cm"', '"camera_position"',
                       '"pivot_position"', '"arm_target_cm"', '"frame_marker_id"'):
            self.assertIn(marker, source)
        self.assertNotIn("AIR_LIGHT_MIN_DISTANCE", source)
        self.assertNotIn("min_air_light_distance", source)

    def test_parry_watch_is_bounded_and_observes_only_a_live_a4_window(self):
        self.assertEqual(self.driver.PARRY_WATCH_SECONDS, 3.0)
        tracker = types.SimpleNamespace(get_current_move=lambda: "A3", is_active_window=lambda: True,
                                        get_attack_instance=lambda: 4, get_position=lambda: 0.72)
        sweep = types.SimpleNamespace(get_parried_count=lambda: 0)
        parry = types.SimpleNamespace(press=lambda: self.fail("parry pressed outside A4"))
        with patch.object(self.driver, "comp", side_effect=lambda actor, name: {
                "RPGAttackTracker": tracker, "RPGBossLowSweep": sweep,
                "RPGPlayerParry": parry}[name]):
            self.driver.S.update(action="parry_watch", action_t=0.1, counts={},
                                 parry_watch_seen=set(), parry_watch_pending=None)
            self.driver.parry_watch_step(object(), object())
        self.assertIsNone(self.driver.S["parry_watch_pending"])
        self.assertEqual(self.driver.S["parry_watch_seen"], set())

    def test_parry_attempt_is_not_success_until_live_sweep_count_increments(self):
        state = {"move": "A4", "active": True, "instance": 9, "parried": 2}
        tracker = types.SimpleNamespace(get_current_move=lambda: state["move"],
                                        is_active_window=lambda: state["active"],
                                        get_attack_instance=lambda: state["instance"], get_position=lambda: 0.72)
        sweep = types.SimpleNamespace(get_parried_count=lambda: state["parried"])
        parry = types.SimpleNamespace(press=lambda: True)
        with patch.object(self.driver, "comp", side_effect=lambda actor, name: {
                "RPGAttackTracker": tracker, "RPGBossLowSweep": sweep,
                "RPGPlayerParry": parry}[name]), patch.object(self.driver, "montage", return_value="A4"):
            self.driver.S.update(action="parry_watch", action_t=0.2, counts={},
                                 parry_watch_seen=set(), parry_watch_pending=None)
            self.driver.parry_watch_step(object(), object())
            self.assertEqual(self.driver.S["counts"].get("parry_contact", 0), 0)
            self.assertIsNotNone(self.driver.S["parry_watch_pending"])
            state["parried"] += 1
            self.driver.parry_watch_step(object(), object())
        self.assertEqual(self.driver.S["counts"]["parry_contact"], 1)
        self.assertIsNone(self.driver.S["parry_watch_pending"])
        self.assertTrue(any("PARRY_CONTACT" in line for line in self.logs))
        self.assertTrue(any("PARRY_BLENDABLE at_press" in line for line in self.logs))
        self.assertTrue(any("PARRY_BLENDABLE at_contact" in line for line in self.logs))

    def test_opportunistic_parry_observes_during_action_and_attempts_when_neutral(self):
        state = {"move": "A4", "active": True, "instance": 31, "parried": 4, "presses": 0}
        tracker = types.SimpleNamespace(get_current_move=lambda: state["move"],
                                        is_active_window=lambda: state["active"],
                                        get_attack_instance=lambda: state["instance"], get_position=lambda: 0.75)
        sweep = types.SimpleNamespace(get_parried_count=lambda: state["parried"])
        parry = types.SimpleNamespace(press=lambda: state.__setitem__("presses", state["presses"] + 1) or True)
        with patch.object(self.driver, "comp", side_effect=lambda actor, name: {
                "RPGAttackTracker": tracker, "RPGBossLowSweep": sweep,
                "RPGPlayerParry": parry}[name]), patch.object(self.driver, "camera_blendables", return_value="camera=FollowCamera count=0"):
            self.driver.S.update(action="light", action_t=0.1, held=set(), fight_time=8.0, counts={},
                                 parry_watch_seen=set(), parry_watch_observed=set(), parry_watch_pending=None)
            self.driver.parry_watch_step(object(), object())
            self.assertEqual(state["presses"], 0)
            self.assertTrue(any("PARRY_WINDOW_OBSERVED instance=31" in line for line in self.logs))
            self.driver.S["action"] = None
            self.driver.parry_watch_step(object(), object())
        self.assertEqual(state["presses"], 1)
        self.assertEqual(self.driver.S["parry_watch_pending"], {"instance": 31, "parried_before": 4})
        self.assertEqual(self.driver.S["action"], "parry_watch")

    def test_parry_only_mode_suppresses_normal_action_cycle(self):
        source = DRIVER.read_text(encoding="utf-8")
        self.assertIn('FIGHT_PARRY_ONLY = os.environ.get("FIGHT_PARRY_ONLY", "0") == "1"', source)
        self.assertIn('if FIGHT_PARRY_ONLY:', source)
        self.assertIn('S["action"] = None', source)

    def test_refused_parry_press_is_recorded_without_contact_credit(self):
        tracker = types.SimpleNamespace(get_current_move=lambda: "A4", is_active_window=lambda: True,
                                        get_attack_instance=lambda: 10, get_position=lambda: 0.72)
        sweep = types.SimpleNamespace(get_parried_count=lambda: 0)
        parry = types.SimpleNamespace(press=lambda: False)
        with patch.object(self.driver, "comp", side_effect=lambda actor, name: {
                "RPGAttackTracker": tracker, "RPGBossLowSweep": sweep,
                "RPGPlayerParry": parry}[name]):
            self.driver.S.update(action="parry_watch", action_t=0.2, counts={},
                                 parry_watch_seen=set(), parry_watch_pending=None)
            self.driver.parry_watch_step(object(), object())
        self.assertEqual(self.driver.S["counts"].get("parry_contact", 0), 0)
        self.assertIsNone(self.driver.S["parry_watch_pending"])
        self.assertTrue(any("outcome=window_refused" in line for line in self.logs))

    def test_multiple_parry_count_increments_fail_closed_and_capture_frames_are_labeled(self):
        state = {"move": "A4", "active": True, "instance": 12, "parried": 0}
        tracker = types.SimpleNamespace(get_current_move=lambda: state["move"],
                                        is_active_window=lambda: state["active"],
                                        get_attack_instance=lambda: state["instance"], get_position=lambda: 0.72)
        sweep = types.SimpleNamespace(get_parried_count=lambda: state["parried"])
        parry = types.SimpleNamespace(press=lambda: True)
        with patch.object(self.driver, "comp", side_effect=lambda actor, name: {
                "RPGAttackTracker": tracker, "RPGBossLowSweep": sweep,
                "RPGPlayerParry": parry}[name]), patch.object(self.driver, "montage", return_value="AM_Boss01_ParryRecoil"), \
             patch.object(self.driver, "camera_blendables", return_value="camera=FollowCamera count=1 weights=[PPM_ParryDistortion=1.000]"):
            self.driver.S.update(action="parry_watch", action_t=0.2, counts={}, fight_time=1.0,
                                 parry_watch_seen=set(), parry_watch_pending=None)
            self.driver.parry_watch_step(object(), object())
            state["parried"] = 2
            self.driver.parry_watch_step(object(), object())
        self.assertEqual(self.driver.S["counts"].get("parry_contact", 0), 0)
        self.assertTrue(any("unexpected_parried_delta" in line for line in self.logs))

        with tempfile.TemporaryDirectory() as root, patch.object(self.driver.plc, "game_time", return_value=10.0), \
             patch.object(self.driver, "camera_blendables", return_value="camera=FollowCamera count=1 weights=[]"):
            self.driver.FRAMES = root
            self.driver.S.update(frame=0, pending=None, pending_parry_frame=None, g_shot=-1.0,
                                 fight_time=1.2, action=None,
                                 parry_capture={"instance": 12, "contact_time": 1.0, "captured": set(), "pawn": object()})
            self.driver.capture(object())
            self.assertTrue(any("PARRY_FRAME_REQUEST label=plus_0p05 instance=12 frame=0" in line for line in self.logs))
            Path(self.driver.S["pending"]).write_bytes(b"png")
            self.game_seconds = 10.1
            self.driver.S["fight_time"] = 1.21
            self.driver.capture(object())
        self.assertTrue(any("PARRY_FRAME_READY label=plus_0p05 instance=12 frame=0" in line for line in self.logs))
        self.assertTrue(any("actual_offset=0.200" in line for line in self.logs))
        self.assertTrue(any("PARRY_BLENDABLE plus_0p05 camera=FollowCamera" in line for line in self.logs))

    def test_recoil_montage_is_a_separate_contact_followup_witness(self):
        self.driver.S.update(fight_time=4.25,
                             parry_capture={"instance": 17, "recoil_seen": False})
        with patch.object(self.driver, "montage", return_value="AM_Boss01_ParryRecoil"):
            self.driver.parry_feedback_step(object())
            self.driver.parry_feedback_step(object())
        markers = [line for line in self.logs if "PARRY_RECOIL" in line]
        self.assertEqual(len(markers), 1)
        self.assertIn("instance=17 t=4.250 montage=AM_Boss01_ParryRecoil", markers[0])

    def test_camera_blendable_readback_includes_weight_and_explicit_missing_camera(self):
        material = types.SimpleNamespace(get_name=lambda: "PPM_ParryDistortion")
        entry = types.SimpleNamespace(object=material, weight=1.0)
        camera = types.SimpleNamespace(get_name=lambda: "FollowCamera",
                                       post_process_settings=types.SimpleNamespace(
                                           weighted_blendables=types.SimpleNamespace(array=[entry])))
        pawn = types.SimpleNamespace(get_components_by_class=lambda _cls: [camera])
        self.assertIn("PPM_ParryDistortion=1.000", self.driver.camera_blendables(pawn))
        self.assertEqual(self.driver.camera_blendables(types.SimpleNamespace(
            get_components_by_class=lambda _cls: [])), "camera=missing")

    def test_parry_watch_times_out_without_a4_and_fails_closed_on_missing_components(self):
        tracker = types.SimpleNamespace(get_current_move=lambda: "A3", is_active_window=lambda: True,
                                        get_attack_instance=lambda: 11, get_position=lambda: 0.8)
        sweep = types.SimpleNamespace(get_parried_count=lambda: 0)
        parry = types.SimpleNamespace(press=lambda: self.fail("parry pressed without A4"))
        with patch.object(self.driver, "comp", side_effect=lambda actor, name: {
                "RPGAttackTracker": tracker, "RPGBossLowSweep": sweep,
                "RPGPlayerParry": parry}[name]):
            self.driver.S.update(action="parry_watch", action_t=self.driver.PARRY_WATCH_SECONDS,
                                 counts={}, parry_watch_seen=set(), parry_watch_pending=None)
            self.driver.parry_watch_step(object(), object())
            self.assertIsNone(self.driver.S["action"])
            self.assertTrue(any("timeout_no_live_a4" in line for line in self.logs))
            self.driver.S.update(action="parry_watch", action_t=0.1)
            with patch.object(self.driver, "comp", return_value=None):
                self.driver.parry_watch_step(object(), object())
        self.assertIsNone(self.driver.S["action"])
        self.assertTrue(any("outcome=missing_component" in line for line in self.logs))

    def test_capture_uses_game_time_and_waits_for_png(self):
        with tempfile.TemporaryDirectory() as root:
            self.driver.FRAMES = root
            self.driver.FIGHT_RUN = "smoke"
            self.driver.S.update(action="air_light", action_id="smoke:action:00001")
            self.driver.capture(object())
            frame_line = next(line for line in self.logs if "FRAME 0 g=1.000" in line)
            self.assertIn("marker=smoke:frame:00000", frame_line)
            self.assertIn("action=air_light action_id=smoke:action:00001", frame_line)
            context_line = next(line for line in self.logs if "FRAME_CONTEXT" in line)
            self.assertIn('"frame_marker_id": "smoke:frame:00000"', context_line)
            self.game_seconds = 1.08
            self.driver.capture(object())  # pending PNG has not appeared yet
            self.assertEqual(self.driver.S["frame"], 1)
            Path(self.driver.S["pending"]).write_bytes(b"png")
            self.driver.capture(object())
            self.assertEqual(self.driver.S["frame"], 2)

    def test_action_provenance_and_summary_separate_refills_deaths_and_boss_state(self):
        provenance = self.driver.run_provenance("run_7", "BUILD-259", "L_SevarogArena",
                                                "data", True, "a" * 64)
        self.assertEqual(provenance, {"run": "run_7", "build_id": "BUILD-259",
                                      "map": "L_SevarogArena", "route": "data",
                                      "tier2": True, "tool_sha256": "a" * 64})
        state = {"fight_time": 12.345, "boss_dead": False,
                 "counts": {"light": 2, "counter": 1}, "refills": 3,
                 "player_deaths": 1, "frame": 45, "boss_health_start": 2000,
                 "boss_health_max_start": 2500,
                 "boss_ai_controller_start": "AIC_Boss", "boss_driver_mutations": 0}
        summary = self.driver.receipt_summary(state, "player dead", 1522, "AIC_Boss")
        self.assertEqual(summary["player_refills"], 3)
        self.assertEqual(summary["player_deaths"], 1)
        self.assertEqual(summary["boss_health_start"], 2000)
        self.assertEqual(summary["boss_health_max_start"], 2500)
        self.assertEqual(summary["boss_health_end"], 1522)
        self.assertEqual(summary["boss_ai_controller_start"], "AIC_Boss")
        self.assertEqual(summary["boss_ai_controller_end"], "AIC_Boss")
        self.assertEqual(summary["boss_driver_mutations"], 0)

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
        self.driver.S.update(player_hp_ready=False, player_missing_at=None)
        self.assertEqual(self.driver.player_failure(object(), 0.0, 10.0), "player dead")
        self.assertIsNone(self.driver.player_failure(None, None, 10.0))
        self.assertIsNone(self.driver.player_failure(None, None, 12.0))
        self.assertEqual(self.driver.player_failure(None, None, 13.1), "player missing for 3 s")
        self.assertIsNone(self.driver.player_failure(object(), 60.0, 14.0))

    def test_zero_then_positive_health_is_initialization_not_death_and_ready_logs_once(self):
        pawn = object()
        self.driver.S.update(player_hp_ready=False, player_missing_at=None)
        self.assertIsNone(self.driver.player_failure(pawn, 0.0, 0.0))
        self.assertIsNone(self.driver.player_failure(pawn, 0.0, 1.9))
        self.assertIsNone(self.driver.player_failure(pawn, 100.0, 2.0))
        self.assertEqual(self.driver.player_failure(pawn, 0.0, 2.1), "player dead")
        ready = [line for line in self.logs if "PLAYER_HP_READY" in line]
        self.assertEqual(len(ready), 1)
        self.assertIn("hp=100.0", ready[0])

    def test_zero_health_times_out_after_five_fight_seconds_without_ready_sample(self):
        self.driver.S.update(player_hp_ready=False, player_missing_at=None)
        pawn = object()
        self.assertIsNone(self.driver.player_failure(pawn, 0.0, 4.99))
        self.assertEqual(self.driver.player_failure(pawn, 0.0, 5.0), "player dead")

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
