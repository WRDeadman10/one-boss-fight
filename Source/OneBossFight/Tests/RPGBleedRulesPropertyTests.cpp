// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBleedRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBleedRulesPropertyTest, "OneBossFight.Framework.Bleed.SeededProperty", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBleedRulesPropertyTest::RunTest(const FString&)
{
	RPGBleedRules::FConfig Config;
	RPGBleedRules::FState State;
	State.Threshold = Config.InitialThreshold;
	FRandomStream Random(0xB1EED);
	int32 PreviousProcs = 0;
	float PreviousThreshold = State.Threshold;
	for (int32 Index = 0; Index < 10000; ++Index)
	{
		const float Amount = Random.FRandRange(-40.f, 40.f);
		RPGBleedRules::Apply(State, Config, Amount, false, false, false, false);
		TestTrue(TEXT("buildup stays finite and non-negative"), FMath::IsFinite(State.Buildup) && State.Buildup >= 0.f);
		TestTrue(TEXT("threshold stays finite, monotonic, and within its configured cap"),
			FMath::IsFinite(State.Threshold) && State.Threshold >= PreviousThreshold && State.Threshold <= Config.ThresholdMax);
		TestTrue(TEXT("proc count is monotonic and cannot exceed applied events"), State.Procs >= PreviousProcs && State.Procs <= Index + 1);
		PreviousThreshold = State.Threshold;
		PreviousProcs = State.Procs;
	}
	const float Before = State.Buildup;
	TestEqual(TEXT("NaN buildup input is ignored without poisoning state"),
		static_cast<uint8>(RPGBleedRules::Apply(State, Config, std::numeric_limits<float>::quiet_NaN(), false, false, false, false)),
		static_cast<uint8>(RPGBleedRules::EResult::IgnoredAmount));
	TestEqual(TEXT("NaN input leaves buildup unchanged"), State.Buildup, Before);
	return true;
}
#endif
