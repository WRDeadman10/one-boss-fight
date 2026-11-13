// Copyright One Boss Fight. All Rights Reserved.
// BL-38 (lane BL, X-2177): RPGBossMusicIntensity guard clauses: health NaN/Inf/<0/>1 -> 0, boost NaN/negative -> 0 with exact 0 and 1 accepted, phase <= 0 -> 0.
// Asserts existing behaviour only.
#include "Player/RPGBossMusicIntensityRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMusicIntensityGuards, "OneBossFight.Framework.MusicIntensity.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossMusicIntensityGuards::RunTest(const FString&)
{
    using RPGBossMusicIntensity::Evaluate;
    const double NaN = std::numeric_limits<double>::quiet_NaN();
    const double Inf = std::numeric_limits<double>::infinity();

    // Controls: half health in phase 1 is 0.5, in phase 2 the default boost adds 0.25.
    TestEqual(TEXT("control: phase 1 at half health is 0.5"), Evaluate(.5, 1), .5);
    TestEqual(TEXT("control: phase 2 at half health is 0.75"), Evaluate(.5, 2), .75);

    TestEqual(TEXT("NaN health gives 0"), Evaluate(NaN, 1), 0.);
    TestEqual(TEXT("+Inf health gives 0"), Evaluate(Inf, 1), 0.);
    TestEqual(TEXT("negative health gives 0"), Evaluate(-.1, 1), 0.);
    TestEqual(TEXT("health above 1 gives 0"), Evaluate(1.1, 1), 0.);

    TestEqual(TEXT("NaN boost gives 0"), Evaluate(.5, 2, NaN), 0.);
    TestEqual(TEXT("negative boost gives 0"), Evaluate(.5, 2, -.1), 0.);
    TestEqual(TEXT("boost exactly 0 is accepted"), Evaluate(.5, 2, 0.), .5);
    TestEqual(TEXT("boost exactly 1 is accepted (clamped to 1)"), Evaluate(.5, 2, 1.), 1.);

    TestEqual(TEXT("phase 0 gives 0"), Evaluate(.5, 0), 0.);
    TestEqual(TEXT("negative phase gives 0"), Evaluate(.5, -1), 0.);
    return true;
}
#endif
