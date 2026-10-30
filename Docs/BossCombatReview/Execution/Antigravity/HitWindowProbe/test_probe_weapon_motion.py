"""
Unit tests for Hit-Window Extraction Probe (A-243).
Runs 100% offline with zero engine dependency using high-fidelity mock reflection.
Includes rotating-parent negative control proving local-space evaluation fails.
"""

import math
import os
import unittest
from pathlib import Path
from typing import Any

# Add probe directory to sys.path
import sys
probe_dir = str(Path(__file__).resolve().parent)
if probe_dir not in sys.path:
    sys.path.insert(0, probe_dir)

from probe_weapon_motion import (
    vector_distance,
    compute_speed,
    extract_active_windows,
    sample_sequence_motion,
    resolve_world_space_enum,
    check_bone_track_presence,
    DEFAULT_SEVAROG_SEQUENCES,
    DEFAULT_BASE_BONE,
    DEFAULT_TIP_BONE,
    DEFAULT_DT
)


class MockVector:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z


class MockTransform:
    def __init__(self, x: float, y: float, z: float):
        self.translation = MockVector(x, y, z)


class MockAnimPoseSpaces:
    LOCAL = 0
    WORLD = 1


class MockAnimPose:
    """Mock FAnimPose holding both local and component-space poses."""
    def __init__(self, time: float, seq_length: float):
        self.time = time
        self.seq_length = seq_length

    def get_bone_pose(self, bone_name: str, space: int = MockAnimPoseSpaces.LOCAL) -> MockTransform:
        # Rotating parent model:
        # In LOCAL space:
        #   weapon_r base position: (0, 0, 100)
        #   root_weapon_end_r tip position: (100, 0, 0) - CONSTANT offset from parent!
        if space == MockAnimPoseSpaces.LOCAL:
            if bone_name == "weapon_r":
                return MockTransform(0.0, 0.0, 100.0)
            elif bone_name == "root_weapon_end_r":
                return MockTransform(100.0, 0.0, 0.0)
            return MockTransform(0.0, 0.0, 0.0)

        # In WORLD (component) space:
        #   weapon_r rotates in XY plane at omega = 10 rad/s
        #   root_weapon_end_r tip sweeps at radius = 100 cm, velocity = 1000 cm/s
        elif space == MockAnimPoseSpaces.WORLD:
            omega = 10.0  # rad/s
            theta = omega * self.time
            if bone_name == "weapon_r":
                bx = 20.0 * math.cos(theta)
                by = 20.0 * math.sin(theta)
                bz = 100.0
                return MockTransform(bx, by, bz)
            elif bone_name == "root_weapon_end_r":
                tx = (20.0 + 100.0) * math.cos(theta)
                ty = (20.0 + 100.0) * math.sin(theta)
                tz = 100.0
                return MockTransform(tx, ty, tz)
            return MockTransform(0.0, 0.0, 0.0)

        raise ValueError(f"Unknown space: {space}")


class MockAnimSequence:
    def __init__(self, name: str, length: float = 1.0):
        self.name = name
        self.length = length

    def get_editor_property(self, prop: str):
        if prop == "sequence_length":
            return self.length
        raise AttributeError(prop)


class MockAnimPoseExtensions:
    @staticmethod
    def get_anim_pose_at_time(seq_asset: MockAnimSequence, time: float, eval_options: Any) -> MockAnimPose:
        return MockAnimPose(time=time, seq_length=seq_asset.length)

    @staticmethod
    def get_bone_pose(pose: MockAnimPose, bone_name: str, space: int) -> MockTransform:
        return pose.get_bone_pose(bone_name, space)


class MockAnimationBlueprintLibrary:
    @staticmethod
    def get_sequence_length(anim_sequence: MockAnimSequence) -> float:
        return anim_sequence.length

    @staticmethod
    def get_animation_track_names(anim_sequence: MockAnimSequence) -> list:
        # weapon_r has an explicit track, root_weapon_end_r is a child bone on weapon_r
        return ["root", "pelvis", "weapon_r"]


class MockEditorAssetLibrary:
    @staticmethod
    def load_asset(path: str):
        if "NonExistent" in path:
            return None
        return MockAnimSequence(name=os.path.basename(path), length=1.0)


class MockUnrealModule:
    AnimPoseSpaces = MockAnimPoseSpaces
    AnimPoseExtensions = MockAnimPoseExtensions
    AnimationBlueprintLibrary = MockAnimationBlueprintLibrary
    EditorAssetLibrary = MockEditorAssetLibrary


class TestRotatingParentComponentVsLocal(unittest.TestCase):
    """
    Proves that component-space evaluation correctly captures weapon rotation,
    while local-space evaluation fails closed (yields 0 tip speed).
    """
    def setUp(self):
        self.mock_unreal = MockUnrealModule()

    def test_world_space_measures_swing_velocity(self):
        # Component-space sampling
        res = sample_sequence_motion(
            self.mock_unreal,
            sequence_path="/Game/TestSwing",
            base_bone="weapon_r",
            tip_bone="root_weapon_end_r",
            dt=1.0 / 120.0
        )
        self.assertEqual(res["bone_pose_method"], "AnimPose.get_bone_pose(WORLD)")
        self.assertGreater(res["peak_tip_speed_cms"], 1000.0, "Rotating tip must yield ~1200 cm/s in component space")
        self.assertGreater(len(res["active_windows_50pct"]), 0, "Must detect active speed window")

    def test_local_space_negative_control_fails_closed(self):
        # If someone mistakenly evaluates in LOCAL space:
        # Tip offset is constant (100, 0, 0), so delta distance between frames is 0.0
        pose_0 = MockAnimPose(time=0.0, seq_length=1.0)
        pose_1 = MockAnimPose(time=0.05, seq_length=1.0)

        t0 = pose_0.get_bone_pose("root_weapon_end_r", MockAnimPoseSpaces.LOCAL)
        t1 = pose_1.get_bone_pose("root_weapon_end_r", MockAnimPoseSpaces.LOCAL)

        p0 = (t0.translation.x, t0.translation.y, t0.translation.z)
        p1 = (t1.translation.x, t1.translation.y, t1.translation.z)

        local_spd = compute_speed(p0, p1, 0.05)
        self.assertEqual(local_spd, 0.0, "Local-space tip speed MUST be 0 for constant child offset")

        # In contrast, WORLD space yields massive velocity:
        w0 = pose_0.get_bone_pose("root_weapon_end_r", MockAnimPoseSpaces.WORLD)
        w1 = pose_1.get_bone_pose("root_weapon_end_r", MockAnimPoseSpaces.WORLD)
        wp0 = (w0.translation.x, w0.translation.y, w0.translation.z)
        wp1 = (w1.translation.x, w1.translation.y, w1.translation.z)

        world_spd = compute_speed(wp0, wp1, 0.05)
        self.assertGreater(world_spd, 1000.0, "World-space tip speed must reflect parent angular velocity")


class TestTrackPresence(unittest.TestCase):
    def test_track_presence_detection(self):
        mock_unreal = MockUnrealModule()
        seq = MockAnimSequence("TestSeq", 1.0)
        tracks = check_bone_track_presence(mock_unreal, seq, ["weapon_r", "root_weapon_end_r", "non_existent_bone"])
        self.assertTrue(tracks["weapon_r"], "weapon_r has track in mock library")
        self.assertFalse(tracks["root_weapon_end_r"], "root_weapon_end_r has no track (child socket/bone)")
        self.assertFalse(tracks["non_existent_bone"])


class TestWeaponMotionMath(unittest.TestCase):
    def test_vector_distance_3d(self):
        v1 = (0.0, 0.0, 0.0)
        v2 = (3.0, 4.0, 0.0)
        self.assertAlmostEqual(vector_distance(v1, v2), 5.0)

        v3 = (1.0, 2.0, 2.0)
        v4 = (4.0, 6.0, 14.0)
        self.assertAlmostEqual(vector_distance(v3, v4), 13.0)

    def test_compute_speed_cms(self):
        p1 = (0.0, 0.0, 0.0)
        p2 = (100.0, 0.0, 0.0)
        dt = 0.1
        self.assertAlmostEqual(compute_speed(p1, p2, dt), 1000.0)

    def test_compute_speed_zero_dt(self):
        self.assertEqual(compute_speed((0, 0, 0), (1, 1, 1), 0.0), 0.0)


class TestActiveWindowExtraction(unittest.TestCase):
    def test_single_active_window(self):
        samples = []
        for i in range(100):
            t = i * 0.01
            spd = 2000.0 * math.exp(-((t - 0.5) ** 2) / 0.01)
            samples.append({
                "time": t,
                "tip_speed": spd
            })

        windows = extract_active_windows(samples, threshold_ratio=0.5, min_samples=3)
        self.assertEqual(len(windows), 1)
        w = windows[0]
        self.assertGreater(w["peak_speed_cms"], 1900.0)
        self.assertAlmostEqual(w["peak_time"], 0.5, delta=0.02)
        self.assertLess(w["start_time"], 0.5)
        self.assertGreater(w["end_time"], 0.5)


class TestEngineSourceCitations(unittest.TestCase):
    def test_anim_pose_header_citations(self):
        header_path = Path("C:/Program Files/Epic Games/UE_5.5/Engine/Source/Editor/AnimationBlueprintLibrary/Public/AnimPose.h")
        self.assertTrue(header_path.is_file(), f"Header must exist at {header_path}")
        content = header_path.read_text(encoding="utf-8", errors="replace")
        self.assertIn("enum class EAnimPoseSpaces : uint8", content)
        self.assertIn("GetBonePose", content)
        self.assertIn("GetAnimPoseAtTime", content)

    def test_animation_blueprint_library_track_names(self):
        header_path = Path("C:/Program Files/Epic Games/UE_5.5/Engine/Source/Editor/AnimationBlueprintLibrary/Public/AnimationBlueprintLibrary.h")
        self.assertTrue(header_path.is_file(), f"Header must exist at {header_path}")
        content = header_path.read_text(encoding="utf-8", errors="replace")
        self.assertIn("GetAnimationTrackNames", content)


class TestReceiptIntegrity(unittest.TestCase):
    def test_evidence_receipt_cleanliness(self):
        receipt_path = Path(__file__).resolve().parent / "evidence_sha256.txt"
        self.assertTrue(receipt_path.is_file(), "evidence_sha256.txt must exist")
        raw = receipt_path.read_bytes()
        self.assertNotIn(b"\r\r\n", raw, "Must not contain \\r\\r\\n")
        self.assertNotIn(b"\n\n", raw, "Must not contain double newlines")
        lines = receipt_path.read_text(encoding="utf-8").splitlines()
        self.assertGreater(len(lines), 0)
        for i, l in enumerate(lines):
            self.assertTrue(l.strip(), f"Line {i+1} must not be blank")
            parts = l.split()
            self.assertEqual(len(parts), 3, f"Line {i+1} must have 3 parts: {l}")
            self.assertEqual(len(parts[0]), 64, "SHA256 must be 64 characters")
            self.assertTrue(parts[1].isdigit(), "Size must be integer")


if __name__ == "__main__":
    unittest.main()
