// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGPlayerMovesSubsystem.h"
#include "Combat/RPGInputTestUtils.h"
#include "Player/RPGDodgeTiming.h"
#include "Player/RPGIFrameMonitor.h"
#include "Player/RPGHitIntake.h"
#include "Player/RPGSwingTracker.h"
#include "Player/RPGBuildLoadout.h"
#include "Player/RPGBossStagger.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossPhases.h"
#include "Player/RPGAttackTracker.h"
#include "Player/RPGRiposteInput.h"
#include "Player/RPGBossBleed.h"
#include "Player/RPGBossLook.h"
#include "Player/RPGBossDeath.h"
#include "Player/RPGBossPosture.h"
#include "Player/RPGCameraRig.h"
#include "Player/RPGBossShockwave.h"
#include "Player/RPGBossLowSweep.h"
#include "Player/RPGBossHealPunish.h"
#include "Player/RPGDamageResolver.h"
#include "Player/RPGTraceAudit.h"
#include "Player/RPGTraceGuard.h"
#include "Player/RPGCombatDebug.h"
#include "Player/RPGLegend.h"
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
	URPGInputTestUtils::RestoreFixedFrameRate(); // a driver that was cut must not leave the editor at 30 FPS
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
			// The two tracks of the fight (Scripts/Editor/import_audio.py imports them). A missing Phase 1 file falls back to the starter cue with a warning; a missing Phase 2 file means no swap.
			Music->Music = LoadObject<USoundBase>(nullptr, TEXT("/Game/OneBossFight/Audio/MX_Boss01_Phase1.MX_Boss01_Phase1"), nullptr, LOAD_NoWarn);
			if (!Music->Music)
			{
				UE_LOG(LogTemp, Warning, TEXT("Boss music: /Game/OneBossFight/Audio/MX_Boss01_Phase1 is not imported, the starter cue plays instead (run Scripts/Editor/import_audio.py)"));
				Music->Music = LoadObject<USoundBase>(nullptr, TEXT("/Game/StarterContent/Audio/Starter_Music_Cue.Starter_Music_Cue"));
			}
			Music->PhaseTwoMusic = LoadObject<USoundBase>(nullptr, TEXT("/Game/OneBossFight/Audio/MX_Boss01_Phase2.MX_Boss01_Phase2"), nullptr, LOAD_NoWarn);
			Music->RegisterComponent();
		}
	}

	if (IsPackPlayer(Pawn) && !Pawn->FindComponentByClass<URPGCameraRig>())
	{
		URPGCameraRig* Rig = NewObject<URPGCameraRig>(Pawn, TEXT("RPGCameraRig"));
		Rig->RegisterComponent();
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
	if (IsPackPlayer(Pawn) && !Pawn->FindComponentByClass<URPGSwingTracker>())
	{
		NewObject<URPGSwingTracker>(Pawn, TEXT("RPGSwingTracker"))->RegisterComponent(); // the swing of the player: weapon, kind, stamina cost from the weapon table (Gate 3)
	}
	if (IsPackPlayer(Pawn) && !Pawn->FindComponentByClass<URPGHitIntake>())
	{
		NewObject<URPGHitIntake>(Pawn, TEXT("RPGHitIntake"))->RegisterComponent(); // the record of every hit the player lands on the boss (Gate 3)
	}
	if (IsPackPlayer(Pawn) && !Pawn->FindComponentByClass<URPGBuildLoadout>())
	{
		NewObject<URPGBuildLoadout>(Pawn, TEXT("RPGBuildLoadout"))->RegisterComponent(); // the weapon of the chosen build (rpg.Build) before the fight, the weapon slot locked in it; nothing is called while no build is chosen (Gate 3, M13)
	}
	if (IsPackPlayer(Pawn) && !Pawn->FindComponentByClass<URPGIFrameMonitor>())
	{
		URPGIFrameMonitor* IFrames = NewObject<URPGIFrameMonitor>(Pawn, TEXT("RPGIFrameMonitor"));
		IFrames->RegisterComponent();
	}
	if (IsPackBoss(Pawn) && !Pawn->FindComponentByClass<URPGBossStagger>())
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
	if (IsPackBoss(Pawn))
	{
		URPGBossDeath::Attach(Pawn, ERPGBossDeathMode::OwnClip); // the death clip (G2-9): the component plays AN_Boss01_DeathLegend itself, holds the pose and keeps the pack's ragdoll off (the pack's ragdoll ability ignores DeathMontages: probe 2026-10-22, DEATH_CLIP_NOTES.md)
	}
	if (IsPackBoss(Pawn) && !Pawn->FindComponentByClass<URPGBossLook>())
	{
		NewObject<URPGBossLook>(Pawn, TEXT("RPGBossLook"))->RegisterComponent(); // the final look: Antigravity's body, crown, mantle, gauntlet and the greatsword on top of the pack mesh that keeps driving the fight (G2-15)
	}
	if (IsPackBoss(Pawn) && !Pawn->FindComponentByClass<URPGBossBleed>())
	{
		NewObject<URPGBossBleed>(Pawn, TEXT("RPGBossBleed"))->RegisterComponent(); // the hemorrhage status (Gate 3)
	}
	if (IsPackBoss(Pawn) && !Pawn->FindComponentByClass<URPGAttackTracker>())
	{
		URPGAttackTracker* Tracker = NewObject<URPGAttackTracker>(Pawn, TEXT("RPGAttackTracker"));
		Tracker->RegisterComponent();
	}
	if (IsPackBoss(Pawn) && !Pawn->FindComponentByClass<URPGBossShockwave>())
	{
		URPGBossShockwave* Wave = NewObject<URPGBossShockwave>(Pawn, TEXT("RPGBossShockwave"));
		Wave->RegisterComponent();
	}
	if (IsPackBoss(Pawn) && !Pawn->FindComponentByClass<URPGBossLowSweep>())
	{
		URPGBossLowSweep* Sweep = NewObject<URPGBossLowSweep>(Pawn, TEXT("RPGBossLowSweep"));
		Sweep->RegisterComponent();
	}
	if (IsPackBoss(Pawn) && !Pawn->FindComponentByClass<URPGBossHealPunish>())
	{
		URPGBossHealPunish* Punish = NewObject<URPGBossHealPunish>(Pawn, TEXT("RPGBossHealPunish"));
		Punish->RegisterComponent();
	}
	if (IsPackBoss(Pawn))
	{
		URPGDamageResolver::FindOrAdd(Pawn); // the one place that lowers the player's health for the boss's moves
		if (!Pawn->FindComponentByClass<URPGTraceGuard>())
		{
			NewObject<URPGTraceGuard>(Pawn, TEXT("RPGTraceGuard"))->RegisterComponent(); // closes the pack's weapon trace on every interrupt, carries the hit set per instance, blocks hits through walls
		}
		if (!Pawn->FindComponentByClass<URPGTraceAudit>())
		{
			NewObject<URPGTraceAudit>(Pawn, TEXT("RPGTraceAudit"))->RegisterComponent(); // observer: trace overlap versus damage accepted (empty in Shipping)
		}
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
	if (IsPackBoss(Pawn) && !Pawn->FindComponentByClass<URPGBossLegend>())
	{
		// The presentation layer (camera shake, hit stop, slow motion): after the tracker, phases, stagger and HUD it polls. Inert while rpg.Legend is 0.
		NewObject<URPGBossLegend>(Pawn, TEXT("RPGBossLegend"))->RegisterComponent();
	}
}
