// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossDesperationRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossDesperationFullThresholdMutationTest,
    "OneBossFight.Framework.Desperation.FullThresholdMutation",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FBossDesperationFullThresholdMutationTest::RunTest(const FString&)
{
    TestEqual(TEXT("a start threshold of one is valid and reaches maximum at zero health"),
        RPGBossDesperation::WeightMultiplier(0., 1., 1.8), 1.8);
    return true;
}
#endif
