// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGDamageScale.h"
#include "Misc/AutomationTest.h"
#include <cmath>
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDamageScalerWindowBoundaryMutationTest,
    "OneBossFight.Combat.DamageScaler.WindowBoundaryMutation",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FDamageScalerWindowBoundaryMutationTest::RunTest(const FString&)
{
    FRPGDamageScaler AtBoundary;
    AtBoundary.OnLoss(0., 20.); // lead fix: loss at time 0, so (Window - 0) is exact; (3 + Window) - 3 rounds differently from Window
    TestEqual(TEXT("a hit exactly at the inclusive window boundary matches"),
        AtBoundary.OnHit(FRPGDamageScaler::Window, .5f), 10.);

    FRPGDamageScaler JustOutside;
    JustOutside.OnLoss(0., 20.);
    const double Outside = std::nextafter(FRPGDamageScaler::Window,
        std::numeric_limits<double>::infinity());
    TestEqual(TEXT("the immediately adjacent value beyond the window does not match"),
        JustOutside.OnHit(Outside, .5f), 0.);
    return true;
}
#endif
