"""Offline source guards for BK-26/27 diagnostics and BK-28/29 tag fencing."""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
SELECTOR = (ROOT / "Source/OneBossFight/Player/RPGEncounterSelectionSubsystem.cpp").read_text(encoding="utf-8")
SELECTOR_H = (ROOT / "Source/OneBossFight/Player/RPGEncounterSelectionSubsystem.h").read_text(encoding="utf-8")
CLEANUP = (ROOT / "Source/OneBossFight/Pack/RPGOwnedTagCleanup.h").read_text(encoding="utf-8")
IFRAME = (ROOT / "Source/OneBossFight/Player/RPGIFrameMonitor.cpp").read_text(encoding="utf-8")
PARRY = (ROOT / "Source/OneBossFight/Player/RPGPlayerParry.cpp").read_text(encoding="utf-8")
NATIVE_TEST = (ROOT / "Source/OneBossFight/Tests/RPGGenerationResetRegressionTests.cpp").read_text(encoding="utf-8")


class BK45SourceContracts(unittest.TestCase):
    def test_diagnostic_getter_and_writer_share_a_lock(self):
        self.assertIn("mutable FCriticalSection SelectionDiagnosticMutex", SELECTOR_H)
        self.assertIn("FScopeLock Lock(&SelectionDiagnosticMutex);", SELECTOR)
        self.assertIn("FString URPGEncounterSelectionSubsystem::GetSelectionDiagnostic() const", SELECTOR)
        self.assertIn("void URPGEncounterSelectionSubsystem::RecordSelectionDiagnostic", SELECTOR)

    def test_early_selection_refusals_publish_the_current_error(self):
        for token in ("EncounterSelection.NotGameThread", "EncounterSelection.WorldState",
                      "EncounterActivation.GenerationExhausted", "EncounterActivation.ResetCountInvalid",
                      "EncounterActivation.GenerationMismatch"):
            block = SELECTOR[SELECTOR.index(token):SELECTOR.index(token) + 300]
            self.assertIn("RecordSelectionDiagnostic(OutError)", block, token)
        self.assertIn("off-thread refusal replaces the old diagnostic safely", (ROOT / "Source/OneBossFight/Tests/RPGBossStartupActivationTests.cpp").read_text(encoding="utf-8"))

    def test_retry_callback_checks_actor_and_generation_before_removal(self):
        self.assertIn("MayRemoveForGeneration(Owner, Owner, ExpectedGeneration, Current)", CLEANUP)
        self.assertLess(CLEANUP.index("MayRemoveForGeneration(Owner, Owner"), CLEANUP.index("const bool bCalled = RemoveOwnedTag(Owner, Tag)"))
        self.assertIn("CreateLambda([WeakOwner, Tag, Source, ExpectedGeneration, Attempt]()", CLEANUP)
        self.assertIn("RetryUntilRemovalIssued(WeakOwner, Tag, Source, ExpectedGeneration, Attempt + 1)", CLEANUP)

    def test_components_capture_the_generation_that_owned_the_tag(self):
        self.assertIn("OwnedTagGeneration = bOwnedNow ? RPGOwnedTagCleanup::CurrentGeneration(GetOwner()) : 0", IFRAME)
        self.assertIn("RPGPlayerParry.EndPlay\"), OwnedTagGeneration", PARRY)
        self.assertIn("OwnedTagGeneration = RPGOwnedTagCleanup::CurrentGeneration(GetOwner())", PARRY)

    def test_same_actor_old_generation_regression_is_authored(self):
        self.assertIn("PriorGenerationCannotRemoveCurrentTag", NATIVE_TEST)
        self.assertIn("MayRemoveForGeneration(Owner, Owner, 7, 8)", NATIVE_TEST)


if __name__ == "__main__":
    unittest.main()
