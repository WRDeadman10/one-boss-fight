// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossPunishRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossPunishSweep,"OneBossFight.Framework.Punish.Sweep",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossPunishSweep::RunTest(const FString&)
{
    using namespace RPGBossPunish;
    bool bRangeMonotonic=true, bFinite=true, bRecoveryMonotonic=true;
    for (int32 Recovery=0;Recovery<=500;++Recovery)
    {
        const double R=double(Recovery)/100.;
        double PreviousMargin=1.e9; // lead hotfix: the range loop checks "never improves", so it starts from +big (was -big: first sample always failed)
        for (int32 Distance=0;Distance<=3000;Distance+=10)
        {
            const double Travel=TravelSeconds(double(Distance),150.,600.);
            const double Margin=MarginSeconds(R,.4,Travel);
            bFinite&=FMath::IsFinite(Margin);
            bRangeMonotonic&=Margin<=PreviousMargin+1.e-9;
            PreviousMargin=Margin;
        }
    }
    for (int32 Distance=0;Distance<=3000;Distance+=10)
    {
        double Previous=-1.e9;
        for (int32 Recovery=0;Recovery<=500;++Recovery)
        {
            const double Margin=MarginSeconds(double(Recovery)/100.,.4,TravelSeconds(double(Distance),150.,600.));
            bRecoveryMonotonic&=Margin+1.e-9>=Previous;
            Previous=Margin;
        }
    }
    TestTrue(TEXT("margins stay finite and never improve as range grows"),bFinite&&bRangeMonotonic);
    TestTrue(TEXT("margins never decrease as recovery grows"),bRecoveryMonotonic);
    return true;
}
#endif
