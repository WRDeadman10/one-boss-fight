// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossMusicIntensityRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMusicIntensityRules,"OneBossFight.Framework.MusicIntensity.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossMusicIntensityRules::RunTest(const FString&)
{
    using namespace RPGBossMusicIntensity;
    TestEqual(TEXT("full health phase one is calm"),Evaluate(1.,1),0.);TestEqual(TEXT("zero health clamps to maximum"),Evaluate(0.,1),1.);
    TestTrue(TEXT("phase two adds intensity"),Evaluate(.8,2) > Evaluate(.8,1));TestEqual(TEXT("intensity never exceeds one"),Evaluate(0.,2),1.);
    double Previous=0.;for(int32 I=0;I<=1000;++I){const double V=Evaluate(1.-double(I)/1000.,1);TestTrue(TEXT("phase one intensity rises monotonically as health drops"),V>=Previous&&V>=0.&&V<=1.);Previous=V;}
    TestEqual(TEXT("invalid phase fails closed"),Evaluate(.5,3),0.);TestEqual(TEXT("invalid boost fails closed"),Evaluate(.5,2,2.),0.);return true;
}
#endif
