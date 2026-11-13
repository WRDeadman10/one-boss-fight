// Copyright One Boss Fight. All Rights Reserved.
// BL-65 (lane BL, X-2190): RPGBossStuckRecovery MaxAttempts <= 0 refuses. Observability: both cases are EQUIVALENT mutants, since
// `Attempts>=0 && Attempts<MaxAttempts` already needs MaxAttempts > 0; the asserts document behaviour. Existing tests cover negative Attempts, cap reached,
// cap > 8 and blocked/used. Asserts existing behaviour only.
#include "Player/RPGBossStuckRecoveryRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossStuckRecoveryGuards, "OneBossFight.Framework.StuckRecovery.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossStuckRecoveryGuards::RunTest(const FString&)
{
    using RPGBossStuckRecovery::CanRecover;
    TestTrue(TEXT("control: blocked, unused, 0 of 3 attempts recovers"), CanRecover(true, false, 0, 3));
    TestFalse(TEXT("MaxAttempts 0 refuses (equivalent mutant)"), CanRecover(true, false, 0, 0));
    TestFalse(TEXT("MaxAttempts -1 refuses (equivalent mutant)"), CanRecover(true, false, 0, -1));
    return true;
}
#endif
