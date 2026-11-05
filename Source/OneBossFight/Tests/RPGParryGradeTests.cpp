// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGParryGradeRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FParryGradeRules,"OneBossFight.Framework.ParryGrade.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FParryGradeRules::RunTest(const FString&)
{
    using namespace RPGParryGrade;
    constexpr double Window=.25;

    TestTrue(TEXT("opening instant is Perfect"),Grade(0.,Window)==EGrade::Perfect);
    TestTrue(TEXT("first 40 percent is Perfect"),Grade(.099,Window)==EGrade::Perfect);
    TestTrue(TEXT("exactly 40 percent is Good"),Grade(.1,Window)==EGrade::Good);
    TestTrue(TEXT("through 80 percent is Good"),Grade(.199,Window)==EGrade::Good);
    TestTrue(TEXT("exactly 80 percent is Late"),Grade(.2,Window)==EGrade::Late);
    TestTrue(TEXT("last valid instant is Late"),Grade(.249999,Window)==EGrade::Late);
    TestTrue(TEXT("closing edge is not graded"),Grade(Window,Window)==EGrade::None);
    TestTrue(TEXT("negative offset fails closed"),Grade(-.001,Window)==EGrade::None);
    TestTrue(TEXT("zero window fails closed"),Grade(0.,0.)==EGrade::None);
    TestTrue(TEXT("NaN offset fails closed"),Grade(std::numeric_limits<double>::quiet_NaN(),Window)==EGrade::None);
    TestTrue(TEXT("NaN window fails closed"),Grade(.1,std::numeric_limits<double>::quiet_NaN())==EGrade::None);
    auto Rank=[](EGrade G){switch(G){case EGrade::Perfect:return 0;case EGrade::Good:return 1;case EGrade::Late:return 2;default:return 3;}};
    int32 Previous=0;
    for(int32 I=0;I<=10000;++I)
    {
        const double Offset=Window*double(I)/10000.;const int32 Current=Rank(Grade(Offset,Window));
        TestTrue(*FString::Printf(TEXT("grade does not improve with later timing sample %d"),I),Current>=Previous);Previous=Current;
    }
    TestTrue(TEXT("grade posture scale decreases monotonically"),PostureScale(EGrade::Perfect)>=PostureScale(EGrade::Good)&&PostureScale(EGrade::Good)>=PostureScale(EGrade::Late)&&PostureScale(EGrade::Late)>=PostureScale(EGrade::None));

    TestEqual(TEXT("Perfect posture scale"),PostureScale(EGrade::Perfect),1.);
    TestEqual(TEXT("Good posture scale"),PostureScale(EGrade::Good),.6);
    TestEqual(TEXT("Late posture scale"),PostureScale(EGrade::Late),.3);
    TestEqual(TEXT("no-grade posture scale"),PostureScale(EGrade::None),0.);
    return true;
}
#endif
