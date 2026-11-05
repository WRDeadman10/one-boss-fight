// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGParryCostRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FParryCostRules,"OneBossFight.Framework.ParryCost.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FParryCostRules::RunTest(const FString&)
{
    using namespace RPGParryCost;

    TestTrue(TEXT("enough stamina can press"),CanPress(10.,4.));
    TestTrue(TEXT("exact cost can press"),CanPress(4.,4.));
    TestFalse(TEXT("insufficient stamina cannot press"),CanPress(3.99,4.));
    TestFalse(TEXT("negative stamina cannot press"),CanPress(-1.,0.));
    TestFalse(TEXT("negative cost cannot press"),CanPress(10.,-1.));
    TestFalse(TEXT("NaN stamina cannot press"),CanPress(std::numeric_limits<double>::quiet_NaN(),1.));
    TestFalse(TEXT("NaN cost cannot press"),CanPress(1.,std::numeric_limits<double>::quiet_NaN()));
    TestTrue(TEXT("maximum stamina can pay a parry cost"),CanPress(100.,4.));

    TestTrue(TEXT("a parried press refunds half the cost"),FMath::IsNearlyEqual(StaminaAfter(10.,4.,true),8.));
    TestTrue(TEXT("a whiff spends the full cost"),FMath::IsNearlyEqual(StaminaAfter(10.,4.,false),6.));
    TestEqual(TEXT("a parried press never exceeds available stamina"),StaminaAfter(3.,4.,true),1.);
    TestEqual(TEXT("a whiff never drains below zero"),StaminaAfter(3.,4.,false),0.);
    TestEqual(TEXT("invalid stamina fails closed"),StaminaAfter(std::numeric_limits<double>::quiet_NaN(),1.,true),0.);
    TestEqual(TEXT("invalid cost fails closed"),StaminaAfter(10.,std::numeric_limits<double>::infinity(),false),0.);
    TestTrue(TEXT("parry refund is capped at maximum stamina"),FMath::IsNearlyEqual(ParryRefund(99.,100.,4.),100.));
    TestTrue(TEXT("parry refund adds half cost below maximum"),FMath::IsNearlyEqual(ParryRefund(90.,100.,4.),92.));
    TestEqual(TEXT("negative maximum fails closed"),ParryRefund(10.,-1.,4.),0.);
    TestEqual(TEXT("NaN refund input fails closed"),ParryRefund(std::numeric_limits<double>::quiet_NaN(),100.,4.),0.);
    return true;
}
#endif
