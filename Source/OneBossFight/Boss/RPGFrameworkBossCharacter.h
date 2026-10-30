// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "GameFramework/Character.h"
#include "Player/RPGBossFrameworkProfile.h"
#include "Player/RPGBleedRules.h"
#include "Player/RPGBossMoveSelector.h"
#include "Player/RPGNativeBossHealth.h"
#include "RPGFrameworkBossCharacter.generated.h"
class URPGFrameworkMoveExecutor;
class ARPGFrameworkProofFixture;
UCLASS()
class ONEBOSSFIGHT_API ARPGFrameworkBossCharacter : public ACharacter, public IRPGNativeBossHealth
{
    GENERATED_BODY()
public:
    ARPGFrameworkBossCharacter();
    bool InitializeProof(ARPGFrameworkProofFixture* Fixture,URPGBossFrameworkProfile* Profile,APawn* Target,uint64 Encounter,uint64 Generation,FString& Error);
    void WalkArrived();
    void Fail(const FString& Error);
    bool ValidateTarget(double& Health) const;
    APawn* ExplicitTarget() const {return Target.Get();}
    const URPGBossFrameworkProfile* ProofProfile() const {return Dependencies?Dependencies->Profile.Get():nullptr;}
    bool Succeeded() const {return bSucceeded;}
    bool Failed() const {return bFailed;}
    /** F4: the executor reports every accepted hit so the target-health invariant expects exactly that loss. */
    void NoteDamageApplied(double Applied) {ExpectedTargetHP-=Applied;}
    // IRPGNativeBossHealth
    virtual bool ReadNativeHealth(bool bMax, double& Out) const override { if (!bHittable) return false; Out = bMax ? MaxHealth : Health; return true; }
    virtual double ApplyPlayerHit(double Multiplier) override;
    bool IsDead() const { return bDead; }
    uint64 CurrentGeneration() const { return GenerationId; }
    /** Encounter restart after the boss died or finished (explicit, proof/test authority): next generation, health and state back, walks to the band again. */
    bool RestartEncounter(uint64 NewGeneration,FString& Error);
    /** Pure state check of the restart preconditions RestartEncounter enforces first (terminal state, newer generation): lets the proof fixture refuse BEFORE it rewrites the target's health (Codex X-370 P2). */
    bool CanRestart(uint64 NewGeneration) const {return bInitialized&&!bFailed&&(bDead||bSucceeded)&&NewGeneration>GenerationId;}
    virtual void Tick(float Delta) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
    UPROPERTY(VisibleAnywhere) TObjectPtr<URPGFrameworkMoveExecutor> Executor;
    TUniquePtr<FRPGFrameworkDependencies> Dependencies;
    TWeakObjectPtr<APawn> Target;
    TWeakObjectPtr<AController> TargetController;
    TWeakObjectPtr<ARPGFrameworkProofFixture> ProofFixture;
    uint64 EncounterId=0, GenerationId=0;
    double StartedAt=0., TargetHPBefore=0., ExpectedTargetHP=0.;
    FVector WalkStart=FVector::ZeroVector;
    bool bInitialized=false,bFailed=false,bArrived=false,bStartedMove=false,bSucceeded=false;
    FRPGBossMoveSelector Selector;
    void Die();
    double Health=0., MaxHealth=0.;
    bool bHittable=false, bDead=false;
    int32 AttacksDone=0;
    /** F6c: the authoritative phase, changed only at the neutral decision gate; latched until restart. */
    FName CurrentPhaseId; bool bPhaseTwoLatched=false;
    /** F8 posture: pool, break state, and the time of the last drain (regeneration delay). */
    double Posture=0., LastPostureDrain=-1., StaggerEndsAt=0.; bool bStaggered=false, bStaggerAbortedAttack=false;
    bool PostureEnabled() const;
    /** F9 bleed: buildup state of the legacy rules and the frame of the last proc (two hits in one frame do not proc twice). */
    RPGBleedRules::FState BleedState; uint64 BleedProcFrame=MAX_uint64;
    bool BleedEnabled() const;
    void ResetBleed();
    void ApplyBleed(double Multiplier);
    void StartStagger();
    void EndStagger();
};
