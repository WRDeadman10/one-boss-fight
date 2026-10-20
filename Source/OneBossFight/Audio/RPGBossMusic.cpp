// Copyright One Boss Fight. All Rights Reserved.

#include "Audio/RPGBossMusic.h"
#include "Components/AudioComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Pack/RPGBlueprintCall.h"
#include "Player/RPGBossEncounter.h"
#include "Sound/SoundBase.h"

URPGBossMusic::URPGBossMusic()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickInterval = 0.25f;
}

void URPGBossMusic::BeginPlay()
{
	Super::BeginPlay();
	Encounter = GetOwner() ? GetOwner()->FindComponentByClass<URPGBossEncounter>() : nullptr;
}

void URPGBossMusic::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	if (Player)
	{
		Player->Stop();
	}
	Super::EndPlay(EndPlayReason);
}

void URPGBossMusic::Start()
{
	if (!Music || bPlaying)
	{
		return;
	}
	if (!Player)
	{
		Player = UGameplayStatics::CreateSound2D(this, Music, Volume, 1.f, 0.f, nullptr, /*bPersistAcrossLevelTransition=*/false, /*bAutoDestroy=*/false);
	}
	if (Player)
	{
		Player->FadeIn(FadeInSeconds, Volume); // null when no audio device exists (-nosound): the state is still tracked
	}
	bPlaying = true;
}

void URPGBossMusic::Stop()
{
	if (bPlaying && Player)
	{
		Player->FadeOut(FadeOutSeconds, 0.f);
	}
	bPlaying = false;
}

void URPGBossMusic::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	AActor* Boss = GetOwner();
	if (Boss && !Encounter)
	{
		Encounter = Boss->FindComponentByClass<URPGBossEncounter>(); // added after this component by the subsystem
	}
	if (!Boss || !Encounter)
	{
		return;
	}
	double Health = 1.0;
	const bool bHaveHealth = RPGPack::ReadAttribute(Boss, TEXT("Attribute.Health"), /*bMax=*/false, Health);
	const bool bDead = bHaveHealth && Health <= 0.0;
	if (!Encounter->IsDormant() && !bDead)
	{
		Start();
	}
	else
	{
		Stop();
	}
}
