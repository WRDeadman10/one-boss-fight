// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossActivation.h"

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

namespace RPGBossActivation
{
	FRPGWorldActivationResult ActivateWorld(UWorld* ExpectedWorld, const ARPGEncounterBinding* Binding,
		const TArray<RPGBossWorldInputCompiler::FSelection>& Selections, const FString& ManifestHash)
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
		FRPGWorldPreparationResult Prepared = RPGBossWorldPreparation::PrepareWorldBatch(ExpectedWorld, Binding, Selections, ManifestHash);
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
			Finish(bContractViolation ? ERPGWorldActivationOutcome::HardError : ERPGWorldActivationOutcome::FallBackToLegacy,
				bContractViolation ? TEXT("ActivationWorld.PreparationContractViolation") : TEXT("ActivationWorld.PrepareRejected"));
			return Result;
		}
		if (!Prepared.Batch->RegisterOwnedComponents(Result.Registration))
		{
			Result.Errors = Result.Registration.Errors;
			// Registration already rolls back then Aborts on execution failure; state refusal may not consume it.
			// Idempotent Abort also handles that refusal, and preserves all cleanup diagnostics.
			const FRPGPreparationAbortReport Cleanup = Prepared.Batch->Abort();
			Result.Errors.Append(Cleanup.Errors);
			const bool bClean = Result.Registration.Cleanup.IsClean() && Cleanup.IsClean()
				&& Prepared.Batch->GetOwnedComponentCount() == 0;
			Prepared.Batch.Reset();
			Finish(bClean ? ERPGWorldActivationOutcome::FallBackToLegacy : ERPGWorldActivationOutcome::HardError,
				bClean ? TEXT("ActivationWorld.RegistrationRejected") : TEXT("ActivationWorld.RegistrationContractViolation"));
			return Result;
		}
		Result.Batch = MoveTemp(Prepared.Batch);
		Finish(ERPGWorldActivationOutcome::Activated, TEXT("ActivationWorld.RegisteredSubset"));
		return Result;
	}
}
