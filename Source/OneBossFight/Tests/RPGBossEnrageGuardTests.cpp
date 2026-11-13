// Copyright One Boss Fight. All Rights Reserved.
// BL-28 (lane BL, X-2172): RPGBossEnrage MaxDamageScale<1 / MaxSpeedScale<1 fail closed; exact upper bounds 3 / 2 accepted. Asserts existing behaviour only.
#include "Player/RPGBossEnrageRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossEnrageGuards, "OneBossFight.Framework.Enrage.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossEnrageGuards::RunTest(const FString&)
{
    using namespace RPGBossEnrage;

    // Control: the default config at half the ramp is already enraged.
    TestEqual(TEXT("control: default damage at 60 s is 1.25"), DamageScale(60.), 1.25);
    TestEqual(TEXT("control: default speed at 60 s is 1.125"), SpeedScale(60.), 1.125);

    // Below-1 maxima fail closed (checked at the full ramp, where a valid config is enraged).
    {
        FConfig C; C.MaxDamageScale = .99;
        TestFalse(TEXT("MaxDamageScale below 1 is invalid"), C.IsValid());
        TestEqual(TEXT("MaxDamageScale below 1: damage 1"), DamageScale(120., C), 1.);
        TestEqual(TEXT("MaxDamageScale below 1: speed 1"), SpeedScale(120., C), 1.);
        TestEqual(TEXT("MaxDamageScale below 1: progress 0"), Progress(120., C), 0.);
    }
    {
        FConfig C; C.MaxSpeedScale = .99;
        TestFalse(TEXT("MaxSpeedScale below 1 is invalid"), C.IsValid());
        TestEqual(TEXT("MaxSpeedScale below 1: damage 1"), DamageScale(120., C), 1.);
        TestEqual(TEXT("MaxSpeedScale below 1: speed 1"), SpeedScale(120., C), 1.);
    }

    // BL-86 (reviewer claim corrected by hand): the IsFinite(RampSeconds) / IsFinite(MaxSpeedScale) clauses are UNOBSERVABLE: NaN already fails
    // RampSeconds>0 / MaxSpeedScale>=1, and +Inf ramp gives progress 0 (scale 1) while +Inf speed fails <=2. These NaN asserts document behaviour.
    {
        FConfig C; C.RampSeconds = std::numeric_limits<double>::quiet_NaN();
        TestFalse(TEXT("NaN RampSeconds is invalid"), C.IsValid());
        TestEqual(TEXT("NaN RampSeconds: damage 1"), DamageScale(60., C), 1.);
    }
    {
        FConfig C; C.MaxSpeedScale = std::numeric_limits<double>::quiet_NaN();
        TestFalse(TEXT("NaN MaxSpeedScale is invalid"), C.IsValid());
        TestEqual(TEXT("NaN MaxSpeedScale: speed 1"), SpeedScale(60., C), 1.);
    }

    // Exact upper bounds are accepted and reached at the end of the ramp.
    {
        FConfig C; C.MaxDamageScale = 3.;
        TestTrue(TEXT("MaxDamageScale exactly 3 is valid"), C.IsValid());
        TestEqual(TEXT("damage reaches 3 at the end of the ramp"), DamageScale(120., C), 3.);
    }
    {
        FConfig C; C.MaxSpeedScale = 2.;
        TestTrue(TEXT("MaxSpeedScale exactly 2 is valid"), C.IsValid());
        TestEqual(TEXT("speed reaches 2 at the end of the ramp"), SpeedScale(120., C), 2.);
    }
    return true;
}
#endif
