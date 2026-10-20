// Copyright One Boss Fight. All Rights Reserved.

#include "Arena/RPGFireSource.h"
#include "Components/AudioComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/SceneComponent.h"
#include "Particles/ParticleSystem.h"
#include "Particles/ParticleSystemComponent.h"

ARPGFireSource::ARPGFireSource()
{
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.bStartWithTickEnabled = true;

	USceneComponent* Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
	SetRootComponent(Root);

	Light = CreateDefaultSubobject<UPointLightComponent>(TEXT("Light"));
	Light->SetupAttachment(Root);
	Light->SetMobility(EComponentMobility::Movable);
	Light->SetSourceRadius(10.f);
	Light->SetSoftSourceRadius(20.f);
	Light->SetUseInverseSquaredFalloff(true);

	auto MakeParticles = [this, Root](const TCHAR* Name)
	{
		UParticleSystemComponent* Component = CreateDefaultSubobject<UParticleSystemComponent>(Name);
		Component->SetupAttachment(Root);
		Component->bAutoActivate = true;
		return Component;
	};
	Fire = MakeParticles(TEXT("Fire"));
	Smoke = MakeParticles(TEXT("Smoke"));
	Sparks = MakeParticles(TEXT("Sparks"));

	Crackle = CreateDefaultSubobject<UAudioComponent>(TEXT("Crackle"));
	Crackle->SetupAttachment(Root);
	Crackle->bAutoActivate = false; // plays in the game only, never in the editor viewport
}

void ARPGFireSource::Apply()
{
	Light->SetRelativeLocation(FVector(0.f, 0.f, LightHeight));
	Light->SetLightColor(LightColor);
	Light->SetIntensity(BaseIntensity);
	Light->SetAttenuationRadius(AttenuationRadius);
	Light->SetCastShadows(bCastShadows);
	if (FireTemplate)
	{
		Fire->SetTemplate(FireTemplate);
	}
	if (SmokeTemplate)
	{
		Smoke->SetTemplate(SmokeTemplate);
	}
	if (SparkTemplate)
	{
		Sparks->SetTemplate(SparkTemplate);
	}
	for (UParticleSystemComponent* Component : {Fire.Get(), Smoke.Get(), Sparks.Get()})
	{
		Component->SetRelativeScale3D(FVector(FireScale));
	}
}

void ARPGFireSource::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	Apply();
}

void ARPGFireSource::BeginPlay()
{
	Super::BeginPlay();
	// A different phase per fire, so a ring of braziers never pulses in step.
	Seed = FMath::FRandRange(0.f, 100.f);
	Apply();
	if (CrackleSound)
	{
		Crackle->SetSound(CrackleSound);
		Crackle->SetVolumeMultiplier(CrackleVolume * FMath::RandRange(0.85f, 1.1f));
		Crackle->bOverrideAttenuation = true;
		Crackle->AttenuationOverrides.bAttenuate = true;
		Crackle->AttenuationOverrides.bSpatialize = true;
		Crackle->AttenuationOverrides.AttenuationShape = EAttenuationShape::Sphere;
		Crackle->AttenuationOverrides.AttenuationShapeExtents = FVector(150.f, 0.f, 0.f);
		Crackle->AttenuationOverrides.FalloffDistance = CrackleRange;
		Crackle->Play(FMath::FRandRange(0.f, 3.f)); // start each fire at a different point of the loop
	}
}

void ARPGFireSource::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	Clock += DeltaSeconds * FlickerSpeed;
	const float T = Seed + Clock;
	// Two noise octaves: a slow swell plus a fast flutter.
	const float Noise = 0.65f * FMath::PerlinNoise1D(T * 0.5f) + 0.35f * FMath::PerlinNoise1D(T * 2.7f + 11.f);
	Light->SetIntensity(BaseIntensity * FMath::Max(0.1f, 1.f + FlickerAmount * Noise * 1.6f));
	// Hotter and whiter when bright, redder when low.
	const float Heat = FMath::Clamp(0.5f + Noise * 0.5f, 0.f, 1.f);
	Light->SetLightColor(FMath::Lerp(LightColor * FLinearColor(1.f, 0.7f, 0.5f), LightColor * FLinearColor(1.f, 1.15f, 1.3f), Heat));
	Light->SetRelativeLocation(FVector(WanderCm * FMath::PerlinNoise1D(T * 1.3f + 3.f), WanderCm * FMath::PerlinNoise1D(T * 1.1f + 7.f), LightHeight + WanderCm * 0.5f * Noise));
}

void ARPGFireSource::Rebuild()
{
	RerunConstructionScripts();
}
