// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossStuckRecoveryRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossStuckRecoveryRules,"OneBossFight.Framework.StuckRecovery.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossStuckRecoveryRules::RunTest(const FString&)
{
    using namespace RPGBossStuckRecovery;TestTrue(TEXT("blocked first attempt can recover"),CanRecover(true,false,0,1));
    TestFalse(TEXT("unblocked movement does not recover"),CanRecover(false,false,0,1));TestFalse(TEXT("one-time recovery cannot repeat"),CanRecover(true,true,0,1));
    TestFalse(TEXT("attempt cap blocks recovery"),CanRecover(true,false,2,2));TestFalse(TEXT("negative attempt count fails closed"),CanRecover(true,false,-1,2));
    TestFalse(TEXT("excessive attempt cap fails closed"),CanRecover(true,false,0,9));return true;
}
#endif
