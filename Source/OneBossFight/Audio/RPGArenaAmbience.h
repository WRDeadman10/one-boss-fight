// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RPGArenaAmbience.generated.h"

class UAudioComponent;
class USoundBase;

/**
 * Arena ambience: a looping wind bed (2D) that plays during the game only (never in the editor viewport). Place one in the level and assign Wind.
 * A sound that is not set to loop is restarted when it finishes.
 */
UCLASS()
class ONEBOSSFIGHT_API ARPGArenaAmbience : public AActor
{
	GENERATED_BODY()

public:
	ARPGArenaAmbience();

	virtual void BeginPlay() override;

	UFUNCTION(BlueprintCallable, CallInEditor, Category = "Editor")
	void Rebuild();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Ambience")
	TObjectPtr<USoundBase> Wind;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Ambience", meta = (ClampMin = "0", ClampMax = "2"))
	float WindVolume = 0.35f;

private:
	UPROPERTY(VisibleAnywhere, Category = "Ambience")
	TObjectPtr<UAudioComponent> WindPlayer;

	UFUNCTION()
	void OnWindFinished();
};
