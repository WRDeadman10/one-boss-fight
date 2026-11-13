// Copyright One Boss Fight. All Rights Reserved.
// BL-72 (lane BL, X-2193): RPGBossYawProbe::YawAt guards: NaN/Inf CenterDeg and AmplitudeDeg, Period 0 / negative -> 0, with an ordinary control.
// Observability (by hand against RPGBossYawProbeRules.h:11-15): the NaN/Inf input guards and Period == 0 are EQUIVALENT mutants, because the final
// `IsFinite(Result) ? Result : 0` already returns 0 for them (at sample 1, Inf*sin(pi/2) is +Inf and NaN propagates; x/0 phases give NaN - reason corrected in BL-86). Only a NEGATIVE Period discriminates
// (a finite negative phase would give a non-zero yaw). Existing extrema/periodicity and overflow witnesses are not repeated. Asserts existing behaviour only.
#include "Player/RPGBossYawProbeRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossYawProbeGuards, "OneBossFight.Framework.BossYawProbe.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossYawProbeGuards::RunTest(const FString&)
{
    using RPGBossYawProbe::YawAt;
    const double NaN = std::numeric_limits<double>::quiet_NaN();
    const double Inf = std::numeric_limits<double>::infinity();

    // Control: a quarter period into a 4-sample cycle is the centre plus the amplitude.
    TestTrue(TEXT("control: sample 1 of period 4 is 15"), FMath::IsNearlyEqual(YawAt(1, 10., 5., 4), 15., 1.e-9));

    // Discriminating: a negative period would give 10 + 5*sin(-pi/2) = 5 without its guard.
    TestEqual(TEXT("negative period gives 0"), YawAt(1, 10., 5., -4), 0.);

    // Equivalent mutants (documented): 0 with or without the input guard.
    TestEqual(TEXT("period 0 gives 0 (equivalent)"), YawAt(1, 10., 5., 0), 0.);
    TestEqual(TEXT("NaN centre gives 0 (equivalent)"), YawAt(1, NaN, 5., 4), 0.);
    TestEqual(TEXT("+Inf centre gives 0 (equivalent)"), YawAt(1, Inf, 5., 4), 0.);
    TestEqual(TEXT("NaN amplitude gives 0 (equivalent)"), YawAt(1, 10., NaN, 4), 0.);
    TestEqual(TEXT("+Inf amplitude gives 0 (equivalent)"), YawAt(1, 10., Inf, 4), 0.);
    return true;
}
#endif
