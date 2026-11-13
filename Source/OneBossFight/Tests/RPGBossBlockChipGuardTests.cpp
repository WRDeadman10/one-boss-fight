// Copyright One Boss Fight. All Rights Reserved.
// BL-13 (lane BL, X-2165/X-2168): RPGBossBlockChip case confirmed untested: a negative finite ChipFraction fails closed to zero. Asserts existing behaviour only.
#include "Player/RPGBossBlockChipRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossBlockChipGuards, "OneBossFight.Framework.BlockChip.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossBlockChipGuards::RunTest(const FString&)
{
    using RPGBossBlockChip::GuardedDamage;
    TestEqual(TEXT("control: valid chip fraction scales damage"), GuardedDamage(100., .25), 25.);
    TestEqual(TEXT("negative chip fraction fails closed"), GuardedDamage(100., -.25), 0.);
    TestEqual(TEXT("smallest negative chip fraction fails closed"), GuardedDamage(100., -1.e-9), 0.);
    return true;
}
#endif
