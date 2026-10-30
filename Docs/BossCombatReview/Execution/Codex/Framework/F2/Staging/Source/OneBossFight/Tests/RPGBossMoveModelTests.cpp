// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossMoveModel.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
namespace BossMoveModelFixture
{
// Synthetic, metadata-only scheduling input: not real assets, tuned combat or playback proof.
TSharedPtr<const FRPGCompiledBossMoveCard> Card(bool bZeroStart=false, float Rate=2.f)
{
    FRPGBossMoveCardSpec S; FRPGBossMoveMetadata M;
    S.Schema=1; S.MoveId=TEXT("SyntheticMove"); S.FamilyId=TEXT("SyntheticFamily"); S.PhaseId=TEXT("SyntheticPhase");
    S.Skeleton=TSoftObjectPtr<USkeleton>(FSoftObjectPath(TEXT("/Game/OneBossFight/Data/TypedABIFixtures/F1/Skeleton.Skeleton")));
    S.Sequence=TSoftObjectPtr<UAnimSequence>(FSoftObjectPath(TEXT("/Game/OneBossFight/Data/TypedABIFixtures/F1/Sequence.Sequence")));
    S.SlotName=TEXT("SyntheticSlot"); S.PlayRate=Rate; S.CommitSeconds=.25f; S.ActiveStartSeconds=.5f;
    S.ActiveEndSeconds=1.f; S.RecoveryEndSeconds=1.5f; S.MinRangeCm=20.f; S.MaxRangeCm=400.f; S.FrontConeDegrees=120.f; S.HPDamage=17.f;
    FRPGBossMoveWindow W; W.WindowId=TEXT("A"); W.HitGroup=TEXT("Shared"); W.SocketA=TEXT("Base"); W.SocketB=TEXT("Tip"); W.RadiusCm=8.f;
    W.StartSeconds=.5f; W.EndSeconds=.75f; S.Windows.Add(W);
    W.WindowId=TEXT("B"); W.StartSeconds=.75f; W.EndSeconds=1.f; S.Windows.Add(W);
    if (bZeroStart) { S.CommitSeconds=S.ActiveStartSeconds=S.Windows[0].StartSeconds=0.f; }
    M.AnimationPath=S.Sequence.ToSoftObjectPath(); M.SkeletonPath=S.Skeleton.ToSoftObjectPath();
    M.AnimationSkeletonPath=M.MeshSkeletonPath=M.SkeletonPath; M.ClipLengthSeconds=2.;
    M.Slots.Add(S.SlotName); M.SocketOrBoneNames.Add(W.SocketA); M.SocketOrBoneNames.Add(W.SocketB);
    TSharedPtr<const FRPGCompiledBossMoveCard> Out;
    RPGBossMoveCards::CompileMetadata(S,M,Out); return Out;
}
FRPGBossDecisionSnapshot Snapshot()
{
    FRPGBossDecisionSnapshot S; S.EncounterId=7; S.Generation=1; S.TargetId=9; S.FrameId=10;
    S.PhaseId=TEXT("SyntheticPhase"); S.ClockSeconds=100.; S.RangeCm=100.; S.SignedYawDegrees=-20.; S.bTargetValid=S.bNeutral=true; return S;
}
struct FRun
{
    FRPGBossMoveModel Model; FRPGBossAttackToken Token; TArray<FRPGBossMoveModelEvent> Events; FString Error;
    bool Start() { return Model.Initialize(7,1,Error) && Model.Start(Card(),Snapshot(),Token,Events,Error); }
};
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveModelEligibility,"OneBossFight.Framework.MoveModel.Eligibility",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossMoveModelEligibility::RunTest(const FString&)
{
    using namespace BossMoveModelFixture;
    FRPGBossMoveModel M; FString E; TestTrue(TEXT("initialize"),M.Initialize(7,1,E)); auto C=Card();
    TestTrue(TEXT("single candidate eligible"),M.IsEligible(C,Snapshot(),E));
    auto Reject=[this,&M,&C,&E](TFunction<void(FRPGBossDecisionSnapshot&)> Change,const TCHAR* Token)
    {auto S=Snapshot(); Change(S); TestFalse(Token,M.IsEligible(C,S,E)); TestEqual(TEXT("named refusal"),E,FString(Token));};
    Reject([](auto& S){S.bTargetValid=false;},TEXT("MoveModel.Target"));
    Reject([](auto& S){S.TargetId=0;},TEXT("MoveModel.Target"));
    Reject([](auto& S){S.bNeutral=false;},TEXT("MoveModel.State"));
    Reject([](auto& S){S.Generation=2;},TEXT("MoveModel.Generation"));
    Reject([](auto& S){S.EncounterId=8;},TEXT("MoveModel.Generation"));
    Reject([](auto& S){S.PhaseId=TEXT("Other");},TEXT("MoveModel.Phase"));
    Reject([](auto& S){S.RangeCm=19.;},TEXT("MoveModel.Range"));
    Reject([](auto& S){S.RangeCm=401.;},TEXT("MoveModel.Range"));
    Reject([](auto& S){S.SignedYawDegrees=60.01;},TEXT("MoveModel.Cone"));
    Reject([](auto& S){S.SignedYawDegrees=-60.01;},TEXT("MoveModel.Cone"));
    Reject([](auto& S){S.ClockSeconds=std::numeric_limits<double>::quiet_NaN();},TEXT("MoveModel.SnapshotDomain"));
    Reject([](auto& S){S.RangeCm=std::numeric_limits<double>::infinity();},TEXT("MoveModel.SnapshotDomain"));
    Reject([](auto& S){S.SignedYawDegrees=-181.;},TEXT("MoveModel.SnapshotDomain"));
    auto S=Snapshot(); S.RangeCm=20.; S.SignedYawDegrees=-60.; TestTrue(TEXT("inclusive lower range/left cone"),M.IsEligible(C,S,E));
    S.RangeCm=400.; S.SignedYawDegrees=60.; TestTrue(TEXT("inclusive upper range/right cone"),M.IsEligible(C,S,E));
    TestFalse(TEXT("missing candidate"),M.IsEligible({},S,E));
    TestFalse(TEXT("no implicit reinitialize"),M.Initialize(8,2,E)); return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveModelCrossing,"OneBossFight.Framework.MoveModel.Crossing",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossMoveModelCrossing::RunTest(const FString&)
{
    using namespace BossMoveModelFixture;
    FRun R; if (!TestTrue(TEXT("start"),R.Start())) return false;
    TestTrue(TEXT("initial Committed state"),R.Model.State()==ERPGBossMoveModelState::Committed);
    TestFalse(TEXT("heading can track before authored commit"),R.Model.HeadingCommitted());
    TestTrue(TEXT("long frame crossing whole move"),R.Model.Advance(R.Token,101.,false,R.Events,R.Error));
    TestTrue(TEXT("finished Idle"),R.Model.State()==ERPGBossMoveModelState::Idle);
    TestEqual(TEXT("both edges of both windows plus recovery/finish"),R.Events.Num(),6);
    if (R.Events.Num()==6)
    {
        const ERPGBossMoveModelEvent K[]={ERPGBossMoveModelEvent::Open,ERPGBossMoveModelEvent::Close,ERPGBossMoveModelEvent::Open,ERPGBossMoveModelEvent::Close,ERPGBossMoveModelEvent::Recovery,ERPGBossMoveModelEvent::Finished};
        const double T[]={.5,.75,.75,1.,1.,1.5};
        for (int32 I=0;I<6;++I) {TestTrue(TEXT("chronological edge kind"),R.Events[I].Kind==K[I]); TestEqual(TEXT("exact authored local timestamp"),R.Events[I].LocalSeconds,T[I]); TestTrue(TEXT("token on each edge"),R.Events[I].Token==R.Token);}
    }
    TestFalse(TEXT("finished callback rejected"),R.Model.AcceptsCallback(R.Token));
    for (float Rate : {.5f,1.f,3.f})
    {
        FRun V; V.Model.Initialize(7,1,V.Error);
        TestTrue(TEXT("authored variable play rate starts"),V.Model.Start(Card(false,Rate),Snapshot(),V.Token,V.Events,V.Error));
        int32 EdgeCount=V.Events.Num();
        V.Model.Advance(V.Token,100.+.3/Rate,false,V.Events,V.Error); EdgeCount+=V.Events.Num();
        V.Model.Advance(V.Token,100.+.9/Rate,false,V.Events,V.Error); EdgeCount+=V.Events.Num();
        V.Model.Advance(V.Token,100.+2./Rate,false,V.Events,V.Error); EdgeCount+=V.Events.Num();
        TestTrue(TEXT("variable dt and rate finish Idle"),V.Model.State()==ERPGBossMoveModelState::Idle);
        TestEqual(TEXT("no edges lost or duplicated across step sizes/rates"),EdgeCount,6);
    }

    FRun Z; TestTrue(TEXT("zero active-start initialization"),Z.Model.Initialize(7,1,Z.Error));
    TestTrue(TEXT("zero-time window start"),Z.Model.Start(Card(true),Snapshot(),Z.Token,Z.Events,Z.Error));
    TestEqual(TEXT("start emits exactly one zero-time open"),Z.Events.Num(),1);
    TestTrue(TEXT("zero-start Active"),Z.Model.State()==ERPGBossMoveModelState::Active);
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveModelPause,"OneBossFight.Framework.MoveModel.PauseAndBoundaries",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossMoveModelPause::RunTest(const FString&)
{
    using namespace BossMoveModelFixture;
    FRun R; if (!TestTrue(TEXT("start"),R.Start())) return false;
    R.Model.Advance(R.Token,100.125,false,R.Events,R.Error);
    TestTrue(TEXT("heading commits at .25 local seconds at2xrate"),R.Model.HeadingCommitted());
    TestTrue(TEXT("still Committed before active"),R.Model.State()==ERPGBossMoveModelState::Committed);
    R.Model.Advance(R.Token,100.25,false,R.Events,R.Error);
    TestTrue(TEXT("Active boundary"),R.Model.State()==ERPGBossMoveModelState::Active); TestEqual(TEXT("open once"),R.Events.Num(),1);
    R.Model.Advance(R.Token,101.,true,R.Events,R.Error); TestEqual(TEXT("pause keeps local time"),R.Model.LocalSeconds(),.5); TestEqual(TEXT("pause no edges"),R.Events.Num(),0);
    R.Model.Advance(R.Token,101.125,false,R.Events,R.Error); TestEqual(TEXT("resume excludes paused wall time"),R.Model.LocalSeconds(),.75); TestEqual(TEXT("touching windows close then open"),R.Events.Num(),2);
    R.Model.Advance(R.Token,101.125,false,R.Events,R.Error); TestEqual(TEXT("same-clock tick no duplicate edges"),R.Events.Num(),0);
    R.Model.Advance(R.Token,101.25,false,R.Events,R.Error); TestTrue(TEXT("Recovery exact boundary"),R.Model.State()==ERPGBossMoveModelState::Recovery);
    R.Model.Advance(R.Token,101.5,false,R.Events,R.Error); TestTrue(TEXT("Idle exact end"),R.Model.State()==ERPGBossMoveModelState::Idle);
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveModelAbort,"OneBossFight.Framework.MoveModel.Abort",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossMoveModelAbort::RunTest(const FString&)
{
    using namespace BossMoveModelFixture;
    const double Times[]={100.,100.25,100.5,101.}; // Committed, Active, Recovery, already Idle.
    for (double T:Times)
    {
        FRun R; if (!R.Start()) {AddError(TEXT("fixture failed")); return false;}
        if (T>100.) R.Model.Advance(R.Token,T,false,R.Events,R.Error);
        const bool bActive=R.Model.State()==ERPGBossMoveModelState::Active;
        TestTrue(TEXT("abort accepts current or finished token"),R.Model.Abort(R.Token,R.Events,R.Error));
        TestTrue(TEXT("abort Idle"),R.Model.State()==ERPGBossMoveModelState::Idle);
        if (bActive) {TestEqual(TEXT("active abort closes window then signals abort"),R.Events.Num(),2); if(R.Events.Num()==2) TestTrue(TEXT("close before abort"),R.Events[0].Kind==ERPGBossMoveModelEvent::Close && R.Events[1].Kind==ERPGBossMoveModelEvent::Aborted);}
        TestTrue(TEXT("repeated abort idempotent"),R.Model.Abort(R.Token,R.Events,R.Error)); TestEqual(TEXT("repeat emits nothing"),R.Events.Num(),0);
    }
    FRun R; R.Start(); R.Model.Advance(R.Token,100.25,false,R.Events,R.Error);
    TestFalse(TEXT("clock reversal fails closed"),R.Model.Advance(R.Token,99.,false,R.Events,R.Error)); TestTrue(TEXT("invalid clock aborts owned attack"),R.Model.State()==ERPGBossMoveModelState::Idle);
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveModelGeneration,"OneBossFight.Framework.MoveModel.GenerationAndDoubleStart",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossMoveModelGeneration::RunTest(const FString&)
{
    using namespace BossMoveModelFixture;
    FRun R; if(!R.Start()) return false; const auto Old=R.Token; FRPGBossAttackToken Refused;
    TestFalse(TEXT("second start while busy"),R.Model.Start(Card(),Snapshot(),Refused,R.Events,R.Error)); TestEqual(TEXT("failure clears output token"),Refused.InstanceId,uint64(0));
    R.Model.Abort(Old,R.Events,R.Error);
    TestFalse(TEXT("same-frame restart after abort"),R.Model.Start(Card(),Snapshot(),Refused,R.Events,R.Error));
    auto S=Snapshot(); ++S.FrameId; S.ClockSeconds+=.25;
    TestTrue(TEXT("next decision starts"),R.Model.Start(Card(),S,R.Token,R.Events,R.Error)); TestTrue(TEXT("strictly increasing instance"),R.Token.InstanceId>Old.InstanceId);
    const auto Current=R.Token;
    TestFalse(TEXT("old callback cannot abort new attack"),R.Model.Abort(Old,R.Events,R.Error)); TestTrue(TEXT("new attack survives stale abort"),R.Model.AcceptsCallback(Current));
    TestTrue(TEXT("generation reset aborts"),R.Model.ResetGeneration(2,R.Events,R.Error)); TestFalse(TEXT("old generation rejected"),R.Model.AcceptsCallback(Current));
    S.Generation=2; ++S.FrameId;
    TestTrue(TEXT("new generation explicit start"),R.Model.Start(Card(),S,R.Token,R.Events,R.Error)); TestTrue(TEXT("counter not reset by generation"),R.Token.InstanceId>Current.InstanceId);
    TestFalse(TEXT("delayed old tick rejected"),R.Model.Advance(Current,999.,false,R.Events,R.Error)); TestEqual(TEXT("stale tick emits nothing"),R.Events.Num(),0); TestTrue(TEXT("new token still live"),R.Model.AcceptsCallback(R.Token));
    TestFalse(TEXT("generation cannot rewind"),R.Model.ResetGeneration(1,R.Events,R.Error));
    return true;
}
#endif
