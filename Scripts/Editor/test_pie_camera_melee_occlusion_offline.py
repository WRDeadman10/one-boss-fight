"""Offline geometry and marker contract for the Lead-only melee camera probe."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).with_name("pie_camera_melee_occlusion.py")


class Point:
    def __init__(self, x, y, z=0.0):
        self.x, self.y, self.z = x, y, z

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scale):
        return Point(self.x * scale, self.y * scale, self.z * scale)

    def length(self):
        return (self.x * self.x + self.y * self.y + self.z * self.z) ** 0.5


class MeleeCameraProbeTests(unittest.TestCase):
    def setUp(self):
        self.logs = []
        ue = types.SimpleNamespace(
            Paths=types.SimpleNamespace(project_dir=lambda: str(SCRIPT.parents[2])),
            register_slate_post_tick_callback=lambda callback: object(),
            unregister_slate_post_tick_callback=lambda handle: None,
            log=self.logs.append,
            SpringArmComponent=type("SpringArmComponent", (), {}),
            CameraComponent=type("CameraComponent", (), {}),
            CapsuleComponent=type("CapsuleComponent", (), {}),
        )
        spec = importlib.util.spec_from_file_location("melee_camera_under_test", SCRIPT)
        self.module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"unreal": ue}):
            spec.loader.exec_module(self.module)

    def test_horizontal_distance_ignores_height(self):
        self.assertEqual(self.module.horizontal_distance(Point(0, 0, -97), Point(3, 4, 200)), 5.0)

    def test_melee_placement_faces_boss(self):
        boss = types.SimpleNamespace(get_actor_location=lambda: Point(100, 200, 10),
                                     get_actor_rotation=lambda: types.SimpleNamespace(yaw=0.0))
        placements = []
        with patch.object(self.module.plc, "place_player", side_effect=lambda *args: placements.append(args)):
            self.module.place(object(), object(), boss, 105.0)
        self.assertEqual(placements[0][2], (205.0, 200.0, 30.0))
        self.assertAlmostEqual(abs(placements[0][3]), 180.0)

    def test_snapshot_uses_world_locations_on_named_camera_and_boom(self):
        def component(name, location):
            return types.SimpleNamespace(
                get_name=lambda: name,
                get_world_location=lambda: location,
                get_editor_property=lambda key: {"target_arm_length": 300.0, "probe_size": 34.0,
                                                 "probe_channel": "Camera"}[key],
            )
        other_arm = component("OtherArm", Point(1, 1, 1))
        boom = component("CameraBoom", Point(2, 2, 2))
        other_camera = component("OtherCamera", Point(9, 9, 9))
        follow = component("FollowCamera", Point(5, 6, 2))
        pawn = types.SimpleNamespace(
            get_components_by_class=lambda cls: [other_arm, boom] if cls.__name__ == "SpringArmComponent"
                else [other_camera, follow] if cls.__name__ == "CameraComponent" else [],
            get_actor_location=lambda: Point(0, 0, 0),
        )
        boss = types.SimpleNamespace(get_components_by_class=lambda cls: [],
                                     get_actor_location=lambda: Point(105, 0, 0))
        manager = types.SimpleNamespace(get_camera_location=lambda: Point(5, 6, 2),
                                        get_camera_rotation=lambda: "rotation")
        pc = types.SimpleNamespace(player_camera_manager=manager,
                                   get_control_rotation=lambda: types.SimpleNamespace(yaw=0.0))
        endpoints = []
        self.module.unreal.Vector = Point
        self.module.unreal.TraceTypeQuery = types.SimpleNamespace(TRACE_TYPE_QUERY2=2)
        self.module.unreal.DrawDebugTrace = types.SimpleNamespace(NONE=0)
        self.module.unreal.SystemLibrary = types.SimpleNamespace(
            sphere_trace_single=lambda world, start, end, *args: endpoints.append(end) or "no_hit")
        self.module.snapshot(object(), pc, pawn, boss, 105.0)
        self.assertTrue(any("pivot=" in line and "camera=" in line and "actual_cm=105.0" in line
                            for line in self.logs))
        self.assertEqual((endpoints[0].x, endpoints[0].y, endpoints[0].z), (-298.0, 2.0, 2.0))

    def test_end_marker_is_explicit(self):
        with patch.object(self.module.plc, "end_play"):
            self.module.finish("three distances sampled")
        self.assertIn("[MeleeCamera] finished: three distances sampled", self.logs)


if __name__ == "__main__":
    unittest.main()
