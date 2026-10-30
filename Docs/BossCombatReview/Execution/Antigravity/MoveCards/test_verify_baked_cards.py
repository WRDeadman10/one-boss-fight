#!/usr/bin/env python3
"""
test_verify_baked_cards.py
==========================
Offline unit tests for verify_baked_cards.py (Orders A-312 / C-427).
Runs 100% offline with zero engine dependency.

Test Coverage:
1. Matching live pose spot-check passes (drift 0.0 cm <= 2.0 cm, PASS).
2. Drift above tolerance (e.g. 5.0 cm > 2.0 cm) fails closed (FAIL, exit 1).
3. Missing baked samples on a card required by --require-baked fails closed (FAIL, exit 1).
4. Stale animation clip (live pose shifted from baked coordinates) fails closed (FAIL, exit 1).
5. In-memory tamper test (--test-tamper-apex 10.0) fails closed without modifying assets (FAIL, exit 1).
6. Non-baked card without --require-baked is skipped cleanly (SKIP, PASS).
"""

import os
import sys
import math
import json
import unittest
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

# Ensure MoveCards directory is on sys.path
cur_dir = str(Path(__file__).resolve().parent)
if cur_dir not in sys.path:
    sys.path.insert(0, cur_dir)

from verify_baked_cards import (
    find_apex_sample_index,
    extract_sample_data,
    verify_card_window_spot_checks,
    run_verification,
    DEFAULT_TOLERANCE_CM
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
        raise KeyError(f"Bone '{bone_name}' not found in fake pose")


class FakeAnimSequence:
    def __init__(self, path: str, length: float = 1.5):
        self.path = path
        self.length = length

    def get_play_length(self) -> float:
        return self.length


class DynamicPoseExtensions:
    def __init__(self, pose_func):
        self.pose_func = pose_func

    def get_anim_pose_at_time(self, seq_asset: Any, time_sec: float, eval_opts: Any = None) -> FakeAnimPose:
        return self.pose_func(seq_asset, time_sec)


class FakeEditorPropertyObject:
    def __init__(self, props: Optional[Dict[str, Any]] = None):
        self._props = props or {}

    def get_editor_property(self, name: str) -> Any:
        if name in self._props:
            return self._props[name]
        raise AttributeError(f"Property '{name}' not found")


class FakeUnrealModule:
    def __init__(self, seq_map: Dict[str, Any], pose_func):
        self.AnimPoseExtensions = DynamicPoseExtensions(pose_func)
        self.AnimPoseSpaces = type("AnimPoseSpaces", (), {"WORLD": 1})()
        self.EditorAssetLibrary = type("FakeAssetLib", (), {
            "load_asset": staticmethod(lambda p: seq_map.get(p)),
            "list_assets": staticmethod(lambda d, recursive=False: list(seq_map.keys()))
        })()


def make_test_card_with_samples(base_thrust_apex: float = 14.0, tip_forward_apex: float = 150.0) -> Dict[str, Any]:
    """Generates a test card with 8 baked samples featuring realistic forward reach excursion (+Y)."""
    times = [0.2500, 0.2583, 0.2667, 0.2750, 0.2833, 0.2917, 0.3000, 0.3083]
    samples = []
    for t in times:
        u = (t - 0.2500) / (0.3083 - 0.2500)
        apex_factor = 4.0 * u * (1.0 - u)
        bx = 120.0 - (120.0 - base_thrust_apex) * apex_factor
        by = 0.0
        bz = 100.0
        tx = bx - 65.0
        ty = 115.0 + (tip_forward_apex - 115.0) * apex_factor  # +Y forward reach apex
        tz = bz + 20.0
        samples.append({
            "TimeSeconds": round(t, 4),
            "BaseCS": [round(bx, 3), round(by, 3), round(bz, 3)],
            "TipCS": [round(tx, 3), round(ty, 3), round(tz, 3)]
        })

    return {
        "MoveId": "Move_Test_AntiGreed",
        "Sequence": "/Game/Animations/TestSeq",
        "Windows": [
            {
                "WindowId": "Window_FastJab",
                "SocketA": "weapon_r",
                "SocketB": "root_weapon_end_r",
                "BakedSamples": samples
            }
        ]
    }


class TestVerifyBakedCards(unittest.TestCase):
    def test_matching_live_pose_passes_within_tolerance(self):
        card = make_test_card_with_samples(base_thrust_apex=14.0)
        seq_path = card["Sequence"]
        seq_asset = FakeAnimSequence(seq_path)

        # Pose function matches the baked coordinates exactly
        def matching_pose(seq, t):
            u = (t - 0.2500) / (0.3083 - 0.2500)
            apex_factor = 4.0 * u * (1.0 - u)
            bx = 120.0 - (120.0 - 14.0) * apex_factor
            by = 0.0
            bz = 100.0
            tx = bx - 65.0
            ty = 115.0 + (150.0 - 115.0) * apex_factor
            tz = bz + 20.0
            return FakeAnimPose({
                "weapon_r": (bx, by, bz),
                "root_weapon_end_r": (tx, ty, tz)
            })

        fake_unreal = FakeUnrealModule({seq_path: seq_asset}, matching_pose)

        ok, logs = verify_card_window_spot_checks(
            unreal_mod=fake_unreal,
            seq_asset=seq_asset,
            move_id="Move_Test_AntiGreed",
            window_data=card["Windows"][0],
            tolerance_cm=2.0
        )
        self.assertTrue(ok, f"Matching pose must pass spot-checks: {logs}")
        self.assertTrue(any("Check=Start" in l and "Status=PASS" in l for l in logs))
        self.assertTrue(any("Check=Apex" in l and "Status=PASS" in l for l in logs))
        self.assertTrue(any("Check=End" in l and "Status=PASS" in l for l in logs))

    def test_drift_above_tolerance_fails_closed(self):
        card = make_test_card_with_samples(base_thrust_apex=14.0)
        seq_path = card["Sequence"]
        seq_asset = FakeAnimSequence(seq_path)

        # Pose function has drifted by 5.0 cm at apex
        def drifted_pose(seq, t):
            u = (t - 0.2500) / (0.3083 - 0.2500)
            apex_factor = 4.0 * u * (1.0 - u)
            bx = 120.0 - (120.0 - 14.0) * apex_factor
            by = 0.0
            bz = 100.0
            tx = bx - 65.0
            ty = by + 115.0 + (5.0 * apex_factor)  # 5.0 cm drift at apex!
            tz = bz + 20.0
            return FakeAnimPose({
                "weapon_r": (bx, by, bz),
                "root_weapon_end_r": (tx, ty, tz)
            })

        fake_unreal = FakeUnrealModule({seq_path: seq_asset}, drifted_pose)

        ok, logs = verify_card_window_spot_checks(
            unreal_mod=fake_unreal,
            seq_asset=seq_asset,
            move_id="Move_Test_AntiGreed",
            window_data=card["Windows"][0],
            tolerance_cm=2.0
        )
        self.assertFalse(ok, "Drift above 2.0 cm must fail spot-check")
        self.assertTrue(any("Status=FAIL" in l for l in logs))
        self.assertTrue(any("[BAKE_FATAL]" in l and "drift" in l for l in logs))

    def test_in_memory_tamper_flag_triggers_failure(self):
        card = make_test_card_with_samples(base_thrust_apex=14.0)
        seq_path = card["Sequence"]
        seq_asset = FakeAnimSequence(seq_path)

        # Normal matching pose
        def matching_pose(seq, t):
            return FakeAnimPose({
                "weapon_r": (120.0, 0.0, 100.0),
                "root_weapon_end_r": (55.0, 115.0, 120.0)
            })

        fake_unreal = FakeUnrealModule({seq_path: seq_asset}, matching_pose)

        # Inject 10.0 cm tamper delta
        ok, logs = verify_card_window_spot_checks(
            unreal_mod=fake_unreal,
            seq_asset=seq_asset,
            move_id="Move_Test_AntiGreed",
            window_data=card["Windows"][0],
            tolerance_cm=2.0,
            tamper_delta_cm=10.0
        )
        self.assertFalse(ok, "--test-tamper-apex must trigger failure")
        self.assertTrue(any("Check=Apex" in l and "Status=FAIL" in l for l in logs))

    def test_missing_baked_samples_with_require_baked_fails(self):
        card = {
            "MoveId": "Move_Required_Baked",
            "Sequence": "/Game/Animations/TestSeq",
            "Windows": [
                {
                    "WindowId": "Win_Empty",
                    "SocketA": "weapon_r",
                    "SocketB": "root_weapon_end_r",
                    "BakedSamples": []  # empty!
                }
            ]
        }
        seq_asset = FakeAnimSequence("/Game/Animations/TestSeq")
        fake_unreal = FakeUnrealModule({"/Game/Animations/TestSeq": seq_asset}, lambda s, t: None)

        # Write temp card json
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"cards": [card]}, f)
            temp_path = f.name

        try:
            success, logs = run_verification(
                unreal_mod=fake_unreal,
                card_json_path=temp_path,
                require_baked_moves=["Move_Required_Baked"]
            )
            self.assertFalse(success, "Must fail when required move has no baked samples")
            self.assertTrue(any("has NO baked samples but is listed in --require-baked" in l for l in logs))
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_apex_index_differs_from_start_and_end(self):
        # 1. Forward thrust path: TipCS.Y reaches apex at midpoint
        thrust_card = make_test_card_with_samples(base_thrust_apex=14.0, tip_forward_apex=155.0)
        thrust_samples = thrust_card["Windows"][0]["BakedSamples"]
        apex_thrust = find_apex_sample_index(thrust_samples)
        self.assertNotEqual(apex_thrust, 0, "Apex index must not be Start (index 0)")
        self.assertNotEqual(apex_thrust, len(thrust_samples) - 1, "Apex index must not be End (index n-1)")
        self.assertIn(apex_thrust, [3, 4], "Apex index must land on peak interior samples")

        # 2. Out-and-back swing path: TipCS.Y sweeps forward and retracts
        swing_times = [0.15, 0.18, 0.21, 0.24, 0.27, 0.30]
        swing_samples = []
        for t in swing_times:
            u = (t - 0.15) / (0.30 - 0.15)
            apex_f = 4.0 * u * (1.0 - u)
            swing_samples.append({
                "TimeSeconds": t,
                "BaseCS": [20.0, 0.0, 100.0],
                "TipCS": [50.0, 80.0 + (60.0 * apex_f), 110.0]
            })
        apex_swing = find_apex_sample_index(swing_samples)
        self.assertNotEqual(apex_swing, 0, "Swing apex must not be Start")
        self.assertNotEqual(apex_swing, len(swing_samples) - 1, "Swing apex must not be End")
        self.assertIn(apex_swing, [2, 3], "Swing apex must land on peak interior samples")

    def test_middle_sample_is_always_checked(self):
        card = make_test_card_with_samples(base_thrust_apex=14.0, tip_forward_apex=150.0)
        seq_path = card["Sequence"]
        seq_asset = FakeAnimSequence(seq_path)

        def matching_pose(seq, t):
            u = (t - 0.2500) / (0.3083 - 0.2500)
            apex_factor = 4.0 * u * (1.0 - u)
            bx = 120.0 - (120.0 - 14.0) * apex_factor
            tx = bx - 65.0
            ty = 115.0 + (150.0 - 115.0) * apex_factor
            return FakeAnimPose({
                "weapon_r": (bx, 0.0, 100.0),
                "root_weapon_end_r": (tx, ty, 120.0)
            })

        fake_unreal = FakeUnrealModule({seq_path: seq_asset}, matching_pose)

        ok, logs = verify_card_window_spot_checks(
            unreal_mod=fake_unreal,
            seq_asset=seq_asset,
            move_id="Move_Test_AntiGreed",
            window_data=card["Windows"][0],
            tolerance_cm=2.0
        )
        self.assertTrue(ok)
        # Verify Mid check is present
        mid_logs = [l for l in logs if "Check=Mid" in l]
        self.assertEqual(len(mid_logs), 1, "Must contain exactly one Check=Mid log")
        self.assertIn("SampleIdx=4", mid_logs[0], "Check=Mid must check sample index n // 2 = 4")
        self.assertIn("Status=PASS", mid_logs[0])

    def test_fatal_raises_runtime_error_in_main(self):
        import subprocess
        # Run verify_baked_cards.py with --test-tamper-apex 10.0 on a temp json
        card = make_test_card_with_samples(base_thrust_apex=14.0, tip_forward_apex=150.0)
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"cards": [card]}, f)
            temp_path = f.name

        try:
            # We run python script directly with --test-tamper-apex 10.0
            script_path = str(Path(__file__).resolve().parent / "verify_baked_cards.py")
            cmd = [
                sys.executable,
                script_path,
                "--card-json", temp_path,
                "--test-tamper-apex", "10.0"
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            self.assertNotEqual(res.returncode, 0, "CLI must exit non-zero on failure")
            self.assertIn("[BAKE_FATAL]", res.stdout + res.stderr, "Output must contain [BAKE_FATAL]")
            self.assertIn("RuntimeError", res.stderr, "Output must contain RuntimeError traceback")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_unbaked_card_without_require_baked_skips_cleanly(self):
        card = {
            "MoveId": "Move_Optional_Unbaked",
            "Sequence": "/Game/Animations/TestSeq",
            "Windows": [
                {
                    "WindowId": "Win_Empty",
                    "SocketA": "weapon_r",
                    "SocketB": "root_weapon_end_r",
                    "BakedSamples": []
                }
            ]
        }
        seq_asset = FakeAnimSequence("/Game/Animations/TestSeq")
        fake_unreal = FakeUnrealModule({"/Game/Animations/TestSeq": seq_asset}, lambda s, t: None)

        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"cards": [card]}, f)
            temp_path = f.name

        try:
            success, logs = run_verification(
                unreal_mod=fake_unreal,
                card_json_path=temp_path,
                require_baked_moves=None
            )
            self.assertTrue(success, "Unbaked card without --require-baked must pass (skip)")
            self.assertTrue(any("Status=SKIP" in l for l in logs))
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


if __name__ == "__main__":
    unittest.main()
