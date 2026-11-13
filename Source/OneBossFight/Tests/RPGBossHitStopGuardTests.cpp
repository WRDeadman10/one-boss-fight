// Copyright One Boss Fight. All Rights Reserved.
// BL-08 (lane BL, X-2164): RPGBossHitStop exact defaults and IsValid clauses that no other test asserted (BL-01..05 audit). Asserts existing behaviour only.
#include "Player/RPGBossHitStopRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossHitStopGuards, "OneBossFight.Framework.HitStop.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossHitStopGuards::RunTest(const FString&)
{
    using namespace RPGBossHitStop;
    using RPGParryGrade::EGrade;
    const double NaN = std::numeric_limits<double>::quiet_NaN();
    const double Inf = std::numeric_limits<double>::infinity();

    // Exact defaults (the existing test only checks their ordering).
    const FConfig Defaults;
    TestEqual(TEXT("default Perfect is 0.12"), Seconds(EGrade::Perfect, Defaults), .12);
    TestEqual(TEXT("default Good is 0.08"), Seconds(EGrade::Good, Defaults), .08);
    TestEqual(TEXT("default Late is 0.04"), Seconds(EGrade::Late, Defaults), .04);

    auto ExpectInvalid = [this](const TCHAR* What, const FConfig& C)
    {
        TestFalse(What, IsValid(C));
        for (EGrade Grade : {EGrade::Perfect, EGrade::Good, EGrade::Late})
        {
            TestEqual(*FString::Printf(TEXT("%s: grade %d gives 0"), What, int32(Grade)), Seconds(Grade, C), 0.);
        }
    };

    // NaN / +Inf / -Inf in each field, one field at a time.
    for (double Bad : {NaN, Inf, -Inf})
    {
        FConfig C; C.PerfectSeconds = Bad; ExpectInvalid(TEXT("non-finite PerfectSeconds"), C);
        C = FConfig(); C.GoodSeconds = Bad; ExpectInvalid(TEXT("non-finite GoodSeconds"), C);
        C = FConfig(); C.LateSeconds = Bad; ExpectInvalid(TEXT("non-finite LateSeconds"), C);
        C = FConfig(); C.MaxSeconds = Bad; ExpectInvalid(TEXT("non-finite MaxSeconds"), C);
    }
    { FConfig C; C.LateSeconds = -.01; ExpectInvalid(TEXT("negative LateSeconds"), C); }
    { FConfig C; C.MaxSeconds = -1.; ExpectInvalid(TEXT("negative MaxSeconds"), C); }
    { FConfig C; C.PerfectSeconds = .07; ExpectInvalid(TEXT("Perfect below Good"), C); }
    { FConfig C; C.GoodSeconds = .03; ExpectInvalid(TEXT("Good below Late"), C); }
    { FConfig C; C.LateSeconds = .09; ExpectInvalid(TEXT("Late above Good"), C); }

    // Equality boundaries are valid.
    { FConfig C; C.PerfectSeconds = C.MaxSeconds = .2; TestTrue(TEXT("Perfect equal to Max is valid"), IsValid(C)); TestEqual(TEXT("Perfect==Max returns Perfect"), Seconds(EGrade::Perfect, C), .2); }
    { FConfig C; C.PerfectSeconds = C.GoodSeconds = C.LateSeconds = .1; TestTrue(TEXT("all grades equal is valid"), IsValid(C)); TestEqual(TEXT("equal grades return the shared value"), Seconds(EGrade::Late, C), .1); }
    { FConfig C; C.LateSeconds = 0.; TestTrue(TEXT("Late zero is valid"), IsValid(C)); }
    { FConfig C; C.PerfectSeconds = C.GoodSeconds = C.LateSeconds = C.MaxSeconds = 0.; TestTrue(TEXT("all zero is valid"), IsValid(C)); TestEqual(TEXT("all zero returns 0"), Seconds(EGrade::Perfect, C), 0.); }
    return true;
}
#endif
