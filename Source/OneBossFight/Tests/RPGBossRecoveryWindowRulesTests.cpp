// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossRecoveryWindowRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossRecoveryWindowRules,"OneBossFight.Framework.RecoveryWindow.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossRecoveryWindowRules::RunTest(const FString&)
{
    using namespace RPGBossRecoveryWindow;
    const double P=Seconds(RPGParryGrade::EGrade::Perfect,1.),G=Seconds(RPGParryGrade::EGrade::Good,1.),L=Seconds(RPGParryGrade::EGrade::Late,1.);
    TestTrue(TEXT("higher parry grade grants a longer punish window"),P>G&&G>L);
    TestTrue(TEXT("window is clamped to configured maximum"),Seconds(RPGParryGrade::EGrade::Perfect,100.)==1.5);
    TestTrue(TEXT("short positive recovery respects minimum"),Seconds(RPGParryGrade::EGrade::Late,.01)==.05);
    TestTrue(TEXT("invalid grade and invalid recovery fail closed"),Seconds(RPGParryGrade::EGrade::None,1.)<0.&&Seconds(RPGParryGrade::EGrade::Good,0.)<0.);
    FConfig Bad; Bad.MaxSeconds=0.; TestTrue(TEXT("invalid config fails closed"),Seconds(RPGParryGrade::EGrade::Perfect,1.,Bad)<0.);
    FConfig InvertedGradeOrder; InvertedGradeOrder.PerfectFraction=.2; InvertedGradeOrder.GoodFraction=.6;
    TestFalse(TEXT("grade fractions must preserve Perfect >= Good >= Late"),InvertedGradeOrder.IsValid());
    TestTrue(TEXT("inverted grade fractions fail closed"),Seconds(RPGParryGrade::EGrade::Perfect,1.,InvertedGradeOrder)<0.);
    for(int32 I=1;I<=1000;++I)
    {
        const double Recovery=double(I)/100.;
        const double SweepP=Seconds(RPGParryGrade::EGrade::Perfect,Recovery),SweepG=Seconds(RPGParryGrade::EGrade::Good,Recovery),SweepL=Seconds(RPGParryGrade::EGrade::Late,Recovery);
        TestTrue(*FString::Printf(TEXT("recovery sweep %d preserves grade order"),I),SweepP>=SweepG&&SweepG>=SweepL&&SweepL>0.&&SweepP<=1.5);
    }
    const double NonFinite=std::numeric_limits<double>::infinity();
    TestTrue(TEXT("non-finite card duration fails closed"),Seconds(RPGParryGrade::EGrade::Perfect,NonFinite)<0.);
    FConfig InvalidFractions;InvalidFractions.GoodFraction=std::numeric_limits<double>::quiet_NaN();TestFalse(TEXT("non-finite config fraction rejected"),InvalidFractions.IsValid());
    FConfig Inverted;Inverted.MinSeconds=1.;Inverted.MaxSeconds=.5;TestFalse(TEXT("inverted clamp interval rejected"),Inverted.IsValid());
    return true;
}
#endif
