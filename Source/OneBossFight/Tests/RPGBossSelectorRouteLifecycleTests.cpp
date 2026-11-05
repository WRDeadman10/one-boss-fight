// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossMoveSelector.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
namespace BossSelectorRouteLifecycleFixture
{
TSharedPtr<const FRPGCompiledBossMoveCard> MakeCard(const TCHAR* Id,float MinRange,float MaxRange)
{
    FRPGBossMoveCardSpec Spec; FRPGBossMoveMetadata Metadata;
    Spec.Schema=1; Spec.MoveId=Id; Spec.FamilyId=TEXT("RouteFamily"); Spec.PhaseId=TEXT("RoutePhase");
    Spec.Skeleton=TSoftObjectPtr<USkeleton>(FSoftObjectPath(TEXT("/Game/OneBossFight/Data/TypedABIFixtures/F1/Skeleton.Skeleton")));
    Spec.Sequence=TSoftObjectPtr<UAnimSequence>(FSoftObjectPath(TEXT("/Game/OneBossFight/Data/TypedABIFixtures/F1/Sequence.Sequence")));
    Spec.SlotName=TEXT("RouteSlot"); Spec.PlayRate=1.f; Spec.CommitSeconds=.25f; Spec.ActiveStartSeconds=.5f;
    Spec.ActiveEndSeconds=1.f; Spec.RecoveryEndSeconds=1.5f; Spec.MinRangeCm=MinRange; Spec.MaxRangeCm=MaxRange;
    Spec.FrontConeDegrees=120.f; Spec.HPDamage=10.f;
    FRPGBossMoveWindow Window; Window.WindowId=TEXT("RouteWindow"); Window.HitGroup=TEXT("RouteGroup");
    Window.SocketA=TEXT("Base"); Window.SocketB=TEXT("Tip"); Window.RadiusCm=8.f; Window.StartSeconds=.5f; Window.EndSeconds=1.f;
    Spec.Windows.Add(Window);
    Metadata.AnimationPath=Spec.Sequence.ToSoftObjectPath(); Metadata.SkeletonPath=Spec.Skeleton.ToSoftObjectPath();
    Metadata.AnimationSkeletonPath=Metadata.MeshSkeletonPath=Metadata.SkeletonPath; Metadata.ClipLengthSeconds=2.;
    Metadata.Slots.Add(Spec.SlotName); Metadata.SocketOrBoneNames.Add(Window.SocketA); Metadata.SocketOrBoneNames.Add(Window.SocketB);
    TSharedPtr<const FRPGCompiledBossMoveCard> Card;
    RPGBossMoveCards::CompileMetadata(Spec,Metadata,Card);
    return Card;
}

FRPGBossDecisionSnapshot Snapshot(uint64 Frame,double Clock,double Range,uint64 Generation=1)
{
    FRPGBossDecisionSnapshot S; S.EncounterId=7; S.Generation=Generation; S.TargetId=9; S.FrameId=Frame;
    S.PhaseId=TEXT("RoutePhase"); S.ClockSeconds=Clock; S.RangeCm=Range; S.SignedYawDegrees=0.;
    S.bTargetValid=true; S.bNeutral=true; return S;
}

FRPGBossSelectorCandidate Candidate(const TCHAR* Id,float MinRange,float MaxRange,float Cooldown=0.f)
{
    FRPGBossSelectorCandidate C; C.Card=MakeCard(Id,MinRange,MaxRange); C.CooldownSeconds=Cooldown; return C;
}

FRPGBossSelectorConfig Config(int32 Seed=0,float TieBand=0.f)
{
    FRPGBossSelectorConfig C; C.RepeatPenalty=.2f; C.RepeatMemory=2; C.TieSeed=Seed; C.TieBand=TieBand; return C;
}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossSelectorImmediateRouteFreshSnapshot,
    "OneBossFight.Framework.SelectorRoute.ImmediateFreshSnapshot", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossSelectorImmediateRouteFreshSnapshot::RunTest(const FString&)
{
    using namespace BossSelectorRouteLifecycleFixture;
    FRPGBossMoveModel Model; FString Error; TestTrue(TEXT("initialize route model"),Model.Initialize(7,1,Error));
    FRPGBossMoveSelector Selector;
    const TArray<FRPGBossSelectorCandidate> Candidates={Candidate(TEXT("Near"),50.f,150.f),Candidate(TEXT("Far"),175.f,225.f,2.f)};
    TestTrue(TEXT("initialize route selector"),Selector.Initialize(Config(),Candidates,Error));
    const FRPGBossDecisionSnapshot CurrentComboSnapshot=Snapshot(11,4.25,200.);
    FRPGBossAttackToken Token; TArray<FRPGBossMoveModelEvent> Events;
    const bool bStarted=Model.Start(Candidates[1].Card,CurrentComboSnapshot,Token,Events,Error);
    TestTrue(TEXT("immediate continuation starts its authored far card with the current combo snapshot"),bStarted);
    if (!bStarted) return false;
    Selector.NoteStarted(1,CurrentComboSnapshot.ClockSeconds);
    TestTrue(TEXT("immediate route card finishes"),Model.Advance(Token,5.85,false,Events,Error));
    FRPGBossSelectorDecision NextDecision;
    TestTrue(TEXT("next normal route is evaluated"),Selector.Select(Model,Snapshot(12,5.85,200.),NextDecision));
    if (NextDecision.Traces.Num()!=Candidates.Num()) return false;
    TestEqual(TEXT("immediate success recorded cooldown from current snapshot clock"),NextDecision.Traces[1].Refusal,FString(TEXT("Selector.Cooldown")));
    TestEqual(TEXT("cooling immediate-route card is not selected"),NextDecision.ChosenIndex,INDEX_NONE);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossSelectorDelayedRouteFreshSnapshot,
    "OneBossFight.Framework.SelectorRoute.DelayedFreshSnapshot", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossSelectorDelayedRouteFreshSnapshot::RunTest(const FString&)
{
    using namespace BossSelectorRouteLifecycleFixture;
    FRPGBossMoveModel Model; FString Error; TestTrue(TEXT("initialize delayed route model"),Model.Initialize(7,1,Error));
    const TArray<FRPGBossSelectorCandidate> Candidates={Candidate(TEXT("Near"),50.f,150.f),Candidate(TEXT("Far"),175.f,225.f,2.f)};
    FRPGBossMoveSelector Selector; TestTrue(TEXT("initialize delayed route selector"),Selector.Initialize(Config(),Candidates,Error));
    FRPGBossAttackToken Token; TArray<FRPGBossMoveModelEvent> Events;
    const FRPGBossDecisionSnapshot BeforePause=Snapshot(10,2.,100.);
    const bool bPrePauseStarted=Model.Start(Candidates[0].Card,BeforePause,Token,Events,Error);
    TestTrue(TEXT("pre-pause card starts"),bPrePauseStarted);
    if (!bPrePauseStarted) return false;
    Selector.NoteStarted(0,BeforePause.ClockSeconds);
    const bool bPrePauseFinished=Model.Advance(Token,3.6,false,Events,Error);
    TestTrue(TEXT("pre-pause card finishes before delayed continuation"),bPrePauseFinished);
    if (!bPrePauseFinished) return false;
    const FRPGBossDecisionSnapshot WakeSnapshot=Snapshot(20,5.,200.);
    TestFalse(TEXT("pre-pause range is stale for the pending far card"),Model.IsEligible(Candidates[1].Card,Snapshot(20,5.,100.),Error));
    TestEqual(TEXT("stale range refuses pending card"),Error,FString(TEXT("MoveModel.Range")));
    FRPGBossAttackToken DelayedToken;
    const bool bDelayedStarted=Model.Start(Candidates[1].Card,WakeSnapshot,DelayedToken,Events,Error);
    TestTrue(TEXT("delayed continuation starts pending far card with fresh wake snapshot"),bDelayedStarted);
    if (!bDelayedStarted) return false;
    Selector.NoteStarted(1,WakeSnapshot.ClockSeconds);
    TestEqual(TEXT("wake snapshot clock is the delayed route clock"),WakeSnapshot.ClockSeconds,5.);
    TestTrue(TEXT("delayed route card finishes"),Model.Advance(DelayedToken,6.6,false,Events,Error));
    FRPGBossSelectorDecision NextDecision; TestTrue(TEXT("post-delay normal route is evaluated"),Selector.Select(Model,Snapshot(21,6.6,200.),NextDecision));
    if (NextDecision.Traces.Num()!=Candidates.Num()) return false;
    TestEqual(TEXT("delayed success recorded cooldown from wake snapshot clock"),NextDecision.Traces[1].Refusal,FString(TEXT("Selector.Cooldown")));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossSelectorGenerationResetClearsMemory,
    "OneBossFight.Framework.SelectorRoute.GenerationResetClearsMemory", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossSelectorGenerationResetClearsMemory::RunTest(const FString&)
{
    using namespace BossSelectorRouteLifecycleFixture;
    FRPGBossMoveSelector Selector; FString Error;
    TestTrue(TEXT("initialize selector"),Selector.Initialize(Config(),{Candidate(TEXT("A"),50.f,150.f,2.f),Candidate(TEXT("B"),50.f,150.f)},Error));
    Selector.NoteStarted(0,100.); Selector.Reset();
    FRPGBossMoveModel NextGeneration; TestTrue(TEXT("initialize next generation model"),NextGeneration.Initialize(7,2,Error));
    FRPGBossSelectorDecision Decision;
    TestTrue(TEXT("new generation accepts its lower encounter clock"),Selector.Select(NextGeneration,Snapshot(1,5.,100.,2),Decision));
    TestEqual(TEXT("reset clears prior cooldown and repeat memory"),Decision.MoveId,FName(TEXT("A")));
    TestTrue(TEXT("new generation snapshot carries the incremented epoch"),Decision.Traces.Num()==2);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossSelectorZeroTieSeedIsValid,
    "OneBossFight.Framework.SelectorRoute.ZeroTieSeedIsValid", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossSelectorZeroTieSeedIsValid::RunTest(const FString&)
{
    using namespace BossSelectorRouteLifecycleFixture;
    FRPGBossMoveModel Model; FString Error; TestTrue(TEXT("initialize zero-seed model"),Model.Initialize(7,1,Error));
    FRPGBossMoveSelector Selector;
    TestTrue(TEXT("zero tie seed initializes valid policy"),Selector.Initialize(Config(0,.5f),{Candidate(TEXT("A"),50.f,150.f),Candidate(TEXT("B"),50.f,150.f)},Error));
    FRPGBossSelectorDecision Decision;
    TestTrue(TEXT("zero-seed tie selection succeeds"),Selector.Select(Model,Snapshot(1,1.,100.),Decision));
    const bool bValidChoice=Decision.ChosenIndex>=0&&Decision.ChosenIndex<Decision.Traces.Num();
    TestTrue(TEXT("zero-seed choice is one of the eligible candidates"),bValidChoice);
    if (!bValidChoice) return false;
    TestEqual(TEXT("chosen ID matches the eligible trace"),Decision.MoveId,Decision.Traces[Decision.ChosenIndex].MoveId);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossSelectorRouteClockRegressionRefused,
    "OneBossFight.Framework.SelectorRoute.ClockRegressionRefused", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossSelectorRouteClockRegressionRefused::RunTest(const FString&)
{
    using namespace BossSelectorRouteLifecycleFixture;
    FRPGBossMoveModel Model; FString Error; TestTrue(TEXT("initialize clock route model"),Model.Initialize(7,1,Error));
    const FRPGBossSelectorCandidate Only=Candidate(TEXT("Clocked"),50.f,150.f);
    FRPGBossMoveSelector Selector; TestTrue(TEXT("initialize clock selector"),Selector.Initialize(Config(),{Only},Error));
    const FRPGBossDecisionSnapshot First=Snapshot(10,10.,100.);
    FRPGBossAttackToken Token; TArray<FRPGBossMoveModelEvent> Events;
    TestTrue(TEXT("start at initial monotonic clock"),Model.Start(Only.Card,First,Token,Events,Error));
    Selector.NoteStarted(0,First.ClockSeconds);
    TestTrue(TEXT("finish the first model card"),Model.Advance(Token,11.6,false,Events,Error));
    FRPGBossSelectorDecision Decision;
    TestTrue(TEXT("selector returns refusal trace on clock regression"),Selector.Select(Model,Snapshot(11,9.9,100.),Decision));
    if (Decision.Traces.Num()!=1) return false;
    TestEqual(TEXT("regressed route snapshot refuses as stale"),Decision.Traces[0].Refusal,FString(TEXT("MoveModel.StaleDecision")));
    TestEqual(TEXT("clock regression selects no card"),Decision.ChosenIndex,INDEX_NONE);
    return true;
}
#endif
