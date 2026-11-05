// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossRecoveryWindowRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossParryRecoveryWiring,"OneBossFight.Framework.ParryRecovery.WiringBoundary",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossParryRecoveryWiring::RunTest(const FString&)
{
    using namespace RPGParryGrade;
    TestEqual(TEXT("profile scale zero is off"),RPGBossRecoveryWindow::ScaledSeconds(EGrade::Perfect,.8,0.),0.);
    const double Perfect=RPGBossRecoveryWindow::ScaledSeconds(EGrade::Perfect,.8,1.);
    TestTrue(TEXT("enabled profile produces grade-scaled extra recovery"),Perfect>0.&&Perfect<=1.5);
    TestEqual(TEXT("profile scale composes before grade rule"),RPGBossRecoveryWindow::ScaledSeconds(EGrade::Good,.8,2.),RPGBossRecoveryWindow::Seconds(EGrade::Good,1.6));
    TestEqual(TEXT("unknown grade fails closed"),RPGBossRecoveryWindow::ScaledSeconds(EGrade::None,.8,1.),-1.);
    TestEqual(TEXT("non-finite scale fails closed"),RPGBossRecoveryWindow::ScaledSeconds(EGrade::Perfect,.8,std::numeric_limits<double>::quiet_NaN()),-1.);
    return true;
}
#endif
