// Copyright One Boss Fight. All Rights Reserved.
// BL-62 (lane BL, X-2190): RPGBossStrafe::NextPosition fail-closed cases not already in RPGBossStrafeTests.cpp (which covers NaN Boss.X, +Inf speed,
// radius 0.5, Dir 0, zero speed and zero delta): non-finite Target / Boss.Y, negative speed, non-finite and negative delta, Dir +/-2, arc overflow.
// The Angle overflow guard is UNREACHABLE (Radius >= 1 means |Angle| <= ArcLength, which is already finite) and is documented, not tested.
// Asserts existing behaviour only.
#include "Player/RPGBossStrafeRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossStrafeNextPositionGuards, "OneBossFight.Framework.Strafe.NextPositionGuards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossStrafeNextPositionGuards::RunTest(const FString&)
{
    using RPGBossStrafe::NextPosition;
    const double NaN = std::numeric_limits<double>::quiet_NaN();
    const double Inf = std::numeric_limits<double>::infinity();
    const FVector2D Boss(300., 0.), Target(0., 0.);

    // Control: a valid step moves the boss along the circle (radius kept).
    const FVector2D Moved = NextPosition(Boss, Target, 200., 1. / 60., 1);
    TestFalse(TEXT("control: a valid step moves the boss"), Moved.Equals(Boss, 1.e-9));
    TestTrue(TEXT("control: the radius is kept"), FMath::IsNearlyEqual((Moved - Target).Size(), 300., 1.e-6));

    auto ExpectUnchanged = [this, &Boss](const TCHAR* What, const FVector2D& R) { TestTrue(What, R.Equals(Boss, 0.)); };
    ExpectUnchanged(TEXT("NaN Target.X returns Boss"), NextPosition(Boss, FVector2D(NaN, 0.), 200., 1. / 60., 1));
    ExpectUnchanged(TEXT("+Inf Target.Y returns Boss"), NextPosition(Boss, FVector2D(0., Inf), 200., 1. / 60., 1));
    {
        // Equals() cannot compare infinities (|-Inf - -Inf| is NaN), so check that the input is returned component-for-component.
        const FVector2D InfBoss(300., -Inf);
        const FVector2D R = NextPosition(InfBoss, Target, 200., 1. / 60., 1);
        TestTrue(TEXT("-Inf Boss.Y returns the unchanged Boss"), R.X == 300. && R.Y == -Inf);
    }
    ExpectUnchanged(TEXT("negative speed returns Boss"), NextPosition(Boss, Target, -200., 1. / 60., 1));
    ExpectUnchanged(TEXT("NaN delta returns Boss"), NextPosition(Boss, Target, 200., NaN, 1));
    ExpectUnchanged(TEXT("+Inf delta returns Boss"), NextPosition(Boss, Target, 200., Inf, 1));
    ExpectUnchanged(TEXT("negative delta returns Boss"), NextPosition(Boss, Target, 200., -1. / 60., 1));
    ExpectUnchanged(TEXT("Dir 2 returns Boss"), NextPosition(Boss, Target, 200., 1. / 60., 2));
    ExpectUnchanged(TEXT("Dir -2 returns Boss"), NextPosition(Boss, Target, 200., 1. / 60., -2));
    // Finite operands whose arc length overflows to +Inf.
    ExpectUnchanged(TEXT("arc overflow (1e200 * 1e200) returns Boss"), NextPosition(Boss, Target, 1.e200, 1.e200, 1));
    return true;
}
#endif
