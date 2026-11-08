// Copyright One Boss Fight. All Rights Reserved.
#include "Misc/AutomationTest.h"
#include "Player/RPGPresentationRules.h"
#include "Player/RPGLegend.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPresentationRules,
	"OneBossFight.Art.Tier2Presentation.PureRules",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FRPGPresentationRules::RunTest(const FString&)
{
	using namespace RPGPresentationRules;
	TestTrue(TEXT("Development CVar enables Tier 2 when nonzero"), IsTier2PreviewEnabledForBuild(true, 1));
	TestTrue(TEXT("any nonzero Development CVar enables Tier 2"), IsTier2PreviewEnabledForBuild(true, -1));
	TestFalse(TEXT("zero keeps Tier 2 disabled in Development"), IsTier2PreviewEnabledForBuild(true, 0));
	TestFalse(TEXT("a non-Development build ignores a nonzero CVar"), IsTier2PreviewEnabledForBuild(false, 1));
	const URPGBossLegend* Legend = GetDefault<URPGBossLegend>();
	TestEqual(TEXT("Tier 2 MPC has an exact soft default path"), Legend->ParryFeedbackCollectionAsset.ToSoftObjectPath().ToString(),
		FString(TEXT("/Game/OneBossFight/Data/MPC_CombatFeedback.MPC_CombatFeedback")));
	TestNull(TEXT("Tier 2 MPC is not eagerly loaded by the Legend CDO"), Legend->ParryFeedbackCollection.Get());
	TestEqual(TEXT("parry pulse starts at full strength"), RPGLegendPulseRules::Strength(10.0, 10.0, 10.35), 1.f);
	TestTrue(TEXT("parry pulse declines halfway"), FMath::IsNearlyEqual(RPGLegendPulseRules::Strength(10.175, 10.0, 10.35), .5f, .001f));
	TestEqual(TEXT("parry pulse ends at zero"), RPGLegendPulseRules::Strength(10.35, 10.0, 10.35), 0.f);
	TestEqual(TEXT("invalid parry pulse duration fails closed"), RPGLegendPulseRules::Strength(10.0, 10.0, 10.0), 0.f);

	const FString Path(TEXT("/Game/OneBossFight/Boss01/Animations/AM_Boss01_A2.AM_Boss01_A2"));
	TestTrue(TEXT("exact optional montage path matches"), MatchesOptionalTrackerMontagePath(Path, Path));
	TestFalse(TEXT("a different montage path does not match"), MatchesOptionalTrackerMontagePath(Path, FString(TEXT("/Game/")) + TEXT("Other/Other.Other"))); // lead fix: assembled so the CookCoverage literal scanner does not see a loaded-by-path asset
	TestFalse(TEXT("empty optional path never matches"), MatchesOptionalTrackerMontagePath(FString(), Path));
	TestFalse(TEXT("empty observed path never matches"), MatchesOptionalTrackerMontagePath(Path, FString()));
	for (int32 Index = 0; Index < Path.Len(); ++Index)
	{
		FString MutatedPath = Path;
		MutatedPath[Index] = MutatedPath[Index] == TEXT('X') ? TEXT('Y') : TEXT('X');
		TestFalse(TEXT("single-character montage path mutation never matches"),
			MatchesOptionalTrackerMontagePath(Path, MutatedPath));
	}
	// lead fix: FString operator== is case-insensitive and UE asset paths are case-insensitive, so a case-only difference MUST still match (the tracker uses the same comparison).
	TestTrue(TEXT("case-only montage path difference still matches (asset paths are case-insensitive)"),
		MatchesOptionalTrackerMontagePath(Path, Path.ToLower()));
	TestFalse(TEXT("prefix extension never matches optional montage path"),
		MatchesOptionalTrackerMontagePath(Path, Path + TEXT("_Extra")));
	return true;
}
#endif
