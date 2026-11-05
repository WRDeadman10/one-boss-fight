// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossArenaEdgeRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossArenaEdgeRules,"OneBossFight.Framework.ArenaEdge.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossArenaEdgeRules::RunTest(const FString&)
{
    using namespace RPGBossArenaEdge;const FVector2D C(0.,0.);
    const FResult Safe=Evaluate(FVector2D(700.,0.),C,1000.,200.);TestEqual(TEXT("interior has no edge pressure"),Safe.Pressure,0.);
    const FResult Half=Evaluate(FVector2D(900.,0.),C,1000.,200.);TestTrue(TEXT("half margin gives half pressure"),FMath::IsNearlyEqual(Half.Pressure,.5));TestTrue(TEXT("inward direction points to arena center"),Half.Inward==FVector2D(-1.,0.));
    TestEqual(TEXT("at the wall gives maximum pressure"),Evaluate(FVector2D(1000.,0.),C,1000.,200.).Pressure,1.);
    TestEqual(TEXT("outside arena remains clamped"),Evaluate(FVector2D(1200.,0.),C,1000.,200.).Pressure,1.);
    TestEqual(TEXT("boss at center has no defined inward direction"),Evaluate(C,C,1000.,200.).Pressure,0.);
    TestEqual(TEXT("invalid margin fails closed"),Evaluate(FVector2D(990.,0.),C,1000.,0.).Pressure,0.);
    TestEqual(TEXT("non-finite radius fails closed"),Evaluate(FVector2D(990.,0.),C,std::numeric_limits<double>::infinity(),200.).Pressure,0.);
    return true;
}
#endif
