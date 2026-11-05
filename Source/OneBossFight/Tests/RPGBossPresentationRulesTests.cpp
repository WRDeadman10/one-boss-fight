// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossPresentationRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossPresentationRules,"OneBossFight.Framework.Presentation.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossPresentationRules::RunTest(const FString&)
{
    using namespace RPGBossPresentation;TestTrue(TEXT("death plays once after terminal death"),ShouldPlayDeath(true,false));
    TestFalse(TEXT("living boss has no death presentation"),ShouldPlayDeath(false,false));TestFalse(TEXT("death presentation does not repeat"),ShouldPlayDeath(true,true));
    TestTrue(TEXT("living phase change permits roar"),ShouldPlayPhaseRoar(false,true,false));TestFalse(TEXT("death suppresses phase roar"),ShouldPlayPhaseRoar(true,true,false));
    TestFalse(TEXT("unchanged phase has no roar"),ShouldPlayPhaseRoar(false,false,false));TestFalse(TEXT("phase roar is one-shot"),ShouldPlayPhaseRoar(false,true,true));return true;
}
#endif
