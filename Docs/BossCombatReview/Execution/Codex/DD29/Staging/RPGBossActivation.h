// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "Player/RPGBossWorldPreparation.h"

/** Activated means REGISTERED NATIVE SUBSET ONLY; never a playable/Ready/bound participant. */
enum class ERPGWorldActivationOutcome : uint8
{
	Activated,
	FallBackToLegacy,
	HardError
};

/** Caller-owned move-only artifact lease; not a registry reservation or a global uniqueness claim.
 *  The held batch retains its plan/config/content/class leases. Destroy on the game thread; the accepted
 *  batch destructor performs Abort, unregistering/destroying this batch's own never-begun components.
 *  Keep world/actors/binding/definitions/epoch stable, as required by the accepted preparation contract.
 *  Outcome describes the original call; IsHeld() becomes false after Release or moving the result.
 */
struct FRPGWorldActivationResult
{
	ERPGWorldActivationOutcome Outcome = ERPGWorldActivationOutcome::HardError;
	FName Reason = FName(TEXT("ActivationWorld.NotExecuted"));
	TArray<FString> Errors;
	FRPGRegistrationReport Registration;
	TUniquePtr<FRPGPreparedBatch> Batch;

	bool IsHeld() const { return IsInGameThread() && Batch.IsValid() && Batch->IsRegistered(); }
	bool Succeeded() const { return Outcome == ERPGWorldActivationOutcome::Activated && IsHeld(); }
	/** Refused off-thread without releasing the artifact; otherwise reports cleanup and is idempotent. */
	ONEBOSSFIGHT_API FRPGPreparationAbortReport Release();
};

namespace RPGBossActivation
{
	/** Explicit library composition: accepted PrepareWorldBatch then owned registration. No startup caller,
	 *  caller-supplied epoch/config/callback, BeginPlay, ticking, context binding, Ready or legacy suppression.
	 *  Ordinary stage rejection with clean cleanup returns FallBackToLegacy; original actor state and earlier
	 *  independent artifacts are preserved. Off-thread use or inherited lifecycle/cleanup contract violations
	 *  are HardError, with diagnostics; never pretend an unclean cleanup permits safe legacy fallback.
	 */
	ONEBOSSFIGHT_API FRPGWorldActivationResult ActivateWorld(UWorld* ExpectedWorld, const ARPGEncounterBinding* Binding,
		const TArray<RPGBossWorldInputCompiler::FSelection>& Selections, const FString& ManifestHash);
}
