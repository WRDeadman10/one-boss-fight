// Copyright One Boss Fight. All Rights Reserved.
// BL-26 (lane BL, X-2172): RPGBossDesperation guard clauses (HealthFraction<0/>1, StartFraction<=0, MaxMultiplier<1) and exact MaxMultiplier=3 acceptance.
// Asserts existing behaviour only.
#include "Player/RPGBossDesperationRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossDesperationGuards, "OneBossFight.Framework.Desperation.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossDesperationGuards::RunTest(const FString&)
{
    using RPGBossDesperation::WeightMultiplier;

    // Controls: at 0 health the default ramp is fully applied (1.5); halfway into the ramp it is 1.25; above the start it is the baseline 1.
    TestEqual(TEXT("control: 0 health gives the max 1.5"), WeightMultiplier(0., .35, 1.5), 1.5);
    TestEqual(TEXT("control: half-way into the ramp gives 1.25"), WeightMultiplier(.175, .35, 1.5), 1.25);
    TestEqual(TEXT("control: above the start fraction is the baseline 1"), WeightMultiplier(.5, .35, 1.5), 1.);

    // Invalid inputs fail closed to the unchanged multiplier 1 (checked at 0 health, where a valid call would give 1.5).
    TestEqual(TEXT("negative health fraction gives 1"), WeightMultiplier(-.1, .35, 1.5), 1.);
    // BL-86 correction: health 1.1 is NOT checked at 0 health and is an EQUIVALENT mutant (the ramp (.35-1.1)/.35 clamps to 0 -> 1 anyway).
    TestEqual(TEXT("health fraction above 1 gives 1 (equivalent)"), WeightMultiplier(1.1, .35, 1.5), 1.);
    // BL-86 missed gap: StartFraction above 1 discriminates (without the guard 0 health would give 1.5).
    TestEqual(TEXT("start fraction above 1 gives 1"), WeightMultiplier(0., 1.1, 1.5), 1.);
    TestEqual(TEXT("start fraction 0 gives 1"), WeightMultiplier(0., 0., 1.5), 1.);
    TestEqual(TEXT("negative start fraction gives 1"), WeightMultiplier(0., -.1, 1.5), 1.);
    TestEqual(TEXT("max multiplier below 1 gives 1"), WeightMultiplier(0., .35, .9), 1.);

    // Exact upper bound: a max multiplier of exactly 3 is accepted and fully applied.
    TestEqual(TEXT("max multiplier exactly 3 is accepted"), WeightMultiplier(0., .35, 3.), 3.);
    return true;
}
#endif
