// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossRetreatRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossRetreatRules,"OneBossFight.Framework.Retreat.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossRetreatRules::RunTest(const FString&)
{
    using namespace RPGBossRetreat;TestTrue(TEXT("threatened and close retreats"),ShouldRetreat(100.,150.,.8));TestFalse(TEXT("far target does not retreat"),ShouldRetreat(200.,150.,.8));
    TestFalse(TEXT("low threat does not retreat"),ShouldRetreat(100.,150.,.49));TestTrue(TEXT("threat threshold is inclusive"),ShouldRetreat(100.,150.,.5));
    TestFalse(TEXT("invalid threat fails closed"),ShouldRetreat(100.,150.,1.1));TestFalse(TEXT("invalid range fails closed"),ShouldRetreat(-1.,150.,.8));return true;
}
#endif
