// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossPunish.h"
#include "Animation/AnimMontage.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossPunishRules,"OneBossFight.Framework.Punish.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossPunishRules::RunTest(const FString&)
{
    // BOSS-PAC-003 / PAC-005: travel, recovery and margin arithmetic, and the refusals of bad numbers.
    using namespace RPGBossPunish;
    TestTrue(TEXT("already in reach: no travel"),TravelSeconds(120.,150.,600.)==0.);
    TestTrue(TEXT("50 cm outside the reach at 600 cm/s"),FMath::IsNearlyEqual(TravelSeconds(200.,150.,600.),50./600.));
    TestTrue(TEXT("no run speed: never"),TravelSeconds(200.,150.,0.)==TNumericLimits<double>::Max()&&TravelSeconds(std::numeric_limits<double>::quiet_NaN(),150.,600.)==TNumericLimits<double>::Max());
    TestTrue(TEXT("recovery is real seconds: card time over the play rate"),FMath::IsNearlyEqual(RecoverySeconds(.5,1.7,2.),.6));
    TestTrue(TEXT("recovery of a bad card is -1"),RecoverySeconds(1.,.5,1.)==-1.&&RecoverySeconds(.5,1.,0.)==-1.&&RecoverySeconds(.5,std::numeric_limits<double>::infinity(),1.)==-1.);
    const double M=MarginSeconds(1.1,.4,.1);
    TestTrue(TEXT("margin = recovery - (startup + travel)"),FMath::IsNearlyEqual(M,.6));
    TestTrue(TEXT("0.6 clears 0.3 and 0"),PunishOk(M,.3)&&PunishOk(M,0.));
    TestFalse(TEXT("0.6 does not clear 0.7"),PunishOk(M,.7));
    TestFalse(TEXT("exactly short by a hair"),PunishOk(MarginSeconds(.79,.4,.1),.3));
    TestTrue(TEXT("exactly on the margin passes"),PunishOk(.3,.3));
    TestFalse(TEXT("NaN and a negative requirement refuse"),PunishOk(std::numeric_limits<double>::quiet_NaN(),.3)||PunishOk(1.,-.1)||PunishOk(1.,std::numeric_limits<double>::quiet_NaN()));
    TestTrue(TEXT("a non finite margin input is a hopeless margin"),!PunishOk(MarginSeconds(std::numeric_limits<double>::quiet_NaN(),.4,.1),0.));
    FPlayerMoves P;P.LightStartupSeconds=.3;P.HeavyStartupSeconds=.7;P.RunSpeedCmPerSecond=600.;P.ReachCm=150.;TestTrue(TEXT("valid moves"),P.IsValid());
    P.RunSpeedCmPerSecond=0.;TestFalse(TEXT("zero run speed is not valid"),P.IsValid());
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossPunishPackMontages,"OneBossFight.Framework.Punish.PackMontages",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossPunishPackMontages::RunTest(const FString&)
{
    // BOSS-PAC-003 / PAC-005: the startup measured from the pack's REAL player montages is sane (inside the clip, light before heavy) and a montage without an attack trace measures -1.
    const TCHAR* Light=TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/Attack_PrimaryA_Montage.Attack_PrimaryA_Montage");
    const TCHAR* Heavy=TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/ChargedAttack_Montage.ChargedAttack_Montage");
    const UAnimMontage* L=LoadObject<UAnimMontage>(nullptr,Light); const UAnimMontage* H=LoadObject<UAnimMontage>(nullptr,Heavy);
    if (!L||!H) { AddError(TEXT("pack montages not loaded")); return false; }
    const double LS=RPGBossPunish::MeasureStartupSeconds(L), HS=RPGBossPunish::MeasureStartupSeconds(H);
    AddInfo(FString::Printf(TEXT("light startup %.4f s (clip %.3f), charged startup %.4f s (clip %.3f)"),LS,double(L->GetPlayLength()),HS,double(H->GetPlayLength())));
    TestTrue(TEXT("light startup is inside its clip"),LS>0.&&LS<double(L->GetPlayLength()));
    TestTrue(TEXT("charged startup is inside its clip"),HS>0.&&HS<double(H->GetPlayLength()));
    TestTrue(TEXT("the charged attack starts later than the light one"),HS>LS);
    TestTrue(TEXT("a null montage measures -1"),RPGBossPunish::MeasureStartupSeconds(nullptr)==-1.);
    const UAnimMontage* Drink=LoadObject<UAnimMontage>(nullptr,TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/DrinkingPotion_Montage.DrinkingPotion_Montage"));
    if (Drink) TestTrue(TEXT("the drink montage has no attack trace: -1"),RPGBossPunish::MeasureStartupSeconds(Drink)==-1.);
    return true;
}
#endif
