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
UCLASS(Config=Game, DefaultConfig)
class ONEBOSSFIGHT_API URPGPlayerMovesSubsystem : public UWorldSubsystem
{
	GENERATED_BODY()

public:
	/** A7-B preparation switch. True preserves the current legacy no-selection startup; explicit data selections remain independent. */
	UPROPERTY(Config, EditDefaultsOnly, Category="Encounter|Startup")
	bool bUseLegacyStartup = true;

	/** Owner decision 2026-11-06 ("retire legacy"): with no explicit selection (no setter call, no benchmark or console path) the world starts the data-driven route
	 *  with DefaultEncounterDefinition. Native default false so a bare subsystem (tests) is unchanged; Config/DefaultGame.ini sets it True for the game.
	 *  Non-Shipping opt-out for parity runs: command-line -RPGLegacyStartup or environment variable RPG_LEGACY_STARTUP=1 keeps the legacy route. */
	UPROPERTY(Config, EditDefaultsOnly, Category="Encounter|Startup")
	bool bDefaultToDataStartup = false;

	/** The default data startup applies only to this map (short name, PIE prefix ignored): the framework proof levels and test worlds keep the route they always had. */
	UPROPERTY(Config, EditDefaultsOnly, Category="Encounter|Startup")
	FString DefaultEncounterMap = TEXT("L_SevarogArena");

	/** Encounter definition used by the default data startup. Empty disables the default (legacy startup resumes). It must stay under a directory the cook always includes. */
	UPROPERTY(Config, EditDefaultsOnly, Category="Encounter|Startup")
	FString DefaultEncounterDefinition = TEXT("/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter");

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

	/** Stores DefaultEncounterDefinition as the game instance's selection when none exists (see bDefaultToDataStartup). A load failure leaves the legacy route in place.
	 *  Runs in PostInitialize and OnWorldBeginPlay; public so tests can drive it. */
	void ApplyDefaultDataSelection();

	static bool IsPackPlayer(const AActor* Actor);
	static bool IsPackBoss(const AActor* Actor);

private:
	void OnActorSpawned(AActor* Actor);
	void ReplacePackPlayerWithGreystoneForTest(TWeakObjectPtr<APawn> SpawnedPackPawn);
	void OnEncounterResetBroadcast(uint64 ParticipantGeneration, int32 ResetCount);
	void OnRebindPoll();
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
	uint64 PendingRebindGeneration = 0;
	int32 PendingRebindResetCount = 0;
	FTimerHandle RebindTimeoutHandle;
	FTimerHandle RebindPollHandle;
	FString LastEncounterRoute = TEXT("legacy");
	FString LastEncounterOutcome = TEXT("NotStarted");
	FString LastEncounterReason;
	FString LastEncounterManifestHash;

	FDelegateHandle SpawnHandle;
	uint64 NextEncounterTimingOperationId = 1;
};
