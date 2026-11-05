// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossMoveModel.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
namespace BossMoveModelFixture
{
// Synthetic, metadata-only scheduling input: not real assets, tuned combat or playback proof.
TSharedPtr<const FRPGCompiledBossMoveCard> Card(bool bZeroStart=false, float Rate=2.f, float MaxVertical=0.f, float MinRange=20.f, float MaxRange=400.f)
{
    FRPGBossMoveCardSpec S; FRPGBossMoveMetadata M; S.MaxVerticalDeltaCm=MaxVertical;
    S.Schema=1; S.MoveId=TEXT("SyntheticMove"); S.FamilyId=TEXT("SyntheticFamily"); S.PhaseId=TEXT("SyntheticPhase");
    S.Skeleton=TSoftObjectPtr<USkeleton>(FSoftObjectPath(TEXT("/Game/OneBossFight/Data/TypedABIFixtures/F1/Skeleton.Skeleton")));
    S.Sequence=TSoftObjectPtr<UAnimSequence>(FSoftObjectPath(TEXT("/Game/OneBossFight/Data/TypedABIFixtures/F1/Sequence.Sequence")));
    S.SlotName=TEXT("SyntheticSlot"); S.PlayRate=Rate; S.CommitSeconds=.25f; S.ActiveStartSeconds=.5f;
    S.ActiveEndSeconds=1.f; S.RecoveryEndSeconds=1.5f; S.MinRangeCm=MinRange; S.MaxRangeCm=MaxRange; S.FrontConeDegrees=120.f; S.HPDamage=17.f;
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
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveModelRefusalPrecedence,"OneBossFight.Framework.MoveModel.RefusalPrecedence",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossMoveModelRefusalPrecedence::RunTest(const FString&)
{
    using namespace BossMoveModelFixture;FRPGBossMoveModel M;FString Error;TestTrue(TEXT("initialize"),M.Initialize(7,1,Error));
    auto S=Snapshot();S.Generation=2;TestFalse(TEXT("generation beats missing card"),M.IsEligible({},S,Error));TestEqual(TEXT("generation token wins"),Error,FString(TEXT("MoveModel.Generation")));
    S=Snapshot();S.bTargetValid=false;S.bNeutral=false;TestFalse(TEXT("target beats non-neutral state"),M.IsEligible(Card(),S,Error));TestEqual(TEXT("target token wins"),Error,FString(TEXT("MoveModel.Target")));
    S=Snapshot();S.bNeutral=false;S.ClockSeconds=std::numeric_limits<double>::quiet_NaN();TestFalse(TEXT("state beats invalid snapshot clock"),M.IsEligible(Card(),S,Error));TestEqual(TEXT("state token wins"),Error,FString(TEXT("MoveModel.State")));
    S=Snapshot();S.PhaseId=TEXT("Other");S.ClockSeconds=std::numeric_limits<double>::quiet_NaN();TestFalse(TEXT("snapshot domain beats phase"),M.IsEligible(Card(),S,Error));TestEqual(TEXT("snapshot token wins"),Error,FString(TEXT("MoveModel.SnapshotDomain")));
    S=Snapshot();S.PhaseId=TEXT("Other");S.RangeCm=19.;TestFalse(TEXT("phase beats range"),M.IsEligible(Card(),S,Error));TestEqual(TEXT("phase token wins"),Error,FString(TEXT("MoveModel.Phase")));
    S=Snapshot();S.RangeCm=19.;S.SignedYawDegrees=61.;TestFalse(TEXT("range beats cone"),M.IsEligible(Card(),S,Error));TestEqual(TEXT("range token wins"),Error,FString(TEXT("MoveModel.Range")));
    S=Snapshot();S.SignedYawDegrees=61.;S.VerticalDeltaCm=20.;TestFalse(TEXT("cone beats vertical separation"),M.IsEligible(Card(false,2.f,10.f),S,Error));TestEqual(TEXT("cone token wins"),Error,FString(TEXT("MoveModel.Cone")));
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveModelRangeBandPartition,"OneBossFight.Framework.MoveModel.RangeBandPartition",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossMoveModelRangeBandPartition::RunTest(const FString&)
{
    using namespace BossMoveModelFixture;
    FRPGBossMoveModel Model;FString Error;TestTrue(TEXT("initialize"),Model.Initialize(7,1,Error));
    // Profile band 250..350 cm is a walk target under MOV-001. Candidate eligibility remains each card's authored range.
    const TSharedPtr<const FRPGCompiledBossMoveCard> Cards[]={Card(false,2.f,0.f,0.f,150.f),Card(false,2.f,0.f,90.f,350.f),Card(false,2.f,0.f,240.f,500.f),Card(false,2.f,0.f,690.f,900.f)};
    const double Distances[]={100.,250.,375.,700.};
    const bool Expected[4][4]={{true,true,false,false},{false,true,true,false},{false,false,true,false},{false,false,false,true}};
    for(int32 D=0;D<4;++D)
    {
        FRPGBossDecisionSnapshot S=Snapshot();S.RangeCm=Distances[D];S.FrameId+=D;
        for(int32 C=0;C<4;++C)
            TestEqual(*FString::Printf(TEXT("distance %.0f card %d uses card range"),Distances[D],C),Model.IsEligible(Cards[C],S,Error),Expected[D][C]);
    }
    return true;
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
    TestEqual(TEXT("finish leaves no open windows"),R.Model.OpenWindowCount(),0);
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
        TestEqual(TEXT("abort leaves no open windows"),R.Model.OpenWindowCount(),0);
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
    TestTrue(TEXT("window opens before reset"),R.Model.Advance(Current,100.5,false,R.Events,R.Error));TestEqual(TEXT("one active window before reset"),R.Model.OpenWindowCount(),1);
    TestTrue(TEXT("generation reset aborts"),R.Model.ResetGeneration(2,R.Events,R.Error)); TestEqual(TEXT("generation reset leaves no open windows"),R.Model.OpenWindowCount(),0);TestFalse(TEXT("old generation rejected"),R.Model.AcceptsCallback(Current));
    S.Generation=2;S.ClockSeconds=100.75;++S.FrameId;
    TestTrue(TEXT("new generation explicit start"),R.Model.Start(Card(),S,R.Token,R.Events,R.Error)); TestTrue(TEXT("counter not reset by generation"),R.Token.InstanceId>Current.InstanceId);
    TestFalse(TEXT("delayed old tick rejected"),R.Model.Advance(Current,999.,false,R.Events,R.Error)); TestEqual(TEXT("stale tick emits nothing"),R.Events.Num(),0); TestTrue(TEXT("new token still live"),R.Model.AcceptsCallback(R.Token));
    TestFalse(TEXT("generation cannot rewind"),R.Model.ResetGeneration(1,R.Events,R.Error));
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveModelObserved,"OneBossFight.Framework.MoveModel.ObservedClock",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossMoveModelObserved::RunTest(const FString&)
{
    using namespace BossMoveModelFixture;FRun R;if(!R.Start())return false;
    TestTrue(TEXT("observation mode explicit"),R.Model.AdvanceObservedLocal(R.Token,0.,R.Events,R.Error));
    TestTrue(TEXT("actual animation .5 not wall x rate"),R.Model.AdvanceObservedLocal(R.Token,.5,R.Events,R.Error));
    TestEqual(TEXT("observed position exact"),R.Model.LocalSeconds(),.5);TestEqual(TEXT("open at observed boundary"),R.Events.Num(),1);
    R.Model.AdvanceObservedLocal(R.Token,.5,R.Events,R.Error);TestEqual(TEXT("stalled pose emits nothing"),R.Events.Num(),0);
    R.Model.AdvanceObservedLocal(R.Token,2.,R.Events,R.Error);TestEqual(TEXT("long observed step crosses remaining five edges"),R.Events.Num(),5);
    TestTrue(TEXT("finished Idle"),R.Model.State()==ERPGBossMoveModelState::Idle);
    FRun Invalid;Invalid.Start();Invalid.Model.AdvanceObservedLocal(Invalid.Token,.5,Invalid.Events,Invalid.Error);
    TestFalse(TEXT("observed rewind aborts"),Invalid.Model.AdvanceObservedLocal(Invalid.Token,.4,Invalid.Events,Invalid.Error));
    TestTrue(TEXT("rewind fails closed"),Invalid.Model.State()==ERPGBossMoveModelState::Idle);
    FRun NaN;NaN.Start();TestFalse(TEXT("nonfinite observation aborts"),NaN.Model.AdvanceObservedLocal(NaN.Token,std::numeric_limits<double>::quiet_NaN(),NaN.Events,NaN.Error));
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveModelClockMode,"OneBossFight.Framework.MoveModel.ClockMode",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossMoveModelClockMode::RunTest(const FString&)
{
    using namespace BossMoveModelFixture;
    for(bool ObservedFirst:{false,true})
    {
        FRun R;if(!R.Start())return false;
        if(ObservedFirst)R.Model.AdvanceObservedLocal(R.Token,.5,R.Events,R.Error);
        else R.Model.Advance(R.Token,100.25,false,R.Events,R.Error);
        const bool Result=ObservedFirst?R.Model.Advance(R.Token,100.5,false,R.Events,R.Error):R.Model.AdvanceObservedLocal(R.Token,.75,R.Events,R.Error);
        TestFalse(TEXT("mixed clock rejected"),Result);TestEqual(TEXT("named mode refusal"),R.Error,FString(TEXT("MoveModel.ClockMode")));
        TestTrue(TEXT("mixed clock aborts"),R.Model.State()==ERPGBossMoveModelState::Idle);
        auto S=Snapshot();++S.FrameId;S.ClockSeconds=101.;
        TestTrue(TEXT("new attack can choose a different mode"),R.Model.Start(Card(),S,R.Token,R.Events,R.Error));
        TestTrue(TEXT("new attack observation"),R.Model.AdvanceObservedLocal(R.Token,.5,R.Events,R.Error));
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveModelStaleObservedAfterRestart,
    "OneBossFight.Framework.MoveModel.StaleObservedAfterRestart",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossMoveModelStaleObservedAfterRestart::RunTest(const FString&)
{
    using namespace BossMoveModelFixture;
    FRun R; if(!R.Start()) return false;
    const FRPGBossAttackToken Old=R.Token;
    TestTrue(TEXT("old attack accepts an observed-local tick"),R.Model.AdvanceObservedLocal(Old,.5,R.Events,R.Error));
    TestTrue(TEXT("generation reset succeeds"),R.Model.ResetGeneration(2,R.Events,R.Error));
    auto S=Snapshot(); S.Generation=2; ++S.FrameId; S.ClockSeconds=101.;
    TestTrue(TEXT("new-generation attack starts"),R.Model.Start(Card(),S,R.Token,R.Events,R.Error));
    R.Events.Reset();
    TestFalse(TEXT("old observed-local callback is rejected after restart"),R.Model.AdvanceObservedLocal(Old,.75,R.Events,R.Error));
    TestEqual(TEXT("stale observed-local callback has named refusal"),R.Error,FString(TEXT("MoveModel.StaleCallback")));
    TestEqual(TEXT("stale observed-local callback emits no events"),R.Events.Num(),0);
    TestTrue(TEXT("new-generation attack remains active"),R.Model.AcceptsCallback(R.Token));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveModelStaleAbortAfterRestart,
    "OneBossFight.Framework.MoveModel.StaleAbortAfterRestart",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossMoveModelStaleAbortAfterRestart::RunTest(const FString&)
{
    using namespace BossMoveModelFixture;
    FRun R; if(!R.Start()) return false;
    const FRPGBossAttackToken Old=R.Token;
    TestTrue(TEXT("generation reset succeeds"),R.Model.ResetGeneration(2,R.Events,R.Error));
    auto S=Snapshot(); S.Generation=2; ++S.FrameId; S.ClockSeconds=101.;
    TestTrue(TEXT("new-generation attack starts"),R.Model.Start(Card(),S,R.Token,R.Events,R.Error));
    R.Events.Reset();
    TestFalse(TEXT("old-generation abort is rejected after a newer attack starts"),R.Model.Abort(Old,R.Events,R.Error));
    TestEqual(TEXT("stale abort has named refusal"),R.Error,FString(TEXT("MoveModel.StaleCallback")));
    TestEqual(TEXT("stale abort emits no events"),R.Events.Num(),0);
    TestTrue(TEXT("new-generation token remains accepted"),R.Model.AcceptsCallback(R.Token));
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveModelReserveBeforePlayback,"OneBossFight.Framework.MoveModel.ReserveBeforePlayback",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossMoveModelReserveBeforePlayback::RunTest(const FString&)
{
    // BOSS-EXE-002: the executor calls Start (reserve) before it plays the montage and Abort when the play fails.
    using namespace BossMoveModelFixture;FRun R;if(!R.Start())return false;
    TestTrue(TEXT("instance exists before any playback"),R.Token.InstanceId!=0&&R.Model.AcceptsCallback(R.Token));
    TestTrue(TEXT("reserved attack is Committed"),R.Model.State()==ERPGBossMoveModelState::Committed);
    TestTrue(TEXT("failed playback aborts the reserved instance"),R.Model.Abort(R.Token,R.Events,R.Error));
    TestTrue(TEXT("model Idle after failed playback"),R.Model.State()==ERPGBossMoveModelState::Idle);
    TestEqual(TEXT("exactly one event"),R.Events.Num(),1);if(R.Events.Num()==1)TestTrue(TEXT("Aborted event"),R.Events[0].Kind==ERPGBossMoveModelEvent::Aborted&&R.Events[0].Token==R.Token);
    TestFalse(TEXT("aborted instance no longer accepts callbacks"),R.Model.AcceptsCallback(R.Token));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveModelVerticalSeparation,"OneBossFight.Framework.MoveModel.VerticalSeparation",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossMoveModelVerticalSeparation::RunTest(const FString&)
{
    // BOSS-AWR-005: elevation separation above the card's limit invalidates the (floor plane) card; equal is in; 0 = no limit.
    using namespace BossMoveModelFixture;
    FRPGBossMoveModel M; FString E; TestTrue(TEXT("initialize"),M.Initialize(7,1,E));
    auto Limited=Card(false,2.f,50.f), Unlimited=Card();
    auto WithZ=[](double Z){auto S=Snapshot();S.VerticalDeltaCm=Z;return S;};
    TestTrue(TEXT("same floor is eligible"),M.IsEligible(Limited,WithZ(0.),E));
    TestTrue(TEXT("exactly at the limit is eligible"),M.IsEligible(Limited,WithZ(50.),E));
    TestFalse(TEXT("just above the limit is refused"),M.IsEligible(Limited,WithZ(50.01),E));TestEqual(TEXT("named refusal"),E,FString(TEXT("MoveModel.Vertical")));
    TestFalse(TEXT("a target far above is refused"),M.IsEligible(Limited,WithZ(400.),E));TestEqual(TEXT("named refusal"),E,FString(TEXT("MoveModel.Vertical")));
    TestTrue(TEXT("a card with no limit ignores any vertical separation"),M.IsEligible(Unlimited,WithZ(400.),E));
    TestFalse(TEXT("negative separation is a bad snapshot"),M.IsEligible(Limited,WithZ(-1.),E));TestEqual(TEXT("named refusal"),E,FString(TEXT("MoveModel.SnapshotDomain")));
    TestFalse(TEXT("NaN separation is a bad snapshot"),M.IsEligible(Limited,WithZ(std::numeric_limits<double>::quiet_NaN()),E));TestEqual(TEXT("named refusal"),E,FString(TEXT("MoveModel.SnapshotDomain")));
    TestFalse(TEXT("infinite separation is a bad snapshot"),M.IsEligible(Unlimited,WithZ(std::numeric_limits<double>::infinity()),E));TestEqual(TEXT("named refusal"),E,FString(TEXT("MoveModel.SnapshotDomain")));
    // The card itself: a negative or NaN limit is refused by the card validator.
    for(float Bad:{-1.f,std::numeric_limits<float>::quiet_NaN(),std::numeric_limits<float>::infinity()}){auto C=Card(false,2.f,Bad);TestFalse(TEXT("card with a bad vertical limit does not compile"),C.IsValid());}
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveModelEventStorm,"OneBossFight.Framework.MoveModel.EventStorm",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossMoveModelEventStorm::RunTest(const FString&)
{
    using namespace BossMoveModelFixture;
    FRandomStream Random(0x87A11);int32 Starts=0,Finishes=0,Aborts=0;
    for(int32 Run=0;Run<1000;++Run)
    {
        FRun R;if(!R.Start())return false;++Starts;
        double Clock=100.;
        for(int32 Event=0;Event<8&&R.Model.State()!=ERPGBossMoveModelState::Idle;++Event)
        {
            if(Random.FRand()<.22f)
            {
                R.Events.Reset();
                if(R.Model.Abort(R.Token,R.Events,R.Error)){++Aborts;{int32 AbortedEvents=0;for(const FRPGBossMoveModelEvent& E:R.Events)AbortedEvents+=E.Kind==ERPGBossMoveModelEvent::Aborted?1:0;TestTrue(TEXT("abort emits exactly one terminal Aborted event, last (window-close events may come before it)"),AbortedEvents==1&&R.Events.Num()>=1&&R.Events.Last().Kind==ERPGBossMoveModelEvent::Aborted);}}
                break;
            }
            Clock+=Random.FRandRange(.01f,.4f);R.Events.Reset();
            TestTrue(TEXT("monotonic random clock advances without illegal transition"),R.Model.Advance(R.Token,Clock,false,R.Events,R.Error));
            TestTrue(TEXT("state stays in declared state machine"),R.Model.State()==ERPGBossMoveModelState::Committed||R.Model.State()==ERPGBossMoveModelState::Active||R.Model.State()==ERPGBossMoveModelState::Recovery||R.Model.State()==ERPGBossMoveModelState::Idle);
            if(R.Model.State()==ERPGBossMoveModelState::Idle){++Finishes;TestFalse(TEXT("terminal token rejects delayed callback"),R.Model.AcceptsCallback(R.Token));}
        }
        if(R.Model.State()!=ERPGBossMoveModelState::Idle){R.Events.Reset();TestTrue(TEXT("storm cleanup aborts live instance"),R.Model.Abort(R.Token,R.Events,R.Error));++Aborts;}
        TestTrue(TEXT("every run ends idle"),R.Model.State()==ERPGBossMoveModelState::Idle);
    }
    TestEqual(TEXT("one instance per run"),Starts,1000);TestTrue(TEXT("randomized stream covers completions and aborts"),Finishes>0&&Aborts>0);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveModelOpenWindowFinishCleanup,"OneBossFight.Framework.MoveModel.OpenWindowFinishCleanup",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossMoveModelOpenWindowFinishCleanup::RunTest(const FString&)
{
    using namespace BossMoveModelFixture;
    FRun R; if (!TestTrue(TEXT("start synthetic move"),R.Start())) return false;
    TestTrue(TEXT("advance into first hit window"),R.Model.Advance(R.Token,100.3,false,R.Events,R.Error));
    TestTrue(TEXT("window is genuinely open before terminal finish"),R.Model.OpenWindowCount()>0);
    TestTrue(TEXT("advance through recovery to normal finish"),R.Model.Advance(R.Token,100.8,false,R.Events,R.Error));
    TestTrue(TEXT("normal finish returns model to idle"),R.Model.State()==ERPGBossMoveModelState::Idle);
    TestEqual(TEXT("normal finish clears all open windows"),R.Model.OpenWindowCount(),0);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveModelCardBeforeTargetRefusal,"OneBossFight.Framework.MoveModel.CardBeforeTargetRefusal",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossMoveModelCardBeforeTargetRefusal::RunTest(const FString&)
{
    using namespace BossMoveModelFixture;
    FRPGBossMoveModel Model; FString Error; TestTrue(TEXT("initialize model"),Model.Initialize(7,1,Error));
    FRPGBossDecisionSnapshot S=Snapshot(); S.bTargetValid=false; S.TargetId=0;
    TestFalse(TEXT("simultaneous invalid card and target refuses"),Model.IsEligible({},S,Error));
    TestEqual(TEXT("card failure has precedence over target failure"),Error,FString(TEXT("MoveModel.Card")));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveModelVerticalBeforeStaleRefusal,"OneBossFight.Framework.MoveModel.VerticalBeforeStaleRefusal",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossMoveModelVerticalBeforeStaleRefusal::RunTest(const FString&)
{
    using namespace BossMoveModelFixture;
    FRPGBossMoveModel Model; FString Error; TestTrue(TEXT("initialize model"),Model.Initialize(7,1,Error));
    const auto LimitedCard=Card(false,2.f,10.f); auto S=Snapshot();
    FRPGBossAttackToken Token; TArray<FRPGBossMoveModelEvent> Events;
    TestTrue(TEXT("start limited card"),Model.Start(LimitedCard,S,Token,Events,Error));
    TestTrue(TEXT("finish card to restore idle eligibility"),Model.Advance(Token,101.,false,Events,Error));
    S.VerticalDeltaCm=20.; S.FrameId=10; S.ClockSeconds=100.;
    TestFalse(TEXT("simultaneous vertical and stale frame refuses"),Model.IsEligible(LimitedCard,S,Error));
    TestEqual(TEXT("vertical refusal precedes stale decision"),Error,FString(TEXT("MoveModel.Vertical")));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveModelOpenWindowAbortCleanup,"OneBossFight.Framework.MoveModel.OpenWindowAbortCleanup",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossMoveModelOpenWindowAbortCleanup::RunTest(const FString&)
{
    using namespace BossMoveModelFixture;
    FRun R; if (!TestTrue(TEXT("start synthetic move"),R.Start())) return false;
    TestTrue(TEXT("advance into active hit window"),R.Model.Advance(R.Token,100.3,false,R.Events,R.Error));
    TestTrue(TEXT("window is open before abort"),R.Model.OpenWindowCount()>0);
    TestTrue(TEXT("abort succeeds"),R.Model.Abort(R.Token,R.Events,R.Error));
    TestEqual(TEXT("abort clears every open window"),R.Model.OpenWindowCount(),0);
    TestTrue(TEXT("abort leaves model idle"),R.Model.State()==ERPGBossMoveModelState::Idle);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveModelBackwardClockWindowCleanup,"OneBossFight.Framework.MoveModel.BackwardClockWindowCleanup",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossMoveModelBackwardClockWindowCleanup::RunTest(const FString&)
{
    using namespace BossMoveModelFixture;
    FRun R; if (!TestTrue(TEXT("start synthetic move"),R.Start())) return false;
    TestTrue(TEXT("advance into active hit window"),R.Model.Advance(R.Token,100.3,false,R.Events,R.Error));
    TestTrue(TEXT("window is open before invalid clock"),R.Model.OpenWindowCount()>0);
    TestFalse(TEXT("backward clock is rejected"),R.Model.Advance(R.Token,100.2,false,R.Events,R.Error));
    TestEqual(TEXT("clock refusal clears every open window"),R.Model.OpenWindowCount(),0);
    TestTrue(TEXT("clock refusal leaves model idle"),R.Model.State()==ERPGBossMoveModelState::Idle);
    return true;
}
#endif
