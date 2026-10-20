// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RPGFireSource.generated.h"

class UAudioComponent;
class USoundBase;
class UParticleSystem;
class UParticleSystemComponent;
class UPointLightComponent;

/**
 * A fire that lives: flame, smoke and spark particles plus a warm point light whose brightness, colour and position
 * flutter with smooth noise. Used for braziers, torches and braziers' embers around the arena.
 * Templates are set by Scripts/Editor/dress_arena.py (Cascade systems from the starter content).
 */
UCLASS()
class ONEBOSSFIGHT_API ARPGFireSource : public AActor
{
	GENERATED_BODY()

public:
	ARPGFireSource();

	virtual void OnConstruction(const FTransform& Transform) override;

	/** Runs the construction again after the editor scripts changed properties (Python cannot call RerunConstructionScripts). */
	UFUNCTION(BlueprintCallable, CallInEditor, Category = "Editor")
	void Rebuild();
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;

	UPROPERTY(EditAnywhere, Category = "Fire")
	TObjectPtr<UParticleSystem> FireTemplate;

	UPROPERTY(EditAnywhere, Category = "Fire")
	TObjectPtr<UParticleSystem> SmokeTemplate;

	UPROPERTY(EditAnywhere, Category = "Fire")
	TObjectPtr<UParticleSystem> SparkTemplate;

	/** Looping crackle, heard within CrackleRange (game only). */
	UPROPERTY(EditAnywhere, Category = "Fire")
	TObjectPtr<USoundBase> CrackleSound;

	UPROPERTY(EditAnywhere, Category = "Fire")
	float CrackleVolume = 0.45f;

	UPROPERTY(EditAnywhere, Category = "Fire")
	float CrackleRange = 1700.f;

	/** Particle scale of the whole fire. */
	UPROPERTY(EditAnywhere, Category = "Fire", meta = (ClampMin = "0.05"))
	float FireScale = 1.f;

	/** Light height above the actor origin, cm. */
	UPROPERTY(EditAnywhere, Category = "Light")
	float LightHeight = 60.f;

	UPROPERTY(EditAnywhere, Category = "Light")
	float BaseIntensity = 60.f;

	UPROPERTY(EditAnywhere, Category = "Light")
	float AttenuationRadius = 1800.f;

	UPROPERTY(EditAnywhere, Category = "Light")
	bool bCastShadows = false;

	UPROPERTY(EditAnywhere, Category = "Light")
	FLinearColor LightColor = FLinearColor(1.f, 0.42f, 0.12f);

	/** 0 = steady, 0.4 = a restless flame. Fraction of BaseIntensity. */
	UPROPERTY(EditAnywhere, Category = "Light", meta = (ClampMin = "0", ClampMax = "1"))
	float FlickerAmount = 0.3f;

	UPROPERTY(EditAnywhere, Category = "Light", meta = (ClampMin = "0.1"))
	float FlickerSpeed = 5.f;

	/** How far the light wanders sideways, cm (shadows dance with it). */
	UPROPERTY(EditAnywhere, Category = "Light")
	float WanderCm = 6.f;

private:
	UPROPERTY(VisibleAnywhere, Category = "Fire")
	TObjectPtr<UPointLightComponent> Light;

	UPROPERTY(VisibleAnywhere, Category = "Fire")
	TObjectPtr<UParticleSystemComponent> Fire;

	UPROPERTY(VisibleAnywhere, Category = "Fire")
	TObjectPtr<UParticleSystemComponent> Smoke;

	UPROPERTY(VisibleAnywhere, Category = "Fire")
	TObjectPtr<UParticleSystemComponent> Sparks;

	UPROPERTY(VisibleAnywhere, Category = "Fire")
	TObjectPtr<UAudioComponent> Crackle;

	float Seed = 0.f;
	float Clock = 0.f;

	void Apply();
};
