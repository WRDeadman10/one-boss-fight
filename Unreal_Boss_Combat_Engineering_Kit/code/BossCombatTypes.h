#pragma once
// Reference Unreal Engine 5.5 schema. Rename project modules as needed.
// Not compiled in this environment.
#include "CoreMinimal.h"
#include "GameplayTagContainer.h"
#include "BossCombatTypes.generated.h"

UENUM(BlueprintType)
enum class EBossCombatState : uint8
{
    Neutral, Positioning, Windup, Committed, Active, Recovery,
    Staggered, PhaseTransition, Dead
};

UENUM(BlueprintType)
enum class EBossAttackGeometry : uint8
{
    Thrust, Sweep, Slam, RadialRing, Lane, Grab, Counter, MultiHitSweep
};

UENUM(BlueprintType)
enum class EBossHitPolicy : uint8
{
    OncePerAttack, OncePerWindow, Periodic, ImpactPlusSplash
};

USTRUCT(BlueprintType)
struct FBossCombatContext
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly) TObjectPtr<AActor> TargetActor = nullptr;
    UPROPERTY(BlueprintReadOnly) float TimestampS = 0.f;
    UPROPERTY(BlueprintReadOnly) float DistanceCm = 0.f;
    UPROPERTY(BlueprintReadOnly) float SignedYawDeg = 0.f;
    UPROPERTY(BlueprintReadOnly) bool bHasLineOfSight = false;
    UPROPERTY(BlueprintReadOnly) float BossHealthFraction = 1.f;
    UPROPERTY(BlueprintReadOnly) int32 Phase = 1;
    UPROPERTY(BlueprintReadOnly) FGameplayTag PlayerActionTag;
    UPROPERTY(BlueprintReadOnly) float TargetRecoveryRemainingS = 0.f;
};

USTRUCT(BlueprintType)
struct FBossDamageSpec
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float HealthDamage = 50.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float StanceDamage = 15.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float RadialSplashFraction = 0.5f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) EBossHitPolicy HitPolicy = EBossHitPolicy::OncePerAttack;
};

USTRUCT(BlueprintType)
struct FBossDecisionCandidate
{
    GENERATED_BODY()
    UPROPERTY(BlueprintReadOnly) FName AttackID;
    UPROPERTY(BlueprintReadOnly) bool bEligible = false;
    UPROPERTY(BlueprintReadOnly) float Score = 0.f;
    UPROPERTY(BlueprintReadOnly) FString RejectionReason;
};
