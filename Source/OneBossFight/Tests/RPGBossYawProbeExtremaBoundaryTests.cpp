// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossYawProbeRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossYawProbeExtremaBoundaryTest,
    "OneBossFight.Framework.BossYawProbe.ExtremaBoundary",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FBossYawProbeExtremaBoundaryTest::RunTest(const FString&)
{
    constexpr double Center = -15.;
    constexpr double Amplitude = 7.;
    constexpr int32 Period = 24;
    TestTrue(TEXT("quarter-cycle sample reaches upper configured extreme"),
        FMath::IsNearlyEqual(RPGBossYawProbe::YawAt(Period / 4, Center, Amplitude, Period), Center + Amplitude, 1.e-12));
    TestTrue(TEXT("three-quarter-cycle sample reaches lower configured extreme"),
        FMath::IsNearlyEqual(RPGBossYawProbe::YawAt(3 * Period / 4, Center, Amplitude, Period), Center - Amplitude, 1.e-12));
    TestEqual(TEXT("periodic extrema repeat at the next cycle"),
        RPGBossYawProbe::YawAt(Period / 4 + Period, Center, Amplitude, Period),
        RPGBossYawProbe::YawAt(Period / 4, Center, Amplitude, Period));
    return true;
}
#endif
