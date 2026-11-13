// Copyright One Boss Fight. All Rights Reserved.
// BQ-28/29 (Queue BQ batch 6; KI-091): the player's default weapon slot holds the sword and the ExampleMagicStaff. If the player cycled to the
// staff before the boss woke, the fight lock (Ability.Quickslot blocked) froze them in MagicCombatStyle for the whole fight. With the opt-in
// URPGBuildLoadout::bReturnToWeaponBeforeLock, SyncLock cycles back to the weapon item first, at most MaxAttempts times. This pins the pure
// decision and the default. The live cycle through the pack's equipment component stays ENG (PIE). Written, not compiled/run.
#include "Player/RPGBuildRules.h"
#include "Player/RPGBuildLoadout.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBuildReturnToWeaponTest, "OneBossFight.Build.ReturnToWeaponBeforeLock", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBuildReturnToWeaponTest::RunTest(const FString&)
{
	using RPGBuildRules::ShouldReturnToWeaponBeforeLock;
	// (opt-in, want lock, item count, active, weapon, attempts so far, max attempts)
	TestTrue(TEXT("staff active as the lock engages: cycle back"), ShouldReturnToWeaponBeforeLock(true, true, 2, 1, 0, 0, 3));
	TestFalse(TEXT("opt-in off (default): lock as before"), ShouldReturnToWeaponBeforeLock(false, true, 2, 1, 0, 0, 3));
	TestFalse(TEXT("weapon already active: lock now"), ShouldReturnToWeaponBeforeLock(true, true, 2, 0, 0, 0, 3));
	TestFalse(TEXT("single-item slot: nothing to cycle"), ShouldReturnToWeaponBeforeLock(true, true, 1, 0, 0, 0, 3));
	TestFalse(TEXT("unlocking: never cycles"), ShouldReturnToWeaponBeforeLock(true, false, 2, 1, 0, 0, 3));
	TestTrue(TEXT("third item: still cycling within the budget"), ShouldReturnToWeaponBeforeLock(true, true, 3, 2, 0, 2, 3));
	TestFalse(TEXT("budget spent: the lock engages anyway (no endless cycle)"), ShouldReturnToWeaponBeforeLock(true, true, 3, 2, 0, 3, 3));
	TestTrue(TEXT("MaxAttempts 0 still allows one cycle (clamped to 1)"), ShouldReturnToWeaponBeforeLock(true, true, 2, 1, 0, 0, 0));
	TestFalse(TEXT("MaxAttempts 0: second attempt refused"), ShouldReturnToWeaponBeforeLock(true, true, 2, 1, 0, 1, 0));
	const URPGBuildLoadout* Defaults = GetDefault<URPGBuildLoadout>();
	TestFalse(TEXT("class default keeps the return opt-in off"), Defaults && Defaults->bReturnToWeaponBeforeLock);
	return true;
}
#endif
