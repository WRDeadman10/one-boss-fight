#!/usr/bin/env python3
"""Source contract for deferred owned-tag cleanup lifetime and retry policy."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
CLEANUP = (ROOT / "Source/OneBossFight/Pack/RPGOwnedTagCleanup.h").read_text(encoding="utf-8")
IFRAME = (ROOT / "Source/OneBossFight/Player/RPGIFrameMonitor.cpp").read_text(encoding="utf-8")
PARRY = (ROOT / "Source/OneBossFight/Player/RPGPlayerParry.cpp").read_text(encoding="utf-8")


class OwnedTagCleanupContract(unittest.TestCase):
    def test_invalid_and_destroying_owners_stop_before_removal_or_timer(self):
        body = CLEANUP[CLEANUP.index("inline void RetryUntilRemovalIssued"):CLEANUP.index("/** Call only after")]
        self.assertIn("AActor* Owner = WeakOwner.Get()", body)
        self.assertIn("if (!Owner || Owner->IsActorBeingDestroyed())", body)
        self.assertLess(body.index("if (!Owner || Owner->IsActorBeingDestroyed())"), body.index("RemoveOwnedTag(Owner, Tag)"))

    def test_retry_uses_weak_owner_across_timer_and_does_not_keep_actor_alive(self):
        body = CLEANUP[CLEANUP.index("inline void RetryUntilRemovalIssued"):CLEANUP.index("/** Call only after")]
        self.assertIn("FTimerDelegate::CreateLambda([WeakOwner, Tag, Source, ExpectedGeneration, Attempt]()", body)
        self.assertNotIn("[Owner", body)
        self.assertIn("RetryUntilRemovalIssued(WeakOwner, Tag, Source, ExpectedGeneration, Attempt + 1)", body)

    def test_retry_policy_stops_after_success_or_owner_loss(self):
        self.assertIn("return bOwnerAlive && !bRemovalCallSucceeded", CLEANUP)
        self.assertIn("ShouldRetry(true, bCalled)", CLEANUP)

    def test_retry_backoff_is_bounded_and_invalid_attempts_are_safe(self):
        self.assertIn("constexpr float RetryDelaySeconds(int32 Attempt)", CLEANUP)
        self.assertIn("Attempt <= 1 ? 0 : (Attempt >= 5 ? 4 : Attempt - 1)", CLEANUP)
        self.assertIn("RetryDelaySeconds(Attempt)", CLEANUP)
        self.assertIn("TPair<int32, float>(-10, .25f)", (ROOT / "Source/OneBossFight/Tests/RPGOwnedTagCleanupTests.cpp").read_text(encoding="utf-8"))

    def test_iframe_endplay_only_schedules_retry_after_removal_failure(self):
        body = IFRAME[IFRAME.index("void URPGIFrameMonitor::EndPlay"):IFRAME.index("void URPGIFrameMonitor::TickComponent")]
        self.assertIn("if (!bRemoved)", body)
        self.assertIn("ScheduleAfterRemovalFailure(GetOwner(), TEXT(\"Status.Invulnerable\")", body)

    def test_parry_endplay_retries_immediately_then_schedules_only_if_still_owned(self):
        body = PARRY[PARRY.index("void URPGPlayerParry::EndPlay"):PARRY.index("void URPGPlayerParry::SetParryTag")]
        self.assertIn("for (int32 Attempt = 0; bTagOn && Attempt < 5; ++Attempt)", body)
        self.assertIn("if (bTagOn)", body)
        self.assertIn("ScheduleAfterRemovalFailure(GetOwner(), TEXT(\"Status.ParryActive\")", body)


if __name__ == "__main__":
    unittest.main(verbosity=2)
