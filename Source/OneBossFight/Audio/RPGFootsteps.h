// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "RPGFootsteps.generated.h"

class ACharacter;
class USoundAttenuation;
class USoundBase;

/**
 * Footstep sounds that follow the animation: each foot bone is watched, and a step is played when it comes down to the floor after having been lifted.
 * Works for any skeleton with two foot bones, so the pack player and the pack boss share it (the boss gets heavier, lower steps and louder landings).
 * Also plays the landing sound. The pack's own footstep notify exists on one animation only and has no sounds assigned.
 */
UCLASS(ClassGroup = (Audio), meta = (BlueprintSpawnableComponent))
class ONEBOSSFIGHT_API URPGFootsteps : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGFootsteps();

	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Footsteps")
	TObjectPtr<USoundBase> WalkSound;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Footsteps")
	TObjectPtr<USoundBase> JogSound;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Footsteps")
	TObjectPtr<USoundBase> RunSound;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Footsteps")
	TObjectPtr<USoundBase> LandSound;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Footsteps")
	FName LeftFootBone = TEXT("foot_l");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Footsteps")
	FName RightFootBone = TEXT("foot_r");

	/** Speeds (cm/s) where the sound switches from walk to jog and from jog to run. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Footsteps")
	float JogSpeed = 280.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Footsteps")
	float RunSpeed = 520.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Footsteps")
	float VolumeScale = 0.8f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Footsteps")
	float PitchScale = 1.f;

	/** How far a foot bone must rise above its own lowest height before the next touch counts as a step, cm for a 98 cm capsule half height (scales with the body). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Footsteps")
	float LiftHeight = 6.f;

	/** A foot counts as touching the floor within this height above its lowest, same scaling. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Footsteps")
	float TouchHeight = 3.f;

	/** Distance in cm where the steps become inaudible (3D attenuation). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Footsteps")
	float AudibleRange = 2600.f;

	UFUNCTION(BlueprintPure, Category = "Footsteps")
	int32 GetStepCount() const { return StepCount; }

private:
	struct FFootState
	{
		FName Bone;
		bool bLifted = false;
		float Cooldown = 0.f;
		float LowestHeight = 0.f; // the bone's own height when planted (an ankle joint sits several cm above the floor)
		bool bHaveLowest = false;
	};

	FFootState Feet[2];

	UPROPERTY(Transient)
	TObjectPtr<ACharacter> Character;

	UPROPERTY(Transient)
	TObjectPtr<USoundAttenuation> Attenuation;

	int32 StepCount = 0;
	bool bWarnedMissingBones = false;

	UFUNCTION()
	void OnLanded(const FHitResult& Hit);

	void PlayAt(USoundBase* Sound, const FVector& Location, float Volume, float Pitch) const;
	USoundBase* PickSound(float Speed) const;
};
