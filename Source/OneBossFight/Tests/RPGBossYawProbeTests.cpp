// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossYawProbeRules.h"
#include "Player/RPGBossAimHysteresisRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossYawProbeRules,"OneBossFight.Framework.BossYawProbe.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossYawProbeRules::RunTest(const FString&)
{
    using namespace RPGBossYawProbe;
    constexpr double Center=30.;
    constexpr double Amplitude=2.;
    constexpr double Enter=30.;
    constexpr double Exit=33.;
    constexpr int32 Period=24;

    bool bPlainInside=false;
    bool bHysteresisInside=true;
    int32 PlainCrossings=0;
    int32 HysteresisCrossings=0;
    for (int32 Sample=0;Sample<240;++Sample)
    {
        const double Yaw=YawAt(Sample,Center,Amplitude,Period);
        const bool bPlainNext=FMath::Abs(Yaw)<=Enter;
        const bool bHysteresisNext=RPGBossAimHysteresis::Step(bHysteresisInside,Yaw,Enter,Exit);
        if (bPlainNext!=bPlainInside) ++PlainCrossings;
        if (bHysteresisNext!=bHysteresisInside) ++HysteresisCrossings;
        bPlainInside=bPlainNext;
        bHysteresisInside=bHysteresisNext;
    }

    TestTrue(TEXT("plain 30 degree gate flickers at least 20 times in 240 samples"),PlainCrossings>=20);
    TestEqual(TEXT("3 degree exit hysteresis prevents crossings for a 2 degree oscillation"),HysteresisCrossings,0);
    TestTrue(TEXT("yaw probe is periodic"),FMath::IsNearlyEqual(YawAt(0,Center,Amplitude,Period),YawAt(Period,Center,Amplitude,Period),1.e-9));
    TestTrue(TEXT("yaw probe is deterministic"),YawAt(17,Center,Amplitude,Period)==YawAt(17,Center,Amplitude,Period));
    FRandomStream Random(0x96A11);
    for(int32 Trial=0;Trial<1000;++Trial)
    {
        const double C=Random.FRandRange(-180.f,180.f),A=Random.FRandRange(0.f,60.f);const int32 P=Random.RandRange(1,240);
        for(int32 Sample:{-P,0,P/4,P/2,P,2*P})
        {
            const double Y=YawAt(Sample,C,A,P);
            TestTrue(*FString::Printf(TEXT("yaw sample %d remains within configured signal bounds"),Sample),FMath::IsFinite(Y)&&Y>=C-A-1.e-9&&Y<=C+A+1.e-9);
            TestTrue(TEXT("yaw repeats exactly each period"),FMath::IsNearlyEqual(Y,YawAt(Sample+P,C,A,P),1.e-9));
        }
    }
    TestEqual(TEXT("zero period fails closed"),YawAt(1,30.,2.,0),0.);
    TestEqual(TEXT("non-finite signal parameters fail closed"),YawAt(1,std::numeric_limits<double>::quiet_NaN(),2.,24),0.);
    TestEqual(TEXT("infinite center fails closed"),YawAt(1,std::numeric_limits<double>::infinity(),2.,24),0.);
    TestEqual(TEXT("infinite amplitude fails closed"),YawAt(1,30.,std::numeric_limits<double>::infinity(),24),0.);
    return true;
}
#endif
