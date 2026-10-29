// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Player/RPGBossHydrationPreparation.h"
#include "Player/RPGBossWorldInputCompiler.h"

class ARPGEncounterBinding;
class UWorld;

/**
 * World-bound unregistered PREPARATION facade (DD18 part A): the explicitly called function that composes the two accepted stages for a placed encounter: RPGBossWorldInputCompiler::CompileWorldInput (the content epoch
 * comes ONLY from the world's own game instance through RPGCombatRegistry::ForWorld, one production config per explicit definition, whole-batch preflight) and RPGBossHydrationPreparation::PrepareBatch (five owned
 * unregistered native components per boss-core member). The function accepts NO caller epoch, config, plan or callback, has no manufactured fallback and repeats NO validator: every input and layer diagnostic is the nested
 * diagnostic of the stage that produced it (WorldInput.* for the input compiler and its nested production and preflight layers, Preflight.* and Preparation.* for the preparation, WorldPrep.* only for what this facade
 * itself checks). Nothing in the project calls it: no spawn, startup or level hook, no UCLASS, no subsystem, no process-static world map.
 *
 * Game thread only (refused before any UObject is touched otherwise). The result is returned by value and is move-only: the prepared artifact exists ONLY on full success, so no stale out parameter can hold a half
 * result. The identities are checked around BOTH stages by one facade-local checkpoint (the input compiler's own checkpoints are private to it and are not duplicated here): the world valid and the same, the world's game
 * instance valid and the same, the published epoch pointer the very lease the input holds, the binding resolved through a retained weak reference (valid, not being destroyed, in the world, not begun or beginning, same
 * GUID), the binding's participants unchanged and matching the compiled input request by request, and every member actor and definition still valid, in the world and not begun. A failed check (WorldPrep.Drift) after
 * the preparation aborts precisely the components THIS call allocated, appends the cleanup errors and returns no artifact (a cleanup that leaves components in place is reported as WorldPrep.ContractViolation: this facade reserves nothing, so a caller that
 * needs such an encounter to stay blocked uses the registry, which quarantines it); a failed check before the preparation allocates nothing. An earlier independent artifact is
 * never touched.
 *
 * Inherited limits, not removed: the components keep the native default bAutoRegister (an engine path that registers all owner components would register them), a destroyed uncollected component name is replaced in place
 * when the same name is created again (no reference to a destroyed component may be kept), the manifest hash and the manifest rows inside the definitions are caller-supplied membership data (the epoch comes from the
 * game instance, the manifest does not), and the artifact must be released on the game thread. It reserves nothing by itself (see the preparation registry) and is not a registration, a participant, a context binding,
 * a Ready state, an activation, a legacy disposition or a target or reset operation: it has none of those operations. Epoch, GI or binding changes DURING a stage cannot be provoked without a callback, a cvar or an
 * injection framework and are covered only by the checkpoints of the stages and of this facade: source claims, not executed failures.
 */
struct FRPGWorldPreparationResult
{
	/** Empty exactly on success. Nested diagnostics are carried unchanged. */
	TArray<FString> Errors;
	/** Set ONLY when Errors is empty: the uniquely owned prepared artifact (unregistered, never begun). */
	TUniquePtr<FRPGPreparedBatch> Batch;

	bool Succeeded() const { return Errors.IsEmpty() && Batch.IsValid(); }
};

namespace RPGBossWorldPreparation
{
	/** Compiles the world input and prepares the whole batch (see above). Game thread only. */
	ONEBOSSFIGHT_API FRPGWorldPreparationResult PrepareWorldBatch(UWorld* ExpectedWorld, const ARPGEncounterBinding* Binding, const TArray<RPGBossWorldInputCompiler::FSelection>& Selections, const FString& ManifestHash);
}
