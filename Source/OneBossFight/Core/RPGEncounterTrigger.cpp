// Copyright One Boss Fight. All Rights Reserved.

#include "Core/RPGEncounterTrigger.h"
#include "Characters/RPGPlayerCharacter.h"
#include "Components/BoxComponent.h"
#include "Core/RPGEncounterSubsystem.h"
#include "Engine/World.h"

ARPGEncounterTrigger::ARPGEncounterTrigger()
{
	PrimaryActorTick.bCanEverTick = false;

	Volume = CreateDefaultSubobject<UBoxComponent>(TEXT("Volume"));
	Volume->SetBoxExtent(FVector(300.f, 600.f, 200.f));
	Volume->SetCollisionProfileName(TEXT("OverlapOnlyPawn"));
	Volume->SetGenerateOverlapEvents(true);
	SetRootComponent(Volume);
}

void ARPGEncounterTrigger::BeginPlay()
{
	Super::BeginPlay();
	Volume->OnComponentBeginOverlap.AddUniqueDynamic(this, &ARPGEncounterTrigger::HandleOverlap);

	if (URPGEncounterSubsystem* Encounter = GetWorld()->GetSubsystem<URPGEncounterSubsystem>())
	{
		Encounter->OnEncounterReset.AddUObject(this, &ARPGEncounterTrigger::Rearm);
	}
}

void ARPGEncounterTrigger::HandleOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp,
	int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	if (!Cast<ARPGPlayerCharacter>(OtherActor))
	{
		return;
	}
	if (URPGEncounterSubsystem* Encounter = GetWorld()->GetSubsystem<URPGEncounterSubsystem>())
	{
		Encounter->StartEncounter();
	}
}

void ARPGEncounterTrigger::Rearm()
{
	// The player is teleported back to the start; if they were standing inside (a short arena) overlap
	// would not fire again, so re-test the overlaps that exist now.
	TArray<AActor*> Overlapping;
	Volume->GetOverlappingActors(Overlapping, ARPGPlayerCharacter::StaticClass());
	if (Overlapping.Num() > 0)
	{
		if (URPGEncounterSubsystem* Encounter = GetWorld()->GetSubsystem<URPGEncounterSubsystem>())
		{
			Encounter->StartEncounter();
		}
	}
}
