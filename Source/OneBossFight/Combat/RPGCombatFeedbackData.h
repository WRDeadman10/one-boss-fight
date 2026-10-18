// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "RPGCombatFeedbackData.generated.h"

class UParticleSystem;
class USoundBase;

/**
 * What a combatant sounds and looks like when things happen to it: taking a hit, blocking, staggering,
 * dodging, dying. What a weapon does on impact lives in URPGWeaponData. Every field is optional.
 */
UCLASS(BlueprintType)
class ONEBOSSFIGHT_API URPGCombatFeedbackData : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	/** Played when this combatant takes damage. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Hit")
	TObjectPtr<USoundBase> PainSound;

	/** Played instead of PainSound when the hit broke poise (a stagger). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Hit")
	TObjectPtr<USoundBase> HeavyPainSound;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Hit")
	TObjectPtr<USoundBase> BlockSound;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Hit")
	TObjectPtr<UParticleSystem> BlockEffect;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Actions")
	TObjectPtr<USoundBase> DodgeSound;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Actions")
	TObjectPtr<USoundBase> DeathSound;
};
