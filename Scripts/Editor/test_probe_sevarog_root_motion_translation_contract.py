"""
Offline contract test for Scripts/Editor/probe_sevarog_root_motion_translation.py.

Authority: Claude Lead Directive [C-1240] / C-1240a (2026-11-10).
Notice: This offline test verifies script structure, safety wrappers, targeted assets,
and API calling conventions. It does NOT invoke Unreal Engine directly.
"""

import os
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCRIPT_PATH = os.path.join(PROJECT_ROOT, "Scripts", "Editor", "probe_sevarog_root_motion_translation.py")


class TestProbeSevarogRootMotionTranslationContract(unittest.TestCase):
    def test_script_exists(self):
        self.assertTrue(os.path.isfile(SCRIPT_PATH), f"Script missing: {SCRIPT_PATH}")

    def test_target_sequences_covered(self):
        with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
            code = f.read()

        targets = [
            "Speedburst",
            "Swing3_Slow",
            "Ultimate_Swing_120fps",
            "Subjugation",
            "Swing1_Medium",
        ]
        for t in targets:
            self.assertIn(t, code, f"Target sequence {t} not found in script")

    def test_guarded_execution_pattern(self):
        with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
            code = f.read()

        # Confirmed AnimationLibrary API check and call
        self.assertIn("get_bone_pose_for_time", code)
        self.assertIn("sample_bone_transform", code)
        self.assertIn("hasattr(AL, \"get_bone_pose_for_time\")", code)

        # Root and pelvis sampling
        self.assertIn('"root"', code)
        self.assertIn('"pelvis"', code)

        # Strictly read-only
        self.assertNotIn("save_asset", code)
        self.assertNotIn("save_loaded_asset", code)


if __name__ == "__main__":
    unittest.main()
