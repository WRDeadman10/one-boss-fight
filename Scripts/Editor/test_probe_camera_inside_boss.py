"""Offline contracts for the Lead dynamic camera probe."""
import importlib.util
import re
import sys
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EDITOR = ROOT / "Scripts" / "Editor"


class CameraProbeContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        unreal = sys.modules.setdefault("unreal", types.ModuleType("unreal"))
        unreal.register_slate_post_tick_callback = lambda _callback: None
        unreal.Paths = types.SimpleNamespace(project_dir=lambda: str(ROOT))
        sys.modules.setdefault("pie_lead_common", types.ModuleType("pie_lead_common"))
        spec = importlib.util.spec_from_file_location(
            "probe_camera_inside_boss", EDITOR / "probe_camera_inside_boss.py")
        cls.probe = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.probe)

    def test_aabb_inside_outside_and_finite_geometry(self):
        p = self.probe
        vec = lambda x, y, z: types.SimpleNamespace(x=x, y=y, z=z)
        center, extent = vec(0, 0, 0), vec(10, 20, 30)
        self.assertTrue(p.point_in_aabb(vec(10, -20, 30), center, extent))
        self.assertFalse(p.point_in_aabb(vec(10.1, 0, 0), center, extent))
        self.assertIsNone(p.point_in_aabb(vec(float("nan"), 0, 0), center, extent))
        self.assertFalse(p.finite_vector(vec(0, float("inf"), 0)))

    def test_observation_contract_keeps_camera_and_collision_evidence_separate(self):
        source = (EDITOR / "probe_camera_inside_boss.py").read_text(encoding="utf-8")
        for marker in ("arm_target_cm=", "arm_actual_cm=", "approximate_sweep_hit_component=",
                       "camera_inside_mesh_aabb=", "capsule_camera_response="):
            self.assertIn(marker, source)
        self.assertIn("get_collision_response_to_channel(unreal.CollisionChannel.ECC_CAMERA)", source)
        self.assertIn("150", (ROOT / "Documentation/Boss/CAMERA_MELEE_OCCLUSION_PROPOSAL.md").read_text(encoding="utf-8"))
        self.assertIn("or choose a camera fix", source)

    def test_route_contract_is_both_route_and_refuses_unexpected_selection(self):
        source = (EDITOR / "probe_camera_inside_boss.py").read_text(encoding="utf-8")
        self.assertIn('os.environ.get("H019_ENCOUNTER_DEFINITION", "").strip()', source)
        self.assertIn('ROUTE = "data" if DATA_ROUTE else "legacy"', source)
        self.assertIn('"rpg.EncounterDefinition " + DATA_ROUTE', source)
        self.assertIn("must be unset or the selected G044 encounter", source)
        self.assertIn('"SUMMARY route=%s finished=%s samples=%d"', source)
        self.assertIn('LOG = "[CameraInsideBoss] "', source)
        self.assertIn("circle_range_cm=150..250 passive=true", source)
        for forbidden in ("set_actor_location", "set_control_rotation", "set_editor_property", "set_collision_response"):
            self.assertNotIn(forbidden, source)

    def test_scenario_and_camera_options_are_read_only_telemetry(self):
        p = self.probe
        source = (EDITOR / "probe_camera_inside_boss.py").read_text(encoding="utf-8")
        values = {
            "rpg.Camera.BossBlocks": 0,
            "rpg.Camera.HideBossInside": 1,
            "rpg.Camera.LockOnFraming": 0,
        }
        seen = []
        sys.modules["unreal"].SystemLibrary = types.SimpleNamespace(
            get_console_variable_int_value=lambda name: seen.append(name) or values[name]
        )
        self.assertEqual(p.camera_option_values(), "boss_blocks=0 hide_boss_inside=1 lock_on_framing=0")
        self.assertEqual(seen, list(values))
        self.assertIn('os.environ.get("CAMERA_PROBE_SCENARIO", "unspecified")', source)
        self.assertIn("OPTIONS t=%.3f scenario=%s", source)
        for cvar in values:
            self.assertIn(cvar, source)
            self.assertNotRegex(source, rf'execute_console_command\([^\n]*{re.escape(cvar)}')


if __name__ == "__main__":
    unittest.main(verbosity=2)
