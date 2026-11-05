// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossMoveSelector.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
namespace
{
TSharedPtr<const FRPGCompiledBossMoveCard> LoopCard(const TCHAR* Id)
{
    FRPGBossMoveCardSpec Spec;
    FRPGBossMoveMetadata Meta;
    Spec.Schema=1; Spec.MoveId=Id; Spec.FamilyId=TEXT("LoopFamily"); Spec.PhaseId=TEXT("PhaseOne");
    Spec.Skeleton=TSoftObjectPtr<USkeleton>(FSoftObjectPath(TEXT("/Game/OneBossFight/Data/TypedABIFixtures/F1/Skeleton.Skeleton")));
    Spec.Sequence=TSoftObjectPtr<UAnimSequence>(FSoftObjectPath(TEXT("/Game/OneBossFight/Data/TypedABIFixtures/F1/Sequence.Sequence")));
    Spec.SlotName=TEXT("SyntheticSlot"); Spec.PlayRate=1.f; Spec.CommitSeconds=.25f;
    Spec.ActiveStartSeconds=.5f; Spec.ActiveEndSeconds=1.f; Spec.RecoveryEndSeconds=1.5f;
    Spec.MinRangeCm=50.f; Spec.MaxRangeCm=150.f; Spec.FrontConeDegrees=120.f; Spec.HPDamage=10.f;
    FRPGBossMoveWindow Window; Window.WindowId=TEXT("Window"); Window.HitGroup=TEXT("Blade");
    Window.SocketA=TEXT("Base"); Window.SocketB=TEXT("Tip"); Window.RadiusCm=8.f;
    Window.StartSeconds=.5f; Window.EndSeconds=1.f; Spec.Windows.Add(Window);
    Meta.AnimationPath=Spec.Sequence.ToSoftObjectPath(); Meta.SkeletonPath=Spec.Skeleton.ToSoftObjectPath();
    Meta.AnimationSkeletonPath=Meta.MeshSkeletonPath=Meta.SkeletonPath; Meta.ClipLengthSeconds=2.;
    Meta.Slots.Add(Spec.SlotName); Meta.SocketOrBoneNames.Add(Window.SocketA); Meta.SocketOrBoneNames.Add(Window.SocketB);
    TSharedPtr<const FRPGCompiledBossMoveCard> Card;
    RPGBossMoveCards::CompileMetadata(Spec,Meta,Card);
    return Card;
}

FRPGBossDecisionSnapshot LoopSnapshot(uint64 Generation,uint64 Frame,double Clock)
{
    FRPGBossDecisionSnapshot S; S.EncounterId=77; S.Generation=Generation; S.TargetId=9; S.FrameId=Frame;
    S.PhaseId=TEXT("PhaseOne"); S.ClockSeconds=Clock; S.RangeCm=100.; S.SignedYawDegrees=0.;
    S.bTargetValid=true; S.bNeutral=true; return S;
}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossEncounterPureLoopRestart,
    "OneBossFight.Framework.EncounterLoop.PureSelectorModelRestart",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossEncounterPureLoopRestart::RunTest(const FString&)
{
    FRPGBossSelectorConfig Config;
    Config.RepeatPenalty=.2f; Config.RepeatMemory=1;
    FRPGBossSelectorCandidate A; A.Card=LoopCard(TEXT("LoopA")); A.CooldownSeconds=0.f;
    FRPGBossSelectorCandidate B; B.Card=LoopCard(TEXT("LoopB")); B.CooldownSeconds=0.f;
    if (!TestTrue(TEXT("synthetic cards compiled"),A.Card.IsValid()&&B.Card.IsValid())) return false;

    FRPGBossMoveModel Model; FString Error;
    FRPGBossMoveSelector Selector;
    TestTrue(TEXT("model initializes for generation one"),Model.Initialize(77,1,Error));
    TestTrue(TEXT("selector initializes"),Selector.Initialize(Config,{A,B},Error));
    FRPGBossSelectorContext Context;
    TArray<FRPGBossMoveModelEvent> Events;
    FRPGBossAttackToken PreviousGenerationToken;
    int32 CompletedGenerationOne=0;
    int32 PreviousChoice=INDEX_NONE;

    for (int32 Attack=0;Attack<2;++Attack)
    {
        FRPGBossDecisionSnapshot S=LoopSnapshot(1,10+Attack*2,100.+Attack*2.);
        FRPGBossSelectorDecision Decision;
        TestTrue(TEXT("generation-one selection runs"),Selector.Select(Model,S,Decision,Context));
        TestTrue(TEXT("generation-one chooses a candidate"),Decision.ChosenIndex!=INDEX_NONE);
        if (!Decision.Traces.IsValidIndex(Decision.ChosenIndex)) return false;
        if (Attack>0) TestTrue(TEXT("repeat penalty favors the other equal candidate"),Decision.ChosenIndex!=PreviousChoice);
        S.ConeHoldSlackDegrees=Decision.Traces[Decision.ChosenIndex].ConeHoldSlackDegrees;
        FRPGBossAttackToken Token;
        TestTrue(TEXT("generation-one chosen card starts on selected snapshot"),Model.Start(Decision.ChosenIndex==0?A.Card:B.Card,S,Token,Events,Error));
        Selector.NoteStarted(Decision.ChosenIndex,S.ClockSeconds);
        PreviousChoice=Decision.ChosenIndex;
        TestTrue(TEXT("generation-one card finishes"),Model.Advance(Token,S.ClockSeconds+1.5,false,Events,Error));
        TestTrue(TEXT("finished card returns to idle"),Model.State()==ERPGBossMoveModelState::Idle);
        ++CompletedGenerationOne;
        PreviousGenerationToken=Token;
    }
    TestEqual(TEXT("two cards completed before reset"),CompletedGenerationOne,2);

    // Restart during an active card: the model must close its open window before aborting.
    FRPGBossDecisionSnapshot Interrupted=LoopSnapshot(1,16,105.);
    FRPGBossSelectorDecision BeforeReset;
    Selector.Select(Model,Interrupted,BeforeReset,Context);
    TestTrue(TEXT("a third generation-one card is selected"),BeforeReset.ChosenIndex!=INDEX_NONE);
    const TSharedPtr<const FRPGCompiledBossMoveCard> InterruptedCard=BeforeReset.ChosenIndex==0?A.Card:B.Card;
    FRPGBossAttackToken InterruptedToken;
    TestTrue(TEXT("third card starts"),Model.Start(InterruptedCard,Interrupted,InterruptedToken,Events,Error));
    TestTrue(TEXT("active window opens before reset"),Model.Advance(InterruptedToken,105.6,false,Events,Error));
    TestTrue(TEXT("window is open before reset"),Model.OpenWindowCount()>0);
    TestTrue(TEXT("generation reset succeeds"),Model.ResetGeneration(2,Events,Error));
    TestEqual(TEXT("generation reset clears open hit windows"),Model.OpenWindowCount(),0);
    TestEqual(TEXT("restart closes the open window then aborts"),Events.Num(),2);
    if (Events.Num()==2)
    {
        TestTrue(TEXT("window close precedes abort"),Events[0].Kind==ERPGBossMoveModelEvent::Close);
        TestTrue(TEXT("reset emits abort"),Events[1].Kind==ERPGBossMoveModelEvent::Aborted);
    }
    Selector.Reset();

    // New generation selection, start, stale callback rejection, and a complete two-card loop.
    int32 CompletedGenerationTwo=0;
    FRPGBossAttackToken CurrentToken;
    PreviousChoice=INDEX_NONE;
    for (int32 Attack=0;Attack<2;++Attack)
    {
        FRPGBossDecisionSnapshot S=LoopSnapshot(2,20+Attack*2,107.+Attack*2.);
        FRPGBossSelectorDecision Decision;
        TestTrue(TEXT("generation-two selection runs"),Selector.Select(Model,S,Decision,Context));
        TestTrue(TEXT("generation-two chooses a candidate"),Decision.ChosenIndex!=INDEX_NONE);
        if (!Decision.Traces.IsValidIndex(Decision.ChosenIndex)) return false;
        if (Attack>0) TestTrue(TEXT("repeat history continues to favor the other equal candidate"),Decision.ChosenIndex!=PreviousChoice);
        S.ConeHoldSlackDegrees=Decision.Traces[Decision.ChosenIndex].ConeHoldSlackDegrees;
        const TSharedPtr<const FRPGCompiledBossMoveCard> Card=Decision.ChosenIndex==0?A.Card:B.Card;
        TestTrue(TEXT("generation-two chosen card starts on selected snapshot"),Model.Start(Card,S,CurrentToken,Events,Error));
        Selector.NoteStarted(Decision.ChosenIndex,S.ClockSeconds);
        PreviousChoice=Decision.ChosenIndex;
        if (Attack==0)
        {
            TestTrue(TEXT("instance id remains monotonic across reset"),CurrentToken.InstanceId>InterruptedToken.InstanceId);
            TestFalse(TEXT("old-generation advance is rejected"),Model.Advance(PreviousGenerationToken,999.,false,Events,Error));
            TestTrue(TEXT("stale callback leaves current generation alive"),Model.AcceptsCallback(CurrentToken));
        }
        TestTrue(TEXT("generation-two card finishes"),Model.Advance(CurrentToken,S.ClockSeconds+1.5,false,Events,Error));
        TestTrue(TEXT("generation-two finish returns to idle"),Model.State()==ERPGBossMoveModelState::Idle);
        ++CompletedGenerationTwo;
    }
    TestEqual(TEXT("two cards completed in generation two"),CompletedGenerationTwo,2);
    return true;
}
#endif
