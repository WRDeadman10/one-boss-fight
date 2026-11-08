"""Static contract checks for optional ER air montage wiring."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class AirAttackWiringContractTests(unittest.TestCase):
    def test_air_fields_wired_by_default_and_asserted_to_load(self):
        # Owner 2026-11-07: the ER clips are wired in by default (was: empty-default assertions).
        header = (ROOT / "Source/OneBossFight/Player/RPGDodgeTiming.h").read_text(encoding="utf-8-sig")
        source = (ROOT / "Source/OneBossFight/Player/RPGDodgeTiming.cpp").read_text(encoding="utf-8-sig")
        tests = (ROOT / "Source/OneBossFight/Tests/RPGAutomationTests.cpp").read_text(encoding="utf-8-sig")
        self.assertIn("TSoftObjectPtr<UAnimMontage> AirLightMontage;", header)
        self.assertIn("TSoftObjectPtr<UAnimMontage> AirHeavyMontage;", header)
        self.assertIn("/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Light.AM_ER_Attack_Air_Light", source)
        self.assertIn("/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Heavy_Plunge.AM_ER_Attack_Air_Heavy_Plunge", source)
        self.assertIn("ER air-light montage loads", tests)
        self.assertIn("ER air-heavy montage loads", tests)

    def test_light_and_heavy_routes_mutate_only_their_pack_arrays(self):
        source = (ROOT / "Source/OneBossFight/Player/RPGDodgeTiming.cpp").read_text(encoding="utf-8-sig")
        light = source.split("void URPGDodgeTiming::OnEldenRingLight", 1)[1].split("void URPGDodgeTiming::OnEldenRingHeavyTap", 1)[0]
        heavy = source.split("void URPGDodgeTiming::OnEldenRingHeavyTap", 1)[1].split("void URPGDodgeTiming::NotifySuccessfulGuardContact", 1)[0]
        self.assertIn('TEXT("FallingAttackMontages")', light)
        self.assertIn('TEXT("StrongAttackMontages")', heavy)
        self.assertIn("RPGAirAttackRules::Select", light)
        self.assertIn("RPGAirAttackRules::Select", heavy)
        self.assertIn("InjectLightUntil = Now + InjectSeconds", light)
        self.assertIn("InjectStrongUntil = Now + InjectSeconds", heavy)

    def test_override_saves_and_restores_the_selected_array(self):
        source = (ROOT / "Source/OneBossFight/Player/RPGDodgeTiming.cpp").read_text(encoding="utf-8-sig")
        self.assertIn("Backup.PropertyName = ArrayName", source)
        self.assertIn("MontageArray->ExportTextItem_Direct", source)
        self.assertIn("FindFProperty<FArrayProperty>(Ability->GetClass(), Backup.PropertyName)", source)
        self.assertIn("MontageArray->ImportText_Direct", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
