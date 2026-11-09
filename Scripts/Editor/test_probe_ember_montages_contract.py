"""
Offline contract test for Scripts/Editor/probe_ember_montages.py.

Authority: Claude Lead Directive [C-1236] (2026-11-10).
Notice: This offline test verifies script structure, safety wrappers, and API calling conventions.
It does NOT verify live Unreal Engine 5.5 API signatures (which are validated via Lead engine run).
"""

import os
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCRIPT_PATH = os.path.join(PROJECT_ROOT, "Scripts", "Editor", "probe_ember_montages.py")


class TestProbeEmberMontagesContract(unittest.TestCase):
    def test_script_exists(self):
        self.assertTrue(os.path.isfile(SCRIPT_PATH), f"Script missing: {SCRIPT_PATH}")

    def test_guarded_execution_pattern(self):
        with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
            code = f.read()

        # Rule 1: Safe guarded call wrappers present
        self.assertIn("def safe_call", code)
        self.assertIn("def safe_prop", code)
        self.assertIn("n/a", code)

        # Rule 2: Uses AnimationLibrary.get_animation_notify_events
        self.assertIn("get_animation_notify_events", code)
        self.assertNotIn("get_editor_property(\"notifies\")", code)

        # Rule 3: Confirmed section methods used
        self.assertIn("get_num_sections", code)
        self.assertIn("get_section_name", code)

        # Strictly read-only: no save_asset calls
        self.assertNotIn("save_asset", code)
        self.assertNotIn("save_loaded_asset", code)


if __name__ == "__main__":
    unittest.main()
