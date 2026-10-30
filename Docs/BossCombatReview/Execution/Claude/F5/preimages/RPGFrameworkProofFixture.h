// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "GameFramework/Actor.h"
#include "GameFramework/GameModeBase.h"
#include "RPGFrameworkProofFixture.generated.h"
class URPGBossFrameworkProfile;
class ARPGFrameworkBossCharacter;
class APlayerStart;
UCLASS()
class ONEBOSSFIGHT_API ARPGFrameworkProofFixture : public AActor
{
    GENERATED_BODY()
public:
    ARPGFrameworkProofFixture();
    UPROPERTY(EditInstanceOnly) TSoftObjectPtr<URPGBossFrameworkProfile> Profile;
    UPROPERTY(EditInstanceOnly) TObjectPtr<APlayerStart> TargetStart;
    UPROPERTY(EditInstanceOnly) FTransform BossSpawnTransform;
    UPROPERTY(EditInstanceOnly) int32 EncounterId=0;
    UPROPERTY(EditInstanceOnly) int32 Generation=0;
    bool Authorizes(const ARPGFrameworkBossCharacter* Boss,const APawn* InTarget) const;
    void SetExplicitTarget(APawn* Pawn);
    void InvalidateTarget();
    virtual void BeginPlay() override;
    virtual void Tick(float Delta) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    const URPGBossFrameworkProfile* LoadedProfile() const {return ResolvedProfile;}
private:
    void Fail(const FString& Error);
    UPROPERTY(Transient) TObjectPtr<URPGBossFrameworkProfile> ResolvedProfile;
    UPROPERTY(Transient) TObjectPtr<ARPGFrameworkBossCharacter> OwnedBoss;
    TWeakObjectPtr<APawn> ExplicitPlayer;
    double WaitStart=0.; bool bFailed=false,bAttempted=false,bTargetPrepared=false;
};
/** Only a NEW proof map can opt in with its own world override; no project default changes. */
UCLASS()
class ONEBOSSFIGHT_API ARPGFrameworkProofGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    ARPGFrameworkProofGameMode();
    bool RegisterFixture(ARPGFrameworkProofFixture* Fixture,FString& Error);
    virtual void PostLogin(APlayerController* Player) override;
    virtual void Logout(AController* Exiting) override;
    virtual void HandleStartingNewPlayer_Implementation(APlayerController* Player) override;
private:
    void TrySpawnTarget();
    TWeakObjectPtr<ARPGFrameworkProofFixture> Fixture;
    TWeakObjectPtr<APlayerController> ExplicitController;
    bool bSpawnAttempted=false;
};
