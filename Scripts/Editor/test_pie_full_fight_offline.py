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

    def test_parry_control_distance_actions_keep_a_no_input_comparison_band(self):
        action = self.driver.parry_control_distance_action
        self.assertEqual(action(140.0), "clamp")
        self.assertEqual(action(130.0), "retreat")
        self.assertEqual(action(120.0), "hold")
        self.assertEqual(action(110.0), "approach")
        self.assertEqual(action(None), "unknown")

    def test_parry_control_is_opt_in_exclusive_and_does_not_press_or_attack(self):
        source = DRIVER.read_text(encoding="utf-8")
        self.assertIn('PARRY_ONLY_CONTROL = os.environ.get("PARRY_ONLY_CONTROL", "0") == "1"', source)
        self.assertIn('if PARRY_ONLY_CONTROL:', source)
        control_branch = source.split('if PARRY_ONLY_CONTROL:', 1)[1].split('if FIGHT_DODGE_ONLY:', 1)[0]
        parry_branch = source.split('if FIGHT_PARRY_ONLY:', 1)[-1].split('if FIGHT_DODGE_ONLY:', 1)[0]
        shared_step = source.split('def parry_control_distance_step(', 1)[1].split('\ndef ', 1)[0]
        self.assertIn('parry_control_distance_step(pawn, boss, pc, dist, "control")', control_branch)
        self.assertIn('parry_control_distance_step(pawn, boss, pc, dist, "parry")', parry_branch)
        self.assertIn('parry_control_distance_action(distance_cm)', shared_step)
        self.assertIn('press=%d attacks=0', shared_step)
        self.assertNotIn('key(pc,', control_branch + shared_step)
        self.assertNotIn('inject_action', control_branch + shared_step)
        self.assertIn('PARRY_CONTROL_HARD_MAX_DISTANCE_CM = 130.0', source)

    def test_any_active_tracker_move_is_a_parry_window_and_a4_sweep_is_fallback_only(self):
        state = self.driver.parry_window_state("A1b", True, 44, "GS_Attack04_Montage", False, 3)
        self.assertEqual(state, (True, 44, "tracker"))
        state = self.driver.parry_window_state("A3a", True, 46, "OtherMontage", False, 0)
        self.assertEqual(state, (True, 46, "tracker"))
        state = self.driver.parry_window_state("A1b", False, 44, "GS_Attack04_Montage", True, 3)
        self.assertEqual(state, (True, 3, "boss_montage_sweep"))
        self.assertEqual(self.driver.parry_window_state("A1b", False, 44,
                         "GS_Attack04_Montage", False, 3), (False, 44, "tracker"))
        self.assertEqual(self.driver.parry_window_state("A4", True, 45,
                         "OtherMontage", True, 4), (True, 45, "tracker"))

    def test_parry_diag_records_active_window_edges_even_without_montage_change(self):
        source = DRIVER.read_text(encoding="utf-8")
        self.assertIn('is_active != S.get("last_parry_diag_active")', source)
        self.assertIn('"last_parry_diag_active": None', source)

    def test_parry_press_targets_use_montage_origin_and_never_fall_back_to_window_fraction(self):
        self.assertEqual(self.driver.parry_press_target("A1b", "GS_Attack04_Montage"), (0.12, "tracker_move"))
        self.assertEqual(self.driver.parry_press_target("A3b", "AM_Boss01_A3b"), (0.10, "tracker_move"))
        self.assertEqual(self.driver.parry_press_target("A1", "AM_Boss01_A1"), (0.27, "tracker_move"))
        self.assertEqual(self.driver.parry_press_target("A3a", "AM_Boss01_A3a"), (0.42, "tracker_move"))
        self.assertEqual(self.driver.parry_press_target("A2", "GS_ChargedAttack"), (1.92, "tracker_move"))
        self.assertEqual(self.driver.parry_press_target("None", "Mid01_Anim_Montage"), (0.62, "montage_name"))
        self.assertEqual(self.driver.parry_press_target("None", "GS_SprintAttackFollowUp_Montage"), (None, "log_only"))
        self.assertEqual(self.driver.parry_press_target("UnknownMove", "OtherMontage"), (None, "no_timing_target"))

    def test_parry_timing_contract_is_independent_of_tracker_window_bounds(self):
        source = DRIVER.read_text(encoding="utf-8")
        self.assertIn('PARRY_MOVE_PRESS_POSITIONS = {"A1b": 0.12', source)
        self.assertIn('PARRY_MONTAGE_PRESS_POSITIONS = {"Mid01_Anim_Montage": 0.62}', source)
        self.assertIn('PARRY_LOG_ONLY_MONTAGES = {"GS_SprintAttackFollowUp_Montage"}', source)
        self.assertIn('current_montage_position >= schedule["target_position"]', source)
        self.assertNotIn('start_value + 0.60 * (end_value - start_value)', source)

    def test_dodge_contact_targets_use_c1132_montage_origin_positions_minus_015(self):
        expected = {
            ("A1b", "GS_Attack04_Montage", 1): (0.190, 0.040, "tracker_move"),
            ("A3b", "AM_Boss01_A3b", 1): (0.152, 0.002, "tracker_move"),
            ("A1", "AM_Boss01_A1", 1): (0.351, 0.201, "tracker_move"),
            ("A3a", "AM_Boss01_A3a", 1): (0.484, 0.334, "tracker_move"),
            ("A2", "GS_ChargedAttack", 1): (1.974, 1.824, "tracker_move"),
            ("None", "Mid01_Anim_Montage", 1): (0.70, 0.55, "montage_name"),
            ("None", "GS_SprintAttackFollowUp_Montage", 1): (0.070, 0.0, "montage_name_clamped"),
            ("None", "GS_SprintAttackFollowUp_Montage", 2): (0.456, 0.306, "montage_name"),
        }
        for args, target in expected.items():
            with self.subTest(args=args):
                actual = self.driver.dodge_contact_target(*args)
                self.assertEqual(actual[0], target[0])
                self.assertAlmostEqual(actual[1], target[1])
                self.assertEqual(actual[2], target[2])
        self.assertEqual(self.driver.dodge_contact_target("Unknown", "Other", 1), (None, None, "no_timing_target"))

    def test_dodge_tag_probe_reports_true_false_and_unknown_without_mutation(self):
        class Pawn:
            def __init__(self, value):
                self.value = value
                self.calls = []
            def call_method(self, name, args=()):
                self.calls.append((name, args))
                if name != "HasMatchingGameplayTag":
                    raise AssertionError("tag probe must be read-only")
                return self.value
        class Tag:
            def __init__(self):
                self.value = None
            def import_text(self, value):
                self.value = value
        with patch.object(self.driver.unreal, "GameplayTag", Tag, create=True):
            for value in (True, False):
                pawn = Pawn(value)
                self.assertIs(self.driver.invulnerability_tag_active(pawn), value)
                self.assertEqual([name for name, _ in pawn.calls], ["HasMatchingGameplayTag"])
                self.assertEqual(pawn.calls[0][1][0].value, '(TagName="Status.Invulnerable")')
            self.assertIsNone(self.driver.invulnerability_tag_active(None))
            self.assertIsNone(self.driver.invulnerability_tag_active(types.SimpleNamespace()))

    def test_dodge_watch_logs_i_frame_tag_rise_delay_after_press(self):
        class Tag:
            def import_text(self, _value):
                pass
        tag = {"active": True}
        pawn = types.SimpleNamespace(
            call_method=lambda name, args=(): tag["active"] if name == "HasMatchingGameplayTag" else None,
            add_movement_input=lambda *_args: None)
        tracker = types.SimpleNamespace(get_current_move=lambda: "None")
        pending = {"id": "run:dodge:0001", "montage": "Mid01_Anim_Montage",
                   "playback_key": ("Mid01_Anim_Montage", 1), "press_position": 0.55,
                   "contact_position": 0.70, "distance_cm": 180.0, "source": "montage_name",
                   "contact_observed": False, "contact_time": None,
                   "i_frame_tag_active_at_contact": None, "player_hit_followed": False,
                   "press_time": 4.0, "iframe_press_state": False,
                   "iframe_last_state": False, "iframe_rise_delay": None}
        self.driver.S.update(action="dodge_watch", action_t=0.0, action_id="run:dodge:0001",
                             held=set(), counts={}, fight_time=4.2, tick_dt=0.1,
                             dodge_watch_seen=set(), dodge_watch_scheduled={},
                             dodge_watch_pending=[pending], dodge_attempt_count=1,
                             parry_montage_last_position={"Mid01_Anim_Montage": 0.58},
                             parry_montage_occurrences={"Mid01_Anim_Montage": 1})
        with patch.object(self.driver.unreal, "GameplayTag", Tag, create=True), \
             patch.object(self.driver, "comp", return_value=tracker), \
             patch.object(self.driver.plc, "player_montage",
                          return_value=("Mid01_Anim_Montage", 0.60)):
            self.driver.dodge_watch_step(pawn, object(), object(), 180.0)
        rise = next(line for line in self.logs if "DODGE_IFRAME_TAG_RISE" in line)
        self.assertIn("delay_since_press=0.200", rise)

    def test_mid01_dodge_target_waits_for_only_mid01_and_sprint_montages(self):
        spec = importlib.util.spec_from_file_location("pie_full_fight_targeted_test", DRIVER)
        targeted = importlib.util.module_from_spec(spec)
        with patch.dict(os.environ, {"FIGHT_DODGE_ONLY": "1", "FIGHT_DODGE_TARGET": "Mid01"}), \
             patch.dict(sys.modules, {"unreal": self.ue}):
            spec.loader.exec_module(targeted)
        self.assertFalse(targeted.dodge_target_allowed("AM_Boss01_A1"))
        self.assertTrue(targeted.dodge_target_allowed("Mid01_Anim_Montage"))
        self.assertTrue(targeted.dodge_target_allowed("GS_SprintAttackFollowUp_Montage"))
        contact, press, source = targeted.dodge_target_for_montage("A1", "Mid01_Anim_Montage", 1)
        self.assertEqual((contact, source), (0.70, "montage_name"))
        self.assertAlmostEqual(press, 0.55)
        self.assertEqual(targeted.dodge_target_for_montage("A1", "AM_Boss01_A1", 1),
                         (None, None, "target_filtered"))

    def test_dodge_watch_presses_at_montage_target_samples_tag_and_links_following_hit(self):
        class Tag:
            def import_text(self, _value):
                pass
        state = {"position": 0.54, "pressed": [], "tag": True}
        tracker = types.SimpleNamespace(get_current_move=lambda: "None")
        pawn = types.SimpleNamespace(
            call_method=lambda name, args=(): state["tag"] if name == "HasMatchingGameplayTag" else None,
            add_movement_input=lambda *_args: None)
        boss = object()
        pc = object()
        with patch.object(self.driver.unreal, "GameplayTag", Tag, create=True), \
             patch.object(self.driver, "comp", side_effect=lambda actor, name: tracker if name == "RPGAttackTracker" else None), \
             patch.object(self.driver.plc, "player_montage",
                          side_effect=lambda _actor: ("Mid01_Anim_Montage", state["position"])), \
             patch.object(self.driver, "key", side_effect=lambda _pc, key, down:
                          state["pressed"].append((key, down)) or
                          (self.driver.S["held"].add(key) if down else self.driver.S["held"].discard(key))):
            self.driver.S.update(action=None, action_t=0.0, action_id=None, action_count=0,
                                 held=set(), counts={}, fight_time=1.0, tick_dt=0.1,
                                 dodge_watch_seen=set(), dodge_watch_scheduled={},
                                 dodge_watch_pending=[], dodge_attempt_count=0,
                                 parry_montage_last_position={}, parry_montage_occurrences={})
            self.driver.dodge_watch_step(pawn, boss, pc, 180.0)
            self.assertEqual(state["pressed"], [])
            state["position"] = 0.55
            self.driver.dodge_watch_step(pawn, boss, pc, 180.0)
            self.assertTrue(any(down for _key, down in state["pressed"]))
            state["position"] = 0.70
            self.driver.S["fight_time"] = 1.2
            self.driver.dodge_watch_step(pawn, boss, pc, 180.0)
            attempt = next(line for line in self.logs if "DODGE_ATTEMPT" in line)
            self.assertIn("i_frame_tag_active_at_contact=true", attempt)
            self.assertIn("target_contact_position=0.700", attempt)
            state["position"] = 0.73
            self.driver.S["fight_time"] = 1.3
            self.driver.dodge_watch_step(pawn, boss, pc, 180.0, player_hit_this_tick=True)
            self.assertTrue(any("DODGE_HIT_LINK" in line and "PLAYER_HIT_FOLLOWED" in line
                                for line in self.logs))
            state["position"] = 0.76
            self.driver.S["fight_time"] = 1.6
            self.driver.dodge_watch_step(pawn, boss, pc, 180.0)
        result = next(line for line in self.logs if "DODGE_RESULT" in line)
        self.assertIn("player_hit_followed=true", result)

    def test_dodge_only_mode_is_opt_in_and_uses_separate_watch_path(self):
        source = DRIVER.read_text(encoding="utf-8")
        self.assertIn('FIGHT_DODGE_ONLY = os.environ.get("FIGHT_DODGE_ONLY", "0") == "1"', source)
        self.assertIn('if FIGHT_DODGE_ONLY:', source)
        self.assertIn('dodge_watch_step(pawn, boss, pc, dist, player_hit_this_tick)', source)
        self.assertIn('DODGE_ATTEMPT', source)
        self.assertIn('i_frame_tag_active_at_contact=', source)
        self.assertIn('DODGE_IFRAME_TAG_RISE', source)
        self.assertIn('FIGHT_DODGE_TARGET = os.environ.get("FIGHT_DODGE_TARGET", "all").strip()', source)
        self.assertIn('player_hit_followed=', source)
        self.assertIn('DODGE_ONLY_PLAYER_DISTANCE_CM = 200.0', source)
        dodge_branch = source.split('if FIGHT_DODGE_ONLY:', 1)[-1].split('if S["action"] != "parry_watch":', 1)[0]
        self.assertIn('if dist > DODGE_ONLY_PLAYER_DISTANCE_CM:', dodge_branch)
        self.assertIn('DODGE_RANGE_CLAMP', dodge_branch)
        self.assertIn('DODGE_ONLY_PLAYER_DISTANCE_CM - 5.0', dodge_branch)

    def test_montage_target_attempts_without_a_tracker_window_and_uses_a_unique_synthetic_instance(self):
        state = {"presses": 0, "parried": 0}
        tracker = types.SimpleNamespace(get_current_move=lambda: "None", get_attack_instance=lambda: 0,
                                        is_active_window=lambda: False, get_position=lambda: 0.0)
        parry = types.SimpleNamespace(press=lambda: state.__setitem__("presses", state["presses"] + 1) or True,
                                      get_parried_count=lambda: state["parried"],
                                      get_press_count=lambda: state["presses"], window_seconds=0.2)
        boss = types.SimpleNamespace(get_actor_location=lambda: types.SimpleNamespace(x=250.0, y=0.0, z=0.0))
        pawn = types.SimpleNamespace(get_actor_location=lambda: types.SimpleNamespace(x=0.0, y=0.0, z=0.0))
        with patch.object(self.driver, "comp", side_effect=lambda actor, name: {
                "RPGAttackTracker": tracker, "RPGBossLowSweep": None,
                "RPGPlayerParry": parry}[name]), patch.object(self.driver.plc, "player_montage",
                return_value=("Mid01_Anim_Montage", 0.62)), patch.object(self.driver.plc, "health", return_value=100.0):
            self.driver.S.update(action="parry_watch", action_t=0.1, held=set(), fight_time=5.0, counts={},
                                 parry_watch_seen=set(), parry_watch_observed=set(), parry_watch_scheduled={},
                                 parry_watch_pending=None)
            self.driver.parry_watch_step(pawn, boss)
        self.assertEqual(state["presses"], 1)
        attempt = next(line for line in self.logs if "PARRY_ATTEMPT" in line)
        self.assertIn("move=UNTRACKED", attempt)
        self.assertIn("source=montage_target", attempt)
        self.assertIn("instance=1000000", attempt)
        self.assertIn("position=0.620", attempt)

    def test_sprint_followup_is_reported_as_untracked_without_pressing(self):
        state = {"presses": 0}
        tracker = types.SimpleNamespace(get_current_move=lambda: "None", get_attack_instance=lambda: 0,
                                        is_active_window=lambda: False, get_position=lambda: 0.0)
        parry = types.SimpleNamespace(press=lambda: state.__setitem__("presses", state["presses"] + 1) or True,
                                      get_parried_count=lambda: 0, get_press_count=lambda: state["presses"])
        with patch.object(self.driver, "comp", side_effect=lambda actor, name: {
                "RPGAttackTracker": tracker, "RPGBossLowSweep": None,
                "RPGPlayerParry": parry}[name]), patch.object(self.driver.plc, "player_montage",
                return_value=("GS_SprintAttackFollowUp_Montage", 0.07)):
            self.driver.S.update(action="parry_watch", action_t=0.1, held=set(), counts={},
                                 parry_watch_seen=set(), parry_watch_observed=set(), parry_watch_scheduled={},
                                 parry_watch_pending=None)
            self.driver.parry_watch_step(object(), object())
        self.assertEqual(state["presses"], 0)
        self.assertTrue(any("PARRY_UNTRACKED_BOSS_HITTER" in line and "action=log_only" in line
                            for line in self.logs))

    def test_tracker_exposes_active_window_bounds_to_blueprint_and_python(self):
        header = (DRIVER.parents[2] / "Source" / "OneBossFight" / "Player" /
                  "RPGAttackTracker.h").read_text(encoding="utf-8")
        self.assertIn("Attacks.FindByPredicate", header)
        for getter in ("GetActiveWindowStartTime", "GetActiveWindowEndTime"):
            self.assertIn('UFUNCTION(BlueprintPure, Category = "Attack|Diagnostics")', header)
            self.assertIn("float " + getter + "() const", header)

    def test_player_hit_marker_binds_hp_drop_to_boss_tracker_and_montage_position(self):
        tracker = types.SimpleNamespace(get_current_move=lambda: "A2", get_attack_instance=lambda: 14,
                                        get_position=lambda: 1.77)
        with patch.object(self.driver, "comp", return_value=tracker), \
             patch.object(self.driver, "montage", return_value="GS_ChargedAttack"), \
             patch.object(self.driver.plc, "player_montage", return_value=("GS_ChargedAttack", 1.77)):
            self.driver.S["fight_time"] = 12.5
            self.driver.log_player_hit(object(), object(), 100.0, 64.0)
        marker = next(line for line in self.logs if "PLAYER_HIT" in line)
        for field in ("hp_before=100.0", "hp_after=64.0", "damage=36.0", "boss_move=A2",
                      "boss_instance=14", "boss_montage=GS_ChargedAttack", "montage_position=1.77"):
            self.assertIn(field, marker)

    def test_parry_receipt_uses_blueprint_counter_accessors(self):
        source = DRIVER.read_text(encoding="utf-8")
        header = (DRIVER.parents[2] / "Source" / "OneBossFight" / "Player" /
                  "RPGPlayerParry.h").read_text(encoding="utf-8")
        self.assertIn("parry.get_parried_count()", source)
        self.assertIn("parry.get_press_count()", source)
        for getter in ("GetParriedCount", "GetPressCount"):
            marker = "int32 " + getter + "() const { return "
            self.assertIn("UFUNCTION(BlueprintPure, Category = \"Parry|Diagnostics\")\n\t" + marker, header)

    def test_parry_timeout_marker_is_once_per_slot(self):
        source = DRIVER.read_text(encoding="utf-8")
        self.assertIn('"parry_timeout_action_ids": set()', source)
        self.assertIn('outcome=timeout_no_live_tracker_window slot=%s', source)
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

    def test_parry_watch_is_bounded_and_does_not_press_without_live_tracker_window(self):
        self.assertEqual(self.driver.PARRY_WATCH_SECONDS, 3.0)
        tracker = types.SimpleNamespace(get_current_move=lambda: "A3", is_active_window=lambda: False,
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

    def test_parry_attempt_is_not_success_until_player_parried_count_increments(self):
        state = {"move": "A1b", "active": True, "instance": 9, "parried": 2, "presses": 0, "sweep": 0}
        tracker = types.SimpleNamespace(get_current_move=lambda: state["move"],
                                        is_active_window=lambda: state["active"],
                                        get_attack_instance=lambda: state["instance"], get_position=lambda: 0.80,
                                        get_active_window_start_time=lambda: 0.60,
                                        get_active_window_end_time=lambda: 0.90)
        sweep = types.SimpleNamespace(get_parried_count=lambda: state["sweep"])
        parry = types.SimpleNamespace(press=lambda: state.__setitem__("presses", state["presses"] + 1) or True,
                                      get_parried_count=lambda: state["parried"],
                                      get_press_count=lambda: state["presses"], window_seconds=0.25)
        pawn = types.SimpleNamespace(get_actor_location=lambda: types.SimpleNamespace(x=0.0, y=0.0, z=0.0))
        boss = types.SimpleNamespace(get_actor_location=lambda: types.SimpleNamespace(x=250.0, y=0.0, z=0.0))
        with patch.object(self.driver, "comp", side_effect=lambda actor, name: {
                "RPGAttackTracker": tracker, "RPGBossLowSweep": sweep,
                "RPGPlayerParry": parry}[name]), patch.object(self.driver.plc, "player_montage",
                return_value=("GS_Attack04_Montage", 0.12)):
            self.driver.S.update(action="parry_watch", action_t=0.2, counts={},
                                 parry_watch_seen=set(), parry_watch_pending=None)
            self.driver.parry_watch_step(pawn, boss)
            self.assertEqual(self.driver.S["counts"].get("parry_contact", 0), 0)
            self.assertIsNotNone(self.driver.S["parry_watch_pending"])
            state["parried"] += 1
            self.driver.parry_watch_step(pawn, boss)
        self.assertEqual(self.driver.S["counts"]["parry_contact"], 1)
        self.assertIsNone(self.driver.S["parry_watch_pending"])
        self.assertTrue(any("PARRY_CONTACT" in line for line in self.logs))
        self.assertTrue(any("PARRY_BLENDABLE at_press" in line for line in self.logs))
        self.assertTrue(any("PARRY_BLENDABLE at_contact" in line for line in self.logs))

    def test_opportunistic_parry_observes_during_action_and_attempts_when_neutral(self):
        state = {"move": "A1b", "active": True, "instance": 31, "parried": 4, "presses": 0,
                 "position": 0.75, "montage_position": 0.0}
        tracker = types.SimpleNamespace(get_current_move=lambda: state["move"],
                                        is_active_window=lambda: state["active"],
                                        get_attack_instance=lambda: state["instance"], get_position=lambda: state["position"],
                                        get_active_window_start_time=lambda: 0.60,
                                        get_active_window_end_time=lambda: 0.90)
        sweep = types.SimpleNamespace(get_parried_count=lambda: 0)
        parry = types.SimpleNamespace(press=lambda: state.__setitem__("presses", state["presses"] + 1) or True,
                                      get_parried_count=lambda: state["parried"],
                                      get_press_count=lambda: state["presses"], window_seconds=0.25)
        pawn = types.SimpleNamespace(get_actor_location=lambda: types.SimpleNamespace(x=0.0, y=0.0, z=0.0))
        boss = types.SimpleNamespace(get_actor_location=lambda: types.SimpleNamespace(x=250.0, y=0.0, z=0.0))
        with patch.object(self.driver, "comp", side_effect=lambda actor, name: {
                "RPGAttackTracker": tracker, "RPGBossLowSweep": sweep,
                "RPGPlayerParry": parry}[name]), patch.object(self.driver.plc, "player_montage",
                side_effect=lambda actor: ("GS_Attack04_Montage", state["montage_position"])), \
             patch.object(self.driver, "camera_blendables", return_value="camera=FollowCamera count=0"), \
             patch.object(self.driver.plc, "health", return_value=1000.0):
            self.driver.S.update(action="light", action_t=0.1, held=set(), fight_time=8.0, counts={},
                                 parry_watch_seen=set(), parry_watch_observed=set(), parry_watch_pending=None)
            self.driver.parry_watch_step(object(), object())
            self.assertEqual(state["presses"], 0)
            self.assertTrue(any("PARRY_TARGET_SCHEDULED instance=31" in line for line in self.logs))
            self.driver.S["action"] = None
            state["position"] = 0.12
            state["montage_position"] = 0.12
            self.driver.parry_watch_step(pawn, boss)
        self.assertEqual(state["presses"], 1)
        self.assertEqual(self.driver.S["parry_watch_pending"], {"instance": 31, "move": "A1b",
                         "source": "tracker", "parried_before": 4, "press_count_after": 1,
                         "sweep_parried_before": 0, "distance_cm": 250.0,
                         "player_hp_before": 1000.0, "attempt_time": 8.0,
                         "parry_window_seconds": 0.25, "tracker_window_seconds": 0.30000000000000004,
                         "watch_limit_seconds": 0.6, "boss_montage": "GS_Attack04_Montage"})
        attempt = next(line for line in self.logs if "PARRY_ATTEMPT" in line)
        self.assertIn("distance_cm=250.0", attempt)
        self.assertIn("player_hp_before=1000.0", attempt)
        self.assertIn("watch_limit_seconds=0.60", attempt)
        self.assertEqual(self.driver.S["action"], "parry_watch")

    def test_parry_only_mode_suppresses_normal_action_cycle(self):
        source = DRIVER.read_text(encoding="utf-8")
        self.assertIn('FIGHT_PARRY_ONLY = os.environ.get("FIGHT_PARRY_ONLY", "0") == "1"', source)
        self.assertIn('if FIGHT_PARRY_ONLY:', source)
        self.assertIn('S["action"] = None', source)

    def test_no_contact_reports_attempt_distance_hp_delta_and_observed_window_seconds(self):
        state = {"move": "A1", "active": True, "instance": 33, "parried": 0, "presses": 0, "hp": 1000.0,
                 "montage_position": 0.25}
        tracker = types.SimpleNamespace(get_current_move=lambda: state["move"],
                                        is_active_window=lambda: state["active"],
                                        get_attack_instance=lambda: state["instance"], get_position=lambda: state["position"],
                                        get_active_window_start_time=lambda: 0.40,
                                        get_active_window_end_time=lambda: 0.60)
        sweep = types.SimpleNamespace(get_parried_count=lambda: 0)
        parry = types.SimpleNamespace(press=lambda: state.__setitem__("presses", state["presses"] + 1) or True,
                                      get_parried_count=lambda: state["parried"],
                                      get_press_count=lambda: state["presses"], window_seconds=0.25)
        pawn = types.SimpleNamespace(get_actor_location=lambda: types.SimpleNamespace(x=0.0, y=0.0, z=0.0))
        boss = types.SimpleNamespace(get_actor_location=lambda: types.SimpleNamespace(x=200.0, y=0.0, z=0.0))
        with patch.object(self.driver, "comp", side_effect=lambda actor, name: {
                "RPGAttackTracker": tracker, "RPGBossLowSweep": sweep,
                "RPGPlayerParry": parry}[name]), patch.object(self.driver.plc, "health", side_effect=lambda actor: state["hp"]), \
             patch.object(self.driver.plc, "player_montage", side_effect=lambda actor: ("AM_Boss01_A1", state["montage_position"])):
            self.driver.S.update(action="parry_watch", action_t=0.2, fight_time=4.0, counts={},
                                 parry_watch_seen=set(), parry_watch_observed=set(), parry_watch_pending=None)
            self.driver.parry_watch_step(pawn, boss)
            self.assertIsNone(self.driver.S["parry_watch_pending"])
            state["montage_position"] = 0.28
            self.driver.S["fight_time"] = 4.1
            self.driver.parry_watch_step(pawn, boss)
            tracker.is_active_window = lambda: False
            state["hp"] = 930.0
            self.driver.S.update(action_t=0.61, fight_time=4.71)
            self.driver.parry_watch_step(pawn, boss)
        result = next(line for line in self.logs if "PARRY_RESULT" in line)
        self.assertIn("outcome=no_contact", result)
        self.assertIn("distance_cm=200.0", result)
        self.assertIn("player_hp_before=1000.0", result)
        self.assertIn("player_hp_after=930.0", result)
        self.assertIn("player_hp_delta=-70.0", result)
        self.assertIn("player_took_damage=true", result)
        self.assertIn("window_seconds=0.61", result)
        self.assertIn("parry_window_seconds=0.2", result)
        self.assertIn("tracker_window_seconds=0.200", result)

    def test_refused_parry_press_is_recorded_without_contact_credit(self):
        tracker = types.SimpleNamespace(get_current_move=lambda: "A1b", is_active_window=lambda: True,
                                        get_attack_instance=lambda: 10, get_position=lambda: 0.80,
                                        get_active_window_start_time=lambda: 0.60,
                                        get_active_window_end_time=lambda: 0.90)
        sweep = types.SimpleNamespace(get_parried_count=lambda: 0)
        press_state = {"count": 0}
        parry = types.SimpleNamespace(press=lambda: press_state.__setitem__("count", press_state["count"] + 1) or False,
                                      get_parried_count=lambda: 0,
                                      get_press_count=lambda: press_state["count"])
        with patch.object(self.driver, "comp", side_effect=lambda actor, name: {
                "RPGAttackTracker": tracker, "RPGBossLowSweep": sweep,
                "RPGPlayerParry": parry}[name]), patch.object(self.driver.plc, "player_montage",
                return_value=("GS_Attack04_Montage", 0.12)):
            self.driver.S.update(action="parry_watch", action_t=0.2, counts={},
                                 parry_watch_seen=set(), parry_watch_pending=None)
            self.driver.parry_watch_step(object(), object())
        self.assertEqual(self.driver.S["counts"].get("parry_contact", 0), 0)
        self.assertIsNone(self.driver.S["parry_watch_pending"])
        self.assertTrue(any("outcome=window_refused" in line for line in self.logs))

    def test_multiple_parry_count_increments_fail_closed_and_capture_frames_are_labeled(self):
        state = {"move": "A1b", "active": True, "instance": 12, "parried": 0}
        tracker = types.SimpleNamespace(get_current_move=lambda: state["move"],
                                        is_active_window=lambda: state["active"],
                                        get_attack_instance=lambda: state["instance"], get_position=lambda: 0.80,
                                        get_active_window_start_time=lambda: 0.60,
                                        get_active_window_end_time=lambda: 0.90)
        sweep = types.SimpleNamespace(get_parried_count=lambda: state["parried"])
        press_state = {"count": 0}
        parry = types.SimpleNamespace(press=lambda: press_state.__setitem__("count", press_state["count"] + 1) or True,
                                      get_parried_count=lambda: state["parried"],
                                      get_press_count=lambda: press_state["count"])
        with patch.object(self.driver, "comp", side_effect=lambda actor, name: {
                "RPGAttackTracker": tracker, "RPGBossLowSweep": sweep,
                "RPGPlayerParry": parry}[name]), patch.object(self.driver.plc, "player_montage",
                return_value=("GS_Attack04_Montage", 0.12)), \
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
        tracker = types.SimpleNamespace(get_current_move=lambda: "A3", is_active_window=lambda: False,
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
        self.assertTrue(any("timeout_no_live_tracker_window" in line for line in self.logs))
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
                                      "tier2": True, "tool_sha256": "a" * 64,
                                      "frame_context_schema": 1})
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
             patch.object(self.driver, "parry_watch_step"), \
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
             patch.object(self.driver, "parry_watch_step"), \
             patch.object(self.driver, "attr", return_value=100.0), \
             patch.object(self.driver, "face", return_value=100.0), \
             patch.object(self.driver, "comp", return_value=dodge):
            self.driver._tick(0.1)
        self.assertIsNone(self.driver.S["action"])


if __name__ == "__main__":
    unittest.main()
