// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossDesperationRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossDesperationRules,"OneBossFight.Framework.Desperation.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossDesperationRules::RunTest(const FString&)
{
    using namespace RPGBossDesperation;TestEqual(TEXT("above threshold leaves default weight"),WeightMultiplier(.5,.35,1.8),1.);
    TestEqual(TEXT("threshold begins at default weight"),WeightMultiplier(.35,.35,1.8),1.);TestTrue(TEXT("half-health ramp is halfway to maximum"),FMath::IsNearlyEqual(WeightMultiplier(.175,.35,1.8),1.4));
    TestEqual(TEXT("zero health clamps at maximum"),WeightMultiplier(0.,.35,1.8),1.8);TestEqual(TEXT("full health is unchanged"),WeightMultiplier(1.),1.);
    double Previous=1.;for(int32 I=0;I<=1000;++I){const double H=1.-double(I)/1000.;const double W=WeightMultiplier(H);TestTrue(TEXT("weight rises monotonically as health falls"),W>=Previous&&W<=1.5);Previous=W;}
    TestEqual(TEXT("invalid health fails safely to default"),WeightMultiplier(std::numeric_limits<double>::quiet_NaN()),1.);
    TestEqual(TEXT("invalid maximum fails safely to default"),WeightMultiplier(.1,.35,4.),1.);
    return true;
}
#endif
