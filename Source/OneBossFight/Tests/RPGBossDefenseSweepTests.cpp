// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossDefenseRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossDefenseSweep,"OneBossFight.Framework.Defense.Sweep",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossDefenseSweep::RunTest(const FString&)
{
    using namespace RPGBossDefense;
    constexpr double Eps=1.e-6;
    TestFalse(TEXT("telegraph just below real-time minimum fails"),TelegraphOk((MinTelegraphSeconds-Eps)*1.,1.));
    TestTrue(TEXT("telegraph safely above minimum passes"),TelegraphOk((MinTelegraphSeconds+Eps)*1.,1.));
    TestFalse(TEXT("rate zero fails closed"),TelegraphOk(1.,0.));
    TestTrue(TEXT("backstep safely inside cap passes"),BackstepDistanceOk(MaxBackstepCm-Eps));
    TestFalse(TEXT("backstep safely beyond cap fails"),BackstepDistanceOk(MaxBackstepCm+Eps));
    TestFalse(TEXT("zero backstep fails"),BackstepDistanceOk(0.));
    TestTrue(TEXT("cooldown safely above minimum passes"),CooldownOk(MinCooldownSeconds+Eps));
    TestFalse(TEXT("cooldown safely below minimum fails"),CooldownOk(MinCooldownSeconds-Eps));
    RPGBossPunish::FPlayerMoves Moves; Moves.LightStartupSeconds=.35; Moves.HeavyStartupSeconds=.55; Moves.RunSpeedCmPerSecond=600.; Moves.ReachCm=150.;
    const double Needed=.35+RPGBossPunish::TravelSeconds(350.,150.,600.);
    TestTrue(TEXT("counterplay with explicit safety margin passes"),RPGBossPunish::PunishOk(CounterplayMarginSeconds(200.,150.,120.,true,Needed+.02,Moves),.01));
    TestFalse(TEXT("counterplay below required window fails"),RPGBossPunish::PunishOk(CounterplayMarginSeconds(200.,150.,120.,true,Needed-.02,Moves),.01));
    TestFalse(TEXT("non-finite move values fail closed"),RPGBossPunish::PunishOk(CounterplayMarginSeconds(200.,150.,120.,true,1.,RPGBossPunish::FPlayerMoves()),0.));
    TestTrue(TEXT("forward warp uses standoff for travel"),
        FMath::IsNearlyEqual(CounterplayMarginSeconds(650.,450.,120.,false,.467,Moves),.467-(.35+0.),1.e-6));
    return true;
}
#endif
