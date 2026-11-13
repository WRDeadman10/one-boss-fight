// Copyright One Boss Fight. All Rights Reserved.
// BL-51 (lane BL, X-2186): RPGBossPunish guards: RequiresRecoveryPunishCheck fails closed for a NaN/negative cone and excludes exactly 180 (179.9 accepted);
// FPlayerMoves::IsValid rejects NaN and zero Light/Heavy startup, negative RunSpeed and negative Reach while Reach=0 is valid; TravelSeconds with a
// negative run speed returns the max double. Existing arithmetic/montage tests are not repeated. Asserts existing behaviour only.
#include "Player/RPGBossPunishRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossPunishGuards, "OneBossFight.Framework.Punish.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossPunishGuards::RunTest(const FString&)
{
    using namespace RPGBossPunish;
    const double NaN = std::numeric_limits<double>::quiet_NaN();

    // A tracking pure channel drain bypasses the recovery check only when its cone leaves an escape (finite, >= 0, < 180).
    TestFalse(TEXT("control: a 90 deg tracking channel can be escaped, check bypassed"), RequiresRecoveryPunishCheck(false, true, 90., true));
    TestTrue(TEXT("NaN cone fails closed: check required"), RequiresRecoveryPunishCheck(false, true, NaN, true));
    TestTrue(TEXT("negative cone fails closed: check required"), RequiresRecoveryPunishCheck(false, true, -1., true));
    TestTrue(TEXT("exactly 180 deg is excluded: check required"), RequiresRecoveryPunishCheck(false, true, 180., true));
    TestFalse(TEXT("179.9 deg is accepted: check bypassed"), RequiresRecoveryPunishCheck(false, true, 179.9, true));

    // FPlayerMoves::IsValid.
    auto Moves = []() { FPlayerMoves M; M.LightStartupSeconds = .3; M.HeavyStartupSeconds = .6; M.RunSpeedCmPerSecond = 500.; M.ReachCm = 150.; return M; };
    TestTrue(TEXT("control: measured moves are valid"), Moves().IsValid());
    { FPlayerMoves M = Moves(); M.LightStartupSeconds = NaN; TestFalse(TEXT("NaN light startup invalid"), M.IsValid()); }
    { FPlayerMoves M = Moves(); M.HeavyStartupSeconds = NaN; TestFalse(TEXT("NaN heavy startup invalid"), M.IsValid()); }
    { FPlayerMoves M = Moves(); M.LightStartupSeconds = 0.; TestFalse(TEXT("zero light startup invalid"), M.IsValid()); }
    { FPlayerMoves M = Moves(); M.HeavyStartupSeconds = 0.; TestFalse(TEXT("zero heavy startup invalid"), M.IsValid()); }
    { FPlayerMoves M = Moves(); M.RunSpeedCmPerSecond = -1.; TestFalse(TEXT("negative run speed invalid"), M.IsValid()); }
    { FPlayerMoves M = Moves(); M.ReachCm = -1.; TestFalse(TEXT("negative reach invalid"), M.IsValid()); }
    { FPlayerMoves M = Moves(); M.ReachCm = 0.; TestTrue(TEXT("zero reach is valid"), M.IsValid()); }

    // TravelSeconds with a negative run speed.
    TestEqual(TEXT("control: 350 cm at 350 cm/s is 1 s"), TravelSeconds(500., 150., 350.), 1.);
    TestTrue(TEXT("negative run speed returns the max double"), TravelSeconds(500., 150., -1.) == TNumericLimits<double>::Max());
    return true;
}
#endif
