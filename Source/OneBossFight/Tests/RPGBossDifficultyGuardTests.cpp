// Copyright One Boss Fight. All Rights Reserved.
// BL-27 (lane BL, X-2172): RPGBossDifficulty IsValid clauses (non-positive minima, reversed ranges, over-bound maxima, non-finite fields) give the
// neutral scales from Evaluate; boundary-valid controls. Asserts existing behaviour only.
#include "Player/RPGBossDifficultyRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossDifficultyGuards, "OneBossFight.Framework.Difficulty.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossDifficultyGuards::RunTest(const FString&)
{
    using namespace RPGBossDifficulty;
    const double NaN = std::numeric_limits<double>::quiet_NaN();
    const double Inf = std::numeric_limits<double>::infinity();

    // Control: the default config at 0.5 is NOT neutral, so a neutral result below comes from the guard.
    {
        const FScales S = Evaluate(.5);
        TestTrue(TEXT("control: default damage at 0.5 is 1.025"), FMath::IsNearlyEqual(S.Damage, 1.025, 1.e-12));
        TestTrue(TEXT("control: default speed at 0.5 is 1.05"), FMath::IsNearlyEqual(S.Speed, 1.05, 1.e-12));
    }

    auto ExpectNeutral = [this](const TCHAR* What, const FConfig& C)
    {
        TestFalse(What, IsValid(C));
        const FScales S = Evaluate(.5, C);
        TestTrue(*FString::Printf(TEXT("%s: neutral scales"), What), S.Damage == 1. && S.Speed == 1. && S.Telegraph == 1.);
    };

    // Non-positive minima.
    { FConfig C; C.DamageMin = 0.; ExpectNeutral(TEXT("DamageMin 0"), C); }
    { FConfig C; C.DamageMin = -1.; ExpectNeutral(TEXT("DamageMin negative"), C); }
    { FConfig C; C.SpeedMin = 0.; ExpectNeutral(TEXT("SpeedMin 0"), C); }
    { FConfig C; C.SpeedMin = -1.; ExpectNeutral(TEXT("SpeedMin negative"), C); }
    { FConfig C; C.TelegraphMin = 0.; ExpectNeutral(TEXT("TelegraphMin 0"), C); }
    { FConfig C; C.TelegraphMin = -1.; ExpectNeutral(TEXT("TelegraphMin negative"), C); }
    // Reversed ranges.
    { FConfig C; C.DamageMax = .7; ExpectNeutral(TEXT("DamageMax below DamageMin"), C); }
    { FConfig C; C.SpeedMax = .8; ExpectNeutral(TEXT("SpeedMax below SpeedMin"), C); }
    { FConfig C; C.TelegraphMax = .8; ExpectNeutral(TEXT("TelegraphMax below TelegraphMin"), C); }
    // Over-bound maxima.
    { FConfig C; C.DamageMax = 3.01; ExpectNeutral(TEXT("DamageMax above 3"), C); }
    { FConfig C; C.SpeedMax = 2.01; ExpectNeutral(TEXT("SpeedMax above 2"), C); }
    { FConfig C; C.TelegraphMax = 2.01; ExpectNeutral(TEXT("TelegraphMax above 2"), C); }
    // Each field non-finite (NaN, +Inf, -Inf).
    for (double Bad : {NaN, Inf, -Inf})
    {
        FConfig C;
        C = FConfig(); C.DamageMin = Bad; ExpectNeutral(TEXT("non-finite DamageMin"), C);
        C = FConfig(); C.DamageMax = Bad; ExpectNeutral(TEXT("non-finite DamageMax"), C);
        C = FConfig(); C.SpeedMin = Bad; ExpectNeutral(TEXT("non-finite SpeedMin"), C);
        C = FConfig(); C.SpeedMax = Bad; ExpectNeutral(TEXT("non-finite SpeedMax"), C);
        C = FConfig(); C.TelegraphMin = Bad; ExpectNeutral(TEXT("non-finite TelegraphMin"), C);
        C = FConfig(); C.TelegraphMax = Bad; ExpectNeutral(TEXT("non-finite TelegraphMax"), C);
    }

    // Boundary-valid controls: exact upper bounds and equal endpoints are valid.
    {
        FConfig C; C.DamageMax = 3.; C.SpeedMax = 2.; C.TelegraphMax = 2.;
        TestTrue(TEXT("exact upper bounds 3/2/2 are valid"), IsValid(C));
        const FScales S = Evaluate(1., C);
        // Lerp(Min,Max,1) = Min+(Max-Min) may differ from Max by one ulp, so compare with a tight tolerance.
        TestTrue(TEXT("at 1 the exact upper bounds are returned"), FMath::IsNearlyEqual(S.Damage, 3., 1.e-12) && FMath::IsNearlyEqual(S.Speed, 2., 1.e-12) && FMath::IsNearlyEqual(S.Telegraph, 2., 1.e-12));
    }
    {
        FConfig C; C.DamageMax = C.DamageMin; C.SpeedMax = C.SpeedMin; C.TelegraphMax = C.TelegraphMin;
        TestTrue(TEXT("equal endpoints are valid"), IsValid(C));
    }
    return true;
}
#endif
