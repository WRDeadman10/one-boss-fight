// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossTurnRateRamp.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossTurnRateRampRules,"OneBossFight.Framework.TurnRateRamp.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossTurnRateRampRules::RunTest(const FString&)
{
    using namespace RPGBossTurnRateRamp;
    TestEqual(TEXT("ramp starts at authored initial rate"),Rate(0.,1.,60.,180.),60.);TestEqual(TEXT("halfway smoothstep is midpoint"),Rate(.5,1.,60.,180.),120.);
    TestEqual(TEXT("ramp clamps at final rate"),Rate(2.,1.,60.,180.),180.);
    double Previous=60.;for(int32 I=0;I<=1000;++I){const double Value=Rate(double(I)/1000.,1.,60.,180.);TestTrue(TEXT("turn rate rises smoothly within bounds"),Value>=Previous&&Value<=180.);Previous=Value;}
    TestEqual(TEXT("invalid time fails closed"),Rate(std::numeric_limits<double>::quiet_NaN(),1.,60.,180.),0.);TestEqual(TEXT("negative rate fails closed"),Rate(.2,1.,-1.,180.),0.);
    return true;
}
#endif
