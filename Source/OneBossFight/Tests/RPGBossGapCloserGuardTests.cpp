// Copyright One Boss Fight. All Rights Reserved.
// BL-33 (lane BL, X-2174): RPGBossGapCloser negative RangeCm / EnterRangeCm return false. Asserts existing behaviour only.
#include "Player/RPGBossGapCloserRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossGapCloserGuards, "OneBossFight.Framework.GapCloser.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossGapCloserGuards::RunTest(const FString&)
{
    using RPGBossGapCloser::ShouldClose;

    // Controls: beyond the exit range a fresh gate closes; beyond the enter range an active gate keeps closing.
    TestTrue(TEXT("control: fresh gate closes beyond exit range"), ShouldClose(false, 800., 300., 500.));
    TestTrue(TEXT("control: active gate keeps closing beyond enter range"), ShouldClose(true, 400., 300., 500.));

    TestFalse(TEXT("negative range, fresh gate"), ShouldClose(false, -1., 300., 500.));
    TestFalse(TEXT("negative range, active gate"), ShouldClose(true, -1., 300., 500.));
    TestFalse(TEXT("negative enter range, fresh gate"), ShouldClose(false, 800., -1., 500.));
    TestFalse(TEXT("negative enter range, active gate"), ShouldClose(true, 400., -1., 500.));
    return true;
}
#endif
