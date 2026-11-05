// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGParryRules.h"
#include "Misc/AutomationTest.h"
#include <cmath>
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FPlayerParryCooldownAdjacentBoundaryTest,
    "OneBossFight.Framework.Parry.CooldownAdjacentBoundary",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FPlayerParryCooldownAdjacentBoundaryTest::RunTest(const FString&)
{
    RPGParry::FState State;
    TestTrue(TEXT("initial press is accepted"), RPGParry::Press(State, 1., .25, .7));
    const double ReadyAt = State.ReadyAt;
    const double JustBefore = std::nextafter(ReadyAt, -std::numeric_limits<double>::infinity());
    TestFalse(TEXT("press immediately before cooldown completion is rejected"), RPGParry::Press(State, JustBefore, .25, .7));
    TestEqual(TEXT("rejected adjacent press preserves opening time"), State.OpenedAt, 1.);
    TestTrue(TEXT("press at exact cooldown completion is accepted"), RPGParry::Press(State, ReadyAt, .25, .7));
    TestEqual(TEXT("accepted press opens at the exact cooldown endpoint"), State.OpenedAt, ReadyAt);
    return true;
}
#endif
