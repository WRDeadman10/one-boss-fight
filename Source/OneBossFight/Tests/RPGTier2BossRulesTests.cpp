// Copyright One Boss Fight. All Rights Reserved.
#include "Misc/AutomationTest.h"
#include "Boss/RPGTier2BossRules.h"
#include "Boss/RPGTier2BossPresentation.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGTier2BossRulesTest,
	"OneBossFight.Art.Tier2Boss.PureRules",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FRPGTier2BossRulesTest::RunTest(const FString&)
{
	using namespace RPGTier2BossRules;
	TestFalse(TEXT("default off never shows aura"), ShouldShowAura(false, 40., 100., false));
	TestFalse(TEXT("above 60 percent stays off"), ShouldShowAura(true, 60.01, 100., false));
	TestTrue(TEXT("at 60 percent enables aura"), ShouldShowAura(true, 60., 100., false));
	TestTrue(TEXT("below 60 percent enables aura"), ShouldShowAura(true, 1., 100., false));
	TestFalse(TEXT("dead boss does not show aura"), ShouldShowAura(true, 0., 100., false));
	TestFalse(TEXT("invalid max health does not show aura"), ShouldShowAura(true, 20., 0., false));
	TestFalse(TEXT("dormant boss does not show aura"), ShouldShowAura(true, 40., 100., true));
	TestTrue(TEXT("first eligible tick spawns once"), ShouldSpawnAura(true, 40., 100., false, false));
	TestFalse(TEXT("existing aura prevents duplicate spawn"), ShouldSpawnAura(true, 40., 100., false, true));
	TestFalse(TEXT("zero health refuses a repeat aura"), ShouldSpawnAura(true, 0., 100., false, false));
	TestFalse(TEXT("restored full health resets visual eligibility"), ShouldShowAura(true, 100., 100., false));
	TestTrue(TEXT("later threshold crossing can spawn after reset"), ShouldSpawnAura(true, 60., 100., false, false));
	TestFalse(TEXT("no successful parry does not recoil"), ShouldPlayParryRecoil(true, false));
	TestFalse(TEXT("Tier 2 off does not recoil"), ShouldPlayParryRecoil(false, true));
	TestTrue(TEXT("successful parry and enabled recoils"), ShouldPlayParryRecoil(true, true));
	TestTrue(TEXT("a later distinct successful parry may recoil"), ShouldPlayParryRecoil(true, true));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGTier2AuraAttachSocketDefaultTest,
	"OneBossFight.Art.Tier2Boss.AuraAttachSocketDefault",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FRPGTier2AuraAttachSocketDefaultTest::RunTest(const FString&)
{
	const URPGTier2BossPresentation* DefaultPresentation = NewObject<URPGTier2BossPresentation>();
	TestNotNull(TEXT("presentation component constructs"), DefaultPresentation);
	if (!DefaultPresentation)
	{
		return false;
	}
	TestTrue(TEXT("default socket preserves mesh-origin attachment"), DefaultPresentation->AuraAttachSocket.IsNone());

	URPGTier2BossPresentation* OptInPresentation = NewObject<URPGTier2BossPresentation>();
	TestNotNull(TEXT("opt-in presentation component constructs"), OptInPresentation);
	if (!OptInPresentation)
	{
		return false;
	}
	OptInPresentation->AuraAttachSocket = FName(TEXT("spine_03"));
	TestEqual(TEXT("explicit socket is retained for an owner-approved look"), OptInPresentation->AuraAttachSocket, FName(TEXT("spine_03")));
	return true;
}
#endif
