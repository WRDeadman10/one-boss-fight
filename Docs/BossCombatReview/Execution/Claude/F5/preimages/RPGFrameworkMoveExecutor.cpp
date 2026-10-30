// Copyright One Boss Fight. All Rights Reserved.
#include "Boss/RPGFrameworkMoveExecutor.h"
#include "Boss/RPGFrameworkBossCharacter.h"
#include "Player/RPGBossFrameworkProfile.h"
#include "Player/RPGDamageResolver.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Animation/AnimSequence.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "CollisionQueryParams.h"
URPGFrameworkMoveExecutor::URPGFrameworkMoveExecutor()
{
    PrimaryComponentTick.bCanEverTick=true; PrimaryComponentTick.bStartWithTickEnabled=false;
    PrimaryComponentTick.TickGroup=TG_PostPhysics;
}
bool URPGFrameworkMoveExecutor::ValidatePlaybackCard(const TSharedPtr<const FRPGCompiledBossMoveCard>& C,FString& Error,bool bDamage)
{
    Error.Reset();
    if (!C||!C->HasResolvedAssets()) {Error=TEXT("Framework.Playback.UnresolvedPreview");return false;}
    if (!RPGBossMoveCards::Validate(C->Spec(),C->Metadata()).IsValid()||!C->Spec().Montage.IsNull()||C->Spec().Sequence.IsNull()||!C->Spec().SectionName.IsNone()||(bDamage?!(C->Spec().HPDamage>0.f):C->Spec().HPDamage!=0.f))
    {Error=TEXT("Framework.Playback.SequenceTelemetryOnly");return false;}
    return true;
}
bool URPGFrameworkMoveExecutor::Initialize(ARPGFrameworkBossCharacter* Boss,const FRPGFrameworkDependencies& D,APawn* InTarget,uint64 Encounter,uint64 Generation,FString& Error)
{
    if (!ValidatePlaybackCard(D.Card,Error,D.Profile.IsValid()&&D.Profile->bDamageEnabled)) return false;
    if (bInitialized||!IsInGameThread()||!IsValid(Boss)||GetOwner()!=Boss||!IsValid(InTarget)||Boss==InTarget||Boss->GetWorld()!=InTarget->GetWorld()||!D.Profile.IsValid())
    {Error=TEXT("Framework.Playback.OwnerTarget");return false;}
    UAnimInstance* Instance=Boss->GetMesh()->GetAnimInstance();
    if (!IsValid(Instance)||Instance->GetClass()!=D.AnimClass.Get()||!RPGFramework::HasSlotNode(Instance,D.Card->Spec().SlotName))
    {Error=TEXT("Framework.Playback.SlotGraph");return false;}
    if (!Model.Initialize(Encounter,Generation,Error)) return false;
    OwnerBoss=Boss; Target=InTarget; Card=D.Card; Profile=D.Profile.Get(); Anim=Instance; bInitialized=true;
    AddTickPrerequisiteComponent(Boss->GetMesh()); SetComponentTickEnabled(true);
    if (Profile->bDamageEnabled)
    {
        // Single life/generation authority of the framework boss: alive until the boss fails; generation = the proof generation.
        URPGDamageResolver* R=URPGDamageResolver::FindOrAdd(Boss);
        if (!IsValid(R)) {Error=TEXT("Framework.Playback.Resolver");return false;}
        const int32 Gen=int32(Generation);
        R->SetLifeProvider([W=TWeakObjectPtr<ARPGFrameworkBossCharacter>(Boss)]{return W.IsValid()&&!W->Failed();},[Gen]{return Gen;});
        Resolver=R;
    }
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] slot_graph name=%s nodeClass=AnimNode_Slot verified=1 label=%s"),*Card->Spec().SlotName.ToString(),*Label());
    return true;
}
bool URPGFrameworkMoveExecutor::Start(const FRPGBossDecisionSnapshot& S,FString& Error)
{
    if (!bInitialized||bAborted||!OwnerBoss.IsValid()||!Target.IsValid()||!IsIdle()||bFinished)
    {Error=TEXT("Framework.Playback.State");return false;}
    if (!ValidatePlaybackCard(Card,Error,Profile->bDamageEnabled)||!Model.IsEligible(Card,S,Error)) return false;
    // Loaded dependency only. No Resolve/Load call or alternate animation path in the playback consumer.
    UAnimSequence* Sequence=Card->Spec().Sequence.Get();
    if (!IsValid(Sequence)||!IsValid(Anim)||OwnerBoss->GetMesh()->GetAnimInstance()!=Anim)
    {Error=TEXT("Framework.Playback.DependencyDrift");return false;}
    // BOSS-EXE-002: the attack instance is reserved BEFORE playback; a failed play aborts that instance.
    TArray<FRPGBossMoveModelEvent> Events;
    if (!Model.Start(Card,S,Token,Events,Error)) return false;
    LogEvents(Events);
    OwnedMontage=Anim->PlaySlotAnimationAsDynamicMontage(Sequence,Card->Spec().SlotName,Profile->BlendInSeconds,Profile->BlendOutSeconds,Card->Spec().PlayRate,1,-1.f,0.f);
    if (!OwnedMontage) {Error=TEXT("Framework.Playback.StartFailed");Abort(Error);return false;}
    if (!Model.AdvanceObservedLocal(Token,0.,Events,Error)) {Abort(Error);return false;}
    StartWorldSeconds=LastWorldSeconds=GetWorld()->GetTimeSeconds(); LastPosition=0.; bSawPoseWeight=false;
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] playback_start encounter=%llu generation=%llu instance=%llu montage=%s slot=%s rate=%g label=%s"),Token.EncounterId,Token.Generation,Token.InstanceId,*OwnedMontage->GetPathName(),*Card->Spec().SlotName.ToString(),Card->Spec().PlayRate,*Label());
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
        {OwnedMontage=nullptr;bFinished=true;SetComponentTickEnabled(false);UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] cleanup reason=Finished modelIdle=1 ownedMontageStopped=1"));}
        return;
    }
    // A montage reaching its natural blend-out point (clip length - blend out) stops itself, possibly between two ticks. That is a finish when the last
    // observed position was within 1.5 ticks (or the blend-out span, whichever is larger) of that point (the profile guarantees RecoveryEnd + BlendOut <= clip length); anything earlier is an interruption.
    const bool bPlaying=Anim->Montage_IsPlaying(OwnedMontage);
    const double NaturalEnd=Card->Metadata().ClipLengthSeconds-Profile->BlendOutSeconds;
    if (!bPlaying&&LastPosition+FMath::Max(double(Delta)*Card->Spec().PlayRate*1.5,double(Profile->BlendOutSeconds))<NaturalEnd) {Fail(TEXT("Framework.Playback.EarlyStop"));return;}
    const double Position=bPlaying?Anim->Montage_GetPosition(OwnedMontage):FMath::Max(NaturalEnd,LastPosition);
    const float Node=Anim->GetSlotNodeGlobalWeight(Card->Spec().SlotName), Weight=Anim->GetSlotMontageGlobalWeight(Card->Spec().SlotName);
    if (!FMath::IsFinite(Node)||!FMath::IsFinite(Weight)||!FMath::IsFinite(Position)||Position<LastPosition)
    {Fail(TEXT("Framework.Playback.Observation"));return;}
    if (Node>0.f&&Weight>0.f) bSawPoseWeight=true;
    if (bPlaying&&((!bSawPoseWeight&&Now-StartWorldSeconds>Profile->BlendInSeconds)||((Node<=0.f||Weight<=0.f)&&Position>=Card->Spec().ActiveStartSeconds)))
    {Fail(TEXT("Framework.Playback.NoSlotContribution"));return;}
    if (!bPlaying) UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] montage_natural_end instance=%llu lastPosition=%g naturalEnd=%g"),Token.InstanceId,LastPosition,NaturalEnd);
    if (!Model.HeadingCommitted())
    {
        const FVector D=Target->GetActorLocation()-OwnerBoss->GetActorLocation();
        const float Yaw=FMath::FixedTurn(OwnerBoss->GetActorRotation().Yaw,D.Rotation().Yaw,Card->Spec().TrackDegreesPerSecond*Delta);
        OwnerBoss->SetActorRotation(FRotator(0.f,Yaw,0.f));
    }
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] playback instance=%llu position=%g nodeWeight=%g montageWeight=%g base=%s tip=%s"),Token.InstanceId,Position,Node,Weight,*OwnerBoss->GetMesh()->GetSocketLocation(TEXT("weapon_r")).ToString(),*OwnerBoss->GetMesh()->GetSocketLocation(TEXT("root_weapon_end_r")).ToString());
    const double PrevPosition=LastPosition; LastPosition=Position; TArray<FRPGBossMoveModelEvent> Events; FString Error;
    if (!Model.AdvanceObservedLocal(Token,Position,Events,Error)) {LogEvents(Events);Fail(*Error);return;}
    LogEvents(Events);
    SweepWindows(PrevPosition,Position);
    if (Model.State()==ERPGBossMoveModelState::Idle) StopOwned(Profile->BlendOutSeconds);
}
void URPGFrameworkMoveExecutor::SweepWindows(double PrevPosition,double Position)
{
    if (!Profile->bDamageEnabled||!Resolver.IsValid()||!Target.IsValid()||!OwnerBoss.IsValid()) return;
    USkeletalMeshComponent* Mesh=OwnerBoss->GetMesh();
    for (const FRPGBossMoveWindow& W:Card->Spec().Windows)
    {
        // The sockets are read live every tick: the blade is not rigid (measured 67..123 cm base-to-tip over the clip).
        const FVector A=Mesh->GetSocketLocation(W.SocketA), B=Mesh->GetSocketLocation(W.SocketB);
        FWindowPose& Prev=PrevPoses.FindOrAdd(W.WindowId);
        const bool bHad=Prev.bValid; const FVector PA=Prev.A, PB=Prev.B;
        Prev.A=A; Prev.B=B; Prev.bValid=true;
        const double Lo=FMath::Max(PrevPosition,double(W.StartSeconds)), Hi=FMath::Min(Position,double(W.EndSeconds));
        if (!bHad||Position<=PrevPosition||Hi<=Lo) continue;
        // Only the part of this tick the window was open: interpolate the pose linearly between the two ticks.
        const double Span=Position-PrevPosition, F0=(Lo-PrevPosition)/Span, F1=(Hi-PrevPosition)/Span;
        const FVector A0=FMath::Lerp(PA,A,F0), B0=FMath::Lerp(PB,B,F0), A1=FMath::Lerp(PA,A,F1), B1=FMath::Lerp(PB,B,F1);
        const double TipDistance=FVector::Dist(B0,B1);
        const int32 Wanted=FMath::Max(1,FMath::CeilToInt(float(TipDistance/Profile->HitStepCm))), Substeps=FMath::Min(Wanted,Profile->HitMaxSubsteps);
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] sweep instance=%llu window=%s from=%g to=%g tipDistanceCm=%g substeps=%d clamped=%d"),Token.InstanceId,*W.WindowId.ToString(),Lo,Hi,TipDistance,Substeps,Wanted>Substeps?1:0);
        FCollisionQueryParams Params(SCENE_QUERY_STAT(FrameworkSweep),false,OwnerBoss.Get());
        const FCollisionObjectQueryParams Objects(ECC_Pawn);
        bool bContact=false;
        for (int32 I=1;I<=Substeps&&!bContact;++I)
        {
            // Each substep is itself a swept capsule between two consecutive poses, so the chain has no gaps even when the cap clamps.
            const double Fa=double(I-1)/Substeps, Fb=double(I)/Substeps;
            const FVector PoseA0=FMath::Lerp(A0,A1,Fa), PoseB0=FMath::Lerp(B0,B1,Fa), PoseA1=FMath::Lerp(A0,A1,Fb), PoseB1=FMath::Lerp(B0,B1,Fb);
            const FVector Axis=PoseB1-PoseA1; const double Length=Axis.Size();
            if (Length<KINDA_SMALL_NUMBER) continue;
            const FQuat Rotation=FQuat::FindBetweenNormals(FVector::UpVector,Axis/Length);
            const FCollisionShape Shape=FCollisionShape::MakeCapsule(W.RadiusCm,float(Length*.5)+W.RadiusCm);
            TArray<FHitResult> Hits;
            GetWorld()->SweepMultiByObjectType(Hits,(PoseA0+PoseB0)*.5,(PoseA1+PoseB1)*.5,Rotation,Objects,Shape,Params);
            for (const FHitResult& H:Hits) if (H.GetActor()==Target.Get()) {bContact=true;break;}
        }
        if (!bContact) continue;
        FRPGDamagePayload Payload;
        Payload.MoveId=Card->Spec().MoveId; Payload.AttackInstance=int32(Token.InstanceId); Payload.Generation=int32(Token.Generation);
        Payload.HitKey=W.HitGroup.IsNone()?W.WindowId:W.HitGroup; Payload.HPDamage=Card->Spec().HPDamage;
        const FRPGDamageResult Result=Resolver->Resolve(Target.Get(),Payload);
        if (Result.Outcome==ERPGDamageOutcome::Accepted) {++HitsAccepted; AppliedDamage+=Result.HPApplied; if (OwnerBoss.IsValid()) OwnerBoss->NoteDamageApplied(Result.HPApplied);}
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] hit instance=%llu window=%s key=%s outcome=%s hpApplied=%g healthBefore=%g healthAfter=%g"),Token.InstanceId,*W.WindowId.ToString(),*Payload.HitKey.ToString(),*UEnum::GetValueAsString(Result.Outcome),Result.HPApplied,Result.HealthBefore,Result.HealthAfter);
    }
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
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] event encounter=%llu generation=%llu instance=%llu kind=%s window=%s group=%s localSeconds=%g label=%s"),E.Token.EncounterId,E.Token.Generation,E.Token.InstanceId,Kind,*E.WindowId.ToString(),*E.HitGroup.ToString(),E.LocalSeconds,*Label());
    }
}
FString URPGFrameworkMoveExecutor::Label() const {return Profile?Profile->FixtureLabel.Replace(TEXT(" "),TEXT("_")):FString(TEXT("none"));}
void URPGFrameworkMoveExecutor::StopOwned(float Blend)
{if(IsValid(Anim)&&IsValid(OwnedMontage))Anim->Montage_Stop(Blend,OwnedMontage);}
void URPGFrameworkMoveExecutor::Abort(const FString& Reason)
{
    // Cleanup runs exactly once: a clean finish or an earlier abort makes later calls (Fail, EndPlay) no-ops.
    if (bAborted||bFinished) return;
    TArray<FRPGBossMoveModelEvent> Events; FString Error;
    if (Token.InstanceId) Model.Abort(Token,Events,Error);
    bAborted=true; LogEvents(Events); StopOwned(0.f); OwnedMontage=nullptr; SetComponentTickEnabled(false);
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] cleanup reason=%s modelIdle=%d ownedMontageStopped=1"),*Reason,Model.State()==ERPGBossMoveModelState::Idle);
}
bool URPGFrameworkMoveExecutor::IsIdle() const {return Model.State()==ERPGBossMoveModelState::Idle&&!OwnedMontage;}
bool URPGFrameworkMoveExecutor::IsClean() const {return IsIdle();}
void URPGFrameworkMoveExecutor::EndPlay(const EEndPlayReason::Type Reason)
{Abort(TEXT("EndPlay"));Super::EndPlay(Reason);}
