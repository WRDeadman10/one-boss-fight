"""Test-first source contract for the guarded first-press activation retry."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


class FirstDodgeActivationRetryContractTests(unittest.TestCase):
    def test_retry_is_first_press_only_allowed_inactive_and_never_forced(self):
        rules = (ROOT / "Source/OneBossFight/Player/RPGDodgeActivationRules.h").read_text(encoding="utf-8")
        source = (ROOT / "Source/OneBossFight/Player/RPGDodgeTiming.cpp").read_text(encoding="utf-8-sig")
        self.assertIn("ShouldRetryFirstPress", rules)
        self.assertIn("PendingDodgeActivationRetryPress", source)
        self.assertIn('TEXT("Try Activate Ability by Class")', source)
        self.assertIn('FindPropertyByName(TEXT("InAbilityClass"))', source)
        self.assertIn('FindPropertyByName(TEXT("bForceActivation"))', source)
        self.assertIn("SetPropertyValue_InContainer(Params, false)", source)
        self.assertIn('TEXT("Add Consumed Buffer Key")', source)
        self.assertIn("buffer_consumed=%d", source)
        self.assertIn("first_dodge_activation_retry", source)

    def test_retry_pure_rule_covers_double_activation_and_blocked_cases(self):
        source = (ROOT / "Source/OneBossFight/Player/RPGDodgeActivationRules.h").read_text(encoding="utf-8")
        self.assertIn("bFirstPress && bCanActivate && !bAbilityActive && !bAlreadyAttempted", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
