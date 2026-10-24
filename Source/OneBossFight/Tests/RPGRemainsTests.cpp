// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Player/RPGBossRemains.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGBossRemainsRulesTest, "OneBossFight.Boss.RemainsRules", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FRPGBossRemainsRulesTest::RunTest(const FString& Parameters)
{
	const RPGBossRemainsRules::FSample Start = RPGBossRemainsRules::Sample(0.f, 2.5f);
	TestEqual(TEXT("start is invisible"), Start.Dissolve, 0.f);
	TestFalse(TEXT("start is unfinished"), Start.bFinished);

	const RPGBossRemainsRules::FSample Middle = RPGBossRemainsRules::Sample(1.25f, 2.5f);
	TestEqual(TEXT("middle is half formed"), Middle.Dissolve, 0.5f);
	TestFalse(TEXT("middle is unfinished"), Middle.bFinished);

	const RPGBossRemainsRules::FSample End = RPGBossRemainsRules::Sample(2.5f, 2.5f);
	TestEqual(TEXT("end is whole"), End.Dissolve, 1.f);
	TestTrue(TEXT("end is finished"), End.bFinished);

	const RPGBossRemainsRules::FSample Clamped = RPGBossRemainsRules::Sample(10.f, 0.f);
	TestEqual(TEXT("late and zero duration clamp whole"), Clamped.Dissolve, 1.f);
	TestTrue(TEXT("late and zero duration finish"), Clamped.bFinished);
	return true;
}

#endif
