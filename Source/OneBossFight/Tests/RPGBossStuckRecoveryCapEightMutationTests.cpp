// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossStuckRecoveryRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossStuckRecoveryCapEightMutationTest,
    "OneBossFight.Framework.StuckRecovery.CapEightMutation",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FBossStuckRecoveryCapEightMutationTest::RunTest(const FString&)
{
    TestTrue(TEXT("the documented maximum attempt cap of eight remains valid"),
        RPGBossStuckRecovery::CanRecover(true, false, 0, 8));
    return true;
}
#endif
