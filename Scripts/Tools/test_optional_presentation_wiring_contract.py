from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def section(text: str, start: str, end: str) -> str:
    return text.split(start, 1)[1].split(end, 1)[0]


class OptionalPresentationWiringContractTests(unittest.TestCase):
    def test_new_reference_properties_remain_empty_by_default(self) -> None:
        tracker = (ROOT / "Source/OneBossFight/Player/RPGAttackTracker.h").read_text(encoding="utf-8")
        director = (ROOT / "Source/OneBossFight/Boss/RPGSevarogDirector.h").read_text(encoding="utf-8")
        legend = (ROOT / "Source/OneBossFight/Player/RPGLegend.h").read_text(encoding="utf-8")

        self.assertRegex(tracker, r"FString\s+OptionalTrackerMontagePath;")
        self.assertRegex(director, r"TSoftObjectPtr<UNiagaraSystem>\s+PhaseTwoAuraEffect;")
        for name in ("PhaseTwoMaterialCollection", "ParryRecoilMontage"):
            self.assertRegex(director, rf"TObjectPtr<[^>]+>\s+{name}\s*=\s*nullptr;")
        for name in ("ParryFeedbackCollection", "ParrySlowMotionSoundMix"):
            self.assertRegex(legend, rf"TObjectPtr<[^>]+>\s+{name}\s*=\s*nullptr;")
        self.assertRegex(legend, r"TSoftObjectPtr<UMaterialInterface>\s+ParryDistortionMaterial;")

        # The four exposed references are default-constructed (null soft references or empty FString), never assigned an asset in a constructor.
        self.assertNotRegex(tracker, r"OptionalTrackerMontagePath\s*=\s*TEXT\(")
        self.assertNotRegex(director, r"PhaseTwoAuraEffect\s*=\s*TEXT\(")

    def test_tier2_gate_is_development_only_and_uses_the_pure_rule(self) -> None:
        header = (ROOT / "Source/OneBossFight/Player/RPGTier1VisualRules.h").read_text(encoding="utf-8")
        source = (ROOT / "Source/OneBossFight/Player/RPGTier1VisualRules.cpp").read_text(encoding="utf-8")
        helper = (ROOT / "Source/OneBossFight/Player/RPGPresentationRules.h").read_text(encoding="utf-8")
        self.assertIn('#include "Player/RPGPresentationRules.h"', header)
        self.assertIn("IsTier2PreviewEnabledForBuild(true, CVarTier2Art.GetValueOnGameThread())", source)
        self.assertIn("IsTier2PreviewEnabledForBuild(false, 0)", source)
        self.assertIn("return bDevelopmentBuild && CVarValue != 0;", helper)

    def test_a2_match_uses_pure_exact_path_predicate(self) -> None:
        source = (ROOT / "Source/OneBossFight/Player/RPGAttackTracker.cpp").read_text(encoding="utf-8")
        helper = (ROOT / "Source/OneBossFight/Player/RPGPresentationRules.h").read_text(encoding="utf-8")
        self.assertIn('#include "Player/RPGPresentationRules.h"', source)
        self.assertGreaterEqual(source.count("RPGPresentationRules::MatchesOptionalTrackerMontagePath("), 2)
        self.assertIn("!OptionalPath.IsEmpty() && !ObjectPath.IsEmpty() && OptionalPath == ObjectPath", helper)

    def test_visual_state_cleanup_is_wired_to_reset_death_and_teardown(self) -> None:
        director = (ROOT / "Source/OneBossFight/Boss/RPGSevarogDirector.cpp").read_text(encoding="utf-8")
        legend = (ROOT / "Source/OneBossFight/Player/RPGLegend.cpp").read_text(encoding="utf-8")
        self.assertIn("ClearPhaseTwoVisuals();", section(director, "void URPGSevarogDirector::EndPlay", "void URPGSevarogDirector::OnActorSpawned"))
        self.assertIn("ClearPhaseTwoVisuals();", section(director, "void URPGSevarogDirector::ResetEncounter", "bool URPGSevarogDirector::TryLightning"))
        death = section(director, "if (Current <= 0.f)", "if (!bPhaseTwo")
        self.assertIn("ClearPhaseTwoVisuals();", death)
        self.assertIn('CancelAll(TEXT("world teardown"))', section(legend, "void URPGLegendSubsystem::Deinitialize", "bool URPGLegendSubsystem::CheckRequest"))
        self.assertIn("RestoreParryFeedbackPulse();", section(legend, "void URPGLegendSubsystem::RestoreSlowMotion", "void URPGLegendSubsystem::RestoreParryFeedbackPulse"))
        self.assertIn("RestoreSlowMotion(Reason);", section(legend, "void URPGLegendSubsystem::CancelAll", "bool URPGLegendSubsystem::TickEffects"))
        self.assertIn('CancelAll(TEXT("encounter reset"))', legend)


if __name__ == "__main__":
    unittest.main()
