// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "Combat/RPGWeaponData.h"
#include "RPGBossAttackData.generated.h"

/**
 * One boss attack: what it does (Attack: montage, damage, poise, fallback timing) and when the boss may
 * choose it (range, arc, phase, weight, cooldown, repeat limit). Fairness knobs live here too: how long the
 * boss keeps turning toward the player before committing, and the pause after the attack.
 */
UCLASS(BlueprintType)
class ONEBOSSFIGHT_API URPGBossAttackData : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Attack")
	FName AttackName;

	/** Montage, damage, poise damage and unblockable flag. Timing comes from the montage's notify states. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Attack")
	FRPGAttackData Attack;

	// ---- Selection -----------------------------------------------------------------------

	/** Distance in cm between the boss and the target (actor origins). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Selection", meta = (ClampMin = "0"))
	float MinRange = 0.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Selection", meta = (ClampMin = "0"))
	float MaxRange = 400.f;

	/** The target must be within this many degrees of the boss's forward direction. 180 = any direction. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Selection", meta = (ClampMin = "0", ClampMax = "180"))
	float MaxAngle = 60.f;

	/** Inclusive phase range (phases start at 1). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Selection", meta = (ClampMin = "1"))
	int32 MinPhase = 1;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Selection", meta = (ClampMin = "1"))
	int32 MaxPhase = 9;

	/** Relative chance among the attacks that are currently allowed. Zero disables the attack. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Selection", meta = (ClampMin = "0"))
	float Weight = 1.f;

	/** Seconds before this attack can be chosen again. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Selection", meta = (ClampMin = "0"))
	float Cooldown = 3.f;

	/** How many times in a row this attack may be chosen. 1 = never twice in a row. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Selection", meta = (ClampMin = "1"))
	int32 MaxConsecutiveRepeats = 1;

	// ---- Fairness and feel ---------------------------------------------------------------

	/** Degrees per second the boss turns toward the target before the first hit window. 0 = committed on start. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Fairness", meta = (ClampMin = "0"))
	float TrackingTurnRate = 120.f;

	/** Pause after the attack ends before the boss decides again. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Fairness", meta = (ClampMin = "0"))
	float RecoveryPause = 0.5f;

	/** Forward speed applied when the first hit window opens (lunges, leaping slams). Zero = none. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Movement", meta = (ClampMin = "0"))
	float LungeSpeed = 0.f;
};
