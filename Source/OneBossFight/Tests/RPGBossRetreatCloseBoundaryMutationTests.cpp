// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossRetreatRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossRetreatCloseBoundaryMutationTest,
    "OneBossFight.Framework.Retreat.CloseBoundaryMutation",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FBossRetreatCloseBoundaryMutationTest::RunTest(const FString&)
{
    TestTrue(TEXT("a threatened boss retreats just inside close range"),
        RPGBossRetreat::ShouldRetreat(149.999, 150., .8));
    TestFalse(TEXT("a threatened boss does not retreat at the strict close boundary"),
        RPGBossRetreat::ShouldRetreat(150., 150., .8));
    return true;
}
#endif
