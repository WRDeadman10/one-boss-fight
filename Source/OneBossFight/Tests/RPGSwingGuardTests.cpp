// Copyright One Boss Fight. All Rights Reserved.
// BL-81 (lane BL, X-2196): RPGSwingRules guards not in RPGAutomationTests/RPGCodexTests: invalid ResolveWindow overrides; WindowOpen NaN inputs; StaminaExtra
// NaN inputs; NeedsRefresh NaN inputs and a negative RefreshAfter.
// Observability (by hand): every WindowOpen NaN case and the NeedsRefresh NaN cases are EQUIVALENT mutants (comparisons with NaN are false, so the result
// is false anyway); NaN StaminaNow with a POSITIVE extra is equivalent too (FMath::Max(NaN,0) gives 0). The ResolveWindow overrides, NaN Wanted/PackCost,
// NaN StaminaNow on a refund, and a negative RefreshAfter DISCRIMINATE. Asserts existing behaviour only.
#include "Player/RPGSwingRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGSwingGuardsTest, "OneBossFight.Player.SwingGuards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGSwingGuardsTest::RunTest(const FString&)
{
    using namespace RPGSwingRules;
    const double DNaN = std::numeric_limits<double>::quiet_NaN();
    const float FNaN = std::numeric_limits<float>::quiet_NaN();

    // ResolveWindow: a valid override is used (control); invalid overrides give no window even on a row that has one.
    FRPGWeaponAttackRow Row; Row.HyperArmorStart = .2f; Row.HyperArmorEnd = .5f;
    auto Resolve = [&Row](const FVector2D& O) { float S = 9.f, E = 9.f; ResolveWindow(Row, &O, S, E); return FVector2D(S, E); };
    TestTrue(TEXT("control: a valid override is used"), Resolve(FVector2D(.1, .4)).Equals(FVector2D(.1, .4), 1.e-6));
    TestTrue(TEXT("negative override start gives no window"), Resolve(FVector2D(-.1, .4)).Equals(FVector2D(-1., -1.), 0.));
    TestTrue(TEXT("NaN override start gives no window"), Resolve(FVector2D(DNaN, .4)).Equals(FVector2D(-1., -1.), 0.));
    TestTrue(TEXT("NaN override end gives no window"), Resolve(FVector2D(.1, DNaN)).Equals(FVector2D(-1., -1.), 0.));
    TestTrue(TEXT("override end equal to start gives no window"), Resolve(FVector2D(.3, .3)).Equals(FVector2D(-1., -1.), 0.));
    TestTrue(TEXT("override end before start gives no window"), Resolve(FVector2D(.4, .1)).Equals(FVector2D(-1., -1.), 0.));

    // WindowOpen NaN inputs (equivalent mutants, documented).
    TestTrue(TEXT("control: inside the window is open"), WindowOpen(.2f, .5f, .3f));
    TestFalse(TEXT("NaN start is closed (equivalent)"), WindowOpen(FNaN, .5f, .3f));
    TestFalse(TEXT("NaN end is closed (equivalent)"), WindowOpen(.2f, FNaN, .3f));
    TestFalse(TEXT("NaN position is closed (equivalent)"), WindowOpen(.2f, .5f, FNaN));

    // StaminaExtra NaN inputs.
    TestEqual(TEXT("NaN Wanted gives 0 (discriminates: would be NaN)"), StaminaExtra(FNaN, 15.f, 100.0), 0.f);
    TestEqual(TEXT("NaN PackCost gives 0 (discriminates: would be NaN)"), StaminaExtra(35.f, FNaN, 100.0), 0.f);
    TestEqual(TEXT("NaN StaminaNow on a refund gives 0 (discriminates: would be -5)"), StaminaExtra(10.f, 15.f, DNaN), 0.f);
    TestEqual(TEXT("NaN StaminaNow on a positive extra gives 0 (equivalent)"), StaminaExtra(35.f, 15.f, DNaN), 0.f);

    // NeedsRefresh.
    TestTrue(TEXT("control: 3 s old with a 3 s refresh needs it"), NeedsRefresh(13., 10., 3.f));
    TestFalse(TEXT("negative RefreshAfter is off (discriminates: would be true)"), NeedsRefresh(13., 10., -1.f));
    TestFalse(TEXT("NaN Now is false (equivalent)"), NeedsRefresh(DNaN, 10., 3.f));
    TestFalse(TEXT("NaN AppliedAt is false (equivalent)"), NeedsRefresh(13., DNaN, 3.f));
    TestFalse(TEXT("NaN RefreshAfter is false (equivalent)"), NeedsRefresh(13., 10., FNaN));
    return true;
}
#endif
