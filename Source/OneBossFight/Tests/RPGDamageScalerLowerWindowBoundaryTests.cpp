// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGDamageScale.h"
#include "Misc/AutomationTest.h"
#include <cmath>
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDamageScalerLowerWindowBoundaryTest,
    "OneBossFight.Combat.DamageScaler.LowerWindowBoundary",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FDamageScalerLowerWindowBoundaryTest::RunTest(const FString&)
{
    constexpr double LossTime = 10.;
    constexpr double Window = FRPGDamageScaler::Window;
    FRPGDamageScaler AtBoundary;
    AtBoundary.OnLoss(LossTime, 20.);
    TestEqual(TEXT("hit exactly one window before the loss still matches"),
        AtBoundary.OnHit(LossTime - Window, .5f), 10.);

    FRPGDamageScaler JustOutside;
    JustOutside.OnLoss(LossTime, 20.);
    const double Outside = std::nextafter(LossTime - Window, -std::numeric_limits<double>::infinity());
    TestEqual(TEXT("hit immediately before the lower matching boundary does not match"),
        JustOutside.OnHit(Outside, .5f), 0.);
    return true;
}
#endif
