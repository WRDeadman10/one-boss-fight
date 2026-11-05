// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossStuckRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossStuckRules,"OneBossFight.Framework.BossStuck.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossStuckRules::RunTest(const FString&)
{
    using namespace RPGBossStuck;

    FStuck Stuck;
    for (int32 Step=0;Step<18;++Step) Update(Stuck,1.,0.,.016);
    TestFalse(TEXT("do not classify as stuck before the 0.3 s observation window"),IsStuck(Stuck,.5,.3));
    Update(Stuck,1.,0.,.02);
    TestTrue(TEXT("less than half the expected arc after the window is stuck"),IsStuck(Stuck,.5,.3));
    TestTrue(TEXT("the first stuck result arms the one-time direction flip"),Stuck.bDirectionFlipped);
    TestFalse(TEXT("do not request a second direction flip"),IsStuck(Stuck,.5,.3));

    FStuck Moving;
    for (int32 Step=0;Step<600;++Step)
    {
        Update(Moving,1.,1.,.016);
        TestFalse(*FString::Printf(TEXT("free movement sample %d is not stuck"),Step),IsStuck(Moving,.5,.3));
    }
    TestFalse(TEXT("free movement never flips direction"),Moving.bDirectionFlipped);

    FStuck Invalid;
    Update(Invalid,1.,std::numeric_limits<double>::quiet_NaN(),.016);
    TestFalse(TEXT("NaN movement fails closed"),IsStuck(Invalid,.5,.3));
    TestFalse(TEXT("NaN threshold fails closed"),IsStuck(Moving,std::numeric_limits<double>::quiet_NaN(),.3));
    TestFalse(TEXT("zero window fails closed"),IsStuck(Moving,.5,0.));
    for(int32 I=0;I<=100;++I)
    {
        FStuck Sample;Update(Sample,100.,double(I),.3);
        const bool Expected=double(I)/100.<.5;
        TestEqual(*FString::Printf(TEXT("movement ratio boundary sample %d"),I),IsStuck(Sample,.5,.3),Expected);
        if(Expected)TestFalse(TEXT("stuck direction flip remains one-shot"),IsStuck(Sample,.5,.3));
    }
    TestFalse(TEXT("infinite threshold fails closed"),IsStuck(Moving,std::numeric_limits<double>::infinity(),.3));
    FStuck Overflow;Update(Overflow,std::numeric_limits<double>::max(),1.,1.);Update(Overflow,std::numeric_limits<double>::max(),1.,1.);
    TestFalse(TEXT("accumulator overflow resets without false stuck verdict"),IsStuck(Overflow,.5,.3));
    return true;
}
#endif
