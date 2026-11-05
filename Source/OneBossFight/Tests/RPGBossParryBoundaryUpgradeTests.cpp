// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGParryGradeRules.h"
#include "Player/RPGParryRules.h"
#include "Player/RPGParryCostRules.h"
#include "Misc/AutomationTest.h"
#include <cmath>
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossParryGradeFortyPercentAdjacent,
    "OneBossFight.Framework.ParryGrade.FortyPercentAdjacent", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossParryGradeFortyPercentAdjacent::RunTest(const FString&)
{
    using RPGParryGrade::EGrade;
    constexpr double Window=.25, Edge=Window*.4;
    const double Before=std::nextafter(Edge,0.);
    const double After=std::nextafter(Edge,std::numeric_limits<double>::infinity());
    TestTrue(TEXT("nearest value before forty percent is Perfect"),RPGParryGrade::Grade(Before,Window)==EGrade::Perfect);
    TestTrue(TEXT("nearest value after forty percent is Good"),RPGParryGrade::Grade(After,Window)==EGrade::Good);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossParryGradeEightyPercentAdjacent,
    "OneBossFight.Framework.ParryGrade.EightyPercentAdjacent", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossParryGradeEightyPercentAdjacent::RunTest(const FString&)
{
    using RPGParryGrade::EGrade;
    constexpr double Window=.25, Edge=Window*.8;
    const double Before=std::nextafter(Edge,0.);
    const double After=std::nextafter(Edge,std::numeric_limits<double>::infinity());
    TestTrue(TEXT("nearest value before eighty percent is Good"),RPGParryGrade::Grade(Before,Window)==EGrade::Good);
    TestTrue(TEXT("nearest value after eighty percent is Late"),RPGParryGrade::Grade(After,Window)==EGrade::Late);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossParryLastValidOffsetSharedBoundary,
    "OneBossFight.Framework.ParryGrade.LastValidSharedBoundary", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossParryLastValidOffsetSharedBoundary::RunTest(const FString&)
{
    constexpr double Window=.25;
    const double LastValid=std::nextafter(Window,0.);
    RPGParry::FState State; TestTrue(TEXT("open parry window"),RPGParry::Press(State,0.,Window,.7));
    TestTrue(TEXT("last valid offset lies inside press window"),RPGParry::IsOpen(State,LastValid,Window));
    TestTrue(TEXT("last valid offset receives Late grade"),RPGParryGrade::Grade(LastValid,Window)==RPGParryGrade::EGrade::Late);
    TestFalse(TEXT("exact close is outside press window"),RPGParry::IsOpen(State,Window,Window));
    TestTrue(TEXT("exact close has no grade"),RPGParryGrade::Grade(Window,Window)==RPGParryGrade::EGrade::None);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossParryReadyAtAdvancesAfterAcceptance,
    "OneBossFight.Framework.Parry.CooldownAcceptedReadyAtAdvance", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossParryReadyAtAdvancesAfterAcceptance::RunTest(const FString&)
{
    RPGParry::FState State;
    TestTrue(TEXT("initial press succeeds"),RPGParry::Press(State,1.,.25,.7));
    const double FirstReadyAt=State.ReadyAt;
    TestTrue(TEXT("press at exact ready time succeeds"),RPGParry::Press(State,FirstReadyAt,.25,.7));
    TestEqual(TEXT("opening time advances to prior ready time"),State.OpenedAt,FirstReadyAt);
    TestEqual(TEXT("ready time advances by configured cooldown"),State.ReadyAt,FirstReadyAt+.7);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossParryCostRejectsInfiniteOperands,
    "OneBossFight.Framework.ParryCost.InfiniteOperands", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossParryCostRejectsInfiniteOperands::RunTest(const FString&)
{
    const double Inf=std::numeric_limits<double>::infinity();
    TestFalse(TEXT("positive infinite stamina rejected"),RPGParryCost::CanPress(Inf,1.));
    TestFalse(TEXT("negative infinite stamina rejected"),RPGParryCost::CanPress(-Inf,1.));
    TestFalse(TEXT("positive infinite cost rejected"),RPGParryCost::CanPress(1.,Inf));
    TestFalse(TEXT("negative infinite cost rejected"),RPGParryCost::CanPress(1.,-Inf));
    return true;
}
#endif
