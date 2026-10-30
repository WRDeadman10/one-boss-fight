"""
test_probe_reach.py
Offline test suite for probe_reach.py (Order A-278).
Runs 100% offline with zero engine dependency.
Includes:
1. Analytical synthetic arc control verifying mathematical max forward, lateral, and vertical envelope.
2. Fake Unreal module reflection mock for AnimPose WORLD API.
3. Logging tag format assertions ([REACH_*]).
4. JSON summary export and edge case handling.
"""

import os
import sys
import math
import json
import tempfile
import unittest
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Ensure current directory is on sys.path
cur_dir = str(Path(__file__).resolve().parent)
if cur_dir not in sys.path:
    sys.path.insert(0, cur_dir)

from probe_reach import (
    analyze_reach_samples,
    resolve_world_space_enum,
    evaluate_pose_at_time,
    get_bone_translation,
    log_reach,
    probe_sequence,
    run_probe,
    DEFAULT_SEQUENCES,
    PROPOSED_ACTIVE_WINDOWS
)


class FakeVector:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z


class FakeTransform:
    def __init__(self, x: float, y: float, z: float):
        self.translation = FakeVector(x, y, z)


class FakeAnimPose:
    def __init__(self, bone_map: Dict[str, Tuple[float, float, float]]):
        self.bone_map = bone_map

    def get_bone_pose(self, bone_name: str, space: int) -> FakeTransform:
        if bone_name in self.bone_map:
            x, y, z = self.bone_map[bone_name]
            return FakeTransform(x, y, z)
        raise KeyError(f"Bone '{bone_name}' not in fake pose")


class FakeAnimSequence:
    def __init__(self, name: str, length: float, pose_generator=None):
        self.name = name
        self.sequence_length = length
        self.pose_generator = pose_generator

    def get_editor_property(self, prop: str) -> Any:
        if prop == "sequence_length":
            return self.sequence_length
        raise AttributeError(f"Unknown property {prop}")


class FakeAnimPoseSpaces:
    WORLD = 1


class FakeAnimPoseEvaluationOptions:
    def __init__(self):
        self.b_should_retarget = False
        self.b_incorporate_root_motion_into_pose = False


class FakeAnimPoseExtensions:
    @staticmethod
    def get_anim_pose_at_time(seq: FakeAnimSequence, time: float, opts=None) -> FakeAnimPose:
        if seq.pose_generator:
            return seq.pose_generator(time)
        # Default fallback pose
        return FakeAnimPose({
            "root": (0.0, 0.0, 0.0),
            "weapon_r": (10.0, 30.0 + time * 10.0, 100.0),
            "root_weapon_end_r": (25.0, 120.0 + time * 20.0, 150.0),
        })

    @staticmethod
    def get_bone_pose(pose: FakeAnimPose, bone_name: str, space: int) -> FakeTransform:
        return pose.get_bone_pose(bone_name, space)


class FakeUnrealModule:
    def __init__(self):
        self.AnimPoseSpaces = FakeAnimPoseSpaces
        self.AnimPoseEvaluationOptions = FakeAnimPoseEvaluationOptions
        self.AnimPoseExtensions = FakeAnimPoseExtensions
        self.logs: List[str] = []
        self.assets: Dict[str, FakeAnimSequence] = {}

    def log(self, msg: str):
        self.logs.append(msg)

    def load_asset(self, path: str) -> Any:
        return self.assets.get(path, None)


class TestProbeReachSyntheticArc(unittest.TestCase):
    """
    Analytical synthetic arc control.
    Constructs a known mathematical trajectory and asserts that analyze_reach_samples
    reproduces exact analytical extremes within floating-point tolerance.
    """

    def setUp(self):
        # Synthetic swing trajectory:
        # Time t in [0.0, 1.0], dt = 1/120 s
        # Root is at (0, 0, 0)
        # Blade sweeps an arc in the XY plane, with vertical dip in Z.
        # Angle phi(t) = -pi/6 + pi * t  (sweeps from -30 deg to +150 deg)
        # Tip radius R_tip = 150.0 cm
        # Base radius R_base = 40.0 cm
        # Component space convention: +Y is forward, X is lateral, +Z is vertical.
        # X(t) = -R * cos(phi(t))  (lateral: right +X, left -X)
        # Y(t) = R * sin(phi(t))   (forward reach)
        # Z(t) = 110.0 + 30.0 * cos(pi * t)
        self.dt = 1.0 / 120.0
        self.total_time = 1.0
        self.num_steps = int(round(self.total_time / self.dt)) + 1

        self.r_tip = 150.0
        self.r_base = 40.0

        self.samples = []
        for step in range(self.num_steps):
            t = min(step * self.dt, self.total_time)
            phi = -math.pi / 6.0 + math.pi * t

            tip_x = -self.r_tip * math.cos(phi)
            tip_y = self.r_tip * math.sin(phi)
            tip_z = 110.0 + 30.0 * math.cos(math.pi * t)

            base_x = -self.r_base * math.cos(phi)
            base_y = self.r_base * math.sin(phi)
            base_z = 80.0 + 15.0 * math.cos(math.pi * t)

            self.samples.append({
                "time": t,
                "base_rel": (base_x, base_y, base_z),
                "tip_rel": (tip_x, tip_y, tip_z),
            })

    def test_analytical_max_forward_tip(self):
        """Analytical peak forward Y occurs at phi = pi/2 -> t = 2/3 s."""
        active_window = (0.4, 0.8)
        analysis = analyze_reach_samples(self.samples, active_window)

        max_tip = analysis["max_tip_forward"]
        # Peak forward Y must equal R_tip (150.0)
        self.assertAlmostEqual(max_tip["forward_y"], 150.0, places=1)
        # Peak time must be near 2/3 s (0.6667 s)
        self.assertAlmostEqual(max_tip["time"], 2.0 / 3.0, places=2)
        # At peak forward, X = -R * cos(pi/2) = 0.0
        self.assertAlmostEqual(max_tip["lateral_x"], 0.0, places=1)
        # At t = 2/3 s, Z = 110.0 + 30.0 * cos(2*pi/3) = 110.0 - 15.0 = 95.0
        self.assertAlmostEqual(max_tip["vertical_z"], 95.0, places=1)

    def test_analytical_max_forward_base(self):
        """Analytical peak forward Y for weapon_r occurs at phi = pi/2 -> t = 2/3 s."""
        active_window = (0.4, 0.8)
        analysis = analyze_reach_samples(self.samples, active_window)

        max_base = analysis["max_base_forward"]
        self.assertAlmostEqual(max_base["forward_y"], 40.0, places=1)
        self.assertAlmostEqual(max_base["time"], 2.0 / 3.0, places=2)
        self.assertAlmostEqual(max_base["lateral_x"], 0.0, places=1)
        # At t = 2/3 s, base Z = 80.0 + 15.0 * cos(2*pi/3) = 80.0 - 7.5 = 72.5
        self.assertAlmostEqual(max_base["vertical_z"], 72.5, places=1)

    def test_active_window_swept_envelope(self):
        """Swept envelope across active window [0.5, 0.8] matches analytical bounds."""
        active_window = (0.5, 0.8)
        analysis = analyze_reach_samples(self.samples, active_window)
        env = analysis["active_window_swept_envelope"]

        # Peak forward in window is at t = 2/3 s -> 150.0
        self.assertAlmostEqual(env["peak_forward_in_window"], 150.0, places=1)

        # Min forward in window occurs at base at t=0.5:
        # phi(0.5) = -pi/6 + pi/2 = pi/3 = 60 deg -> sin(60) = sqrt(3)/2 ~= 0.8660
        # base_y(0.5) = 40 * 0.8660 = 34.64 cm
        expected_min_y = 40.0 * math.sin(math.pi / 3.0)
        self.assertAlmostEqual(env["forward_y_range"][0], round(expected_min_y, 2), places=1)
        self.assertAlmostEqual(env["forward_y_range"][1], 150.0, places=1)

        # Lateral range: at t=0.5, phi=60 deg -> cos(60) = 0.5. tip_x = -150 * 0.5 = -75.0
        # at t=0.8, phi= -pi/6 + 0.8*pi = 0.6333*pi = 114 deg -> cos(114) ~= -0.4067 -> tip_x = +61.01
        self.assertTrue(env["lateral_x_range"][0] < 0.0)
        self.assertTrue(env["lateral_x_range"][1] > 0.0)
        self.assertGreater(env["lateral_half_width"], 50.0)


class TestProbeReachFakeModule(unittest.TestCase):
    """Tests probe_reach execution against fake unreal reflection module."""

    def setUp(self):
        self.unreal = FakeUnrealModule()
        # Register a fake Swing1_Slow asset
        self.seq_path = "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing1_Slow"
        self.unreal.assets[self.seq_path] = FakeAnimSequence("Swing1_Slow", 1.8333)

    def test_resolve_world_space_enum(self):
        val = resolve_world_space_enum(self.unreal)
        self.assertEqual(val, 1)

    def test_evaluate_and_get_bone_translation(self):
        seq = self.unreal.assets[self.seq_path]
        pose = evaluate_pose_at_time(self.unreal, seq, 0.5)
        root_xyz = get_bone_translation(self.unreal, pose, "root")
        base_xyz = get_bone_translation(self.unreal, pose, "weapon_r")
        tip_xyz = get_bone_translation(self.unreal, pose, "root_weapon_end_r")

        self.assertEqual(root_xyz, (0.0, 0.0, 0.0))
        self.assertEqual(base_xyz, (10.0, 35.0, 100.0))
        self.assertEqual(tip_xyz, (25.0, 130.0, 150.0))

    def test_log_reach_format(self):
        log_reach(self.unreal, "TEST_TAG", {"key": "val", "num": 42})
        self.assertEqual(len(self.unreal.logs), 1)
        logged = self.unreal.logs[0]
        self.assertTrue(logged.startswith("[REACH_TEST_TAG] "))
        parsed = json.loads(logged[len("[REACH_TEST_TAG] "):])
        self.assertEqual(parsed["key"], "val")
        self.assertEqual(parsed["num"], 42)

    def test_probe_sequence_success(self):
        res = probe_sequence(self.unreal, self.seq_path, dt=0.1)
        self.assertIsNotNone(res)
        self.assertEqual(res["sequence_name"], "Swing1_Slow")
        self.assertEqual(res["sequence_path"], self.seq_path)
        self.assertIn("max_tip_forward", res)
        self.assertIn("max_base_forward", res)
        self.assertIn("active_window_swept_envelope", res)

        # Check logs emitted
        tags = [l.split(" ")[0] for l in self.unreal.logs]
        self.assertIn("[REACH_SEQUENCE]", tags)
        self.assertIn("[REACH_MAX_FORWARD]", tags)
        self.assertIn("[REACH_ACTIVE_WINDOW]", tags)

    def test_probe_sequence_missing_asset(self):
        res = probe_sequence(self.unreal, "/Game/NonExistent", dt=0.1)
        self.assertIsNone(res)
        tags = [l.split(" ")[0] for l in self.unreal.logs]
        self.assertIn("[REACH_WARNING]", tags)

    def test_run_probe_end_to_end_with_json_output(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_json = os.path.join(tmpdir, "probe_reach_output.json")
            summary = run_probe(
                self.unreal,
                sequences=[self.seq_path],
                output_path=out_json,
                dt=0.1
            )
            self.assertEqual(summary["status"], "SUCCESS")
            self.assertEqual(len(summary["measured_sequences"]), 1)
            self.assertTrue(os.path.exists(out_json))

            with open(out_json, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            self.assertEqual(loaded["status"], "SUCCESS")
            self.assertEqual(loaded["measured_sequences"][0]["sequence_name"], "Swing1_Slow")


class TestReachAnalysisEdgeCases(unittest.TestCase):
    """Tests edge cases and validations in reach calculation."""

    def test_empty_samples_raises_value_error(self):
        with self.assertRaises(ValueError):
            analyze_reach_samples([], (0.1, 0.5))

    def test_single_sample_window_fallback(self):
        sample = {
            "time": 0.5,
            "base_rel": (0.0, 30.0, 50.0),
            "tip_rel": (0.0, 120.0, 80.0),
        }
        # Window [0.1, 0.2] does not contain 0.5, should fallback to nearest
        analysis = analyze_reach_samples([sample], (0.1, 0.2))
        env = analysis["active_window_swept_envelope"]
        self.assertEqual(env["sample_count"], 1)
        self.assertEqual(env["peak_forward_in_window"], 120.0)


if __name__ == "__main__":
    unittest.main()
