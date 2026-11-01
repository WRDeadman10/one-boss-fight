// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "Components/ActorComponent.h"
#include "Player/RPGBossMoveModel.h"
#include "Player/RPGBossTrackRules.h"
#include "RPGFrameworkMoveExecutor.generated.h"
class ARPGFrameworkBossCharacter;
class APawn;
class ACharacter;
class UAnimInstance;
class UAnimMontage;
class URPGBossFrameworkProfile;
class URPGDamageResolver;
struct FRPGFrameworkDependencies;
UCLASS()
class ONEBOSSFIGHT_API URPGFrameworkMoveExecutor : public UActorComponent
{
    GENERATED_BODY()
public:
    URPGFrameworkMoveExecutor();
    static bool ValidatePlaybackCard(const TSharedPtr<const FRPGCompiledBossMoveCard>& Card,FString& Error,bool bDamage=false);
    bool Initialize(ARPGFrameworkBossCharacter* Boss,const FRPGFrameworkDependencies& Dependencies,APawn* Target,uint64 Encounter,uint64 Generation,FString& Error);
    bool Start(const FRPGBossDecisionSnapshot& Snapshot,FString& Error);
    /** F5: starts the card the selector chose (any resolved card of the profile); Start() plays the card given to Initialize. */
    bool StartCard(const TSharedPtr<const FRPGCompiledBossMoveCard>& NextCard,const FRPGBossDecisionSnapshot& Snapshot,FString& Error);
    /** After a clean finish: re-arms the executor for the next attack of the same encounter. */
    bool PrepareNextAttack();
    /** F8: after an Abort (stagger) in the SAME generation: clears the abort and the spent attack token so the next StartCard can run. False unless aborted, not finished and idle. */
    bool RecoverAfterAbort();
    /** Encounter restart (also after an abort): stops the owned montage, moves the model to the new generation and re-arms; Start* re-enables the tick. */
    bool Rearm(uint64 NewGeneration,FString& Error);
    const FRPGBossMoveModel& Model() const { return Model_; }
    /** BOSS-QA-001: the card of the attack in progress, null when idle. */
    const FRPGCompiledBossMoveCard* ActiveCard() const { return Model_.State()!=ERPGBossMoveModelState::Idle ? Card.Get() : nullptr; }
    void Abort(const FString& Reason);
    bool IsIdle() const;
    bool IsClean() const;
    bool DidFinish() const { return bFinished; }
    /** BOSS-EXE-007: true after the watchdog aborted the running card (cleared by RecoverAfterAbort / Rearm / StartCard). */
    bool WatchdogFired() const { return bWatchdogFired; }
    int32 AcceptedHits() const { return HitsAccepted; }
    double AppliedDamageTotal() const { return AppliedDamage; }
    virtual void TickComponent(float Delta,ELevelTick TickType,FActorComponentTickFunction* ThisTick) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
    void LogEvents(const TArray<FRPGBossMoveModelEvent>& Events) const;
    void StopOwned(float BlendSeconds);
    FString Label() const;
    /** F4: sweeps every card window over the part of this tick it was open and resolves a contact with the explicit target. */
    void SweepWindows(double PrevPosition,double Position);
    struct FWindowPose { FVector A=FVector::ZeroVector,B=FVector::ZeroVector; bool bValid=false; };
    TMap<FName,FWindowPose> PrevPoses;
    TWeakObjectPtr<URPGDamageResolver> Resolver;
    int32 HitsAccepted=0; double AppliedDamage=0.;
    TWeakObjectPtr<ARPGFrameworkBossCharacter> OwnerBoss;
    TWeakObjectPtr<APawn> Target;
    UPROPERTY(Transient) TObjectPtr<UAnimInstance> Anim;
    UPROPERTY(Transient) TObjectPtr<UAnimMontage> OwnedMontage;
    UPROPERTY(Transient) TObjectPtr<URPGBossFrameworkProfile> Profile;
    TSharedPtr<const FRPGCompiledBossMoveCard> Card;
    FRPGBossMoveModel Model_;
    FRPGBossAttackToken Token;
    bool bInitialized=false, bAborted=false, bFinished=false, bSawPoseWeight=false;
    double StartWorldSeconds=0., LastWorldSeconds=0., LastPosition=0.;
    /** BOSS-ANM-004 telemetry of the heading tracking of the running attack (log lines heading_commit / heading_locked). */
    double TrackTurned=0., TrackMaxRate=0., TrackDriftMax=0.; float TrackYawAtCommit=0.f; bool bTrackCommitLogged=false;
    FRPGBossAttackToken LastAbortedToken;   // BOSS-EXE-004 test hook: the token of the last aborted attack
    double CardWatchdogTimeoutSeconds=0.;   // BOSS-EXE-007: RPGBossTrack::WatchdogTimeoutSeconds of the running card
    bool bWatchdogFired=false, bSuppressLogged=false, bSuppressDone=false;   // bSuppressDone: the test hook acts on ONE card only
    /** BOSS-HIT-012: the grab. Held is the caught victim, the saved values are put back on release; bGrabUsed: one catch per card. */
    void BeginGrab(const FRPGBossMoveWindow& Window);
    void ReleaseGrab(const TCHAR* Reason,bool bInterrupted);
    void TickGrab(double Position);
    /** BOSS-ANM-006: the bounded warp of the running card: what it has used of its budgets so far. */
    void TickWarp(double PrevPosition,double Position);
    double WarpMovedCm=0., WarpTurnedDeg=0.; bool bWarpSummaryLogged=false;
    RPGBossTrack::FGrabState Grab; bool bGrabUsed=false; double GrabReleaseAt=0.; FName GrabWindowId; FName GrabHitKey;
    TWeakObjectPtr<ACharacter> Held; TEnumAsByte<ECollisionEnabled::Type> HeldCapsuleCollision=ECollisionEnabled::QueryAndPhysics;
    double DecisionYawDeg=0.;    // BOSS-AWR-002: the signed yaw to the target in the same decision snapshot
    double DecisionRangeCm=0.;   // BOSS-AWR-002: the range of the decision snapshot the running attack was started with
};
