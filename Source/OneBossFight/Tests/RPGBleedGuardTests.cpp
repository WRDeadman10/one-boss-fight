// Copyright One Boss Fight. All Rights Reserved.
// BL-06 (lane BL, X-2164): RPGBleedRules guard clauses that no other test asserted (BL-01..05 audit). Asserts existing behaviour only.
#include "Player/RPGBleedRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
namespace
{
    bool SameFloat(float A, float B) { return (FMath::IsNaN(A) && FMath::IsNaN(B)) || A == B; }
    bool SameState(const RPGBleedRules::FState& A, const RPGBleedRules::FState& B)
    {
        return SameFloat(A.Buildup, B.Buildup) && SameFloat(A.Threshold, B.Threshold) && A.Procs == B.Procs;
    }
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBleedGuards, "OneBossFight.Framework.Bleed.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBleedGuards::RunTest(const FString&)
{
    using namespace RPGBleedRules;
    const float NaN = std::numeric_limits<float>::quiet_NaN();
    const float Inf = std::numeric_limits<float>::infinity();

    // Apply: every invalid amount / config / state returns IgnoredAmount and leaves the state exactly as it was.
    auto ExpectIgnored = [this](const TCHAR* What, FState State, const FConfig& Config, float Amount)
    {
        const FState Before = State;
        TestTrue(What, Apply(State, Config, Amount, false, false, false, false) == EResult::IgnoredAmount);
        TestTrue(*FString::Printf(TEXT("%s: state unchanged"), What), SameState(State, Before));
    };
    const FConfig Good;
    const FState Fresh;
    ExpectIgnored(TEXT("zero amount"), Fresh, Good, 0.f);
    ExpectIgnored(TEXT("negative finite amount"), Fresh, Good, -5.f);
    ExpectIgnored(TEXT("NaN amount"), Fresh, Good, NaN);
    ExpectIgnored(TEXT("positive infinite amount"), Fresh, Good, Inf);
    ExpectIgnored(TEXT("negative infinite amount"), Fresh, Good, -Inf);
    {
        FConfig C; C.InitialThreshold = 0.f; ExpectIgnored(TEXT("InitialThreshold 0"), Fresh, C, 20.f);
        C.InitialThreshold = -1.f; ExpectIgnored(TEXT("InitialThreshold negative"), Fresh, C, 20.f);
        C.InitialThreshold = NaN; ExpectIgnored(TEXT("InitialThreshold NaN"), Fresh, C, 20.f);
        C.InitialThreshold = Inf; ExpectIgnored(TEXT("InitialThreshold positive infinite"), Fresh, C, 20.f);
        C.InitialThreshold = -Inf; ExpectIgnored(TEXT("InitialThreshold negative infinite"), Fresh, C, 20.f);
    }
    {
        FConfig C; C.ThresholdIncrease = -1.f; ExpectIgnored(TEXT("ThresholdIncrease negative"), Fresh, C, 20.f);
        C.ThresholdIncrease = NaN; ExpectIgnored(TEXT("ThresholdIncrease NaN"), Fresh, C, 20.f);
        C.ThresholdIncrease = Inf; ExpectIgnored(TEXT("ThresholdIncrease infinite"), Fresh, C, 20.f);
        C.ThresholdIncrease = -Inf; ExpectIgnored(TEXT("ThresholdIncrease negative infinite"), Fresh, C, 20.f);
    }
    {
        FConfig C; C.ThresholdMax = 99.f; ExpectIgnored(TEXT("ThresholdMax below InitialThreshold"), Fresh, C, 20.f);
        C.ThresholdMax = -Inf; ExpectIgnored(TEXT("ThresholdMax negative infinite"), Fresh, C, 20.f);
        C.ThresholdMax = NaN; ExpectIgnored(TEXT("ThresholdMax NaN"), Fresh, C, 20.f);
        C.ThresholdMax = Inf; ExpectIgnored(TEXT("ThresholdMax positive infinite"), Fresh, C, 20.f);
    }
    {
        FConfig C; C.HpFraction = -0.01f; ExpectIgnored(TEXT("HpFraction negative"), Fresh, C, 20.f);
        C.HpFraction = NaN; ExpectIgnored(TEXT("HpFraction NaN"), Fresh, C, 20.f);
        C.HpFraction = Inf; ExpectIgnored(TEXT("HpFraction infinite"), Fresh, C, 20.f);
    }
    {
        FState S; S.Buildup = -1.f; ExpectIgnored(TEXT("state Buildup negative"), S, Good, 20.f);
        S.Buildup = NaN; ExpectIgnored(TEXT("state Buildup NaN"), S, Good, 20.f);
        S.Buildup = Inf; ExpectIgnored(TEXT("state Buildup infinite"), S, Good, 20.f);
    }
    {
        FState S; S.Threshold = -1.f; ExpectIgnored(TEXT("state Threshold negative"), S, Good, 20.f);
        S.Threshold = 0.f; ExpectIgnored(TEXT("state Threshold 0"), S, Good, 20.f);
        S.Threshold = NaN; ExpectIgnored(TEXT("state Threshold NaN"), S, Good, 20.f);
        S.Threshold = Inf; ExpectIgnored(TEXT("state Threshold infinite"), S, Good, 20.f);
        S.Threshold = -Inf; ExpectIgnored(TEXT("state Threshold negative infinite"), S, Good, 20.f);
    }
    {
        FState S; S.Procs = -1; ExpectIgnored(TEXT("state Procs negative"), S, Good, 20.f);
    }
    {
        FState S; // positive control: a valid hit is added, so the cases above fail on their guard, not on the inputs
        TestTrue(TEXT("control: valid hit is Added"), Apply(S, Good, 20.f, false, false, false, false) == EResult::Added);
    }

    // ProcDamage: invalid inputs give 0.
    TestEqual(TEXT("ProcDamage MaxHealth 0"), ProcDamage(0.f, 100.f, Good), 0.f);
    TestEqual(TEXT("ProcDamage MaxHealth negative"), ProcDamage(-100.f, 100.f, Good), 0.f);
    TestEqual(TEXT("ProcDamage Health 0"), ProcDamage(2000.f, 0.f, Good), 0.f);
    TestEqual(TEXT("ProcDamage Health negative"), ProcDamage(2000.f, -5.f, Good), 0.f);
    TestEqual(TEXT("ProcDamage MaxHealth NaN"), ProcDamage(NaN, 100.f, Good), 0.f);
    TestEqual(TEXT("ProcDamage MaxHealth infinite"), ProcDamage(Inf, 100.f, Good), 0.f);
    TestEqual(TEXT("ProcDamage MaxHealth negative infinite"), ProcDamage(-Inf, 100.f, Good), 0.f);
    TestEqual(TEXT("ProcDamage Health NaN"), ProcDamage(2000.f, NaN, Good), 0.f);
    TestEqual(TEXT("ProcDamage Health infinite"), ProcDamage(2000.f, Inf, Good), 0.f);
    TestEqual(TEXT("ProcDamage Health negative infinite"), ProcDamage(2000.f, -Inf, Good), 0.f);
    {
        FConfig C; C.HpFraction = -0.5f; TestEqual(TEXT("ProcDamage HpFraction negative"), ProcDamage(2000.f, 2000.f, C), 0.f);
        C.HpFraction = NaN; TestEqual(TEXT("ProcDamage HpFraction NaN"), ProcDamage(2000.f, 2000.f, C), 0.f);
        C.HpFraction = Inf; TestEqual(TEXT("ProcDamage HpFraction infinite"), ProcDamage(2000.f, 2000.f, C), 0.f);
        C.HpFraction = -Inf; TestEqual(TEXT("ProcDamage HpFraction negative infinite"), ProcDamage(2000.f, 2000.f, C), 0.f);
    }
    TestEqual(TEXT("control: ProcDamage valid"), ProcDamage(2000.f, 2000.f, Good), 60.f);

    // Name: exact text for all seven results and the fallback for an out-of-range value.
    TestEqual(TEXT("Name Added"), FString(Name(EResult::Added)), FString(TEXT("added")));
    TestEqual(TEXT("Name Proc"), FString(Name(EResult::Proc)), FString(TEXT("proc")));
    TestEqual(TEXT("Name IgnoredAmount"), FString(Name(EResult::IgnoredAmount)), FString(TEXT("no buildup")));
    TestEqual(TEXT("Name IgnoredDead"), FString(Name(EResult::IgnoredDead)), FString(TEXT("dead")));
    TestEqual(TEXT("Name IgnoredDormant"), FString(Name(EResult::IgnoredDormant)), FString(TEXT("dormant")));
    TestEqual(TEXT("Name IgnoredTransition"), FString(Name(EResult::IgnoredTransition)), FString(TEXT("transition")));
    TestEqual(TEXT("Name IgnoredSameFrame"), FString(Name(EResult::IgnoredSameFrame)), FString(TEXT("same frame as a proc")));
    TestEqual(TEXT("Name out-of-range falls back to ?"), FString(Name(static_cast<EResult>(200))), FString(TEXT("?")));
    return true;
}
#endif
