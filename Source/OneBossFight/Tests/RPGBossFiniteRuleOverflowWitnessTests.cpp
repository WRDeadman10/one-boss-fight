// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossYawProbeRules.h"
#include "Player/RPGBossStrafeRules.h"
#include "Player/RPGBossTrackRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossYawProbePositiveOverflowWitness,
    "OneBossFight.Framework.FiniteRules.YawPositiveOverflowWitness", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossYawProbePositiveOverflowWitness::RunTest(const FString&)
{
    const double Max=std::numeric_limits<double>::max();
    const double Result=RPGBossYawProbe::YawAt(1,Max,Max,4);
    TestTrue(TEXT("finite extreme center and amplitude fail closed to neutral yaw"),FMath::IsFinite(Result));
    TestEqual(TEXT("positive overflow falls back to neutral yaw"),Result,0.);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossStrafeHoldRangeOverflowWitness,
    "OneBossFight.Framework.FiniteRules.StrafeHoldRangeOverflowWitness", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossStrafeHoldRangeOverflowWitness::RunTest(const FString&)
{
    const double Max=std::numeric_limits<double>::max();
    const double Result=RPGBossStrafe::HoldSeconds(17,4,-Max,Max);
    TestTrue(TEXT("finite endpoints whose difference overflows fall back to the finite minimum"),FMath::IsFinite(Result));
    TestEqual(TEXT("overflowed hold range returns its minimum"),Result,-Max);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossRingFrontOverflowFailClosedWitness,
    "OneBossFight.Framework.FiniteRules.RingFrontOverflowFailClosedWitness", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossRingFrontOverflowFailClosedWitness::RunTest(const FString&)
{
    const double Max=std::numeric_limits<double>::max();
    const double Front=RPGBossTrack::RingFront(Max,Max,2.);
    TestTrue(TEXT("finite extreme ring inputs return the invalid-front sentinel"),Front<0.);
    TestFalse(TEXT("ring contact rule rejects nonfinite front"),RPGBossTrack::RingTouches(Front,Front,10.,100.,5.,0.,5.));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossGroundedZOverflowWitness,
    "OneBossFight.Framework.FiniteRules.GroundedZOverflowWitness", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossGroundedZOverflowWitness::RunTest(const FString&)
{
    const double Max=std::numeric_limits<double>::max();
    const double Result=RPGBossTrack::GroundedZ(Max,Max,0.);
    TestTrue(TEXT("finite floor and capsule inputs fall back to finite floor Z"),FMath::IsFinite(Result));
    TestEqual(TEXT("grounded overflow returns floor Z"),Result,Max);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossYawProbeNegativeOverflowWitness,
    "OneBossFight.Framework.FiniteRules.YawNegativeOverflowWitness", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossYawProbeNegativeOverflowWitness::RunTest(const FString&)
{
    const double Max=std::numeric_limits<double>::max();
    const double Result=RPGBossYawProbe::YawAt(3,-Max,Max,4);
    TestTrue(TEXT("finite opposite-sign extreme inputs fail closed to neutral yaw"),FMath::IsFinite(Result));
    TestEqual(TEXT("negative overflow falls back to neutral yaw"),Result,0.);
    return true;
}
#endif
