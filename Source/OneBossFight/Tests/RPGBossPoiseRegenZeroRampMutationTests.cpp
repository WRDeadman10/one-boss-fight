// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossPoiseRegenRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossPoiseRegenZeroRampMutationTest,
    "OneBossFight.Framework.PoiseRegen.ZeroRampMutation",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FBossPoiseRegenZeroRampMutationTest::RunTest(const FString&)
{
    TestEqual(TEXT("zero ramp duration fails closed"),
        RPGBossPoiseRegen::Rate(10., 1., 1., 0., 1.5), 0.);
    return true;
}
#endif
