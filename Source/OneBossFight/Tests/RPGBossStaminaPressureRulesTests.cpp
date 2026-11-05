// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossStaminaPressureRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossStaminaPressureRules,"OneBossFight.Framework.StaminaPressure.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossStaminaPressureRules::RunTest(const FString&)
{
    using namespace RPGBossStaminaPressure;TestEqual(TEXT("full stamina has no pressure"),Pressure(1.),0.);TestEqual(TEXT("threshold has no added pressure"),Pressure(.4),0.);
    TestTrue(TEXT("half of threshold creates half pressure"),FMath::IsNearlyEqual(Pressure(.2),.5));TestEqual(TEXT("empty stamina reaches cap"),Pressure(0.),1.);
    double Previous=0.;for(int32 I=0;I<=1000;++I){const double V=Pressure(1.-double(I)/1000.);TestTrue(TEXT("pressure rises monotonically as stamina falls"),V>=Previous&&V<=1.);Previous=V;}
    TestEqual(TEXT("invalid fraction fails closed"),Pressure(-.1),0.);TestEqual(TEXT("invalid maximum fails closed"),Pressure(.1,.4,4.),0.);return true;
}
#endif
