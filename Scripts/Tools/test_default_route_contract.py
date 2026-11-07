from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class DefaultRouteContractTests(unittest.TestCase):
    def test_arena_configuration_defaults_to_data_selection_before_world_start(self) -> None:
        config = read("Config/DefaultGame.ini")
        header = read("Source/OneBossFight/Player/RPGPlayerMovesSubsystem.h")
        source = read("Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp")
        self.assertIn("bDefaultToDataStartup=True", config)
        self.assertIn('DefaultEncounterMap = TEXT("L_SevarogArena")', header)
        self.assertIn("DefaultEncounterDefinition = TEXT(", header)
        begin = source.split("void URPGPlayerMovesSubsystem::OnWorldBeginPlay", 1)[1].split("void URPGPlayerMovesSubsystem::Deinitialize", 1)[0]
        self.assertIn("ApplyDefaultDataSelection()", begin)
        self.assertIn('LastEncounterRoute = bSelectionRequested ? TEXT("data")', begin)
        self.assertIn('DefaultEncounterDefinition = TEXT("/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter")', header)

    def test_legacy_parity_overrides_are_development_only_and_setter_remains_shipping_api(self) -> None:
        moves = read("Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp")
        selection = read("Source/OneBossFight/Player/RPGEncounterSelectionSubsystem.cpp")
        apply_default = moves.split("void URPGPlayerMovesSubsystem::ApplyDefaultDataSelection", 1)[1]
        legacy_override = apply_default.split("#if !UE_BUILD_SHIPPING", 1)[1].split("#endif", 1)[0]
        self.assertIn('TEXT("RPGLegacyStartup")', legacy_override)
        self.assertIn('TEXT("RPG_LEGACY_STARTUP")', legacy_override)
        selector = selection.split("#if !UE_BUILD_SHIPPING", 1)[1].split("#endif", 1)[0]
        self.assertIn('TEXT("rpg.EncounterDefinition")', selector)
        setter = selection.split("void URPGEncounterSelectionSubsystem::SetSelectedDefinition", 1)[1].split("void URPGEncounterSelectionSubsystem::ClearSelectedDefinition", 1)[0]
        self.assertIn("SelectedDefinition = Definition", setter)

    def test_explicit_data_route_failure_does_not_fall_through_to_legacy_attach(self) -> None:
        source = read("Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp")
        startup = source.split("if (bSelectionRequested)", 1)[1].split("if (!bUseLegacyStartup)", 1)[0]
        self.assertIn('LastEncounterOutcome = TEXT("HardError")', startup)
        self.assertIn("AttachSelectedPlayerComponents", startup)
        self.assertNotRegex(startup, r"\bAttach\(\*It\)")

    def test_native_regression_cases_cover_data_default_and_legacy_control(self) -> None:
        tests = read("Source/OneBossFight/Tests/RPGBossStartupActivationTests.cpp")
        self.assertIn("OneBossFight.Binding.EncounterSelection.DefaultDataStartup", tests)
        self.assertIn("OneBossFight.Binding.EncounterSelection.AbsentPreservesLegacyStartup", tests)
        self.assertIn("OneBossFight.Binding.EncounterSelection.LegacyStartupConfigOff", tests)

    def test_optional_er_animation_assets_have_an_explicit_cook_root(self) -> None:
        config = read("Config/DefaultGame.ini")
        self.assertIn('+DirectoriesToAlwaysCook=(Path="/Game/OneBossFight/Player/Animations")', config)
        self.assertIn('+DirectoriesToAlwaysCook=(Path="/Game/OneBossFight/VFX")', config)
        self.assertIn('+DirectoriesToAlwaysCook=(Path="/Game/OneBossFight/Boss")', config)


if __name__ == "__main__":
    unittest.main()
