// Copyright One Boss Fight. All Rights Reserved.
// BQ-14 (Queue BQ batch 3; KI-059 characterization): pins the two dodge decisions URPGDodgeTiming makes in C++, extracted verbatim into
// pure seams (behaviour unchanged): "no direction input" (input size strictly below NoInputThreshold, which selects the backward dodge
// when bBackwardWithoutInput) and "double-tap long roll" (opt-in, press gap <= DoubleTapWindow). KI-059's other symptoms (double
// stamina payment, the quick-to-full restart) live in the pack's Blueprint dodge ability and stay ENG. Written, not compiled/run.
#include "Player/RPGDodgeTiming.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDodgeDecisionTest, "OneBossFight.Dodge.DecisionSeams", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FDodgeDecisionTest::RunTest(const FString&)
{
	const float Threshold = 0.1f;  // the URPGDodgeTiming default NoInputThreshold
	TestTrue(TEXT("no stick input counts as no direction"), URPGDodgeTiming::IsNoDirectionInput(0.f, Threshold));
	TestTrue(TEXT("just below the threshold counts as no direction"), URPGDodgeTiming::IsNoDirectionInput(0.0999f, Threshold));
	TestFalse(TEXT("exactly at the threshold is a direction (strict <)"), URPGDodgeTiming::IsNoDirectionInput(0.1f, Threshold));
	TestFalse(TEXT("full stick is a direction"), URPGDodgeTiming::IsNoDirectionInput(1.f, Threshold));
	TestFalse(TEXT("NaN input size is not treated as neutral"), URPGDodgeTiming::IsNoDirectionInput(std::numeric_limits<float>::quiet_NaN(), Threshold));

	const float Window = 0.30f;  // the URPGDodgeTiming default DoubleTapWindow
	TestTrue(TEXT("a second press inside the window is a long roll"), URPGDodgeTiming::IsDoubleTapLongRoll(true, 0.2, Window));
	TestTrue(TEXT("a press exactly at the window edge is a long roll (<=)"), URPGDodgeTiming::IsDoubleTapLongRoll(true, double(Window), Window));
	TestFalse(TEXT("a press after the window is a quick dodge"), URPGDodgeTiming::IsDoubleTapLongRoll(true, 0.31, Window));
	TestFalse(TEXT("long roll off: never a long roll"), URPGDodgeTiming::IsDoubleTapLongRoll(false, 0.1, Window));
	TestFalse(TEXT("the first press (LastPressTime starts at -1e9, huge gap) is never a long roll"), URPGDodgeTiming::IsDoubleTapLongRoll(true, 1.0e9, Window));
	return true;
}
#endif
