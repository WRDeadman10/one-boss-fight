// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossStrafeRules.h"
#include "Misc/AutomationTest.h"
#include <cmath>
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossStrafeHoldBoundaryMutationTest,
    "OneBossFight.Framework.Strafe.HoldBoundaryMutation",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FBossStrafeHoldBoundaryMutationTest::RunTest(const FString&)
{
    const double FirstHold = RPGBossStrafe::HoldSeconds(29, 0, .5, .8);
    const double Before = std::nextafter(FirstHold, -std::numeric_limits<double>::infinity());
    TestTrue(TEXT("direction remains unchanged immediately before the generated hold boundary"),
        RPGBossStrafe::DirectionAt(29, Before, .5, .8) == -RPGBossStrafe::DirectionAt(29, FirstHold, .5, .8));
    return true;
}
#endif
