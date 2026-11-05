// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossMoveSelector.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
namespace BossComboFallbackFixture
{
TSharedPtr<const FRPGCompiledBossMoveCard> Card(const TCHAR* Id, float Cone)
{
    FRPGBossMoveCardSpec Spec;
    FRPGBossMoveMetadata Metadata;
    Spec.Schema=1;
    Spec.MoveId=Id;
    Spec.FamilyId=TEXT("ComboFallbackFixture");
    Spec.PhaseId=TEXT("Phase_1");
    Spec.Skeleton=TSoftObjectPtr<USkeleton>(FSoftObjectPath(TEXT("/Game/OneBossFight/Data/TypedABIFixtures/F1/Skeleton.Skeleton")));
    Spec.Sequence=TSoftObjectPtr<UAnimSequence>(FSoftObjectPath(TEXT("/Game/OneBossFight/Data/TypedABIFixtures/F1/Sequence.Sequence")));
    Spec.SlotName=TEXT("SyntheticSlot");
    Spec.PlayRate=1.f;
    Spec.CommitSeconds=.25f;
    Spec.ActiveStartSeconds=.5f;
    Spec.ActiveEndSeconds=1.f;
    Spec.RecoveryEndSeconds=1.5f;
    Spec.MinRangeCm=50.f;
    Spec.MaxRangeCm=150.f;
    Spec.FrontConeDegrees=Cone;
    Spec.HPDamage=1.f;

    FRPGBossMoveWindow Window;
    Window.WindowId=TEXT("Window");
    Window.HitGroup=TEXT("Shared");
    Window.SocketA=TEXT("Base");
    Window.SocketB=TEXT("Tip");
    Window.RadiusCm=8.f;
    Window.StartSeconds=.5f;
    Window.EndSeconds=1.f;
    Spec.Windows.Add(Window);

    Metadata.AnimationPath=Spec.Sequence.ToSoftObjectPath();
    Metadata.SkeletonPath=Spec.Skeleton.ToSoftObjectPath();
    Metadata.AnimationSkeletonPath=Metadata.MeshSkeletonPath=Metadata.SkeletonPath;
    Metadata.ClipLengthSeconds=2.;
    Metadata.Slots.Add(Spec.SlotName);
    Metadata.SocketOrBoneNames.Add(Window.SocketA);
    Metadata.SocketOrBoneNames.Add(Window.SocketB);

    TSharedPtr<const FRPGCompiledBossMoveCard> Compiled;
    RPGBossMoveCards::CompileMetadata(Spec,Metadata,Compiled);
    return Compiled;
}

}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossComboFallbackAfterModelRefusal,
    "OneBossFight.Framework.Combo.FallbackAfterModelRefusal",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossComboFallbackAfterModelRefusal::RunTest(const FString&)
{
    // Fresh model, selector, candidate array, and cards for this case. The combo continuation
    // sees a newly captured gate snapshot outside its cone; a wider ordinary card remains eligible.
    FRPGBossMoveModel Model;
    FString Error;
    TestTrue(TEXT("initialize fresh model"),Model.Initialize(81,1,Error));

    const TSharedPtr<const FRPGCompiledBossMoveCard> ComboCard=BossComboFallbackFixture::Card(TEXT("ComboForward"),60.f);
    const TSharedPtr<const FRPGCompiledBossMoveCard> FallbackCard=BossComboFallbackFixture::Card(TEXT("OrdinaryFallback"),120.f);
    TestTrue(TEXT("compile combo card fixture"),ComboCard.IsValid());
    TestTrue(TEXT("compile fallback card fixture"),FallbackCard.IsValid());
    FRPGBossSelectorCandidate ComboCandidate;
    ComboCandidate.Card=ComboCard;
    FRPGBossSelectorCandidate FallbackCandidate;
    FallbackCandidate.Card=FallbackCard;
    FRPGBossSelectorConfig Config;
    Config.RepeatPenalty=.5f;
    Config.RepeatMemory=2;
    FRPGBossMoveSelector Selector;
    TestTrue(TEXT("initialize fresh selector fixture"),Selector.Initialize(Config,{ComboCandidate,FallbackCandidate},Error));

    FRPGBossDecisionSnapshot FreshGate;
    FreshGate.EncounterId=81;
    FreshGate.Generation=1;
    FreshGate.TargetId=9;
    FreshGate.FrameId=27;
    FreshGate.PhaseId=TEXT("Phase_1");
    FreshGate.ClockSeconds=4.0;
    FreshGate.RangeCm=100.0;
    FreshGate.SignedYawDegrees=50.0;
    FreshGate.bTargetValid=true;
    FreshGate.bNeutral=true;

    FRPGBossAttackToken RefusedToken;
    TArray<FRPGBossMoveModelEvent> Events;
    TestFalse(TEXT("fresh gate refuses the forward combo continuation"),Model.Start(ComboCard,FreshGate,RefusedToken,Events,Error));
    TestEqual(TEXT("combo refusal is the cone filter"),Error,FString(TEXT("MoveModel.Cone")));
    TestTrue(TEXT("refusal leaves the model idle"),Model.State()==ERPGBossMoveModelState::Idle);

    FRPGBossSelectorDecision Decision;
    TestTrue(TEXT("ordinary selector fallback evaluation succeeds"),Selector.Select(Model,FreshGate,Decision));
    TestEqual(TEXT("selector chooses the other eligible card"),Decision.MoveId,FName(TEXT("OrdinaryFallback")));
    TestFalse(TEXT("combo card remains ineligible"),Decision.Traces[0].bEligible);
    TestEqual(TEXT("combo refusal remains visible"),Decision.Traces[0].Refusal,FString(TEXT("MoveModel.Cone")));
    TestTrue(TEXT("ordinary fallback is eligible"),Decision.Traces[1].bEligible);

    TestTrue(TEXT("ordinary fallback starts with the same fresh gate snapshot"),Model.Start(FallbackCard,FreshGate,RefusedToken,Events,Error));
    TestTrue(TEXT("fallback owns the active model token"),Model.AcceptsCallback(RefusedToken));
    return true;
}
#endif
