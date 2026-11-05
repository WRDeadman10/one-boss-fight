// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossComboAbortRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossComboAbortRules,"OneBossFight.Framework.ComboAbort.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossComboAbortRules::RunTest(const FString&)
{
    using namespace RPGBossComboAbort;
    TestTrue(TEXT("parry of first hit aborts active combo"),ShouldAbort(true,0,true));
    TestFalse(TEXT("no active combo has nothing to abort"),ShouldAbort(false,0,true));
    TestFalse(TEXT("parry after accepted combo hit does not trigger first-hit abort"),ShouldAbort(true,1,true));
    TestFalse(TEXT("no parry does not abort"),ShouldAbort(true,0,false));
    for(int32 Hits=0;Hits<20;++Hits)TestEqual(TEXT("only zero accepted hits can abort"),ShouldAbort(true,Hits,true),Hits==0);
    return true;
}
#endif
