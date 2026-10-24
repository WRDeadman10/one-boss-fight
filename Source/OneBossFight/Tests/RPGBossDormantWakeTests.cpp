// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"
#include "Player/RPGBossDormantWakeRules.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGBossDormantWakeRulesTest, "OneBossFight.Boss.DormantWakeRules", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FRPGBossDormantWakeRulesTest::RunTest(const FString& Parameters)
{
	using namespace RPGBossDormantWakeRules;
	TestFalse(TEXT("a running wake remains gated"), ShouldFinishWake(true, 3.5f, 3.5f));
	TestFalse(TEXT("a just-started missing montage has grace"), ShouldFinishWake(false, 0.1f, 3.5f));
	TestTrue(TEXT("a stopped wake after grace resumes"), ShouldFinishWake(false, 0.2f, 3.5f));
	TestTrue(TEXT("a zero-length fallback resumes after grace"), ShouldFinishWake(false, 0.15f, 0.f));
	return true;
}
#endif
