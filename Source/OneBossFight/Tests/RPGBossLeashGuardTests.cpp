// Copyright One Boss Fight. All Rights Reserved.
// BL-37 (lane BL, X-2177): RPGBossLeashRules confirmed gap only: a negative finite radius disables the leash (never outside). Asserts existing behaviour only.
#include "Player/RPGBossLeashRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossLeashGuards, "OneBossFight.Framework.Leash.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossLeashGuards::RunTest(const FString&)
{
    using RPGBossLeashRules::IsOutsideArena;
    const FVector Far(1000., 0., 0.), Center(0., 0., 0.);
    TestTrue(TEXT("control: a positive radius puts a far point outside"), IsOutsideArena(Far, Center, 100.));
    TestFalse(TEXT("negative finite radius disables the leash"), IsOutsideArena(Far, Center, -100.));
    return true;
}
#endif
