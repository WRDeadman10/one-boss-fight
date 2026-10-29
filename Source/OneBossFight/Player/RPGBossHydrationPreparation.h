// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Player/RPGBossHydrationPreflight.h"
#include "UObject/StrongObjectPtr.h"

class UActorComponent;
class FRPGBatchPreparer;

/**
 * Unregistered batch PREPARATION (DD15 package 01): the first step that creates real components, and the only thing it does is create and configure the accepted native subset for a whole explicit batch WITHOUT
 * registering or beginning any of them. It is an explicitly called primitive: nothing in the project calls it (no spawn, startup or level hook), no UCLASS, no process-static map or subsystem.
 *
 * What PrepareBatch does. On the game thread only (refused before any UObject is touched otherwise) it runs the accepted CompilePreflight over the ENTIRE input and retains the validated plan (world, encounter,
 * slots, targets, config and content leases, class leases, the five plans per boss-core member). Any rejection returns the preflight's own named errors, no artifact and no component for any actor. Only after the
 * whole batch passed does it allocate exactly the five accepted native consumer classes (Stagger, Phases, Encounter, DormantWake, Posture, with the reviewed instance names) for every boss-core member, owned by the
 * member's actor, strongly leased from the moment of creation, then configure every one with its accepted plan callback and the member's validated config. A target-only member gets no component. Before and
 * immediately after every allocation and every configure the weak actor, the world, the role, the encounter identity and the component (valid, exact class, instance name, owner, owned by the actor, not
 * registered, not begun) are checked again. The result holds the artifact ONLY if every allocation and every configure succeeded; on any failure everything created so far, for EVERY member, is destroyed
 * before the result is returned. The old per-actor CreateConfigureRegister is never called, no target is looked up or inferred and no player0 is read.
 *
 * What the artifact is. A move-only unique object (privately constructed, not copyable or movable) that owns the unregistered components. It has NO register, commit, activate, ready, context-binding or
 * legacy-suppression operation and says nothing about the legacy components: an incomplete prepared subset never authorizes suppressing a legacy attachment, it is not a reservation, not a participant binding and
 * not a ready context. It does not prevent a second preparation by lock; a second PrepareBatch over actors that still hold the components is refused by the preflight (a preexisting consumer) and never touches the
 * first artifact's components. The default plan order is a relative order, not a BeginPlay chronology.
 *
 * Lifetime and cleanup. Abort() and the destructor run on the game thread (an off-thread call is refused without touching any UObject; destroying the artifact off the game thread is a contract violation that is
 * flagged and cleans nothing). Abort explicitly DestroyComponent()s precisely the components this artifact allocated, each at most once, and releases every lease; it is idempotent. A component or owner that is already
 * destroyed or invalid is released without being dereferenced. A component that somebody else registered or began is NOT rolled back or destroyed (nothing here can undo a registration callback): it is left in
 * place, no longer owned, and reported as a contract violation. Cleanup claims pre-registration owned-resource cleanup only. The caller must release every other reference to a destroyed component: the engine
 * replaces a same-name garbage object in place when the same name is created again before collection.
 *
 * Accepted limit: the components keep the native default bAutoRegister, so an engine path that registers all components of the owner (for example a deferred spawn that is finished after the preparation) registers them;
 * the artifact cannot prevent that, Abort reports it as a contract violation and the caller must keep the owners spawned and unchanged while an artifact lives. Nothing here guards against another object that
 * already carries one of the instance names: the allocation refuses a live one and the engine's in-place replacement of a destroyed one is the caller's contract above.
 *
 * Provenance limits stay those of the preflight: the caller's content lease is not proof of the game instance's epoch, manifest membership is not derived provenance, the const configs may have mutable aliases
 * elsewhere, and the input must not be mutated during the call. Real assets are not loaded here and no asset is touched.
 *
 * Failures are named: Preparation.NotGameThread, Preparation.PlanMismatch, Preparation.MemberInvalid, Preparation.ComponentInvalid, Preparation.AllocationFailed, Preparation.ConfigureRejected, Preparation.ContractViolation,
 * Preparation.InjectedFault (dev automation builds only), plus every Preflight.* token of the accepted preflight, unchanged.
 */

/** What one Abort did. Counts are per owned component. */
struct FRPGPreparationAbortReport
{
	/** Owned, unregistered, not begun components that this call destroyed. */
	int32 Destroyed = 0;
	/** Owned components that were already destroyed or whose owner was already gone: released without being touched. */
	int32 AlreadyGone = 0;
	/** Owned components that somebody registered or began, or re-parented: left in place, not destroyed, reported in Errors. */
	int32 ContractViolations = 0;
	/** True when the call was refused because it was not on the game thread; nothing was touched. */
	bool bRefused = false;
	TArray<FString> Errors;

	bool IsClean() const { return Errors.IsEmpty() && !bRefused; }
};

/** A read-only summary line of one participant of a prepared batch. */
struct FRPGPreparedParticipantInfo
{
	FName Slot;
	FName TargetSlot;
	ERPGPreflightRole Role = ERPGPreflightRole::None;
	/** The explicit phase id of a boss-core member (None for a target-only member). */
	FName SelectedPhaseId;
	/** Components still leased by the artifact (0 after Abort and for a target-only member). */
	int32 OwnedComponentCount = 0;
};

/** DD28: one successful registration, in actual member/plan call order. */
struct FRPGRegisteredComponentInfo
{
	int32 MemberIndex = INDEX_NONE;
	int32 PlanIndex = INDEX_NONE;
	FName Slot;
	FName ClassName;
	FName InstanceName;
};

struct FRPGRegistrationReport
{
	bool bSucceeded = false;
	int32 FailedMemberIndex = INDEX_NONE;
	int32 FailedPlanIndex = INDEX_NONE;
	FName FailedClassName;
	TArray<FString> Errors;
	TArray<FRPGRegisteredComponentInfo> Registered;
	FRPGPreparationAbortReport Cleanup;
};

namespace RPGBossActivation
{
#if WITH_DEV_AUTOMATION_TESTS
	/** Independent registration-only hook. Fails after a real successful registration; no callbacks, nesting or production controls. */
	class ONEBOSSFIGHT_API FRegistrationFaultScope
	{
	public:
		explicit FRegistrationFaultScope(int32 InFailAfterRegistration);
		~FRegistrationFaultScope();
		bool Fired() const;
		FRegistrationFaultScope(const FRegistrationFaultScope&) = delete;
		FRegistrationFaultScope& operator=(const FRegistrationFaultScope&) = delete;
	};
#endif
}

/** The owned, unregistered prepared subset. Game thread only; keep it and release it on the game thread. */
class ONEBOSSFIGHT_API FRPGPreparedBatch
{
public:
	~FRPGPreparedBatch();

	FRPGPreparedBatch(const FRPGPreparedBatch&) = delete;
	FRPGPreparedBatch& operator=(const FRPGPreparedBatch&) = delete;
	FRPGPreparedBatch(FRPGPreparedBatch&&) = delete;
	FRPGPreparedBatch& operator=(FRPGPreparedBatch&&) = delete;

	/** True from a successful PrepareBatch until Abort. Not a gameplay or context readiness. */
	bool IsPrepared() const { return bPrepared && !bAborted; }

	/** DD28 additive step: game-thread only, never-begun owners/world only. No binding, Ready or suppression.
	 *  Own registrations are undone by Abort (and thus by the existing destructor's Abort). External registrations retain the old contract-violation behaviour.
	 *  Thread/state refusals do not touch an earlier success; execution/prevalidation failure unregisters this call in reverse, then Abort. */
	bool RegisterOwnedComponents(FRPGRegistrationReport& OutReport);
	bool IsRegistered() const { return bRegisteredByBatch; }

	/** Destroys exactly the components this artifact allocated and releases every lease. Idempotent. Game thread only. */
	FRPGPreparationAbortReport Abort();

	/** The validated preflight plan this artifact was prepared from (world, encounter, slots, targets, the very config and content leases). Null never. */
	TSharedPtr<const FRPGHydrationPreflightPlan> GetPreflightPlan() const { return Plan; }
	const FGuid& GetEncounterInstance() const { return Plan->EncounterInstance; }
	int32 GetOwnedComponentCount() const;
	/** One line per participant, in the request order. */
	TArray<FRPGPreparedParticipantInfo> GetParticipants() const;

#if WITH_DEV_AUTOMATION_TESTS
	/** Dev automation only: the owned components in participant and plan order, as const pointers (null leases skipped). Production code has no access to the components. */
	TArray<const UActorComponent*> OwnedComponentsForTest() const;
#endif

private:
	friend class FRPGBatchPreparer;

	FRPGPreparedBatch(TSharedRef<const FRPGHydrationPreflightPlan> InPlan, TArray<FName>&& InSelectedPhaseIds);

	struct FOwnedComponent
	{
		FName Name;
		TStrongObjectPtr<UActorComponent> Component;
		FOwnedComponent(FName InName, UActorComponent* InComponent) : Name(InName), Component(InComponent) {}
	};

	struct FMember
	{
		FName SelectedPhaseId;
		/** In plan order; a lease exists from the moment of creation. */
		TArray<FOwnedComponent> Owned;
	};

	/** The validated plan, the same participant order as Members. */
	TSharedPtr<const FRPGHydrationPreflightPlan> Plan;
	TArray<FMember> Members;
	bool bPrepared = false;
	bool bAborted = false;
	bool bRegisteredByBatch = false;
};

/** The result of PrepareBatch: move-only. The artifact is set only when Errors is empty. */
struct FRPGPreparationResult
{
	TArray<FString> Errors;
	TUniquePtr<FRPGPreparedBatch> Batch;

	bool Succeeded() const { return Errors.IsEmpty() && Batch.IsValid(); }
};

namespace RPGBossHydrationPreparation
{
	/** Prepares the whole batch (see above). Game thread only. No caller-supplied plan or callback is accepted: the plans are the ones the accepted preflight builds from the input. */
	ONEBOSSFIGHT_API FRPGPreparationResult PrepareBatch(const FRPGHydrationPreflightInput& Input);

#if WITH_DEV_AUTOMATION_TESTS
	/**
	 * TEST ONLY, dev automation builds only. While the scope lives, PrepareBatch fails right AFTER the N-th real step (counted from 1 per PrepareBatch call: the allocations of all boss-core members in order,
	 * then the configures in the same order) as if that step had failed, so the cleanup of really allocated components can be exercised. It is an injected failure, never an organically reproduced native failure.
	 * No author, config or cvar control exists, and it takes no callback. Game thread only; scopes do not nest.
	 */
	class ONEBOSSFIGHT_API FFaultInjectionScope
	{
	public:
		explicit FFaultInjectionScope(int32 InFailAfterStep);
		~FFaultInjectionScope();
		FFaultInjectionScope(const FFaultInjectionScope&) = delete;
		FFaultInjectionScope& operator=(const FFaultInjectionScope&) = delete;

		/** True when the injected failure actually fired inside this scope. */
		bool Fired() const;
	};
#endif
}
