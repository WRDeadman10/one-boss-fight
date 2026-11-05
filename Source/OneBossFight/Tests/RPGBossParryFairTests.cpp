// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossParryFairRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossParryFairRules,"OneBossFight.Framework.BossParryFair.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossParryFairRules::RunTest(const FString&)
{
    using namespace RPGBossParryFair;
    constexpr double Required=.2+.5*.25;

    TestTrue(TEXT("exactly reaction plus half the parry window is fair"),ParryableOk(0.,Required,1.));
    TestFalse(TEXT("a shorter reaction gap is not fair"),ParryableOk(0.,Required-.001,1.));
    TestTrue(TEXT("card seconds are divided by play rate"),ParryableOk(.2,.85,2.));
    TestTrue(TEXT("default reaction and window values apply"),ParryableOk(.1,.425,1.));
    TestFalse(TEXT("active start before telegraph fails closed"),ParryableOk(.4,.3,1.));
    TestFalse(TEXT("zero play rate fails closed"),ParryableOk(0.,1.,0.));
    TestFalse(TEXT("negative play rate fails closed"),ParryableOk(0.,1.,-1.));
    TestFalse(TEXT("NaN telegraph fails closed"),ParryableOk(std::numeric_limits<double>::quiet_NaN(),1.,1.));
    TestFalse(TEXT("NaN active start fails closed"),ParryableOk(0.,std::numeric_limits<double>::quiet_NaN(),1.));
    TestFalse(TEXT("NaN play rate fails closed"),ParryableOk(0.,1.,std::numeric_limits<double>::quiet_NaN()));
    TestFalse(TEXT("NaN window fails closed"),ParryableOk(0.,1.,1.,std::numeric_limits<double>::quiet_NaN()));
    TestFalse(TEXT("NaN reaction fails closed"),ParryableOk(0.,1.,1.,.25,std::numeric_limits<double>::quiet_NaN()));
    return true;
}
#endif
