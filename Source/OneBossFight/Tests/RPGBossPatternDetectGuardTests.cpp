// Copyright One Boss Fight. All Rights Reserved.
// BL-43 (lane BL, X-2179): RPGBossPatternDetect gaps: RequiredRepeats 100 accepted with detection at the exact count; corrupt negative / oversize Consecutive
// clamps to [0,100]; an invalid RequiredRepeats fully resets the state. Asserts existing behaviour only.
#include "Player/RPGBossPatternDetectRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossPatternDetectGuards, "OneBossFight.Framework.PatternDetect.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossPatternDetectGuards::RunTest(const FString&)
{
    using namespace RPGBossPatternDetect;
    const FName A(TEXT("Swing")), B(TEXT("Thrust"));

    // Control: three repeats with RequiredRepeats 3 detect on the third.
    {
        FState S;
        TestFalse(TEXT("control: 1st"), Observe(S, A, 3));
        TestFalse(TEXT("control: 2nd"), Observe(S, A, 3));
        TestTrue(TEXT("control: 3rd detects"), Observe(S, A, 3));
    }

    // RequiredRepeats 100 is accepted: no detection before the 100th observation, detection exactly at it.
    {
        FState S; bool bEarly = false;
        for (int32 I = 1; I < 100; ++I) { bEarly |= Observe(S, A, 100); }
        TestFalse(TEXT("no detection before the 100th repeat"), bEarly);
        TestTrue(TEXT("detection at exactly the 100th repeat"), Observe(S, A, 100));
        TestEqual(TEXT("count is 100"), S.Consecutive, 100);
        TestTrue(TEXT("count saturates at 100"), Observe(S, A, 100) && S.Consecutive == 100);
    }

    // Corrupt counts are clamped to [0,100] before use.
    {
        FState S; S.LastPattern = A; S.Consecutive = -5;
        TestFalse(TEXT("negative count clamps to 0, then +1 = 1: no detection"), Observe(S, A, 3));
        TestEqual(TEXT("negative count clamped then incremented to 1"), S.Consecutive, 1);
    }
    {
        FState S; S.LastPattern = A; S.Consecutive = 1000;
        // BL-86 note: the clamp's UPPER bound is an equivalent mutant (FMath::Min(1001,100) caps it anyway); only the lower bound (above) discriminates.
        TestTrue(TEXT("oversize count clamps to 100 and detects (equivalent upper bound)"), Observe(S, A, 3));
        TestEqual(TEXT("oversize count stays at the 100 cap"), S.Consecutive, 100);
    }

    // Invalid RequiredRepeats (below 2 or above 100) resets the whole state, not just the result.
    for (int32 Bad : {1, 101})
    {
        FState S; S.LastPattern = A; S.Consecutive = 7;
        TestFalse(*FString::Printf(TEXT("RequiredRepeats %d: no detection"), Bad), Observe(S, B, Bad));
        TestTrue(*FString::Printf(TEXT("RequiredRepeats %d: LastPattern reset"), Bad), S.LastPattern.IsNone());
        TestEqual(*FString::Printf(TEXT("RequiredRepeats %d: Consecutive reset"), Bad), S.Consecutive, 0);
    }
    return true;
}
#endif
