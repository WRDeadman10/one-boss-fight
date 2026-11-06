// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Player/RPGDodgeInputRules.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGDodgeInputRulesTest, "OneBossFight.Player.DodgeInputRules",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGDodgeInputRulesTest::RunTest(const FString& Parameters)
{
	(void)Parameters;
	using RPGDodgeInputRules::DecideTap;
	using RPGDodgeInputRules::EDodgeTapDecision;

	TestTrue(TEXT("direction input keeps the roll choice even when a backstep clip is available"),
		DecideTap(true, true) == EDodgeTapDecision::Roll);
	TestTrue(TEXT("standing tap with the optional clip selects a backstep"),
		DecideTap(false, true) == EDodgeTapDecision::Backstep);
	TestTrue(TEXT("empty optional clip preserves today's standing roll"),
		DecideTap(false, false) == EDodgeTapDecision::Roll);

	for (int32 Tap = 0; Tap < 3; ++Tap)
	{
		TestTrue(*FString::Printf(TEXT("standing tap %d can choose a backstep again"), Tap + 1),
			DecideTap(false, true) == EDodgeTapDecision::Backstep);
	}

	return true;
}

#endif
