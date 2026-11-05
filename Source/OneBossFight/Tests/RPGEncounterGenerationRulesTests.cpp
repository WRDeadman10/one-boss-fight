// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGEncounterGenerationRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterGenerationAdvanceRules,
	"OneBossFight.Binding.EncounterLifecycle.GenerationAdvanceRules",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FRPGEncounterGenerationAdvanceRules::RunTest(const FString&)
{
	FString Error;
	TestTrue(TEXT("first broadcast generation advances from the initial value"), RPGEncounterGenerationRules::CanAdvance(1, 2, Error));
	TestTrue(TEXT("accepted advance clears prior error"), Error.IsEmpty());

	TestFalse(TEXT("duplicate generation is refused"), RPGEncounterGenerationRules::CanAdvance(2, 2, Error));
	TestEqual(TEXT("duplicate reason is stable"), Error, FString(TEXT("EncounterActivation.GenerationNotIncreasing")));
	TestFalse(TEXT("late generation is refused"), RPGEncounterGenerationRules::CanAdvance(2, 1, Error));
	TestEqual(TEXT("late reason is stable"), Error, FString(TEXT("EncounterActivation.GenerationNotIncreasing")));
	TestFalse(TEXT("zero is not a participant generation"), RPGEncounterGenerationRules::CanAdvance(0, 0, Error));
	TestEqual(TEXT("zero reason is stable"), Error, FString(TEXT("EncounterActivation.GenerationNotIncreasing")));

	TestFalse(TEXT("maximum current generation is exhausted"), RPGEncounterGenerationRules::CanAdvance(MAX_uint64, MAX_uint64, Error));
	TestEqual(TEXT("current exhaustion reason is stable"), Error, FString(TEXT("EncounterActivation.GenerationExhausted")));
	TestFalse(TEXT("maximum broadcast generation is refused"), RPGEncounterGenerationRules::CanAdvance(2, MAX_uint64, Error));
	TestEqual(TEXT("broadcast exhaustion reason is stable"), Error, FString(TEXT("EncounterActivation.GenerationExhausted")));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterGenerationSequenceProperty,
	"OneBossFight.Binding.EncounterLifecycle.GenerationSequenceProperty",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FRPGEncounterGenerationSequenceProperty::RunTest(const FString&)
{
	FRandomStream Random(0x5EED);
	uint64 Current = 1;
	FString Error;
	for (int32 Index = 0; Index < 256; ++Index)
	{
		const uint64 Candidate = Current + static_cast<uint64>(Random.RandRange(1, 7));
		TestTrue(FString::Printf(TEXT("seeded strictly increasing generation %d is accepted"), Index),
			RPGEncounterGenerationRules::CanAdvance(Current, Candidate, Error));
		TestTrue(FString::Printf(TEXT("seeded generation %d remains monotonic and usable"), Index),
			Candidate > Current && Candidate != 0 && Candidate != MAX_uint64);
		TestTrue(FString::Printf(TEXT("seeded generation %d leaves no refusal token"), Index), Error.IsEmpty());
		Current = Candidate;
	}
	return true;
}

#endif
