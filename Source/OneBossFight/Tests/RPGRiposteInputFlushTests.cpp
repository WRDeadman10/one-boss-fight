// Copyright One Boss Fight. All Rights Reserved.
// BQ-13 (Queue BQ batch 3; KI-085): after the synchronized riposte, URPGBossStagger restores the player's input with EnableInput. Disabled
// input drops key-release events, so a sprint/guard key released during the execution can stay latched. With the opt-in
// bFlushInputAfterRiposte, the restore also calls APlayerController::FlushPressedKeys. This pins the pure restore decision and the
// opt-in default. The live latched-key behaviour stays ENG (a PIE driver that holds a key through an execution). Written, not compiled/run.
#include "Player/RPGBossStagger.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRiposteInputFlushTest, "OneBossFight.Riposte.InputFlushOnRestore", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRiposteInputFlushTest::RunTest(const FString&)
{
	TestTrue(TEXT("both alive and opted in: flush after EnableInput"), URPGBossStagger::ShouldFlushInputOnRestore(true, true, true));
	TestFalse(TEXT("opt-in off (default): no flush, behaviour unchanged"), URPGBossStagger::ShouldFlushInputOnRestore(true, true, false));
	TestFalse(TEXT("boss dead: the HUD victory lock owns input, no flush"), URPGBossStagger::ShouldFlushInputOnRestore(false, true, true));
	TestFalse(TEXT("player dead: the reset owns input, no flush"), URPGBossStagger::ShouldFlushInputOnRestore(true, false, true));
	TestFalse(TEXT("both dead: no flush"), URPGBossStagger::ShouldFlushInputOnRestore(false, false, true));
	const URPGBossStagger* Defaults = GetDefault<URPGBossStagger>();
	TestFalse(TEXT("class default keeps the flush opt-in off"), Defaults && Defaults->bFlushInputAfterRiposte);
	// BQ-19 / KI-074: the get-up immunity re-apply is opt-in too (the live effect application needs the pack ASC, ENG).
	TestFalse(TEXT("class default keeps the get-up immunity re-apply off"), Defaults && Defaults->bReapplyImmunityAtGetUp);
	return true;
}
#endif
