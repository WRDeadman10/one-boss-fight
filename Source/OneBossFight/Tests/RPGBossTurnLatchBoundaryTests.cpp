// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossTrackRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
namespace
{
RPGBossTrack::FTurnLatch StartPositiveTurn()
{
    RPGBossTrack::FTurnLatch Latch;
    RPGBossTrack::StepYawLatched(0.f,10.f,90.f,.1f,false,Latch);
    return Latch;
}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossTurnLatchExactThreshold,
    "OneBossFight.Framework.Track.TurnLatch.ExactThreshold",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossTurnLatchExactThreshold::RunTest(const FString&)
{
    auto Latch=StartPositiveTurn();
    RPGBossTrack::StepYawLatched(0.f,-150.f,90.f,.1f,false,Latch);
    TestEqual(TEXT("exact 150 degree back-axis threshold keeps prior direction"),Latch.Dir,1);
    TestEqual(TEXT("exact threshold does not count a reversal"),Latch.Flips,0);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossTurnLatchBelowThresholdReleases,
    "OneBossFight.Framework.Track.TurnLatch.BelowThresholdReleases",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossTurnLatchBelowThresholdReleases::RunTest(const FString&)
{
    auto Latch=StartPositiveTurn();
    RPGBossTrack::StepYawLatched(0.f,-149.99f,90.f,.1f,false,Latch);
    TestEqual(TEXT("angle just below 150 degrees releases prior direction"),Latch.Dir,-1);
    TestEqual(TEXT("released reversal increments the flip count"),Latch.Flips,1);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossTurnLatchAboveThresholdRetains,
    "OneBossFight.Framework.Track.TurnLatch.AboveThresholdRetains",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossTurnLatchAboveThresholdRetains::RunTest(const FString&)
{
    auto Latch=StartPositiveTurn();
    RPGBossTrack::StepYawLatched(0.f,-150.01f,90.f,.1f,false,Latch);
    TestEqual(TEXT("angle just above 150 degrees keeps prior direction"),Latch.Dir,1);
    TestEqual(TEXT("retained turn does not count a flip"),Latch.Flips,0);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossTurnLatchZeroAndWrap,
    "OneBossFight.Framework.Track.TurnLatch.ZeroAndWrap",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossTurnLatchZeroAndWrap::RunTest(const FString&)
{
    RPGBossTrack::FTurnLatch Latch;
    Latch.Dir=1; Latch.LastDir=1;
    const float Zero=RPGBossTrack::StepYawLatched(0.f,0.f,90.f,.1f,false,Latch);
    TestTrue(TEXT("zero delta returns zero yaw"),FMath::IsNearlyZero(Zero));
    TestEqual(TEXT("reaching zero clears active direction"),Latch.Dir,0);
    const float AcrossPositive=RPGBossTrack::StepYawLatched(179.f,-179.f,90.f,.1f,false,Latch);
    const float AcrossNegative=RPGBossTrack::StepYawLatched(-179.f,179.f,90.f,.1f,false,Latch);
    TestTrue(TEXT("positive wrap follows the two-degree shortest path"),FMath::IsNearlyEqual(AcrossPositive,-179.f,.001f));
    TestTrue(TEXT("negative wrap follows the two-degree shortest path"),FMath::IsNearlyEqual(AcrossNegative,179.f,.001f));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossTurnLatchRefusalPreservesState,
    "OneBossFight.Framework.Track.TurnLatch.RefusalPreservesState",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossTurnLatchRefusalPreservesState::RunTest(const FString&)
{
    const auto CheckUnchanged=[this](const TCHAR* Label,float Speed,float Dt,bool bCommitted)
    {
        RPGBossTrack::FTurnLatch Latch; Latch.Dir=1; Latch.LastDir=-1; Latch.Flips=4;
        const float Result=RPGBossTrack::StepYawLatched(25.f,-80.f,Speed,Dt,bCommitted,Latch);
        TestEqual(FString::Printf(TEXT("%s returns current yaw"),Label),Result,25.f);
        TestEqual(FString::Printf(TEXT("%s preserves active direction"),Label),Latch.Dir,1);
        TestEqual(FString::Printf(TEXT("%s preserves last direction"),Label),Latch.LastDir,-1);
        TestEqual(FString::Printf(TEXT("%s preserves flip count"),Label),Latch.Flips,4);
    };
    CheckUnchanged(TEXT("committed"),90.f,.1f,true);
    CheckUnchanged(TEXT("zero speed"),0.f,.1f,false);
    CheckUnchanged(TEXT("negative timestep"),90.f,-.1f,false);
    CheckUnchanged(TEXT("nonfinite timestep"),90.f,std::numeric_limits<float>::quiet_NaN(),false);
    return true;
}
#endif
