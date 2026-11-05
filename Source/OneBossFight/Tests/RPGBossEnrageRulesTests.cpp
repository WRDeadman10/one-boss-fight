// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossEnrageRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossEnrageRules,"OneBossFight.Framework.Enrage.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossEnrageRules::RunTest(const FString&)
{
    using namespace RPGBossEnrage;FConfig C;C.RampSeconds=100.;C.MaxDamageScale=1.8;C.MaxSpeedScale=1.4;
    TestTrue(TEXT("valid enrage configuration"),C.IsValid());TestEqual(TEXT("before fight no ramp"),Progress(-1.,C),0.);
    TestEqual(TEXT("zero starts at baseline"),DamageScale(0.,C),1.);TestTrue(TEXT("midpoint damage ramp"),FMath::IsNearlyEqual(DamageScale(50.,C),1.4));
    TestTrue(TEXT("midpoint speed ramp"),FMath::IsNearlyEqual(SpeedScale(50.,C),1.2));TestEqual(TEXT("ramp clamps at configured max"),DamageScale(1000.,C),1.8);
    double Previous=1.,PreviousSpeed=1.;for(int32 I=0;I<=1000;++I){const double T=double(I)/10.;const double D=DamageScale(T,C),S=SpeedScale(T,C);TestTrue(TEXT("damage and speed stay bounded and monotone"),D>=Previous&&D<=1.8&&S>=PreviousSpeed&&S<=1.4);Previous=D;PreviousSpeed=S;}
    C.RampSeconds=0.;TestFalse(TEXT("zero ramp is invalid"),C.IsValid());TestEqual(TEXT("invalid config fails safely to baseline"),DamageScale(20.,C),1.);
    C=FConfig();C.MaxDamageScale=std::numeric_limits<double>::infinity();
    TestFalse(TEXT("infinite maximum damage scale invalidates config"),C.IsValid());
    TestEqual(TEXT("invalid maximum damage scale keeps baseline output"),DamageScale(1000.,C),1.);
    C=FConfig();C.MaxSpeedScale=2.01;
    TestFalse(TEXT("speed maximum above the documented bound invalidates config"),C.IsValid());
    TestEqual(TEXT("invalid speed maximum keeps baseline output"),SpeedScale(1000.,C),1.);
    return true;
}
#endif
