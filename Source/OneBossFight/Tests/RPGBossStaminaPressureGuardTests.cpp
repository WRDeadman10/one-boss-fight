// Copyright One Boss Fight. All Rights Reserved.
// BL-61 (lane BL, X-2190): RPGBossStaminaPressure guards not already covered (fraction <0 and max pressure >3 are): threshold <=0 / >1, max pressure <0,
// non-finite inputs, fraction >1; exact boundaries. Observability: fraction >1 and threshold == 0 are EQUIVALENT mutants (the clamped ramp already gives 0),
// so those asserts document behaviour; +Inf threshold is equivalent too (BL-86: caught by > 1), and NaN threshold pins IsFinite. The remaining cases
// discriminate. Asserts existing behaviour only.
#include "Player/RPGBossStaminaPressureRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossStaminaPressureGuards, "OneBossFight.Framework.StaminaPressure.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossStaminaPressureGuards::RunTest(const FString&)
{
    using RPGBossStaminaPressure::Pressure;
    const double NaN = std::numeric_limits<double>::quiet_NaN();
    const double Inf = std::numeric_limits<double>::infinity();

    // Controls and exact boundaries.
    TestEqual(TEXT("control: empty stamina gives full pressure 1"), Pressure(0.), 1.);
    TestEqual(TEXT("control: half-way below the threshold gives 0.5"), Pressure(.2), .5);
    TestEqual(TEXT("threshold exactly 1 is accepted"), Pressure(0., 1., 1.), 1.);
    TestEqual(TEXT("max pressure exactly 3 is accepted"), Pressure(0., .4, 3.), 3.);
    TestEqual(TEXT("max pressure exactly 0 is accepted (gives 0)"), Pressure(0., .4, 0.), 0.);

    // Discriminating guards (each would give a non-zero value without its guard).
    TestEqual(TEXT("negative threshold gives 0"), Pressure(.2, -.1, 1.), 0.);
    TestEqual(TEXT("threshold above 1 gives 0"), Pressure(.2, 1.5, 1.), 0.);
    TestEqual(TEXT("negative max pressure gives 0"), Pressure(0., .4, -.1), 0.);
    TestEqual(TEXT("NaN stamina gives 0"), Pressure(NaN), 0.);
    // BL-86 correction: +Inf threshold is EQUIVALENT (LowThreshold > 1 also refuses it); a NaN threshold is the case that pins IsFinite
    // (without the guard (NaN-.2)/NaN clamps to 1 -> pressure 1).
    TestEqual(TEXT("+Inf threshold gives 0 (equivalent)"), Pressure(.2, Inf, 1.), 0.);
    TestEqual(TEXT("NaN threshold gives 0 (discriminates)"), Pressure(.2, NaN, 1.), 0.);
    TestEqual(TEXT("NaN max pressure gives 0"), Pressure(0., .4, NaN), 0.);

    // Equivalent mutants (documented): 0 with or without the guard.
    TestEqual(TEXT("threshold 0 gives 0 (equivalent: (0-0.2)/0 = -Inf clamps to 0)"), Pressure(.2, 0., 1.), 0.);
    TestEqual(TEXT("stamina above 1 gives 0 (equivalent: the ramp is negative and clamps to 0)"), Pressure(1.1), 0.);
    return true;
}
#endif
