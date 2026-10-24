// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"
#include "UI/RPGFlaskHudRules.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGFlaskHudFillTest, "OneBossFight.UI.FlaskFill", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FRPGFlaskHudFillTest::RunTest(const FString& Parameters)
{
	using namespace RPGFlaskHudRules;
	TestEqual(TEXT("missing maximum is unavailable"), DecideFill(10, 0), EFill::Unavailable);
	TestEqual(TEXT("negative count is unavailable"), DecideFill(-1, 10), EFill::Unavailable);
	TestEqual(TEXT("zero is empty"), DecideFill(0, 10), EFill::Empty);
	TestEqual(TEXT("one remaining is half"), DecideFill(1, 10), EFill::Half);
	TestEqual(TEXT("exactly two thirds is half"), DecideFill(6, 9), EFill::Half);
	TestEqual(TEXT("above two thirds is full"), DecideFill(7, 10), EFill::Full);
	TestEqual(TEXT("starting count is full"), DecideFill(10, 10), EFill::Full);
	return true;
}
#endif
