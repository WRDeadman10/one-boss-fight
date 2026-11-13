// Copyright One Boss Fight. All Rights Reserved.
// BL-66 (lane BL): RPGBossStuck::IsStuck rejects a negative MinRatio. Observability: EQUIVALENT mutant, since moved >= 0 makes the ratio >= 0, which is never
// below a negative MinRatio; the assert documents behaviour. NaN/Inf threshold, zero window and window boundaries are already covered. Asserts existing behaviour only.
#include "Player/RPGBossStuckRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossStuckGuards, "OneBossFight.Framework.BossStuck.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossStuckGuards::RunTest(const FString&)
{
    using namespace RPGBossStuck;
    auto Blocked = []() { FStuck S; Update(S, 10., 1., .4); return S; }; // ratio 0.1 over a complete 0.4 s window

    { FStuck S = Blocked(); TestTrue(TEXT("control: ratio 0.1 below 0.5 is stuck"), IsStuck(S, .5, .3)); }
    { FStuck S = Blocked(); TestFalse(TEXT("negative MinRatio is refused (equivalent mutant)"), IsStuck(S, -.1, .3)); TestFalse(TEXT("refusal does not consume the one-shot flip"), S.bDirectionFlipped); }
    return true;
}
#endif
