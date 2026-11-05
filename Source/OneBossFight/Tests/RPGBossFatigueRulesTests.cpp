// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossFatigueRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossFatigueRules,"OneBossFight.Framework.Fatigue.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossFatigueRules::RunTest(const FString&)
{
    using namespace RPGBossFatigue;
    double Previous=1.;
    for (int32 Whiffs=0;Whiffs<1000;++Whiffs)
    {
        const double Scale=RateScale(Whiffs);
        TestTrue(TEXT("fatigue rate stays finite and bounded"),FMath::IsFinite(Scale)&&Scale>=.7&&Scale<=1.);
        TestTrue(TEXT("more whiffs never increase attack rate"),Scale<=Previous+1.e-12);
        Previous=Scale;
    }
    TestTrue(TEXT("grace count does not slow the first two whiffs"),RateScale(0)==1.&&RateScale(2)==1.);
    TestTrue(TEXT("invalid count/config fails closed"),RateScale(-1)<0.);
    FConfig Bad; Bad.MinRateScale=0.; TestTrue(TEXT("zero floor is invalid"),RateScale(4,Bad)<0.);
    return true;
}
#endif
