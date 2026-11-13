// Copyright One Boss Fight. All Rights Reserved.
// BL-46 (lane BL, X-2182): RPGBossPoiseRegen guards not exercised by Rules/ZeroRamp/QueueE: BasePerSecond <0 / >1e6, negative SecondsSinceHit and
// DelaySeconds, DelaySeconds / RampSeconds >1e6, MaxScale <1 / >3, NaN in each otherwise-uncovered parameter; exact MaxScale=3 acceptance.
// (+Inf elapsed and zero ramp are already covered and not repeated.) Asserts existing behaviour only.
#include "Player/RPGBossPoiseRegenRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossPoiseRegenGuards, "OneBossFight.Framework.PoiseRegen.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossPoiseRegenGuards::RunTest(const FString&)
{
    using RPGBossPoiseRegen::Rate;
    const double NaN = std::numeric_limits<double>::quiet_NaN();

    // Controls: 3 s after a hit with a 1 s delay and 2 s ramp the ramp is complete (15 at MaxScale 1.5); MaxScale exactly 3 is accepted (30).
    TestEqual(TEXT("control: full ramp at MaxScale 1.5 is 15"), Rate(10., 3., 1., 2., 1.5), 15.);
    TestEqual(TEXT("MaxScale exactly 3 is accepted"), Rate(10., 3., 1., 2., 3.), 30.);

    // Each invalid parameter gives 0 (the same call is 15 when valid).
    TestEqual(TEXT("negative BasePerSecond"), Rate(-1., 3., 1., 2., 1.5), 0.);
    TestEqual(TEXT("BasePerSecond above 1e6"), Rate(1.e6 + 1., 3., 1., 2., 1.5), 0.);
    TestEqual(TEXT("negative DelaySeconds"), Rate(10., 3., -1., 2., 1.5), 0.);
    TestEqual(TEXT("DelaySeconds above 1e6 (elapsed beyond it)"), Rate(10., 2.e6, 1.e6 + 1., 2., 1.5), 0.);
    TestEqual(TEXT("RampSeconds above 1e6"), Rate(10., 3., 1., 1.e6 + 1., 1.5), 0.);
    TestEqual(TEXT("MaxScale below 1"), Rate(10., 3., 1., 2., .99), 0.);
    TestEqual(TEXT("MaxScale above 3"), Rate(10., 3., 1., 2., 3.01), 0.);
    // Negative elapsed time gives 0. NOTE: this guard is unobservable (a negative elapsed time is always below a non-negative delay,
    // which also returns 0), so the assert documents behaviour rather than discriminating the guard.
    TestEqual(TEXT("negative SecondsSinceHit"), Rate(10., -1., 0., 2., 1.5), 0.);

    // NaN in each parameter not already covered (the existing suite only covers +Inf elapsed).
    TestEqual(TEXT("NaN BasePerSecond"), Rate(NaN, 3., 1., 2., 1.5), 0.);
    TestEqual(TEXT("NaN SecondsSinceHit"), Rate(10., NaN, 1., 2., 1.5), 0.);
    TestEqual(TEXT("NaN DelaySeconds"), Rate(10., 3., NaN, 2., 1.5), 0.);
    TestEqual(TEXT("NaN RampSeconds"), Rate(10., 3., 1., NaN, 1.5), 0.);
    TestEqual(TEXT("NaN MaxScale"), Rate(10., 3., 1., 2., NaN), 0.);
    return true;
}
#endif
