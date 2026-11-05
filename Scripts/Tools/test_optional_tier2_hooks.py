from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class OptionalTier2HookTests(unittest.TestCase):
    def test_a2_tracker_preview_is_opt_in_and_does_not_replace_start_move(self) -> None:
        header = read("Source/OneBossFight/Player/RPGAttackTracker.h")
        source = read("Source/OneBossFight/Player/RPGAttackTracker.cpp")
        driver = read("Scripts/Editor/pie_authored_close_clips.py")
        self.assertIn("FString OptionalTrackerMontagePath;", header)
        self.assertIn('TEXT("rpg.AttackTracker.A2PreviewClip"), 0', source)
        self.assertIn("A2.OptionalTrackerMontagePath = TEXT(\"/Game/OneBossFight/Boss01/Animations/AM_Boss01_A2.AM_Boss01_A2\")", source)
        preview = source.split("bool URPGAttackTracker::PlayMoveMontageForTest", 1)[1].split("FString URPGAttackTracker::GetPhaseName", 1)[0]
        start = source.split("bool URPGAttackTracker::StartMove", 1)[1].split("void URPGAttackTracker::End(", 1)[0]
        self.assertIn("CVarRPGAttackTrackerA2PreviewClip.GetValueOnGameThread() != 0", preview)
        self.assertIn("RPGPresentationRules::MatchesOptionalTrackerMontagePath(Timing.OptionalTrackerMontagePath, Montage->GetPathName())", source)
        self.assertNotIn("OptionalTrackerMontagePath", start)
        self.assertIn("Timing.OptionalTrackerMontagePath", source.split("void URPGAttackTracker::UpdateTelegraph", 1)[1].split("bool URPGAttackTracker::BranchAllowedNow", 1)[0])
        self.assertIn('"A2": (1.68, 1.93, 2.11, 3.14)', driver)
        self.assertIn('os.environ.get("A2_TRACKER_PREVIEW", "0")', driver)
        self.assertIn('"rpg.AttackTracker.A2PreviewClip %d" % preview', driver)

    def test_tier_two_preview_switch_is_development_only_and_off_by_default(self) -> None:
        source = read("Source/OneBossFight/Player/RPGTier1VisualRules.cpp")
        self.assertIn("#if UE_BUILD_DEVELOPMENT", source)
        self.assertIn('TEXT("rpg.Art.Tier2"), 0', source)
        function = source.split("bool RPGTier1Visuals::IsTier2PreviewEnabled()", 1)[1].split("UNiagaraComponent*", 1)[0]
        self.assertIn("IsTier2PreviewEnabledForBuild(true, CVarTier2Art.GetValueOnGameThread())", function)
        self.assertIn("IsTier2PreviewEnabledForBuild(false, 0)", function)

    def test_parry_mpc_pulse_follows_legend_scope_restore(self) -> None:
        header = read("Source/OneBossFight/Player/RPGLegend.h")
        source = read("Source/OneBossFight/Player/RPGLegend.cpp")
        self.assertRegex(header, r"ParryFeedbackCollection\s*=\s*nullptr")
        self.assertIn('FName ParryPulseParameter = TEXT("ParryPulse")', header)
        request = source.split("bool URPGBossLegend::HandlePlayerParrySlowMotion", 1)[1].split("void URPGBossLegend::TickComponent", 1)[0]
        restore = source.split("void URPGLegendSubsystem::RestoreSlowMotion", 1)[1].split("void URPGLegendSubsystem::CancelAll", 1)[0]
        self.assertIn("Time->BeginParryFeedbackPulse(ParryFeedbackCollection, ParryPulseParameter, ParrySlowMotionSoundMix)", request)
        self.assertIn("RestoreParryFeedbackPulse();", restore)
        self.assertIn("RPGTier1Visuals::IsTier2PreviewEnabled()", source.split("void URPGLegendSubsystem::BeginParryFeedbackPulse", 1)[1].split("void URPGLegendSubsystem::RestoreHitStop", 1)[0])

    def test_parry_sound_mix_is_optional_and_popped_with_the_slow_motion_scope(self) -> None:
        header = read("Source/OneBossFight/Player/RPGLegend.h")
        source = read("Source/OneBossFight/Player/RPGLegend.cpp")
        self.assertRegex(header, r"ParrySlowMotionSoundMix\s*=\s*nullptr")
        begin = source.split("void URPGLegendSubsystem::BeginParryFeedbackPulse", 1)[1].split("void URPGLegendSubsystem::RestoreHitStop", 1)[0]
        restore = source.split("void URPGLegendSubsystem::RestoreParryFeedbackPulse", 1)[1].split("void URPGLegendSubsystem::CancelAll", 1)[0]
        self.assertIn("if (!RPGTier1Visuals::IsTier2PreviewEnabled())", begin)
        self.assertIn("PushSoundMixModifier(World, SoundMix)", begin)
        self.assertIn("PopSoundMixModifier(World, SoundMix)", restore)
        self.assertIn("RestoreParryFeedbackPulse();", source.split("void URPGLegendSubsystem::RestoreSlowMotion", 1)[1].split("void URPGLegendSubsystem::CancelAll", 1)[0])

    def test_phase_aura_and_parry_recoil_are_optional_and_cleaned_up(self) -> None:
        header = read("Source/OneBossFight/Boss/RPGSevarogDirector.h")
        source = read("Source/OneBossFight/Boss/RPGSevarogDirector.cpp")
        parry = read("Source/OneBossFight/Player/RPGPlayerParry.cpp")
        self.assertRegex(header, r"TSoftObjectPtr<UNiagaraSystem> PhaseTwoAuraEffect;")
        self.assertRegex(header, r"PhaseTwoMaterialCollection\s*=\s*nullptr")
        self.assertRegex(header, r"ParryRecoilMontage\s*=\s*nullptr")
        self.assertIn("ApplyPhaseTwoVisuals();", source.split("void URPGSevarogDirector::EnterPhaseTwo", 1)[1].split("void URPGSevarogDirector::ApplyPhaseTwoVisuals", 1)[0])
        self.assertIn("ClearPhaseTwoVisuals();", source.split("void URPGSevarogDirector::EndPlay", 1)[1].split("void URPGSevarogDirector::OnActorSpawned", 1)[0])
        self.assertIn("ClearPhaseTwoVisuals();", source.split("void URPGSevarogDirector::ResetEncounter", 1)[1].split("bool URPGSevarogDirector::TryLightning", 1)[0])
        self.assertIn("ClearPhaseTwoVisuals();", source.split("if (Current <= 0.f)", 1)[1].split("if (!bPhaseTwo", 1)[0])
        self.assertIn("RPGTier1Visuals::IsTier2PreviewEnabled()", source.split("bool URPGSevarogDirector::PlayParryRecoil", 1)[1].split("namespace", 1)[0])
        self.assertIn("Director->PlayParryRecoil();", parry)
        self.assertIn("rpg.Art.Tier2", read("Source/OneBossFight/Player/RPGTier1VisualRules.cpp"))

    def test_optional_asset_paths_have_cook_root_and_default_parity_samples_are_registered(self) -> None:
        tracker = read("Source/OneBossFight/Player/RPGAttackTracker.cpp")
        config = read("Config/DefaultGame.ini")
        nightly = read("Scripts/RunA5ParityNightly.ps1")
        plan = read("Documentation/Boss/V_C038_C039_COOK_AND_PARITY_GATES.md")
        self.assertIn('A2.OptionalTrackerMontagePath = TEXT("/Game/OneBossFight/Boss01/Animations/AM_Boss01_A2.AM_Boss01_A2")', tracker)
        self.assertIn('+DirectoriesToAlwaysCook=(Path="/Game/OneBossFight/Boss01")', config)
        block = nightly.split("$drivers = @(", 1)[1].split("\n)", 1)[0]
        drivers = [name for name in block.split("'") if name.startswith("pie_")]
        self.assertEqual(len(drivers), 31)
        for driver in ("pie_authored_close_clips", "pie_legend", "pie_phase_reset", "pie_boss_death", "pie_iframes"):
            with self.subTest(driver=driver):
                self.assertIn(driver, drivers)
                self.assertIn(f"`{driver}`", plan)


if __name__ == "__main__":
    unittest.main()
