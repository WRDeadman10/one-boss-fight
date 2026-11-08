"""Movement precondition tests for the default-wiring dodge witness."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).with_name("pie_er_default_wiring_dodge.py")


class DefaultWiringDodgeTests(unittest.TestCase):
    def test_moving_roll_requires_input_and_velocity_at_press(self):
        ue = types.SimpleNamespace(register_slate_post_tick_callback=lambda callback: object(), log=lambda message: None)
        spec = importlib.util.spec_from_file_location("default_dodge_under_test", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"unreal": ue}):
            spec.loader.exec_module(module)
        self.assertTrue(module.valid_sample("dodge_standing_tap", "AM_ER_Backstep_Back", 0.0, 0.0))
        self.assertTrue(module.valid_sample("dodge_moving_tap", "Dodge_Small_Forward_Roll_Montage", 474.2, 1.0))
        self.assertFalse(module.valid_sample("dodge_moving_tap", "Dodge_Small_Forward_Roll_Montage", 0.0, 0.0))
        self.assertFalse(module.valid_sample("dodge_moving_tap", "AM_ER_Backstep_Back", 474.2, 1.0))
        self.assertFalse(module.valid_sample("dodge_standing_tap", "AM_ER_Backstep_Back", 0.0, 1.0))


if __name__ == "__main__":
    unittest.main()
