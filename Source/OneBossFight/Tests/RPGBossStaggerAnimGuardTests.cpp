// Copyright One Boss Fight. All Rights Reserved.
// BL-09 (lane BL, X-2164): RPGStaggerAnim guard clauses that no other test asserted (BL-01..05 audit). Asserts existing behaviour only.
#include "Player/RPGBossStaggerAnimRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossStaggerAnimGuards, "OneBossFight.Framework.Runtime.StaggerAnimGuards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossStaggerAnimGuards::RunTest(const FString&)
{
    using RPGStaggerAnim::EState;
    using RPGStaggerAnim::Evaluate;

    // Invalid geometry fails closed to Finished (Dt chosen inside what would otherwise be the Loop phase).
    TestTrue(TEXT("negative StartLen -> Finished"), Evaluate(-.1f, .6f, 3.f, 1.f) == EState::Finished);
    TestTrue(TEXT("negative EndLen -> Finished"), Evaluate(.8f, -.1f, 3.f, 1.f) == EState::Finished);
    TestTrue(TEXT("Total 0 -> Finished"), Evaluate(.8f, .6f, 0.f, 0.f) == EState::Finished);
    TestTrue(TEXT("negative Total -> Finished"), Evaluate(.8f, .6f, -1.f, 0.f) == EState::Finished);
    TestTrue(TEXT("Start+End above Total -> Finished"), Evaluate(2.f, 2.f, 3.f, 1.f) == EState::Finished);
    TestTrue(TEXT("control: same Dt with valid geometry is Loop"), Evaluate(.8f, .6f, 3.f, 1.f) == EState::Loop);

    // Negative elapsed time: the documented branch order (Dt < StartLen) gives Start.
    TestTrue(TEXT("negative Dt -> Start"), Evaluate(.8f, .6f, 3.f, -1.f) == EState::Start);

    // Validate: a zero Start or End clip length is TooShort.
    auto Params = []()
    {
        RPGStaggerAnim::FPureParams P;
        P.bStart = P.bLoop = P.bEnd = true;
        P.StartLen = .8f; P.LoopLen = .5f; P.EndLen = .6f; P.Total = 3.f;
        P.BossSkeleton = P.StartSkeleton = P.LoopSkeleton = P.EndSkeleton = TEXT("SK_Boss");
        P.Slot = FName(TEXT("DefaultSlot"));
        P.bSlotNodePresent = true;
        return P;
    };
    TestTrue(TEXT("control: valid params pass"), RPGStaggerAnim::Validate(Params()).IsEmpty());
    { auto P = Params(); P.StartLen = 0.f; TestEqual(TEXT("zero StartLen is TooShort"), RPGStaggerAnim::Validate(P), FString(TEXT("Framework.Profile.StaggerAnim.TooShort"))); }
    { auto P = Params(); P.EndLen = 0.f; TestEqual(TEXT("zero EndLen is TooShort"), RPGStaggerAnim::Validate(P), FString(TEXT("Framework.Profile.StaggerAnim.TooShort"))); }
    return true;
}
#endif
