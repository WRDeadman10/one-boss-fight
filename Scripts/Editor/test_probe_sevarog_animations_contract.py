"""
Offline contract test for Scripts/Editor/probe_sevarog_animations.py.

Authority: Claude Lead Directive [C-1238] (2026-11-10).
Notice: This offline test verifies script structure, safety wrappers, and API calling conventions.
It does NOT verify live Unreal Engine 5.5 API signatures (which are validated via Lead engine run).
"""

import os
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCRIPT_PATH = os.path.join(PROJECT_ROOT, "Scripts", "Editor", "probe_sevarog_animations.py")


class TestProbeSevarogAnimationsContract(unittest.TestCase):
    def test_script_exists(self):
        self.assertTrue(os.path.isfile(SCRIPT_PATH), f"Script missing: {SCRIPT_PATH}")

    def test_categories_and_assets_covered(self):
        with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
            code = f.read()

        # Category A: Montages
        self.assertIn("Swing1_Medium_Montage", code)
        self.assertIn("Swing2_Medium_Montage", code)
        self.assertIn("LevelStart_Montage", code)

        # Category B: Melee sequences
        self.assertIn("Swing1_Medium", code)
        self.assertIn("Swing2_Medium", code)
        self.assertIn("Swing3_Medium", code)
        self.assertIn("Swing_In_Air", code)

        # Category C: Abilities
        self.assertIn("Ultimate_Swing_120fps", code)
        self.assertIn("Subjugation", code)
        self.assertIn("Soul_Siphon", code)
        self.assertIn("Speedburst", code)

    def test_guarded_execution_pattern(self):
        with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
            code = f.read()

        # Guarded wrappers present
        self.assertIn("def safe_call", code)
        self.assertIn("def safe_prop", code)
        self.assertIn("probe_root_motion", code)
        self.assertIn("enable_root_motion", code)

        # AnimationLibrary.get_animation_notify_events used
        self.assertIn("get_animation_notify_events", code)
        self.assertNotIn("get_editor_property(\"notifies\")", code)

        # Strictly read-only
        self.assertNotIn("save_asset", code)
        self.assertNotIn("save_loaded_asset", code)


if __name__ == "__main__":
    unittest.main()
