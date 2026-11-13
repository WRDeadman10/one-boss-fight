// Copyright One Boss Fight. All Rights Reserved.
// BL-16 (lane BL): RPGBossChannelDrain tick cap and guard clauses confirmed untested (BL-01..05 audit). Asserts existing behaviour only.
#include "Player/RPGBossChannelDrainRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossChannelDrainGuards, "OneBossFight.Framework.ChannelDrain.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossChannelDrainGuards::RunTest(const FString&)
{
    using namespace RPGBossChannelDrain;
    const double NaN = std::numeric_limits<double>::quiet_NaN();
    const double Inf = std::numeric_limits<double>::infinity();

    // TickCount: the 65-tick cap and the fail-closed inputs.
    TestEqual(TEXT("control: one second at 0.25 s is 4 ticks"), TickCount(0., 1., .25), 4);
    TestEqual(TEXT("ratio exactly at the cap gives 65"), TickCount(0., 65., 1.), 65);
    TestEqual(TEXT("ratio far above the cap gives 65"), TickCount(0., 1000., 1.), 65);
    TestEqual(TEXT("negative start gives 0"), TickCount(-.1, 1., .25), 0);
    TestEqual(TEXT("end equal to start gives 0"), TickCount(1., 1., .25), 0);
    TestEqual(TEXT("end before start gives 0"), TickCount(1., .5, .25), 0);
    TestEqual(TEXT("negative interval gives 0"), TickCount(0., 1., -.25), 0);
    TestEqual(TEXT("NaN start gives 0"), TickCount(NaN, 1., .25), 0);
    TestEqual(TEXT("infinite end gives 0"), TickCount(0., Inf, .25), 0);
    TestEqual(TEXT("NaN interval gives 0"), TickCount(0., 1., NaN), 0);

    // CappedHeal: every fail-closed input gives 0.
    TestEqual(TEXT("control: heal 30 * .5 capped by 7 missing"), CappedHeal(30., .5, 93., 100.), 7.);
    TestEqual(TEXT("heal fraction above 1 gives 0"), CappedHeal(30., 1.01, 50., 100.), 0.);
    TestEqual(TEXT("heal fraction 0 gives 0"), CappedHeal(30., 0., 50., 100.), 0.);
    TestEqual(TEXT("negative heal fraction gives 0"), CappedHeal(30., -.5, 50., 100.), 0.);
    TestEqual(TEXT("negative boss health gives 0"), CappedHeal(30., .5, -1., 100.), 0.);
    // BL-86 correction: BossMaxHealth <= 0 is an EQUIVALENT mutant (BossHealth >= 0 then always satisfies BossHealth >= BossMaxHealth -> 0 anyway).
    TestEqual(TEXT("boss max health 0 gives 0 (equivalent)"), CappedHeal(30., .5, 0., 0.), 0.);
    TestEqual(TEXT("negative boss max health gives 0 (equivalent)"), CappedHeal(30., .5, 0., -100.), 0.);
    TestEqual(TEXT("negative accepted HP gives 0"), CappedHeal(-30., .5, 50., 100.), 0.);
    TestEqual(TEXT("NaN accepted HP gives 0"), CappedHeal(NaN, .5, 50., 100.), 0.);
    TestEqual(TEXT("infinite heal fraction gives 0 (equivalent: HealFraction > 1 also refuses)"), CappedHeal(30., Inf, 50., 100.), 0.);
    TestEqual(TEXT("NaN boss health gives 0"), CappedHeal(30., .5, NaN, 100.), 0.);
    TestEqual(TEXT("infinite boss max health gives 0"), CappedHeal(30., .5, 50., Inf), 0.);
    TestEqual(TEXT("boss health above max gives 0"), CappedHeal(30., .5, 120., 100.), 0.);
    return true;
}
#endif
