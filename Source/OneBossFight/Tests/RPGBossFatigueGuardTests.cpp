// Copyright One Boss Fight. All Rights Reserved.
// BL-31 (lane BL, X-2174): RPGBossFatigue invalid GraceWhiffs, ReductionPerWhiff (<0, >1, non-finite) and MinRateScale (>1, non-finite) return -1.
// Asserts existing behaviour only.
#include "Player/RPGBossFatigueRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossFatigueGuards, "OneBossFight.Framework.Fatigue.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossFatigueGuards::RunTest(const FString&)
{
    using namespace RPGBossFatigue;
    const double NaN = std::numeric_limits<double>::quiet_NaN();
    const double Inf = std::numeric_limits<double>::infinity();

    TestEqual(TEXT("control: 4 whiffs with grace 2 give 0.9"), RateScale(4), .9);

    auto ExpectInvalid = [this](const TCHAR* What, const FConfig& C) { TestEqual(What, RateScale(4, C), -1.); };
    { FConfig C; C.GraceWhiffs = -1; ExpectInvalid(TEXT("negative GraceWhiffs gives -1"), C); }
    { FConfig C; C.ReductionPerWhiff = -.01; ExpectInvalid(TEXT("negative ReductionPerWhiff gives -1"), C); }
    { FConfig C; C.ReductionPerWhiff = 1.01; ExpectInvalid(TEXT("ReductionPerWhiff above 1 gives -1"), C); }
    { FConfig C; C.ReductionPerWhiff = NaN; ExpectInvalid(TEXT("NaN ReductionPerWhiff gives -1"), C); }
    { FConfig C; C.ReductionPerWhiff = Inf; ExpectInvalid(TEXT("infinite ReductionPerWhiff gives -1"), C); }
    { FConfig C; C.MinRateScale = 1.01; ExpectInvalid(TEXT("MinRateScale above 1 gives -1"), C); }
    { FConfig C; C.MinRateScale = NaN; ExpectInvalid(TEXT("NaN MinRateScale gives -1"), C); }
    { FConfig C; C.MinRateScale = -Inf; ExpectInvalid(TEXT("-Inf MinRateScale gives -1"), C); }
    return true;
}
#endif
