import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class DodgeActivationDiagnosticsContract(unittest.TestCase):
    def test_first_press_trace_reports_ability_tags_stamina_and_can_activate(self):
        source = (ROOT / "Source/OneBossFight/Player/RPGDodgeTiming.cpp").read_text(encoding="utf-8-sig")
        handler = source.split("void URPGDodgeTiming::OnDodgePressed", 1)[1].split("void URPGDodgeTiming::OnDodgeStarted", 1)[0]
        self.assertIn('TEXT("Can Activate Ability?")', handler)
        self.assertIn('ReadAttribute(GetOwner(), TEXT("Attribute.Stamina")', handler)
        self.assertIn("DescribeGuardState()", handler)
        self.assertIn("first_dodge_activation_trace", handler)
        self.assertIn("bCanActivate", handler)

    def test_probe_reaches_draw_ready_and_keeps_standing_and_moving_first_press_cases(self):
        probe = (ROOT / "Scripts/Editor/probe_first_dodge_after_draw.py").read_text(encoding="utf-8")
        self.assertIn('yield from wait(2.2)', probe)
        self.assertIn('key(pc, R2, True)', probe)
        self.assertIn('loadout.is_combat_enabled()', probe)
        self.assertIn('first_standing_dodge', probe)
        self.assertIn('first_moving_dodge', probe)
        self.assertIn('AM_ER_Backstep_Mixamo_V2', probe)
        self.assertIn('Dodge_Small_Forward_Roll_Montage', probe)
        self.assertNotIn('set_editor_property', probe)

    def test_default_wired_moving_probe_expects_owner_approved_standing_clip(self):
        probe = (ROOT / "Scripts/Editor/pie_er_default_wiring_dodge.py").read_text(encoding="utf-8")
        standing = probe.split('if case == "dodge_standing_tap":', 1)[1].split('if case == "dodge_moving_tap":', 1)[0]
        self.assertIn('AM_ER_Backstep_Mixamo_V2', standing)
        self.assertNotIn('AM_ER_Backstep_Back', standing)
        moving = probe.split('if case == "dodge_moving_tap":', 1)[1].split('return False', 1)[0]
        self.assertIn('Dodge_Small_Forward_Roll_Montage', moving)


if __name__ == "__main__":
    unittest.main()
