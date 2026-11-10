// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossDefenseRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossDefenseRules,"OneBossFight.Framework.Defense.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossDefenseRules::RunTest(const FString&)
{
    // BOSS-DEF-005: the fair-window rules of a defensive card.
    using namespace RPGBossDefense;
    TestTrue(TEXT("a move that starts 0.3 s in is telegraphed"),TelegraphOk(.3,1.));
    TestFalse(TEXT("0.2 s is not"),TelegraphOk(.2,1.));
    TestTrue(TEXT("exactly 0.25 s is"),TelegraphOk(.25,1.));
    TestTrue(TEXT("card time runs at the play rate: 0.5 card seconds at rate 2 is 0.25 real"),TelegraphOk(.5,2.));
    TestFalse(TEXT("bad numbers are not telegraphed"),TelegraphOk(std::numeric_limits<double>::quiet_NaN(),1.)||TelegraphOk(.5,0.)||TelegraphOk(.5,std::numeric_limits<double>::infinity()));
    TestTrue(TEXT("a 150 cm backstep is fine, 250 is the cap"),BackstepDistanceOk(150.)&&BackstepDistanceOk(250.));
    TestFalse(TEXT("0, 251 and NaN are not"),BackstepDistanceOk(0.)||BackstepDistanceOk(251.)||BackstepDistanceOk(std::numeric_limits<double>::quiet_NaN()));
    TestTrue(TEXT("a 3 s cooldown is enough"),CooldownOk(3.)&&CooldownOk(10.));
    TestFalse(TEXT("2.9 s and NaN are not"),CooldownOk(2.9)||CooldownOk(std::numeric_limits<double>::quiet_NaN()));
    RPGBossPunish::FPlayerMoves M;M.LightStartupSeconds=.35;M.HeavyStartupSeconds=.5;M.RunSpeedCmPerSecond=600.;M.ReachCm=150.;
    // range 200 + backstep 150 = 350, 200 cm outside the reach = 0.3333 s of walking; + 0.35 s startup = 0.6833 s needed
    TestTrue(TEXT("0.75 s of recovery after the backstep leaves a window"),CounterplayMarginSeconds(200.,150.,120.,true,.75,M)>0.);
    TestTrue(TEXT("backstep margin remains 0.75 - 0.6833"),FMath::IsNearlyEqual(CounterplayMarginSeconds(200.,150.,120.,true,.75,M),.75-(.35+200./600.),1e-6));
    TestFalse(TEXT("0.6 s of recovery does not"),RPGBossPunish::PunishOk(CounterplayMarginSeconds(200.,150.,120.,true,.6,M),0.));
    TestFalse(TEXT("a longer backstep needs more recovery"),RPGBossPunish::PunishOk(CounterplayMarginSeconds(200.,250.,120.,true,.75,M),0.));
    TestTrue(TEXT("forward warp counterplay starts at its standoff, not its selector range"),
        FMath::IsNearlyEqual(CounterplayMarginSeconds(650.,450.,120.,false,.467,M),.467-(.35+0.),1e-6));
    return true;
}
#endif
