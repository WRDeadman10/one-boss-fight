// Copyright One Boss Fight. All Rights Reserved.
// BL-63/64 (lane BL, X-2190): RPGBossStrafe::HoldSeconds non-finite endpoints (the reversed range and the finite-range overflow are already covered by
// RPGBossStrafeTests.cpp:55 and the overflow witness) and DirectionAt invalid elapsed/holds plus segment behaviour beyond the existing boundary
// mutation. Elapsed values stay small so the bounded-but-huge source loop never runs long. Asserts existing behaviour only.
#include "Player/RPGBossStrafeRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossStrafeHoldDirectionGuards, "OneBossFight.Framework.Strafe.HoldDirectionGuards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossStrafeHoldDirectionGuards::RunTest(const FString&)
{
    using namespace RPGBossStrafe;
    const double NaN = std::numeric_limits<double>::quiet_NaN();
    const double Inf = std::numeric_limits<double>::infinity();

    // HoldSeconds: stable in-range control, then non-finite endpoints.
    {
        const double Hold = HoldSeconds(19, 3, .4, 1.1);
        TestTrue(TEXT("control: hold is in range"), Hold >= .4 && Hold <= 1.1);
        TestTrue(TEXT("control: hold is deterministic"), Hold == HoldSeconds(19, 3, .4, 1.1));
    }
    TestEqual(TEXT("NaN min gives 0"), HoldSeconds(19, 3, NaN, 1.1), 0.);
    TestEqual(TEXT("-Inf min gives 0"), HoldSeconds(19, 3, -Inf, 1.1), 0.);
    TestEqual(TEXT("NaN max with a finite min gives the min"), HoldSeconds(19, 3, .4, NaN), .4);
    TestEqual(TEXT("+Inf max with a finite min gives the min"), HoldSeconds(19, 3, .4, Inf), .4);

    // DirectionAt: pick a seed whose initial direction is -1, so "invalid returns 1" discriminates.
    int32 Seed = INDEX_NONE;
    for (int32 S = 0; S < 256 && Seed == INDEX_NONE; ++S) { if (DirectionAt(S, 0., .5, .8) == -1) { Seed = S; } }
    TestTrue(TEXT("a seed with initial direction -1 exists"), Seed != INDEX_NONE);
    if (Seed != INDEX_NONE)
    {
        TestEqual(TEXT("NaN elapsed returns 1"), DirectionAt(Seed, NaN, .5, .8), 1);
        TestEqual(TEXT("negative elapsed returns 1"), DirectionAt(Seed, -.1, .5, .8), 1);
        TestEqual(TEXT("+Inf elapsed returns 1"), DirectionAt(Seed, Inf, .5, .8), 1);
        TestEqual(TEXT("MinHold 0 returns 1"), DirectionAt(Seed, .1, 0., .8), 1);
        TestEqual(TEXT("negative MaxHold returns 1"), DirectionAt(Seed, .1, .5, -.8), 1);
        TestEqual(TEXT("NaN MinHold returns 1"), DirectionAt(Seed, .1, NaN, .8), 1);
        TestEqual(TEXT("NaN MaxHold returns 1"), DirectionAt(Seed, .1, .5, NaN), 1);

        // Segments: the direction flips after the first hold and flips back after the second.
        const double First = HoldSeconds(Seed, 0, .5, .8), Second = HoldSeconds(Seed, 1, .5, .8);
        TestEqual(TEXT("start of segment 0 is the initial direction"), DirectionAt(Seed, 0., .5, .8), -1);
        TestEqual(TEXT("inside segment 1 the direction is flipped"), DirectionAt(Seed, First + .5 * Second, .5, .8), 1);
        TestEqual(TEXT("after two holds the direction is back to the initial one"), DirectionAt(Seed, First + Second + 1.e-6, .5, .8), -1);
    }
    return true;
}
#endif
