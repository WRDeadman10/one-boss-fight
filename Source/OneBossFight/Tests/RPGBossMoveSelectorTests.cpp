// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossMoveSelector.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
namespace BossMoveSelectorFixture
{
// Synthetic, metadata-only cards: scheduling inputs, not real assets, tuned combat or playback proof.
TSharedPtr<const FRPGCompiledBossMoveCard> Card(const TCHAR* Id, float MinRange, float MaxRange,float FrontCone=120.f)
{
    FRPGBossMoveCardSpec S; FRPGBossMoveMetadata M;
    S.Schema=1; S.MoveId=Id; S.FamilyId=TEXT("SyntheticFamily"); S.PhaseId=TEXT("SyntheticPhase");
    S.Skeleton=TSoftObjectPtr<USkeleton>(FSoftObjectPath(TEXT("/Game/OneBossFight/Data/TypedABIFixtures/F1/Skeleton.Skeleton")));
    S.Sequence=TSoftObjectPtr<UAnimSequence>(FSoftObjectPath(TEXT("/Game/OneBossFight/Data/TypedABIFixtures/F1/Sequence.Sequence")));
    S.SlotName=TEXT("SyntheticSlot"); S.PlayRate=1.f; S.CommitSeconds=.25f; S.ActiveStartSeconds=.5f;
    S.ActiveEndSeconds=1.f; S.RecoveryEndSeconds=1.5f; S.MinRangeCm=MinRange; S.MaxRangeCm=MaxRange; S.FrontConeDegrees=FrontCone; S.HPDamage=17.f;
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
FRPGBossSelectorCandidate Cand(const TCHAR* Id, float Min, float Max, float Cooldown=0.f, float Weight=1.f,float FrontCone=120.f)
{ FRPGBossSelectorCandidate C; C.Card=Card(Id,Min,Max,FrontCone); C.CooldownSeconds=Cooldown; C.Weight=Weight; return C; }
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
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveSelectorBoundedTie,"OneBossFight.Framework.Selector.BoundedTie",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossMoveSelectorBoundedTie::RunTest(const FString&)
{
    // BOSS-SEL-005 bounded randomness. Scores at range 100 (centred): A 1.0, B 0.95, C 0.5; TieBand 0.1 -> threshold 0.9 -> top tier {A,B}; C must never be picked.
    using namespace BossMoveSelectorFixture;
    FRPGBossMoveModel Model;FString E;if(!Model.Initialize(7,1,E))return false;
    auto Cfg=[](float Band,int32 Seed){FRPGBossSelectorConfig C;C.RepeatPenalty=1.f;C.RepeatMemory=1;C.TieBand=Band;C.TieSeed=Seed;return C;};
    auto Run=[&](float Band,int32 Seed,int32 Count,int32 Counts[3],TArray<int32>* First){
        FRPGBossMoveSelector S;S.Initialize(Cfg(Band,Seed),{Cand(TEXT("A"),50,150,0.f,1.f),Cand(TEXT("B"),50,150,0.f,.95f),Cand(TEXT("C"),50,150,0.f,.5f)},E);
        for(int32 I=0;I<3;++I)Counts[I]=0;
        for(int32 I=0;I<Count;++I){FRPGBossSelectorDecision D;S.Select(Model,Snapshot(100.,100.+I),D);if(D.ChosenIndex>=0&&D.ChosenIndex<3)++Counts[D.ChosenIndex];if(First&&I<50)First->Add(D.ChosenIndex);S.NoteStarted(D.ChosenIndex,100.+I);}};
    int32 N[3];TArray<int32> Seq1,Seq2,Seq3;
    Run(.1f,12345,1000,N,&Seq1);
    TestEqual(TEXT("1000 selections all counted"),N[0]+N[1]+N[2],1000);
    TestEqual(TEXT("the card below the top tier is never picked"),N[2],0);
    TestTrue(TEXT("top tier member A picked often"),N[0]>300);TestTrue(TEXT("top tier member B picked often"),N[1]>300);
    Run(.1f,12345,1000,N,&Seq2);TestTrue(TEXT("same seed, same sequence"),Seq1==Seq2);
    Run(.1f,54321,1000,N,&Seq3);TestTrue(TEXT("another seed gives another sequence"),Seq1!=Seq3);TestEqual(TEXT("still never the card below the tier"),N[2],0);
    Run(0.f,12345,100,N,nullptr);TestEqual(TEXT("TieBand 0 stays deterministic: always A"),N[0],100);
    Run(.02f,12345,200,N,nullptr);TestEqual(TEXT("a narrow band (threshold 0.98) leaves only A in the tier"),N[0],200);
    for(float Bad:{-.1f,.51f,std::numeric_limits<float>::infinity(),std::numeric_limits<float>::quiet_NaN()}){FRPGBossMoveSelector S;FString Er;TestFalse(TEXT("tie band outside [0,0.5] refused"),S.Initialize(Cfg(Bad,1),{Cand(TEXT("A"),50,150)},Er));TestEqual(TEXT("named refusal"),Er,FString(TEXT("Selector.Config")));}
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveSelectorPattern,"OneBossFight.Framework.Selector.PatternMultipliers",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossMoveSelectorPattern::RunTest(const FString&)
{
    // BOSS-PHS-005: the kite / hug multipliers scale a card's score only while the context says so; domain refusals are named.
    using namespace BossMoveSelectorFixture;
    FRPGBossMoveModel Model;FString E;if(!Model.Initialize(7,1,E))return false;
    FRPGBossSelectorCandidate Base=Cand(TEXT("Base"),50,150,0.f,1.f), Boost=Cand(TEXT("Boost"),50,150,0.f,.5f);Boost.KiteMultiplier=3.f;Boost.HugMultiplier=2.f;
    FRPGBossMoveSelector S;TestTrue(TEXT("init"),S.Initialize(Config(),{Base,Boost},E));
    FRPGBossSelectorDecision D;
    S.Select(Model,Snapshot(100.),D);TestEqual(TEXT("no pattern: the heavier base card wins"),D.MoveId,FName(TEXT("Base")));
    FRPGBossSelectorContext Kite;Kite.bKiting=true;S.Select(Model,Snapshot(100.),D,Kite);TestEqual(TEXT("kiting: 0.5 x 3 beats 1"),D.MoveId,FName(TEXT("Boost")));
    FRPGBossSelectorContext Hug;Hug.bHugging=true;S.Select(Model,Snapshot(100.),D,Hug);TestEqual(TEXT("hugging: 0.5 x 2 ties 1 -> lowest index"),D.MoveId,FName(TEXT("Base")));
    FRPGBossSelectorContext Both;Both.bKiting=Both.bHugging=true;S.Select(Model,Snapshot(100.),D,Both);TestEqual(TEXT("both: 0.5 x 3 x 2 wins"),D.MoveId,FName(TEXT("Boost")));
    TestTrue(TEXT("the score carries the multipliers (range factor 1 at the middle of 50..150: 0.5 x 3 x 2 = 3)"),FMath::IsNearlyEqual(D.Score,3.f,.01f));
    for(float Bad:{0.f,-1.f,1.0001e6f,std::numeric_limits<float>::quiet_NaN()}){FRPGBossSelectorCandidate X=Cand(TEXT("X"),50,150);X.KiteMultiplier=Bad;FRPGBossMoveSelector T;FString Err;TestFalse(TEXT("bad kite multiplier refused"),T.Initialize(Config(),{X},Err));TestEqual(TEXT("named refusal"),Err,FString(TEXT("Selector.Domain")));}
    // BOSS-AWR-008 / AWR-006: the back-dodge and greed multipliers act only in their own context flag; bad values are refused.
    FRPGBossSelectorCandidate Fast=Cand(TEXT("Fast"),50,150,0.f,.5f);Fast.BackDodgeMultiplier=4.f;Fast.GreedMultiplier=3.f;
    FRPGBossMoveSelector G;TestTrue(TEXT("init greed"),G.Initialize(Config(),{Base,Fast},E));
    G.Select(Model,Snapshot(100.),D);TestEqual(TEXT("no flag: the base card wins"),D.MoveId,FName(TEXT("Base")));
    FRPGBossSelectorContext Greedy;Greedy.bGreedy=true;G.Select(Model,Snapshot(100.),D,Greedy);TestEqual(TEXT("greedy: 0.5 x 3 beats 1"),D.MoveId,FName(TEXT("Fast")));
    FRPGBossSelectorContext Back;Back.bBackDodging=true;G.Select(Model,Snapshot(100.),D,Back);TestEqual(TEXT("back dodging: 0.5 x 4 beats 1"),D.MoveId,FName(TEXT("Fast")));
    for(float Bad:{0.f,-1.f,1.0001e6f,std::numeric_limits<float>::quiet_NaN()}){FRPGBossSelectorCandidate X=Cand(TEXT("X"),50,150);X.GreedMultiplier=Bad;FRPGBossMoveSelector T;FString Err;TestFalse(TEXT("bad greed multiplier refused"),T.Initialize(Config(),{X},Err));}
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveSelectorConeHysteresis,"OneBossFight.Framework.Selector.ConeHysteresis",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossMoveSelectorConeHysteresis::RunTest(const FString&)
{
    using namespace BossMoveSelectorFixture;
    FRPGBossMoveModel Model;FString Error;if(!Model.Initialize(7,1,Error))return false;
    auto Eligible=[&](FRPGBossMoveSelector& Selector,double Yaw,const FRPGBossSelectorContext& Context)
    {
        FRPGBossDecisionSnapshot S=Snapshot();S.SignedYawDegrees=Yaw;
        FRPGBossSelectorDecision D;Selector.Select(Model,S,D,Context);
        return D.Traces.Num()==1&&D.Traces[0].bEligible;
    };

    const FRPGBossSelectorCandidate Candidate60=Cand(TEXT("Cone"),50,150,0.f,1.f,60.f);
    FRPGBossSelectorContext Off;
    FRPGBossMoveSelector NoHysteresis;TestTrue(TEXT("initialize no-hysteresis selector"),NoHysteresis.Initialize(Config(),{Candidate60},Error));
    bool bPrevious=false;int32 PlainFlips=0;
    for(int32 Cycle=0;Cycle<20;++Cycle)
        for(const double Yaw:{29.,31.})
        {
            const bool bNow=Eligible(NoHysteresis,Yaw,Off);
            if(bNow!=bPrevious)++PlainFlips;
            bPrevious=bNow;
        }
    TestEqual(TEXT("without hysteresis, oscillating around the cone edge flips 40 times"),PlainFlips,40);

    FRPGBossSelectorContext On;On.ConeHysteresisDegrees=6.;
    FRPGBossMoveSelector Hysteresis;TestTrue(TEXT("initialize hysteresis selector"),Hysteresis.Initialize(Config(),{Candidate60},Error));
    bool bInside=Eligible(Hysteresis,29.,On);TestTrue(TEXT("first entry at or inside half angle"),bInside);
    int32 FlipsAfterEntry=0;
    for(int32 Cycle=0;Cycle<20;++Cycle)
        for(const double Yaw:{31.,29.})
        {
            const bool bNow=Eligible(Hysteresis,Yaw,On);
            if(bNow!=bInside)++FlipsAfterEntry;
            bInside=bNow;
        }
    TestEqual(TEXT("six degrees of full-cone slack holds through the same edge oscillation"),FlipsAfterEntry,0);

    TestFalse(TEXT("outside the exit edge leaves the cone"),Eligible(Hysteresis,34.,On));
    TestFalse(TEXT("after leaving, hysteresis does not re-enter above the original half angle"),Eligible(Hysteresis,31.,On));
    TestTrue(TEXT("after leaving, re-enter at the original half angle"),Eligible(Hysteresis,30.,On));

    FRPGBossMoveSelector Resettable;TestTrue(TEXT("initialize reset selector"),Resettable.Initialize(Config(),{Candidate60},Error));
    TestTrue(TEXT("reset test enters cone"),Eligible(Resettable,30.,On));
    TestTrue(TEXT("remembered card stays eligible in exit band"),Eligible(Resettable,32.,On));
    Resettable.Reset();
    TestFalse(TEXT("reset forgets cone memory"),Eligible(Resettable,32.,On));

    FRPGBossMoveSelector ZeroSlack;TestTrue(TEXT("initialize zero-slack selector"),ZeroSlack.Initialize(Config(),{Candidate60},Error));
    const double Yaws[]={-180.,-90.,-30.001,-30.,-12.,0.,12.,30.,30.001,90.,179.,180.};
    for(const double Yaw:Yaws)
        TestEqual(*FString::Printf(TEXT("zero slack retains prior cone rule at yaw %g"),Yaw),Eligible(ZeroSlack,Yaw,Off),FMath::Abs(Yaw)<=30.);
    return true;
}
#endif
