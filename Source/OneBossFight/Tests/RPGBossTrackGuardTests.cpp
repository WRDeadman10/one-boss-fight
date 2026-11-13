// Copyright One Boss Fight. All Rights Reserved.
// BL-68 (lane BL): RPGBossTrack gaps: PlayerActivityName text for every EPlayerActivity value (and the "None" fallback of the ternary for an invalid
// value); WatchdogTimeoutSeconds refuses a negative ClipLength / BlendOut (both discriminate: without the guard a positive timeout would be returned).
// Existing watchdog cases (bad recovery end / play rate, clip and blend budgets) are not repeated. Asserts existing behaviour only.
#include "Player/RPGBossTrackRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossTrackGuards, "OneBossFight.Framework.Track.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossTrackGuards::RunTest(const FString&)
{
    using namespace RPGBossTrack;

    TestEqual(TEXT("activity None"), FString(PlayerActivityName(EPlayerActivity::None)), FString(TEXT("None")));
    TestEqual(TEXT("activity Flask"), FString(PlayerActivityName(EPlayerActivity::Flask)), FString(TEXT("Flask")));
    TestEqual(TEXT("activity HeavyCommit"), FString(PlayerActivityName(EPlayerActivity::HeavyCommit)), FString(TEXT("HeavyCommit")));
    TestEqual(TEXT("invalid activity falls back to None"), FString(PlayerActivityName(static_cast<EPlayerActivity>(200))), FString(TEXT("None")));

    TestTrue(TEXT("control: 1.65 s at rate 1 is 2.15 s"), FMath::IsNearlyEqual(WatchdogTimeoutSeconds(1.65f, 1.f), 2.15, 1.e-6));
    TestTrue(TEXT("negative clip length is invalid"), WatchdogTimeoutSeconds(1.65f, 1.f, -1.f, 0.f) < 0.);
    TestTrue(TEXT("negative blend-out is invalid"), WatchdogTimeoutSeconds(1.65f, 1.f, 1.2f, -.1f) < 0.);
    return true;
}
#endif
