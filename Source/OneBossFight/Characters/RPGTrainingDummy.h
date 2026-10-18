// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Characters/RPGCharacterBase.h"
#include "Combat/RPGCombatTypes.h"
#include "RPGTrainingDummy.generated.h"

/**
 * A target that takes hits, shows what happened, and resets itself after dying. Used to prove hit
 * detection, damage, poise and death before the boss exists. It has no AI and never attacks.
 */
UCLASS()
class ONEBOSSFIGHT_API ARPGTrainingDummy : public ARPGCharacterBase
{
	GENERATED_BODY()

public:
	ARPGTrainingDummy();

	/** Seconds after death before the dummy stands up again. Zero or less disables the reset. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dummy")
	float ResetDelay = 3.f;

protected:
	virtual void BeginPlay() override;
	virtual void HandleDeath() override;

	UFUNCTION()
	void HandleHitReceived(const FRPGHitInfo& Hit, const FRPGHitResult& Result);

private:
	FTimerHandle ResetTimer;
};
