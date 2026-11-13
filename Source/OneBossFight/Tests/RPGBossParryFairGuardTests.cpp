// Copyright One Boss Fight. All Rights Reserved.
// BL-42 (lane BL, X-2179): RPGBossParryFair negative Telegraph/Window/Reaction fail false; an overflowing ReactionGap (tiny positive PlayRate) fails false;
// +Inf in fields the NaN-only existing tests do not cover. The negative and overflow cases would be FAIR without their guard; the two +Inf cases are
// equivalent mutants (BL-86 correction, see below). Asserts existing behaviour only.
#include "Player/RPGBossParryFairRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossParryFairGuards, "OneBossFight.Framework.BossParryFair.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossParryFairGuards::RunTest(const FString&)
{
    using RPGBossParryFair::ParryableOk;
    const double Inf = std::numeric_limits<double>::infinity();

    // Control: a 0.5 s gap at play rate 1 is fair (needs 0.2 + 0.125).
    TestTrue(TEXT("control: 0.5 s gap is fair"), ParryableOk(0., .5, 1.));

    TestFalse(TEXT("negative telegraph fails closed"), ParryableOk(-.1, .5, 1.));
    TestFalse(TEXT("negative window fails closed"), ParryableOk(0., .5, 1., -.1, .2));
    TestFalse(TEXT("negative reaction fails closed"), ParryableOk(0., .5, 1., .25, -.1));

    // Overflow: the same huge gap is fair at play rate 1 but overflows to +Inf at a tiny positive play rate.
    TestTrue(TEXT("control: a 1e308 s gap at play rate 1 is fair"), ParryableOk(0., 1.e308, 1.));
    TestFalse(TEXT("overflowing reaction gap fails closed"), ParryableOk(0., 1.e308, 1.e-300));

    // BL-86 correction: these two are EQUIVALENT mutants, not "fair without the guard": +Inf active start makes ReactionGap +Inf, which the
    // IsFinite(ReactionGap) check at :23 refuses; +Inf reaction makes `gap >= Inf` false. They document behaviour.
    TestFalse(TEXT("+Inf active start fails closed (equivalent)"), ParryableOk(0., Inf, 1.));
    TestFalse(TEXT("+Inf reaction fails closed (equivalent)"), ParryableOk(0., .5, 1., .25, Inf));
    return true;
}
#endif
