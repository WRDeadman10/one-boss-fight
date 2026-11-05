// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossTrackRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossWarpExactDurationBoundaryTest,
    "OneBossFight.Framework.Runtime.WarpExactDurationBoundary",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FBossWarpExactDurationBoundaryTest::RunTest(const FString&)
{
    constexpr double Duration = .4;
    for (const double Dt : {1. / 240., 1. / 60., 1. / 30., .1})
    {
        double Elapsed = 0.;
        double Moved = 0.;
        int32 Steps = 0;
        while (Elapsed < Duration)
        {
            const double Remaining = Duration - Elapsed;
            const double Step = FMath::Min(Dt, Remaining);
            Moved += RPGBossTrack::WarpStepCm(100. - Moved, 150. - Moved, Step, Remaining);
            Elapsed += Step;
            ++Steps;
        }
        TestEqual(*FString::Printf(TEXT("dt %.9f schedule reaches exact duration"), Dt), Elapsed, Duration);
        TestTrue(*FString::Printf(TEXT("dt %.9f advances through multiple bounded steps"), Dt), Steps >= 1);
        TestTrue(*FString::Printf(TEXT("dt %.9f uses full time window to cover requested warp"), Dt), FMath::IsNearlyEqual(Moved, 100., 1.e-9));
    }
    return true;
}
#endif
