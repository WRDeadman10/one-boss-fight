// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossAimHysteresisRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossAimHysteresisRules,"OneBossFight.Framework.AimHysteresis.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossAimHysteresisRules::RunTest(const FString&)
{
    using namespace RPGBossAimHysteresis;
    constexpr double Enter=30.,Exit=34.;

    TestTrue(TEXT("enter at exactly the positive enter angle"),Step(false,Enter,Enter,Exit));
    TestTrue(TEXT("stay inside between enter and exit"),Step(true,32.,Enter,Exit));
    TestTrue(TEXT("stay inside at exactly the exit angle"),Step(true,Exit,Enter,Exit));
    TestFalse(TEXT("leave above exit"),Step(true,Exit+.001,Enter,Exit));
    TestFalse(TEXT("do not re-enter above enter"),Step(false,Enter+.001,Enter,Exit));
    TestTrue(TEXT("re-enter at enter after leaving"),Step(false,Enter,Enter,Exit));
    TestTrue(TEXT("negative angles use the same enter boundary"),Step(false,-Enter,Enter,Exit));
    TestTrue(TEXT("negative angles use the same exit boundary"),Step(true,-Exit,Enter,Exit));
    TestFalse(TEXT("negative angles leave above exit"),Step(true,-(Exit+.001),Enter,Exit));

    bool bHysteresisInside=true;
    bool bPlainInside=true;
    int32 HysteresisFlips=0,PlainFlips=0;
    for (int32 Cycle=0;Cycle<60;++Cycle)
    {
        for (const double Yaw : {30.5,29.5})
        {
            const bool bNext=Step(bHysteresisInside,Yaw,Enter,32.);
            if (bNext!=bHysteresisInside) ++HysteresisFlips;
            bHysteresisInside=bNext;

            const bool bPlainNext=FMath::Abs(Yaw)<=Enter;
            if (bPlainNext!=bPlainInside) ++PlainFlips;
            bPlainInside=bPlainNext;
        }
    }
    TestEqual(TEXT("oscillation smaller than the band causes no hysteresis flips"),HysteresisFlips,0);
    TestEqual(TEXT("the no-hysteresis boundary flips on every oscillation sample"),PlainFlips,120);

    bool bNegativeInside=true;
    int32 NegativeFlips=0;
    for (int32 Cycle=0;Cycle<60;++Cycle)
    {
        for (const double Yaw : {-30.5,-29.5})
        {
            const bool bNext=Step(bNegativeInside,Yaw,Enter,32.);
            if (bNext!=bNegativeInside) ++NegativeFlips;
            bNegativeInside=bNext;
        }
    }
    TestEqual(TEXT("negative-yaw oscillation is equally stable"),NegativeFlips,0);

    TestFalse(TEXT("NaN yaw fails closed"),Step(true,std::numeric_limits<double>::quiet_NaN(),Enter,Exit));
    TestFalse(TEXT("infinite yaw fails closed"),Step(true,std::numeric_limits<double>::infinity(),Enter,Exit));
    TestFalse(TEXT("NaN threshold fails closed"),Step(true,0.,std::numeric_limits<double>::quiet_NaN(),Exit));
    TestFalse(TEXT("infinite threshold fails closed"),Step(true,0.,Enter,std::numeric_limits<double>::infinity()));
    TestTrue(TEXT("exit below enter is treated as equal to enter"),Step(true,Enter,Enter,Enter-5.));
    TestFalse(TEXT("collapsed band exits above enter"),Step(true,Enter+.001,Enter,Enter-5.));

    bool bSweepA=false,bSweepB=false;
    int32 SweepFlipsA=0,SweepFlipsB=0;
    for (int32 Sample=0;Sample<360;++Sample)
    {
        const double Yaw=double(Sample)-180.;
        const bool bNextA=Step(bSweepA,Yaw,Enter,Exit);
        const bool bNextB=Step(bSweepB,Yaw,Enter,Exit);
        if (bNextA!=bSweepA) ++SweepFlipsA;
        if (bNextB!=bSweepB) ++SweepFlipsB;
        TestEqual(*FString::Printf(TEXT("deterministic sweep sample %d"),Sample),bNextA,bNextB);
        bSweepA=bNextA;
        bSweepB=bNextB;
    }
    TestEqual(TEXT("deterministic sweep transition count"),SweepFlipsA,SweepFlipsB);
    return true;
}
#endif
