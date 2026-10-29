// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossPreparationRegistry.h"

#include "Engine/World.h"
#include "GameFramework/Actor.h"
#include "Player/RPGBossWorldPreparation.h"
#include "Player/RPGEncounterBinding.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGPreparationRegistry, Log, All);

/** The private shared state of one registry. Tokens hold it only weakly: when the registry dies the state dies with it and every token becomes invalid. */
struct FRPGPreparationRegistryState
{
	enum class EEntryState : uint8
	{
		Active,
		Quarantined,
	};

	struct FEntry
	{
		uint64 Serial = 0;
		FGuid Encounter;
		/** Every actor of the batch (all roles), weakly: a destroyed actor never aliases a new one. */
		TArray<TWeakObjectPtr<AActor>> Actors;
		/** The owned artifact; reset once it was aborted. */
		TUniquePtr<FRPGPreparedBatch> Batch;
		EEntryState State = EEntryState::Active;
		TArray<FString> Diagnostics;
	};

	FGuid RegistryId = FGuid::NewGuid();
	TWeakObjectPtr<UWorld> World;
	bool bClosed = false;
	bool bAdmitting = false;
	/** Serials start at 1 and are never reused. */
	uint64 NextSerial = 1;
	TArray<FEntry> Entries;

	int32 FindSerial(uint64 Serial) const
	{
		return Entries.IndexOfByPredicate([Serial](const FEntry& Entry) { return Entry.Serial == Serial; });
	}
};

namespace
{
	/** The failure family of a set of nested diagnostics: contract violation first, then drift, then preparation, else the inputs. */
	EReservationFailure Classify(const TArray<FString>& Errors)
	{
		bool bViolation = false;
		bool bDrift = false;
		bool bPreparation = false;
		for (const FString& Error : Errors)
		{
			if (Error.StartsWith(TEXT("Reservation.ContractViolation")) || Error.StartsWith(TEXT("WorldPrep.ContractViolation")) || Error.StartsWith(TEXT("Preparation.ContractViolation")) || Error.StartsWith(TEXT("WorldPrep.NotGameThread")))
			{
				bViolation = true;
			}
			else if (Error.StartsWith(TEXT("WorldPrep.Drift")) || Error.StartsWith(TEXT("WorldInput.ContentDrift")) || Error.StartsWith(TEXT("WorldInput.BindingDrift")))
			{
				bDrift = true;
			}
			else if (Error.StartsWith(TEXT("Preparation.")) || Error.StartsWith(TEXT("WorldPrep.PreparationRejected")) || Error.StartsWith(TEXT("WorldPrep.CleanupAfterDrift")))
			{
				bPreparation = true;
			}
		}
		return bViolation ? EReservationFailure::ContractViolation : bDrift ? EReservationFailure::Drift : bPreparation ? EReservationFailure::PreparationFailed : EReservationFailure::InvalidInput;
	}

	/** Releases the active entry of a serial: aborts exactly its artifact and frees the entry only after a clean cleanup; otherwise the entry is quarantined and nothing is reopened. */
	FRPGReleaseReport ReleaseSerial(FRPGPreparationRegistryState& State, uint64 Serial)
	{
		FRPGReleaseReport Report;
		const int32 Index = State.FindSerial(Serial);
		if (Index == INDEX_NONE)
		{
			Report.Outcome = FRPGReleaseReport::EOutcome::Stale;
			Report.Errors.Add(FString::Printf(TEXT("Reservation.TokenStale: serial %llu is not reserved here"), Serial));
			return Report;
		}
		FRPGPreparationRegistryState::FEntry& Entry = State.Entries[Index];
		if (Entry.State != FRPGPreparationRegistryState::EEntryState::Active || !Entry.Batch.IsValid())
		{
			Report.Outcome = FRPGReleaseReport::EOutcome::Stale;
			Report.Errors.Add(FString::Printf(TEXT("Reservation.TokenStale: serial %llu is quarantined or already released; nothing was touched"), Serial));
			return Report;
		}
		Report.Abort = Entry.Batch->Abort();
		if (Report.Abort.IsClean() && Report.Abort.ContractViolations == 0)
		{
			State.Entries.RemoveAt(Index); // the indices are freed only now, after the clean cleanup
			Report.Outcome = FRPGReleaseReport::EOutcome::Released;
			return Report;
		}
		// Not clean: quarantine. The GUID and the actors stay reserved, no repair or deletion is attempted, no rollback is claimed.
		Entry.State = FRPGPreparationRegistryState::EEntryState::Quarantined;
		Entry.Diagnostics = Report.Abort.Errors;
		Entry.Diagnostics.Add(FString::Printf(TEXT("Reservation.Quarantined[serial=%llu][encounter=%s]: the cleanup left %d component(s) in place (violations); the reservation stays, nothing was rolled back"), Serial, *Entry.Encounter.ToString(), Report.Abort.ContractViolations));
		Entry.Batch.Reset();
		Report.Outcome = FRPGReleaseReport::EOutcome::Quarantined;
		Report.Errors = Entry.Diagnostics;
		UE_LOG(LogRPGPreparationRegistry, Error, TEXT("reservation %llu of encounter %s is quarantined: %s"), Serial, *Entry.Encounter.ToString(), *FString::Join(Report.Abort.Errors, TEXT(" | ")));
		return Report;
	}

	/** Publishes a QUARANTINED reservation (it has no artifact: a cleanup left components in place) so that its GUID and its actors stay reserved and admission is not silently reopened. Nothing is rolled back, repaired or deleted. */
	void PublishQuarantine(FRPGPreparationRegistryState& State, const FGuid& Encounter, const TArray<TWeakObjectPtr<AActor>>& Actors, const TArray<FString>& Errors)
	{
		FRPGPreparationRegistryState::FEntry Entry;
		Entry.Serial = State.NextSerial++;
		Entry.Encounter = Encounter;
		Entry.Actors = Actors;
		Entry.State = FRPGPreparationRegistryState::EEntryState::Quarantined;
		Entry.Diagnostics = Errors;
		Entry.Diagnostics.Add(FString::Printf(TEXT("Reservation.Quarantined[serial=%llu][encounter=%s]: a cleanup during admission left components in place; the encounter stays reserved, nothing was rolled back"), Entry.Serial, *Encounter.ToString()));
		UE_LOG(LogRPGPreparationRegistry, Error, TEXT("encounter %s is quarantined (serial %llu): %s"), *Encounter.ToString(), Entry.Serial, *FString::Join(Errors, TEXT(" | ")));
		State.Entries.Add(MoveTemp(Entry));
	}

	/** RAII guard of the admission flag. */
	struct FAdmissionScope
	{
		explicit FAdmissionScope(FRPGPreparationRegistryState& InState) : State(InState) { State.bAdmitting = true; }
		~FAdmissionScope() { State.bAdmitting = false; }
		FAdmissionScope(const FAdmissionScope&) = delete;
		FAdmissionScope& operator=(const FAdmissionScope&) = delete;
		FRPGPreparationRegistryState& State;
	};
}

// ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
// Lease token

FRPGPreparationLeaseToken::~FRPGPreparationLeaseToken()
{
	if (Serial == 0 || !State.IsValid())
	{
		return; // nothing held, or the registry is already gone (nothing to release, nothing to flag)
	}
	if (!IsInGameThread())
	{
		// A held token destroyed off the game thread: flagged, no UObject cleanup here. The reservation stays in the registry until the registry is destroyed on the game thread.
		ensureMsgf(false, TEXT("a held preparation lease token was destroyed off the game thread: its reservation stays until the registry is destroyed (contract violation)"));
		return;
	}
	Release();
}

FRPGPreparationLeaseToken::FRPGPreparationLeaseToken(FRPGPreparationLeaseToken&& Other) noexcept
	: State(MoveTemp(Other.State))
	, RegistryId(Other.RegistryId)
	, Encounter(Other.Encounter)
	, Serial(Other.Serial)
{
	Other.Clear();
}

FRPGPreparationLeaseToken& FRPGPreparationLeaseToken::operator=(FRPGPreparationLeaseToken&& Other) noexcept
{
	if (this != &Other)
	{
		// The token being replaced is released first (game thread) like a destroyed token.
		if (Serial != 0 && State.IsValid())
		{
			if (IsInGameThread())
			{
				Release();
			}
			else
			{
				ensureMsgf(false, TEXT("a held preparation lease token was replaced off the game thread: its reservation stays until the registry is destroyed (contract violation)"));
			}
		}
		State = MoveTemp(Other.State);
		RegistryId = Other.RegistryId;
		Encounter = Other.Encounter;
		Serial = Other.Serial;
		Other.Clear();
	}
	return *this;
}

void FRPGPreparationLeaseToken::Clear()
{
	State.Reset();
	RegistryId.Invalidate();
	Encounter.Invalidate();
	Serial = 0;
}

bool FRPGPreparationLeaseToken::IsHeld() const
{
	if (Serial == 0 || !IsInGameThread())
	{
		return false; // reads are game-thread only
	}
	const TSharedPtr<FRPGPreparationRegistryState> Pinned = State.Pin();
	if (!Pinned.IsValid() || Pinned->bClosed || Pinned->RegistryId != RegistryId)
	{
		return false;
	}
	const int32 Index = Pinned->FindSerial(Serial);
	return Index != INDEX_NONE && Pinned->Entries[Index].State == FRPGPreparationRegistryState::EEntryState::Active && Pinned->Entries[Index].Encounter == Encounter;
}

FRPGReleaseReport FRPGPreparationLeaseToken::Release()
{
	FRPGReleaseReport Report;
	if (!IsInGameThread())
	{
		Report.Outcome = FRPGReleaseReport::EOutcome::Refused;
		Report.Errors.Add(TEXT("Reservation.NotGameThread: a lease is released on the game thread only (nothing was touched)"));
		return Report;
	}
	const TSharedPtr<FRPGPreparationRegistryState> Pinned = State.Pin();
	if (Serial == 0 || !Pinned.IsValid() || Pinned->bClosed || Pinned->RegistryId != RegistryId)
	{
		Report.Outcome = FRPGReleaseReport::EOutcome::Stale;
		Report.Errors.Add(TEXT("Reservation.TokenStale: the token holds nothing or its registry is gone or closed (nothing was touched)"));
		Clear();
		return Report;
	}
	const int32 Index = Pinned->FindSerial(Serial);
	if (Index == INDEX_NONE || Pinned->Entries[Index].Encounter != Encounter)
	{
		Report.Outcome = FRPGReleaseReport::EOutcome::Stale;
		Report.Errors.Add(FString::Printf(TEXT("Reservation.TokenStale: serial %llu is not reserved for encounter %s here (nothing was touched)"), Serial, *Encounter.ToString()));
		Clear();
		return Report;
	}
	Report = ReleaseSerial(*Pinned, Serial);
	Clear();
	return Report;
}

#if WITH_DEV_AUTOMATION_TESTS
FRPGPreparationLeaseToken FRPGPreparationLeaseToken::ForgeForTest(const FRPGBossPreparationRegistry& Registry, uint64 ForgedSerial, const FGuid& ForgedEncounter)
{
	FRPGPreparationLeaseToken Token;
	Token.State = Registry.State;
	Token.RegistryId = Registry.GetRegistryId();
	Token.Encounter = ForgedEncounter;
	Token.Serial = ForgedSerial;
	return Token;
}
#endif

// ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
// Registry

FRPGBossPreparationRegistry::FRPGBossPreparationRegistry(UWorld* InWorld)
	: State(MakeShared<FRPGPreparationRegistryState>())
{
	if (!IsInGameThread())
	{
		ensureMsgf(false, TEXT("a preparation registry was created off the game thread (contract violation): admission is closed"));
		State->bClosed = true;
		return;
	}
	State->World = InWorld;
}

FRPGBossPreparationRegistry::~FRPGBossPreparationRegistry()
{
	State->bClosed = true; // admission is closed first; tokens become invalid from here
	if (!IsInGameThread())
	{
		ensureMsgf(false, TEXT("a preparation registry was destroyed off the game thread (contract violation): no UObject cleanup was done here"));
		return;
	}
	for (int32 Index = State->Entries.Num() - 1; Index >= 0; --Index)
	{
		FRPGPreparationRegistryState::FEntry& Entry = State->Entries[Index];
		if (Entry.State == FRPGPreparationRegistryState::EEntryState::Active && Entry.Batch.IsValid())
		{
			const FRPGPreparationAbortReport Report = Entry.Batch->Abort(); // each artifact once
			if (!Report.IsClean() || Report.ContractViolations != 0)
			{
				UE_LOG(LogRPGPreparationRegistry, Error, TEXT("registry %s destroyed: the cleanup of reservation %llu (encounter %s) was not clean: %s"), *State->RegistryId.ToString(), Entry.Serial, *Entry.Encounter.ToString(), *FString::Join(Report.Errors, TEXT(" | ")));
			}
		}
	}
	State->Entries.Reset();
}

const FGuid& FRPGBossPreparationRegistry::GetRegistryId() const
{
	return State->RegistryId;
}

bool FRPGBossPreparationRegistry::IsAdmissionClosed() const
{
	return !IsInGameThread() || State->bClosed;
}

int32 FRPGBossPreparationRegistry::GetActiveReservationCount() const
{
	if (!IsInGameThread())
	{
		return 0;
	}
	int32 Count = 0;
	for (const FRPGPreparationRegistryState::FEntry& Entry : State->Entries)
	{
		Count += Entry.State == FRPGPreparationRegistryState::EEntryState::Active ? 1 : 0;
	}
	return Count;
}

int32 FRPGBossPreparationRegistry::GetQuarantinedCount() const
{
	return IsInGameThread() ? State->Entries.Num() - GetActiveReservationCount() : 0;
}

TArray<FGuid> FRPGBossPreparationRegistry::GetReservedEncounters() const
{
	TArray<FGuid> Encounters;
	if (!IsInGameThread())
	{
		return Encounters;
	}
	for (const FRPGPreparationRegistryState::FEntry& Entry : State->Entries)
	{
		Encounters.Add(Entry.Encounter);
	}
	return Encounters;
}

TArray<FString> FRPGBossPreparationRegistry::GetQuarantineDiagnostics() const
{
	TArray<FString> Diagnostics;
	if (!IsInGameThread())
	{
		return Diagnostics;
	}
	for (const FRPGPreparationRegistryState::FEntry& Entry : State->Entries)
	{
		if (Entry.State == FRPGPreparationRegistryState::EEntryState::Quarantined)
		{
			Diagnostics.Append(Entry.Diagnostics);
		}
	}
	return Diagnostics;
}

FRPGReleaseReport FRPGBossPreparationRegistry::Release(FRPGPreparationLeaseToken& Token)
{
	FRPGReleaseReport Report;
	if (!IsInGameThread())
	{
		Report.Outcome = FRPGReleaseReport::EOutcome::Refused;
		Report.Errors.Add(TEXT("Reservation.NotGameThread: a lease is released on the game thread only (nothing was touched, the token is unchanged)"));
		return Report;
	}
	if (Token.Serial == 0)
	{
		Report.Outcome = FRPGReleaseReport::EOutcome::Stale;
		Report.Errors.Add(TEXT("Reservation.TokenStale: the token holds nothing (nothing was touched)"));
		return Report;
	}
	if (Token.RegistryId != State->RegistryId)
	{
		Report.Outcome = FRPGReleaseReport::EOutcome::WrongRegistry;
		Report.Errors.Add(FString::Printf(TEXT("Reservation.TokenWrongRegistry: the token belongs to registry %s, not to %s (nothing was touched, the token is unchanged)"), *Token.RegistryId.ToString(), *State->RegistryId.ToString()));
		return Report;
	}
	const int32 Index = State->FindSerial(Token.Serial);
	if (State->bClosed || Index == INDEX_NONE || State->Entries[Index].Encounter != Token.Encounter)
	{
		Report.Outcome = FRPGReleaseReport::EOutcome::Stale;
		Report.Errors.Add(FString::Printf(TEXT("Reservation.TokenStale: serial %llu is not reserved for encounter %s in this registry (nothing was touched, the stale token was cleared)"), Token.Serial, *Token.Encounter.ToString()));
		Token.Clear();
		return Report;
	}
	Report = ReleaseSerial(*State, Token.Serial);
	Token.Clear(); // consumed on Released and Quarantined
	return Report;
}

FRPGReservationResult FRPGBossPreparationRegistry::TryPrepareAndReserve(const ARPGEncounterBinding* Binding, const TArray<RPGBossWorldInputCompiler::FSelection>& Selections, const FString& ManifestHash)
{
	FRPGReservationResult Result;
	// Before any UObject is touched.
	if (!IsInGameThread())
	{
		Result.Failure = EReservationFailure::ContractViolation;
		Result.Errors.Add(TEXT("Reservation.NotGameThread: a reservation is admitted on the game thread only (nothing was touched)"));
		return Result;
	}
	if (State->bClosed)
	{
		Result.Failure = EReservationFailure::InvalidInput;
		Result.Errors.Add(TEXT("Reservation.Closed: the registry is closed to admission"));
		return Result;
	}
	if (State->bAdmitting)
	{
		Result.Failure = EReservationFailure::ContractViolation;
		Result.Errors.Add(TEXT("Reservation.ContractViolation: re-entrant admission on the same registry is refused"));
		return Result;
	}
	FAdmissionScope Admission(*State);

	UWorld* World = State->World.Get();
	if (!World || !IsValid(World))
	{
		Result.Failure = EReservationFailure::InvalidInput;
		Result.Errors.Add(TEXT("Reservation.WorldGone: the registry's world no longer exists"));
		return Result;
	}
	if (!Binding || !IsValid(Binding) || Binding->GetWorld() != World)
	{
		Result.Failure = EReservationFailure::InvalidInput;
		Result.Errors.Add(TEXT("Reservation.InvalidBinding: no binding was given, it was destroyed or collected, or it is not in this registry's world"));
		return Result;
	}

	// The conflict pre-check, BEFORE anything is allocated: the encounter GUID and every actor of every role. Quarantined reservations still reserve. A null or stale actor is not a conflict here (the stages report it).
	TArray<FString> Conflicts;
	for (const FRPGPreparationRegistryState::FEntry& Entry : State->Entries)
	{
		if (Binding->EncounterInstance.IsValid() && Entry.Encounter == Binding->EncounterInstance)
		{
			Conflicts.Add(FString::Printf(TEXT("Reservation.DuplicateEncounter[encounter=%s]: already reserved by serial %llu"), *Entry.Encounter.ToString(), Entry.Serial));
		}
		for (const FRPGPlacedParticipantBinding& Participant : Binding->Participants)
		{
			AActor* Actor = Participant.Actor.Get();
			if (Actor && IsValid(Actor) && Entry.Actors.Contains(TWeakObjectPtr<AActor>(Actor)))
			{
				Conflicts.Add(FString::Printf(TEXT("Reservation.ActorConflict[slot=%s][actor=%s]: already reserved by serial %llu of encounter %s"), *Participant.Slot.ToString(), *Actor->GetName(), Entry.Serial, *Entry.Encounter.ToString()));
			}
		}
	}
	if (!Conflicts.IsEmpty())
	{
		Result.Failure = EReservationFailure::Conflict;
		Result.Errors = Conflicts;
		return Result;
	}

	TArray<TWeakObjectPtr<AActor>> BindingActors;
	for (const FRPGPlacedParticipantBinding& Participant : Binding->Participants)
	{
		if (AActor* Actor = Participant.Actor.Get())
		{
			BindingActors.Add(Actor);
		}
	}

	// The whole batch: input compile and owned preparation, with the facade's identity checks. A failure leaves every earlier reservation and artifact exactly as it was and no entry of this attempt.
	FRPGWorldPreparationResult Prepared = RPGBossWorldPreparation::PrepareWorldBatch(World, Binding, Selections, ManifestHash);
	if (!Prepared.Succeeded())
	{
		Result.Errors = Prepared.Errors;
		if (Result.Errors.IsEmpty())
		{
			Result.Errors.Add(TEXT("WorldPrep.PreparationRejected: the facade returned no artifact and no error"));
		}
		Result.Failure = Classify(Result.Errors);
		if (Result.Errors.ContainsByPredicate([](const FString& Error) { return Error.StartsWith(TEXT("WorldPrep.ContractViolation")) || Error.StartsWith(TEXT("Preparation.ContractViolation")); }))
		{
			// A cleanup left components in place: the encounter is quarantined (reserved, never silently reopened).
			PublishQuarantine(*State, Binding->EncounterInstance, BindingActors, Result.Errors);
		}
		return Result;
	}

	// The final gate before publication: the registry is still open and in the same world, and the artifact still matches the encounter and has no conflict (the admission guard makes a change impossible here; the check is a defence).
	const TSharedPtr<const FRPGHydrationPreflightPlan> Plan = Prepared.Batch->GetPreflightPlan();
	bool bFinalOk = !State->bClosed && State->World.Get() == World && Plan.IsValid() && Plan->EncounterInstance == Binding->EncounterInstance;
	TArray<TWeakObjectPtr<AActor>> Actors;
	if (bFinalOk)
	{
		for (const FRPGPreflightParticipantPlan& Participant : Plan->Participants)
		{
			AActor* Actor = Participant.Actor.Get();
			bFinalOk = bFinalOk && Actor && IsValid(Actor) && Actor->GetWorld() == World;
			Actors.Add(Participant.Actor);
		}
	}
	for (const FRPGPreparationRegistryState::FEntry& Entry : State->Entries)
	{
		bFinalOk = bFinalOk && Entry.Encounter != Binding->EncounterInstance;
		for (const TWeakObjectPtr<AActor>& Actor : Actors)
		{
			bFinalOk = bFinalOk && !Entry.Actors.Contains(Actor);
		}
	}
	if (!bFinalOk)
	{
		Result.Failure = EReservationFailure::Drift;
		Result.Errors.Add(TEXT("Reservation.Drift: the registry, the world or the artifact changed before publication (this call's components were aborted)"));
		const FRPGPreparationAbortReport Cleanup = Prepared.Batch->Abort();
		for (const FString& CleanupError : Cleanup.Errors)
		{
			Result.Errors.Add(FString::Printf(TEXT("Reservation.CleanupAfterDrift: %s"), *CleanupError));
		}
		if (Cleanup.ContractViolations > 0 || Cleanup.bRefused)
		{
			Result.Failure = EReservationFailure::ContractViolation;
			Result.Errors.Add(TEXT("Reservation.ContractViolation: the cleanup after drift left components in place or was refused"));
			PublishQuarantine(*State, Binding->EncounterInstance, Actors, Result.Errors);
		}
		return Result;
	}

	// Publication: entries become visible only now.
	FRPGPreparationRegistryState::FEntry Entry;
	Entry.Serial = State->NextSerial++;
	Entry.Encounter = Plan->EncounterInstance;
	Entry.Actors = MoveTemp(Actors);
	Entry.Batch = MoveTemp(Prepared.Batch);
	Entry.State = FRPGPreparationRegistryState::EEntryState::Active;
	Result.Token.State = State;
	Result.Token.RegistryId = State->RegistryId;
	Result.Token.Encounter = Entry.Encounter;
	Result.Token.Serial = Entry.Serial;
	State->Entries.Add(MoveTemp(Entry));
	return Result;
}
