// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Player/RPGAirAttackRules.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGAirAttackRulesTest, "OneBossFight.Player.AirAttackRules",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGAirAttackRulesTest::RunTest(const FString& Parameters)
{
	(void)Parameters;
	using RPGAirAttackRules::EAirAttackRoute;
	using RPGAirAttackRules::Select;
	TestTrue(TEXT("grounded light keeps pack route even when optional clip exists"), Select(false, false, true) == EAirAttackRoute::Pack);
	TestTrue(TEXT("grounded heavy keeps pack route even when optional clip exists"), Select(false, true, true) == EAirAttackRoute::Pack);
	TestTrue(TEXT("airborne light uses optional route when assigned"), Select(true, false, true) == EAirAttackRoute::AirLight);
	TestTrue(TEXT("airborne heavy uses optional route when assigned"), Select(true, true, true) == EAirAttackRoute::AirHeavy);
	TestTrue(TEXT("airborne light preserves pack fallback when empty"), Select(true, false, false) == EAirAttackRoute::Pack);
	TestTrue(TEXT("airborne heavy preserves pack fallback when empty"), Select(true, true, false) == EAirAttackRoute::Pack);
	return true;
}

#endif
