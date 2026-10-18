// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RPGEncounterTrigger.generated.h"

class UBoxComponent;

/** Starts the encounter when the player walks in. Re-arms itself after every encounter reset. */
UCLASS()
class ONEBOSSFIGHT_API ARPGEncounterTrigger : public AActor
{
	GENERATED_BODY()

public:
	ARPGEncounterTrigger();

protected:
	virtual void BeginPlay() override;

	UFUNCTION()
	void HandleOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp,
		int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

private:
	void Rearm();

	UPROPERTY(VisibleAnywhere, Category = "Encounter")
	TObjectPtr<UBoxComponent> Volume;
};
