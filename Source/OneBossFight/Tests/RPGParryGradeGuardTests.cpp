// Copyright One Boss Fight. All Rights Reserved.
// BL-78 (lane BL): RPGParryGrade::Grade returns None for an infinite offset or window. Observability: a +Inf WINDOW discriminates (offset/Inf = 0 would grade
// Perfect without the guard); +Inf / -Inf offsets and a -Inf window are EQUIVALENT mutants (already refused by offset >= window, offset < 0, window <= 0).
// NaN offset/window, zero window and the 40/80 % boundaries are already covered. Asserts existing behaviour only.
#include "Player/RPGParryGradeRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FParryGradeGuards, "OneBossFight.Framework.ParryGrade.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FParryGradeGuards::RunTest(const FString&)
{
    using namespace RPGParryGrade;
    const double Inf = std::numeric_limits<double>::infinity();

    TestTrue(TEXT("control: 0.05 of 0.25 is Perfect"), Grade(.05, .25) == EGrade::Perfect);
    TestTrue(TEXT("+Inf window gives None (discriminates)"), Grade(.05, Inf) == EGrade::None);
    TestTrue(TEXT("+Inf offset gives None (equivalent)"), Grade(Inf, .25) == EGrade::None);
    TestTrue(TEXT("-Inf offset gives None (equivalent)"), Grade(-Inf, .25) == EGrade::None);
    TestTrue(TEXT("-Inf window gives None (equivalent)"), Grade(.05, -Inf) == EGrade::None);
    return true;
}
#endif
