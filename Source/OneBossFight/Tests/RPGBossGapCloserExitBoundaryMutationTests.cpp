// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossGapCloserRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossGapCloserExitBoundaryMutationTest,
    "OneBossFight.Framework.GapCloser.ExitBoundaryMutation",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FBossGapCloserExitBoundaryMutationTest::RunTest(const FString&)
{
    TestFalse(TEXT("a new chase does not start exactly at the strict exit boundary"),
        RPGBossGapCloser::ShouldClose(false, 600., 250., 600.));
    TestTrue(TEXT("a new chase starts immediately beyond the exit boundary"),
        RPGBossGapCloser::ShouldClose(false, 600.001, 250., 600.));
    return true;
}
#endif
