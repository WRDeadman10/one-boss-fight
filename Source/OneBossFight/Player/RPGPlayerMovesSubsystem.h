// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Player/RPGBossActivation.h"
#include "Subsystems/WorldSubsystem.h"
#include "TimerManager.h"
#include "RPGPlayerMovesSubsystem.generated.h"

/**
 * Adds this project's moves to the Advanced ARPG pack's pawns without editing the pack: when the pack player pawn (BP_CombatPlayerCharacter or a child) spawns, in any
 * game world, it gets a URPGDodgeTiming component (a new pawn after a respawn gets its own); the pack great-sword boss (BP_ExampleGreatSwordBoss) gets a
 * URPGBossStagger component (stance break and critical window).
 */
UCLASS()
class ONEBOSSFIGHT_API URPGPlayerMovesSubsystem : public UWorldSubsystem
{
	GENERATED_BODY()

public:
	/** Read-only reflected accessor for editor/runtime diagnostics that need this world's subsystem. */
	UFUNCTION(BlueprintCallable, Category="Encounter|Diagnostics", meta=(WorldContext="WorldContextObject"))
	static URPGPlayerMovesSubsystem* GetForWorld(const UObject* WorldContextObject);

	virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
	virtual void PostInitialize() override;
	virtual void OnWorldBeginPlay(UWorld& InWorld) override;
	virtual void Deinitialize() override;

	/** Captured runtime selection/participant/activation snapshot for opt-in parity tooling. */
	UFUNCTION(BlueprintCallable, Category="Encounter|Diagnostics")
	FString BuildEncounterParitySnapshot() const;

	static bool IsPackPlayer(const AActor* Actor);
	static bool IsPackBoss(const AActor* Actor);

private:
	void OnActorSpawned(AActor* Actor);
	void OnEncounterResetBroadcast(uint64 ParticipantGeneration, int32 ResetCount);
	void OnRebindTimeout();
	void FailSelectedRebind(const FString& Reason, bool bReleaseCurrentActivation);
	void BindResetBroadcast(AActor* Boss);
	void Attach(AActor* Pawn);
	void AttachPlayerComponents(AActor* Pawn) const;
	void AttachSelectedPlayerComponents(AActor* Pawn) const;
	void AttachBossDiagnostics(AActor* Pawn) const;
	bool RemoveOwnedLegacyBossComponents(AActor* Boss, FString& OutError);
	void DisableSelectedBoss(AActor* Boss) const;
	void ReportActivationFailure(UWorld* World, const FString& Reason) const;
	uint64 BeginEncounterTiming(const TCHAR* Operation, double& OutStartSeconds);
	void EndEncounterTiming(uint64 OperationId, const TCHAR* Operation, double StartSeconds, const FString& Outcome) const;
	void AttachLegacyBossPrelude(AActor* Pawn) const; // boss footsteps and music, called from the boss branch ahead of the player components
	void AttachLegacyBossBundle(AActor* Pawn) const; // the guarded boss component registrations, called after the player components

	TMap<TWeakObjectPtr<AActor>, TArray<TWeakObjectPtr<UActorComponent>>> LegacyBossComponents;
	FRPGWorldActivationResult ActiveDataActivation;
	TWeakObjectPtr<AActor> ActiveTransientBinding;
	TWeakObjectPtr<class URPGBossEncounterDefinition> ActiveSelectionDefinition;
	TWeakObjectPtr<class URPGBossEncounter> ResetBroadcastSource;
	FDelegateHandle ResetBroadcastHandle;
	FString ActiveManifestHash;
	FGuid ActiveEncounterInstance;
	FName ActiveBossSlot;
	FName ActivePlayerSlot;
	FName ActiveBossPhase;
	FSoftObjectPath ActiveBossDefinitionPath;
	FSoftObjectPath ActivePlayerDefinitionPath;
	uint64 LastAcceptedParticipantGeneration = 0;
	TWeakObjectPtr<AActor> PendingRespawnPlayer;
	FTimerHandle RebindTimeoutHandle;
	FString LastEncounterRoute = TEXT("legacy");
	FString LastEncounterOutcome = TEXT("NotStarted");
	FString LastEncounterReason;
	FString LastEncounterManifestHash;

	FDelegateHandle SpawnHandle;
	uint64 NextEncounterTimingOperationId = 1;
};
