// Copyright One Boss Fight. All Rights Reserved.
// BL-77 (lane BL): RPGParryCost::StaminaAfter returns 0 for a negative stamina or cost. Observability: a negative COST discriminates (10 - (-4) would be 14
// without the guard); a negative STAMINA is an EQUIVALENT mutant (Max(0, negative - non-negative cost) is already 0) and is documented. The ParryRefund
// over-max case needs a product decision and is excluded. NaN stamina / Inf cost are already covered. Asserts existing behaviour only.
#include "Player/RPGParryCostRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FParryCostGuards, "OneBossFight.Framework.ParryCost.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FParryCostGuards::RunTest(const FString&)
{
    using RPGParryCost::StaminaAfter;
    TestEqual(TEXT("control: a whiff spends the full cost"), StaminaAfter(10., 4., false), 6.);
    TestEqual(TEXT("negative cost gives 0 (discriminates)"), StaminaAfter(10., -4., false), 0.);
    TestEqual(TEXT("negative cost on a parried press gives 0"), StaminaAfter(10., -4., true), 0.);
    TestEqual(TEXT("negative stamina gives 0 (equivalent mutant)"), StaminaAfter(-1., 4., false), 0.);
    return true;
}
#endif
