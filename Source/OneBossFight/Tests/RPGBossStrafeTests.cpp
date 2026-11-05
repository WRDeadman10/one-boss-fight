// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossStrafeRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossStrafeRules, "OneBossFight.Framework.Strafe.Rules", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossStrafeRules::RunTest(const FString&)
{
    using namespace RPGBossStrafe;
    const FVector2D Target(0., 0.);
    const FVector2D Start(300., 0.);
    const double Pi = 3.14159265358979323846;

    const FVector2D OneStep = NextPosition(Start, Target, 200., 1. / 60., 1);
    const double OneStepAngle = FMath::Atan2(OneStep.Y, OneStep.X);
    TestTrue(TEXT("one-step angular displacement is arc length divided by radius"), FMath::Abs(OneStepAngle - (200. / 60. / 300.)) < 1.e-9);
    const FVector2D ReverseStep = NextPosition(Start, Target, 200., 1. / 60., -1);
    TestTrue(TEXT("negative direction rotates the other way"), ReverseStep.Y < 0.);

    FVector2D Position = Start;
    for (int32 I = 0; I < 600; ++I)
        Position = NextPosition(Position, Target, 200., 1. / 60., 1);
    TestTrue(TEXT("radius is preserved over 600 steps"), FMath::Abs(FVector2D::Distance(Position, Target) - 300.) < .01);
    TestTrue(TEXT("600 steps advance by the expected angle"), FMath::Abs(FMath::Atan2(Position.Y, Position.X) - (200. * 10. / 300. - 2. * Pi)) < 1.e-9);

    FRandomStream Random(0x90A11);Position=FVector2D(300.,0.);
    for(int32 I=0;I<10000;++I)
    {
        const double Speed=Random.FRandRange(20.f,400.f),Dt=Random.FRandRange(1.f/240.f,1.f/30.f);
        Position=NextPosition(Position,Target,Speed,Dt,(I&1)?1:-1);
        if((I%100)==0)TestTrue(*FString::Printf(TEXT("seeded strafe remains on arena radius at step %d"),I),FMath::Abs(FVector2D::Distance(Position,Target)-300.)<.01);
    }
    TestTrue(TEXT("long seeded strafe remains on arena radius at final step"),FMath::Abs(FVector2D::Distance(Position,Target)-300.)<.01);

    const double NaN = std::numeric_limits<double>::quiet_NaN();
    const double Inf = std::numeric_limits<double>::infinity();
    const FVector2D InvalidResults[] = {
        NextPosition(FVector2D(NaN, 0.), Target, 1., 1., 1),
        NextPosition(Start, Target, Inf, 1., 1),
        NextPosition(FVector2D(.5, 0.), Target, 1., 1., 1),
        NextPosition(Start, Target, 1., 1., 0),
        NextPosition(Start, Target, 0., 1., 1),
        NextPosition(Start, Target, 1., 0., 1)
    };
    for (int32 I = 0; I < UE_ARRAY_COUNT(InvalidResults); ++I)
        TestTrue(FString::Printf(TEXT("invalid movement case %d leaves Boss unchanged"), I), InvalidResults[I] == (I == 2 ? FVector2D(.5, 0.) : Start));

    for (int32 I = 0; I < 100; ++I)
    {
        const double Hold = HoldSeconds(19, I, .4, 1.1);
        TestTrue(FString::Printf(TEXT("hold %d lies in range"), I), Hold >= .4 && Hold <= 1.1);
        TestTrue(FString::Printf(TEXT("hold %d is deterministic"), I), Hold == HoldSeconds(19, I, .4, 1.1));
    }
    TestTrue(TEXT("reversed hold range collapses to minimum"), HoldSeconds(3, 7, 2.5, 1.) == 2.5);
    const double FirstHold = HoldSeconds(29, 0, .5, .8);
    const int32 BeforeBoundary = DirectionAt(29, FirstHold - 1.e-9, .5, .8);
    const int32 AtBoundary = DirectionAt(29, FirstHold, .5, .8);
    TestTrue(TEXT("direction flips at the first hold boundary"), BeforeBoundary == -AtBoundary);
    TestTrue(TEXT("direction is always plus or minus one"), (BeforeBoundary == 1 || BeforeBoundary == -1) && (AtBoundary == 1 || AtBoundary == -1));
    return true;
}
#endif
