// Copyright One Boss Fight. All Rights Reserved.
// BL-11 (lane BL, X-2165/X-2168): RPGBossArenaEdge guard clauses confirmed untested (NaN Boss/Center, negative radius/margin). Asserts existing behaviour only.
#include "Player/RPGBossArenaEdgeRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossArenaEdgeGuards, "OneBossFight.Framework.ArenaEdge.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossArenaEdgeGuards::RunTest(const FString&)
{
    using RPGBossArenaEdge::Evaluate;
    using RPGBossArenaEdge::FResult;
    const double NaN = std::numeric_limits<double>::quiet_NaN();
    // Boss 950 cm from the centre of a 1000 cm arena with a 200 cm margin: inside the margin, so a valid call has pressure.
    const FVector2D Boss(950., 0.), Center(0., 0.);

    const FResult Control = Evaluate(Boss, Center, 1000., 200.);
    TestTrue(TEXT("control: valid inputs give positive pressure"), Control.Pressure > 0.);
    TestTrue(TEXT("control: valid inputs give an inward heading"), Control.Inward.Equals(FVector2D(-1., 0.), 1.e-9));

    auto ExpectEmpty = [this](const TCHAR* What, const FResult& R)
    {
        TestEqual(*FString::Printf(TEXT("%s: zero pressure"), What), R.Pressure, 0.);
        TestTrue(*FString::Printf(TEXT("%s: zero heading"), What), R.Inward.IsZero());
    };
    // BL-86 correction: the four NaN Boss/Center cases are EQUIVALENT mutants (a NaN component makes Distance NaN, and the IsFinite(Distance) check at
    // :14 returns the empty result anyway); they document behaviour.
    ExpectEmpty(TEXT("NaN Boss X"), Evaluate(FVector2D(NaN, 0.), Center, 1000., 200.));
    ExpectEmpty(TEXT("NaN Boss Y"), Evaluate(FVector2D(950., NaN), Center, 1000., 200.));
    ExpectEmpty(TEXT("NaN Center X"), Evaluate(Boss, FVector2D(NaN, 0.), 1000., 200.));
    ExpectEmpty(TEXT("NaN Center Y"), Evaluate(Boss, FVector2D(0., NaN), 1000., 200.));
    ExpectEmpty(TEXT("negative arena radius"), Evaluate(Boss, Center, -1000., 200.));
    ExpectEmpty(TEXT("negative margin"), Evaluate(Boss, Center, 1000., -200.));
    // BL-86 missed gap: an infinite margin discriminates (without IsFinite(Margin): Clamp((Inf-50)/Inf = NaN) gives 1 pressure).
    ExpectEmpty(TEXT("+Inf margin"), Evaluate(Boss, Center, 1000., std::numeric_limits<double>::infinity()));
    return true;
}
#endif
