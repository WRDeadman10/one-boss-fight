// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossAggroRules.h"
#include "Player/RPGBossGapCloserRules.h"
#include "Player/RPGBossRetreatRules.h"
#include "Player/RPGBleedRules.h"
#include "Misc/AutomationTest.h"
#include <cmath>
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossRetreatAdjacentRangeAndThreat,
    "OneBossFight.Framework.Retreat.AdjacentRangeAndThreat",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossRetreatAdjacentRangeAndThreat::RunTest(const FString&)
{
    const double BelowRange=std::nextafter(150.,-std::numeric_limits<double>::infinity());
    const double AboveRange=std::nextafter(150.,std::numeric_limits<double>::infinity());
    const double BelowThreat=std::nextafter(.7,-std::numeric_limits<double>::infinity());
    TestTrue(TEXT("one representable step below close range retreats"),RPGBossRetreat::ShouldRetreat(BelowRange,150.,.7,.7));
    TestFalse(TEXT("exact close-range equality does not retreat"),RPGBossRetreat::ShouldRetreat(150.,150.,.7,.7));
    TestFalse(TEXT("one representable step above close range does not retreat"),RPGBossRetreat::ShouldRetreat(AboveRange,150.,.7,.7));
    TestFalse(TEXT("one representable step below a custom threat threshold does not retreat"),RPGBossRetreat::ShouldRetreat(100.,150.,BelowThreat,.7));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossBleedExactThresholdCrossing,
    "OneBossFight.Framework.Bleed.ExactThresholdCrossing",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossBleedExactThresholdCrossing::RunTest(const FString&)
{
    RPGBleedRules::FConfig Config;
    RPGBleedRules::FState Below; Below.Threshold=Config.InitialThreshold;
    TestEqual(TEXT("one representable amount below threshold only adds buildup"),static_cast<uint8>(RPGBleedRules::Apply(Below,Config,std::nextafter(Config.InitialThreshold,0.f),false,false,false,false)),static_cast<uint8>(RPGBleedRules::EResult::Added));
    TestEqual(TEXT("below-threshold buildup remains present"),Below.Buildup,std::nextafter(Config.InitialThreshold,0.f));
    RPGBleedRules::FState At; At.Threshold=Config.InitialThreshold;
    TestEqual(TEXT("exact threshold amount procs"),static_cast<uint8>(RPGBleedRules::Apply(At,Config,Config.InitialThreshold,false,false,false,false)),static_cast<uint8>(RPGBleedRules::EResult::Proc));
    TestEqual(TEXT("exact threshold proc increments once"),At.Procs,1);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossAggroRangeAdjacentBoundaries,
    "OneBossFight.Framework.Aggro.RangeAdjacentBoundaries",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossAggroRangeAdjacentBoundaries::RunTest(const FString&)
{
    using RPGBossAggro::EBand;
    const double Below250=std::nextafter(250.,-std::numeric_limits<double>::infinity());
    const double Below300=std::nextafter(300.,-std::numeric_limits<double>::infinity());
    const double Above600=std::nextafter(600.,std::numeric_limits<double>::infinity());
    const double Above700=std::nextafter(700.,std::numeric_limits<double>::infinity());
    TestTrue(TEXT("exact close-entry threshold stays balanced"),RPGBossAggro::Step(EBand::Balanced,250.,false,false)==EBand::Balanced);
    TestTrue(TEXT("one representable step below close-entry threshold enters close"),RPGBossAggro::Step(EBand::Balanced,Below250,false,false)==EBand::Close);
    TestTrue(TEXT("close band persists just below exit threshold"),RPGBossAggro::Step(EBand::Close,Below300,false,false)==EBand::Close);
    TestTrue(TEXT("close band exits exactly at exit threshold"),RPGBossAggro::Step(EBand::Close,300.,false,false)==EBand::Balanced);
    TestTrue(TEXT("far band exits exactly at exit threshold"),RPGBossAggro::Step(EBand::Far,600.,false,false)==EBand::Balanced);
    TestTrue(TEXT("far band persists one representable step above exit threshold"),RPGBossAggro::Step(EBand::Far,Above600,false,false)==EBand::Far);
    TestTrue(TEXT("exact far-entry threshold stays balanced"),RPGBossAggro::Step(EBand::Balanced,700.,false,false)==EBand::Balanced);
    TestTrue(TEXT("one representable step above far-entry threshold enters far"),RPGBossAggro::Step(EBand::Balanced,Above700,false,false)==EBand::Far);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossGapCloserExitAdjacentRepresentable,
    "OneBossFight.Framework.GapCloser.ExitAdjacentRepresentable",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossGapCloserExitAdjacentRepresentable::RunTest(const FString&)
{
    const double Below=std::nextafter(600.,-std::numeric_limits<double>::infinity());
    const double Above=std::nextafter(600.,std::numeric_limits<double>::infinity());
    TestFalse(TEXT("one representable step below exit does not start a new chase"),RPGBossGapCloser::ShouldClose(false,Below,250.,600.));
    TestFalse(TEXT("exact exit equality does not start a new chase"),RPGBossGapCloser::ShouldClose(false,600.,250.,600.));
    TestTrue(TEXT("one representable step above exit starts a new chase"),RPGBossGapCloser::ShouldClose(false,Above,250.,600.));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossGapCloserEnterAdjacentAndCollapsedBand,
    "OneBossFight.Framework.GapCloser.EnterAdjacentAndCollapsedBand",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossGapCloserEnterAdjacentAndCollapsedBand::RunTest(const FString&)
{
    const double Below=std::nextafter(250.,-std::numeric_limits<double>::infinity());
    const double Above=std::nextafter(250.,std::numeric_limits<double>::infinity());
    TestFalse(TEXT("active chase stops one representable step below enter"),RPGBossGapCloser::ShouldClose(true,Below,250.,600.));
    TestFalse(TEXT("active chase stops at exact enter equality"),RPGBossGapCloser::ShouldClose(true,250.,250.,600.));
    TestTrue(TEXT("active chase continues one representable step above enter"),RPGBossGapCloser::ShouldClose(true,Above,250.,600.));
    TestTrue(TEXT("equal thresholds are accepted and use the strict greater-than edge"),RPGBossGapCloser::ShouldClose(false,Above,250.,250.));
    return true;
}
#endif
