// Copyright One Boss Fight. All Rights Reserved.
// BL-52 (lane BL, X-2186): RPGBossReactiveDodge invalid configs (HitsToStart <0 / >100, BaseChance > MaxChance, negative/NaN BaseChance and ChancePerHit)
// and ShouldDodge roll range (<0 and >=1). Max-int/negative RecentHits, NaN roll and MaxChance>1 are already covered and not repeated.
// Asserts existing behaviour only.
#include "Player/RPGBossReactiveDodgeRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossReactiveDodgeGuards, "OneBossFight.Framework.ReactiveDodge.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossReactiveDodgeGuards::RunTest(const FString&)
{
    using namespace RPGBossReactiveDodge;
    const double NaN = std::numeric_limits<double>::quiet_NaN();

    // Control: 3 recent hits on a heavy attack give 0.05 + 2 * 0.1 = 0.25; 200 hits saturate at the 0.65 max.
    TestTrue(TEXT("control: 3 hits give 0.25"), FMath::IsNearlyEqual(Chance(true, 3), .25, 1.e-12));
    TestEqual(TEXT("control: 200 hits saturate at 0.65"), Chance(true, 200), .65);

    auto ExpectZero = [this](const TCHAR* What, const FConfig& C, int32 Hits)
    {
        TestFalse(What, IsValid(C));
        TestEqual(*FString::Printf(TEXT("%s: chance 0"), What), Chance(true, Hits, C), 0.);
    };
    { FConfig C; C.HitsToStart = -1; ExpectZero(TEXT("HitsToStart -1"), C, 3); }
    { FConfig C; C.HitsToStart = 101; ExpectZero(TEXT("HitsToStart 101 (200 hits, so the guard discriminates)"), C, 200); }
    { FConfig C; C.BaseChance = .7; ExpectZero(TEXT("BaseChance above MaxChance"), C, 3); }
    { FConfig C; C.BaseChance = -.01; ExpectZero(TEXT("negative BaseChance"), C, 3); }
    { FConfig C; C.BaseChance = NaN; ExpectZero(TEXT("NaN BaseChance"), C, 3); }
    { FConfig C; C.ChancePerHit = -.01; ExpectZero(TEXT("negative ChancePerHit"), C, 3); }
    { FConfig C; C.ChancePerHit = NaN; ExpectZero(TEXT("NaN ChancePerHit"), C, 3); }

    // ShouldDodge roll range.
    TestTrue(TEXT("control: roll 0.1 below 0.25 dodges"), ShouldDodge(true, 3, .1));
    TestFalse(TEXT("negative roll is refused (would be below the chance)"), ShouldDodge(true, 3, -.1));
    // Roll >= 1 is refused. NOTE: unobservable guard, since Chance never exceeds 1 a roll >= 1 can never be below it; the assert documents behaviour.
    TestFalse(TEXT("roll exactly 1 is refused"), ShouldDodge(true, 200, 1.));
    return true;
}
#endif
