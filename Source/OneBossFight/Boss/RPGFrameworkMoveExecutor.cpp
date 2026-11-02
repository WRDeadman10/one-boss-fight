// Copyright One Boss Fight. All Rights Reserved.
#include "Boss/RPGFrameworkMoveExecutor.h"
#include "Player/RPGBossTrackRules.h"
#include "Player/RPGBossApproachRules.h"
#include "Player/RPGBossCueRules.h"
#include "Player/RPGBossGuardRules.h"
#include "Player/RPGBossDamage.h"
#include "Player/RPGPlayerParry.h"
#include "AIController.h"
#include "Navigation/PathFollowingComponent.h"
#include "Player/RPGFlipbookEffect.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"
#include "Boss/RPGFrameworkBossCharacter.h"
#include "Player/RPGBossFrameworkProfile.h"
#include "Player/RPGDamageResolver.h"
#include "Player/RPGBossSweepSampling.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Animation/AnimSequence.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/Character.h"
#include "Components/CapsuleComponent.h"
#include "CollisionQueryParams.h"

namespace
{
	void RecordParriedContact(ARPGFrameworkBossCharacter* Boss, APawn* Target)
	{
		const URPGPlayerParry* Parry=Target?Target->FindComponentByClass<URPGPlayerParry>():nullptr;
		const RPGParryGrade::EGrade Grade=Parry?Parry->GradeNow():RPGParryGrade::EGrade::None;
		const TCHAR* GradeName=Grade==RPGParryGrade::EGrade::Perfect?TEXT("Perfect"):Grade==RPGParryGrade::EGrade::Good?TEXT("Good"):Grade==RPGParryGrade::EGrade::Late?TEXT("Late"):TEXT("None");
		const URPGBossFrameworkProfile* Profile=Boss?Boss->ProofProfile():nullptr;
		const double Scale=Profile&&Profile->bParryGradeScale?RPGParryGrade::PostureScale(Grade):1.0;
		if (Boss) Boss->NoteParried(Scale);
		UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] parry_grade grade=%s scale=%g"),GradeName,Scale);
	}
}
#if !UE_BUILD_SHIPPING
static TAutoConsoleVariable<int32> CVarCueMode(TEXT("rpg.CueMode"),0,TEXT("Accessible feedback (BOSS-QA-007): 0 = every boss cue shows its visual AND plays its sound, 1 = visual only, 2 = sound only, 3 = both with the visual at half size."),ECVF_Default);
#if !UE_BUILD_SHIPPING
static TAutoConsoleVariable<int32> CVarBossProofRepeatAbort(TEXT("rpg.BossProofRepeatAbort"),0,TEXT("Test hook (BOSS-EXE-006): after every abort the executor is aborted N more times and the duplicate cleanups / releases are counted (must be 0). 0 = off."),ECVF_Default);
static TAutoConsoleVariable<float> CVarBossProofMotionIntruder(TEXT("rpg.BossProofMotionIntruder"),-1.f,TEXT("Test hook (BOSS-ANM-005): at this card time (seconds) a navigation move request is sent to the boss controller; the boss must not move. Negative = off."),ECVF_Default);
#endif
static TAutoConsoleVariable<int32> CVarBossProofStaleCallback(TEXT("rpg.BossProofStaleCallback"),0,TEXT("Test hook (BOSS-EXE-004): 1 sends a late abort callback of the PREVIOUS (aborted) attack to the move model right after the next attack started; it must be refused and the new attack must live. 0 = off. Not compiled into shipping builds."),ECVF_Default);
static TAutoConsoleVariable<int32> CVarBossProofSuppressMontageEnd(TEXT("rpg.BossProofSuppressMontageEnd"),0,TEXT("Test hook (BOSS-EXE-007 / ANM-007): 1 stops feeding the montage position to the move model once the card has played 0.3 s, as if the end notifications were dropped; the watchdog must then abort the card. 0 = off. Not compiled into shipping builds."),ECVF_Default);
#endif
URPGFrameworkMoveExecutor::URPGFrameworkMoveExecutor()
{
    PrimaryComponentTick.bCanEverTick=true; PrimaryComponentTick.bStartWithTickEnabled=false;
    PrimaryComponentTick.TickGroup=TG_PostPhysics;
}
bool URPGFrameworkMoveExecutor::ValidatePlaybackCard(const TSharedPtr<const FRPGCompiledBossMoveCard>& C,FString& Error,bool bDamage)
{
    Error.Reset();
    if (!C||!C->HasResolvedAssets()) {Error=TEXT("Framework.Playback.UnresolvedPreview");return false;}
    if (!RPGBossMoveCards::Validate(C->Spec(),C->Metadata()).IsValid()||!C->Spec().Montage.IsNull()||C->Spec().Sequence.IsNull()||!C->Spec().SectionName.IsNone()||((bDamage&&!C->Spec().bDefensive)?!(C->Spec().HPDamage>0.f):C->Spec().HPDamage!=0.f))
    {Error=TEXT("Framework.Playback.SequenceTelemetryOnly");return false;}
    return true;
}
bool URPGFrameworkMoveExecutor::Initialize(ARPGFrameworkBossCharacter* Boss,const FRPGFrameworkDependencies& D,APawn* InTarget,uint64 Encounter,uint64 Generation,FString& Error)
{
    const TSharedPtr<const FRPGCompiledBossMoveCard> First=D.Candidates.Num()>0?D.Candidates[0].Card:D.Card;
    if (!ValidatePlaybackCard(First,Error,D.Profile.IsValid()&&D.Profile->bDamageEnabled)) return false;
    if (bInitialized||!IsInGameThread()||!IsValid(Boss)||GetOwner()!=Boss||!IsValid(InTarget)||Boss==InTarget||Boss->GetWorld()!=InTarget->GetWorld()||!D.Profile.IsValid())
    {Error=TEXT("Framework.Playback.OwnerTarget");return false;}
    UAnimInstance* Instance=Boss->GetMesh()->GetAnimInstance();
    if (!IsValid(Instance)||Instance->GetClass()!=D.AnimClass.Get()||!RPGFramework::HasSlotNode(Instance,First->Spec().SlotName))
    {Error=TEXT("Framework.Playback.SlotGraph");return false;}
    if (!Model_.Initialize(Encounter,Generation,Error)) return false;
    OwnerBoss=Boss; Target=InTarget; Card=First; Profile=D.Profile.Get(); Anim=Instance; bInitialized=true;
    AddTickPrerequisiteComponent(Boss->GetMesh()); SetComponentTickEnabled(true);
    if (Profile->bDamageEnabled)
    {
        // Single life/generation authority of the framework boss: alive until the boss fails; generation = the proof generation.
        URPGDamageResolver* R=URPGDamageResolver::FindOrAdd(Boss);
        if (!IsValid(R)) {Error=TEXT("Framework.Playback.Resolver");return false;}
        R->SetLifeProvider([W=TWeakObjectPtr<ARPGFrameworkBossCharacter>(Boss)]{return W.IsValid()&&!W->Failed()&&!W->IsDead();},[W=TWeakObjectPtr<ARPGFrameworkBossCharacter>(Boss)]{return W.IsValid()?int32(W->CurrentGeneration()):0;});
        Resolver=R;
    }
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] slot_graph name=%s nodeClass=AnimNode_Slot verified=1 label=%s"),*Card->Spec().SlotName.ToString(),*Label());
    return true;
}
bool URPGFrameworkMoveExecutor::Start(const FRPGBossDecisionSnapshot& S,FString& Error)
{
    return StartCard(Card,S,Error);
}
bool URPGFrameworkMoveExecutor::Rearm(uint64 NewGeneration,FString& Error)
{
    if (!bInitialized||!IsInGameThread()) {Error=TEXT("Framework.Playback.State");return false;}
    StopOwned(0.f); OwnedMontage=nullptr;
    TArray<FRPGBossMoveModelEvent> Events;
    if (!Model_.ResetGeneration(NewGeneration,Events,Error)) return false;
    LogEvents(Events);
    bAborted=false; bFinished=false; bWatchdogFired=false; bSuppressDone=false; bSawPoseWeight=false; LastPosition=0.; PrevPoses.Reset(); bGrabUsed=false; WarpMovedCm=WarpTurnedDeg=0.; WarpEaseDistanceCm=0.; bWarpEaseDistanceSet=false; bWarpEaseLogged=false; bWarpSummaryLogged=false; Token=FRPGBossAttackToken();
    SetComponentTickEnabled(false);
    return true;
}
bool URPGFrameworkMoveExecutor::RecoverAfterAbort()
{
    if (!bInitialized||!bAborted||bFinished||!IsIdle()) return false;
    bAborted=false; bFinished=false; bWatchdogFired=false; bSawPoseWeight=false; LastPosition=0.; PrevPoses.Reset(); bGrabUsed=false; WarpMovedCm=WarpTurnedDeg=0.; WarpEaseDistanceCm=0.; bWarpEaseDistanceSet=false; bWarpEaseLogged=false; bWarpSummaryLogged=false; Token=FRPGBossAttackToken();
    SetComponentTickEnabled(false);
    return true;
}
bool URPGFrameworkMoveExecutor::PrepareNextAttack()
{
    if (!bInitialized||bAborted||!bFinished||!IsIdle()) return false;
    bFinished=false; bSawPoseWeight=false; LastPosition=0.; PrevPoses.Reset(); bGrabUsed=false; WarpMovedCm=WarpTurnedDeg=0.; WarpEaseDistanceCm=0.; bWarpEaseDistanceSet=false; bWarpEaseLogged=false; bWarpSummaryLogged=false;
    return true;
}
bool URPGFrameworkMoveExecutor::StartCard(const TSharedPtr<const FRPGCompiledBossMoveCard>& NextCard,const FRPGBossDecisionSnapshot& S,FString& Error)
{
    if (!NextCard) {Error=TEXT("Framework.Playback.State");return false;}
    Card=NextCard;
    if (!bInitialized||bAborted||!OwnerBoss.IsValid()||!Target.IsValid()||!IsIdle()||bFinished)
    {Error=TEXT("Framework.Playback.State");return false;}
    if (!ValidatePlaybackCard(Card,Error,Profile->bDamageEnabled)||!Model_.IsEligible(Card,S,Error)) return false;
    // BOSS-EXE-007: the watchdog budget of this card. A healthy card must end inside it, otherwise the watchdog would abort it: refuse such a card here, named.
    CardWatchdogTimeoutSeconds=RPGBossTrack::WatchdogTimeoutSeconds(Card->Spec().RecoveryEndSeconds,Card->Spec().PlayRate);
    if (CardWatchdogTimeoutSeconds>=0.&&Card->Spec().HoldMaxSeconds>0.f) CardWatchdogTimeoutSeconds+=double(Card->Spec().HoldMaxSeconds);   // BOSS-ANM-003: the watchdog allows the longest hold
    if (CardWatchdogTimeoutSeconds<0.||(double(Card->Metadata().ClipLengthSeconds)-double(Profile->BlendOutSeconds))/double(Card->Spec().PlayRate)>CardWatchdogTimeoutSeconds) {Error=TEXT("Framework.Playback.WatchdogWindow");return false;}
    bWatchdogFired=false; bSuppressLogged=false; bHoldActive=bHoldDone=false; CuesFiredMask=0; PreloadCues();
    // Loaded dependency only. No Resolve/Load call or alternate animation path in the playback consumer.
    SetComponentTickEnabled(true);
    UAnimSequence* Sequence=Card->Spec().Sequence.Get();
    if (!IsValid(Sequence)||!IsValid(Anim)||OwnerBoss->GetMesh()->GetAnimInstance()!=Anim)
    {Error=TEXT("Framework.Playback.DependencyDrift");return false;}
    // BOSS-EXE-002: the attack instance is reserved BEFORE playback; a failed play aborts that instance.
    TArray<FRPGBossMoveModelEvent> Events;
    if (!Model_.Start(Card,S,Token,Events,Error)) return false;
    LogEvents(Events);
    OwnedMontage=Anim->PlaySlotAnimationAsDynamicMontage(Sequence,Card->Spec().SlotName,Profile->BlendInSeconds,Profile->BlendOutSeconds,Card->Spec().PlayRate,1,-1.f,0.f);
    if (!OwnedMontage) {Error=TEXT("Framework.Playback.StartFailed");Abort(Error);return false;}
    if (!Model_.AdvanceObservedLocal(Token,0.,Events,Error)) {Abort(Error);return false;}
    StartWorldSeconds=LastWorldSeconds=GetWorld()->GetTimeSeconds(); LastPosition=0.; bSawPoseWeight=false;
    TrackTurned=TrackMaxRate=TrackDriftMax=0.; TrackYawAtCommit=0.f; bTrackCommitLogged=false; DecisionRangeCm=S.RangeCm; DecisionYawDeg=S.SignedYawDegrees;
#if !UE_BUILD_SHIPPING
    if (CVarBossProofStaleCallback.GetValueOnGameThread()>0&&LastAbortedToken.InstanceId&&!(LastAbortedToken==Token))
    {
        TArray<FRPGBossMoveModelEvent> StaleEvents; FString StaleError; const bool bAccepted=Model_.Abort(LastAbortedToken,StaleEvents,StaleError);
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] stale_callback oldInstance=%llu newInstance=%llu refused=%d error=%s newAttackAlive=%d"),LastAbortedToken.InstanceId,Token.InstanceId,bAccepted?0:1,*StaleError,Model_.AcceptsCallback(Token)?1:0);
        LastAbortedToken=FRPGBossAttackToken();
    }
#endif
    LockMotion(); bIntruderDone=false; bIntruderPending=false;
    UE_LOG(LogTemp,Display,TEXT("[CARD_START] instance=%llu card=%s family=%s phase=%s rangeCm=%g"),Token.InstanceId,*Card->Spec().MoveId.ToString(),*Card->Spec().FamilyId.ToString(),*Card->Spec().PhaseId.ToString(),S.RangeCm);
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
    // BOSS-EXE-007 / ANM-007 watchdog: a card still running after RecoveryEndSeconds / PlayRate + 0.5 s (end notification dropped, montage stuck) is aborted; the boss recovers and decides again.
    if (Now-StartWorldSeconds>CardWatchdogTimeoutSeconds)
    {
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] watchdog_timeout instance=%llu elapsedSeconds=%g timeoutSeconds=%g recoveryEndSeconds=%g playRate=%g"),Token.InstanceId,Now-StartWorldSeconds,CardWatchdogTimeoutSeconds,double(Card->Spec().RecoveryEndSeconds),double(Card->Spec().PlayRate));
        bWatchdogFired=true; Abort(TEXT("Framework.Playback.WatchdogTimeout")); return;
    }
#if !UE_BUILD_SHIPPING
    if (CVarBossProofSuppressMontageEnd.GetValueOnGameThread()>0&&LastPosition>=0.3&&(bSuppressLogged||!bSuppressDone))
    {
        if (!bSuppressLogged) {bSuppressLogged=true; bSuppressDone=true; UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] montage_end_suppressed instance=%llu position=%g"),Token.InstanceId,LastPosition);}
        return;
    }
#endif
    if (Model_.State()==ERPGBossMoveModelState::Idle)
    {
        if (!Anim->Montage_IsActive(OwnedMontage))
        {
            if (bTrackCommitLogged) UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] heading_locked instance=%llu yawAtCommit=%g maxDriftAfterCommitDegrees=%g"),Token.InstanceId,double(TrackYawAtCommit),TrackDriftMax);
            ReleaseGrab(TEXT("CardEnded"),true);
            UnlockMotion(TEXT("Finished")); ++CleanupLogCount;
            UE_LOG(LogTemp,Display,TEXT("[CARD_END] instance=%llu card=%s reason=Finished hitsAccepted=%d appliedDamage=%g"),Token.InstanceId,*Card->Spec().MoveId.ToString(),HitsAccepted,AppliedDamage);
            OwnedMontage=nullptr;bFinished=true;SetComponentTickEnabled(false);UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] cleanup reason=Finished modelIdle=1 ownedMontageStopped=1"));
        }
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
    TickHold(Position,Now);
#if !UE_BUILD_SHIPPING
    {
        // BOSS-ANM-005 test hook: a navigation request is sent mid-card; 0.4 s later the displacement is logged (the lock must have refused it).
        const float At=CVarBossProofMotionIntruder.GetValueOnGameThread();
        if (At>=0.f&&!bIntruderDone&&Position>=double(At))
        {
            bIntruderDone=true; bIntruderPending=true; IntruderAt=Now; IntruderFrom=OwnerBoss->GetActorLocation();
            AAIController* AI=Cast<AAIController>(OwnerBoss->GetController());
            const EPathFollowingRequestResult::Type R=AI?AI->MoveToLocation(IntruderFrom+OwnerBoss->GetActorForwardVector()*600.,5.f,false,true,false,false):EPathFollowingRequestResult::Failed;
            UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] motion_intruder state=Requested instance=%llu requestResult=%d locked=%d"),Token.InstanceId,int32(R),bMotionLocked?1:0);
        }
        if (bIntruderPending&&Now-IntruderAt>=.4)
        {
            bIntruderPending=false;
            UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] motion_intruder state=Result instance=%llu movedCm=%g locked=%d"),Token.InstanceId,FVector::Dist2D(IntruderFrom,OwnerBoss->GetActorLocation()),bMotionLocked?1:0);
        }
    }
#endif
    if (bPlaying&&((!bSawPoseWeight&&Now-StartWorldSeconds>Profile->BlendInSeconds)||((Node<=0.f||Weight<=0.f)&&Position>=Card->Spec().ActiveStartSeconds)))
    {Fail(TEXT("Framework.Playback.NoSlotContribution"));return;}
    if (!bPlaying) UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] montage_natural_end instance=%llu lastPosition=%g naturalEnd=%g"),Token.InstanceId,LastPosition,NaturalEnd);
    {
        // BOSS-ANM-004: the pure rule (RPGBossTrack::StepYaw) turns at most the card's TrackDegreesPerSecond until the heading is committed, then the yaw is locked.
        const bool bCommitted=Model_.HeadingCommitted();
        const float YawBefore=OwnerBoss->GetActorRotation().Yaw;
        if (!bCommitted)
        {
            const FVector D=Target->GetActorLocation()-OwnerBoss->GetActorLocation();
            const float Yaw=RPGBossTrack::StepYaw(YawBefore,D.Rotation().Yaw,Card->Spec().TrackDegreesPerSecond,Delta,false);
            OwnerBoss->SetActorRotation(FRotator(0.f,Yaw,0.f));
            const double Step=FMath::Abs(FMath::FindDeltaAngleDegrees(YawBefore,Yaw)); TrackTurned+=Step; if (Delta>0.f) TrackMaxRate=FMath::Max(TrackMaxRate,Step/double(Delta));
        }
        else
        {
            if (!bTrackCommitLogged)
            {
                bTrackCommitLogged=true; TrackYawAtCommit=YawBefore;
                UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] heading_commit instance=%llu yaw=%g turnedDegrees=%g maxRateDegPerSec=%g capDegPerSec=%g decisionRangeCm=%g liveRangeCm=%g decisionYawDeg=%g liveYawDeg=%g"),Token.InstanceId,double(YawBefore),TrackTurned,TrackMaxRate,double(Card->Spec().TrackDegreesPerSecond),DecisionRangeCm,FVector::Dist2D(OwnerBoss->GetActorLocation(),Target->GetActorLocation()),DecisionYawDeg,double(FMath::FindDeltaAngleDegrees(OwnerBoss->GetActorRotation().Yaw,(Target->GetActorLocation()-OwnerBoss->GetActorLocation()).Rotation().Yaw)));
            }
            TrackDriftMax=FMath::Max(TrackDriftMax,double(FMath::Abs(FMath::FindDeltaAngleDegrees(TrackYawAtCommit,YawBefore))));
        }
    }
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] playback instance=%llu position=%g nodeWeight=%g montageWeight=%g base=%s tip=%s"),Token.InstanceId,Position,Node,Weight,*OwnerBoss->GetMesh()->GetSocketLocation(TEXT("weapon_r")).ToString(),*OwnerBoss->GetMesh()->GetSocketLocation(TEXT("root_weapon_end_r")).ToString());
    const double PrevPosition=LastPosition; LastPosition=Position; TArray<FRPGBossMoveModelEvent> Events; FString Error;
    if (!Model_.AdvanceObservedLocal(Token,Position,Events,Error)) {LogEvents(Events);Fail(*Error);return;}
    LogEvents(Events);
    TickWarp(PrevPosition,Position);
    SweepWindows(PrevPosition,Position);
    TickGrab(Position);
    TickCues(PrevPosition,Position);
    if (Model_.State()==ERPGBossMoveModelState::Idle) StopOwned(Profile->BlendOutSeconds);
}
void URPGFrameworkMoveExecutor::SweepWindows(double PrevPosition,double Position)
{
    if (!Profile->bDamageEnabled||!Resolver.IsValid()||!Target.IsValid()||!OwnerBoss.IsValid()) return;
    USkeletalMeshComponent* Mesh=OwnerBoss->GetMesh();
    // BOSS-HIT-010: the direct windows are swept first, the secondary ones (splash) after them in the same tick: with a shared hit group the direct hit is applied and a simultaneous splash is refused as a duplicate.
    TArray<const FRPGBossMoveWindow*> Ordered; for (const FRPGBossMoveWindow& D:Card->Spec().Windows) if (!D.bSecondary) Ordered.Add(&D); for (const FRPGBossMoveWindow& D:Card->Spec().Windows) if (D.bSecondary) Ordered.Add(&D);
    // The hit application is shared by the blade windows and the ring windows (BOSS-HIT-011): the same payload, the same resolver, the same hit key.
    auto ApplyHit=[&](const FRPGBossMoveWindow& W)
    {
        FRPGDamagePayload Payload;
        Payload.MoveId=Card->Spec().MoveId; Payload.AttackInstance=int32(Token.InstanceId); Payload.Generation=int32(Token.Generation);
        Payload.HitKey=W.HitGroup.IsNone()?W.WindowId:W.HitGroup; Payload.HPDamage=Card->Spec().HPDamage;
        const bool bBlocking=RPGBossDamage::HasTag(Target.Get(),TEXT("Status.Blocking"));   // read BEFORE the damage: the guard of the moment of contact
        const FRPGDamageResult Result=Resolver->Resolve(Target.Get(),Payload);
        const RPGBossGuard::EGuardState Guard=RPGBossGuard::Classify(bBlocking,Result.Outcome==ERPGDamageOutcome::Parried);   // the parry window is decided by the resolver
        if (Result.Outcome==ERPGDamageOutcome::Accepted) {++HitsAccepted; AppliedDamage+=Result.HPApplied; if (Guard==RPGBossGuard::EGuardState::Guarded) ++HitsGuarded; if (OwnerBoss.IsValid()) OwnerBoss->NoteDamageApplied(Result.HPApplied);}
        else if (Result.Outcome==ERPGDamageOutcome::Parried) {++HitsParried; if (OwnerBoss.IsValid()) RecordParriedContact(OwnerBoss.Get(),Target.Get());}
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] guard_state instance=%llu window=%s guard=%s outcome=%s"),Token.InstanceId,*W.WindowId.ToString(),RPGBossGuard::Name(Guard),*UEnum::GetValueAsString(Result.Outcome));
        UE_LOG(LogTemp,Display,TEXT("[CARD_HIT] instance=%llu card=%s window=%s outcome=%s hpApplied=%g"),Token.InstanceId,*Card->Spec().MoveId.ToString(),*W.WindowId.ToString(),*UEnum::GetValueAsString(Result.Outcome),Result.HPApplied);
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] hit instance=%llu window=%s key=%s outcome=%s hpApplied=%g healthBefore=%g healthAfter=%g"),Token.InstanceId,*W.WindowId.ToString(),*Payload.HitKey.ToString(),*UEnum::GetValueAsString(Result.Outcome),Result.HPApplied,Result.HealthBefore,Result.HealthAfter);
    };
    for (const FRPGBossMoveWindow* WP:Ordered)
    {
        const FRPGBossMoveWindow& W=*WP;
        if (W.bRing)
        {
            // BOSS-HIT-011: the band covered by the front during THIS tick, around the boss; no sockets, no capsule sweep.
            const double Lo=FMath::Max(PrevPosition,double(W.StartSeconds)), Hi=FMath::Min(Position,double(W.EndSeconds));
            if (Position<=PrevPosition||Hi<=Lo) continue;
            const double FrontLo=RPGBossTrack::RingFront(W.RingStartRadiusCm,W.RingSpeedCmPerSecond,Lo-W.StartSeconds), FrontHi=RPGBossTrack::RingFront(W.RingStartRadiusCm,W.RingSpeedCmPerSecond,Hi-W.StartSeconds);
            const double Dist=FVector::Dist2D(Target->GetActorLocation(),OwnerBoss->GetActorLocation());
            FVector TO,TE,BO,BE; Target->GetActorBounds(true,TO,TE); OwnerBoss->GetActorBounds(true,BO,BE);
            const double DzAbs=FMath::Abs((TO.Z-TE.Z)-(BO.Z-BE.Z));
            const double TargetRadius=Target->IsA<ACharacter>()?double(Cast<ACharacter>(Target.Get())->GetCapsuleComponent()->GetScaledCapsuleRadius()):double(FMath::Max(TE.X,TE.Y));
            const bool bTouch=RPGBossTrack::RingTouches(FrontLo,FrontHi,W.RingThicknessCm,Dist,TargetRadius,DzAbs,W.RingHeightCm);
            UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] ring_sweep instance=%llu window=%s from=%g to=%g frontLoCm=%g frontHiCm=%g thicknessCm=%g targetDistCm=%g targetRadiusCm=%g dzCm=%g heightCm=%g contact=%d"),Token.InstanceId,*W.WindowId.ToString(),Lo,Hi,FrontLo,FrontHi,double(W.RingThicknessCm),Dist,TargetRadius,DzAbs,double(W.RingHeightCm),bTouch?1:0);
            if (bTouch) ApplyHit(W);
            continue;
        }
        // The sockets are read live every tick: the blade is not rigid (measured 67..123 cm base-to-tip over the clip).
        const FVector A=Mesh->GetSocketLocation(W.SocketA), B=Mesh->GetSocketLocation(W.SocketB);
        FWindowPose& Prev=PrevPoses.FindOrAdd(W.WindowId);
        const bool bHad=Prev.bValid; const FVector PA=Prev.A, PB=Prev.B;
        Prev.A=A; Prev.B=B; Prev.bValid=true;
        FRPGSweepPose PrevTick; PrevTick.A=PA; PrevTick.B=PB; FRPGSweepPose CurrentTick; CurrentTick.A=A; CurrentTick.B=B;
        TArray<FRPGSweepPose> Keys; bool bBaked=false; double Lo=0., Hi=0.;
        if (!bHad||!RPGBossSweep::BuildKeyPoses(W,PrevPosition,Position,PrevTick,CurrentTick,Keys,bBaked,Lo,Hi)) continue;
        // Baked poses are component space: the component transform of THIS tick puts them in the world (the heading is fixed after the commit time, before any window).
        if (bBaked) { const FTransform Xf=Mesh->GetComponentTransform(); for (FRPGSweepPose& K:Keys) { K.A=Xf.TransformPosition(K.A); K.B=Xf.TransformPosition(K.B); } }
        else
        {
            // Live sockets: only the part of this tick the window was open, subdivided by tip distance (profile step and cap), each substep one swept capsule.
            const FRPGSweepPose First=Keys[0], Last=Keys.Last();
            const double TipDistance=FVector::Dist(First.B,Last.B);
            const int32 Wanted=FMath::Max(1,FMath::CeilToInt(float(TipDistance/Profile->HitStepCm))), Substeps=FMath::Min(Wanted,Profile->HitMaxSubsteps);
            Keys.Reset();
            for (int32 I=0;I<=Substeps;++I) { const double F=double(I)/Substeps; FRPGSweepPose K; K.A=FMath::Lerp(First.A,Last.A,F); K.B=FMath::Lerp(First.B,Last.B,F); Keys.Add(K); }
        }
        double TipDistance=0.; for (int32 I=1;I<Keys.Num();++I) TipDistance+=FVector::Dist(Keys[I-1].B,Keys[I].B);
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] sweep instance=%llu window=%s from=%g to=%g tipDistanceCm=%g substeps=%d clamped=0 baked=%d"),Token.InstanceId,*W.WindowId.ToString(),Lo,Hi,TipDistance,Keys.Num()-1,bBaked?1:0);
        FCollisionQueryParams Params(SCENE_QUERY_STAT(FrameworkSweep),false,OwnerBoss.Get());
        const FCollisionObjectQueryParams Objects(ECC_Pawn);
        bool bContact=false; TSet<const AActor*> IgnoredPawns; FString FirstIgnored;   // BOSS-HIT-005: pawns the sweep touched that are not the target
        for (int32 I=1;I<Keys.Num()&&!bContact;++I)
        {
            // Each pair of consecutive key poses is one swept capsule, so the chain has no gaps even across a long frame.
            const FVector PoseA0=Keys[I-1].A, PoseB0=Keys[I-1].B, PoseA1=Keys[I].A, PoseB1=Keys[I].B;
            const FVector Axis=PoseB1-PoseA1; const double Length=Axis.Size();
            if (Length<KINDA_SMALL_NUMBER) continue;
            const FQuat Rotation=FQuat::FindBetweenNormals(FVector::UpVector,Axis/Length);
            const FCollisionShape Shape=FCollisionShape::MakeCapsule(W.RadiusCm,float(Length*.5)+W.RadiusCm);
            TArray<FHitResult> Hits;
            GetWorld()->SweepMultiByObjectType(Hits,(PoseA0+PoseB0)*.5,(PoseA1+PoseB1)*.5,Rotation,Objects,Shape,Params);
            for (const FHitResult& H:Hits)
            {
                if (H.GetActor()==Target.Get()) bContact=true;
                else if (const AActor* Other=H.GetActor()) { bool bAlready=false; IgnoredPawns.Add(Other,&bAlready); if (!bAlready&&FirstIgnored.IsEmpty()) FirstIgnored=Other->GetName(); }
            }
        }
        // Only logged when something was filtered, so the logs of every earlier scenario are unchanged. The boss itself is excluded by the query params and never appears here.
        if (IgnoredPawns.Num()>0) UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] sweep_filter instance=%llu window=%s ignoredPawns=%d first=%s targetContact=%d selfHits=%d"),Token.InstanceId,*W.WindowId.ToString(),IgnoredPawns.Num(),*FirstIgnored,bContact?1:0,IgnoredPawns.Contains(OwnerBoss.Get())?1:0);
        if (!bContact) continue;
        if (W.bGrab) { if (!bGrabUsed&&!Grab.bHeld) BeginGrab(W); continue; }   // BOSS-HIT-012: the contact catches, the damage comes at the release
        ApplyHit(W);
    }
}
void URPGFrameworkMoveExecutor::BeginGrab(const FRPGBossMoveWindow& W)
{
    // BOSS-HIT-012: the victim is the explicit target, caught once per card. Movement off and the capsule out of the way while it rides the boss's socket; the saved values come back on release.
    ACharacter* Victim=Cast<ACharacter>(Target.Get()); USkeletalMeshComponent* Mesh=OwnerBoss.IsValid()?OwnerBoss->GetMesh():nullptr;
    if (!Victim||!Mesh||Victim->GetCharacterMovement()==nullptr||Victim->GetCapsuleComponent()==nullptr) return;
    if (RPGBossTrack::GrabStep(Grab,true,LastPosition,double(W.GrabReleaseSeconds),false)!=RPGBossTrack::EGrabEvent::Caught) return;
    bGrabUsed=true; GrabWindowId=W.WindowId; GrabHitKey=W.HitGroup.IsNone()?W.WindowId:W.HitGroup; GrabReleaseAt=W.GrabReleaseSeconds;
    UCharacterMovementComponent* Move=Victim->GetCharacterMovement(); UCapsuleComponent* Capsule=Victim->GetCapsuleComponent();
    const FString Before=UEnum::GetValueAsString(Move->MovementMode.GetValue());
    HeldCapsuleCollision=Capsule->GetCollisionEnabled(); Held=Victim;
    Move->StopMovementImmediately(); Move->DisableMovement(); Capsule->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Victim->AttachToComponent(Mesh,FAttachmentTransformRules::SnapToTargetNotIncludingScale,W.GrabAttachSocket);
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] grab_catch instance=%llu window=%s socket=%s releaseAt=%g modeBefore=%s modeHeld=%s attached=%d"),Token.InstanceId,*W.WindowId.ToString(),*W.GrabAttachSocket.ToString(),double(W.GrabReleaseSeconds),*Before,*UEnum::GetValueAsString(Move->MovementMode.GetValue()),Victim->GetAttachParentActor()==OwnerBoss.Get()?1:0);
}
void URPGFrameworkMoveExecutor::ReleaseGrab(const TCHAR* Reason,bool bInterrupted)
{
    // BOSS-HIT-012: put the victim back on the floor, upright, walking, collidable, with no attachment and no velocity, whatever ended the hold. Once per hold (Held is cleared first).
    ACharacter* Victim=Held.Get(); Held.Reset(); Grab=RPGBossTrack::FGrabState();
    if (!Victim) return;
    ++ReleaseLogCount;
    UCharacterMovementComponent* Move=Victim->GetCharacterMovement(); UCapsuleComponent* Capsule=Victim->GetCapsuleComponent();
    Victim->DetachFromActor(FDetachmentTransformRules::KeepWorldTransform);
    FVector Where=Victim->GetActorLocation(); const double Half=Capsule?Capsule->GetScaledCapsuleHalfHeight():0.;
    // The floor under the victim; when the socket put it inside the floor (no hit from above) the boss's own feet are the floor.
    FHitResult Floor; FCollisionQueryParams Params(SCENE_QUERY_STAT(GrabFloor),false,Victim); if (OwnerBoss.IsValid()) Params.AddIgnoredActor(OwnerBoss.Get());
    double FloorZ=0.; const bool bFloor=GetWorld()->LineTraceSingleByChannel(Floor,Where+FVector(0.,0.,Half+50.),Where-FVector(0.,0.,5000.),ECC_Visibility,Params);
    if (bFloor) FloorZ=Floor.ImpactPoint.Z; else if (OwnerBoss.IsValid()) { FVector BO,BE; OwnerBoss->GetActorBounds(true,BO,BE); FloorZ=BO.Z-BE.Z; }
    Where.Z=RPGBossTrack::GroundedZ(FloorZ,Half,2.);
    Victim->SetActorLocationAndRotation(Where,FRotator(0.,Victim->GetActorRotation().Yaw,0.),false,nullptr,ETeleportType::TeleportPhysics);
    if (Capsule) Capsule->SetCollisionEnabled(HeldCapsuleCollision);
    if (Move) { Move->StopMovementImmediately(); Move->SetMovementMode(MOVE_Walking); }
    FVector O,E; Victim->GetActorBounds(true,O,E);
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] grab_release instance=%llu reason=%s interrupted=%d attached=%d mode=%s floorFound=%d floorZ=%g feetZ=%g gapCm=%g"),Token.InstanceId,Reason,bInterrupted?1:0,Victim->GetAttachParentActor()?1:0,Move?*UEnum::GetValueAsString(Move->MovementMode.GetValue()):TEXT("none"),bFloor?1:0,FloorZ,O.Z-E.Z,(O.Z-E.Z)-FloorZ);
}
void URPGFrameworkMoveExecutor::TickGrab(double Position)
{
    if (!Grab.bHeld) return;
    // A victim that was destroyed while held is lost: nothing to put back (a stale weak pointer makes ReleaseGrab a no-op).
    const bool bLost=!Held.IsValid()||Held->IsActorBeingDestroyed();
    const RPGBossTrack::EGrabEvent Event=RPGBossTrack::GrabStep(Grab,false,Position,0.,bLost);
    if (Event==RPGBossTrack::EGrabEvent::Released)
    {
        // The normal end of the hold: the damage of the card, once, with the hit key of the grab window, then the release.
        if (Resolver.IsValid()&&Target.IsValid())
        {
            FRPGDamagePayload Payload; Payload.MoveId=Card->Spec().MoveId; Payload.AttackInstance=int32(Token.InstanceId); Payload.Generation=int32(Token.Generation); Payload.HitKey=GrabHitKey; Payload.HPDamage=Card->Spec().HPDamage;
            const bool bBlocking=RPGBossDamage::HasTag(Target.Get(),TEXT("Status.Blocking"));
            const FRPGDamageResult Result=Resolver->Resolve(Target.Get(),Payload);
            const RPGBossGuard::EGuardState Guard=RPGBossGuard::Classify(bBlocking,Result.Outcome==ERPGDamageOutcome::Parried);
            if (Result.Outcome==ERPGDamageOutcome::Accepted) {++HitsAccepted; AppliedDamage+=Result.HPApplied; if (Guard==RPGBossGuard::EGuardState::Guarded) ++HitsGuarded; if (OwnerBoss.IsValid()) OwnerBoss->NoteDamageApplied(Result.HPApplied);}
            else if (Result.Outcome==ERPGDamageOutcome::Parried) {++HitsParried; if (OwnerBoss.IsValid()) RecordParriedContact(OwnerBoss.Get(),Target.Get());}
            UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] grab_damage instance=%llu key=%s outcome=%s hpApplied=%g"),Token.InstanceId,*GrabHitKey.ToString(),*UEnum::GetValueAsString(Result.Outcome),Result.HPApplied);
        }
        ReleaseGrab(TEXT("Released"),false);
    }
    else if (Event==RPGBossTrack::EGrabEvent::Interrupted) ReleaseGrab(TEXT("VictimLost"),true);
}
void URPGFrameworkMoveExecutor::TickWarp(double PrevPosition,double Position)
{
    const FRPGBossMoveCardSpec& S=Card->Spec();
    if (!(S.WarpMaxDistanceCm>0.f||S.WarpMaxAngleDegrees>0.f)||!OwnerBoss.IsValid()||!Target.IsValid()) return;
    const double Lo=FMath::Max(PrevPosition,double(S.WarpStartSeconds)), Hi=FMath::Min(Position,double(S.WarpEndSeconds));
    if (Position<=PrevPosition||Hi<=Lo)
    {
        if (!bWarpSummaryLogged&&Position>=S.WarpEndSeconds&&PrevPosition>=S.WarpStartSeconds)
        {
            bWarpSummaryLogged=true;
            UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] warp_summary instance=%llu movedCm=%g maxDistanceCm=%g turnedDeg=%g maxAngleDeg=%g"),Token.InstanceId,WarpMovedCm,double(S.WarpMaxDistanceCm),WarpTurnedDeg,double(S.WarpMaxAngleDegrees));
        }
        return;
    }
    // What is still needed: the distance down to the standoff and the yaw to face the target, as of THIS tick (the target may have moved).
    const FVector Boss=OwnerBoss->GetActorLocation(); FVector ToTarget=Target->GetActorLocation()-Boss; ToTarget.Z=0.;
    const double Dist=ToTarget.Size(); if (Dist<KINDA_SMALL_NUMBER) return;
    // BOSS-DEF-005: a backstep (bWarpAway) walks AWAY from the target until it stands WarpStandoffCm away; every other warp closes on the target down to the standoff.
    const double NeededCm=S.bWarpAway?FMath::Max(0.,double(S.WarpStandoffCm)-Dist):FMath::Max(0.,Dist-double(S.WarpStandoffCm));
    const FVector WarpDir=S.bWarpAway?-ToTarget/Dist:ToTarget/Dist;
    const double YawBefore=OwnerBoss->GetActorRotation().Yaw, NeededDeg=FMath::FindDeltaAngleDegrees(YawBefore,ToTarget.Rotation().Yaw);
    const double Delta=Hi-Lo, SecondsLeft=double(S.WarpEndSeconds)-Lo;
    double StepCm=0.;
    if(S.WarpEaseInOut)
    {
        if(!bWarpEaseDistanceSet)
        {
            WarpEaseDistanceCm=FMath::Min(NeededCm,double(S.WarpMaxDistanceCm));
            bWarpEaseDistanceSet=true;
        }
        if(!bWarpEaseLogged)
        {
            bWarpEaseLogged=true;
            UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] warp_ease on=1"));
        }
        const double Duration=double(S.WarpEndSeconds)-double(S.WarpStartSeconds);
        const double T0=(Lo-double(S.WarpStartSeconds))/Duration;
        const double T1=(Hi-double(S.WarpStartSeconds))/Duration;
        const double EasedStep=RPGBossApproach::StepCm(WarpEaseDistanceCm,T0,T1);
        const double ClampStep=RPGBossTrack::WarpStepCm(NeededCm,double(S.WarpMaxDistanceCm)-WarpMovedCm,1.,1.);
        StepCm=FMath::Min(EasedStep,ClampStep);
    }
    else
    {
        StepCm=RPGBossTrack::WarpStepCm(NeededCm,double(S.WarpMaxDistanceCm)-WarpMovedCm,Delta,SecondsLeft);
    }
    const double StepDeg=RPGBossTrack::WarpStepDegrees(NeededDeg,double(S.WarpMaxAngleDegrees)-WarpTurnedDeg,Delta,SecondsLeft);
    // Swept: the boss does not walk through the target or a wall. The budget is charged with the distance the boss really moved (a blocked step costs less than it asked for).
    double ActualCm=0.;
    FHitResult WarpHit;
    if (StepCm>0.) { OwnerBoss->AddActorWorldOffset(WarpDir*StepCm,true,&WarpHit); ActualCm=FVector::Dist2D(Boss,OwnerBoss->GetActorLocation()); }
    // BOSS-MOV-004: a swept step that is stopped by a wall or another actor costs less than it asked for; the stop is logged with what blocked it and where the boss stands.
    if (StepCm>0.&&ActualCm<StepCm-0.5) UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] warp_blocked instance=%llu stepCm=%g actualCm=%g blocker=%s bossX=%g bossY=%g"),Token.InstanceId,StepCm,ActualCm,WarpHit.GetActor()?*WarpHit.GetActor()->GetName():TEXT("None"),OwnerBoss->GetActorLocation().X,OwnerBoss->GetActorLocation().Y);
    if (StepDeg!=0.) OwnerBoss->SetActorRotation(FRotator(0.,YawBefore+StepDeg,0.));
    WarpMovedCm+=ActualCm; WarpTurnedDeg+=FMath::Abs(StepDeg);
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] warp_step instance=%llu from=%g to=%g distCm=%g neededCm=%g stepCm=%g actualCm=%g movedCm=%g budgetCm=%g neededDeg=%g stepDeg=%g turnedDeg=%g budgetDeg=%g"),Token.InstanceId,Lo,Hi,Dist,NeededCm,StepCm,ActualCm,WarpMovedCm,double(S.WarpMaxDistanceCm),NeededDeg,StepDeg,WarpTurnedDeg,double(S.WarpMaxAngleDegrees));
}
void URPGFrameworkMoveExecutor::PreloadCues()
{
    // The sounds are loaded here, at the start of the card, never at the frame a cue fires.
    CueSounds.Reset(); for (const FRPGBossCue& C:Card->Spec().Cues) if (USoundBase* Sound=C.Sound.LoadSynchronous()) CueSounds.Add(Sound);
}
void URPGFrameworkMoveExecutor::TickHold(double Position,double Now)
{
    const FRPGBossMoveCardSpec& S=Card->Spec();
    if (!(S.HoldMaxSeconds>0.f)||!IsValid(OwnedMontage)) return;
    if (bHoldActive)
    {
        if (Now<HoldEndsAt) return;
        // The hold is over: the montage goes on at the card's rate, the release cues fire, the actual length is logged.
        Anim->Montage_SetPlayRate(OwnedMontage,S.PlayRate); bHoldActive=false; bHoldDone=true;
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] hold_release instance=%llu position=%g heldSeconds=%g chosenSeconds=%g minSeconds=%g maxSeconds=%g"),Token.InstanceId,Position,Now-HoldStartedAt,HoldChosen,double(S.HoldMinSeconds),double(S.HoldMaxSeconds));
        for (const FRPGBossCue& C:S.Cues) if (C.bAtHoldRelease) FireCue(C,TEXT("HoldRelease"));
        return;
    }
    if (bHoldDone||Position<double(S.HoldAtSeconds)) return;
    HoldChosen=RPGBossCue::HoldSeconds(S.HoldMinSeconds,S.HoldMaxSeconds,S.HoldSeed,++HoldsInRun);
    if (HoldChosen<0.) {bHoldDone=true;return;}
    Anim->Montage_SetPlayRate(OwnedMontage,0.f); bHoldActive=true; HoldStartedAt=Now; HoldEndsAt=Now+HoldChosen;
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] hold_start instance=%llu position=%g holdAtSeconds=%g chosenSeconds=%g minSeconds=%g maxSeconds=%g"),Token.InstanceId,Position,double(S.HoldAtSeconds),HoldChosen,double(S.HoldMinSeconds),double(S.HoldMaxSeconds));
}
void URPGFrameworkMoveExecutor::TickCues(double PrevPosition,double Position)
{
    const TArray<FRPGBossCue>& Cues=Card->Spec().Cues;
    for (int32 I=0;I<Cues.Num()&&I<31;++I)
    {
        const FRPGBossCue& C=Cues[I];
        if (C.bAtHoldRelease||(CuesFiredMask&(1<<I))||Position<double(C.TimeSeconds)) continue;
        CuesFiredMask|=(1<<I); FireCue(C,TEXT("Time"));
    }
}
void URPGFrameworkMoveExecutor::FireCue(const FRPGBossCue& Cue,const TCHAR* Why)
{
    // One cue: its visual (a flipbook sheet at the socket or at the boss's feet) and its sound, as the accessibility setting allows. Both channels exist for every cue (validated), so each mode still carries the cue.
    if (!OwnerBoss.IsValid()) return;
    const int32 Mode=CVarCueMode.GetValueOnGameThread(); const RPGBossCue::FChannels Channels=RPGBossCue::ChannelsFor(Mode);
    const USkeletalMeshComponent* Mesh=OwnerBoss->GetMesh();
    const FVector Where=(!Cue.Socket.IsNone()&&Mesh)?Mesh->GetSocketLocation(Cue.Socket):OwnerBoss->GetActorLocation()-FVector(0.,0.,double(OwnerBoss->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()));
    bool bVisual=false, bAudio=false;
    if (Channels.bVisual)
    {
        const ERPGEFlipbookKind Kind=Cue.Visual==ERPGBossCueVisual::DodgeDust?ERPGEFlipbookKind::DodgeDust:(Cue.Visual==ERPGBossCueVisual::BloodBurst?ERPGEFlipbookKind::BloodBurst:ERPGEFlipbookKind::HitSpark);
        if (ARPGFlipbookEffect* Effect=ARPGFlipbookEffect::Spawn(GetWorld(),Where,Kind,ARPGFlipbookEffect::LoadMaterial(Kind))) {Effect->SetActorScale3D(FVector(Channels.VisualScale)); bVisual=true;}
    }
    USoundBase* Sound=Cue.Sound.Get();
    if (Channels.bAudio&&Sound) {UGameplayStatics::PlaySoundAtLocation(this,Sound,Where); bAudio=true;}
    // BOSS-ANM-002: a cue that fires INSIDE the telegraph phase [0, CommitSeconds] is logged as such, before any hit window can open.
    if (LastPosition<double(Card->Spec().CommitSeconds)) UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] telegraph_cue instance=%llu cue=%s positionSeconds=%g commitSeconds=%g visual=%d audio=%d"),Token.InstanceId,*Cue.CueId.ToString(),LastPosition,double(Card->Spec().CommitSeconds),bVisual?1:0,bAudio?1:0);
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] cue_fired instance=%llu cue=%s why=%s mode=%d visual=%d audio=%d visualKind=%d visualScale=%g sound=%s"),Token.InstanceId,*Cue.CueId.ToString(),Why,Mode,bVisual?1:0,bAudio?1:0,int32(Cue.Visual),double(Channels.VisualScale),Sound?*Sound->GetName():TEXT("None"));
}
void URPGFrameworkMoveExecutor::LockMotion()
{
    // BOSS-ANM-005: one motion authority per attack. Navigation is stopped and the movement component is disabled for the whole card: only the executor (the bounded warp) moves the boss.
    if (bMotionLocked||!OwnerBoss.IsValid()) return;
    if (AController* AI=OwnerBoss->GetController()) AI->StopMovement();
    UCharacterMovementComponent* Move=OwnerBoss->GetCharacterMovement(); if (!Move) return;
    Move->StopMovementImmediately(); Move->DisableMovement(); bMotionLocked=true;
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] motion_lock state=Acquired instance=%llu mode=%s"),Token.InstanceId,*UEnum::GetValueAsString(Move->MovementMode.GetValue()));
}
void URPGFrameworkMoveExecutor::UnlockMotion(const TCHAR* Why)
{
    if (!bMotionLocked) return;
    bMotionLocked=false;
    if (!OwnerBoss.IsValid()) return;
    UCharacterMovementComponent* Move=OwnerBoss->GetCharacterMovement(); if (!Move) return;
    // A dead or failed boss stays down; every other end gives the walking back.
    if (!OwnerBoss->IsDead()&&!OwnerBoss->Failed()) Move->SetMovementMode(MOVE_Walking);
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] motion_lock state=Released instance=%llu why=%s mode=%s"),Token.InstanceId,Why,*UEnum::GetValueAsString(Move->MovementMode.GetValue()));
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
    ReleaseGrab(*Reason,true);   // BOSS-HIT-012: every abort (stagger, death, leash, watchdog, EndPlay, a failure) frees a held victim first
    TArray<FRPGBossMoveModelEvent> Events; FString Error;
    if (Token.InstanceId) {LastAbortedToken=Token; Model_.Abort(Token,Events,Error);}
    bAborted=true; LogEvents(Events); StopOwned(0.f); OwnedMontage=nullptr; SetComponentTickEnabled(false);
    UnlockMotion(*Reason); ++CleanupLogCount;
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] cleanup reason=%s modelIdle=%d ownedMontageStopped=1"),*Reason,Model_.State()==ERPGBossMoveModelState::Idle);
    UE_LOG(LogTemp,Display,TEXT("[CARD_ABORT] instance=%llu card=%s reason=%s"),Token.InstanceId,Card.IsValid()?*Card->Spec().MoveId.ToString():TEXT("None"),*Reason);
#if !UE_BUILD_SHIPPING
    if (CVarBossProofRepeatAbort.GetValueOnGameThread()>0&&!bInRepeatAbort)
    {
        // BOSS-EXE-006: abort again, N times: nothing may happen twice (no second cleanup, no second release, no second model event).
        bInRepeatAbort=true; const int32 Cleanups=CleanupLogCount, Releases=ReleaseLogCount; const int32 N=CVarBossProofRepeatAbort.GetValueOnGameThread();
        for (int32 I=0;I<N;++I) Abort(Reason);
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] abort_repeat reason=%s repeats=%d duplicateCleanups=%d duplicateReleases=%d modelIdle=%d"),*Reason,N,CleanupLogCount-Cleanups,ReleaseLogCount-Releases,Model_.State()==ERPGBossMoveModelState::Idle);
        bInRepeatAbort=false;
    }
#endif
}
bool URPGFrameworkMoveExecutor::IsIdle() const {return Model_.State()==ERPGBossMoveModelState::Idle&&!OwnedMontage;}
bool URPGFrameworkMoveExecutor::IsClean() const {return IsIdle();}
void URPGFrameworkMoveExecutor::EndPlay(const EEndPlayReason::Type Reason)
{Abort(TEXT("EndPlay"));Super::EndPlay(Reason);}
