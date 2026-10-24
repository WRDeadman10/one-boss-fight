// Copyright One Boss Fight. All Rights Reserved.

#include "Audio/RPGArenaAmbience.h"
#include "Components/AudioComponent.h"
#include "Components/SceneComponent.h"
#include "Sound/SoundBase.h"

ARPGArenaAmbience::ARPGArenaAmbience()
{
	PrimaryActorTick.bCanEverTick = false;
	USceneComponent* Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
	SetRootComponent(Root);

	WindPlayer = CreateDefaultSubobject<UAudioComponent>(TEXT("Wind"));
	WindPlayer->SetupAttachment(Root);
	WindPlayer->bAutoActivate = false;
	WindPlayer->bAllowSpatialization = false;
}

void ARPGArenaAmbience::Rebuild()
{
#if WITH_EDITOR // RerunConstructionScripts exists only in editor builds (the packaged game target failed to compile without this guard)
	RerunConstructionScripts();
#endif
}

void ARPGArenaAmbience::BeginPlay()
{
	Super::BeginPlay();
	if (Wind)
	{
		WindPlayer->SetSound(Wind);
		WindPlayer->SetVolumeMultiplier(WindVolume);
		WindPlayer->OnAudioFinished.AddDynamic(this, &ARPGArenaAmbience::OnWindFinished);
		WindPlayer->FadeIn(3.f, WindVolume);
	}
}

void ARPGArenaAmbience::OnWindFinished()
{
	if (WindPlayer && IsValid(this) && !IsActorBeingDestroyed())
	{
		WindPlayer->Play();
	}
}
