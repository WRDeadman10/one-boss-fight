// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossDifficultyRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossDifficultyEqualEndpointsMutationTest,
    "OneBossFight.Framework.Difficulty.EqualEndpointsMutation",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FBossDifficultyEqualEndpointsMutationTest::RunTest(const FString&)
{
    RPGBossDifficulty::FConfig Config;
    Config.DamageMin = .9;
    Config.DamageMax = .9;
    TestTrue(TEXT("equal damage endpoints form a valid constant scale"),
        RPGBossDifficulty::IsValid(Config));
    TestEqual(TEXT("the equal damage endpoint is preserved at maximum difficulty"),
        RPGBossDifficulty::Evaluate(1., Config).Damage, .9);
    return true;
}
#endif
