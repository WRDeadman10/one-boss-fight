// Copyright One Boss Fight. All Rights Reserved.
// BL-71 (lane BL, X-2193): RPGBossWarpCurve::Fraction guards: NaN/Inf T01 and OvershootAmount, negative OvershootAmount, exact supported overshoot bounds
// 0 and 0.5, and the invalid ECurve fallback. Endpoints/midpoints, finite time clamp, an overshoot amount above 0.5 and the overshoot shape are already
// covered by RPGBossWarpCurveRulesTests.cpp and not repeated. Each invalid case discriminates (without its guard a non-zero value would be returned).
// Asserts existing behaviour only.
#include "Player/RPGBossWarpCurveRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossWarpCurveGuards, "OneBossFight.Framework.WarpCurve.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossWarpCurveGuards::RunTest(const FString&)
{
    using namespace RPGBossWarpCurve;
    const double NaN = std::numeric_limits<double>::quiet_NaN();
    const double Inf = std::numeric_limits<double>::infinity();

    TestEqual(TEXT("control: linear at 0.5 is 0.5"), Fraction(.5, ECurve::Linear), .5);

    TestEqual(TEXT("NaN T01 gives 0"), Fraction(NaN, ECurve::Linear), 0.);
    TestEqual(TEXT("+Inf T01 gives 0 (would clamp to 1)"), Fraction(Inf, ECurve::Linear), 0.);
    TestEqual(TEXT("NaN overshoot amount gives 0"), Fraction(.5, ECurve::Linear, NaN), 0.);
    TestEqual(TEXT("+Inf overshoot amount gives 0"), Fraction(.5, ECurve::Linear, Inf), 0.);
    TestEqual(TEXT("negative overshoot amount gives 0"), Fraction(.5, ECurve::Linear, -.01), 0.);

    // Exact supported overshoot bounds are accepted.
    TestEqual(TEXT("overshoot amount 0 accepted (ends at 1)"), Fraction(1., ECurve::Overshoot, 0.), 1.);
    TestEqual(TEXT("overshoot amount 0.5 accepted (ends at 1)"), Fraction(1., ECurve::Overshoot, .5), 1.);
    TestTrue(TEXT("overshoot amount 0.5 still overshoots mid-way"), Fraction(.5, ECurve::Overshoot, .5) > 1.);

    // An out-of-range ECurve value falls back to 0.
    TestEqual(TEXT("invalid ECurve falls back to 0"), Fraction(.5, static_cast<ECurve>(99)), 0.);
    return true;
}
#endif
