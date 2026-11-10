// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "GameFramework/Character.h"
#include "Player/RPGBossTrackRules.h"
#include "Player/RPGBossFrameworkProfile.h"
#include "Player/RPGBleedRules.h"
#include "Player/RPGBossMoveSelector.h"
#include "Player/RPGBossStuckRules.h"
#include "Player/RPGBossStaggerAnimRules.h"
#include "Player/RPGNativeBossHealth.h"
#include "RPGFrameworkBossCharacter.generated.h"
class URPGFrameworkMoveExecutor;
class ARPGFrameworkProofFixture;
class UAnimMontage;
class UAnimSequence;
UCLASS()
class ONEBOSSFIGHT_API ARPGFrameworkBossCharacter : public ACharacter, public IRPGNativeBossHealth
{
    GENERATED_BODY()
public:
    ARPGFrameworkBossCharacter();
    bool InitializeProof(ARPGFrameworkProofFixture* Fixture,URPGBossFrameworkProfile* Profile,APawn* Target,uint64 Encounter,uint64 Generation,FString& Error);
#if WITH_EDITORONLY_DATA
    UFUNCTION(BlueprintCallable, Category = "Framework proof|Test")
#endif
    bool InitializeWithProfileForTest(URPGBossFrameworkProfile* Profile,APawn* Target,FString& Error);
#if WITH_EDITORONLY_DATA
    UFUNCTION(BlueprintCallable, Category = "Framework proof|Test")
#endif
    bool StartCardForTest(FName MoveId);
#if WITH_EDITORONLY_DATA
    UFUNCTION(BlueprintCallable, Category = "Framework proof|Test")
#endif
    bool StartComboForTest(FName RootMoveId);
#if WITH_EDITORONLY_DATA
    UFUNCTION(BlueprintCallable, Category = "Framework proof|Test", meta=(WorldContext="WorldContextObject"))
#endif
    static ARPGFrameworkBossCharacter* SpawnFrameworkBossForTest(UObject* WorldContextObject,TSubclassOf<ARPGFrameworkBossCharacter> CharacterClass,FVector Location,FRotator Rotation);
#if WITH_DEV_AUTOMATION_TESTS
    /** Initializes the real proof actor/target path for transient-world automation, omitting only the map-owned navigation request. */
#endif
    void WalkArrived();
    void Fail(const FString& Error);
    bool ValidateTarget(double& Health) const;
    /** BOSS-AWR-001: NAME_None when the target is valid, else Invalid, Destroyed, OffArena, Unreadable or Dead (checked in this order). */
    FName TargetFault(double& Health) const;
    /** BOSS-MOV-005: the target is outside the arena and the profile asks for a leash: abort the card, walk back to the arena centre, wait in neutral. */
    void HandleLeash();
    /** BOSS-AWR-005: vertical separation of the two FLOORS (feet to feet), not of the actor origins: a boss and a target with different capsule heights stand 0 cm apart on the same floor. */
    double FloorSeparationCm() const;
    APawn* ExplicitTarget() const {return Target.Get();}
    /** BOSS-AWR-001 / MOV-002 / MOV-005: the arena centre (authored in the profile, else where the target began). */
    FVector ArenaCentre() const {return ArenaOrigin;}
    /** BOSS-SEL-009: true from the end of the reaction delay of a perceived flask drink until the drink montage stops. */
    bool FlaskKnown() const {return bFlaskKnown;}
    const URPGBossFrameworkProfile* ProofProfile() const {return Dependencies?Dependencies->Profile.Get():nullptr;}
    int32 ConsecutiveWhiffs() const { return FatigueWhiffs; }
    bool Succeeded() const {return bSucceeded;}
    bool Failed() const {return bFailed;}
    /** F4: the executor reports every accepted hit so the target-health invariant expects exactly that loss. */
    void NoteDamageApplied(double Applied) {ExpectedTargetHP-=Applied;}
    /** The player parried a contact of this boss (called by the move executor): schedules the posture reaction of the profile (ParryPostureAmount) at the start of the next tick. */
    void NoteParried(double PostureScale=1.0,double RecoverySeconds=0.,int32 RecoveryGrade=0){
        const double SafeScale=FMath::IsFinite(PostureScale)?FMath::Clamp(PostureScale,0.0,1.0):0.0;
        PendingParryReactionScale=bParryReactionPending?FMath::Max(PendingParryReactionScale,SafeScale):SafeScale;
        bParryReactionPending=true;
        if(FMath::IsFinite(RecoverySeconds)&&RecoverySeconds>PendingParryRecoverySeconds){PendingParryRecoverySeconds=RecoverySeconds;PendingParryRecoveryGrade=RecoveryGrade;}
    }
    // IRPGNativeBossHealth
    virtual bool ReadNativeHealth(bool bMax, double& Out) const override { if (!bHittable) return false; Out = bMax ? MaxHealth : Health; return true; }
    virtual double ApplyPlayerHit(double Multiplier) override;
    virtual double ApplyPlayerAttackHit(const FRPGWeaponAttackRow& Row, double Multiplier) override;
    bool IsDead() const { return bDead; }
    uint64 CurrentGeneration() const { return GenerationId; }
    /** Encounter restart after the boss died or finished (explicit, proof/test authority): next generation, health and state back, walks to the band again. */
    bool RestartEncounter(uint64 NewGeneration,FString& Error);
    /** Pure state check of the restart preconditions RestartEncounter enforces first (terminal state, newer generation): lets the proof fixture refuse BEFORE it rewrites the target's health (Codex X-370 P2). */
    bool CanRestart(uint64 NewGeneration) const {return bInitialized&&!bFailed&&(bDead||bSucceeded)&&NewGeneration>GenerationId;}
    virtual void Tick(float Delta) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
    bool InitializeProofInternal(ARPGFrameworkProofFixture* Fixture,URPGBossFrameworkProfile* Profile,APawn* Target,uint64 Encounter,uint64 Generation,FString& Error,bool bAllowDevTest);
#if WITH_DEV_AUTOMATION_TESTS
    friend class FBossParryRecoveryLifecycleHarness;
#endif
    UPROPERTY(VisibleAnywhere) TObjectPtr<URPGFrameworkMoveExecutor> Executor;
    TUniquePtr<FRPGFrameworkDependencies> Dependencies;
    TWeakObjectPtr<APawn> Target;
    TWeakObjectPtr<AController> TargetController;
    TWeakObjectPtr<ARPGFrameworkProofFixture> ProofFixture;
    uint64 EncounterId=0, GenerationId=0;
    double StartedAt=0., TargetHPBefore=0., ExpectedTargetHP=0.;
    FVector WalkStart=FVector::ZeroVector;
    bool bInitialized=false,bFailed=false,bArrived=false,bStartedMove=false,bSucceeded=false;
    bool bTestInitialized=false;
    FRPGBossMoveSelector Selector;
    void Die();
    double Health=0., MaxHealth=0.;
    bool bHittable=false, bDead=false;
    int32 AttacksDone=0;
    /** BOSS-QA-002: one id per selector decision, never reset inside a process (attack= is an attack-budget slot and repeats after an aborted attack). Logged as seq= on candidate, refusal and decision lines. */
    int32 DecisionSeq=0;
    FVector ArenaOrigin=FVector::ZeroVector;   // BOSS-AWR-001: where the target stood when the encounter began
    double ProofIFStart=-1., ProofIFPressAt=-1.; int32 ProofIFProbes=0; bool bProofIFPressed=false;   // test hook rpg.BossProofIFrameSweep (BOSS-HIT-009)
    double ProofGStart=-1.;   // test hook rpg.BossProofPlayerGuard (BOSS-COM-004 / HIT-008)
    double ProofHitStart=-1.; int32 ProofHitsDone=0; TArray<double> ProofHitOffsets;   // test hook rpg.BossProofPlayerHits: scripted player hits on the GAME clock
    bool bLeashed=false, bLeashAtCenter=false;   // BOSS-MOV-005
    RPGBossTrack::EPlayerActivity Activity=RPGBossTrack::EPlayerActivity::None; ERPGAttackKind SwingKindSeen=ERPGAttackKind::Unknown; void TickActivity();   // BOSS-AWR-006
    RPGBossTrack::FDodgeHistory DodgeHistory; bool bDodgeWasFast=false; double DodgeSeenAt=-100.; int32 DodgesSeen=0; void TickDodge();   // BOSS-AWR-008
    double ProofDodgeStart=-1.; int32 ProofDodgesDone=0; TArray<TPair<double,bool>> ProofDodges;   // test hook rpg.BossProofPlayerDodge (bool = backward)
    RPGBossTrack::FLosMemory Los; bool bLosWalking=false; void TickLos();   // BOSS-AWR-007
    // BOSS-SEL-009: perception of the target's flask drink and the reaction delay
    TWeakObjectPtr<UAnimMontage> DrinkMontage; bool bDrinkWasPlaying=false, bFlaskPending=false, bFlaskKnown=false; int32 FlaskPerceivedCount=0; double FlaskPerceivedAt=0., FlaskReactAt=0.; void TickFlask();
    double ProofDrinkStart=-1.; int32 ProofDrinksDone=0; TArray<double> ProofDrinkOffsets;   // test hook rpg.BossProofPlayerDrink
    int32 KiteStreak=0, HugStreak=0;             // BOSS-PHS-005: consecutive chosen decisions with the target far / close
    TArray<TPair<double,FVector>> ProofShifts; int32 ProofShiftsDone=0; double ProofShiftStart=-1.;   // test hook rpg.BossProofTargetShift
    bool bTargetFaultInjected=false;           // test hook rpg.BossProofTargetFault: once per encounter
    /** BOSS-HIT-005 test hook (rpg.BossProofBystander): spawned once per encounter. */
    bool bBystanderSpawned=false;
    /** F6c: the authoritative phase, changed only at the neutral decision gate; latched until restart. */
    FName CurrentPhaseId; bool bPhaseTwoLatched=false;
    /** F8 posture: pool, break state, and the time of the last drain (regeneration delay). */
    double Posture=0., LastPostureDrain=-1., StaggerEndsAt=0.; bool bStaggered=false, bStaggerAbortedAttack=false;
    bool PostureEnabled() const;
    /** BOSS-DEF-004: the running card has hyperarmor and is in its ACTIVE state. */
    bool HyperArmorNow() const;
    /** BOSS-DEF-002 telemetry: the regeneration of the current cycle was already logged (reset by every drain, break and restart). */
    bool bPostureRegenLogged=false;
    /** F9 bleed: buildup state of the legacy rules and the frame of the last proc (two hits in one frame do not proc twice). */
    RPGBleedRules::FState BleedState; uint64 BleedProcFrame=MAX_uint64;
    bool BleedEnabled() const;
    void ResetBleed();
    void ApplyBleed(double Amount);
    /** The one hit path: health factor (times PlayerHitDamage), posture amount and bleed amount already include the multiplier. */
    double ApplyHit(double HealthFactor, double PostureAmount, double BleedAmount);
    void StartStagger();
    void EndStagger();
    /** F11 stagger / phase transition animations (all optional, empty clips = the F8 and F6c behaviour unchanged). The stagger sub state is a pure function of the time since the break (RPGStaggerAnim). */
    double StaggerStartedAt=0., PhaseHoldStartedAt=0.; RPGStaggerAnim::EState StaggerAnimState=RPGStaggerAnim::EState::Start; bool bStaggerAnimActive=false, bPhaseHold=false;
    TWeakObjectPtr<UAnimMontage> F11Montage;
    bool PlayF11Clip(UAnimSequence* Clip,int32 Loops);
    void StopF11Clip();
    void TickStaggerAnim();
    /** BOSS-QA-001: the runtime overlay (console variable rpg.BossOverlay): on screen each tick, as a log line once per second at 2. */
    double OverlayLoggedAt=-1.; FString OverlayLastState;
    /** Combo (BOSS-COM rows): the pure graph of the profile and the state of the running combo; a branch gate is evaluated when a card of the combo finishes. */
    RPGBossCombo::FComboGraph ComboGraph; RPGBossCombo::FComboState ComboState; bool bComboActive=false; int32 ComboHitsAtStart=0, ComboGuardedAtStart=0, ComboParriedAtStart=0; uint64 ComboGateCounter=0;
    bool bComboPausing=false; double ComboPauseUntil=0.; int32 ComboPendingCard=INDEX_NONE;   // BOSS-PAC-002: a deliberate tempo pause between two cards of a combo
    void StartComboCard();
    /** Repositions in a row since the last attack started (profile RepositionMax). */
    bool bParryReactionPending=false; double PendingParryReactionScale=0.;   // a contact was parried: apply the strongest same-tick grade at the start of the NEXT boss tick, never inside the executor's sweep
    double PendingParryRecoverySeconds=0.,ParryRecoveryUntil=0.; int32 PendingParryRecoveryGrade=0;
    RPGBossAggro::EBand AggroBand=RPGBossAggro::EBand::Balanced; TArray<double> AggroDodgeTimes;
    int32 FatigueWhiffs=0; bool bFatigueFinishedCardSeen=false;
    int32 RepositionsInARow=0; double RepositionTurnStartedAt=-1., StrafeStartedAt=-1., StrafeLastLog=-1., StrafeLastTick=-1.;   // StrafeStartedAt: BOSS-SEL-008 neutral strafe
    int32 StrafeDirFlip=1; RPGBossStuck::FStuck StrafeStuck; int32 YawProbeSampleIndex=0;
    RPGBossTrack::FTurnLatch RepositionLatch;   // BOSS-MOV-003: direction memory of the reposition turn
    bool HandleComboGate();
    FRPGBossDecisionSnapshot MakeSnapshot() const;
    void TickOverlay();
};
