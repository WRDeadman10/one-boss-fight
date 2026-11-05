// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossHitStopRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossHitStopRules,"OneBossFight.Framework.HitStop.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossHitStopRules::RunTest(const FString&)
{
    using namespace RPGBossHitStop;FConfig C;
    TestTrue(TEXT("default config valid"),RPGBossHitStop::IsValid(C));TestTrue(TEXT("perfect has longest hit stop"),Seconds(RPGParryGrade::EGrade::Perfect,C)>Seconds(RPGParryGrade::EGrade::Good,C));
    TestTrue(TEXT("good exceeds late"),Seconds(RPGParryGrade::EGrade::Good,C)>Seconds(RPGParryGrade::EGrade::Late,C));
    TestEqual(TEXT("none grade has no hit stop"),Seconds(RPGParryGrade::EGrade::None,C),0.);
    C.PerfectSeconds=.5;TestFalse(TEXT("duration above cap invalid"),RPGBossHitStop::IsValid(C));TestEqual(TEXT("invalid config fails closed"),Seconds(RPGParryGrade::EGrade::Perfect,C),0.);
    C=FConfig();C.GoodSeconds=.15;TestFalse(TEXT("grade order inversion invalid"),RPGBossHitStop::IsValid(C));
    return true;
}
#endif
