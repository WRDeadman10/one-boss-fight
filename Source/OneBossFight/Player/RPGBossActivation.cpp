// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossActivation.h"
#include "Player/RPGEncounterBinding.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGActivationWorld, Log, All);

FRPGPreparationAbortReport FRPGWorldActivationResult::Release()
{
	FRPGPreparationAbortReport Report;
	if (!IsInGameThread())
	{
		Report.bRefused = true;
		Report.Errors.Add(TEXT("ActivationWorld.ReleaseNotGameThread: release on the game thread only; artifact retained"));
		return Report;
	}
	if (Batch.IsValid())
	{
		Report = Batch->Abort();
		if (!Report.bRefused) { Batch.Reset(); }
	}
	return Report;
}

FRPGPreparationAbortReport FRPGWorldActivationResult::ReleaseForRebind()
{
	FRPGPreparationAbortReport Report;
	if (!IsInGameThread())
	{
		Report.bRefused = true;
		Report.Errors.Add(TEXT("ActivationWorld.ReleaseNotGameThread: runtime release on the game thread only; artifact retained"));
		return Report;
	}
	if (Batch.IsValid())
	{
		Report = Batch->AbortForRebind();
		if (Report.IsClean()) { Batch.Reset(); }
	}
	return Report;
}

bool FRPGWorldActivationResult::RetagForRebind(const ARPGEncounterBinding& Binding, uint64 ExpectedGeneration, FString& OutError)
{
	OutError.Reset();
	if (!IsInGameThread()) { OutError = TEXT("ActivationWorld.RebindRetagNotGameThread"); return false; }
	if (!Batch.IsValid()) { OutError = TEXT("ActivationWorld.RebindRetagLeaseUnavailable"); return false; }
	return Batch->RetagForRebind(Binding, ExpectedGeneration, OutError);
}

namespace RPGBossActivation
{
	static FRPGWorldActivationResult ActivateWorldInternal(UWorld* ExpectedWorld, const ARPGEncounterBinding* Binding,
		const TArray<RPGBossWorldInputCompiler::FSelection>& Selections, const FString& ManifestHash, bool bForRebind, uint64 ParticipantGeneration)
	{
		FRPGWorldActivationResult Result;
		auto Finish = [&](ERPGWorldActivationOutcome Outcome, const TCHAR* Reason)
		{
			Result.Outcome = Outcome;
			Result.Reason = FName(Reason);
			const TCHAR* Label = Outcome == ERPGWorldActivationOutcome::Activated ? TEXT("ActivatedRegisteredSubset")
				: Outcome == ERPGWorldActivationOutcome::FallBackToLegacy ? TEXT("FallBackToLegacy") : TEXT("HardError");
			// Exactly one line per call. No UObject path is dereferenced for logging.
			UE_LOG(LogRPGActivationWorld, Display, TEXT("%s reason=%s"), Label, Reason);
		};
		if (!IsInGameThread())
		{
			Result.Errors.Add(TEXT("ActivationWorld.NotGameThread: no UObject touched"));
			Finish(ERPGWorldActivationOutcome::HardError, TEXT("ActivationWorld.NotGameThread"));
			return Result;
		}

		// The facade obtains the epoch from this world's GI; no duplicate validators, registry or manufactured fallback config.
		FRPGWorldPreparationResult Prepared = bForRebind
			? RPGBossWorldPreparation::PrepareWorldBatchForRebind(ExpectedWorld, Binding, Selections, ManifestHash, ParticipantGeneration)
			: RPGBossWorldPreparation::PrepareWorldBatch(ExpectedWorld, Binding, Selections, ManifestHash);
		if (!Prepared.Succeeded())
		{
			Result.Errors = MoveTemp(Prepared.Errors);
			const bool bContractViolation = Result.Errors.ContainsByPredicate([](const FString& Error)
			{
				return Error.StartsWith(TEXT("WorldPrep.ContractViolation:"))
					|| Error.StartsWith(TEXT("Preparation.ContractViolation["))
					|| Error.StartsWith(TEXT("WorldPrep.Drift["))
					|| Error.StartsWith(TEXT("WorldInput.ContentDrift"))
					|| Error.StartsWith(TEXT("WorldInput.BindingDrift"))
					|| Error.StartsWith(TEXT("WorldPrep.NotGameThread:"));
			});
			// Match leading diagnostic tokens, never arbitrary identifier/message substrings.
			// Mid-call authority/input mutation violates the accepted stable-input contract; do not claim it was undone.
			const bool bHardError = bForRebind || bContractViolation;
			Finish(bHardError ? ERPGWorldActivationOutcome::HardError : ERPGWorldActivationOutcome::FallBackToLegacy,
				bHardError ? (bForRebind ? TEXT("ActivationWorld.RebindRejected") : TEXT("ActivationWorld.PreparationContractViolation")) : TEXT("ActivationWorld.PrepareRejected"));
			return Result;
		}
		const bool bRegistered = bForRebind
			? Prepared.Batch->RegisterOwnedComponentsForRebind(Result.Registration)
			: Prepared.Batch->RegisterOwnedComponents(Result.Registration);
		if (!bRegistered)
		{
			Result.Errors = Result.Registration.Errors;
			// Registration already rolls back then Aborts on execution failure; state refusal may not consume it.
			// Idempotent Abort also handles that refusal, and preserves all cleanup diagnostics.
			const FRPGPreparationAbortReport Cleanup = bForRebind ? Prepared.Batch->AbortForRebind() : Prepared.Batch->Abort();
			Result.Errors.Append(Cleanup.Errors);
			const bool bClean = Result.Registration.Cleanup.IsClean() && Cleanup.IsClean()
				&& Prepared.Batch->GetOwnedComponentCount() == 0;
			Prepared.Batch.Reset();
			const bool bHardError = !bClean || bForRebind;
			Finish(bHardError ? ERPGWorldActivationOutcome::HardError : ERPGWorldActivationOutcome::FallBackToLegacy,
				bHardError ? (bClean ? TEXT("ActivationWorld.RebindRegistrationRejected") : TEXT("ActivationWorld.RegistrationContractViolation")) : TEXT("ActivationWorld.RegistrationRejected"));
			return Result;
		}
		Result.Batch = MoveTemp(Prepared.Batch);
		Finish(ERPGWorldActivationOutcome::Activated, TEXT("ActivationWorld.RegisteredSubset"));
		return Result;
	}

	FRPGWorldActivationResult ActivateWorld(UWorld* ExpectedWorld, const ARPGEncounterBinding* Binding,
		const TArray<RPGBossWorldInputCompiler::FSelection>& Selections, const FString& ManifestHash)
	{
		return ActivateWorldInternal(ExpectedWorld, Binding, Selections, ManifestHash, false, 0);
	}

	FRPGWorldActivationResult ActivateWorldForRebind(UWorld* ExpectedWorld, const ARPGEncounterBinding* Binding,
		const TArray<RPGBossWorldInputCompiler::FSelection>& Selections, const FString& ManifestHash, uint64 ParticipantGeneration)
	{
		return ActivateWorldInternal(ExpectedWorld, Binding, Selections, ManifestHash, true, ParticipantGeneration);
	}
}
