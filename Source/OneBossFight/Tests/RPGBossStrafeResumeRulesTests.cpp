// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossStrafeResumeRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossStrafeResumeRules,"OneBossFight.Framework.StrafeResume.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossStrafeResumeRules::RunTest(const FString&)
{
    using namespace RPGBossStrafeResume;
    struct FCase { bool bInterrupted; bool bUsed; double Budget; bool bExpected; const TCHAR* Label; };
    const FCase Cases[]={
        {true,false,.5,true,TEXT("first qualifying interruption with budget restarts")},
        {false,false,.5,false,TEXT("no interruption does not restart")},
        {true,true,.5,false,TEXT("restart is not reusable after it was consumed")},
        {true,false,0.,false,TEXT("exhausted budget does not restart")},
        {true,false,std::numeric_limits<double>::denorm_min(),true,TEXT("any finite positive residual budget qualifies")},
        {true,false,-.1,false,TEXT("negative budget fails closed")},
        {true,false,std::numeric_limits<double>::infinity(),false,TEXT("infinite budget fails closed")},
        {true,false,std::numeric_limits<double>::quiet_NaN(),false,TEXT("NaN budget fails closed")},
    };
    for (const FCase& Case:Cases)
        TestEqual(Case.Label,ShouldRestart(Case.bInterrupted,Case.bUsed,Case.Budget),Case.bExpected);
    return true;
}
#endif
