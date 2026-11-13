// Copyright One Boss Fight. All Rights Reserved.
// BL-12 (lane BL, X-2165/X-2168): RPGBossBakeFreshness case confirmed untested: both fingerprints zero (equal, yet not fresh). Asserts existing behaviour only.
#include "Player/RPGBossBakeFreshnessRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossBakeFreshnessGuards, "OneBossFight.Framework.BakeFreshness.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossBakeFreshnessGuards::RunTest(const FString&)
{
    using RPGBossBakeFreshness::IsFresh;
    TestTrue(TEXT("control: equal non-zero fingerprints are fresh"), IsFresh(0x1234ull, 0x1234ull));
    TestFalse(TEXT("both fingerprints zero are equal but NOT fresh"), IsFresh(0ull, 0ull));
    return true;
}
#endif
