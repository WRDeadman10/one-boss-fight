// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossWorldPreparation.h"

#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"
#include "Player/RPGCombatCatalog.h"
#include "Player/RPGEncounterBinding.h"

namespace
{
	/** The identities this facade holds around both stages. Captured before the input stage (from the live binding), completed from the compiled input, checked after each stage. */
	struct FIdentity
	{
		struct FMember
		{
			TWeakObjectPtr<AActor> Actor;
			FName Slot;
			FName TargetSlot;
			TWeakObjectPtr<URPGBossDefinition> Definition;
		};

		TWeakObjectPtr<UWorld> World;
		TWeakObjectPtr<UGameInstance> GameInstance;
		TWeakObjectPtr<const ARPGEncounterBinding> Binding;
		FGuid Encounter;
		TArray<FMember> Members;
		/** The very epoch lease the compiled input holds (set by Complete). */
		TSharedPtr<const RPGCombatRegistry::FEpoch> Content;
		bool bCaptured = false;
		bool bCompleted = false;
	};

	/** Reads the live binding. False when the world or the binding cannot be read (the input stage then reports the real reason; a success of that stage after a failed capture is drift). */
	bool Capture(UWorld* World, const ARPGEncounterBinding* Binding, FIdentity& Out)
	{
		if (!World || !IsValid(World) || !Binding || !IsValid(Binding))
		{
			return false;
		}
		Out.World = World;
		Out.GameInstance = World->GetGameInstance();
		Out.Binding = Binding;
		Out.Encounter = Binding->EncounterInstance;
		for (const FRPGPlacedParticipantBinding& Participant : Binding->Participants)
		{
			FIdentity::FMember Member;
			Member.Actor = Participant.Actor.Get();
			Member.Slot = Participant.Slot;
			Member.TargetSlot = Participant.TargetSlot;
			Member.Definition = Participant.Definition.Get();
			Out.Members.Add(Member);
		}
		Out.bCaptured = true;
		return true;
	}

	/** Completes the identity from the compiled input and requires that the input is exactly the captured encounter: world, GUID, one request per participant with the same actor, slot and target. */
	bool Complete(FIdentity& Identity, UWorld* World, const FRPGHydrationPreflightInput& Input, FString& Why)
	{
		if (!Identity.bCaptured)
		{
			Why = TEXT("the world and binding identities could not be captured before the input stage");
			return false;
		}
		if (Input.ExpectedWorld.Get() != World || Input.EncounterInstance != Identity.Encounter || !Input.ExpectedContent.IsValid() || Input.Requests.Num() != Identity.Members.Num())
		{
			Why = TEXT("the compiled input is not the captured world, encounter GUID and participant count");
			return false;
		}
		for (int32 Index = 0; Index < Input.Requests.Num(); ++Index)
		{
			const FRPGHydrationPreflightRequest& Request = Input.Requests[Index];
			const FIdentity::FMember& Member = Identity.Members[Index];
			if (Request.Actor.Get() != Member.Actor.Get() || Request.Slot != Member.Slot || Request.TargetSlot != Member.TargetSlot)
			{
				Why = FString::Printf(TEXT("request #%d of the compiled input is not participant #%d of the captured binding"), Index, Index);
				return false;
			}
		}
		Identity.Content = Input.ExpectedContent;
		Identity.bCompleted = true;
		return true;
	}

	/** The checkpoint, run after the input stage and after the preparation stage. */
	bool Holds(UWorld* World, const FIdentity& Identity, FString& Why)
	{
		if (!Identity.bCompleted || !Identity.World.IsValid() || Identity.World.Get() != World || !IsValid(World))
		{
			Why = TEXT("the world changed or is no longer valid");
			return false;
		}
		UGameInstance* GameInstance = World->GetGameInstance();
		if (!GameInstance || GameInstance != Identity.GameInstance.Get() || !IsValid(GameInstance))
		{
			Why = TEXT("the world's game instance changed or is no longer valid");
			return false;
		}
		if (RPGCombatRegistry::ForWorld(World).Get() != Identity.Content.Get())
		{
			Why = TEXT("the published epoch is no longer the very lease the compiled input holds");
			return false;
		}
		const ARPGEncounterBinding* Live = Identity.Binding.Get();
		if (!Live || !IsValid(Live) || Live->IsActorBeingDestroyed() || Live->GetWorld() != World || Live->HasActorBegunPlay() || Live->IsActorBeginningPlay())
		{
			Why = TEXT("the encounter binding is no longer valid, is being destroyed, is not in the world or began play");
			return false;
		}
		if (Live->EncounterInstance != Identity.Encounter || Live->Participants.Num() != Identity.Members.Num())
		{
			Why = TEXT("the encounter GUID or the participant count of the binding changed");
			return false;
		}
		for (int32 Index = 0; Index < Identity.Members.Num(); ++Index)
		{
			const FRPGPlacedParticipantBinding& Participant = Live->Participants[Index];
			const FIdentity::FMember& Member = Identity.Members[Index];
			if (Participant.Slot != Member.Slot || Participant.TargetSlot != Member.TargetSlot || Participant.Actor.Get() != Member.Actor.Get() || Participant.Definition.Get() != Member.Definition.Get())
			{
				Why = FString::Printf(TEXT("participant #%d of the binding changed"), Index);
				return false;
			}
			const AActor* Actor = Member.Actor.Get();
			if (!Actor || !IsValid(Actor) || Actor->IsActorBeingDestroyed() || Actor->GetWorld() != World || Actor->HasActorBegunPlay() || Actor->IsActorBeginningPlay() || !Member.Definition.Get() || !IsValid(Member.Definition.Get()))
			{
				Why = FString::Printf(TEXT("the actor or the definition of participant #%d is no longer valid, in the world and not begun"), Index);
				return false;
			}
		}
		return true;
	}
}

namespace RPGBossWorldPreparation
{
	FRPGWorldPreparationResult PrepareWorldBatch(UWorld* ExpectedWorld, const ARPGEncounterBinding* Binding, const TArray<RPGBossWorldInputCompiler::FSelection>& Selections, const FString& ManifestHash)
	{
		FRPGWorldPreparationResult Result;
		// Before any UObject (the world, the binding) is touched.
		if (!IsInGameThread())
		{
			Result.Errors.Add(TEXT("WorldPrep.NotGameThread: a world batch is prepared on the game thread only (nothing was touched)"));
			return Result;
		}

		FIdentity Identity;
		Capture(ExpectedWorld, Binding, Identity);

		// Stage 1: the world-bound input (the epoch comes only from the world's own game instance). Its diagnostics, nested layers included, are carried unchanged.
		FRPGHydrationPreflightInput Input;
		const FRPGHydrationResult Compiled = RPGBossWorldInputCompiler::CompileWorldInput(ExpectedWorld, Binding, Selections, ManifestHash, Input);
		if (!Compiled.IsReady())
		{
			Result.Errors = Compiled.Errors;
			return Result; // nothing was allocated: the input stage creates no component
		}
		FString Why;
		if (!Complete(Identity, ExpectedWorld, Input, Why) || !Holds(ExpectedWorld, Identity, Why))
		{
			Result.Errors.Add(FString::Printf(TEXT("WorldPrep.Drift[after the input stage]: %s (nothing was allocated)"), *Why));
			return Result;
		}

		// Stage 2: the owned unregistered preparation of the whole batch. Its diagnostics are carried unchanged.
		FRPGPreparationResult Prepared = RPGBossHydrationPreparation::PrepareBatch(Input);
		if (!Prepared.Succeeded())
		{
			Result.Errors = Prepared.Errors; // PrepareBatch already destroyed everything it allocated
			if (Result.Errors.IsEmpty())
			{
				Result.Errors.Add(TEXT("WorldPrep.PreparationRejected: the preparation returned no artifact and no error"));
			}
			return Result;
		}

		// The same checkpoint after the preparation. A failure aborts precisely the components this call allocated.
		if (!Holds(ExpectedWorld, Identity, Why))
		{
			Result.Errors.Add(FString::Printf(TEXT("WorldPrep.Drift[after the preparation stage]: %s (this call's components were aborted)"), *Why));
			const FRPGPreparationAbortReport Cleanup = Prepared.Batch->Abort();
			for (const FString& CleanupError : Cleanup.Errors)
			{
				Result.Errors.Add(FString::Printf(TEXT("WorldPrep.CleanupAfterDrift: %s"), *CleanupError));
			}
			if (Cleanup.ContractViolations > 0 || Cleanup.bRefused)
			{
				Result.Errors.Add(FString::Printf(TEXT("WorldPrep.ContractViolation: the cleanup after drift left %d component(s) in place (violations) or was refused"), Cleanup.ContractViolations));
			}
			return Result; // the artifact is destroyed with Prepared; none escapes
		}

		Result.Batch = MoveTemp(Prepared.Batch);
		return Result;
	}
}
