// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossStaggerResistRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossStaggerResistUnknownPhaseMutationTest,
    "OneBossFight.Framework.StaggerResist.UnknownPhaseMutation",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FBossStaggerResistUnknownPhaseMutationTest::RunTest(const FString&)
{
    TestEqual(TEXT("phase zero is unknown and uses the neutral scale"),
        RPGBossStaggerResist::Scale(0, .8, 1.6), 1.);
    return true;
}
#endif
