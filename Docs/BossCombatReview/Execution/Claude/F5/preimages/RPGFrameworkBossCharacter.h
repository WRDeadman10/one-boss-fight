// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "GameFramework/Character.h"
#include "Player/RPGBossFrameworkProfile.h"
#include "RPGFrameworkBossCharacter.generated.h"
class URPGFrameworkMoveExecutor;
class ARPGFrameworkProofFixture;
UCLASS()
class ONEBOSSFIGHT_API ARPGFrameworkBossCharacter : public ACharacter
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
};
