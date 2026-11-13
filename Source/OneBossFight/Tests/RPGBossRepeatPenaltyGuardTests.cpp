// Copyright One Boss Fight. All Rights Reserved.
// BL-56 (lane BL, X-2188): RPGBossRepeatPenalty guards: RepeatCount 101 -> 0; negative/NaN BaseWeight; negative/NaN PerRepeatScale. Asserts existing behaviour only.
#include "Player/RPGBossRepeatPenaltyRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossRepeatPenaltyGuards, "OneBossFight.Framework.RepeatPenalty.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossRepeatPenaltyGuards::RunTest(const FString&)
{
    using RPGBossRepeatPenalty::Weight;
    const double NaN = std::numeric_limits<double>::quiet_NaN();

    TestEqual(TEXT("control: no repeat keeps the base weight"), Weight(10., 0), 10.);
    TestTrue(TEXT("control: two repeats give 10 * 0.7^2 = 4.9"), FMath::IsNearlyEqual(Weight(10., 2), 4.9, 1.e-9));
    TestTrue(TEXT("control: 100 repeats are still accepted (tiny, > 0)"), Weight(10., 100) > 0.);

    TestEqual(TEXT("RepeatCount 101 gives 0"), Weight(10., 101), 0.);
    // BL-86 note: a negative BaseWeight is an equivalent mutant (FMath::Clamp(-7, 0, -10) returns the 0 lower bound anyway).
    TestEqual(TEXT("negative BaseWeight gives 0 (equivalent)"), Weight(-10., 1), 0.);
    TestEqual(TEXT("NaN BaseWeight gives 0"), Weight(NaN, 1), 0.);
    TestEqual(TEXT("negative PerRepeatScale gives 0"), Weight(10., 1, -.1), 0.);
    TestEqual(TEXT("NaN PerRepeatScale gives 0"), Weight(10., 1, NaN), 0.);
    return true;
}
#endif
