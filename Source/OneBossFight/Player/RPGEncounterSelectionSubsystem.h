// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "Player/RPGBossWorldInputCompiler.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "RPGEncounterSelectionSubsystem.generated.h"

class ARPGEncounterBinding;
class APawn;
class URPGBossEncounterDefinition;
class UWorld;

namespace RPGEncounterPlayerIdentity
{
	/** Counts locally possessed, valid, live pack-player pawns and returns the sole pawn when exactly one exists. */
	ONEBOSSFIGHT_API int32 CountLocalPossessedPlayers(UWorld& World, APawn*& OutPlayer);
}

/** Per-game-instance encounter selection. It stores definitions, never pawn pointers. */
UCLASS()
class ONEBOSSFIGHT_API URPGEncounterSelectionSubsystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	virtual void Initialize(FSubsystemCollectionBase& Collection) override;
	virtual void Deinitialize() override;

	UFUNCTION(BlueprintCallable, Category="Encounter") void SetSelectedDefinition(URPGBossEncounterDefinition* Definition);
	UFUNCTION(BlueprintCallable, Category="Encounter") void ClearSelectedDefinition();
	UFUNCTION(BlueprintPure, Category="Encounter") bool HasSelectionRequest() const;
	UFUNCTION(BlueprintPure, Category="Encounter") FString GetSelectionDiagnostic() const { return SelectionDiagnostic; }
	/** Read-only requested path for diagnostics; does not synchronously load an unresolved asset. */
	FString GetRequestedDefinitionPathForDiagnostics() const;
	/** Read-only selected asset's stored membership digest; empty when a console path is unresolved. */
	FString GetRequestedManifestHashForDiagnostics() const;

	/** Resolve the selected soft path on demand. A nonempty but invalid path remains a selected request and must fail closed. */
	URPGBossEncounterDefinition* ResolveSelectedDefinition(FString& OutError);

	/** Exact pre-BeginPlay pack census; produces a transient binding and explicit boss/player selections. */
	bool BuildWorldBinding(UWorld& World, ARPGEncounterBinding*& OutBinding,
		TArray<RPGBossWorldInputCompiler::FSelection>& OutSelections, FString& OutError);
	/** Exact same selection record, but a fresh binding for the begun world and reset-broadcast generation. */
	bool BuildWorldBindingForRebind(UWorld& World, uint64 ParticipantGeneration, int32 ResetCount, ARPGEncounterBinding*& OutBinding,
		TArray<RPGBossWorldInputCompiler::FSelection>& OutSelections, FString& OutError);

private:
	UPROPERTY(Transient) TObjectPtr<URPGBossEncounterDefinition> SelectedDefinition;
	UPROPERTY(Transient) FString SelectionDiagnostic;
	/** Benchmark-only startup selection. Empty unless -RPGBenchmark and its explicit H019 argument are both present. */
	FString BenchmarkDefinitionPath;
	bool BuildWorldBindingInternal(UWorld& World, uint64 ParticipantGeneration, int32 ResetCount, bool bAllowBegunPlay, ARPGEncounterBinding*& OutBinding,
		TArray<RPGBossWorldInputCompiler::FSelection>& OutSelections, FString& OutError);
};
