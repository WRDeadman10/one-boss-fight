// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossPoiseRegenRules.h"
#include "Player/RPGBossStaggerResistRules.h"
#include "Player/RPGBossAggroRules.h"
#include "Player/RPGBossDifficultyRules.h"
#include "Player/RPGBossEnrageRules.h"
#include "Player/RPGBossPunishLimiterRules.h"
#include "Player/RPGBossRetreatRules.h"
#include "Player/RPGBossGapCloserRules.h"
#include "Player/RPGBossFatigueRules.h"
#include "Player/RPGBossReactiveDodgeRules.h"
#include "Player/RPGBossCueJitterRules.h"
#include "Player/RPGBossDefenseRules.h"
#include "Misc/AutomationTest.h"
#include <cmath>
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossPoiseRegenExactRampEndpoint,
    "OneBossFight.Framework.PoiseRegen.ExactRampEndpoint", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossPoiseRegenExactRampEndpoint::RunTest(const FString&)
{
    TestEqual(TEXT("exact delay plus ramp endpoint reaches max scale"),
        RPGBossPoiseRegen::Rate(10.,3.,1.,2.,1.5),15.);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossPoiseRegenZeroDelayAndFlatScale,
    "OneBossFight.Framework.PoiseRegen.ZeroDelayAndFlatScale", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossPoiseRegenZeroDelayAndFlatScale::RunTest(const FString&)
{
    TestEqual(TEXT("zero elapsed at zero delay returns base rate"),
        RPGBossPoiseRegen::Rate(10.,0.,0.,2.,2.),10.);
    TestEqual(TEXT("unit max scale remains flat at ramp endpoint"),
        RPGBossPoiseRegen::Rate(10.,2.,0.,2.,1.),10.);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossStaggerResistScaleEndpointsAndInvalids,
    "OneBossFight.Framework.StaggerResist.ScaleEndpointsAndInvalids", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossStaggerResistScaleEndpointsAndInvalids::RunTest(const FString&)
{
    TestEqual(TEXT("zero phase-one scale endpoint is accepted"),RPGBossStaggerResist::Scale(1,0.,1.25),0.);
    TestEqual(TEXT("three phase-two scale endpoint is accepted"),RPGBossStaggerResist::Scale(2,1.,3.),3.);
    TestEqual(TEXT("negative scale override fails neutral"),RPGBossStaggerResist::Scale(1,-.01,1.25),1.);
    TestEqual(TEXT("NaN scale override fails neutral"),RPGBossStaggerResist::Scale(1,std::numeric_limits<double>::quiet_NaN(),1.25),1.);
    TestEqual(TEXT("infinite scale override fails neutral"),RPGBossStaggerResist::Scale(2,1.,std::numeric_limits<double>::infinity()),1.);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossAggroCloseThresholdAdjacent,
    "OneBossFight.Framework.Aggro.CloseThresholdAdjacent", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossAggroCloseThresholdAdjacent::RunTest(const FString&)
{
    using RPGBossAggro::EBand;
    const auto BelowEnter=std::nextafter(250.,0.);
    const auto BelowExit=std::nextafter(300.,0.);
    TestTrue(TEXT("exact close entry equality remains balanced"),RPGBossAggro::Step(EBand::Balanced,250.,false,false)==EBand::Balanced);
    TestTrue(TEXT("immediately below close entry enters close"),RPGBossAggro::Step(EBand::Balanced,BelowEnter,false,false)==EBand::Close);
    TestTrue(TEXT("immediately below close exit remains close"),RPGBossAggro::Step(EBand::Close,BelowExit,false,false)==EBand::Close);
    TestTrue(TEXT("exact close exit equality returns balanced"),RPGBossAggro::Step(EBand::Close,300.,false,false)==EBand::Balanced);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossDifficultyEndpointAdjacent,
    "OneBossFight.Framework.Difficulty.EndpointAdjacent", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossDifficultyEndpointAdjacent::RunTest(const FString&)
{
    using namespace RPGBossDifficulty;
    const FConfig Config;
    const double NearZero=std::nextafter(0.,1.);
    const double NearOne=std::nextafter(1.,0.);
    const FScales Low=Evaluate(NearZero,Config),High=Evaluate(NearOne,Config);
    TestTrue(TEXT("near-zero damage interpolation remains finite"),FMath::IsFinite(Low.Damage));
    TestTrue(TEXT("near-one damage interpolation remains finite"),FMath::IsFinite(High.Damage));
    TestTrue(TEXT("near-zero outputs remain within configured endpoints"),
        Low.Damage>=Config.DamageMin&&Low.Damage<=Config.DamageMax&&Low.Speed>=Config.SpeedMin&&Low.Speed<=Config.SpeedMax&&Low.Telegraph>=Config.TelegraphMin&&Low.Telegraph<=Config.TelegraphMax);
    TestTrue(TEXT("near-one outputs remain within configured endpoints"),
        High.Damage>=Config.DamageMin&&High.Damage<=Config.DamageMax&&High.Speed>=Config.SpeedMin&&High.Speed<=Config.SpeedMax&&High.Telegraph>=Config.TelegraphMin&&High.Telegraph<=Config.TelegraphMax);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossEnrageRampEndpointAdjacent,
    "OneBossFight.Framework.Enrage.RampEndpointAdjacent", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossEnrageRampEndpointAdjacent::RunTest(const FString&)
{
    RPGBossEnrage::FConfig Config; Config.RampSeconds=100.; Config.MaxDamageScale=1.8; Config.MaxSpeedScale=1.4;
    const double Before=std::nextafter(Config.RampSeconds,0.);
    const double After=std::nextafter(Config.RampSeconds,std::numeric_limits<double>::infinity());
    const double Below=RPGBossEnrage::DamageScale(Before,Config);
    const double At=RPGBossEnrage::DamageScale(Config.RampSeconds,Config);
    const double Above=RPGBossEnrage::DamageScale(After,Config);
    TestTrue(TEXT("samples around ramp endpoint remain ordered"),Below<=At&&At<=Above);
    TestEqual(TEXT("exact ramp endpoint reaches configured damage cap"),At,Config.MaxDamageScale);
    TestEqual(TEXT("sample after endpoint remains clamped"),Above,Config.MaxDamageScale);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossEnrageNonfiniteAndRepeat,
    "OneBossFight.Framework.Enrage.NonfiniteAndRepeat", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossEnrageNonfiniteAndRepeat::RunTest(const FString&)
{
    const double NaN=std::numeric_limits<double>::quiet_NaN(), Inf=std::numeric_limits<double>::infinity();
    TestEqual(TEXT("NaN elapsed returns baseline"),RPGBossEnrage::DamageScale(NaN),1.);
    TestEqual(TEXT("positive infinity elapsed returns baseline"),RPGBossEnrage::SpeedScale(Inf),1.);
    TestEqual(TEXT("negative infinity elapsed returns baseline"),RPGBossEnrage::Progress(-Inf),0.);
    TestEqual(TEXT("repeated equal inputs are deterministic"),RPGBossEnrage::DamageScale(45.),RPGBossEnrage::DamageScale(45.));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossPunishLimiterMaximumAndOverflow,
    "OneBossFight.Framework.PunishLimiter.MaximumAndOverflow", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossPunishLimiterMaximumAndOverflow::RunTest(const FString&)
{
    using namespace RPGBossPunishLimiter;
    FState S;
    TestTrue(TEXT("maximum supported use budget is valid"),CanUse(S,100));
    TestFalse(TEXT("budget above maximum is refused"),CanUse(S,101));
    S.Uses=MAX_int32;
    TestFalse(TEXT("maximum integer use counter refuses"),CanUse(S,100));
    TestFalse(TEXT("maximum integer use counter cannot increment"),RecordUse(S,100));
    TestEqual(TEXT("refusal preserves corrupt maximum counter"),S.Uses,MAX_int32);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossRetreatAdjacentThresholds,
    "OneBossFight.Framework.Retreat.AdjacentThresholds", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossRetreatAdjacentThresholds::RunTest(const FString&)
{
    const double RangeBelow=std::nextafter(150.,0.);
    const double ThreatBelow=std::nextafter(.75,0.);
    TestTrue(TEXT("immediately inside strict close range retreats"),RPGBossRetreat::ShouldRetreat(RangeBelow,150.,.8));
    TestFalse(TEXT("exact close range does not retreat"),RPGBossRetreat::ShouldRetreat(150.,150.,.8));
    TestFalse(TEXT("threat immediately below configured threshold does not retreat"),RPGBossRetreat::ShouldRetreat(100.,150.,ThreatBelow,.75));
    TestTrue(TEXT("threat exactly at configured threshold retreats"),RPGBossRetreat::ShouldRetreat(100.,150.,.75,.75));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossGapCloserAdjacentThresholds,
    "OneBossFight.Framework.GapCloser.AdjacentThresholds", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossGapCloserAdjacentThresholds::RunTest(const FString&)
{
    const double BelowEnter=std::nextafter(400.,0.), AboveEnter=std::nextafter(400.,std::numeric_limits<double>::infinity());
    const double BelowExit=std::nextafter(600.,0.), AboveExit=std::nextafter(600.,std::numeric_limits<double>::infinity());
    TestFalse(TEXT("active gap closer stops immediately below enter edge"),RPGBossGapCloser::ShouldClose(true,BelowEnter,400.,600.));
    TestFalse(TEXT("active gap closer stops at exact enter edge"),RPGBossGapCloser::ShouldClose(true,400.,400.,600.));
    TestTrue(TEXT("active gap closer persists immediately above enter edge"),RPGBossGapCloser::ShouldClose(true,AboveEnter,400.,600.));
    TestFalse(TEXT("new gap closer does not start immediately below exit edge"),RPGBossGapCloser::ShouldClose(false,BelowExit,400.,600.));
    TestTrue(TEXT("new gap closer starts immediately above exit edge"),RPGBossGapCloser::ShouldClose(false,AboveExit,400.,600.));
    TestTrue(TEXT("equal thresholds are accepted at the strict outside value"),RPGBossGapCloser::ShouldClose(false,std::nextafter(600.,std::numeric_limits<double>::infinity()),600.,600.));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossPoiseRegenRampEndpointAdjacent,
    "OneBossFight.Framework.PoiseRegen.RampEndpointAdjacent", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossPoiseRegenRampEndpointAdjacent::RunTest(const FString&)
{
    const double End=3., Before=std::nextafter(End,0.), After=std::nextafter(End,std::numeric_limits<double>::infinity());
    const double VBefore=RPGBossPoiseRegen::Rate(10.,Before,1.,2.,1.5);
    const double VAt=RPGBossPoiseRegen::Rate(10.,End,1.,2.,1.5);
    const double VAfter=RPGBossPoiseRegen::Rate(10.,After,1.,2.,1.5);
    TestTrue(TEXT("adjacent samples are ordered and capped"),VBefore<=VAt&&VAt<=VAfter&&VAfter<=15.);
    TestEqual(TEXT("exact delay plus ramp reaches cap"),VAt,15.);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossStaggerResistUnknownExtremePhases,
    "OneBossFight.Framework.StaggerResist.UnknownExtremePhases", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossStaggerResistUnknownExtremePhases::RunTest(const FString&)
{
    TestEqual(TEXT("negative unknown phase is neutral with overrides"),RPGBossStaggerResist::Scale(-1,.5,2.),1.);
    TestEqual(TEXT("maximum integer unknown phase is neutral with overrides"),RPGBossStaggerResist::Scale(MAX_int32,.5,2.),1.);
    TestEqual(TEXT("minimum integer unknown phase is neutral with overrides"),RPGBossStaggerResist::Scale(MIN_int32,.5,2.),1.);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossAggroFarThresholdAdjacent,
    "OneBossFight.Framework.Aggro.FarThresholdAdjacent", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossAggroFarThresholdAdjacent::RunTest(const FString&)
{
    using RPGBossAggro::EBand;
    const double AboveEnter=std::nextafter(700.,std::numeric_limits<double>::infinity());
    const double AboveExit=std::nextafter(600.,std::numeric_limits<double>::infinity());
    TestTrue(TEXT("exact far entry equality remains balanced"),RPGBossAggro::Step(EBand::Balanced,700.,false,false)==EBand::Balanced);
    TestTrue(TEXT("immediately above far entry enters far"),RPGBossAggro::Step(EBand::Balanced,AboveEnter,false,false)==EBand::Far);
    TestTrue(TEXT("immediately above far exit persists far"),RPGBossAggro::Step(EBand::Far,AboveExit,false,false)==EBand::Far);
    TestTrue(TEXT("exact far exit equality returns balanced"),RPGBossAggro::Step(EBand::Far,600.,false,false)==EBand::Balanced);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossAggroDodgeThresholdAdjacent,
    "OneBossFight.Framework.Aggro.DodgeThresholdAdjacent", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossAggroDodgeThresholdAdjacent::RunTest(const FString&)
{
    using RPGBossAggro::EBand;
    const double BelowEnter=std::nextafter(.6,0.), AboveExit=std::nextafter(.3,std::numeric_limits<double>::infinity());
    const double NaN=std::numeric_limits<double>::quiet_NaN();
    RPGBossAggro::FConfig Invalid; Invalid.EnterCloseCm=-1.;
    TestTrue(TEXT("dodge rate below enter remains balanced"),RPGBossAggro::Step(EBand::Balanced,500.,false,false,BelowEnter)==EBand::Balanced);
    TestTrue(TEXT("exact dodge enter transitions to far"),RPGBossAggro::Step(EBand::Balanced,500.,false,false,.6)==EBand::Far);
    TestTrue(TEXT("dodge rate above exit remains far"),RPGBossAggro::Step(EBand::Far,500.,false,false,AboveExit)==EBand::Far);
    TestTrue(TEXT("invalid config preserves current state"),RPGBossAggro::Step(EBand::Far,500.,false,false,0.,Invalid)==EBand::Far);
    TestTrue(TEXT("nonfinite dodge rate preserves current state"),RPGBossAggro::Step(EBand::Close,500.,false,false,NaN)==EBand::Close);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossDifficultyInvalidInputsAndEqualEndpoints,
    "OneBossFight.Framework.Difficulty.InvalidInputsAndEqualEndpoints", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossDifficultyInvalidInputsAndEqualEndpoints::RunTest(const FString&)
{
    const double Inf=std::numeric_limits<double>::infinity();
    TestEqual(TEXT("negative difficulty returns neutral"),RPGBossDifficulty::Evaluate(-std::numeric_limits<double>::epsilon()).Damage,1.);
    TestEqual(TEXT("difficulty above one returns neutral"),RPGBossDifficulty::Evaluate(1.+std::numeric_limits<double>::epsilon()).Damage,1.);
    TestEqual(TEXT("infinite difficulty returns neutral"),RPGBossDifficulty::Evaluate(Inf).Damage,1.);
    TestEqual(TEXT("negative infinite difficulty returns neutral"),RPGBossDifficulty::Evaluate(-Inf).Damage,1.);
    RPGBossDifficulty::FConfig C; C.SpeedMin=C.SpeedMax=1.1; C.TelegraphMin=C.TelegraphMax=1.2;
    for (double D : {0.,.5,1.})
    {
        const auto S=RPGBossDifficulty::Evaluate(D,C);
        TestEqual(TEXT("equal speed endpoints remain constant"),S.Speed,1.1);
        TestEqual(TEXT("equal telegraph endpoints remain constant"),S.Telegraph,1.2);
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossFatigueExactRuleBoundaries,
    "OneBossFight.Framework.Fatigue.ExactRuleBoundaries", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossFatigueExactRuleBoundaries::RunTest(const FString&)
{
    RPGBossFatigue::FConfig C; C.GraceWhiffs=2; C.ReductionPerWhiff=.1; C.MinRateScale=.7;
    TestEqual(TEXT("exact grace count retains full rate"),RPGBossFatigue::RateScale(2,C),1.);
    TestTrue(TEXT("first whiff beyond grace reduces rate"),RPGBossFatigue::RateScale(3,C)<1.);
    TestEqual(TEXT("floor is reached at exact count"),RPGBossFatigue::RateScale(5,C),.7);
    C.ReductionPerWhiff=0.;
    TestEqual(TEXT("zero reduction remains at full rate"),RPGBossFatigue::RateScale(100,C),1.);
    C.MinRateScale=1.;
    TestEqual(TEXT("unit floor remains constant"),RPGBossFatigue::RateScale(100,C),1.);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossReactiveDodgeMaximumHitBoundary,
    "OneBossFight.Framework.ReactiveDodge.MaximumHitBoundary", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossReactiveDodgeMaximumHitBoundary::RunTest(const FString&)
{
    RPGBossReactiveDodge::FConfig C; C.HitsToStart=0; C.BaseChance=0.; C.ChancePerHit=.1; C.MaxChance=1.;
    TestEqual(TEXT("maximum hit count saturates at configured cap"),RPGBossReactiveDodge::Chance(true,MAX_int32,C),1.);
    TestTrue(TEXT("roll below saturated chance dodges"),RPGBossReactiveDodge::ShouldDodge(true,MAX_int32,.999,C));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossCueJitterSeedAndIndexVariation,
    "OneBossFight.Framework.CueJitter.SeedAndIndexVariation", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossCueJitterSeedAndIndexVariation::RunTest(const FString&)
{
    using RPGBossCueJitter::Time;
    const double Baseline=Time(123,7,1.,.2,.8,1.2);
    bool bSeedChanged=false, bIndexChanged=false;
    for (int32 Seed=124;Seed<156;++Seed) bSeedChanged|=Time(Seed,7,1.,.2,.8,1.2)!=Baseline;
    for (int32 Index=8;Index<40;++Index) bIndexChanged|=Time(123,Index,1.,.2,.8,1.2)!=Baseline;
    TestTrue(TEXT("at least one alternate seed changes the deterministic sample"),bSeedChanged);
    TestTrue(TEXT("at least one alternate cue index changes the deterministic sample"),bIndexChanged);
    for (int32 Index=0;Index<64;++Index)
    {
        const double Value=Time(123,Index,1.,.2,.8,1.2);
        TestTrue(TEXT("cue jitter remains inside authored safe interval"),Value>=.8&&Value<=1.2);
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossCueJitterExactSafeClamps,
    "OneBossFight.Framework.CueJitter.ExactSafeClamps", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossCueJitterExactSafeClamps::RunTest(const FString&)
{
    TestEqual(TEXT("zero jitter below safe range clamps exactly to minimum"),RPGBossCueJitter::Time(1,0,-1.,0.,.5,1.5),.5);
    TestEqual(TEXT("zero jitter above safe range clamps exactly to maximum"),RPGBossCueJitter::Time(1,0,2.,0.,.5,1.5),1.5);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossDefenseCooldownAdjacentBoundary,
    "OneBossFight.Framework.Defense.CooldownAdjacentBoundary", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossDefenseCooldownAdjacentBoundary::RunTest(const FString&)
{
    const double Before=std::nextafter(RPGBossDefense::MinCooldownSeconds,0.);
    const double After=std::nextafter(RPGBossDefense::MinCooldownSeconds,std::numeric_limits<double>::infinity());
    TestFalse(TEXT("immediately below minimum cooldown is rejected"),RPGBossDefense::CooldownOk(Before));
    TestTrue(TEXT("exact minimum cooldown is accepted"),RPGBossDefense::CooldownOk(RPGBossDefense::MinCooldownSeconds));
    TestTrue(TEXT("immediately above minimum cooldown is accepted"),RPGBossDefense::CooldownOk(After));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossFatigueMaximumWhiffCount,
    "OneBossFight.Framework.Fatigue.MaximumWhiffCount", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossFatigueMaximumWhiffCount::RunTest(const FString&)
{
    RPGBossFatigue::FConfig C; C.GraceWhiffs=0; C.ReductionPerWhiff=.1; C.MinRateScale=.7;
    const double Scale=RPGBossFatigue::RateScale(MAX_int32,C);
    TestTrue(TEXT("maximum whiff count remains finite"),FMath::IsFinite(Scale));
    TestEqual(TEXT("maximum whiff count clamps at configured floor"),Scale,.7);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossPunishLimiterMaximumCounterFailsClosed,
    "OneBossFight.Framework.PunishLimiter.MaximumCounterFailsClosed", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossPunishLimiterMaximumCounterFailsClosed::RunTest(const FString&)
{
    RPGBossPunishLimiter::FState State; State.Uses=MAX_int32;
    TestFalse(TEXT("maximum corrupt counter cannot use budget"),RPGBossPunishLimiter::CanUse(State,3));
    TestFalse(TEXT("maximum corrupt counter cannot be incremented"),RPGBossPunishLimiter::RecordUse(State,3));
    TestEqual(TEXT("refusal preserves maximum counter"),State.Uses,MAX_int32);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossReactiveDodgeNegativeHitCountFailsClosed,
    "OneBossFight.Framework.ReactiveDodge.NegativeHitCountFailsClosed", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossReactiveDodgeNegativeHitCountFailsClosed::RunTest(const FString&)
{
    RPGBossReactiveDodge::FConfig C; C.HitsToStart=0;
    TestEqual(TEXT("negative recent-hit count produces zero chance"),RPGBossReactiveDodge::Chance(true,MIN_int32,C),0.);
    TestFalse(TEXT("negative hit count cannot trigger dodge"),RPGBossReactiveDodge::ShouldDodge(true,MIN_int32,0.,C));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossRetreatNonfiniteThresholdsFailClosed,
    "OneBossFight.Framework.Retreat.NonfiniteThresholdsFailClosed", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossRetreatNonfiniteThresholdsFailClosed::RunTest(const FString&)
{
    const double NaN=std::numeric_limits<double>::quiet_NaN();
    const double Inf=std::numeric_limits<double>::infinity();
    TestFalse(TEXT("NaN close range fails closed"),RPGBossRetreat::ShouldRetreat(10.,NaN,.8,.5));
    TestFalse(TEXT("infinite threat fails closed"),RPGBossRetreat::ShouldRetreat(10.,20.,Inf,.5));
    TestFalse(TEXT("infinite threshold fails closed"),RPGBossRetreat::ShouldRetreat(10.,20.,.8,Inf));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossGapAndCueNonfiniteInputsFailClosed,
    "OneBossFight.Framework.RuleEdges.NonfiniteInputsFailClosed", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossGapAndCueNonfiniteInputsFailClosed::RunTest(const FString&)
{
    const double NaN=std::numeric_limits<double>::quiet_NaN();
    const double Inf=std::numeric_limits<double>::infinity();
    TestFalse(TEXT("infinite enter range refuses gap close"),RPGBossGapCloser::ShouldClose(false,700.,Inf,800.));
    TestFalse(TEXT("infinite exit range refuses gap close"),RPGBossGapCloser::ShouldClose(false,700.,400.,Inf));
    TestEqual(TEXT("infinite cue base returns fail-closed zero"),RPGBossCueJitter::Time(1,0,Inf,.1,.5,1.5),0.);
    TestEqual(TEXT("NaN cue jitter returns fail-closed zero"),RPGBossCueJitter::Time(1,0,1.,NaN,.5,1.5),0.);
    return true;
}
#endif
