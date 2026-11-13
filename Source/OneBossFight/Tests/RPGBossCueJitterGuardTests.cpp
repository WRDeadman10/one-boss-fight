// Copyright One Boss Fight. All Rights Reserved.
// BL-21 (lane BL, X-2171): RPGBossCueJitter guard clauses confirmed untested: CueIndex<0, JitterSeconds<0, reversed and non-finite safe bounds.
// Asserts existing behaviour only.
#include "Player/RPGBossCueJitterRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossCueJitterGuards, "OneBossFight.Framework.CueJitter.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossCueJitterGuards::RunTest(const FString&)
{
    using RPGBossCueJitter::Time;
    const double NaN = std::numeric_limits<double>::quiet_NaN();
    const double Inf = std::numeric_limits<double>::infinity();

    // Control: zero jitter returns the base time exactly (inside the safe interval), so a 0 below comes from a guard.
    TestEqual(TEXT("control: zero jitter returns the base time"), Time(1, 0, 1., 0., 0., 2.), 1.);

    TestEqual(TEXT("negative cue index gives 0"), Time(1, -1, 1., 0., 0., 2.), 0.);
    TestEqual(TEXT("negative jitter gives 0"), Time(1, 0, 1., -.1, 0., 2.), 0.);
    TestEqual(TEXT("reversed safe bounds give 0"), Time(1, 0, 1., 0., 2., 1.5), 0.);
    TestEqual(TEXT("NaN SafeMin gives 0"), Time(1, 0, 1., 0., NaN, 2.), 0.);
    TestEqual(TEXT("NaN SafeMax gives 0"), Time(1, 0, 1., 0., 0., NaN), 0.);
    TestEqual(TEXT("infinite SafeMax gives 0"), Time(1, 0, 1., 0., 0., Inf), 0.);
    TestEqual(TEXT("-Inf SafeMin gives 0"), Time(1, 0, 1., 0., -Inf, 2.), 0.);
    return true;
}
#endif
