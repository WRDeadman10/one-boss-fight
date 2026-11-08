"""Offline contracts for the maintained camera engagement PIE probe."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import math
import sys
import types
import unittest

ROOT = Path(__file__).resolve().parents[2]
PROBE = ROOT / "Scripts/Editor/pie_camera_engage.py"


class CameraEngageProbeContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = PROBE.read_text(encoding="utf-8")
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
        self.assertIn("attack_distance_min_cm=80", self.source)
        self.assertIn("attack_distance_max_cm=150", self.source)

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


if __name__ == "__main__":
    unittest.main()
