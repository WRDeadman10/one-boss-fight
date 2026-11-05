// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossCueJitterRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossCueJitterRules,"OneBossFight.Framework.CueJitter.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossCueJitterRules::RunTest(const FString&)
{
    using namespace RPGBossCueJitter;
    for(int32 I=0;I<1000;++I){const double T=Time(1234,I,1.,.3,.8,1.2);TestTrue(TEXT("jitter stays within safe band"),T>=.8&&T<=1.2);TestEqual(TEXT("same seed and cue index repeat exactly"),T,Time(1234,I,1.,.3,.8,1.2));}
    TestEqual(TEXT("unsafe negative interval fails closed"),Time(1,0,1.,.2,-1.,2.),0.);
    return true;
}
#endif
