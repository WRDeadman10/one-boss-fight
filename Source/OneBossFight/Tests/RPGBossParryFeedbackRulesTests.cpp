// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossParryFeedbackRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossParryFeedbackRules,"OneBossFight.Framework.ParryFeedback.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossParryFeedbackRules::RunTest(const FString&)
{
    using namespace RPGBossParryFeedback;TestTrue(TEXT("first resolved parry emits feedback"),ShouldEmit(true,false));
    TestFalse(TEXT("non-parry outcome emits no feedback"),ShouldEmit(false,false));TestFalse(TEXT("duplicate parry feedback is suppressed"),ShouldEmit(true,true));return true;
}
#endif
