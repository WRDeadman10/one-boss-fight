// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGParryRules.h"
#include "Misc/AutomationTest.h"
#include <cmath>
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FPlayerParryAdjacentWindowBoundaryTest,
    "OneBossFight.Framework.Parry.AdjacentWindowBoundary",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FPlayerParryAdjacentWindowBoundaryTest::RunTest(const FString&)
{
    RPGParry::FState State;
    constexpr double OpenedAt = 10.;
    constexpr double Window = .25;
    TestTrue(TEXT("press opens the test window"), RPGParry::Press(State, OpenedAt, Window, .7));
    const double Closing = OpenedAt + Window;
    const double JustBefore = std::nextafter(Closing, OpenedAt);
    const double JustAfter = std::nextafter(Closing, std::numeric_limits<double>::infinity());
    TestTrue(TEXT("the adjacent representable instant before close is open"), RPGParry::IsOpen(State, JustBefore, Window));
    TestFalse(TEXT("the exact close instant is excluded"), RPGParry::IsOpen(State, Closing, Window));
    TestFalse(TEXT("the adjacent representable instant after close is closed"), RPGParry::IsOpen(State, JustAfter, Window));
    return true;
}
#endif
