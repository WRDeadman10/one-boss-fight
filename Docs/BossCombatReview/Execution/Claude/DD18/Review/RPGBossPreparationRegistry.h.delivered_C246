// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Player/RPGBossHydrationPreparation.h"
#include "Player/RPGBossWorldInputCompiler.h"
#include "Templates/SharedPointer.h"

class ARPGEncounterBinding;
class FRPGBossPreparationRegistry;
class UWorld;
struct FRPGPreparationRegistryState;

/**
 * Explicit, registry-scoped RESERVATION and lifetime of prepared encounters (DD18 part B). A FRPGBossPreparationRegistry is an explicitly created, non-copyable, non-movable object owned by whoever creates it (a test, a
 * future coordinator): there is no global registry, no subsystem, no process-static map and no automatic hook, and nothing here calls it. It is bound to ONE world and to the game thread.
 *
 * TryPrepareAndReserve composes RPGBossWorldPreparation::PrepareWorldBatch (the world-bound input compiler plus the owned unregistered preparation) with a reservation: the registry takes ownership of the prepared artifact
 * and returns a move-only lease token. Conflicts are checked BEFORE any consumer is allocated: a duplicate encounter GUID, or any actor (boss-core or target-only, every role) already reserved by this registry, is
 * refused. Two different, disjoint encounters coexist; identical slot strings across different encounters are legal; one batch may hold two bosses and a target. Registry entries (GUID and actors) are published ONLY after the
 * whole batch compiled, was prepared and passed the facade's final identity checks; any failure leaves every earlier reservation and artifact intact and no provisional entry or allocation of this attempt. Admission of a
 * second call while one is in progress on the same registry is refused (no caller callback exists, so this guards only a native re-entry, for example from an asset load).
 *
 * Tokens carry the registry identity (a GUID), a unique serial that is never reused, and the encounter GUID, and they hold only a WEAK reference to the registry's private shared state: a token that outlives the registry is
 * safe and simply invalid. Tokens are validated by registry identity AND serial, never by encounter GUID alone: a stale, consumed, wrong-registry or repeated release can neither destroy a replacement reservation nor
 * anything else. Release (explicit or by destroying the token on the game thread) aborts exactly its own unregistered artifact and frees the GUID and actor entries ONLY after a clean cleanup. A cleanup that is not clean
 * (a component somebody registered, began or re-owned: DD15's contract violation) leaves a QUARANTINED reservation with diagnostics: its GUID and actors stay reserved, admission is not silently reopened and no
 * rollback, unregistration, repair or deletion is attempted or claimed. A cleanup failure DURING admission (the identity checks after the preparation failed and the abort left components in place) quarantines the encounter the
 * same way. Destroying the registry closes admission, aborts every owned artifact once (on the game thread; an abort that is not clean at that point is only logged, nothing is rolled back) and invalidates every surviving token.
 *
 * Threads: every operation is game-thread only: mutations are refused WITHOUT touching any UObject otherwise (a violation result) and the read accessors return neutral values (0, empty, not held, closed) off the game thread. Destroying a held token or the registry off the game thread is a contract violation that is flagged
 * (ensure) and performs no UObject cleanup there: a held token destroyed off-thread leaves its reservation in the registry until the registry is destroyed on the game thread; the registry destroyed off-thread only closes
 * admission and invalidates tokens, its artifacts being destroyed by their own destructors under the DD15 contract. No worker-destructor experiment exists.
 *
 * What a reservation is: an INCOMPLETE, UNREGISTERED, per-registry native subset (five components per boss-core member). It is NOT a world-wide or global uniqueness claim across separately created registries (a future
 * coordinator must own the authoritative instance), not a published combat context, not a hydrated or Ready participant, not an activation, not a complete playable bundle and gives no authority to suppress a legacy
 * attachment. Nothing is registered. Epoch or binding drift and re-entry cannot be provoked without a callback, a cvar or an injection framework: the code checks them, the tests do not execute them.
 */

/** Why a TryPrepareAndReserve call failed (None on success). */
enum class EReservationFailure : uint8
{
	None,
	/** The inputs are invalid: world (including a world that no longer exists), binding, selections, definitions, manifest hash, content, closed registry. */
	InvalidInput,
	/** The encounter GUID or an actor is already reserved by this registry. */
	Conflict,
	/** The world, the game instance, the epoch or the binding changed. */
	Drift,
	/** The preparation (allocation or configuration) failed and was cleaned up. */
	PreparationFailed,
	/** A contract was violated: wrong thread, re-entry, or a cleanup that left something in place. */
	ContractViolation,
};

/** What one release did. */
struct FRPGReleaseReport
{
	enum class EOutcome : uint8
	{
		/** Released: the artifact was aborted cleanly and the reservation was freed. */
		Released,
		/** Refused: not on the game thread, nothing was touched. */
		Refused,
		/** The token holds nothing, or its serial is no longer reserved here (consumed, stale, registry gone). Nothing was touched and the stale token was cleared. */
		Stale,
		/** The token belongs to another registry. Nothing was touched. */
		WrongRegistry,
		/** The abort was not clean: the reservation is quarantined, not freed, and the token is consumed. */
		Quarantined,
	};

	EOutcome Outcome = EOutcome::Stale;
	TArray<FString> Errors;
	/** What the abort of the owned artifact did (empty unless the artifact was aborted). */
	FRPGPreparationAbortReport Abort;

	bool IsReleased() const { return Outcome == EOutcome::Released; }
};

/** The move-only lease of one reservation. Destroying it on the game thread releases the reservation. */
class ONEBOSSFIGHT_API FRPGPreparationLeaseToken
{
public:
	FRPGPreparationLeaseToken() = default;
	~FRPGPreparationLeaseToken();

	FRPGPreparationLeaseToken(const FRPGPreparationLeaseToken&) = delete;
	FRPGPreparationLeaseToken& operator=(const FRPGPreparationLeaseToken&) = delete;
	FRPGPreparationLeaseToken(FRPGPreparationLeaseToken&& Other) noexcept;
	FRPGPreparationLeaseToken& operator=(FRPGPreparationLeaseToken&& Other) noexcept;

	/** True while the registry is alive and still reserves this token's serial as an active reservation. */
	bool IsHeld() const;

	uint64 GetSerial() const { return Serial; }
	const FGuid& GetRegistryId() const { return RegistryId; }
	const FGuid& GetEncounter() const { return Encounter; }

	/** Releases through the token's own registry (same validation and effect as FRPGBossPreparationRegistry::Release: Released, Quarantined and Stale consume the token, Refused leaves it). */
	FRPGReleaseReport Release();

#if WITH_DEV_AUTOMATION_TESTS
	/** TEST ONLY, dev automation builds only: a token carrying the given registry identity, serial and encounter, to prove that validation is by registry and SERIAL and never by GUID alone. It is not an author control. */
	static FRPGPreparationLeaseToken ForgeForTest(const FRPGBossPreparationRegistry& Registry, uint64 ForgedSerial, const FGuid& ForgedEncounter);
#endif

private:
	friend class FRPGBossPreparationRegistry;

	void Clear();

	TWeakPtr<FRPGPreparationRegistryState> State;
	FGuid RegistryId;
	FGuid Encounter;
	uint64 Serial = 0;
};

/** The result of TryPrepareAndReserve: move-only (it holds the token). The token is held ONLY on success. */
struct FRPGReservationResult
{
	TArray<FString> Errors;
	EReservationFailure Failure = EReservationFailure::None;
	FRPGPreparationLeaseToken Token;

	bool Succeeded() const { return Errors.IsEmpty() && Failure == EReservationFailure::None && Token.IsHeld(); }
};

/** The explicit per-world registry (see above). Game thread only. */
class ONEBOSSFIGHT_API FRPGBossPreparationRegistry
{
public:
	/** Bound to one world. */
	explicit FRPGBossPreparationRegistry(UWorld* InWorld);
	~FRPGBossPreparationRegistry();

	FRPGBossPreparationRegistry(const FRPGBossPreparationRegistry&) = delete;
	FRPGBossPreparationRegistry& operator=(const FRPGBossPreparationRegistry&) = delete;
	FRPGBossPreparationRegistry(FRPGBossPreparationRegistry&&) = delete;
	FRPGBossPreparationRegistry& operator=(FRPGBossPreparationRegistry&&) = delete;

	/** Conflict pre-check, whole-batch preparation, final identity checks, then publication of the reservation. Game thread only. */
	FRPGReservationResult TryPrepareAndReserve(const ARPGEncounterBinding* Binding, const TArray<RPGBossWorldInputCompiler::FSelection>& Selections, const FString& ManifestHash);

	/** Releases the reservation of the token (validated by registry identity and serial). On Released, Quarantined and Stale the token is consumed (a stale token is worthless); on Refused and WrongRegistry it is left as it was. Game thread only. */
	FRPGReleaseReport Release(FRPGPreparationLeaseToken& Token);

	const FGuid& GetRegistryId() const;
	bool IsAdmissionClosed() const;
	/** Active (releasable) reservations. */
	int32 GetActiveReservationCount() const;
	int32 GetQuarantinedCount() const;
	/** The encounter GUIDs reserved by active or quarantined reservations, in admission order. */
	TArray<FGuid> GetReservedEncounters() const;
	/** The diagnostics of every quarantined reservation. */
	TArray<FString> GetQuarantineDiagnostics() const;

private:
	friend class FRPGPreparationLeaseToken;

	TSharedRef<FRPGPreparationRegistryState> State;
};
