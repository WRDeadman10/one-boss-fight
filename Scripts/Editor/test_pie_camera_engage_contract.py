"""Offline contracts for the maintained camera engagement PIE probe."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import math
import ast
import sys
import types
import unittest

ROOT = Path(__file__).resolve().parents[2]
PROBE = ROOT / "Scripts/Editor/pie_camera_engage.py"
MATRIX = ROOT / "Documentation/Boss/AQ_C11_C15_BC_MATRIX.md"


class CameraEngageProbeContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = PROBE.read_text(encoding="utf-8")
        cls.matrix = MATRIX.read_text(encoding="utf-8")
        cls._old_unreal = sys.modules.get("unreal")
        fake = types.ModuleType("unreal")

        class FakePaths:
            @staticmethod
            def project_dir():
                return str(ROOT)

        fake.Paths = FakePaths
        fake.log = lambda _message: None
        fake.register_slate_post_tick_callback = lambda _callback: object()
        sys.modules["unreal"] = fake
        spec = spec_from_file_location("maintained_pie_camera_engage", PROBE)
        cls.probe = module_from_spec(spec)
        spec.loader.exec_module(cls.probe)

    @classmethod
    def tearDownClass(cls):
        if cls._old_unreal is None:
            sys.modules.pop("unreal", None)
        else:
            sys.modules["unreal"] = cls._old_unreal

    def test_probe_supports_existing_and_attack_camera_modes_and_speed_input(self):
        cfg = self.probe.read_configuration({"CAM_MODE": "fixed", "CAM_SPEED": "0.35"})
        self.assertEqual(cfg.mode, "fixed")
        self.assertEqual(cfg.cam_speed, 0.35)
        self.assertEqual(self.probe.read_configuration({"CAM_SPEED": "1.0"}).cam_speed, 1.0)
        for mode in ("orbit", "away", "retreat", "fixed", "attack"):
            self.assertEqual(self.probe.read_configuration({"CAM_MODE": mode}).mode, mode)

    def test_attack_mode_is_bounded_to_tracker_start_move_ids(self):
        cfg = self.probe.read_configuration({"CAM_MODE": "attack"})
        self.assertEqual(cfg.attack_moves, ("A4", "A6"))
        configured = self.probe.read_configuration({"CAM_ATTACK_MOVES": "A4,A6,Close"})
        self.assertEqual(configured.attack_moves, ("A4", "A6", "Close"))
        self.assertIn('tracker.start_move(move_id, True)', self.source)
        self.assertIn('hold_for_test(True)', self.source)
        self.assertIn("ATTACK_DISTANCE_MIN_CM = 80.0", self.source)
        self.assertIn("ATTACK_DISTANCE_MAX_CM = 150.0", self.source)
        self.assertIn('"ATTACK_START move=', self.source)
        self.assertIn("attack_band_samples=%d", self.source)

    def test_attack_band_summary_filters_out_of_band_distances(self):
        values = [79.9, 80.0, 115.0, 150.0, 150.1, 798.0, float("nan")]
        self.assertEqual(self.probe.attack_band_metrics(values), (3, 80.0, 150.0))
        count, lower, upper = self.probe.attack_band_metrics([151.0, 798.0])
        self.assertEqual(count, 0)
        self.assertTrue(math.isnan(lower))
        self.assertTrue(math.isnan(upper))
        self.assertIn('band_count, band_min, band_max = attack_band_metrics(S["attack_dist"])', self.source)

    def test_probe_supports_manual_look_injection_switch(self):
        cfg = self.probe.read_configuration({"CAM_LOOK_TEST": "1"})
        self.assertTrue(cfg.look_test)
        self.assertFalse(self.probe.read_configuration({}).look_test)

    def test_camera_cvars_are_whitelisted_binary_and_include_both_combined_switches(self):
        cfg = self.probe.read_configuration({
            "CAMERA_CVARS": "rpg.Camera.HideBossInside 1;rpg.Camera.LockOnFraming 1"
        })
        self.assertEqual(cfg.camera_cvars["rpg.Camera.HideBossInside"], 1)
        self.assertEqual(cfg.camera_cvars["rpg.Camera.LockOnFraming"], 1)
        self.assertEqual(cfg.camera_cvars["rpg.Camera.BossBlocks"], 0)
        self.assertIn("CAMERA_CVARS", self.source)
        self.assertIn('effective_cvars = ";".join', self.source)

    def test_invalid_mode_speed_and_cvar_fail_closed_before_editor_run(self):
        invalid = (
            {"CAM_MODE": "unknown"},
            {"CAM_ATTACK_MOVES": "A1"},
            {"CAM_ATTACK_MOVES": "A4,A4"},
            {"CAM_ATTACK_MOVES": ""},
            {"CAM_SPEED": "nan"},
            {"CAM_SPEED": "-0.1"},
            {"CAM_SPEED": "1.01"},
            {"CAMERA_CVARS": "rpg.Camera.HideBossInside 2"},
            {"CAMERA_CVARS": "quit"},
            {"CAMERA_CVARS": "rpg.Camera.LockOnFraming 1;rpg.Camera.LockOnFraming 0"},
        )
        for env in invalid:
            with self.subTest(env=env), self.assertRaises(ValueError):
                self.probe.read_configuration(env)

    def test_probe_is_passive_with_respect_to_asset_and_component_properties(self):
        self.assertNotIn("set_editor_property", self.source)
        self.assertNotIn("save_asset", self.source)
        self.assertNotIn("save_loaded_asset", self.source)
        self.assertIn("pie_lead_common as plc", self.source)
        self.assertTrue(math.isfinite(self.probe.read_configuration({}).cam_speed))

    def test_telemetry_helpers_do_not_mutate_world_assets_or_global_camera_state(self):
        tree = ast.parse(self.source)
        functions = {
            node.name: node for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        forbidden_calls = {
            "set_editor_property", "save_asset", "save_loaded_asset",
            "set_console_variable", "execute_console_command",
            "set_control_rotation", "add_movement_input", "start_move",
            "place_player", "reset_for_test", "wake", "hold_for_test",
            "inject_action", "set_visibility", "set_hidden_in_game",
        }
        for name in ("attack_band_metrics", "mesh_inside", "capsule_inside", "sample"):
            with self.subTest(function=name):
                calls = {
                    node.func.attr if isinstance(node.func, ast.Attribute)
                    else node.func.id if isinstance(node.func, ast.Name) else ""
                    for node in ast.walk(functions[name]) if isinstance(node, ast.Call)
                }
                self.assertFalse(calls & forbidden_calls, sorted(calls & forbidden_calls))
                for node in ast.walk(functions[name]):
                    if isinstance(node, ast.Attribute):
                        self.assertFalse(node.attr.startswith("set_editor_property"))
        self.assertIn("unreal.SystemLibrary.execute_console_command(None, cmd)", self.source)
        self.assertIn("def drive():", self.source)
        self.assertIn("def tick(dt):", self.source)

    def test_bc_matrix_covers_four_option_states_both_routes_and_attack_and_look_fields(self):
        for case in range(12):
            self.assertIn("| R%d |" % case, self.matrix)
        for token in (
            "all off", "HideBossInside=1", "LockOnFraming=1",
            "HideBossInside=1; LockOnFraming=1", "legacy", "data",
            "CAM_ATTACK_MOVES=A4,A6", "look injection", "median and p90",
            "hide duration distribution", "time to reacquire", "original matrix comprises 24 PIE runs",
        ):
            self.assertIn(token.lower(), self.matrix.lower())

    def test_bc_matrix_preserves_pending_and_no_generalization_boundary(self):
        self.assertIn("C-1090 has since supplied one B+C attack-mode PIE case", self.matrix)
        self.assertIn("R0–R8 remain pending", self.matrix)
        self.assertIn("R9–R11 at speed 0.35", self.matrix)
        self.assertIn("A tracker start alone does not prove a hit or a lunge", self.matrix)
        self.assertIn("Owner selection and package", self.matrix)


if __name__ == "__main__":
    unittest.main()
