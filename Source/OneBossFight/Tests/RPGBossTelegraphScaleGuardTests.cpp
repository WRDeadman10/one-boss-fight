// Copyright One Boss Fight. All Rights Reserved.
// BL-67 (lane BL): RPGBossTelegraphScale::Rate refuses MinRateScale <= 0 or > 1 and ActiveStartSeconds <= 0.
// Observability: MinRateScale <= 0 DISCRIMINATES (without the guard the floor is <= 0 and the slowed rate would be returned). MinRateScale > 1 and
// ActiveStartSeconds <= 0 are EQUIVALENT mutants (Needed <= CurrentRate < Floor, or Needed <= 0 < Floor, already returns -1); documented.
// Asserts existing behaviour only.
#include "Player/RPGBossTelegraphScaleRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossTelegraphScaleGuards, "OneBossFight.Framework.TelegraphScale.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossTelegraphScaleGuards::RunTest(const FString&)
{
    using RPGBossTelegraphScale::Rate;

    // Control: 0.4 s to the opening needs 0.5 s real, so the rate is slowed to 0.8 (above the 0.4 floor).
    TestTrue(TEXT("control: slowed to 0.8"), FMath::IsNearlyEqual(Rate(.4, 1., .5, .4), .8, 1.e-12));

    // Discriminating: a non-positive floor scale would let the slowed rate through.
    TestEqual(TEXT("MinRateScale 0 is refused"), Rate(.4, 1., .5, 0.), -1.);
    TestEqual(TEXT("negative MinRateScale is refused"), Rate(.4, 1., .5, -.1), -1.);

    // Equivalent mutants (documented): -1 with or without the guard.
    TestEqual(TEXT("MinRateScale above 1 is refused (equivalent)"), Rate(.4, 1., .5, 1.1), -1.);
    TestEqual(TEXT("ActiveStartSeconds 0 is refused (equivalent)"), Rate(0., 1., .5, .4), -1.);
    TestEqual(TEXT("negative ActiveStartSeconds is refused (equivalent)"), Rate(-.4, 1., .5, .4), -1.);
    return true;
}
#endif
