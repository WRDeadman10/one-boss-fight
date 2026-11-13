// Copyright One Boss Fight. All Rights Reserved.
// BL-57 (lane BL, X-2188): RPGBossRetreat guards: NaN RangeCm, negative CloseRangeCm, ThreatThreshold <0 and >1 -> false.
// Observability (by hand, against RPGBossRetreatRules.h:10-12): NaN RangeCm, negative CloseRangeCm and ThreatThreshold>1 are EQUIVALENT mutants
// (without the guard the final `Range<Close && Threat>=Threshold` is already false), so those asserts document behaviour. ThreatThreshold<0 DOES
// discriminate: without its guard a close, low-threat case would retreat. Existing negative Range, Threat>1, NaN CloseRange, Inf Threat/Threshold and
// adjacent tests are not repeated. Asserts existing behaviour only.
#include "Player/RPGBossRetreatRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossRetreatGuards, "OneBossFight.Framework.Retreat.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossRetreatGuards::RunTest(const FString&)
{
    using RPGBossRetreat::ShouldRetreat;
    const double NaN = std::numeric_limits<double>::quiet_NaN();

    TestTrue(TEXT("control: close and threatened retreats"), ShouldRetreat(50., 100., .6));

    // Discriminating: threat 0.3 would satisfy a -0.1 threshold, so only the guard refuses.
    TestFalse(TEXT("negative threshold is refused (discriminates)"), ShouldRetreat(50., 100., .3, -.1));

    // Equivalent mutants (documented): false with or without the guard.
    TestFalse(TEXT("NaN range is refused (equivalent: NaN < Close is false)"), ShouldRetreat(NaN, 100., .6));
    TestFalse(TEXT("negative close range is refused (equivalent: Range >= 0 is never below it)"), ShouldRetreat(50., -1., .6));
    TestFalse(TEXT("threshold above 1 is refused (equivalent: Threat <= 1 never reaches it)"), ShouldRetreat(50., 100., 1., 1.1));
    return true;
}
#endif
