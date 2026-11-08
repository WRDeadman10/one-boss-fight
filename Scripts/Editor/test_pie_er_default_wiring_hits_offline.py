"""Damage gate edges for the unassigned default-wiring PIE probe."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).with_name("pie_er_default_wiring_hits.py")


class DefaultWiringHitTests(unittest.TestCase):
    def test_clip_identity_and_measured_hp_are_both_required(self):
        ue = types.SimpleNamespace(
            Paths=types.SimpleNamespace(project_dir=lambda: str(SCRIPT.parents[2])),
            register_slate_post_tick_callback=lambda callback: object(),
            log=lambda message: None,
        )
        spec = importlib.util.spec_from_file_location("default_hits_under_test", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"unreal": ue}):
            spec.loader.exec_module(module)
        self.assertTrue(module.expected_hit("jump_R1_air_light", "AM_ER_Attack_Air_Light", 2000, 1984.01))
        self.assertTrue(module.expected_hit("jump_R2_air_heavy", "AM_ER_Attack_Air_Heavy_Plunge", 1984.01, 1961.624))
        self.assertFalse(module.expected_hit("jump_R2_air_heavy", "Ability_E_Anim_Montage", 1984.01, 1961.624))
        self.assertFalse(module.expected_hit("jump_R1_air_light", "AM_ER_Attack_Air_Light", 2000, 2000))
        self.assertFalse(module.expected_hit("R1_tap_light", "Attack_PrimaryA_Montage", None, 1984.01))


if __name__ == "__main__":
    unittest.main()
