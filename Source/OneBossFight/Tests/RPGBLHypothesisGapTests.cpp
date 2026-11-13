// Copyright One Boss Fight. All Rights Reserved.
// BL-91..95 (lane BL, X-2201): the BL-01 audit hypotheses that turned out to be GENUINE, deterministic, owner-independent gaps (hand-verified against each
// header). Covered / equivalent / unreachable / decision-dependent hypotheses are reported in Documentation/Boss/BL_91_95_HYPOTHESES_PASS.md, not tested.
// Asserts existing behaviour only.
#include "Player/RPGAirAttackRules.h"
#include "Player/RPGBleedRules.h"
#include "Player/RPGBossDormantWakeRules.h"
#include "Player/RPGBossStaggerResistRules.h"
#include "Player/RPGBossStuckRules.h"
#include "Player/RPGBossTrackRules.h"
#include "Player/RPGDodgeInputRules.h"
#include "Player/RPGPackParryRules.h"
#include "Player/RPGParryRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBLHypothesisGapTests, "OneBossFight.Framework.HypothesisGaps", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBLHypothesisGapTests::RunTest(const FString&)
{
    const double NaN = std::numeric_limits<double>::quiet_NaN();

    // H1 RPGAirAttackRules.h:12 - grounded with no clip keeps the pack route (the two untested of 8 combinations).
    TestTrue(TEXT("H1 grounded light, no clip -> Pack"), RPGAirAttackRules::Select(false, false, false) == RPGAirAttackRules::EAirAttackRoute::Pack);
    TestTrue(TEXT("H1 grounded heavy, no clip -> Pack"), RPGAirAttackRules::Select(false, true, false) == RPGAirAttackRules::EAirAttackRoute::Pack);

    // H2 RPGBleedRules.h:52,69 - ThresholdIncrease 0 is valid and the threshold never rises after a proc.
    {
        RPGBleedRules::FConfig C; C.ThresholdIncrease = 0.f;
        RPGBleedRules::FState S;
        TestTrue(TEXT("H2 a full hit procs"), RPGBleedRules::Apply(S, C, 100.f, false, false, false, false) == RPGBleedRules::EResult::Proc);
        TestTrue(TEXT("H2 threshold stays 100, buildup reset, one proc"), S.Threshold == 100.f && S.Buildup == 0.f && S.Procs == 1);
    }

    // H6 RPGBossDormantWakeRules.h:13 - an expected time inside (0, 0.15) becomes the grace (not the 0.15 cap).
    TestTrue(TEXT("H6 0.05 s expected: finishes at 0.05"), RPGBossDormantWakeRules::ShouldFinishWake(false, .05f, .05f));
    TestFalse(TEXT("H6 0.05 s expected: not at 0.04"), RPGBossDormantWakeRules::ShouldFinishWake(false, .04f, .05f));

    // H10 RPGBossStaggerResistRules.h:10 - an invalid phase-two override also neutralizes phase one (shared guard).
    TestEqual(TEXT("H10 control: valid overrides, phase 1 uses 0.8"), RPGBossStaggerResist::Scale(1, .8, 1.25), .8);
    TestEqual(TEXT("H10 invalid phase-two override -> phase 1 is 1"), RPGBossStaggerResist::Scale(1, .8, 4.), 1.);

    // H12 RPGBossStuckRules.h:20-26 - a negative sample resets the accumulators (separately from the NaN case).
    {
        RPGBossStuck::FStuck S; RPGBossStuck::Update(S, 10., 1., .4);
        RPGBossStuck::Update(S, -1., 0., 0.);
        TestTrue(TEXT("H12 negative expected resets everything"), S.AccumExpected == 0. && S.AccumMoved == 0. && S.Window == 0.);
        TestFalse(TEXT("H12 a reset window is not stuck"), RPGBossStuck::IsStuck(S, .5, .3));
        RPGBossStuck::FStuck T; RPGBossStuck::Update(T, 10., 1., .4); RPGBossStuck::Update(T, 1., -1., 0.);
        TestEqual(TEXT("H12 negative moved resets the window"), T.Window, 0.);
        RPGBossStuck::FStuck U; RPGBossStuck::Update(U, 10., 1., .4); RPGBossStuck::Update(U, 1., 0., -.1);
        TestEqual(TEXT("H12 negative dt resets the window"), U.Window, 0.);
    }

    // H14 RPGBossTrackRules.h:120 - non-finite GroundedZ inputs: a bad floor gives 0, a bad offset keeps the floor.
    TestEqual(TEXT("H14 control: 10 + 90 + 2"), RPGBossTrack::GroundedZ(10., 90., 2.), 102.);
    TestEqual(TEXT("H14 NaN floor -> 0"), RPGBossTrack::GroundedZ(NaN, 90., 2.), 0.);
    TestEqual(TEXT("H14 NaN half height -> floor"), RPGBossTrack::GroundedZ(10., NaN, 2.), 10.);

    // H15 RPGBossTrackRules.h:81 - Push with Depth < 1 is ignored and keeps the existing history (without the guard it would empty it).
    {
        RPGBossTrack::FDodgeHistory H;
        H.Push(RPGBossTrack::EDodgeDir::Back, 3);
        H.Push(RPGBossTrack::EDodgeDir::Back, 0);
        TestEqual(TEXT("H15 depth 0 keeps the one entry"), H.Dirs.Num(), 1);
        H.Push(RPGBossTrack::EDodgeDir::Back, -2);
        TestEqual(TEXT("H15 negative depth keeps the one entry"), H.Dirs.Num(), 1);
    }

    // H20 RPGDodgeInputRules.h:20-24 - direction input without a backstep clip rolls (the missing 4th combination).
    TestTrue(TEXT("H20 direction, no clip -> Roll"), RPGDodgeInputRules::DecideTap(true, false) == RPGDodgeInputRules::EDodgeTapDecision::Roll);

    // H23 RPGPackParryRules.h:47-50, 87-91 - BossId 0 gives an empty key; Reset forgets accepted keys.
    {
        TestTrue(TEXT("H23 BossId 0 gives an empty key"), RPGPackParry::BuildAttackKey(3, 0, TEXT("A1b"), 18, NAME_None, 0.).IsEmpty());
        RPGPackParry::FRewardDeduplicator D;
        const FString Key = RPGPackParry::BuildAttackKey(3, 42, TEXT("A1b"), 18, NAME_None, 0.);
        TestTrue(TEXT("H23 first accept"), D.TryAccept(3, Key));
        TestFalse(TEXT("H23 duplicate refused"), D.TryAccept(3, Key));
        D.Reset();
        TestTrue(TEXT("H23 after Reset the same key is accepted again"), D.TryAccept(3, Key));
    }

    // H25 RPGParryRules.h:18-19 - a negative cooldown is floored to the window.
    {
        RPGParry::FState S;
        TestTrue(TEXT("H25 press accepted"), RPGParry::Press(S, 1., .25, -1.));
        TestEqual(TEXT("H25 negative cooldown floors to the window"), S.ReadyAt, 1.25);
    }
    return true;
}
#endif
