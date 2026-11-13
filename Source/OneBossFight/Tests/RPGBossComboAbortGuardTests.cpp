// Copyright One Boss Fight. All Rights Reserved.
// BL-17 (lane BL): RPGBossComboAbort case confirmed untested: a negative AcceptedHits count never aborts (only exactly 0 can). Asserts existing behaviour only.
#include "Player/RPGBossComboAbortRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossComboAbortGuards, "OneBossFight.Framework.ComboAbort.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossComboAbortGuards::RunTest(const FString&)
{
    using RPGBossComboAbort::ShouldAbort;
    TestTrue(TEXT("control: first-hit parry of an active combo aborts"), ShouldAbort(true, 0, true));
    TestFalse(TEXT("AcceptedHits -1 does not abort"), ShouldAbort(true, -1, true));
    TestFalse(TEXT("AcceptedHits MIN_int32 does not abort"), ShouldAbort(true, MIN_int32, true));
    return true;
}
#endif
