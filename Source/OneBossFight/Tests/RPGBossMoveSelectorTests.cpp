// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossMoveSelector.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
namespace BossMoveSelectorFixture
{
// Synthetic, metadata-only cards: scheduling inputs, not real assets, tuned combat or playback proof.
TSharedPtr<const FRPGCompiledBossMoveCard> Card(const TCHAR* Id, float MinRange, float MaxRange)
{
    FRPGBossMoveCardSpec S; FRPGBossMoveMetadata M;
    S.Schema=1; S.MoveId=Id; S.FamilyId=TEXT("SyntheticFamily"); S.PhaseId=TEXT("SyntheticPhase");
    S.Skeleton=TSoftObjectPtr<USkeleton>(FSoftObjectPath(TEXT("/Game/OneBossFight/Data/TypedABIFixtures/F1/Skeleton.Skeleton")));
    S.Sequence=TSoftObjectPtr<UAnimSequence>(FSoftObjectPath(TEXT("/Game/OneBossFight/Data/TypedABIFixtures/F1/Sequence.Sequence")));
    S.SlotName=TEXT("SyntheticSlot"); S.PlayRate=1.f; S.CommitSeconds=.25f; S.ActiveStartSeconds=.5f;
    S.ActiveEndSeconds=1.f; S.RecoveryEndSeconds=1.5f; S.MinRangeCm=MinRange; S.MaxRangeCm=MaxRange; S.FrontConeDegrees=120.f; S.HPDamage=17.f;
    FRPGBossMoveWindow W; W.WindowId=TEXT("A"); W.HitGroup=TEXT("Shared"); W.SocketA=TEXT("Base"); W.SocketB=TEXT("Tip"); W.RadiusCm=8.f;
    W.StartSeconds=.5f; W.EndSeconds=1.f; S.Windows.Add(W);
    M.AnimationPath=S.Sequence.ToSoftObjectPath(); M.SkeletonPath=S.Skeleton.ToSoftObjectPath();
    M.AnimationSkeletonPath=M.MeshSkeletonPath=M.SkeletonPath; M.ClipLengthSeconds=2.;
    M.Slots.Add(S.SlotName); M.SocketOrBoneNames.Add(W.SocketA); M.SocketOrBoneNames.Add(W.SocketB);
    TSharedPtr<const FRPGCompiledBossMoveCard> Out;
    RPGBossMoveCards::CompileMetadata(S,M,Out); return Out;
}
FRPGBossDecisionSnapshot Snapshot(double Range=100., double Clock=100.)
{
    FRPGBossDecisionSnapshot S; S.EncounterId=7; S.Generation=1; S.TargetId=9; S.FrameId=10;
    S.PhaseId=TEXT("SyntheticPhase"); S.ClockSeconds=Clock; S.RangeCm=Range; S.SignedYawDegrees=0.; S.bTargetValid=S.bNeutral=true; return S;
}
FRPGBossSelectorConfig Config() { FRPGBossSelectorConfig C; C.RepeatPenalty=.2f; C.RepeatMemory=2; return C; }
FRPGBossSelectorCandidate Cand(const TCHAR* Id, float Min, float Max, float Cooldown=0.f, float Weight=1.f)
{ FRPGBossSelectorCandidate C; C.Card=Card(Id,Min,Max); C.CooldownSeconds=Cooldown; C.Weight=Weight; return C; }
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveSelectorInit,"OneBossFight.Framework.Selector.Init",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossMoveSelectorInit::RunTest(const FString&)
{
    using namespace BossMoveSelectorFixture;
    auto Reject=[this](const FRPGBossSelectorConfig& C,TArray<FRPGBossSelectorCandidate> L,const TCHAR* Token)
    {FRPGBossMoveSelector S;FString E;TestFalse(Token,S.Initialize(C,L,E));TestEqual(TEXT("named refusal"),E,FString(Token));};
    FRPGBossSelectorConfig Zero;Reject(Zero,{Cand(TEXT("A"),50,150)},TEXT("Selector.Config"));
    auto Bad=Config();Bad.RepeatMemory=9;Reject(Bad,{Cand(TEXT("A"),50,150)},TEXT("Selector.Config"));
    Bad=Config();Bad.RepeatPenalty=1.5f;Reject(Bad,{Cand(TEXT("A"),50,150)},TEXT("Selector.Config"));
    Reject(Config(),{},TEXT("Selector.NoCandidates"));
    FRPGBossSelectorCandidate Null;Reject(Config(),{Null},TEXT("Selector.NullCard"));
    Reject(Config(),{Cand(TEXT("A"),50,150,-1.f)},TEXT("Selector.Domain"));
    Reject(Config(),{Cand(TEXT("A"),50,150,0.f,0.f)},TEXT("Selector.Domain"));
    Reject(Config(),{Cand(TEXT("A"),50,150),Cand(TEXT("A"),60,160)},TEXT("Selector.DuplicateMoveId"));
    FRPGBossMoveSelector Ok;FString E;TestTrue(TEXT("valid"),Ok.Initialize(Config(),{Cand(TEXT("A"),50,150)},E));
    TestFalse(TEXT("second initialize refused"),Ok.Initialize(Config(),{Cand(TEXT("B"),50,150)},E));
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveSelectorPolicy,"OneBossFight.Framework.Selector.Policy",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossMoveSelectorPolicy::RunTest(const FString&)
{
    using namespace BossMoveSelectorFixture;
    FRPGBossMoveModel Model;FString E;if(!Model.Initialize(7,1,E))return false;
    // Hard filters first: the out-of-range card is refused by the model's named token and cannot win however high its weight is.
    {
        FRPGBossMoveSelector S;S.Initialize(Config(),{Cand(TEXT("Far"),300,500,0.f,100.f),Cand(TEXT("Near"),50,150)},E);
        FRPGBossSelectorDecision D;TestTrue(TEXT("select runs"),S.Select(Model,Snapshot(100.),D));
        TestEqual(TEXT("eligible card wins over a heavier refused one"),D.MoveId,FName(TEXT("Near")));
        TestEqual(TEXT("refusal token traced"),D.Traces[0].Refusal,FString(TEXT("MoveModel.Range")));TestFalse(TEXT("refused is not scored"),D.Traces[0].bEligible);
    }
    // Determinism and tie rule: identical candidates -> lowest index, every time.
    {
        FRPGBossMoveSelector S;S.Initialize(Config(),{Cand(TEXT("A"),50,150),Cand(TEXT("B"),50,150)},E);
        for(int32 I=0;I<5;++I){FRPGBossSelectorDecision D;S.Select(Model,Snapshot(),D);TestEqual(TEXT("tie goes to the lowest index"),D.ChosenIndex,0);}
    }
    // Range preference: the card whose range is centred on the distance scores higher.
    {
        FRPGBossMoveSelector S;S.Initialize(Config(),{Cand(TEXT("Wide"),20,400),Cand(TEXT("Centred"),80,120)},E);
        FRPGBossSelectorDecision D;S.Select(Model,Snapshot(100.),D);
        TestEqual(TEXT("centred range preferred"),D.MoveId,FName(TEXT("Centred")));TestTrue(TEXT("scores ordered"),D.Traces[1].Score>D.Traces[0].Score);
    }
    // Cooldown is a hard filter until exactly CooldownSeconds have passed.
    {
        FRPGBossMoveSelector S;S.Initialize(Config(),{Cand(TEXT("A"),50,150,2.f)},E);S.NoteStarted(0,100.);
        FRPGBossSelectorDecision D;S.Select(Model,Snapshot(100.,101.5),D);
        TestEqual(TEXT("cooling card refused"),D.Traces[0].Refusal,FString(TEXT("Selector.Cooldown")));TestEqual(TEXT("nothing chosen is not an error"),D.ChosenIndex,(int32)INDEX_NONE);
        S.Select(Model,Snapshot(100.,102.),D);TestEqual(TEXT("eligible again at the cooldown edge"),D.ChosenIndex,0);
        S.NoteStarted(0,200.);S.Reset();S.Select(Model,Snapshot(100.,50.),D);TestEqual(TEXT("reset forgets cooldown and history (new encounter clock below the old start)"),D.ChosenIndex,0);
    }
    // Anti-repeat: the card that just started is scaled down, so an equal alternative is chosen; memory is bounded.
    {
        FRPGBossMoveSelector S;S.Initialize(Config(),{Cand(TEXT("A"),50,150),Cand(TEXT("B"),50,150),Cand(TEXT("C"),50,150)},E);
        FRPGBossSelectorDecision D;S.Select(Model,Snapshot(),D);TestEqual(TEXT("first pick"),D.ChosenIndex,0);S.NoteStarted(0,100.);
        S.Select(Model,Snapshot(),D);TestEqual(TEXT("repeat avoided"),D.ChosenIndex,1);S.NoteStarted(1,101.);
        S.Select(Model,Snapshot(),D);TestEqual(TEXT("both recent cards avoided"),D.ChosenIndex,2);S.NoteStarted(2,102.);
        S.Select(Model,Snapshot(),D);TestEqual(TEXT("memory of 2 forgets the oldest"),D.ChosenIndex,0);
    }
    // No candidate: a valid answer, every trace carries its refusal.
    {
        FRPGBossMoveSelector S;S.Initialize(Config(),{Cand(TEXT("A"),300,500),Cand(TEXT("B"),600,800)},E);
        FRPGBossSelectorDecision D;TestTrue(TEXT("select runs"),S.Select(Model,Snapshot(100.),D));
        TestEqual(TEXT("no choice"),D.ChosenIndex,(int32)INDEX_NONE);TestEqual(TEXT("both traced"),D.Traces.Num(),2);
        TestTrue(TEXT("every refusal named"),!D.Traces[0].Refusal.IsEmpty()&&!D.Traces[1].Refusal.IsEmpty());
    }
    return true;
}
#endif
