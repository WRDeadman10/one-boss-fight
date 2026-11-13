// Copyright One Boss Fight. All Rights Reserved.
// BL-23 (lane BL, X-2171): RPGBossDefense guard clauses confirmed untested: negative play rate, negative backstep, +Inf cooldown. Asserts existing behaviour only.
#include "Player/RPGBossDefenseRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossDefenseGuards, "OneBossFight.Framework.Defense.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossDefenseGuards::RunTest(const FString&)
{
    using namespace RPGBossDefense;
    const double Inf = std::numeric_limits<double>::infinity();

    TestTrue(TEXT("control: 0.5 s at play rate 1 is a fair telegraph"), TelegraphOk(.5, 1.));
    TestFalse(TEXT("negative play rate is not a fair telegraph"), TelegraphOk(.5, -1.));
    TestFalse(TEXT("negative play rate with a negative start is still refused"), TelegraphOk(-.5, -1.));

    TestTrue(TEXT("control: a 100 cm backstep is fair"), BackstepDistanceOk(100.));
    TestFalse(TEXT("negative backstep is refused"), BackstepDistanceOk(-10.));

    TestTrue(TEXT("control: a 3 s cooldown is fair"), CooldownOk(3.));
    TestFalse(TEXT("+Inf cooldown is refused"), CooldownOk(Inf));
    return true;
}
#endif
