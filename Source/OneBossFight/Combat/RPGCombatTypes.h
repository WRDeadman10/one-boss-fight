// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "RPGCombatTypes.generated.h"

/** Logical combat state. Exactly one at a time; see URPGCombatComponent for the allowed transitions. */
UENUM(BlueprintType)
enum class ERPGCombatState : uint8
{
	Locomotion,
	/** Attack started, before the hit window closes. */
	Attacking,
	/** Next attack in the chain may be started now. */
	ComboWindow,
	/** Attack finished dealing damage; still committed until the animation ends or is cancelled. */
	Recovery,
	Dodging,
	Blocking,
	Staggered,
	Dead
};

UENUM(BlueprintType)
enum class ERPGAttackType : uint8
{
	Light,
	Heavy
};

/** An input pressed too early, remembered for a short time and replayed when the action allows it. */
UENUM(BlueprintType)
enum class ERPGBufferedAction : uint8
{
	None,
	LightAttack,
	HeavyAttack,
	Dodge
};

/** Everything the single damage path needs to know about one incoming hit. */
USTRUCT(BlueprintType)
struct FRPGHitInfo
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "Combat")
	TObjectPtr<AActor> Instigator = nullptr;

	UPROPERTY(BlueprintReadWrite, Category = "Combat")
	float Damage = 0.f;

	UPROPERTY(BlueprintReadWrite, Category = "Combat")
	float PoiseDamage = 0.f;

	UPROPERTY(BlueprintReadWrite, Category = "Combat")
	FVector HitLocation = FVector::ZeroVector;

	/** Unit direction from the attacker toward the victim. */
	UPROPERTY(BlueprintReadWrite, Category = "Combat")
	FVector HitDirection = FVector::ForwardVector;

	/** Grabs and some boss attacks ignore blocking. */
	UPROPERTY(BlueprintReadWrite, Category = "Combat")
	bool bUnblockable = false;
};

/** What the damage path did with a hit. */
USTRUCT(BlueprintType)
struct FRPGHitResult
{
	GENERATED_BODY()

	/** False when the hit was ignored (dead target, i-frames). */
	UPROPERTY(BlueprintReadOnly, Category = "Combat")
	bool bProcessed = false;

	UPROPERTY(BlueprintReadOnly, Category = "Combat")
	bool bIgnoredInvulnerable = false;

	UPROPERTY(BlueprintReadOnly, Category = "Combat")
	bool bBlocked = false;

	UPROPERTY(BlueprintReadOnly, Category = "Combat")
	float DamageApplied = 0.f;

	UPROPERTY(BlueprintReadOnly, Category = "Combat")
	bool bPoiseBroken = false;

	UPROPERTY(BlueprintReadOnly, Category = "Combat")
	bool bKilled = false;
};
