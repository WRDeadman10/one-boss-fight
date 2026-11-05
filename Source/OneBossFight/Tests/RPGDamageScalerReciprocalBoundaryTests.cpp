// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGDamageScale.h"
#include "Misc/AutomationTest.h"
#include <cmath>
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDamageScalerReciprocalBoundaryTest,
    "OneBossFight.Combat.DamageScaler.ReciprocalBoundary",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FDamageScalerReciprocalBoundaryTest::RunTest(const FString&)
{
    constexpr double Window = FRPGDamageScaler::Window;
    FRPGDamageScaler AtBoundary;
    AtBoundary.OnHit(5., .5f);
    TestEqual(TEXT("loss at the exact symmetric boundary matches a prior hit"),
        AtBoundary.OnLoss(5. + Window, 20.), 10.);

    FRPGDamageScaler JustOutside;
    JustOutside.OnHit(7., .5f);
    const double Outside = std::nextafter(7. + Window, std::numeric_limits<double>::infinity());
    TestEqual(TEXT("loss one representable instant beyond the symmetric boundary does not match"),
        JustOutside.OnLoss(Outside, 20.), 0.);
    TestEqual(TEXT("out-of-window prior hit is pruned"), JustOutside.Hits.Num(), 0);
    return true;
}
#endif
