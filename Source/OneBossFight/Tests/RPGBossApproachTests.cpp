// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossApproachRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossApproachRules,"OneBossFight.Framework.BossApproach.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossApproachRules::RunTest(const FString&)
{
    using namespace RPGBossApproach;

    TestEqual(TEXT("smoothstep starts at zero"),StepFraction(0.),0.);
    TestEqual(TEXT("smoothstep ends at one"),StepFraction(1.),1.);
    TestTrue(TEXT("smoothstep clamps below the domain"),StepFraction(-1.)==0.);
    TestTrue(TEXT("smoothstep clamps above the domain"),StepFraction(2.)==1.);
    TestTrue(TEXT("smoothstep is monotone over the interval"),StepFraction(.25)<StepFraction(.5)&&StepFraction(.5)<StepFraction(.75));

    constexpr double Total=880.;
    constexpr double Partition[]={0.,.07,.2,.51,.777,1.};
    double Sum=0.;
    for (int32 Index=0;Index<UE_ARRAY_COUNT(Partition)-1;++Index)
    {
        const double Step=StepCm(Total,Partition[Index],Partition[Index+1]);
        TestTrue(*FString::Printf(TEXT("partition step %d is nonnegative"),Index),Step>=0.);
        Sum+=Step;
    }
    TestTrue(TEXT("steps over an arbitrary partition sum to total distance"),FMath::IsNearlyEqual(Sum,Total,1.e-6));
    TestTrue(TEXT("a single full step equals total distance"),FMath::IsNearlyEqual(StepCm(Total,0.,1.),Total,1.e-6));
    TestEqual(TEXT("backwards step fails closed"),StepCm(Total,.5,.4),0.);
    TestEqual(TEXT("out-of-range step fails closed"),StepCm(Total,-.1,.4),0.);

    constexpr double PackChargeCap=2200.;
    constexpr double Headroom=1.27;
    constexpr double AllowedPeak=PackChargeCap*Headroom; // 2794 cm/s, below the requested 2800 cm/s ceiling.
    const double Peak=PeakSpeedCm(Total,.483);
    TestTrue(TEXT("880 cm over 0.483 s stays under the 2200 cm/s pack cap with 1.27 headroom (2794 cm/s)"),Peak<AllowedPeak&&Peak<2800.);
    TestEqual(TEXT("invalid duration fails closed"),PeakSpeedCm(Total,0.),0.);
    TestEqual(TEXT("invalid distance fails closed"),PeakSpeedCm(std::numeric_limits<double>::quiet_NaN(),1.),0.);
    FRandomStream Random(0x94A11);
    for(int32 Trial=0;Trial<1000;++Trial)
    {
        constexpr double Distance=913.25;double PreviousT=0.,SumDistance=0.;
        for(int32 Part=0;Part<20;++Part)
        {
            const double NextT=Part==19?1.:PreviousT+(1.-PreviousT)*Random.FRand();
            const double Step=StepCm(Distance,PreviousT,NextT);
            TestTrue(*FString::Printf(TEXT("partition %d step %d is nonnegative"),Trial,Part),Step>=0.);
            SumDistance+=Step;PreviousT=NextT;
        }
        TestTrue(*FString::Printf(TEXT("partition %d conserves total distance"),Trial),FMath::IsNearlyEqual(SumDistance,Distance,1.e-7));
    }
    TestEqual(TEXT("non-finite time fails closed"),StepCm(10.,0.,std::numeric_limits<double>::infinity()),0.);
    TestEqual(TEXT("non-finite duration fails closed"),PeakSpeedCm(10.,std::numeric_limits<double>::infinity()),0.);
    return true;
}
#endif
