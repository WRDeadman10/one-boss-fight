// Copyright One Boss Fight. All Rights Reserved.
// BL-32 (lane BL, X-2174): RPGBossFeint negative reaction/Fast/MinChance, MaxChance<MinChance or >1, and Slow==Fast return 0. Asserts existing behaviour only.
#include "Player/RPGBossFeintRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossFeintGuards, "OneBossFight.Framework.Feint.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossFeintGuards::RunTest(const FString&)
{
    using RPGBossFeint::Chance;

    // Controls: a fast reaction gives the max chance, a mid one is strictly between min and max.
    TestEqual(TEXT("control: fast reaction gives 0.45"), Chance(.15), .45);
    TestTrue(TEXT("control: mid reaction is non-zero"), Chance(.375) > .05);

    TestEqual(TEXT("negative player reaction gives 0"), Chance(-.1), 0.);
    TestEqual(TEXT("negative fast reaction gives 0"), Chance(.3, -.1, .6, .05, .45), 0.);
    TestEqual(TEXT("negative min chance gives 0"), Chance(.3, .15, .6, -.05, .45), 0.);
    TestEqual(TEXT("max chance below min chance gives 0"), Chance(.3, .15, .6, .3, .2), 0.);
    TestEqual(TEXT("max chance above 1 gives 0"), Chance(.3, .15, .6, .05, 1.01), 0.);
    TestEqual(TEXT("slow equal to fast gives 0"), Chance(.3, .3, .3, .05, .45), 0.);
    return true;
}
#endif
