"""Evidence gate edges for the real A4 guard-counter probe."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).with_name("pie_er_a4_guard_counter.py")


class A4GuardCounterTests(unittest.TestCase):
    def test_requires_real_arm_counter_montage_and_boss_damage(self):
        ue = types.SimpleNamespace(
            Paths=types.SimpleNamespace(project_dir=lambda: str(SCRIPT.parents[2])),
            register_slate_post_tick_callback=lambda callback: object(),
        )
        spec = importlib.util.spec_from_file_location("a4_guard_under_test", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"unreal": ue}):
            spec.loader.exec_module(module)
        clip = {"AM_ER_Attack_GuardCounter"}
        self.assertTrue(module.valid_counter(True, clip, 2000.0, 1977.6))
        self.assertFalse(module.valid_counter(False, clip, 2000.0, 1977.6))
        self.assertFalse(module.valid_counter(True, {"Ability_E_Anim_Montage"}, 2000.0, 1977.6))
        self.assertFalse(module.valid_counter(True, clip, 2000.0, 2000.0))
        self.assertFalse(module.valid_counter(True, clip, None, 1977.6))

        loadout = types.SimpleNamespace(is_combat_enabled=lambda: True)
        with patch.object(module.plc, "player_montage", return_value=("DrawMontage", 0.2)):
            self.assertFalse(module.draw_ready(loadout, object()))
        with patch.object(module.plc, "player_montage", return_value=(None, None)):
            self.assertTrue(module.draw_ready(loadout, object()))
            self.assertFalse(module.draw_ready(types.SimpleNamespace(is_combat_enabled=lambda: False), object()))


if __name__ == "__main__":
    unittest.main()
