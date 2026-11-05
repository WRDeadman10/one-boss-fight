from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class LegacyStartupConfigTests(unittest.TestCase):
    def test_single_game_config_key_defaults_legacy_startup_on(self):
        config = (ROOT / "Config/DefaultGame.ini").read_text(encoding="utf-8")
        section = "[/Script/OneBossFight.RPGPlayerMovesSubsystem]"
        self.assertEqual(config.count(section), 1)
        body = config.split(section, 1)[1].split("\n[", 1)[0]
        self.assertEqual(body.count("bUseLegacyStartup="), 1)
        self.assertIn("bUseLegacyStartup=True", body)

    def test_config_switch_gates_only_unselected_legacy_attach_path(self):
        source = (ROOT / "Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp").read_text(encoding="utf-8")
        header = (ROOT / "Source/OneBossFight/Player/RPGPlayerMovesSubsystem.h").read_text(encoding="utf-8")
        self.assertIn("UPROPERTY(Config, EditDefaultsOnly", header)
        self.assertIn("bool bUseLegacyStartup = true;", header)
        self.assertIn("if (!bUseLegacyStartup)", source)
        self.assertIn("bSelectionRequested ? TEXT(\"data\")", source)
        self.assertIn("if (bSelectionRequested)", source)


if __name__ == "__main__":
    unittest.main()
