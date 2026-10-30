#!/usr/bin/env python3
"""
test_bake_blade_path.py
=======================
Offline test suite for bake_blade_path.py (A-308 / C-425).
Runs 100% offline with zero engine dependency.

Test Coverage:
1. Time sampling math: exact window edges included, 120 Hz intermediate timestamps, monotonicity.
2. Synthetic arc control: analytical thrust/swing kinematics, apex penetration.
3. Safety gates & refusal cases:
   - Sequence mismatch refusal.
   - Window end exceeding clip length refusal.
4. Unreal reflection mock: AnimPose WORLD evaluation and bone translation extraction.
5. End-to-end validator parity: baked card output passes validate_move_card_spec() with 0 errors.
"""

import os
import sys
import math
import json
import unittest
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Ensure MoveCards directory is on sys.path
cur_dir = str(Path(__file__).resolve().parent)
if cur_dir not in sys.path:
    sys.path.insert(0, cur_dir)

from bake_blade_path import (
    compute_sample_times,
    generate_synthetic_arc_samples,
    run_bake,
    NOMINAL_RATE_HZ,
    NOMINAL_DT
)
from author_move_cards import validate_move_card_spec


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
        raise KeyError(f"Bone '{bone_name}' not found in fake pose")


class FakeAnimSequence:
    def __init__(self, path: str, length: float):
        self.path = path
        self.length = length

    def get_play_length(self) -> float:
        return self.length


class FakeEditorAssetLibrary:
    def __init__(self, asset_map: Dict[str, Any]):
        self.asset_map = asset_map

    def load_asset(self, path: str) -> Any:
        return self.asset_map.get(path)


class FakeAnimPoseExtensions:
    @staticmethod
    def get_anim_pose_at_time(seq_asset: Any, time_sec: float, eval_opts: Any = None) -> FakeAnimPose:
        # Dynamic kinematics based on time
        base_x = 115.0 - 100.0 * math.sin(time_sec * math.pi)
        base_y = 0.0
        base_z = 100.0
        tip_x = base_x - 65.0
        tip_y = 115.0
        tip_z = base_z + 20.0
        return FakeAnimPose({
            "weapon_r": (base_x, base_y, base_z),
            "root_weapon_end_r": (tip_x, tip_y, tip_z)
        })


class FakeUnrealModule:
    def __init__(self, seq_map: Dict[str, Any]):
        self.EditorAssetLibrary = FakeEditorAssetLibrary(seq_map)
        self.AnimPoseExtensions = FakeAnimPoseExtensions()
        self.AnimPoseSpaces = type("AnimPoseSpaces", (), {"WORLD": 1})()


def make_test_card() -> Dict[str, Any]:
    """Produces a minimal valid card spec for testing."""
    return {
        "Schema": 1,
        "MoveId": "Move_Test_Thrust",
        "FamilyId": "Family_02_AntiGreed",
        "PhaseId": "Phase_1",
        "Skeleton": "/Game/Skeleton",
        "Sequence": "/Game/Animations/ThrustAnim",
        "Montage": None,
        "SlotName": "FullBody",
        "SectionName": "None",
        "PlayRate": 1.0,
        "ClipLengthSeconds": 1.5,
        "CommitSeconds": 0.2,
        "ActiveStartSeconds": 0.25,
        "ActiveEndSeconds": 0.3083,
        "RecoveryEndSeconds": 0.5,
        "TrackDegreesPerSecond": 180.0,
        "MinRangeCm": 90.0,
        "MaxRangeCm": 185.0,
        "FrontConeDegrees": 100.0,
        "HPDamage": 20.0,
        "bUsesRootMotion": False,
        "Windows": [
            {
                "WindowId": "Window_Thrust_0",
                "HitGroup": "HitGroup_ScytheBlade",
                "StartSeconds": 0.25,
                "EndSeconds": 0.3083,
                "SocketA": "weapon_r",
                "SocketB": "root_weapon_end_r",
                "RadiusCm": 15.0
            }
        ]
    }


class TestBakeBladePath(unittest.TestCase):
    def test_compute_sample_times_exact_edges_and_120hz(self):
        w_start = 0.2500
        w_end = 0.3083
        times = compute_sample_times(w_start, w_end, rate_hz=120.0)

        self.assertEqual(times[0], w_start, "First sample must exactly match w_start")
        self.assertEqual(times[-1], w_end, "Last sample must exactly match w_end")
        self.assertEqual(len(times), 8, f"Expected exactly 8 samples for AntiGreed window span, got {len(times)}")

        # Check strict monotonicity and step bound
        dt = 1.0 / 120.0
        for i in range(1, len(times)):
            delta = times[i] - times[i - 1]
            self.assertGreater(delta, 0.0, f"Times must be strictly monotonic at index {i}")
            self.assertLessEqual(delta, dt * 1.5, f"Step delta {delta} exceeds max step tolerance at index {i}")

    def test_synthetic_arc_control_kinematics(self):
        samples = generate_synthetic_arc_samples(0.25, 0.3083, rate_hz=120.0, is_thrust=True)
        self.assertEqual(len(samples), 8)

        # Check start and end positions match retracted windup/recovery
        self.assertEqual(samples[0]["BaseCS"][0], 120.0)
        self.assertEqual(samples[-1]["BaseCS"][0], 120.0)

        # Check apex forward thrust penetration (midpoint sample has lowest BaseCS.X)
        mid_idx = len(samples) // 2
        apex_base_x = samples[mid_idx]["BaseCS"][0]
        self.assertLess(apex_base_x, 20.0, f"Apex Base X ({apex_base_x}) should deeply penetrate player boundary")

    def test_refusal_on_sequence_mismatch(self):
        card = make_test_card()
        success, _, logs = run_bake(
            card_data=card,
            requested_sequence="/Game/Animations/DifferentSequence",
            synthetic_arc=True
        )
        self.assertFalse(success, "Bake must fail when requested sequence != card declared sequence")
        self.assertTrue(any("Sequence mismatch" in l for l in logs), f"Logs must report sequence mismatch: {logs}")

    def test_refusal_on_window_end_exceeding_clip_length(self):
        card = make_test_card()
        card["ClipLengthSeconds"] = 0.28  # shorter than Window.EndSeconds (0.3083)
        success, _, logs = run_bake(
            card_data=card,
            synthetic_arc=True
        )
        self.assertFalse(success, "Bake must fail when window EndSeconds > clip length")
        self.assertTrue(any("exceeds clip length" in l for l in logs), f"Logs must report clip length exceedance: {logs}")

    def test_fake_unreal_reflection_bake(self):
        card = make_test_card()
        seq_path = card["Sequence"]
        fake_seq = FakeAnimSequence(seq_path, length=1.5)
        fake_unreal = FakeUnrealModule({seq_path: fake_seq})

        success, baked_card, logs = run_bake(
            card_data=card,
            unreal_mod=fake_unreal,
            synthetic_arc=False,
            rate_hz=120.0
        )
        self.assertTrue(success, f"Fake Unreal bake failed: {logs}")
        self.assertEqual(baked_card["ClipLengthSeconds"], 1.5)

        baked_win = baked_card["Windows"][0]
        self.assertIn("BakedSamples", baked_win)
        self.assertEqual(len(baked_win["BakedSamples"]), 8)
        self.assertEqual(baked_win["BakedClipLengthSeconds"], 1.5)

    def test_baked_card_passes_author_validator_cleanly(self):
        card = make_test_card()
        success, baked_card, logs = run_bake(
            card_data=card,
            synthetic_arc=True,
            rate_hz=120.0
        )
        self.assertTrue(success)

        # Validate with author_move_cards validator
        errors = validate_move_card_spec(baked_card)
        self.assertEqual(errors, [], f"Baked card must pass validate_move_card_spec with 0 errors: {errors}")


if __name__ == "__main__":
    unittest.main()
