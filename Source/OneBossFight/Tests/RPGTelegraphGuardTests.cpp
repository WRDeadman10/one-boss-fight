// Copyright One Boss Fight. All Rights Reserved.
// BL-82 (lane BL, X-2196): RPGTelegraphRules guards not in RPGCodexTests: RateFor non-finite ActiveStart/Target/Position -> 1; TargetFor NaN/+Inf/negative CVar -> 0.
// Observability (by hand against RPGTelegraphRules.h:9-30): for RateFor only a +Inf TARGET discriminates ((A-P)/Inf = 0 clamps to 0.1, not 1); NaN inputs
// and +Inf ActiveStart are EQUIVALENT mutants (FMath::Clamp(NaN, .1, 1) returns 1; Target <= +Inf refuses). Every TargetFor case discriminates
// (FMath::Min(NaN,.35) gives .35 for A1, and A3a would return the raw value). Asserts existing behaviour only.
#include "Player/RPGTelegraphRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGTelegraphGuardsTest, "OneBossFight.Player.TelegraphGuards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGTelegraphGuardsTest::RunTest(const FString&)
{
    using namespace RPGTelegraphRules;
    const float NaN = std::numeric_limits<float>::quiet_NaN();
    const float Inf = std::numeric_limits<float>::infinity();

    // RateFor.
    TestEqual(TEXT("control: A3a plain ratio 0.425"), RateFor(.17f, .40f), .425f, .0001f);
    TestEqual(TEXT("+Inf target leaves the rate at 1 (discriminates)"), RateFor(.17f, Inf), 1.f);
    TestEqual(TEXT("NaN active start leaves 1 (equivalent)"), RateFor(NaN, .40f), 1.f);
    TestEqual(TEXT("+Inf active start leaves 1 (equivalent)"), RateFor(Inf, .40f), 1.f);
    TestEqual(TEXT("NaN target leaves 1 (equivalent)"), RateFor(.17f, NaN), 1.f);
    TestEqual(TEXT("NaN position leaves 1 (equivalent)"), RateFor(.17f, .40f, NaN), 1.f);

    // TargetFor.
    TestEqual(TEXT("control: A3a keeps the cvar target"), TargetFor(TEXT("A3a"), .40f), .40f);
    TestEqual(TEXT("NaN cvar gives 0 for A1"), TargetFor(TEXT("A1"), NaN), 0.f);
    TestEqual(TEXT("NaN cvar gives 0 for A3a"), TargetFor(TEXT("A3a"), NaN), 0.f);
    TestEqual(TEXT("+Inf cvar gives 0 for A1"), TargetFor(TEXT("A1"), Inf), 0.f);
    TestEqual(TEXT("+Inf cvar gives 0 for A3a"), TargetFor(TEXT("A3a"), Inf), 0.f);
    TestEqual(TEXT("negative cvar gives 0 for A3a"), TargetFor(TEXT("A3a"), -.1f), 0.f);
    return true;
}
#endif
