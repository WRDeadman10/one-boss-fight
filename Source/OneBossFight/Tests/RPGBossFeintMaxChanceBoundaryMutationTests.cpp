// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossFeintRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossFeintMaxChanceBoundaryMutationTest,
    "OneBossFight.Framework.Feint.MaxChanceBoundaryMutation",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FBossFeintMaxChanceBoundaryMutationTest::RunTest(const FString&)
{
    const double Chance = RPGBossFeint::Chance(.15, .15, .6, .05, 1.);
    TestTrue(TEXT("a maximum chance of exactly one is valid and reachable"),
        FMath::IsNearlyEqual(Chance, 1.));
    return true;
}
#endif
