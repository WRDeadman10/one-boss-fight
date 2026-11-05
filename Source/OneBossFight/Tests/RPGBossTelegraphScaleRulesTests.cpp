// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossTelegraphScaleRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossTelegraphScaleRules,"OneBossFight.Framework.TelegraphScale.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossTelegraphScaleRules::RunTest(const FString&)
{
    using namespace RPGBossTelegraphScale;
    constexpr double Required=.325;
    // ActiveStart values are sourced from RPGAttackTracker's eight current rows A1, A1b, A3a, A3b, A2, A6, A4 and A5.
    struct FCard { const TCHAR* Id; double ActiveStart; double ExpectedRate; };
    const FCard Cards[]={{TEXT("A1"),.35,1.},{TEXT("A1b"),.16,.16/.325},{TEXT("A3a"),.40,1.},{TEXT("A3b"),.15,.15/.325},{TEXT("A2"),1.93,1.},{TEXT("A6"),.75,1.},{TEXT("A4"),.60,1.},{TEXT("A5"),.45,1.}};
    for (const FCard& Card:Cards)
    {
        const double Scaled=Rate(Card.ActiveStart,1.,Required,.4);
        TestTrue(FString::Printf(TEXT("%s expected-rate table"),Card.Id),FMath::IsNearlyEqual(Scaled,Card.ExpectedRate,1.e-9));
        TestTrue(FString::Printf(TEXT("%s has a valid bounded rate"),Card.Id),Scaled>=.4&&Scaled<=1.);
        TestTrue(FString::Printf(TEXT("%s meets parry fairness after scaling"),Card.Id),RPGBossParryFair::ParryableOk(0.,Card.ActiveStart,Scaled,.25,.2));
    }
    TestTrue(TEXT("already fair card is not sped up"),Rate(.8,1.,Required,.4)==1.);
    TestTrue(TEXT("required slowdown beyond cap refuses"),Rate(.1,1.,.5,.4)<0.);
    TestTrue(TEXT("invalid rate fails closed"),Rate(.4,0.,Required,.4)<0.);
    // B5 applies its whiff scale first; B3 may reduce that result to preserve a fair tell, never speed it back up.
    const double FatiguedBase=.7;
    const double Composed=Rate(.16,FatiguedBase,Required,.4);
    TestTrue(TEXT("telegraph composition never exceeds fatigue rate"),Composed<=FatiguedBase);
    TestTrue(TEXT("composed fair rate meets parry rule"),Composed>=.4*FatiguedBase&&RPGBossParryFair::ParryableOk(0.,.16,Composed,.25,.2));
    for(int32 I=1;I<=100;++I)
    {
        const double Active=double(I)/100.;
        for(int32 J=1;J<=50;++J)
        {
            const double Current=.2+double(J)/50.;const double Scaled=Rate(Active,Current,.25,.4);
            if(Scaled>=0.)TestTrue(*FString::Printf(TEXT("rate sweep %d/%d never accelerates"),I,J),Scaled<=Current+1.e-9);
            else TestTrue(*FString::Printf(TEXT("rate sweep %d/%d refuses below slowdown floor"),I,J),Active/.25<Current*.4);
        }
    }
    TestTrue(TEXT("infinite fairness requirement fails closed"),Rate(.4,1.,std::numeric_limits<double>::infinity(),.4)<0.);
    TestTrue(TEXT("NaN slowdown floor fails closed"),Rate(.4,1.,.2,std::numeric_limits<double>::quiet_NaN())<0.);
    return true;
}
#endif
