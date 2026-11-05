// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossParryFairRules.h"
#include "Misc/AutomationTest.h"
#include <cmath>
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossParryFairAdjacentBoundaryTest,
    "OneBossFight.Framework.BossParryFair.AdjacentBoundary",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FBossParryFairAdjacentBoundaryTest::RunTest(const FString&)
{
    constexpr double Required = .2 + .5 * .25;
    constexpr double Tolerance = 1.e-9;
    const double AtTolerance = Required - Tolerance;
    const double JustOutside = std::nextafter(AtTolerance, -std::numeric_limits<double>::infinity());
    const double JustInside = std::nextafter(AtTolerance, std::numeric_limits<double>::infinity());
    TestTrue(TEXT("the documented tolerance boundary remains fair"), RPGBossParryFair::ParryableOk(0., AtTolerance, 1.));
    TestFalse(TEXT("the adjacent value below the tolerance boundary is unfair"), RPGBossParryFair::ParryableOk(0., JustOutside, 1.));
    TestTrue(TEXT("the adjacent value above the tolerance boundary is fair"), RPGBossParryFair::ParryableOk(0., JustInside, 1.));
    return true;
}
#endif
