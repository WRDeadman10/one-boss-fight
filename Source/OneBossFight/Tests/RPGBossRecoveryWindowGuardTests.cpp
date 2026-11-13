// Copyright One Boss Fight. All Rights Reserved.
// BL-53 (lane BL, X-2186): RPGBossRecoveryWindow guards: ScaledSeconds Scale <0 / >3 rejected and exactly 3 accepted; config fractions <0 / >1 and
// MinSeconds <= 0 rejected; a zero scale returns 0 even with an invalid recovery. NaN scale, the normal zero scale, non-finite / non-positive recovery and
// inverted fractions/range are already covered and not repeated. Asserts existing behaviour only.
#include "Player/RPGBossRecoveryWindowRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossRecoveryWindowGuards, "OneBossFight.Framework.RecoveryWindow.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossRecoveryWindowGuards::RunTest(const FString&)
{
    using namespace RPGBossRecoveryWindow;
    using RPGParryGrade::EGrade;
    const double NaN = std::numeric_limits<double>::quiet_NaN();

    // Scale range.
    TestEqual(TEXT("control: scale 1 on a 1 s recovery, perfect, is 0.65"), ScaledSeconds(EGrade::Perfect, 1., 1.), .65);
    // BL-86 note: Scale<0 is an equivalent mutant (Seconds(Perfect, 1*-.1) refuses the non-positive recovery and also returns -1).
    TestEqual(TEXT("negative scale rejected (equivalent)"), ScaledSeconds(EGrade::Perfect, 1., -.1), -1.);
    TestEqual(TEXT("scale above 3 rejected"), ScaledSeconds(EGrade::Perfect, 1., 3.01), -1.);
    TestEqual(TEXT("scale exactly 3 accepted (1.95 clamped to the 1.5 max)"), ScaledSeconds(EGrade::Perfect, 1., 3.), 1.5);

    // Config clauses, each isolated (ordering stays valid).
    auto ExpectInvalid = [this](const TCHAR* What, const FConfig& C)
    {
        TestFalse(What, C.IsValid());
        TestEqual(*FString::Printf(TEXT("%s: -1"), What), Seconds(EGrade::Perfect, 1., C), -1.);
    };
    TestTrue(TEXT("control: default config is valid"), FConfig().IsValid());
    { FConfig C; C.LateFraction = -.01; ExpectInvalid(TEXT("LateFraction below 0"), C); }
    { FConfig C; C.PerfectFraction = 1.01; ExpectInvalid(TEXT("PerfectFraction above 1"), C); }
    { FConfig C; C.MinSeconds = 0.; ExpectInvalid(TEXT("MinSeconds 0"), C); }
    { FConfig C; C.MinSeconds = -.1; ExpectInvalid(TEXT("negative MinSeconds"), C); }

    // A zero scale is "off" and returns 0 before the recovery is even checked.
    TestEqual(TEXT("zero scale with a negative recovery returns 0"), ScaledSeconds(EGrade::Perfect, -5., 0.), 0.);
    TestEqual(TEXT("zero scale with a NaN recovery returns 0"), ScaledSeconds(EGrade::Perfect, NaN, 0.), 0.);
    TestEqual(TEXT("control: a non-zero scale with a negative recovery is -1"), ScaledSeconds(EGrade::Perfect, -5., 1.), -1.);
    return true;
}
#endif
