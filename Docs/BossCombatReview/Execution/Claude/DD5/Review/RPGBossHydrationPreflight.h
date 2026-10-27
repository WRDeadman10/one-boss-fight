// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Player/RPGEncounterBinding.h"

/**
 * Whole-batch core preflight of an encounter's startup (DD5 package 01): a PURE native compile of an explicit batch into a core-subset plan, or a named failure and no output.
 *
 * Input, all explicit: the expected world, the encounter GUID, the expected immutable content lease and the participant requests (actor, unique slot, explicit target slot, native role, immutable compiled
 * config lease, and for a boss-core member the explicit selected phase id). There is no first-actor lookup, no player0, no iterator and no silent default anywhere.
 *
 * Every member is validated before anything is produced. If any check fails for any member, NO plan is published, the caller's previous output is cleared first so that a failed compile can never leave an old,
 * apparently usable plan behind, and no actor, component or combat context is touched. Failures are collected with the slot (and field) they concern, never by dereferencing an invalid actor.
 *
 * Output on success: weak actor identities, copied slot / target slot / encounter identity, the expected world, the SAME content lease and config leases that were validated, class leases, and for each boss-core member the
 * plans of the accepted stats and phase adapters in the deterministic order of the selected subset's legacy order: Phases, Encounter, Posture. A target-only member gets no boss plan. Participants keep the order of the request list.
 *
 * WHAT THIS IS NOT. The result is a CORE SUBSET PREFLIGHT. It is not a complete playable boss bundle (stagger, wake, death, presentation, audio and the other legacy consumers are absent), not a reservation, not a hydrated
 * or ready context and not an authorization to suppress any legacy component. It has no activate, register or ready operation and the plan says so (IsCompletePlayableBundle, IsReservation and IsReady are false by construction).
 * The kernel never calls a Configure callback (not even as a dry run), never creates or registers a component, never queries a pack attribute, never ticks, never loads animation playback, never binds a context.
 *
 * Provenance limits, stated so nobody reads more into a success: the caller's expected content lease is compared by identity with the lease inside every config; it is not proof that this lease is the one the world's game
 * instance published (verifying that against the game instance is a later integration gate). A required manifest path being present is membership evidence, not proof of a derived value or a source hash. The bSyntheticFixture
 * flag of a config is a plain flag set by the dev-automation factory; the kernel can only accept it in a dev-automation build and cannot prove who set it (the existing binding has the same limit).
 *
 * Failures are named: each message starts with one of these tokens followed by [slot=...] where a slot is known.
 *   Batch:   Preflight.NotGameThread, Preflight.NoWorld, Preflight.InvalidEncounter, Preflight.InvalidContent, Preflight.EmptyBatch
 *   Member:  Preflight.InvalidSlot, Preflight.DuplicateSlot, Preflight.InvalidRole, Preflight.NullActor, Preflight.StaleActor, Preflight.ActorDestroying, Preflight.ForeignWorld, Preflight.ActorBegunPlay,
 *            Preflight.DuplicateActor, Preflight.NoConfig, Preflight.ContentLeaseMismatch, Preflight.InvalidManifestIdentity, Preflight.SyntheticUnavailable, Preflight.ProductionPrerequisite,
 *            Preflight.TargetMissing, Preflight.SelfTarget, Preflight.TargetNotInBatch, Preflight.UnexpectedPhaseSelection, Preflight.PreexistingConsumer,
 *            Preflight.StatsRejected, Preflight.PhaseRejected (both carry the accepted adapter's own named failure after the colon), Preflight.MissingRequiredField
 */

/** The native role of a participant. None is the explicit "not set" value and is always rejected. */
enum class ERPGPreflightRole : uint8
{
	None,
	BossCore,   // receives the Phases, Encounter and Posture plans
	TargetOnly, // receives no boss component plan
};

struct FRPGHydrationPreflightRequest
{
	/** Weak: a stale or destroyed actor is detected and reported, never dereferenced. */
	TWeakObjectPtr<AActor> Actor;
	FName Slot;
	/** Explicit: the slot of ANOTHER member of the same batch. */
	FName TargetSlot;
	ERPGPreflightRole Role = ERPGPreflightRole::None;
	/** The immutable compiled config; its Content lease must be the SAME lease as the batch's expected content. */
	TSharedPtr<const FRPGParticipantConfig> Config;
	/** Explicit selected phase id for a boss-core member (never inferred); must be None for a target-only member. */
	FName SelectedPhaseId;
};

struct FRPGHydrationPreflightInput
{
	TWeakObjectPtr<UWorld> ExpectedWorld;
	FGuid EncounterInstance;
	TSharedPtr<const RPGCombatRegistry::FEpoch> ExpectedContent;
	TArray<FRPGHydrationPreflightRequest> Requests;
};

struct FRPGPreflightParticipantPlan
{
	TWeakObjectPtr<AActor> Actor;
	FName Slot;
	FName TargetSlot;
	ERPGPreflightRole Role = ERPGPreflightRole::None;
	/** The very config lease that was validated. */
	TSharedPtr<const FRPGParticipantConfig> Config;
	/** Boss-core: Phases, Encounter, Posture in this order. Target-only: empty. Plans were built, never run. */
	TArray<FRPGComponentPlan> Plans;
	/** One lease per plan class. */
	TArray<TStrongObjectPtr<UClass>> ClassLeases;
};

struct FRPGHydrationPreflightPlan
{
	FGuid EncounterInstance;
	TWeakObjectPtr<UWorld> World;
	/** The very content lease that was validated against every config. */
	TSharedPtr<const RPGCombatRegistry::FEpoch> Content;
	TArray<FRPGPreflightParticipantPlan> Participants;

	/** Explicit scope marker of this output. */
	static const TCHAR* ScopeName() { return TEXT("CoreSubsetPreflight"); }
	bool IsCompletePlayableBundle() const { return false; }
	bool IsReservation() const { return false; }
	bool IsReady() const { return false; }
};

namespace RPGBossHydrationPreflight
{
	/** The four boss-core consumers a preflighted actor must not already have (and the participant component, which no member may have). */
	ONEBOSSFIGHT_API TArray<UClass*> ManagedCoreConsumerClasses();

	/**
	 * The compiled dependencies of a production config, checked on the leases the config already holds and never by loading, retargeting or falling back: a valid compiled skeleton, at least one compiled
	 * animation, EVERY animation lease valid (a null or garbage entry is refused even when the array is not empty) and EVERY animation on exactly the compiled skeleton (the identity rule of the binding:
	 * GetSkeleton() == Skeleton; an animation with no skeleton or another skeleton is refused, an explicit retargeted dependency would have to be compiled into the config). Returns false and one message that
	 * names every problem found (by position in the animation list). This is a narrow predicate that is tested on its own; it says nothing about the actor's mesh.
	 */
	ONEBOSSFIGHT_API bool CheckCompiledDependencies(const FRPGParticipantConfig& Config, FString& OutError);

	/**
	 * Compiles the batch. OutPlan is cleared FIRST. On success OutPlan holds the plan and the result is ready; on any failure OutPlan stays null and the result lists every failure found,
	 * with its slot. Game thread only.
	 */
	ONEBOSSFIGHT_API FRPGHydrationResult CompilePreflight(const FRPGHydrationPreflightInput& Input, TSharedPtr<const FRPGHydrationPreflightPlan>& OutPlan);
}
