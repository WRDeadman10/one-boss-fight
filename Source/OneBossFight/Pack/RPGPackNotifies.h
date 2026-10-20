// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimNotifies/AnimNotify.h"
#include "Animation/AnimNotifies/AnimNotifyState.h"
#include "RPGPackNotifies.generated.h"

class UNiagaraSystem;
class USoundBase;

/**
 * Animation notify for the montages that drive the pack's abilities: spawns a Niagara system and/or a sound in front of the actor
 * (Sevarog's shockwave ring, cast sound). Damage and hit detection stay in the pack's own notifies (ANS_CollisionTrace).
 */
UCLASS(meta = (DisplayName = "RPG Spawn Effect"))
class ONEBOSSFIGHT_API URPGAN_SpawnEffect : public UAnimNotify
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Effect")
	TObjectPtr<UNiagaraSystem> NiagaraEffect;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Effect")
	TObjectPtr<USoundBase> Sound;

	/** Distance in front of the actor (negative = behind). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Effect")
	float ForwardOffset = 0.f;

	/** Lowers the effect from the actor origin to the floor. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Effect")
	float GroundDrop = 0.f;

	/** Uniform scale of the spawned system. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Effect", meta = (ClampMin = "0.01"))
	float Scale = 1.f;

	virtual void Notify(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, const FAnimNotifyEventReference& EventReference) override;
	virtual FString GetNotifyName_Implementation() const override { return TEXT("RPG Spawn Effect"); }
};

/**
 * Charge: while active, drives the character towards the player so a mid-range swing reaches him. Speed is chosen every tick so the character arrives at StopDistance
 * exactly when the window ends (WindowEndTime, in montage seconds), capped at MaxSpeed. Used by Sevarog's mid-range attack; the pack's own abilities do not move
 * for a plain montage.
 */
UCLASS(meta = (DisplayName = "RPG Charge To Target"))
class ONEBOSSFIGHT_API URPGANS_ChargeToTarget : public UAnimNotifyState
{
	GENERATED_BODY()

public:
	/** Stops this far (cm) from the target. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Charge", meta = (ClampMin = "0"))
	float StopDistance = 200.f;

	/** Upper speed limit in cm/s. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Charge", meta = (ClampMin = "0"))
	float MaxSpeed = 2200.f;

	/** Montage time (seconds) at which the charge should have reached the target. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Charge")
	float WindowEndTime = 0.3f;

	virtual void NotifyTick(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, float FrameDeltaTime, const FAnimNotifyEventReference& EventReference) override;
	virtual FString GetNotifyName_Implementation() const override { return TEXT("RPG Charge To Target"); }
};
