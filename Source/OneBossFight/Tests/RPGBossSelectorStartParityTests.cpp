// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossMoveSelector.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
namespace BossSelectorParityFixture
{
TSharedPtr<const FRPGCompiledBossMoveCard> Card(const TCHAR* Id, float Cone=120.f)
{
    FRPGBossMoveCardSpec Spec;
    FRPGBossMoveMetadata Metadata;
    Spec.Schema=1; Spec.MoveId=Id; Spec.FamilyId=TEXT("SelectorParityFixture"); Spec.PhaseId=TEXT("Phase_1");
    Spec.Skeleton=TSoftObjectPtr<USkeleton>(FSoftObjectPath(TEXT("/Game/OneBossFight/Data/TypedABIFixtures/F1/Skeleton.Skeleton")));
    Spec.Sequence=TSoftObjectPtr<UAnimSequence>(FSoftObjectPath(TEXT("/Game/OneBossFight/Data/TypedABIFixtures/F1/Sequence.Sequence")));
    Spec.SlotName=TEXT("SyntheticSlot"); Spec.PlayRate=1.f; Spec.CommitSeconds=.25f;
    Spec.ActiveStartSeconds=.5f; Spec.ActiveEndSeconds=1.f; Spec.RecoveryEndSeconds=1.5f;
    Spec.MinRangeCm=50.f; Spec.MaxRangeCm=150.f; Spec.FrontConeDegrees=Cone; Spec.HPDamage=1.f;
    FRPGBossMoveWindow Window; Window.WindowId=TEXT("Window"); Window.HitGroup=TEXT("Shared");
    Window.SocketA=TEXT("Base"); Window.SocketB=TEXT("Tip"); Window.RadiusCm=8.f; Window.StartSeconds=.5f; Window.EndSeconds=1.f;
    Spec.Windows.Add(Window); Metadata.AnimationPath=Spec.Sequence.ToSoftObjectPath(); Metadata.SkeletonPath=Spec.Skeleton.ToSoftObjectPath();
    Metadata.AnimationSkeletonPath=Metadata.MeshSkeletonPath=Metadata.SkeletonPath; Metadata.ClipLengthSeconds=2.;
    Metadata.Slots.Add(Spec.SlotName); Metadata.SocketOrBoneNames.Add(Window.SocketA); Metadata.SocketOrBoneNames.Add(Window.SocketB);
    TSharedPtr<const FRPGCompiledBossMoveCard> Result; RPGBossMoveCards::CompileMetadata(Spec,Metadata,Result); return Result;
}
FRPGBossDecisionSnapshot Snapshot(double Yaw=0.)
{
    FRPGBossDecisionSnapshot S; S.EncounterId=81; S.Generation=1; S.TargetId=9; S.FrameId=27;
    S.PhaseId=TEXT("Phase_1"); S.ClockSeconds=4.; S.RangeCm=100.; S.SignedYawDegrees=Yaw; S.bTargetValid=true; S.bNeutral=true; return S;
}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossSelectorStartParity, "OneBossFight.Framework.Selector.StartParity", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossSelectorStartParity::RunTest(const FString&)
{
    using namespace BossSelectorParityFixture;
    FString Error; FRPGBossMoveModel Model; TestTrue(TEXT("initialize move model"),Model.Initialize(81,1,Error));
    const auto CardA=Card(TEXT("ParityA"),120.f); TestTrue(TEXT("compile card"),CardA.IsValid());
    FRPGBossSelectorCandidate Candidate; Candidate.Card=CardA;
    FRPGBossSelectorConfig Config; Config.RepeatPenalty=1.f; Config.RepeatMemory=1;
    FRPGBossMoveSelector Selector; TestTrue(TEXT("initialize selector"),Selector.Initialize(Config,{Candidate},Error));
    FRPGBossSelectorDecision Decision; const auto S=Snapshot();
    TestTrue(TEXT("selector evaluation succeeds"),Selector.Select(Model,S,Decision));
    TestTrue(TEXT("selector and start share eligible snapshot"),Model.IsEligible(CardA,S,Error));
    TestEqual(TEXT("eligible candidate selected"),Decision.MoveId,FName(TEXT("ParityA")));
    FRPGBossAttackToken Token; TArray<FRPGBossMoveModelEvent> Events;
    TestTrue(TEXT("same snapshot starts selected card"),Model.Start(CardA,S,Token,Events,Error));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossSelectorConeBoundaryParity, "OneBossFight.Framework.Selector.ConeBoundaryParity", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossSelectorConeBoundaryParity::RunTest(const FString&)
{
    using namespace BossSelectorParityFixture;
    FString Error; FRPGBossMoveModel Model; TestTrue(TEXT("initialize move model"),Model.Initialize(81,1,Error));
    const auto CardA=Card(TEXT("ConeEdge"),120.f); FRPGBossSelectorCandidate Candidate; Candidate.Card=CardA;
    FRPGBossSelectorConfig Config; Config.RepeatPenalty=1.f; Config.RepeatMemory=1; FRPGBossMoveSelector Selector;
    TestTrue(TEXT("initialize selector"),Selector.Initialize(Config,{Candidate},Error));
    FRPGBossSelectorDecision Decision; const auto S=Snapshot(60.);
    TestTrue(TEXT("selector evaluates exact cone edge"),Selector.Select(Model,S,Decision));
    TestTrue(TEXT("exact cone edge is eligible in selector"),Decision.Traces[0].bEligible);
    TestTrue(TEXT("exact cone edge is eligible at start"),Model.IsEligible(CardA,S,Error));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossSelectorConeAdjacentParity, "OneBossFight.Framework.Selector.ConeAdjacentParity", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossSelectorConeAdjacentParity::RunTest(const FString&)
{
    using namespace BossSelectorParityFixture;
    FString Error; FRPGBossMoveModel Model; TestTrue(TEXT("initialize move model"),Model.Initialize(81,1,Error));
    const auto CardA=Card(TEXT("ConeAdjacent"),120.f); FRPGBossSelectorCandidate Candidate; Candidate.Card=CardA;
    FRPGBossSelectorConfig Config; Config.RepeatPenalty=1.f; Config.RepeatMemory=1; FRPGBossMoveSelector Selector;
    TestTrue(TEXT("initialize selector"),Selector.Initialize(Config,{Candidate},Error));
    FRPGBossSelectorDecision Decision; const auto S=Snapshot(60.0001);
    TestTrue(TEXT("selector evaluates outside cone"),Selector.Select(Model,S,Decision));
    TestFalse(TEXT("outside cone is refused by selector"),Decision.Traces[0].bEligible);
    TestFalse(TEXT("outside cone is refused at start"),Model.IsEligible(CardA,S,Error));
    TestEqual(TEXT("start refusal token matches selector trace"),Decision.Traces[0].Refusal,Error);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossSelectorEmptySingleParity, "OneBossFight.Framework.Selector.EmptySingleParity", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossSelectorEmptySingleParity::RunTest(const FString&)
{
    using namespace BossSelectorParityFixture;
    FString Error; FRPGBossMoveModel Model; TestTrue(TEXT("initialize move model"),Model.Initialize(81,1,Error));
    FRPGBossSelectorConfig Config; Config.RepeatPenalty=1.f; Config.RepeatMemory=1; FRPGBossMoveSelector Empty;
    TestFalse(TEXT("empty candidate set refuses initialization"),Empty.Initialize(Config,{},Error));
    TestEqual(TEXT("empty candidate refusal token stable"),Error,FString(TEXT("Selector.NoCandidates")));
    const auto CardA=Card(TEXT("Single")); FRPGBossSelectorCandidate Candidate; Candidate.Card=CardA;
    FRPGBossMoveSelector Single; TestTrue(TEXT("single candidate initializes"),Single.Initialize(Config,{Candidate},Error));
    FRPGBossSelectorDecision Decision; const auto S=Snapshot();
    TestTrue(TEXT("single candidate selection succeeds"),Single.Select(Model,S,Decision));
    TestEqual(TEXT("single eligible candidate selected"),Decision.MoveId,FName(TEXT("Single")));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossSelectorTieRepeatability, "OneBossFight.Framework.Selector.TieRepeatability", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossSelectorTieRepeatability::RunTest(const FString&)
{
    using namespace BossSelectorParityFixture;
    FString Error; FRPGBossMoveModel Model; TestTrue(TEXT("initialize move model"),Model.Initialize(81,1,Error));
    const auto A=Card(TEXT("TieA")); const auto B=Card(TEXT("TieB"));
    FRPGBossSelectorCandidate CA; CA.Card=A; FRPGBossSelectorCandidate CB; CB.Card=B;
    FRPGBossSelectorConfig Config; Config.RepeatPenalty=1.f; Config.RepeatMemory=1; Config.TieBand=.2f; Config.TieSeed=771;
    FRPGBossMoveSelector First,Second; TestTrue(TEXT("initialize first selector"),First.Initialize(Config,{CA,CB},Error));
    TestTrue(TEXT("initialize second selector"),Second.Initialize(Config,{CA,CB},Error));
    FRPGBossSelectorDecision One,Two; const auto S=Snapshot();
    TestTrue(TEXT("first seeded selection succeeds"),First.Select(Model,S,One));
    TestTrue(TEXT("second seeded selection succeeds"),Second.Select(Model,S,Two));
    TestEqual(TEXT("identical seeded selector inputs reproduce tie choice"),One.MoveId,Two.MoveId);
    TestTrue(TEXT("tie result is an eligible candidate"),One.MoveId==FName(TEXT("TieA"))||One.MoveId==FName(TEXT("TieB")));
    return true;
}
#endif
