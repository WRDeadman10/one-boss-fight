from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class Tier1VisualWiringContractTests(unittest.TestCase):
    def test_both_event_paths_have_one_opt_in_spawn_call(self) -> None:
        wave = (ROOT / "Source/OneBossFight/Player/RPGBossShockwave.cpp").read_text(encoding="utf-8")
        parry = (ROOT / "Source/OneBossFight/Player/RPGPlayerParry.cpp").read_text(encoding="utf-8")
        wave_launch = wave.split("void URPGBossShockwave::Launch()", 1)[1].split("void URPGBossShockwave::Stop", 1)[0]
        parry_notify = parry.split("void URPGPlayerParry::NotifyParried(AActor* Actor)", 1)[1].split("void URPGPlayerParry::FinishStaminaCost", 1)[0]
        self.assertEqual(wave_launch.count("SpawnConfiguredEffect("), 1)
        self.assertEqual(parry_notify.count("SpawnConfiguredEffect("), 1)
        self.assertIn("++Tier1VisualSpawnCount", wave_launch)
        self.assertIn("++Parry->Tier1VisualSpawnCount", parry_notify)

    def test_preview_cvar_is_development_only_and_default_off(self) -> None:
        rules = (ROOT / "Source/OneBossFight/Player/RPGTier1VisualRules.cpp").read_text(encoding="utf-8")
        self.assertEqual(rules.count("#if UE_BUILD_DEVELOPMENT"), 2)
        self.assertIn('TEXT("rpg.Art.Tier1"), 0', rules)
        self.assertIn("#else\n\treturn false;", rules)

    def test_asset_overrides_and_default_empty_properties_are_optional(self) -> None:
        wave = (ROOT / "Source/OneBossFight/Player/RPGBossShockwave.h").read_text(encoding="utf-8")
        parry = (ROOT / "Source/OneBossFight/Player/RPGPlayerParry.h").read_text(encoding="utf-8")
        self.assertIn("TSoftObjectPtr<UNiagaraSystem> ShockwaveVFX;", wave)
        self.assertIn("TSoftObjectPtr<class UNiagaraSystem> ParrySparkVFX;", parry)
        self.assertNotIn("ShockwaveVFX =", wave)
        self.assertNotIn("ParrySparkVFX =", parry)

    def test_native_fixture_covers_default_fallback_and_authored_priority(self) -> None:
        tests = (ROOT / "Source/OneBossFight/Tests/RPGTier1VisualRulesTests.cpp").read_text(encoding="utf-8")
        self.assertIn('"OneBossFight.Art.Tier1Visual.SelectionAndDefaults"', tests)
        self.assertIn("SelectEffect(Empty, Tier1Path, false).IsNull()", tests)
        self.assertIn("SelectEffect(Empty, Tier1Path, true)", tests)
        self.assertIn("SelectEffect(Authored, Tier1Path, false)", tests)
        self.assertIn("#if !UE_BUILD_DEVELOPMENT", tests)


if __name__ == "__main__":
    unittest.main()
