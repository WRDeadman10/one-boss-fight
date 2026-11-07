import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class GuardCounterWiringContractTests(unittest.TestCase):
    def test_optional_montage_and_successful_contact_source(self):
        header = (ROOT / "Source/OneBossFight/Player/RPGDodgeTiming.h").read_text(encoding="utf-8-sig")
        executor = (ROOT / "Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp").read_text(encoding="utf-8-sig")
        self.assertIn("TSoftObjectPtr<UAnimMontage> GuardCounterMontage;", header)
        self.assertIn("void NotifySuccessfulGuardContact();", header)
        self.assertGreaterEqual(executor.count("Timing->NotifySuccessfulGuardContact()"), 2)
        for contact in re.findall(r"if \(Result\.Outcome==ERPGDamageOutcome::Accepted\).*?\n", executor):
            if "NotifySuccessfulGuardContact" in contact:
                self.assertIn("Guard==RPGBossGuard::EGuardState::Guarded", contact)

    def test_r2_requires_counter_window_and_retains_pack_attack_fallback(self):
        source = (ROOT / "Source/OneBossFight/Player/RPGDodgeTiming.cpp").read_text(encoding="utf-8-sig")
        self.assertIn("RPGGuardCounterRules::IsCounterPress(LastSuccessfulGuardTime, Now, GuardCounterWindowSeconds)", source)
        self.assertIn("LastSuccessfulGuardTime = -1.0e9", source)
        self.assertIn("InjectStrongUntil = Now + InjectSeconds", source)
        self.assertIn("StrongAttackMontages", source)
        self.assertIn("ImportText_Direct", source)

    def test_end_play_restores_temporary_arrays_and_invalidates_window(self):
        header = (ROOT / "Source/OneBossFight/Player/RPGDodgeTiming.h").read_text(encoding="utf-8-sig")
        source = (ROOT / "Source/OneBossFight/Player/RPGDodgeTiming.cpp").read_text(encoding="utf-8-sig")
        self.assertIn("virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;", header)
        end_play = re.search(r"void URPGDodgeTiming::EndPlay\(.*?\n\}", source, re.S)
        self.assertIsNotNone(end_play)
        body = end_play.group(0)
        self.assertIn("RestoreGuardCounterMontageOverride();", body)
        self.assertIn("LastSuccessfulGuardTime = -1.0e9;", body)
        self.assertIn("Super::EndPlay(EndPlayReason);", body)


if __name__ == "__main__":
    unittest.main(verbosity=2)
