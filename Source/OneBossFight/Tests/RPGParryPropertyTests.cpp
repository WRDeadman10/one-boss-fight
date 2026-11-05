// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGParryGradeRules.h"
#include "Player/RPGParryRules.h"
#include "Player/RPGParryCostRules.h"
#include "Misc/AutomationTest.h"
#include <cmath>
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGParryGradeBoundedProperty,"OneBossFight.Parry.Property.Grade",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FRPGParryGradeBoundedProperty::RunTest(const FString&)
{
    FRandomStream Random(0xD121); // Fixed seed; generated windows are a harness domain only.
    const auto Rank=[](RPGParryGrade::EGrade G)
    { return G==RPGParryGrade::EGrade::Perfect?0:G==RPGParryGrade::EGrade::Good?1:G==RPGParryGrade::EGrade::Late?2:3; };
    for(int32 Case=0;Case<128;++Case)
    {
        const double Window=Random.FRandRange(.01f,2.f);
        int32 Previous=-1;
        for(int32 Point=0;Point<=16;++Point)
        {
            const double Offset=Window*double(Point)/16.;
            const auto Grade=RPGParryGrade::Grade(Offset,Window);
            if(Point<16) TestTrue(TEXT("every in-window offset has a grade"),Grade!=RPGParryGrade::EGrade::None);
            else TestTrue(TEXT("exact close edge is excluded"),Grade==RPGParryGrade::EGrade::None);
            if(Point<16){TestTrue(TEXT("grade rank never decreases"),Rank(Grade)>=Previous);Previous=Rank(Grade);}
        }
        const double P40=.4*Window,P80=.8*Window;
        if(P40/Window==.4) TestTrue(TEXT("exact 40 percent boundary is Good"),RPGParryGrade::Grade(P40,Window)==RPGParryGrade::EGrade::Good);
        if(P80/Window==.8) TestTrue(TEXT("exact 80 percent boundary is Late"),RPGParryGrade::Grade(P80,Window)==RPGParryGrade::EGrade::Late);
        const double Before40=std::nextafter(P40,std::numeric_limits<double>::lowest()),Before80=std::nextafter(P80,std::numeric_limits<double>::lowest());
        if(Before40>=0.&&Before40/Window<.4) TestTrue(TEXT("representable instant before 40 percent is Perfect"),RPGParryGrade::Grade(Before40,Window)==RPGParryGrade::EGrade::Perfect);
        if(Before80>=0.&&Before80/Window<.8) TestTrue(TEXT("representable instant before 80 percent is Good"),RPGParryGrade::Grade(Before80,Window)==RPGParryGrade::EGrade::Good);
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGParryCooldownBoundedProperty,"OneBossFight.Parry.Property.Cooldown",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FRPGParryCooldownBoundedProperty::RunTest(const FString&)
{
    FRandomStream Random(0xD122); // Bounded finite values keep Now + max duration finite.
    for(int32 Case=0;Case<128;++Case)
    {
        const double Now=Random.FRandRange(0.f,1000.f);
        const double Window=Random.FRandRange(.01f,10.f);
        double Cooldown=Random.FRandRange(.01f,10.f);
        if(Case%3==0) Cooldown=Window*.5;
        else if(Case%3==1) Cooldown=Window;
        else Cooldown=Window*2.;
        RPGParry::FState State;
        TestTrue(TEXT("fresh press is accepted"),RPGParry::Press(State,Now,Window,Cooldown));
        TestEqual(TEXT("ready time follows max duration"),State.ReadyAt,Now+FMath::Max(Window,Cooldown));
        TestTrue(TEXT("cooldown does not end before the window"),State.ReadyAt>=State.OpenedAt+Window);
        const RPGParry::FState Before=State;
        TestFalse(TEXT("immediately-before-ready press is refused"),RPGParry::Press(State,std::nextafter(State.ReadyAt,std::numeric_limits<double>::lowest()),Window,Cooldown));
        TestEqual(TEXT("refusal preserves open time"),State.OpenedAt,Before.OpenedAt);
        TestEqual(TEXT("refusal preserves ready time"),State.ReadyAt,Before.ReadyAt);
        TestTrue(TEXT("exact ready time is accepted"),RPGParry::Press(State,Before.ReadyAt,Window,Cooldown));
        TestEqual(TEXT("accepted boundary opens at ready time"),State.OpenedAt,Before.ReadyAt);
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGParryCostBoundedProperty,"OneBossFight.Parry.Property.Cost",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FRPGParryCostBoundedProperty::RunTest(const FString&)
{
    FRandomStream Random(0xD123); // Values stay below 1e6; this is not a gameplay limit.
    for(int32 Case=0;Case<128;++Case)
    {
        const double Stamina=Random.FRandRange(0.f,1000000.f);
        const double Cost=Random.FRandRange(0.f,1000000.f);
        const double Maximum=Random.FRandRange(0.f,1000000.f);
        TestEqual(TEXT("press eligibility follows stamina >= cost"),RPGParryCost::CanPress(Stamina,Cost),Stamina>=Cost);
        const double Full=RPGParryCost::StaminaAfter(Stamina,Cost,false);
        const double Half=RPGParryCost::StaminaAfter(Stamina,Cost,true);
        TestTrue(TEXT("full-cost result stays within bounds"),Full>=0.&&Full<=Stamina);
        TestTrue(TEXT("half-cost result stays within bounds"),Half>=0.&&Half<=Stamina);
        TestTrue(TEXT("full cost is no greater than half-cost result"),Full<=Half);
        if(Stamina>=Cost)
        {
            TestTrue(TEXT("full-cost conservation outside floor region"),FMath::IsNearlyEqual(Stamina-Full,Cost,1.e-8));
            TestTrue(TEXT("half-cost conservation outside floor region"),FMath::IsNearlyEqual(Stamina-Half,Cost*.5,1.e-8));
        }
        const double Refund=RPGParryCost::ParryRefund(Stamina,Maximum,Cost);
        const double MoreRefund=RPGParryCost::ParryRefund(Stamina+1.,Maximum,Cost);
        TestTrue(TEXT("refund remains capped"),Refund>=0.&&Refund<=Maximum);
        TestTrue(TEXT("refund is monotone in stamina"),MoreRefund>=Refund);
    }
    return true;
}
#endif
