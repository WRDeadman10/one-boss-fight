// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGDamageScale.h"
#include "Player/RPGBleedRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossDamageScalerRejectsNonfiniteLoss,
    "OneBossFight.Framework.DamageScaler.NonfiniteLoss", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossDamageScalerRejectsNonfiniteLoss::RunTest(const FString&)
{
    FRPGDamageScaler Scaler;
    const double NaN=std::numeric_limits<double>::quiet_NaN(), Inf=std::numeric_limits<double>::infinity();
    TestEqual(TEXT("NaN loss time returns no adjustment"),Scaler.OnLoss(NaN,10.),0.);
    TestEqual(TEXT("infinite loss amount returns no adjustment"),Scaler.OnLoss(1.,Inf),0.);
    TestEqual(TEXT("invalid losses are not queued"),Scaler.Losses.Num(),0);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossDamageScalerNonfiniteHitMultiplierClaimsLoss,
    "OneBossFight.Framework.DamageScaler.NonfiniteHitMultiplierClaimsLoss", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossDamageScalerNonfiniteHitMultiplierClaimsLoss::RunTest(const FString&)
{
    FRPGDamageScaler Scaler;
    TestEqual(TEXT("unmatched loss queues without adjustment"),Scaler.OnLoss(2.,100.),0.);
    TestEqual(TEXT("nonfinite multiplier falls back to one and adds no adjustment"),
        Scaler.OnHit(2.,std::numeric_limits<float>::quiet_NaN()),0.);
    TestEqual(TEXT("fallback multiplier claims the matching loss"),Scaler.Losses.Num(),0);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossDamageScalerApplyNonfiniteInputs,
    "OneBossFight.Framework.DamageScaler.ApplyNonfiniteInputs", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossDamageScalerApplyNonfiniteInputs::RunTest(const FString&)
{
    const double Inf=std::numeric_limits<double>::infinity(), NaN=std::numeric_limits<double>::quiet_NaN();
    TestEqual(TEXT("nonfinite adjustment preserves finite health"),FRPGDamageScaler::Apply(50.,Inf,100.),50.);
    TestTrue(TEXT("nonfinite health input is passed through unchanged"),FMath::IsNaN(FRPGDamageScaler::Apply(NaN,1.,100.)));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossBleedExtremeFiniteBuildup,
    "OneBossFight.Framework.Bleed.ExtremeFiniteBuildup", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossBleedExtremeFiniteBuildup::RunTest(const FString&)
{
    RPGBleedRules::FState State; State.Buildup=std::numeric_limits<float>::max();
    const auto Result=RPGBleedRules::Apply(State,RPGBleedRules::FConfig(),std::numeric_limits<float>::max(),false,false,false,false);
    TestTrue(TEXT("finite extreme buildup produces one proc"),Result==RPGBleedRules::EResult::Proc);
    TestEqual(TEXT("overflowed buildup is reset"),State.Buildup,0.f);
    TestEqual(TEXT("proc count increments once"),State.Procs,1);
    TestEqual(TEXT("threshold advances once"),State.Threshold,120.f);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossBleedExternalThresholdAboveConfig,
    "OneBossFight.Framework.Bleed.ExternalThresholdAboveConfig", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossBleedExternalThresholdAboveConfig::RunTest(const FString&)
{
    RPGBleedRules::FState State; State.Threshold=300.f;
    const auto Result=RPGBleedRules::Apply(State,RPGBleedRules::FConfig(),1.f,false,false,false,false);
    TestTrue(TEXT("sub-threshold addition is accepted"),Result==RPGBleedRules::EResult::Added);
    TestEqual(TEXT("externally supplied threshold remains above configured maximum"),State.Threshold,300.f);
    return true;
}
#endif
