// Copyright One Boss Fight. All Rights Reserved.
#include "Boss/RPGFrameworkMoveExecutor.h"
#include "Boss/RPGFrameworkBossCharacter.h"
#include "Player/RPGBossFrameworkProfile.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Animation/AnimSequence.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
URPGFrameworkMoveExecutor::URPGFrameworkMoveExecutor()
{
    PrimaryComponentTick.bCanEverTick=true; PrimaryComponentTick.bStartWithTickEnabled=false;
    PrimaryComponentTick.TickGroup=TG_PostPhysics;
}
bool URPGFrameworkMoveExecutor::ValidatePlaybackCard(const TSharedPtr<const FRPGCompiledBossMoveCard>& C,FString& Error)
{
    Error.Reset();
    if (!C||!C->HasResolvedAssets()) {Error=TEXT("Framework.Playback.UnresolvedPreview");return false;}
    if (!RPGBossMoveCards::Validate(C->Spec(),C->Metadata()).IsValid()||!C->Spec().Montage.IsNull()||C->Spec().Sequence.IsNull()||!C->Spec().SectionName.IsNone()||C->Spec().HPDamage!=0.f)
    {Error=TEXT("Framework.Playback.SequenceTelemetryOnly");return false;}
    return true;
}
bool URPGFrameworkMoveExecutor::Initialize(ARPGFrameworkBossCharacter* Boss,const FRPGFrameworkDependencies& D,APawn* InTarget,uint64 Encounter,uint64 Generation,FString& Error)
{
    if (!ValidatePlaybackCard(D.Card,Error)) return false;
    if (bInitialized||!IsInGameThread()||!IsValid(Boss)||GetOwner()!=Boss||!IsValid(InTarget)||Boss==InTarget||Boss->GetWorld()!=InTarget->GetWorld()||!D.Profile.IsValid())
    {Error=TEXT("Framework.Playback.OwnerTarget");return false;}
    UAnimInstance* Instance=Boss->GetMesh()->GetAnimInstance();
    if (!IsValid(Instance)||Instance->GetClass()!=D.AnimClass.Get()||!RPGFramework::HasSlotNode(Instance,D.Card->Spec().SlotName))
    {Error=TEXT("Framework.Playback.SlotGraph");return false;}
    if (!Model.Initialize(Encounter,Generation,Error)) return false;
    OwnerBoss=Boss; Target=InTarget; Card=D.Card; Profile=D.Profile.Get(); Anim=Instance; bInitialized=true;
    AddTickPrerequisiteComponent(Boss->GetMesh()); SetComponentTickEnabled(true);
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] slot_graph name=%s nodeClass=AnimNode_Slot verified=1 label=F3_fixture"),*Card->Spec().SlotName.ToString());
    return true;
}
bool URPGFrameworkMoveExecutor::Start(const FRPGBossDecisionSnapshot& S,FString& Error)
{
    if (!bInitialized||bAborted||!OwnerBoss.IsValid()||!Target.IsValid()||!IsIdle()||bFinished)
    {Error=TEXT("Framework.Playback.State");return false;}
    if (!ValidatePlaybackCard(Card,Error)||!Model.IsEligible(Card,S,Error)) return false;
    // Loaded dependency only. No Resolve/Load call or alternate animation path in the playback consumer.
    UAnimSequence* Sequence=Card->Spec().Sequence.Get();
    if (!IsValid(Sequence)||!IsValid(Anim)||OwnerBoss->GetMesh()->GetAnimInstance()!=Anim)
    {Error=TEXT("Framework.Playback.DependencyDrift");return false;}
    OwnedMontage=Anim->PlaySlotAnimationAsDynamicMontage(Sequence,Card->Spec().SlotName,Profile->BlendInSeconds,Profile->BlendOutSeconds,Card->Spec().PlayRate,1,-1.f,0.f);
    if (!OwnedMontage) {Error=TEXT("Framework.Playback.StartFailed");return false;}
    TArray<FRPGBossMoveModelEvent> Events;
    if (!Model.Start(Card,S,Token,Events,Error)) {StopOwned(0.f);OwnedMontage=nullptr;return false;}
    LogEvents(Events);
    if (!Model.AdvanceObservedLocal(Token,0.,Events,Error)) {Abort(Error);return false;}
    StartWorldSeconds=LastWorldSeconds=GetWorld()->GetTimeSeconds(); LastPosition=0.; bSawPoseWeight=false;
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] playback_start encounter=%llu generation=%llu instance=%llu montage=%s slot=%s rate=%g label=F3_fixture"),Token.EncounterId,Token.Generation,Token.InstanceId,*OwnedMontage->GetPathName(),*Card->Spec().SlotName.ToString(),Card->Spec().PlayRate);
    return true;
}
void URPGFrameworkMoveExecutor::TickComponent(float Delta,ELevelTick Type,FActorComponentTickFunction* Tick)
{
    Super::TickComponent(Delta,Type,Tick);
    if (!bInitialized||!OwnedMontage) return;
    auto Fail=[this](const TCHAR* E){if(OwnerBoss.IsValid())OwnerBoss->Fail(E);else Abort(E);};
    if (!OwnerBoss.IsValid()||!Target.IsValid()||!IsValid(Anim)||OwnerBoss->GetMesh()->GetAnimInstance()!=Anim||Target->GetWorld()!=GetWorld()||Target->IsActorBeingDestroyed())
    {Fail(TEXT("Framework.Playback.Lifecycle"));return;}
    const double Now=GetWorld()->GetTimeSeconds();
    if (!FMath::IsFinite(Now)||Now<LastWorldSeconds||Now-StartWorldSeconds>Profile->WalkTimeoutSeconds)
    {Fail(TEXT("Framework.Playback.TimeoutOrClock"));return;}
    LastWorldSeconds=Now;
    if (Model.State()==ERPGBossMoveModelState::Idle)
    {
        if (!Anim->Montage_IsActive(OwnedMontage))
        {OwnedMontage=nullptr;bFinished=true;UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] cleanup reason=Finished modelIdle=1 ownedMontageStopped=1"));}
        return;
    }
    if (!Anim->Montage_IsPlaying(OwnedMontage)) {Fail(TEXT("Framework.Playback.EarlyStop"));return;}
    const double Position=Anim->Montage_GetPosition(OwnedMontage);
    const float Node=Anim->GetSlotNodeGlobalWeight(Card->Spec().SlotName), Weight=Anim->GetSlotMontageGlobalWeight(Card->Spec().SlotName);
    if (!FMath::IsFinite(Node)||!FMath::IsFinite(Weight)||!FMath::IsFinite(Position)||Position<LastPosition)
    {Fail(TEXT("Framework.Playback.Observation"));return;}
    if (Node>0.f&&Weight>0.f) bSawPoseWeight=true;
    if ((!bSawPoseWeight&&Now-StartWorldSeconds>Profile->BlendInSeconds)||((Node<=0.f||Weight<=0.f)&&Position>=Card->Spec().ActiveStartSeconds))
    {Fail(TEXT("Framework.Playback.NoSlotContribution"));return;}
    if (!Model.HeadingCommitted())
    {
        const FVector D=Target->GetActorLocation()-OwnerBoss->GetActorLocation();
        const float Yaw=FMath::FixedTurn(OwnerBoss->GetActorRotation().Yaw,D.Rotation().Yaw,Card->Spec().TrackDegreesPerSecond*Delta);
        OwnerBoss->SetActorRotation(FRotator(0.f,Yaw,0.f));
    }
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] playback instance=%llu position=%g nodeWeight=%g montageWeight=%g base=%s tip=%s"),Token.InstanceId,Position,Node,Weight,*OwnerBoss->GetMesh()->GetSocketLocation(TEXT("weapon_r")).ToString(),*OwnerBoss->GetMesh()->GetSocketLocation(TEXT("root_weapon_end_r")).ToString());
    LastPosition=Position; TArray<FRPGBossMoveModelEvent> Events; FString Error;
    if (!Model.AdvanceObservedLocal(Token,Position,Events,Error)) {LogEvents(Events);Fail(*Error);return;}
    LogEvents(Events);
    if (Model.State()==ERPGBossMoveModelState::Idle) StopOwned(Profile->BlendOutSeconds);
}
void URPGFrameworkMoveExecutor::LogEvents(const TArray<FRPGBossMoveModelEvent>& Events) const
{
    for (const auto& E:Events)
    {
        const TCHAR* Kind=TEXT("Invalid");
        switch(E.Kind)
        {
        case ERPGBossMoveModelEvent::Open:Kind=TEXT("Open");break;
        case ERPGBossMoveModelEvent::Close:Kind=TEXT("Close");break;
        case ERPGBossMoveModelEvent::Recovery:Kind=TEXT("Recovery");break;
        case ERPGBossMoveModelEvent::Finished:Kind=TEXT("Finished");break;
        case ERPGBossMoveModelEvent::Aborted:Kind=TEXT("Aborted");break;
        }
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] event encounter=%llu generation=%llu instance=%llu kind=%s window=%s group=%s localSeconds=%g label=F3_fixture"),E.Token.EncounterId,E.Token.Generation,E.Token.InstanceId,Kind,*E.WindowId.ToString(),*E.HitGroup.ToString(),E.LocalSeconds);
    }
}
void URPGFrameworkMoveExecutor::StopOwned(float Blend)
{if(IsValid(Anim)&&IsValid(OwnedMontage))Anim->Montage_Stop(Blend,OwnedMontage);}
void URPGFrameworkMoveExecutor::Abort(const FString& Reason)
{
    TArray<FRPGBossMoveModelEvent> Events; FString Error;
    if (Token.InstanceId) Model.Abort(Token,Events,Error);
    bAborted=true; LogEvents(Events); StopOwned(0.f); OwnedMontage=nullptr; SetComponentTickEnabled(false);
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] cleanup reason=%s modelIdle=%d ownedMontageStopped=1"),*Reason,Model.State()==ERPGBossMoveModelState::Idle);
}
bool URPGFrameworkMoveExecutor::IsIdle() const {return Model.State()==ERPGBossMoveModelState::Idle&&!OwnedMontage;}
bool URPGFrameworkMoveExecutor::IsClean() const {return IsIdle();}
void URPGFrameworkMoveExecutor::EndPlay(const EEndPlayReason::Type Reason)
{Abort(TEXT("EndPlay"));Super::EndPlay(Reason);}
