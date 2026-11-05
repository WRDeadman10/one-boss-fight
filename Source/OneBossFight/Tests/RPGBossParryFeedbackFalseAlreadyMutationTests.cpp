// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossParryFeedbackRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossParryFeedbackFalseAlreadyMutationTest,
    "OneBossFight.Framework.ParryFeedback.FalseAlreadyMutation",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FBossParryFeedbackFalseAlreadyMutationTest::RunTest(const FString&)
{
    TestFalse(TEXT("a non-parry outcome never emits, even when the gate was already used"),
        RPGBossParryFeedback::ShouldEmit(false, true));
    return true;
}
#endif
