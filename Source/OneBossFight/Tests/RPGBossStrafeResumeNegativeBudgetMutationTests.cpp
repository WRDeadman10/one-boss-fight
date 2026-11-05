// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossStrafeResumeRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossStrafeResumeNegativeBudgetMutationTest,
    "OneBossFight.Framework.StrafeResume.NegativeBudgetMutation",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FBossStrafeResumeNegativeBudgetMutationTest::RunTest(const FString&)
{
    TestFalse(TEXT("a finite negative remaining budget cannot restart strafe"),
        RPGBossStrafeResume::ShouldRestart(true, false, -.1));
    return true;
}
#endif
