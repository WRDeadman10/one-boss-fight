// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "RPGBossMusic.generated.h"

class UAudioComponent;
class URPGBossEncounter;
class USoundBase;

/**
 * Boss fight music. Fades in when the boss wakes (player in the gate or boss hurt), fades out when the boss dies or the encounter resets.
 * The track is a placeholder until a real piece is licensed (set Music from the editor or the subsystem).
 */
UCLASS(ClassGroup = (Audio), meta = (BlueprintSpawnableComponent))
class ONEBOSSFIGHT_API URPGBossMusic : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGBossMusic();

	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Music")
	TObjectPtr<USoundBase> Music;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Music", meta = (ClampMin = "0", ClampMax = "2"))
	float Volume = 0.55f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Music", meta = (ClampMin = "0"))
	float FadeInSeconds = 2.5f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Music", meta = (ClampMin = "0"))
	float FadeOutSeconds = 4.f;

	UFUNCTION(BlueprintPure, Category = "Music")
	bool IsPlaying() const { return bPlaying; }

private:
	UPROPERTY(Transient)
	TObjectPtr<UAudioComponent> Player;

	UPROPERTY(Transient)
	TObjectPtr<URPGBossEncounter> Encounter;

	bool bPlaying = false;

	void Start();
	void Stop();
};
