// Copyright One Boss Fight. All Rights Reserved.
// BL-07 (lane BL, X-2164): RPGBossApproach guard clauses that no other test asserted (BL-01..05 audit). Asserts existing behaviour only.
#include "Player/RPGBossApproachRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossApproachGuards, "OneBossFight.Framework.BossApproach.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossApproachGuards::RunTest(const FString&)
{
    using namespace RPGBossApproach;
    const double NaN = std::numeric_limits<double>::quiet_NaN();

    TestEqual(TEXT("StepFraction(NaN) is 0"), StepFraction(NaN), 0.);

    TestEqual(TEXT("StepCm with T1 above 1 fails closed"), StepCm(100., 0.5, 1.0001), 0.);
    TestEqual(TEXT("StepCm with negative total fails closed"), StepCm(-100., 0., 1.), 0.);
    TestTrue(TEXT("control: StepCm valid full range"), FMath::IsNearlyEqual(StepCm(100., 0., 1.), 100., 1.e-9));

    TestEqual(TEXT("PeakSpeedCm with negative distance fails closed"), PeakSpeedCm(-100., 1.), 0.);
    TestEqual(TEXT("PeakSpeedCm with negative duration fails closed"), PeakSpeedCm(100., -1.), 0.);
    TestEqual(TEXT("control: PeakSpeedCm valid"), PeakSpeedCm(100., 1.), 150.);
    return true;
}
#endif
