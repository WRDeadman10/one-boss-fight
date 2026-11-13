// Copyright One Boss Fight. All Rights Reserved.
// BL-36 (lane BL, X-2177): RPGBossGuard proof-pulse guard clauses (NaN/Inf SinceFirstAttack, phase clamp at +/-FLT_MAX, large-negative phase, exact pulse
// edges) and negative CardOutcome counts treated as zero. Asserts existing behaviour only.
#include "Player/RPGBossGuardRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossGuardGuards, "OneBossFight.Framework.Guard.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossGuardGuards::RunTest(const FString&)
{
    using namespace RPGBossGuard;
    const double NaN = std::numeric_limits<double>::quiet_NaN();
    const double Inf = std::numeric_limits<double>::infinity();
    const double FltMax = double(std::numeric_limits<float>::max());

    // Control: inside the first 100 ms of the cycle the pulse is on.
    TestTrue(TEXT("control: 0.05 s into the cycle is a pulse"), IsProofParryPulse(.05, 0.));

    // Non-finite elapsed time fails closed.
    TestFalse(TEXT("NaN SinceFirstAttack"), IsProofParryPulse(NaN, 0.));
    TestFalse(TEXT("+Inf SinceFirstAttack"), IsProofParryPulse(Inf, 0.));

    // Phase clamp: a huge positive phase behaves exactly like +FLT_MAX; a huge negative phase gives a negative clock -> false.
    TestTrue(TEXT("phase 1e300 clamps to +FLT_MAX"), IsProofParryPulse(0., 1.e300) == IsProofParryPulse(0., FltMax));
    TestFalse(TEXT("phase -1e300 clamps to -FLT_MAX: negative clock is false"), IsProofParryPulse(0., -1.e300));
    TestFalse(TEXT("phase -FLT_MAX: negative clock is false"), IsProofParryPulse(10., -FltMax));
    // BL-86 correction: the three asserts above do not discriminate the clamp (the unclamped results are the same). This one does: without the clamp
    // 1.7e308 + 1.7e308 overflows to +Inf and fails closed; with it the clock is 1.7e308 + FLT_MAX (finite, a multiple of 0.5) -> pulse on.
    TestTrue(TEXT("clamp keeps a huge phase finite: pulse on"), IsProofParryPulse(1.7e308, 1.7e308));

    // Exact pulse edges: position 0.1 is excluded, and the 0.5 s period wraps back to position 0 (on).
    TestFalse(TEXT("clock exactly 0.1 is excluded"), IsProofParryPulse(.1, 0.));
    TestTrue(TEXT("clock exactly 0.5 wraps to a pulse"), IsProofParryPulse(.5, 0.));
    TestTrue(TEXT("clock 0.25 + phase 0.25 = 0.5 wraps to a pulse"), IsProofParryPulse(.25, .25));

    // CardOutcome: negative counts are treated like zero (only > 0 counts).
    TestTrue(TEXT("control: one parry wins"), CardOutcome(1, 1, 1) == ECardOutcome::Parried);
    TestTrue(TEXT("all negative counts give Whiff"), CardOutcome(-1, -1, -1) == ECardOutcome::Whiff);
    TestTrue(TEXT("negative guarded/parried with an accepted hit gives Hit"), CardOutcome(1, -5, -5) == ECardOutcome::Hit);
    TestTrue(TEXT("negative parried with a guard gives Guarded"), CardOutcome(0, 1, -3) == ECardOutcome::Guarded);
    return true;
}
#endif
