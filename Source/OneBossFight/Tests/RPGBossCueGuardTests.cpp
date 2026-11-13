// Copyright One Boss Fight. All Rights Reserved.
// BL-22 (lane BL, X-2171): RPGBossCue::HoldSeconds boundary confirmed untested: MaxSeconds exactly 3 is accepted, +Inf is rejected (-1).
// Asserts existing behaviour only.
#include "Player/RPGBossCueRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossCueGuards, "OneBossFight.Framework.Cue.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossCueGuards::RunTest(const FString&)
{
    using RPGBossCue::HoldSeconds;
    const float Inf = std::numeric_limits<float>::infinity();

    for (int32 Index = 0; Index < 8; ++Index)
    {
        const double Hold = HoldSeconds(1.f, 3.f, 42, Index);
        TestTrue(*FString::Printf(TEXT("MaxSeconds == 3 accepted (index %d)"), Index), Hold >= 1. && Hold <= 3.);
    }
    // BL-86 note: +Inf is also caught by MaxSeconds > 3, so it does not pin IsFinite(MaxSeconds); NaN does (without it the hold would be NaN).
    TestEqual(TEXT("MaxSeconds +Inf rejected (equivalent)"), HoldSeconds(1.f, Inf, 42, 0), -1.);
    TestEqual(TEXT("MaxSeconds NaN rejected (pins IsFinite)"), HoldSeconds(1.f, std::numeric_limits<float>::quiet_NaN(), 42, 0), -1.);
    return true;
}
#endif
