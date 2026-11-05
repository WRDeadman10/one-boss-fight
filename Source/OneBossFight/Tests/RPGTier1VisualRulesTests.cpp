// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"
#include "Player/RPGTier1VisualRules.h"

#if WITH_DEV_AUTOMATION_TESTS

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGTier1VisualSelection,
	"OneBossFight.Art.Tier1Visual.SelectionAndDefaults",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FRPGTier1VisualSelection::RunTest(const FString&)
{
	const TSoftObjectPtr<UNiagaraSystem> Empty;
	const TSoftObjectPtr<UNiagaraSystem> Authored(FSoftObjectPath(TEXT("/Game/Test/NS_Authored.NS_Authored")));
	const TCHAR* Tier1Path = TEXT("/Game/OneBossFight/VFX/NS_Boss_ShockwaveRing.NS_Boss_ShockwaveRing");

	TestTrue(TEXT("empty field with preview disabled selects no additional effect"),
		RPGTier1Visuals::SelectEffect(Empty, Tier1Path, false).IsNull());
	TestEqual(TEXT("empty field with Development preview selects the Tier 1 asset"),
		RPGTier1Visuals::SelectEffect(Empty, Tier1Path, true).ToSoftObjectPath().ToString(), FString(Tier1Path));
	TestEqual(TEXT("an authored field takes priority over the preview fallback"),
		RPGTier1Visuals::SelectEffect(Authored, Tier1Path, true).ToSoftObjectPath().ToString(),
		Authored.ToSoftObjectPath().ToString());
	TestEqual(TEXT("authored fields remain eligible when the preview switch is disabled"),
		RPGTier1Visuals::SelectEffect(Authored, Tier1Path, false).ToSoftObjectPath().ToString(),
		Authored.ToSoftObjectPath().ToString());
#if !UE_BUILD_DEVELOPMENT
	TestFalse(TEXT("non-Development builds have no Tier 1 preview switch"), RPGTier1Visuals::IsTier1PreviewEnabled());
#endif
	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
