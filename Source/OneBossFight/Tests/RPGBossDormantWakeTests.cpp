// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"
#include "Player/RPGBossDormantWakeRules.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGBossDormantWakeRulesTest, "OneBossFight.Boss.DormantWakeRules", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FRPGBossDormantWakeRulesTest::RunTest(const FString& Parameters)
{
	using namespace RPGBossDormantWakeRules;
	TestFalse(TEXT("a running wake remains gated"), ShouldFinishWake(true, 3.5f, 3.5f));
	TestFalse(TEXT("a just-started missing montage has grace"), ShouldFinishWake(false, 0.1f, 3.5f));
	TestTrue(TEXT("a stopped wake after grace resumes"), ShouldFinishWake(false, 0.2f, 3.5f));
	TestTrue(TEXT("a zero-length fallback resumes after grace"), ShouldFinishWake(false, 0.15f, 0.f));
	TestFalse(TEXT("negative elapsed does not finish wake"), ShouldFinishWake(false, -0.01f, 0.f));
	TestFalse(TEXT("positive infinity elapsed does not finish wake"), ShouldFinishWake(false, std::numeric_limits<float>::infinity(), 0.f));
	TestTrue(TEXT("negative expected length clamps grace to zero"), ShouldFinishWake(false, 0.f, -1.f));
	TestFalse(TEXT("wake remains gated just before grace"), ShouldFinishWake(false, 0.149f, 3.5f));
	TestFalse(TEXT("non-finite elapsed does not finish wake"), ShouldFinishWake(false, std::numeric_limits<float>::quiet_NaN(), 3.5f));
	TestTrue(TEXT("invalid expected length uses the bounded grace"), ShouldFinishWake(false, 0.15f, std::numeric_limits<float>::quiet_NaN()));
	TestTrue(TEXT("infinite expected length uses the bounded grace"), ShouldFinishWake(false, 0.15f, std::numeric_limits<float>::infinity()));
	return true;
}
#endif
