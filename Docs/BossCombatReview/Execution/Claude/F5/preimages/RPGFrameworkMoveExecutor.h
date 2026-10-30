// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "Components/ActorComponent.h"
#include "Player/RPGBossMoveModel.h"
#include "RPGFrameworkMoveExecutor.generated.h"
class ARPGFrameworkBossCharacter;
class APawn;
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
    void Abort(const FString& Reason);
    bool IsIdle() const;
    bool IsClean() const;
    bool DidFinish() const { return bFinished; }
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
    FRPGBossMoveModel Model;
    FRPGBossAttackToken Token;
    bool bInitialized=false, bAborted=false, bFinished=false, bSawPoseWeight=false;
    double StartWorldSeconds=0., LastWorldSeconds=0., LastPosition=0.;
};
