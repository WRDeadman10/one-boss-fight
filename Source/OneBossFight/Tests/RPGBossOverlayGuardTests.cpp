// Copyright One Boss Fight. All Rights Reserved.
// BL-41 (lane BL, X-2179): RPGBossOverlay gaps: Num with Digits>=2 uses "%.2f"; Format with parry data and a CLOSED window shows "Parry=Closed".
// Focused unit checks only; the broad runtime overlay suite is not restated. Asserts existing behaviour only.
#include "Player/RPGBossOverlayRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossOverlayGuards, "OneBossFight.Framework.Overlay.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossOverlayGuards::RunTest(const FString&)
{
    using namespace RPGBossOverlay;

    // Num: Digits 2 and anything above 2 use two decimals (control: Digits 0 rounds to an integer).
    TestEqual(TEXT("control: Digits 0"), Num(1.234), FString(TEXT("1")));
    TestEqual(TEXT("Digits 2 uses %.2f"), Num(1.234, 2), FString(TEXT("1.23")));
    TestEqual(TEXT("Digits 3 also uses %.2f"), Num(1., 3), FString(TEXT("1.00")));
    TestEqual(TEXT("Digits 5 also uses %.2f"), Num(2.5, 5), FString(TEXT("2.50")));

    // Format: parry data with a closed window appends " Parry=Closed Grade=<grade>"; without parry data nothing is appended.
    FInput In;
    In.CardId = TEXT("Swing1"); In.State = TEXT("Windup"); In.Phase = TEXT("One");
    const FString Baseline = Format(In);
    TestFalse(TEXT("control: no parry data, no Parry field"), Baseline.Contains(TEXT("Parry=")));
    In.bHasParryData = true; In.bParryWindowOpen = false; In.LastParryGrade = TEXT("Good");
    const FString Closed = Format(In);
    TestTrue(TEXT("closed window shows Parry=Closed with the grade"), Closed.EndsWith(TEXT(" Parry=Closed Grade=Good")));
    TestEqual(TEXT("parry fields are appended to the unchanged core line"), Closed, Baseline + TEXT(" Parry=Closed Grade=Good"));
    return true;
}
#endif
