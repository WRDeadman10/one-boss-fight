// Copyright One Boss Fight. All Rights Reserved.
// BL-58 (lane BL, X-2188): RPGBossRules::ResolveTransition non-finite Health/Max/Fraction and Fraction <0 / >1 -> NotReady; negative health -> Dead;
// exact Name() text for every EBreakResult and ETransitionResult value plus the "?" fallback for an invalid enum. Existing priority/threshold tests are
// not repeated. Asserts existing behaviour only.
#include "Player/RPGBossRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossRulesGuards, "OneBossFight.Framework.BossRules.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossRulesGuards::RunTest(const FString&)
{
    using namespace RPGBossRules;
    const double NaN = std::numeric_limits<double>::quiet_NaN();
    const double Inf = std::numeric_limits<double>::infinity();
    const FFlags F;

    // Controls: at exactly the threshold the transition starts; above it, it waits.
    TestTrue(TEXT("control: 50/100 at fraction 0.5 starts"), ResolveTransition(F, 50., 100., .5f) == ETransitionResult::Start);
    TestTrue(TEXT("control: 80/100 at fraction 0.5 is above threshold"), ResolveTransition(F, 80., 100., .5f) == ETransitionResult::AboveThreshold);

    TestTrue(TEXT("NaN health -> NotReady"), ResolveTransition(F, NaN, 100., .5f) == ETransitionResult::NotReady);
    TestTrue(TEXT("+Inf max -> NotReady"), ResolveTransition(F, 50., Inf, .5f) == ETransitionResult::NotReady);
    TestTrue(TEXT("NaN fraction -> NotReady"), ResolveTransition(F, 50., 100., std::numeric_limits<float>::quiet_NaN()) == ETransitionResult::NotReady);
    TestTrue(TEXT("fraction below 0 -> NotReady"), ResolveTransition(F, 50., 100., -.1f) == ETransitionResult::NotReady);
    TestTrue(TEXT("fraction above 1 -> NotReady"), ResolveTransition(F, 50., 100., 1.1f) == ETransitionResult::NotReady);
    TestTrue(TEXT("negative health -> Dead"), ResolveTransition(F, -1., 100., .5f) == ETransitionResult::Dead);

    // Name(EBreakResult): every value and the fallback.
    TestEqual(TEXT("Break Started"), FString(Name(EBreakResult::Started)), FString(TEXT("started")));
    TestEqual(TEXT("Break Dead"), FString(Name(EBreakResult::Dead)), FString(TEXT("dead")));
    TestEqual(TEXT("Break Dormant"), FString(Name(EBreakResult::Dormant)), FString(TEXT("dormant")));
    TestEqual(TEXT("Break Transition"), FString(Name(EBreakResult::Transition)), FString(TEXT("transition")));
    TestEqual(TEXT("Break AlreadyStaggered"), FString(Name(EBreakResult::AlreadyStaggered)), FString(TEXT("staggered")));
    TestEqual(TEXT("Break Cooldown"), FString(Name(EBreakResult::Cooldown)), FString(TEXT("cooldown")));
    TestEqual(TEXT("Break invalid enum falls back to ?"), FString(Name(static_cast<EBreakResult>(200))), FString(TEXT("?")));

    // Name(ETransitionResult): every value and the fallback.
    TestEqual(TEXT("Transition Start"), FString(Name(ETransitionResult::Start)), FString(TEXT("start")));
    TestEqual(TEXT("Transition NotReady"), FString(Name(ETransitionResult::NotReady)), FString(TEXT("not ready")));
    TestEqual(TEXT("Transition Dead"), FString(Name(ETransitionResult::Dead)), FString(TEXT("dead")));
    TestEqual(TEXT("Transition Dormant"), FString(Name(ETransitionResult::Dormant)), FString(TEXT("dormant")));
    TestEqual(TEXT("Transition AlreadyDone"), FString(Name(ETransitionResult::AlreadyDone)), FString(TEXT("already done")));
    TestEqual(TEXT("Transition AboveThreshold"), FString(Name(ETransitionResult::AboveThreshold)), FString(TEXT("above threshold")));
    TestEqual(TEXT("Transition QueuedBehindStagger"), FString(Name(ETransitionResult::QueuedBehindStagger)), FString(TEXT("queued behind the stance break")));
    TestEqual(TEXT("Transition invalid enum falls back to ?"), FString(Name(static_cast<ETransitionResult>(200))), FString(TEXT("?")));
    return true;
}
#endif
