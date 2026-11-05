// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGPlayerMovesSubsystem.h"
#include "Player/RPGBossEncounterDefinition.h"

#include "Player/RPGEncounterSelectionSubsystem.h"
#include "Player/RPGEncounterBinding.h"
#include "Player/RPGBossActivation.h"
#include "Player/RPGEncounterGenerationRules.h"
#include "Player/RPGStartupChronology.h"
#include "Combat/RPGInputTestUtils.h"
#include "Player/RPGDodgeTiming.h"
#include "Player/RPGPlayerParry.h"
#include "Player/RPGIFrameMonitor.h"
#include "Player/RPGHitIntake.h"
#include "Player/RPGSwingTracker.h"
#include "Player/RPGBuildLoadout.h"
#include "Player/RPGBossStagger.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossDormantWake.h"
#include "Player/RPGBossPhases.h"
#include "Player/RPGAttackTracker.h"
#include "Player/RPGDevelopmentBuildStamp.h"
#include "Player/RPGBossCloseClipSwap.h"
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
#include "UI/RPGBuildSelect.h"
#include "UI/RPGFlaskHud.h"
#include "Audio/RPGBossMusic.h"
#include "Audio/RPGFootsteps.h"
#include "Sound/SoundBase.h"
#include "EngineUtils.h"
#include "GameFramework/Pawn.h"
#include "Engine/World.h"
#include "Engine/GameInstance.h"
#include "Engine/Engine.h"
#include "GameFramework/Actor.h"
#include "HAL/IConsoleManager.h"
#include "HAL/PlatformTime.h"
#include "TimerManager.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"

URPGPlayerMovesSubsystem* URPGPlayerMovesSubsystem::GetForWorld(const UObject* WorldContextObject)
{
	UWorld* World = WorldContextObject ? WorldContextObject->GetWorld() : nullptr;
	return World ? World->GetSubsystem<URPGPlayerMovesSubsystem>() : nullptr;
}
#include "Misc/ScopeExit.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGEncounterTiming, Log, All);

#if !UE_BUILD_SHIPPING
namespace
{
	void SetDeterminismSeed(const TArray<FString>& Arguments)
	{
		if (Arguments.Num() != 1)
		{
			UE_LOG(LogTemp, Warning, TEXT("[Determinism] usage: rpg.DeterminismSeed <unsigned-integer>"));
			return;
		}
		if (!Arguments[0].IsNumeric())
		{
			UE_LOG(LogTemp, Warning, TEXT("[Determinism] seed must contain decimal digits only"));
			return;
		}
		const uint64 ParsedSeed = FCString::Strtoui64(*Arguments[0], nullptr, 10);
		if (ParsedSeed > MAX_uint32)
		{
			UE_LOG(LogTemp, Warning, TEXT("[Determinism] seed is outside the uint32 range"));
			return;
		}
		const uint32 Seed = static_cast<uint32>(ParsedSeed);
		FMath::RandInit(static_cast<int32>(Seed));
		UE_LOG(LogTemp, Display, TEXT("[Determinism] global FMath random stream seeded with %u"), Seed);
	}

	FAutoConsoleCommand DeterminismSeedCommand(
		TEXT("rpg.DeterminismSeed"),
		TEXT("Development test hook: seed the global FMath random stream before a deterministic PIE repeat."),
		FConsoleCommandWithArgsDelegate::CreateStatic(&SetDeterminismSeed));
}

static TAutoConsoleVariable<int32> CVarEncounterSpawnGate(
	TEXT("rpg.EncounterLifecycle.SpawnGate"), 0,
	TEXT("Temporary diagnostic: 1 logs pack pawn spawn-gate state. 0 = off. Not compiled into Shipping."), ECVF_Default);
#endif

bool URPGPlayerMovesSubsystem::ShouldCreateSubsystem(UObject* Outer) const
{
	const UWorld* World = Cast<UWorld>(Outer);
	return World && World->IsGameWorld();
}

void URPGPlayerMovesSubsystem::PostInitialize()
{
	Super::PostInitialize();
	// Lead (BUILD-212): restored. The legacy spawn hook must be live before BeginPlay (AttachWitness/AbsentPreservesLegacyStartup
	// spawn pawns in worlds that never begin play); OnWorldBeginPlay only binds when this did not.
	if (UWorld* World = GetWorld())
	{
		SpawnHandle = World->AddOnActorSpawnedHandler(FOnActorSpawned::FDelegate::CreateUObject(this, &URPGPlayerMovesSubsystem::OnActorSpawned));
	}
}

void URPGPlayerMovesSubsystem::OnWorldBeginPlay(UWorld& InWorld)
{
	RPGDevelopmentBuildStamp::ShowIfAvailable(InWorld);
	// Bind at the world-begin-play boundary: transient test worlds can initialize the subsystem before their
	// actor-spawn delegate is ready, and all preexisting actors are handled by the census below.
	if (!SpawnHandle.IsValid())
	{
		SpawnHandle = InWorld.AddOnActorSpawnedHandler(FOnActorSpawned::FDelegate::CreateUObject(this, &URPGPlayerMovesSubsystem::OnActorSpawned));
	}
	RPGStartupChronology::AtWorldBeginPlay(InWorld);
	Super::OnWorldBeginPlay(InWorld);
	UGameInstance* GameInstance = InWorld.GetGameInstance();
	URPGEncounterSelectionSubsystem* Selection = GameInstance ? GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>() : nullptr;
	const bool bSelectionRequested = Selection && Selection->HasSelectionRequest();
	LastEncounterRoute = bSelectionRequested ? TEXT("data") : (bUseLegacyStartup ? TEXT("legacy") : TEXT("disabled"));
	LastEncounterOutcome = bSelectionRequested ? TEXT("Pending") : (bUseLegacyStartup ? TEXT("LegacyNoSelection") : TEXT("LegacyStartupDisabled"));
	LastEncounterReason.Reset();
	LastEncounterManifestHash.Reset();
	if (bSelectionRequested)
	{
		double OperationStartSeconds = 0.0;
		const uint64 OperationId = BeginEncounterTiming(TEXT("selected_startup"), OperationStartSeconds);
		ON_SCOPE_EXIT
		{
			EndEncounterTiming(OperationId, TEXT("selected_startup"), OperationStartSeconds, LastEncounterOutcome);
		};
		FString Error;
		TArray<RPGBossWorldInputCompiler::FSelection> Selections;
		ARPGEncounterBinding* Binding = nullptr;
		bool bReady = Selection->BuildWorldBinding(InWorld, Binding, Selections, Error);
		if (bReady)
		{
			for (TActorIterator<APawn> It(&InWorld); It; ++It)
			{
				if (IsPackBoss(*It) && !RemoveOwnedLegacyBossComponents(*It, Error))
				{
					bReady = false;
					break;
				}
			}
		}
		URPGBossEncounterDefinition* Definition = bReady ? Selection->ResolveSelectedDefinition(Error) : nullptr;
		if (Definition) { LastEncounterManifestHash = Definition->StableManifestHash; }
		if (bReady && Definition)
		{
			FRPGWorldActivationResult Attempt = RPGBossActivation::ActivateWorld(&InWorld, Binding, Selections, Definition->StableManifestHash);
			if (Attempt.Succeeded())
			{
				LastEncounterOutcome = TEXT("Activated");
				LastEncounterReason.Reset();
				ActiveTransientBinding = Binding;
				ActiveDataActivation = MoveTemp(Attempt);
				ActiveSelectionDefinition = Definition;
				ActiveManifestHash = Definition->StableManifestHash;
				ActiveEncounterInstance = Binding->EncounterInstance;
				ActiveBossSlot = Definition->BossSlot;
				ActivePlayerSlot = Definition->PlayerSlot;
				ActiveBossPhase = Definition->InitialBossPhase;
				ActiveBossDefinitionPath = Definition->BossDefinition.ToSoftObjectPath();
				ActivePlayerDefinitionPath = Definition->PlayerDefinition.ToSoftObjectPath();
				LastAcceptedParticipantGeneration = Binding->ParticipantGeneration;
				for (TActorIterator<APawn> It(&InWorld); It; ++It)
				{
					if (IsPackBoss(*It)) { BindResetBroadcast(*It); break; }
				}
			}
			else
			{
				Error = Attempt.Errors.IsEmpty() ? Attempt.Reason.ToString() : FString::Join(Attempt.Errors, TEXT("; "));
				if (Attempt.Batch.IsValid())
				{
					double ReleaseStartSeconds = 0.0;
					const uint64 ReleaseOperationId = BeginEncounterTiming(TEXT("activation_release_startup_refusal"), ReleaseStartSeconds);
					const FRPGPreparationAbortReport Release = Attempt.Release();
					EndEncounterTiming(ReleaseOperationId, TEXT("activation_release_startup_refusal"), ReleaseStartSeconds,
						Release.IsClean() ? TEXT("clean") : TEXT("refused"));
					if (!Release.Errors.IsEmpty()) { Error += TEXT("; cleanup: ") + FString::Join(Release.Errors, TEXT("; ")); }
				}
				if (IsValid(Binding)) Binding->Destroy();
				LastEncounterOutcome = TEXT("HardError");
				LastEncounterReason = Error;
				bReady = false;
			}
		}
		else
		{
			if (IsValid(Binding)) Binding->Destroy();
			bReady = false;
		}

		if (!bReady)
		{
			for (TActorIterator<APawn> It(&InWorld); It; ++It)
			{
				if (IsPackBoss(*It))
				{
					FString CleanupError;
					if (!RemoveOwnedLegacyBossComponents(*It, CleanupError)) { Error += TEXT("; ") + CleanupError; }
					DisableSelectedBoss(*It);
				}
			}
			LastEncounterOutcome = TEXT("HardError");
			LastEncounterReason = Error.IsEmpty() ? TEXT("EncounterActivation.Refused") : Error;
			ReportActivationFailure(&InWorld, LastEncounterReason);
		}
		// The player-side additions are independent of boss activation and remain available on refusal.
		for (TActorIterator<APawn> It(&InWorld); It; ++It)
		{
			AttachSelectedPlayerComponents(*It);
			AttachBossDiagnostics(*It);
		}
		return;
	}
	if (!bUseLegacyStartup)
	{
		UE_LOG(LogTemp, Display, TEXT("[EncounterActivation] outcome=LegacyStartupDisabled reason=Config.bUseLegacyStartupFalse"));
		return;
	}
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
		World->GetTimerManager().ClearTimer(RebindTimeoutHandle);
		World->GetTimerManager().ClearTimer(RebindPollHandle);
	}
	if (URPGBossEncounter* Source = ResetBroadcastSource.Get()) { Source->OnResetBroadcast().Remove(ResetBroadcastHandle); }
	ResetBroadcastSource.Reset();
	if (ActiveDataActivation.Batch.IsValid())
	{
		double ReleaseStartSeconds = 0.0;
		const uint64 ReleaseOperationId = BeginEncounterTiming(TEXT("activation_release_shutdown"), ReleaseStartSeconds);
		const FRPGPreparationAbortReport Release = ActiveDataActivation.ReleaseForRebind();
		EndEncounterTiming(ReleaseOperationId, TEXT("activation_release_shutdown"), ReleaseStartSeconds,
			Release.IsClean() ? TEXT("clean") : TEXT("refused"));
		for (const FString& Error : Release.Errors) { UE_LOG(LogTemp, Error, TEXT("[EncounterActivation] cleanup=%s"), *Error); }
	}
	if (AActor* Binding = ActiveTransientBinding.Get()) { Binding->Destroy(); }
	ActiveTransientBinding.Reset();
	LegacyBossComponents.Reset();
	if (UWorld* World = GetWorld())
	{
		World->RemoveOnActorSpawnedHandler(SpawnHandle);
	}
	Super::Deinitialize();
}

void URPGPlayerMovesSubsystem::OnActorSpawned(AActor* Actor)
{
	UWorld* World = GetWorld();
	UGameInstance* GameInstance = World ? World->GetGameInstance() : nullptr;
	URPGEncounterSelectionSubsystem* Selection = GameInstance ? GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>() : nullptr;
	const bool bSpawnIsPackPlayer = IsPackPlayer(Actor);
	const bool bSpawnIsPackBoss = IsPackBoss(Actor);
	const bool bWorldHasBegunPlay = World && World->HasBegunPlay();
	const bool bSelectionRequested = Selection && Selection->HasSelectionRequest();
	const bool bSelectedMode = LastAcceptedParticipantGeneration > 0 || bSelectionRequested;
	// Temporary BUILD-212 probe: distinguish a missing spawn callback from a skipped begun-world/player gate.
#if !UE_BUILD_SHIPPING
	if (CVarEncounterSpawnGate.GetValueOnGameThread() != 0 && (bSpawnIsPackPlayer || bSpawnIsPackBoss))
	{
		UE_LOG(LogTemp, Display, TEXT("[EncounterLifecycle] spawn_gate actor_id=%u actor_class=%s world_begun=%d pack_player=%d pack_boss=%d selection_requested=%d selected_mode=%d accepted_generation=%llu pending_valid=%d"),
			Actor ? static_cast<uint32>(Actor->GetUniqueID()) : 0u, Actor ? *Actor->GetClass()->GetPathName() : TEXT("<null>"),
			bWorldHasBegunPlay ? 1 : 0, bSpawnIsPackPlayer ? 1 : 0, bSpawnIsPackBoss ? 1 : 0, bSelectionRequested ? 1 : 0,
			bSelectedMode ? 1 : 0, static_cast<unsigned long long>(LastAcceptedParticipantGeneration), PendingRespawnPlayer.IsValid() ? 1 : 0);
	}
#endif
	if (World && World->HasBegunPlay() && IsPackPlayer(Actor))
	{
		uint64 Generation = 0;
		int32 ResetCount = 0;
		for (TActorIterator<APawn> It(World); It; ++It)
		{
			if (IsPackBoss(*It))
			{
				if (const URPGBossEncounter* Encounter = (*It)->FindComponentByClass<URPGBossEncounter>())
				{
					Generation = Encounter->GetParticipantGeneration();
					ResetCount = Encounter->GetResetCount();
				}
				break;
			}
		}
		UE_LOG(LogTemp, Display, TEXT("[EncounterLifecycle] spawn_player timestamp=%.6f generation=%llu reset_count=%d actor_id=%u"),
			FPlatformTime::Seconds(), static_cast<unsigned long long>(Generation), ResetCount, static_cast<uint32>(Actor->GetUniqueID()));
	}
	if (bSelectedMode)
	{
		if (LastAcceptedParticipantGeneration > 0 && World && World->HasBegunPlay() && IsPackPlayer(Actor))
		{
			// Respawn can precede possession and the reset broadcast. Remember the spawn, but let the reset event own the bounded rebind window.
			PendingRespawnPlayer = Actor;
			UE_LOG(LogTemp, Display, TEXT("[EncounterLifecycle] rebind_spawn_seen timestamp=%.6f generation=%llu actor_id=%u waiting_for_reset_broadcast=%d"),
				FPlatformTime::Seconds(), static_cast<unsigned long long>(LastAcceptedParticipantGeneration), static_cast<uint32>(Actor->GetUniqueID()), PendingRebindGeneration == 0 ? 1 : 0);
		}
		else if (LastAcceptedParticipantGeneration > 0 && World && World->HasBegunPlay() && IsPackBoss(Actor))
		{
			FailSelectedRebind(TEXT("EncounterActivation.LateBossSpawn"), true);
		}
		else if (World && World->HasBegunPlay() && IsPackBoss(Actor))
		{
			DisableSelectedBoss(Actor);
			ReportActivationFailure(World, TEXT("EncounterActivation.SelectedRouteUnavailable"));
		}
		if (IsPackPlayer(Actor)) { AttachSelectedPlayerComponents(Actor); }
		AttachBossDiagnostics(Actor);
		return;
	}
	if (!bUseLegacyStartup) return;
	Attach(Actor);
}

void URPGPlayerMovesSubsystem::BindResetBroadcast(AActor* Boss)
{
	URPGBossEncounter* Encounter = IsValid(Boss) ? Boss->FindComponentByClass<URPGBossEncounter>() : nullptr;
	if (!Encounter)
	{
		FailSelectedRebind(TEXT("EncounterActivation.ResetSourceUnavailable"), true);
		return;
	}
	ResetBroadcastSource = Encounter;
	ResetBroadcastHandle = Encounter->OnResetBroadcast().AddUObject(this, &URPGPlayerMovesSubsystem::OnEncounterResetBroadcast);
}

void URPGPlayerMovesSubsystem::OnRebindTimeout()
{
	double OperationStartSeconds = 0.0;
	const uint64 OperationId = BeginEncounterTiming(TEXT("selected_rebind_timeout"), OperationStartSeconds);
	ON_SCOPE_EXIT
	{
		EndEncounterTiming(OperationId, TEXT("selected_rebind_timeout"), OperationStartSeconds, LastEncounterOutcome);
	};
	if (PendingRebindGeneration != 0)
	{
		FailSelectedRebind(TEXT("EncounterActivation.RebindTimeout"), true);
	}
}

void URPGPlayerMovesSubsystem::OnRebindPoll()
{
	if (PendingRebindGeneration == 0) { return; }
	UWorld* World = GetWorld();
	if (!World)
	{
		FailSelectedRebind(TEXT("EncounterActivation.RebindWorldMissing"), true);
		return;
	}
	APawn* CandidatePlayer = nullptr;
	if (RPGEncounterPlayerIdentity::CountLocalPossessedPlayers(*World, CandidatePlayer) == 0) { return; }
	const uint64 Generation = PendingRebindGeneration;
	const int32 ResetCount = PendingRebindResetCount;
	World->GetTimerManager().ClearTimer(RebindPollHandle);
	OnEncounterResetBroadcast(Generation, ResetCount);
}

void URPGPlayerMovesSubsystem::FailSelectedRebind(const FString& Reason, bool bReleaseCurrentActivation)
{
	double OperationStartSeconds = 0.0;
	const uint64 OperationId = BeginEncounterTiming(TEXT("selected_rebind_refusal"), OperationStartSeconds);
	ON_SCOPE_EXIT
	{
		EndEncounterTiming(OperationId, TEXT("selected_rebind_refusal"), OperationStartSeconds, LastEncounterOutcome);
	};
	UWorld* World = GetWorld();
	if (World)
	{
		World->GetTimerManager().ClearTimer(RebindTimeoutHandle);
		World->GetTimerManager().ClearTimer(RebindPollHandle);
	}
	if (URPGBossEncounter* Source = ResetBroadcastSource.Get()) { Source->OnResetBroadcast().Remove(ResetBroadcastHandle); }
	ResetBroadcastSource.Reset();
	FString FullReason = Reason;
	bool bReleaseClean = true;
	if (bReleaseCurrentActivation && ActiveDataActivation.Batch.IsValid())
	{
		double ReleaseStartSeconds = 0.0;
		const uint64 ReleaseOperationId = BeginEncounterTiming(TEXT("activation_release_failure"), ReleaseStartSeconds);
		const FRPGPreparationAbortReport Release = ActiveDataActivation.ReleaseForRebind();
		EndEncounterTiming(ReleaseOperationId, TEXT("activation_release_failure"), ReleaseStartSeconds,
			Release.IsClean() ? TEXT("clean") : TEXT("refused"));
		bReleaseClean = Release.IsClean();
		for (const FString& Error : Release.Errors) { FullReason += TEXT("; cleanup: ") + Error; }
	}
	if (bReleaseCurrentActivation && bReleaseClean)
	{
		if (AActor* Binding = ActiveTransientBinding.Get()) { Binding->Destroy(); }
		ActiveTransientBinding.Reset();
	}
	if (World)
	{
		for (TActorIterator<APawn> It(World); It; ++It) { if (IsPackBoss(*It)) { DisableSelectedBoss(*It); } }
	}
	PendingRespawnPlayer.Reset();
	PendingRebindGeneration = 0;
	PendingRebindResetCount = 0;
	LastEncounterOutcome = TEXT("HardError");
	LastEncounterReason = FullReason;
	ReportActivationFailure(World, FullReason);
}

void URPGPlayerMovesSubsystem::OnEncounterResetBroadcast(uint64 ParticipantGeneration, int32 ResetCount)
{
	double OperationStartSeconds = 0.0;
	const uint64 OperationId = BeginEncounterTiming(TEXT("selected_rebind"), OperationStartSeconds);
	FString TimingOutcome = TEXT("InProgress");
	ON_SCOPE_EXIT
	{
		EndEncounterTiming(OperationId, TEXT("selected_rebind"), OperationStartSeconds,
			TimingOutcome == TEXT("InProgress") ? LastEncounterOutcome : TimingOutcome);
	};
	if (ParticipantGeneration == LastAcceptedParticipantGeneration)
	{
		TimingOutcome = TEXT("DuplicateNoOp");
		UE_LOG(LogTemp, Display, TEXT("[EncounterLifecycle] rebind_duplicate timestamp=%.6f generation=%llu reset_count=%d"),
			FPlatformTime::Seconds(), static_cast<unsigned long long>(ParticipantGeneration), ResetCount);
		return;
	}
	FString GenerationError;
	if (!RPGEncounterGenerationRules::CanAdvance(LastAcceptedParticipantGeneration, ParticipantGeneration, GenerationError))
	{
		FailSelectedRebind(GenerationError, true);
		return;
	}
	UWorld* World = GetWorld();
	if (!World)
	{
		FailSelectedRebind(TEXT("EncounterActivation.RebindWorldMissing"), true);
		return;
	}
	APawn* CandidatePlayer = nullptr;
	const int32 AuthoritativePlayerCount = RPGEncounterPlayerIdentity::CountLocalPossessedPlayers(*World, CandidatePlayer);
	if (AuthoritativePlayerCount == 0)
	{
		PendingRebindGeneration = ParticipantGeneration;
		PendingRebindResetCount = ResetCount;
		if (!World->GetTimerManager().IsTimerActive(RebindTimeoutHandle))
		{
			World->GetTimerManager().SetTimer(RebindTimeoutHandle, this, &URPGPlayerMovesSubsystem::OnRebindTimeout, 5.0f, false);
		}
		if (!World->GetTimerManager().IsTimerActive(RebindPollHandle))
		{
			World->GetTimerManager().SetTimer(RebindPollHandle, this, &URPGPlayerMovesSubsystem::OnRebindPoll, 0.05f, true);
		}
		TimingOutcome = TEXT("PendingPlayerPossession");
		UE_LOG(LogTemp, Display, TEXT("[EncounterLifecycle] rebind_pending_possession timestamp=%.6f generation=%llu reset_count=%d timeout_seconds=5"),
			FPlatformTime::Seconds(), static_cast<unsigned long long>(ParticipantGeneration), ResetCount);
		return;
	}
	if (AuthoritativePlayerCount != 1)
	{
		FailSelectedRebind(TEXT("EncounterActivation.RebindAmbiguousPlayer"), true);
		return;
	}

	// Stop receiving callbacks from the old lease while the replacement binding is validated.
	if (URPGBossEncounter* Source = ResetBroadcastSource.Get()) { Source->OnResetBroadcast().Remove(ResetBroadcastHandle); }
	ResetBroadcastSource.Reset();

	UGameInstance* GameInstance = World->GetGameInstance();
	URPGEncounterSelectionSubsystem* Selection = GameInstance ? GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>() : nullptr;
	FString Error;
	URPGBossEncounterDefinition* Definition = Selection ? Selection->ResolveSelectedDefinition(Error) : nullptr;
	if (!Definition || Definition != ActiveSelectionDefinition.Get() || Definition->StableManifestHash != ActiveManifestHash
		|| Definition->EncounterInstance != ActiveEncounterInstance || Definition->BossSlot != ActiveBossSlot
		|| Definition->PlayerSlot != ActivePlayerSlot || Definition->InitialBossPhase != ActiveBossPhase
		|| Definition->BossDefinition.ToSoftObjectPath() != ActiveBossDefinitionPath
		|| Definition->PlayerDefinition.ToSoftObjectPath() != ActivePlayerDefinitionPath)
	{
		FailSelectedRebind(Error.IsEmpty() ? TEXT("EncounterActivation.SelectionChanged") : Error, true);
		return;
	}

	ARPGEncounterBinding* Binding = nullptr;
	TArray<RPGBossWorldInputCompiler::FSelection> Selections;
	if (!Selection->BuildWorldBindingForRebind(*World, ParticipantGeneration, ResetCount, Binding, Selections, Error))
	{
		if (IsValid(Binding)) { Binding->Destroy(); }
		FailSelectedRebind(Error.IsEmpty() ? TEXT("EncounterActivation.RebindCensus") : Error, true);
		return;
	}
	const bool bCandidateBound = Binding->Participants.ContainsByPredicate([&](const FRPGPlacedParticipantBinding& Participant)
	{
		return Participant.Slot == ActivePlayerSlot && Participant.Actor.Get() == CandidatePlayer;
	});
	if (!bCandidateBound)
	{
		Binding->Destroy();
		FailSelectedRebind(TEXT("EncounterActivation.RebindPlayerMissing"), true);
		return;
	}
	if (!ActiveDataActivation.RetagForRebind(*Binding, LastAcceptedParticipantGeneration, Error))
	{
		Binding->Destroy();
		FailSelectedRebind(Error.IsEmpty() ? TEXT("EncounterActivation.RebindRetag") : Error, true);
		return;
	}
	if (AActor* OldBinding = ActiveTransientBinding.Get()) { OldBinding->Destroy(); }
	ActiveTransientBinding = Binding;
	LastEncounterOutcome = TEXT("Activated");
	LastEncounterReason.Reset();
	LastAcceptedParticipantGeneration = ParticipantGeneration;
	World->GetTimerManager().ClearTimer(RebindTimeoutHandle);
	World->GetTimerManager().ClearTimer(RebindPollHandle);
	PendingRespawnPlayer.Reset();
	PendingRebindGeneration = 0;
	PendingRebindResetCount = 0;
	for (TActorIterator<APawn> It(World); It; ++It)
	{
		if (IsPackBoss(*It)) { BindResetBroadcast(*It); break; }
	}
	UE_LOG(LogTemp, Display, TEXT("[EncounterLifecycle] rebind_activated timestamp=%.6f generation=%llu reset_count=%d"),
		FPlatformTime::Seconds(), static_cast<unsigned long long>(ParticipantGeneration), ResetCount);
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

FString URPGPlayerMovesSubsystem::BuildEncounterParitySnapshot() const
{
	const UWorld* World = GetWorld();
	const ARPGEncounterBinding* Binding = Cast<ARPGEncounterBinding>(ActiveTransientBinding.Get());   // the weak pointer is typed AActor
	const bool bHasBinding = IsValid(Binding);
	const bool bSelected = LastEncounterRoute == TEXT("data");

	TSharedRef<FJsonObject> Root = MakeShared<FJsonObject>();
	Root->SetStringField(TEXT("schema"), TEXT("onebossfight.encounter-runtime-snapshot/v1"));
	Root->SetStringField(TEXT("world"), World ? World->GetPathName() : FString());
	Root->SetStringField(TEXT("route"), LastEncounterRoute);
	Root->SetStringField(TEXT("participant_generation"),
		bHasBinding ? FString::Printf(TEXT("%llu"), static_cast<unsigned long long>(Binding->ParticipantGeneration))
			: (LastAcceptedParticipantGeneration > 0
				? FString::Printf(TEXT("%llu"), static_cast<unsigned long long>(LastAcceptedParticipantGeneration)) : FString()));
	Root->SetNumberField(TEXT("reset_count"), bHasBinding ? Binding->ResetCount : 0);

	TSharedRef<FJsonObject> Selection = MakeShared<FJsonObject>();
	Selection->SetBoolField(TEXT("selected"), bSelected);
	Selection->SetStringField(TEXT("definition"), bHasBinding ? Binding->SelectionDefinitionPath : FString());
	Selection->SetStringField(TEXT("manifest_sha256"), bHasBinding ? Binding->StableManifestHash : LastEncounterManifestHash);
	Selection->SetStringField(TEXT("encounter_instance"), bHasBinding ? Binding->EncounterInstance.ToString() : FString());
	Selection->SetStringField(TEXT("boss_slot"), bHasBinding ? Binding->BossSlot.ToString() : ActiveBossSlot.ToString());
	Selection->SetStringField(TEXT("player_slot"), bHasBinding ? Binding->PlayerSlot.ToString() : ActivePlayerSlot.ToString());
	Selection->SetStringField(TEXT("initial_boss_phase"), bHasBinding ? Binding->InitialBossPhase.ToString() : ActiveBossPhase.ToString());
	if (!bHasBinding && bSelected)
	{
		if (UGameInstance* GameInstance = World ? World->GetGameInstance() : nullptr)
		{
			if (const URPGEncounterSelectionSubsystem* Store = GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>())
			{
				Selection->SetStringField(TEXT("definition"), Store->GetRequestedDefinitionPathForDiagnostics());
				if (LastEncounterManifestHash.IsEmpty())
				{
					Selection->SetStringField(TEXT("manifest_sha256"), Store->GetRequestedManifestHashForDiagnostics());
				}
			}
		}
	}
	Root->SetObjectField(TEXT("selection"), Selection);

	TSharedRef<FJsonObject> Activation = MakeShared<FJsonObject>();
	Activation->SetStringField(TEXT("outcome"), LastEncounterOutcome);
	Activation->SetStringField(TEXT("reason"), LastEncounterReason);
	Activation->SetBoolField(TEXT("lease_held"), ActiveDataActivation.IsHeld());
	Activation->SetBoolField(TEXT("binding_retained"), bHasBinding);
	Root->SetObjectField(TEXT("activation"), Activation);

	TArray<TSharedPtr<FJsonValue>> ParticipantRows;
	TSharedRef<FJsonObject> ComponentCensus = MakeShared<FJsonObject>();
	for (const TCHAR* RoleName : {TEXT("boss"), TEXT("player")})
	{
		TArray<TSharedPtr<FJsonValue>> ComponentsForRole;
		if (bHasBinding)
		{
			const FName RoleSlot = FCString::Stricmp(RoleName, TEXT("boss")) == 0 ? Binding->BossSlot : Binding->PlayerSlot;
			for (const FRPGPlacedParticipantBinding& Participant : Binding->Participants)
			{
				if (Participant.Slot != RoleSlot) { continue; }
				const AActor* Actor = Participant.Actor;
				TSharedRef<FJsonObject> Row = MakeShared<FJsonObject>();
				Row->SetStringField(TEXT("role"), RoleName);
				Row->SetStringField(TEXT("slot"), Participant.Slot.ToString());
				Row->SetStringField(TEXT("target_slot"), Participant.TargetSlot.ToString());
				Row->SetStringField(TEXT("actor_class"), IsValid(Actor) ? Actor->GetClass()->GetPathName() : FString());
				Row->SetStringField(TEXT("actor_id"), IsValid(Actor) ? Actor->GetPathName() : FString());
				Row->SetStringField(TEXT("participant_generation"),
					FString::Printf(TEXT("%llu"), static_cast<unsigned long long>(Binding->ParticipantGeneration)));
				Row->SetNumberField(TEXT("reset_count"), Binding->ResetCount);
				Row->SetStringField(TEXT("definition"), IsValid(Participant.Definition) ? Participant.Definition->GetPathName() : FString());
				ParticipantRows.Add(MakeShared<FJsonValueObject>(Row));
				if (IsValid(Actor))
				{
					TArray<UActorComponent*> ActorComponents;
					Actor->GetComponents(ActorComponents);
					for (const UActorComponent* Component : ActorComponents)
					{
						if (IsValid(Component)) { ComponentsForRole.Add(MakeShared<FJsonValueString>(Component->GetPathName())); }
					}
				}
			}
		}
		else if (World)
		{
			for (TActorIterator<APawn> It(World); It; ++It)
			{
				const AActor* Actor = *It;
				const bool bRoleMatches = FCString::Stricmp(RoleName, TEXT("boss")) == 0 ? IsPackBoss(Actor) : IsPackPlayer(Actor);
				if (!bRoleMatches) { continue; }
				TSharedRef<FJsonObject> Row = MakeShared<FJsonObject>();
				Row->SetStringField(TEXT("role"), RoleName);
				Row->SetStringField(TEXT("slot"), FString());
				Row->SetStringField(TEXT("target_slot"), FString());
				Row->SetStringField(TEXT("actor_class"), Actor->GetClass()->GetPathName());
				Row->SetStringField(TEXT("actor_id"), Actor->GetPathName());
				Row->SetStringField(TEXT("participant_generation"), FString());
				Row->SetNumberField(TEXT("reset_count"), 0);
				Row->SetStringField(TEXT("definition"), FString());
				ParticipantRows.Add(MakeShared<FJsonValueObject>(Row));
				TArray<UActorComponent*> ActorComponents;
				Actor->GetComponents(ActorComponents);
				for (const UActorComponent* Component : ActorComponents)
				{
					if (IsValid(Component)) { ComponentsForRole.Add(MakeShared<FJsonValueString>(Component->GetPathName())); }
				}
			}
		}
		ComponentsForRole.Sort([](const TSharedPtr<FJsonValue>& Left, const TSharedPtr<FJsonValue>& Right)
		{
			return Left->AsString() < Right->AsString();
		});
		ComponentCensus->SetArrayField(RoleName, ComponentsForRole);
	}
	Root->SetArrayField(TEXT("participants"), ParticipantRows);
	Root->SetObjectField(TEXT("components"), ComponentCensus);

	FString Json;
	const TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&Json);
	FJsonSerializer::Serialize(Root, Writer);
	return Json;
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

// The early part of the boss registration: footsteps and the music. It stays ahead of the player components and is reached only from the else-if of Attach, so a
// class that is both pack player and pack boss still gets neither (the player branch wins), exactly as before.
void URPGPlayerMovesSubsystem::AttachLegacyBossPrelude(AActor* Pawn) const
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

// The later part of the boss registration, every statement with its own IsPackBoss guard as before. It is called after the player components, so for a hybrid class
// the player statements still run first.
void URPGPlayerMovesSubsystem::AttachLegacyBossBundle(AActor* Pawn) const
{
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
	if (IsPackBoss(Pawn) && !Pawn->FindComponentByClass<URPGBossDormantWake>())
	{
		NewObject<URPGBossDormantWake>(Pawn, TEXT("RPGBossDormantWake"))->RegisterComponent(); // the authored idle loop and wake gate: behaviour resumes only after AN_Boss01_Wake ends
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
	if (IsPackBoss(Pawn) && !Pawn->FindComponentByClass<URPGBossCloseClipSwap>())
	{
		NewObject<URPGBossCloseClipSwap>(Pawn, TEXT("RPGBossCloseClipSwap"))->RegisterComponent();
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
	}
	if (IsPackBoss(Pawn) && !Pawn->FindComponentByClass<URPGBossHud>())
	{
		URPGBossHud* Hud = NewObject<URPGBossHud>(Pawn, TEXT("RPGBossHud"));
		Hud->RegisterComponent();
	}
	if (IsPackBoss(Pawn) && !Pawn->FindComponentByClass<URPGBossLegend>())
	{
		// The presentation layer (camera shake, hit stop, slow motion): after the tracker, phases, stagger and HUD it polls. Inert while rpg.Legend is 0.
		NewObject<URPGBossLegend>(Pawn, TEXT("RPGBossLegend"))->RegisterComponent();
	}
}

void URPGPlayerMovesSubsystem::Attach(AActor* Pawn)
{
	if (!IsValid(Pawn)) return;
	TArray<UActorComponent*> Before;
	Pawn->GetComponents(Before);
	if (IsPackPlayer(Pawn))
	{
		AddFootsteps(Pawn, false);
	}
	else if (IsPackBoss(Pawn))
	{
		AttachLegacyBossPrelude(Pawn);
	}

	AttachPlayerComponents(Pawn);
	AttachLegacyBossBundle(Pawn); // after the player components, as the boss statements always were

	if (IsPackBoss(Pawn))
	{
		TArray<UActorComponent*> After;
		Pawn->GetComponents(After);
		TArray<TWeakObjectPtr<UActorComponent>>& Owned = LegacyBossComponents.FindOrAdd(Pawn);
		for (UActorComponent* Component : After)
		{
			if (IsValid(Component) && !Before.Contains(Component)) { Owned.AddUnique(Component); }
		}
	}
	AttachBossDiagnostics(Pawn);
}

void URPGPlayerMovesSubsystem::AttachBossDiagnostics(AActor* Pawn) const
{
	if (!IsPackBoss(Pawn)) return;
	if (!Pawn->FindComponentByClass<URPGTraceAudit>())
	{
		NewObject<URPGTraceAudit>(Pawn, TEXT("RPGTraceAudit"))->RegisterComponent(); // observer: trace overlap versus damage accepted (empty in Shipping)
	}
	if (!Pawn->FindComponentByClass<URPGCombatDebug>())
	{
		// Shows nothing until the console variable rpg.Debug is above 0.
		NewObject<URPGCombatDebug>(Pawn, TEXT("RPGCombatDebug"))->RegisterComponent();
	}
}

void URPGPlayerMovesSubsystem::AttachPlayerComponents(AActor* Pawn) const
{
	if (!IsPackPlayer(Pawn)) return;
	if (!Pawn->FindComponentByClass<URPGCameraRig>())
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
	if (IsPackPlayer(Pawn) && !Pawn->FindComponentByClass<URPGPlayerParry>())
	{
		NewObject<URPGPlayerParry>(Pawn, TEXT("RPGPlayerParry"))->RegisterComponent(); // the parry window of the player (owner decision 2026-11-02)
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
	if (IsPackPlayer(Pawn) && !Pawn->FindComponentByClass<URPGBuildSelect>()) NewObject<URPGBuildSelect>(Pawn, TEXT("RPGBuildSelect"))->RegisterComponent(); // pre-fight B-key build selector (Gate 3, G3-5)
	if (IsPackPlayer(Pawn) && !Pawn->FindComponentByClass<URPGFlaskHud>()) NewObject<URPGFlaskHud>(Pawn, TEXT("RPGFlaskHud"))->RegisterComponent(); // own overlay for the pack HealthPotion stack (Gate 3, G3-5); the pack widget stays unmodified
	if (IsPackPlayer(Pawn) && !Pawn->FindComponentByClass<URPGIFrameMonitor>())
	{
		URPGIFrameMonitor* IFrames = NewObject<URPGIFrameMonitor>(Pawn, TEXT("RPGIFrameMonitor"));
		IFrames->RegisterComponent();
	}
}

void URPGPlayerMovesSubsystem::AttachSelectedPlayerComponents(AActor* Pawn) const
{
	if (!IsPackPlayer(Pawn)) return;
	AddFootsteps(Pawn, false);
	AttachPlayerComponents(Pawn);
}

void URPGPlayerMovesSubsystem::DisableSelectedBoss(AActor* Boss) const
{
	if (!IsValid(Boss) || !IsPackBoss(Boss)) return;
	Boss->SetActorTickEnabled(false);
	Boss->SetActorEnableCollision(false);
	Boss->SetActorHiddenInGame(true);
	TArray<UActorComponent*> Components;
	Boss->GetComponents(Components);
	for (UActorComponent* Component : Components)
	{
		if (!IsValid(Component)) continue;
		Component->Deactivate();
		Component->SetComponentTickEnabled(false);
	}
}

bool URPGPlayerMovesSubsystem::RemoveOwnedLegacyBossComponents(AActor* Boss, FString& OutError)
{
	OutError.Reset();
	if (!IsValid(Boss)) { OutError = TEXT("EncounterActivation.LegacyOwnerInvalid"); return false; }
	TArray<TWeakObjectPtr<UActorComponent>>* Owned = LegacyBossComponents.Find(Boss);
	if (!Owned) return true;
	for (const TWeakObjectPtr<UActorComponent>& WeakComponent : *Owned)
	{
		UActorComponent* Component = WeakComponent.Get();
		if (!IsValid(Component)) continue;
		if (Component->HasBegunPlay())
		{
			OutError = TEXT("EncounterActivation.LegacyAlreadyBegun");
			return false;
		}
	}
	for (const TWeakObjectPtr<UActorComponent>& WeakComponent : *Owned)
	{
		if (UActorComponent* Component = WeakComponent.Get()) { Component->DestroyComponent(); }
	}
	LegacyBossComponents.Remove(Boss);
	return true;
}

uint64 URPGPlayerMovesSubsystem::BeginEncounterTiming(const TCHAR* Operation, double& OutStartSeconds)
{
	OutStartSeconds = FPlatformTime::Seconds();
	const uint64 OperationId = NextEncounterTimingOperationId;
	if (NextEncounterTimingOperationId < MAX_uint64) { ++NextEncounterTimingOperationId; }
	const UWorld* World = GetWorld();
	UE_LOG(LogRPGEncounterTiming, Display, TEXT("[EncounterTiming] world_id=%u operation_id=%llu operation=%s event=begin timestamp_seconds=%.9f"),
		World ? static_cast<uint32>(World->GetUniqueID()) : 0u,
		static_cast<unsigned long long>(OperationId), Operation, OutStartSeconds);
	return OperationId;
}

void URPGPlayerMovesSubsystem::EndEncounterTiming(uint64 OperationId, const TCHAR* Operation, double StartSeconds, const FString& Outcome) const
{
	const double EndSeconds = FPlatformTime::Seconds();
	const UWorld* World = GetWorld();
	UE_LOG(LogRPGEncounterTiming, Display, TEXT("[EncounterTiming] world_id=%u operation_id=%llu operation=%s event=end timestamp_seconds=%.9f elapsed_ms=%.6f outcome=%s"),
		World ? static_cast<uint32>(World->GetUniqueID()) : 0u,
		static_cast<unsigned long long>(OperationId), Operation, EndSeconds, FMath::Max(0.0, EndSeconds - StartSeconds) * 1000.0, *Outcome);
}

void URPGPlayerMovesSubsystem::ReportActivationFailure(UWorld* World, const FString& Reason) const
{
	UE_LOG(LogTemp, Error, TEXT("[EncounterActivation] outcome=HardError reason=%s"), *Reason);
	if (GEngine && World)
	{
		GEngine->AddOnScreenDebugMessage(uint64(World->GetUniqueID()), 10.f, FColor::Red,
			FString::Printf(TEXT("Encounter activation refused: %s"), *Reason));
	}
}
