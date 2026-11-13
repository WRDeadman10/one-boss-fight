// Copyright One Boss Fight. All Rights Reserved.
// BQ-67/68 (Queue BQ batch 14; KI-057): URPGBossPosture pins the pack poise attribute full every tick, which hides the pack's
// 20 (light) / 50 (heavy) poise subtraction that KI-057 needs to observe on a victim. The Development switch
// rpg.Posture.PinPackPoiseTest (default 1, Shipping always 1) lets a PIE driver suspend the pin. This pins the pure decision
// and the defaults. The 20/50 measurement itself is ENG (PIE). Written, not compiled/run.
#include "Player/RPGBossPosture.h"
#include "HAL/IConsoleManager.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FPackPoisePinSwitchTest, "OneBossFight.Boss.PackPoisePinSwitch", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FPackPoisePinSwitchTest::RunTest(const FString&)
{
	TestTrue(TEXT("authored: property on, configured, switch 1 -> pin"), URPGBossPosture::ShouldPinPackPoise(true, true, 1));
	TestFalse(TEXT("test switch 0 suspends the pin"), URPGBossPosture::ShouldPinPackPoise(true, true, 0));
	TestFalse(TEXT("property off never pins"), URPGBossPosture::ShouldPinPackPoise(false, true, 1));
	TestFalse(TEXT("attribute not configured yet: no pin"), URPGBossPosture::ShouldPinPackPoise(true, false, 1));
	TestTrue(TEXT("any non-zero switch value keeps the pin"), URPGBossPosture::ShouldPinPackPoise(true, true, 2));
	const URPGBossPosture* Defaults = GetDefault<URPGBossPosture>();
	TestTrue(TEXT("class default keeps the pin property on"), Defaults && Defaults->bPinPackPoise);
	const IConsoleVariable* Switch = IConsoleManager::Get().FindConsoleVariable(TEXT("rpg.Posture.PinPackPoiseTest"));
	TestTrue(TEXT("test switch is registered in non-Shipping builds"), Switch != nullptr);
	// The live CVar value may be overridden by project config or another test; its
	// declared default (1) is verified from the registration source, not current state.
	return true;
}
#endif
