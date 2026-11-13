// Copyright One Boss Fight. All Rights Reserved.
// BQ-17 (Queue BQ batch 4; KI-067/068): the A4, A5 and A6 hits only wrote health. With the CVar rpg.Boss.ProjectHitReaction (default 0)
// and a configured URPGDamageResolver::ProjectHitReactionMontage, an accepted non-lethal opted-in hit plays the montage on the player.
// This pins the pure decision and the defaults. The live reaction and the montage asset stay ENG/ART. Written, not compiled/run.
#include "Player/RPGDamageResolver.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FProjectHitReactionTest, "OneBossFight.Damage.ProjectHitReaction", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FProjectHitReactionTest::RunTest(const FString&)
{
	using namespace RPGDamageRules;
	const ERPGDamageOutcome Ok = ERPGDamageOutcome::Accepted;
	TestTrue(TEXT("all conditions met: reaction"), ShouldRequestHitReaction(true, true, Ok, false, true));
	TestFalse(TEXT("CVar off (default): damage only, unchanged"), ShouldRequestHitReaction(false, true, Ok, false, true));
	TestFalse(TEXT("move did not opt in"), ShouldRequestHitReaction(true, false, Ok, false, true));
	TestFalse(TEXT("lethal hit: only the death follows (Freeze 1267)"), ShouldRequestHitReaction(true, true, Ok, true, true));
	TestFalse(TEXT("no montage configured"), ShouldRequestHitReaction(true, true, Ok, false, false));
	TestFalse(TEXT("blocked: no reaction"), ShouldRequestHitReaction(true, true, ERPGDamageOutcome::Blocked, false, true));
	TestFalse(TEXT("parried: no reaction"), ShouldRequestHitReaction(true, true, ERPGDamageOutcome::Parried, false, true));
	TestFalse(TEXT("dodged (invulnerable): no reaction"), ShouldRequestHitReaction(true, true, ERPGDamageOutcome::RejectedInvulnerable, false, true));
	TestFalse(TEXT("write failed: no reaction"), ShouldRequestHitReaction(true, true, ERPGDamageOutcome::Failed, false, true));
	TestFalse(TEXT("payload default does not opt in"), FRPGDamagePayload().bRequestHitReaction);
	const URPGDamageResolver* Defaults = GetDefault<URPGDamageResolver>();
	TestTrue(TEXT("class default has no reaction montage"), Defaults && Defaults->ProjectHitReactionMontage.IsNull());
	return true;
}
#endif
