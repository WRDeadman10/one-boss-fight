// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "Combat/RPGCombatTypes.h"
#include "RPGWeaponData.generated.h"

class UAnimMontage;

/**
 * One attack. The montage owns the timing through anim notify states (hit window, combo window, ...).
 * When no montage is assigned the combat component runs the same windows from the Fallback* times,
 * so combat is testable and playable before animations are authored.
 */
USTRUCT(BlueprintType)
struct FRPGAttackData
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Attack")
	TObjectPtr<UAnimMontage> Montage = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Attack", meta = (ClampMin = "0.1"))
	float PlayRate = 1.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Attack", meta = (ClampMin = "0"))
	float StaminaCost = 20.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Attack", meta = (ClampMin = "0"))
	float Damage = 25.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Attack", meta = (ClampMin = "0"))
	float PoiseDamage = 15.f;

	/** Grabs and some boss attacks ignore the target's block. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Attack")
	bool bUnblockable = false;

	/** Seconds. Used only without a montage. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Fallback Timing", meta = (ClampMin = "0.05"))
	float FallbackDuration = 0.8f;

	/** X = start, Y = end, seconds. Used only without a montage. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Fallback Timing")
	FVector2D FallbackHitWindow = FVector2D(0.25, 0.5);

	/** X = start, Y = end, seconds. Used only without a montage. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Fallback Timing")
	FVector2D FallbackComboWindow = FVector2D(0.5, 0.8);
};

/**
 * Data asset describing one weapon: its attacks and where the damage trace sits on the model.
 * New weapons are new assets, not new code.
 */
UCLASS(BlueprintType)
class ONEBOSSFIGHT_API URPGWeaponData : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Weapon")
	FText DisplayName;

	/** Light attacks in chain order. Pressing light during a combo window plays the next one; the chain then wraps. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Attacks")
	TArray<FRPGAttackData> LightCombo;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Attacks")
	FRPGAttackData HeavyAttack;

	/** Component carrying the sockets below. None = the character mesh. Matched by component name. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Trace")
	FName TraceComponentName;

	/** Hilt end of the damage line. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Trace")
	FName TraceBaseSocket;

	/** Tip end of the damage line. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Trace")
	FName TraceTipSocket;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Trace", meta = (ClampMin = "1"))
	float TraceRadius = 20.f;

	/** Points sampled along the base-tip line. More points catch thin targets on long blades. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Trace", meta = (ClampMin = "1", ClampMax = "8"))
	int32 TraceSamples = 4;

	/** The attack for a type and combo index. Falls back to a default attack when the asset has none, never null. */
	const FRPGAttackData& GetAttack(ERPGAttackType Type, int32 ComboIndex) const;

	int32 GetLightComboLength() const { return LightCombo.Num(); }
};
