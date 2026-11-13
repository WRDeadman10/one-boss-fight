// Copyright One Boss Fight. All Rights Reserved.
// BM-26..30 (lane BM batch 6; KI-128): RPGBleedRules::Apply threshold growth `Threshold = Min(Threshold + Increase, ThresholdMax)` at the float limit.
// The intermediate Threshold + Increase overflows to +Inf when both are near FLT_MAX; FMath::Min(+Inf, finite cap) then returns the finite cap, so the
// stored threshold stays finite. URPGBossBleed delegates to this rule (RPGBossBleed.cpp), so the rule is the single growth site. Existing coverage
// (RPGBossDamageBleedFiniteInputTests.cpp:46-51) overflows the BUILDUP with the default thresholds only. Asserts existing behaviour; not yet compiled/run.
#include "Player/RPGBleedRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBleedThresholdOverflowTest, "OneBossFight.Framework.Bleed.ThresholdGrowthOverflow", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBleedThresholdOverflowTest::RunTest(const FString&)
{
    using namespace RPGBleedRules;
    const float Max = std::numeric_limits<float>::max();

    // Control: ordinary growth, 100 + 20 -> 120.
    {
        FConfig C; FState S;
        TestTrue(TEXT("control: a 100 hit procs"), Apply(S, C, 100.f, false, false, false, false) == EResult::Proc);
        TestEqual(TEXT("control: threshold grows to 120"), S.Threshold, 120.f);
    }

    // Overflowing intermediate: Threshold = FLT_MAX, Increase = FLT_MAX -> FLT_MAX + FLT_MAX is +Inf, Min(+Inf, FLT_MAX cap) = FLT_MAX.
    {
        FConfig C; C.InitialThreshold = 100.f; C.ThresholdIncrease = Max; C.ThresholdMax = Max;
        FState S; S.Threshold = Max;
        TestTrue(TEXT("a FLT_MAX hit reaches a FLT_MAX threshold and procs"), Apply(S, C, Max, false, false, false, false) == EResult::Proc);
        TestTrue(TEXT("the grown threshold stays finite"), FMath::IsFinite(S.Threshold));
        TestEqual(TEXT("the grown threshold is the finite cap"), S.Threshold, Max);
        TestEqual(TEXT("buildup resets after the proc"), S.Buildup, 0.f);
        // The state stays usable: the next ordinary hit is Added (not refused as an invalid state).
        TestTrue(TEXT("the next hit is accepted"), Apply(S, C, 1.f, false, false, false, false) == EResult::Added);
    }

    // Growth that lands exactly on a smaller finite cap (no overflow): 150 + 100 is clamped to 200.
    {
        FConfig C; C.InitialThreshold = 100.f; C.ThresholdIncrease = 100.f; C.ThresholdMax = 200.f;
        FState S; S.Threshold = 150.f;
        TestTrue(TEXT("a 150 hit procs"), Apply(S, C, 150.f, false, false, false, false) == EResult::Proc);
        TestEqual(TEXT("growth is clamped to the 200 cap"), S.Threshold, 200.f);
    }
    return true;
}
#endif
