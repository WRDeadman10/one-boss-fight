// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossRepeatPenaltyRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossRepeatPenaltyRules,"OneBossFight.Framework.RepeatPenalty.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossRepeatPenaltyRules::RunTest(const FString&)
{
    using namespace RPGBossRepeatPenalty;double Previous=10.;
    for(int32 Repeats=0;Repeats<=100;++Repeats){const double W=Weight(10.,Repeats,.8);TestTrue(TEXT("weight stays bounded and falls with repeats"),W>=0.&&W<=Previous);Previous=W;}
    TestEqual(TEXT("zero repeats preserves base weight"),Weight(2.,0),2.);TestEqual(TEXT("zero factor clears after first repeat"),Weight(2.,1,0.),0.);
    TestEqual(TEXT("invalid scale fails closed"),Weight(2.,3,1.1),0.);TestEqual(TEXT("negative repeat count fails closed"),Weight(2.,-1),0.);
    return true;
}
#endif
