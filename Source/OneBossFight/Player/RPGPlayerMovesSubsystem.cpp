// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGPlayerMovesSubsystem.h"
#include "Player/RPGDodgeTiming.h"
#include "Player/RPGBossStagger.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossPhases.h"
#include "Player/RPGAttackTracker.h"
#include "Player/RPGRiposteInput.h"
#include "Player/RPGBossPosture.h"
#include "Player/RPGCombatDebug.h"
#include "UI/RPGBossHud.h"
#include "Audio/RPGBossMusic.h"
#include "Audio/RPGFootsteps.h"
#include "Sound/SoundBase.h"
#include "EngineUtils.h"
#include "GameFramework/Pawn.h"
#include "Engine/World.h"

bool URPGPlayerMovesSubsystem::ShouldCreateSubsystem(UObject* Outer) const
{
	const UWorld* World = Cast<UWorld>(Outer);
	return World && World->IsGameWorld();
}

void URPGPlayerMovesSubsystem::PostInitialize()
{
	Super::PostInitialize();
	if (UWorld* World = GetWorld())
	{
		SpawnHandle = World->AddOnActorSpawnedHandler(FOnActorSpawned::FDelegate::CreateUObject(this, &URPGPlayerMovesSubsystem::OnActorSpawned));
	}
}

void URPGPlayerMovesSubsystem::OnWorldBeginPlay(UWorld& InWorld)
{
	Super::OnWorldBeginPlay(InWorld);
	// Pawns that exist already (placed in the level or spawned before the handler).
	for (TActorIterator<APawn> It(&InWorld); It; ++It)
	{
		Attach(*It);
	}
}

void URPGPlayerMovesSubsystem::Deinitialize()
{
	if (UWorld* World = GetWorld())
	{
		World->RemoveOnActorSpawnedHandler(SpawnHandle);
	}
	Super::Deinitialize();
}

void URPGPlayerMovesSubsystem::OnActorSpawned(AActor* Actor)
{
	Attach(Actor);
}

bool URPGPlayerMovesSubsystem::IsPackPlayer(const AActor* Actor)
{
	// The pack is Blueprint only: match the class or one of its parents by name.
	for (const UClass* Class = Actor ? Actor->GetClass() : nullptr; Class; Class = Class->GetSuperClass())
	{
		if (Class->GetName() == TEXT("BP_CombatPlayerCharacter_C"))
		{
			return true;
		}
	}
	return false;
}

bool URPGPlayerMovesSubsystem::IsPackBoss(const AActor* Actor)
{
	for (const UClass* Class = Actor ? Actor->GetClass() : nullptr; Class; Class = Class->GetSuperClass())
	{
		if (Class->GetName() == TEXT("BP_ExampleGreatSwordBoss_C"))
		{
			return true;
		}
	}
	return false;
}

namespace
{
	// Concrete boot steps from the Essential Footsteps pack (the arena floor is stone).
	USoundBase* StepSound(const TCHAR* Name)
	{
		return LoadObject<USoundBase>(nullptr, *FString::Printf(TEXT("/Game/Essential_Foosteps_SK/CUE/Concrete/%s.%s"), Name, Name));
	}

	void AddFootsteps(AActor* Pawn, bool bBoss)
	{
		if (Pawn->FindComponentByClass<URPGFootsteps>())
		{
			return;
		}
		URPGFootsteps* Steps = NewObject<URPGFootsteps>(Pawn, TEXT("RPGFootsteps"));
		Steps->WalkSound = StepSound(TEXT("Footstep_Concrete_Boots_Walk_1_Cue"));
		Steps->JogSound = StepSound(TEXT("Footstep_Concrete_Boots_Jog_8_Cue"));
		Steps->RunSound = StepSound(TEXT("Footstep_Concrete_Boots_Run_8_Cue"));
		Steps->LandSound = StepSound(TEXT("Footstep_Concrete_Boots_Land_4_Cue"));
		if (bBoss)
		{
			// A giant: deeper, louder, heard from further away.
			Steps->PitchScale = 0.62f;
			Steps->VolumeScale = 1.5f;
			Steps->AudibleRange = 4500.f;
			Steps->JogSpeed = 200.f;
			Steps->RunSpeed = 420.f;
		}
		Steps->RegisterComponent();
	}
}

void URPGPlayerMovesSubsystem::Attach(AActor* Pawn) const
{
	if (IsPackPlayer(Pawn))
	{
		AddFootsteps(Pawn, false);
	}
	else if (IsPackBoss(Pawn))
	{
		AddFootsteps(Pawn, true);
		if (!Pawn->FindComponentByClass<URPGBossMusic>())
		{
			URPGBossMusic* Music = NewObject<URPGBossMusic>(Pawn, TEXT("RPGBossMusic"));
			// Placeholder until a real boss track is licensed.
			Music->Music = LoadObject<USoundBase>(nullptr, TEXT("/Game/StarterContent/Audio/Starter_Music_Cue.Starter_Music_Cue"));
			Music->RegisterComponent();
		}
	}

	if (IsPackPlayer(Pawn) && !Pawn->FindComponentByClass<URPGRiposteInput>())
	{
		URPGRiposteInput* Riposte = NewObject<URPGRiposteInput>(Pawn, TEXT("RPGRiposteInput"));
		Riposte->RegisterComponent();
	}
	if (IsPackPlayer(Pawn) && !Pawn->FindComponentByClass<URPGDodgeTiming>())
	{
		URPGDodgeTiming* Timing = NewObject<URPGDodgeTiming>(Pawn, TEXT("RPGDodgeTiming"));
		Timing->RegisterComponent();
	}
	else if (IsPackBoss(Pawn) && !Pawn->FindComponentByClass<URPGBossStagger>())
	{
		URPGBossStagger* Stagger = NewObject<URPGBossStagger>(Pawn, TEXT("RPGBossStagger"));
		Stagger->RegisterComponent();
	}
	if (IsPackBoss(Pawn) && !Pawn->FindComponentByClass<URPGBossPhases>())
	{
		URPGBossPhases* Phases = NewObject<URPGBossPhases>(Pawn, TEXT("RPGBossPhases"));
		Phases->RegisterComponent();
	}
	if (IsPackBoss(Pawn) && !Pawn->FindComponentByClass<URPGBossEncounter>())
	{
		URPGBossEncounter* Encounter = NewObject<URPGBossEncounter>(Pawn, TEXT("RPGBossEncounter"));
		Encounter->RegisterComponent();
	}
	if (IsPackBoss(Pawn) && !Pawn->FindComponentByClass<URPGBossPosture>())
	{
		URPGBossPosture* Posture = NewObject<URPGBossPosture>(Pawn, TEXT("RPGBossPosture"));
		Posture->RegisterComponent();
	}
	if (IsPackBoss(Pawn) && !Pawn->FindComponentByClass<URPGAttackTracker>())
	{
		URPGAttackTracker* Tracker = NewObject<URPGAttackTracker>(Pawn, TEXT("RPGAttackTracker"));
		Tracker->RegisterComponent();
	}
	if (IsPackBoss(Pawn) && !Pawn->FindComponentByClass<URPGBossHud>())
	{
		URPGBossHud* Hud = NewObject<URPGBossHud>(Pawn, TEXT("RPGBossHud"));
		Hud->RegisterComponent();
	}
	if (IsPackBoss(Pawn) && !Pawn->FindComponentByClass<URPGCombatDebug>())
	{
		// Shows nothing until the console variable rpg.Debug is above 0.
		URPGCombatDebug* Debug = NewObject<URPGCombatDebug>(Pawn, TEXT("RPGCombatDebug"));
		Debug->RegisterComponent();
	}
}
