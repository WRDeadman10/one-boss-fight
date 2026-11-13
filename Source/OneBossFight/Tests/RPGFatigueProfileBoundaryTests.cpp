// Copyright One Boss Fight. All Rights Reserved.
// BQ-61..64 (Queue BQ batch 13; QUEUE_200 Q21-Q25 gap): ValidateProfile's fatigue rule (RPGBossFrameworkProfile.cpp, the
// "Framework.Profile.Fatigue" refusal) has more boundaries than OneBossFight.Framework.Runtime.FatigueProfile pins: grace
// upper bound 100 (101 refused), a NaN floor, the inclusive floor 1.0, and grace 0 with an enabled floor. This adds them,
// reusing the runtime test fixture (FrameworkRuntimeFixture::Fill, defined in RPGFrameworkRuntimeTests.cpp). Written, not compiled/run.
#include "Player/RPGBossFrameworkProfile.h"
#include "Misc/AutomationTest.h"
#include "UObject/StrongObjectPtr.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
namespace FrameworkRuntimeFixture { void Fill(URPGBossFrameworkProfile& P); }

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFatigueProfileBoundaryTest, "OneBossFight.Framework.Runtime.FatigueProfileBoundaries", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FFatigueProfileBoundaryTest::RunTest(const FString&)
{
	using namespace FrameworkRuntimeFixture;
	TStrongObjectPtr<URPGBossFrameworkProfile> P(NewObject<URPGBossFrameworkProfile>());
	FString Error;
	// The same F5 setup as FFrameworkFatigueProfile (fatigue is only legal on an F5 profile).
	auto F5 = [&P]()
	{
		Fill(*P); P->FixtureLabel = TEXT("F5 fixture"); P->bDamageEnabled = true; P->HitStepCm = 15.f; P->HitMaxSubsteps = 8;
		P->RepeatPenalty = .2f; P->RepeatMemory = 2; P->AttackCount = 2;
		FRPGBossProfileCard C; C.Card = P->Card; C.CooldownSeconds = 1.f; C.Weight = 1.f; P->Card.Reset(); P->Cards.Reset(); P->Cards.Add(C);
	};
	const FString Token(TEXT("Framework.Profile.Fatigue"));

	F5(); P->FatigueGraceWhiffs = 100; P->FatigueFloor = .7f;
	TestTrue(TEXT("grace 100 is the inclusive upper bound"), RPGFramework::ValidateProfile(*P, Error));
	F5(); P->FatigueGraceWhiffs = 101; P->FatigueFloor = .7f;
	TestFalse(TEXT("grace 101 is refused"), RPGFramework::ValidateProfile(*P, Error)); TestEqual(TEXT("token at 101"), Error, Token);
	F5(); P->FatigueGraceWhiffs = 2; P->FatigueFloor = std::numeric_limits<float>::quiet_NaN();
	TestFalse(TEXT("NaN floor is refused"), RPGFramework::ValidateProfile(*P, Error)); TestEqual(TEXT("token for NaN"), Error, Token);
	F5(); P->FatigueGraceWhiffs = 2; P->FatigueFloor = std::numeric_limits<float>::infinity();
	TestFalse(TEXT("infinite floor is refused"), RPGFramework::ValidateProfile(*P, Error)); TestEqual(TEXT("token for inf"), Error, Token);
	F5(); P->FatigueGraceWhiffs = 2; P->FatigueFloor = 1.f;
	TestTrue(TEXT("floor 1.0 is the inclusive upper bound (fatigue enabled but never slows)"), RPGFramework::ValidateProfile(*P, Error));
	F5(); P->FatigueGraceWhiffs = 0; P->FatigueFloor = .7f;
	TestTrue(TEXT("grace 0 with a floor is valid (fatigue from the first whiff)"), RPGFramework::ValidateProfile(*P, Error));
	F5(); P->FatigueGraceWhiffs = 0; P->FatigueFloor = -0.1f;
	TestFalse(TEXT("negative floor is refused"), RPGFramework::ValidateProfile(*P, Error)); TestEqual(TEXT("token for negative"), Error, Token);
	return true;
}
#endif
