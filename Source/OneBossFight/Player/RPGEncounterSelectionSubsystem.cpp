// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGEncounterSelectionSubsystem.h"

#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/Pawn.h"
#include "HAL/IConsoleManager.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Player/RPGEncounterBinding.h"
#include "Player/RPGBossDamage.h"
#include "Player/RPGBossEncounterDefinition.h"
#include "Player/RPGPlayerMovesSubsystem.h"

namespace
{
#if !UE_BUILD_SHIPPING
	FString GEncounterDefinitionPath;
	FAutoConsoleVariableRef CVarEncounterDefinition(
		TEXT("rpg.EncounterDefinition"),
		GEncounterDefinitionPath,
		TEXT("Encounter-definition asset path for the opt-in data startup route; empty preserves legacy startup."),
		ECVF_Cheat);
#endif
}

int32 RPGEncounterPlayerIdentity::CountLocalPossessedPlayers(UWorld& World, APawn*& OutPlayer)
{
	OutPlayer = nullptr;
	int32 Count = 0;
	for (FConstPlayerControllerIterator It = World.GetPlayerControllerIterator(); It; ++It)
	{
		APlayerController* Controller = It->Get();
		if (!IsValid(Controller)) continue;
		const bool bLocalController = Controller->IsLocalController() || World.GetNetMode() == NM_Standalone;
		if (!bLocalController) continue;
		APawn* Pawn = Controller->GetPawn();
		if (!IsValid(Pawn) || Pawn->IsActorBeingDestroyed() || Pawn->IsPendingKillPending()
			|| !URPGPlayerMovesSubsystem::IsPackPlayer(Pawn) || RPGBossDamage::HasTag(Pawn, TEXT("Status.Dead"))) continue;
		OutPlayer = Pawn;
		++Count;
	}
	if (Count != 1) OutPlayer = nullptr;
	return Count;
}

void URPGEncounterSelectionSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);
	SelectedDefinition = nullptr;
	SelectionDiagnostic.Reset();
	BenchmarkDefinitionPath.Reset();
	// This opt-in path exists only for paired packaged benchmark captures. An unset
	// argument leaves the historical startup path and command line unchanged.
	// Lead fix (C-871): compiled out of Shipping. GATE4 benchmarks a Development package, and a
	// command-line selector in Shipping is the open owner decision J049/KI-183, not a benchmark detail.
#if !UE_BUILD_SHIPPING
	if (FParse::Param(FCommandLine::Get(), TEXT("RPGBenchmark")))
	{
		FString RequestedPath;
		if (FParse::Value(FCommandLine::Get(), TEXT("H019EncounterDefinition="), RequestedPath, false))
		{
			RequestedPath.TrimStartAndEndInline();
			BenchmarkDefinitionPath = RequestedPath;
		}
	}
#endif
}

void URPGEncounterSelectionSubsystem::Deinitialize()
{
	SelectedDefinition = nullptr;
	SelectionDiagnostic.Reset();
	BenchmarkDefinitionPath.Reset();
	Super::Deinitialize();
}

void URPGEncounterSelectionSubsystem::SetSelectedDefinition(URPGBossEncounterDefinition* Definition)
{
	SelectedDefinition = Definition;
	SelectionDiagnostic.Reset();
}

void URPGEncounterSelectionSubsystem::ClearSelectedDefinition()
{
	SelectedDefinition = nullptr;
	SelectionDiagnostic.Reset();
	BenchmarkDefinitionPath.Reset();
#if !UE_BUILD_SHIPPING
	GEncounterDefinitionPath.Reset();
#endif
}

bool URPGEncounterSelectionSubsystem::HasSelectionRequest() const
{
	if (IsValid(SelectedDefinition)) return true;
	if (!BenchmarkDefinitionPath.IsEmpty()) return true;
#if !UE_BUILD_SHIPPING
	return !GEncounterDefinitionPath.IsEmpty();
#else
	return false;
#endif
}

FString URPGEncounterSelectionSubsystem::GetRequestedDefinitionPathForDiagnostics() const
{
	if (IsValid(SelectedDefinition)) { return SelectedDefinition->GetPathName(); }
	if (!BenchmarkDefinitionPath.IsEmpty()) { return BenchmarkDefinitionPath; }
#if !UE_BUILD_SHIPPING
	return GEncounterDefinitionPath;
#else
	return FString();
#endif
}

FString URPGEncounterSelectionSubsystem::GetRequestedManifestHashForDiagnostics() const
{
	return IsValid(SelectedDefinition) ? SelectedDefinition->StableManifestHash : FString();
}

URPGBossEncounterDefinition* URPGEncounterSelectionSubsystem::ResolveSelectedDefinition(FString& OutError)
{
	OutError.Reset();
	if (IsValid(SelectedDefinition)) return SelectedDefinition;
	FString RequestedPath = BenchmarkDefinitionPath;
#if !UE_BUILD_SHIPPING
	if (RequestedPath.IsEmpty()) RequestedPath = GEncounterDefinitionPath;
#endif
	if (!RequestedPath.IsEmpty())
	{
		const FSoftObjectPath Path(RequestedPath);
		UObject* Loaded = Path.TryLoad();
		SelectedDefinition = Cast<URPGBossEncounterDefinition>(Loaded);
		if (!SelectedDefinition)
		{
			OutError = TEXT("EncounterSelection.AssetLoad");
			SelectionDiagnostic = OutError;
			return nullptr;
		}
		return SelectedDefinition;
	}
	// Lead fix (C-871): removed a stray #endif left by the X-1240 edit (C1020).
	OutError = HasSelectionRequest() ? TEXT("EncounterSelection.AssetLoad") : TEXT("EncounterSelection.Absent");
	SelectionDiagnostic = OutError;
	return nullptr;
}

bool URPGEncounterSelectionSubsystem::BuildWorldBinding(UWorld& World, ARPGEncounterBinding*& OutBinding,
	TArray<RPGBossWorldInputCompiler::FSelection>& OutSelections, FString& OutError)
{
	return BuildWorldBindingInternal(World, 1, 0, false, OutBinding, OutSelections, OutError);
}

bool URPGEncounterSelectionSubsystem::BuildWorldBindingForRebind(UWorld& World, uint64 ParticipantGeneration, int32 ResetCount, ARPGEncounterBinding*& OutBinding,
	TArray<RPGBossWorldInputCompiler::FSelection>& OutSelections, FString& OutError)
{
	return BuildWorldBindingInternal(World, ParticipantGeneration, ResetCount, true, OutBinding, OutSelections, OutError);
}

bool URPGEncounterSelectionSubsystem::BuildWorldBindingInternal(UWorld& World, uint64 ParticipantGeneration, int32 ResetCount, bool bAllowBegunPlay,
	ARPGEncounterBinding*& OutBinding, TArray<RPGBossWorldInputCompiler::FSelection>& OutSelections, FString& OutError)
{
	OutBinding = nullptr;
	OutSelections.Reset();
	OutError.Reset();
	if (!IsInGameThread()) { OutError = TEXT("EncounterSelection.NotGameThread"); return false; }
	if (!World.IsGameWorld() || (World.HasBegunPlay() && !bAllowBegunPlay) || World.GetGameInstance() != GetGameInstance())
	{
		OutError = TEXT("EncounterSelection.WorldState");
		return false;
	}

	FString DefinitionError;
	URPGBossEncounterDefinition* Definition = ResolveSelectedDefinition(DefinitionError);
	if (!Definition) { OutError = DefinitionError; return false; }
	if (ParticipantGeneration == 0 || ParticipantGeneration == MAX_uint64 || ResetCount < 0)
	{
		OutError = ParticipantGeneration == MAX_uint64 ? TEXT("EncounterActivation.GenerationExhausted")
			: (ResetCount < 0 ? TEXT("EncounterActivation.ResetCountInvalid") : TEXT("EncounterActivation.GenerationMismatch"));
		return false;
	}
	if (!Definition->ValidateSelectionRecord(OutError)) { SelectionDiagnostic = OutError; return false; }

	APawn* Boss = nullptr;
	int32 BossCount = 0;
	for (TActorIterator<APawn> It(&World); It; ++It)
	{
		APawn* Pawn = *It;
		if (URPGPlayerMovesSubsystem::IsPackBoss(Pawn)) { ++BossCount; Boss = Pawn; }
	}
	APawn* Player = nullptr;
	const int32 PlayerCount = RPGEncounterPlayerIdentity::CountLocalPossessedPlayers(World, Player);
	if (BossCount != 1 || PlayerCount != 1 || !IsValid(Boss) || !IsValid(Player) || Boss == Player)
	{
		OutError = TEXT("EncounterSelection.Census");
		SelectionDiagnostic = OutError;
		return false;
	}
	if (Boss->GetWorld() != &World || Player->GetWorld() != &World
		|| ((!bAllowBegunPlay) && (Boss->HasActorBegunPlay() || Player->HasActorBegunPlay()))
		|| Boss->IsActorBeginningPlay() || Player->IsActorBeginningPlay())
	{
		OutError = TEXT("EncounterSelection.ActorState");
		SelectionDiagnostic = OutError;
		return false;
	}

	URPGBossDefinition* BossData = Definition->BossDefinition.LoadSynchronous();
	URPGBossDefinition* PlayerData = Definition->PlayerDefinition.LoadSynchronous();
	if (!IsValid(BossData) || !IsValid(PlayerData) || BossData == PlayerData)
	{
		OutError = TEXT("EncounterSelection.DefinitionLoad");
		SelectionDiagnostic = OutError;
		return false;
	}
	const bool bPhaseExists = BossData->Phases.ContainsByPredicate([&Definition](const FRPGPhaseConfig& Phase)
	{
		return Phase.PhaseId == Definition->InitialBossPhase;
	});
	if (!bPhaseExists)
	{
		OutError = TEXT("EncounterSelection.Phase");
		SelectionDiagnostic = OutError;
		return false;
	}

	FActorSpawnParameters SpawnParameters;
	SpawnParameters.ObjectFlags |= RF_Transient;
	SpawnParameters.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	ARPGEncounterBinding* Binding = World.SpawnActor<ARPGEncounterBinding>(ARPGEncounterBinding::StaticClass(),
		FTransform::Identity, SpawnParameters);
	if (!IsValid(Binding))
	{
		OutError = TEXT("EncounterSelection.BindingSpawn");
		SelectionDiagnostic = OutError;
		return false;
	}
	Binding->EncounterInstance = Definition->EncounterInstance;
	Binding->SelectionDefinitionPath = Definition->GetPathName();
	Binding->StableManifestHash = Definition->StableManifestHash;
	Binding->InitialBossPhase = Definition->InitialBossPhase;
	Binding->BossSlot = Definition->BossSlot;
	Binding->PlayerSlot = Definition->PlayerSlot;
	Binding->ParticipantGeneration = ParticipantGeneration;
	Binding->ResetCount = ResetCount;

	FRPGPlacedParticipantBinding BossParticipant;
	BossParticipant.Slot = Definition->BossSlot;
	BossParticipant.TargetSlot = Definition->PlayerSlot;
	BossParticipant.Actor = Boss;
	BossParticipant.Definition = BossData;
	Binding->Participants.Add(BossParticipant);

	FRPGPlacedParticipantBinding PlayerParticipant;
	PlayerParticipant.Slot = Definition->PlayerSlot;
	PlayerParticipant.TargetSlot = Definition->BossSlot;
	PlayerParticipant.Actor = Player;
	PlayerParticipant.Definition = PlayerData;
	Binding->Participants.Add(PlayerParticipant);

	RPGBossWorldInputCompiler::FSelection BossSelection;
	BossSelection.Slot = Definition->BossSlot;
	BossSelection.Role = ERPGPreflightRole::BossCore;
	BossSelection.SelectedPhaseId = Definition->InitialBossPhase;
	OutSelections.Add(BossSelection);

	RPGBossWorldInputCompiler::FSelection PlayerSelection;
	PlayerSelection.Slot = Definition->PlayerSlot;
	PlayerSelection.Role = ERPGPreflightRole::TargetOnly;
	PlayerSelection.SelectedPhaseId = NAME_None;
	OutSelections.Add(PlayerSelection);

	OutBinding = Binding;
	SelectionDiagnostic.Reset();
	return true;
}
