// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Player/RPGDLSSPlayerSettingsRules.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGDLSSPlayerSettingsRulesTest, "OneBossFight.Player.DLSSPlayerSettingsRules",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGDLSSPlayerSettingsRulesTest::RunTest(const FString& Parameters)
{
	(void)Parameters;
	using namespace RPGDLSSPlayerSettingsRules;
	TestTrue(TEXT("Off selects TSR"), Resolve(EPlayerMode::Off, true) == ERuntimeMode::TSR);
	TestTrue(TEXT("unsupported DLAA falls back to TSR"), Resolve(EPlayerMode::DLAA, false) == ERuntimeMode::TSR);
	TestTrue(TEXT("unsupported Quality falls back to TSR"), Resolve(EPlayerMode::Quality, false) == ERuntimeMode::TSR);
	TestTrue(TEXT("unsupported Balanced falls back to TSR"), Resolve(EPlayerMode::Balanced, false) == ERuntimeMode::TSR);
	TestTrue(TEXT("unsupported Performance falls back to TSR"), Resolve(EPlayerMode::Performance, false) == ERuntimeMode::TSR);
	TestTrue(TEXT("supported DLAA is retained"), Resolve(EPlayerMode::DLAA, true) == ERuntimeMode::DLAA);
	TestTrue(TEXT("supported Quality is retained"), Resolve(EPlayerMode::Quality, true) == ERuntimeMode::Quality);
	TestTrue(TEXT("supported Balanced is retained"), Resolve(EPlayerMode::Balanced, true) == ERuntimeMode::Balanced);
	TestTrue(TEXT("supported Performance is retained"), Resolve(EPlayerMode::Performance, true) == ERuntimeMode::Performance);
	return true;
}

#endif
