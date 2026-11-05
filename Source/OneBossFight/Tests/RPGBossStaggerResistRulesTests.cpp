// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossStaggerResistRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossStaggerResistRules,"OneBossFight.Framework.StaggerResist.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossStaggerResistRules::RunTest(const FString&)
{
    using namespace RPGBossStaggerResist;TestEqual(TEXT("phase one default baseline"),Scale(1),1.);TestEqual(TEXT("phase two default resistance"),Scale(2),1.25);
    TestEqual(TEXT("unknown phase uses baseline"),Scale(3),1.);TestEqual(TEXT("explicit phase value is used"),Scale(1,.8,1.6),.8);
    TestEqual(TEXT("invalid scale falls back to neutral"),Scale(2,1.,4.),1.);return true;
}
#endif
