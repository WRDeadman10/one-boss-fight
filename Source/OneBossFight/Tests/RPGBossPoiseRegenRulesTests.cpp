// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossPoiseRegenRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossPoiseRegenRules,"OneBossFight.Framework.PoiseRegen.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossPoiseRegenRules::RunTest(const FString&)
{
    using namespace RPGBossPoiseRegen;TestEqual(TEXT("before delay no regeneration"),Rate(10.,.9,1.,2.,1.5),0.);
    TestEqual(TEXT("delay boundary begins at base rate"),Rate(10.,1.,1.,2.,1.5),10.);TestTrue(TEXT("half ramp scales to midpoint"),FMath::IsNearlyEqual(Rate(10.,2.,1.,2.,1.5),12.5));
    TestEqual(TEXT("ramp caps at max scale"),Rate(10.,10.,1.,2.,1.5),15.);
    double Previous=0.;for(int32 I=0;I<=1000;++I){const double Value=Rate(10.,double(I)/100.,1.,2.,1.5);TestTrue(TEXT("regen rises monotonically and stays bounded"),Value>=Previous&&Value<=15.);Previous=Value;}
    TestEqual(TEXT("invalid elapsed time fails closed"),Rate(10.,std::numeric_limits<double>::infinity(),1.,2.),0.);return true;
}
#endif
