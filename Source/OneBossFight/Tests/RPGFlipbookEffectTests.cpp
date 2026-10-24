// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Player/RPGFlipbookEffect.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGFlipbookRulesTest, "OneBossFight.Presentation.FlipbookRules", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FRPGFlipbookRulesTest::RunTest(const FString& Parameters)
{
	const RPGFlipbookRules::FSample Start = RPGFlipbookRules::Sample(0.f, 0.6f);
	TestEqual(TEXT("first sample is frame zero"), Start.Frame, 0);
	TestFalse(TEXT("first sample is live"), Start.bFinished);

	const RPGFlipbookRules::FSample Middle = RPGFlipbookRules::Sample(0.3f, 0.6f);
	TestEqual(TEXT("middle sample is frame 31"), Middle.Frame, 31);
	TestFalse(TEXT("middle sample is live"), Middle.bFinished);

	const RPGFlipbookRules::FSample End = RPGFlipbookRules::Sample(0.6f, 0.6f);
	TestEqual(TEXT("terminal sample is frame 63"), End.Frame, 63);
	TestTrue(TEXT("terminal sample finishes"), End.bFinished);

	const RPGFlipbookRules::FSample ZeroDuration = RPGFlipbookRules::Sample(0.f, 0.f);
	TestEqual(TEXT("zero duration clamps frame 63"), ZeroDuration.Frame, 63);
	TestTrue(TEXT("zero duration finishes"), ZeroDuration.bFinished);
	return true;
}

#endif
