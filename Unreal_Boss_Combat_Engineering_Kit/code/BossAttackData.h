#pragma once
// Primary Data Asset schema: data fields only. Executor still owns all runtime state.
#include "CoreMinimal.h"
#include "Engine/PrimaryDataAsset.h"
#include "Animation/AnimMontage.h"
#include "BossCombatTypes.h"
#include "BossAttackData.generated.h"

USTRUCT(BlueprintType)
struct FBossComboEdge
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FName GateName;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FName FollowupAttackID;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float MinDistanceCm = 0.f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float MaxDistanceCm = 99999.f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float MinAbsYawDeg = 0.f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float MaxAbsYawDeg = 180.f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) int32 MinimumPhase = 1;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) bool bRequiresHitConfirm = false;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float BranchWeight = 1.f;
};

UCLASS(BlueprintType)
class UBossAttackData : public UPrimaryDataAsset
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Identity") FName AttackID;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Identity") EBossAttackGeometry Geometry = EBossAttackGeometry::Sweep;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Animation") TObjectPtr<UAnimMontage> Montage = nullptr;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Selection") float MinRangeCm = 100.f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Selection") float MaxRangeCm = 400.f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Selection") float PreferredRangeCm = 230.f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Selection") float MinAbsoluteYawDeg = 0.f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Selection") float MaxAbsoluteYawDeg = 100.f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Selection") int32 MinimumPhase = 1;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Selection") float BaseWeight = 0.5f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Selection") float CooldownSeconds = 2.f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Selection") bool bRequiresLOS = true;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Motion") float MaxTurnDegreesPerSecondDuringEarlyWindup = 160.f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Motion") float MaxTurnDegreesPerSecondAfterCommit = 10.f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Motion") float MaxWarpTranslationCm = 350.f;

    // Timing values are designer reference metadata; runtime hit windows are
    // started/stopped by Animation Notifies, not independent delayed timers.
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Timing") float WindupSeconds = 0.4f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Timing") float HoldSeconds = 0.f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Timing") float RecoverySeconds = 0.6f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Damage") FBossDamageSpec DamageSpec;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Combos") TArray<FBossComboEdge> ComboEdges;
};
