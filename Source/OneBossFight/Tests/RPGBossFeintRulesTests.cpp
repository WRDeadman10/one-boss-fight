// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossFeintRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossFeintRules,"OneBossFight.Framework.Feint.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossFeintRules::RunTest(const FString&)
{
    using namespace RPGBossFeint;TestEqual(TEXT("slow reaction gets minimum feint chance"),Chance(.6),.05);TestEqual(TEXT("fast reaction gets maximum feint chance"),Chance(.15),.45);
    TestTrue(TEXT("faster reaction never lowers feint chance"),Chance(.2)>Chance(.4));TestTrue(TEXT("reaction outside measured band clamps"),Chance(1.)==.05&&Chance(0.)==.45);
    TestEqual(TEXT("invalid reaction fails closed"),Chance(std::numeric_limits<double>::quiet_NaN()),0.);TestEqual(TEXT("invalid reaction band fails closed"),Chance(.3,.5,.2),0.);return true;
}
#endif
