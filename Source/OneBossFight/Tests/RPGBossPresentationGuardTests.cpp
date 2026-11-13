// Copyright One Boss Fight. All Rights Reserved.
// BL-47 (lane BL, X-2182): RPGBossPresentation missing case: ShouldPlayDeath(false, true) is false (a living boss never plays death, even with the
// played flag set). Asserts existing behaviour only.
#include "Player/RPGBossPresentationRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossPresentationGuards, "OneBossFight.Framework.Presentation.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossPresentationGuards::RunTest(const FString&)
{
    using RPGBossPresentation::ShouldPlayDeath;
    TestTrue(TEXT("control: a dead boss without a played death plays it"), ShouldPlayDeath(true, false));
    TestFalse(TEXT("living boss with the played flag set does not play death"), ShouldPlayDeath(false, true));
    return true;
}
#endif
