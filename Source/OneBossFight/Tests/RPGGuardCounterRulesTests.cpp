// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Player/RPGGuardCounterRules.h"

#include <limits>

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGGuardCounterRulesTest, "OneBossFight.Player.GuardCounterRules",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGGuardCounterRulesTest::RunTest(const FString& Parameters)
{
	(void)Parameters;
	using namespace RPGGuardCounterRules;
	const double NaN = std::numeric_limits<double>::quiet_NaN();
	const double Inf = std::numeric_limits<double>::infinity();

	TestTrue(TEXT("counter press exactly at the block is valid"), IsCounterPress(4.0, 4.0, 0.60));
	TestTrue(TEXT("counter press at the inclusive window end is valid"), IsCounterPress(4.0, 4.60, 0.60));
	TestFalse(TEXT("counter press after the window is rejected"), IsCounterPress(4.0, 4.600001, 0.60));
	TestFalse(TEXT("press before block is rejected"), IsCounterPress(4.0, 3.99, 0.60));
	TestFalse(TEXT("nonpositive counter window is rejected"), IsCounterPress(4.0, 4.0, 0.0));
	TestFalse(TEXT("negative counter window is rejected"), IsCounterPress(4.0, 4.0, -0.1));
	TestFalse(TEXT("NaN block timestamp is rejected"), IsCounterPress(NaN, 4.0, 0.60));
	TestFalse(TEXT("NaN press timestamp is rejected"), IsCounterPress(4.0, NaN, 0.60));
	TestFalse(TEXT("infinite block timestamp is rejected"), IsCounterPress(Inf, 4.0, 0.60));
	TestFalse(TEXT("infinite press timestamp is rejected"), IsCounterPress(4.0, Inf, 0.60));
	TestFalse(TEXT("NaN counter window is rejected"), IsCounterPress(4.0, 4.0, NaN));
	TestFalse(TEXT("infinite window is rejected"), IsCounterPress(4.0, 4.0, Inf));
	TestFalse(TEXT("no-block state cannot counter: its absent-block timestamp is outside the window"), IsCounterPress(-1.0e9, 4.0, 0.60));

	TestEqual(TEXT("armed strong-kind hit uses the configured scale"), PostureScale(true, true, 2.0), 2.0);
	TestEqual(TEXT("no block means no armed posture bonus"), PostureScale(false, true, 2.0), 1.0);
	TestEqual(TEXT("armed non-strong hit receives no bonus"), PostureScale(true, false, 2.0), 1.0);
	TestEqual(TEXT("unit multiplier is valid"), PostureScale(true, true, 1.0), 1.0);
	TestEqual(TEXT("sub-unit multiplier fails closed"), PostureScale(true, true, 0.99), 1.0);
	TestEqual(TEXT("negative multiplier fails closed"), PostureScale(true, true, -2.0), 1.0);
	TestEqual(TEXT("NaN multiplier fails closed"), PostureScale(true, true, NaN), 1.0);
	TestEqual(TEXT("infinite multiplier fails closed"), PostureScale(true, true, Inf), 1.0);

	TestTrue(TEXT("arm is valid at its start"), IsArmed(10.0, 10.0, 1.20));
	TestTrue(TEXT("arm is valid at the inclusive lifetime end"), IsArmed(10.0, 11.20, 1.20));
	TestFalse(TEXT("arm expires after its lifetime"), IsArmed(10.0, 11.200001, 1.20));
	TestFalse(TEXT("arm is invalid before its start"), IsArmed(10.0, 9.99, 1.20));
	TestFalse(TEXT("nonpositive armed lifetime is rejected"), IsArmed(10.0, 10.0, 0.0));
	TestFalse(TEXT("negative armed lifetime is rejected"), IsArmed(10.0, 10.0, -1.0));
	TestFalse(TEXT("NaN current time is rejected"), IsArmed(10.0, NaN, 1.20));
	TestFalse(TEXT("NaN armed timestamp is rejected"), IsArmed(NaN, 10.0, 1.20));
	TestFalse(TEXT("infinite current time is rejected"), IsArmed(10.0, Inf, 1.20));
	TestFalse(TEXT("infinite armed timestamp is rejected"), IsArmed(Inf, 10.0, 1.20));
	TestFalse(TEXT("NaN armed lifetime is rejected"), IsArmed(10.0, 10.0, NaN));
	TestFalse(TEXT("infinite armed lifetime is rejected"), IsArmed(10.0, 10.0, Inf));

	return true;
}

#endif
