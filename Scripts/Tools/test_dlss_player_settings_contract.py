import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class DLSSPlayerSettingsContractTests(unittest.TestCase):
    def test_user_settings_are_registered_and_default_to_tsr(self):
        config = (ROOT / "Config/DefaultEngine.ini").read_text(encoding="utf-8-sig")
        header = (ROOT / "Source/OneBossFight/Player/RPGDLSSGameUserSettings.h").read_text(encoding="utf-8-sig")
        self.assertIn("GameUserSettingsClassName=/Script/OneBossFight.RPGDLSSGameUserSettings", config)
        self.assertIn("UPROPERTY(Config, BlueprintReadOnly", header)
        self.assertIn("DLSSPlayerMode = ERPGDLSSPlayerMode::Off", header)

    def test_setting_persists_and_applies_supported_modes(self):
        source = (ROOT / "Source/OneBossFight/Player/RPGDLSSGameUserSettings.cpp").read_text(encoding="utf-8-sig")
        self.assertIn("ApplyDLSSPlayerMode();\n\tSaveSettings();", source)
        self.assertIn("UDLSSLibrary::IsDLSSSupported()", source)
        self.assertIn("UDLSSLibrary::IsDLSSModeSupported(Requested)", source)
        for mode in ("DLAA", "Quality", "Balanced", "Performance"):
            self.assertIn(f"UDLSSMode::{mode}", source)

    def test_unsupported_or_off_uses_tsr_without_console_commands(self):
        source = (ROOT / "Source/OneBossFight/Player/RPGDLSSGameUserSettings.cpp").read_text(encoding="utf-8-sig")
        self.assertIn("Resolve(ToRulesMode(DLSSPlayerMode), bRequestedSupported)", source)
        self.assertIn('FindConsoleVariable(TEXT("r.AntiAliasingMethod"))', source)
        self.assertIn("AntiAliasing->Set(2, ECVF_SetByGameSetting)", source)
        self.assertNotIn("ExecuteConsoleCommand", source)
        self.assertNotIn("ConsoleCommand", source)

    def test_unsupported_fallback_does_not_overwrite_saved_preference(self):
        source = (ROOT / "Source/OneBossFight/Player/RPGDLSSGameUserSettings.cpp").read_text(encoding="utf-8-sig")
        fallback = source.split("if (RuntimeMode == RPGDLSSPlayerSettingsRules::ERuntimeMode::TSR)", 1)[1].split("\n\t}", 1)[0]
        self.assertIn("UDLSSLibrary::SetDLSSMode(nullptr, UDLSSMode::Off)", fallback)
        self.assertIn("SelectTSRFallback();", fallback)
        self.assertNotIn("DLSSPlayerMode =", fallback)


if __name__ == "__main__":
    unittest.main(verbosity=2)
