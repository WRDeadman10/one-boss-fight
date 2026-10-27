// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossHydrationPreflight.h"
#include "Animation/Skeleton.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"
#include "GameFramework/Character.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossPhaseAdapters.h"
#include "Player/RPGBossPhases.h"
#include "Player/RPGBossPosture.h"
#include "Player/RPGBossStatsAdapters.h"
#include "UObject/StrongObjectPtr.h"

namespace RPGBossHydrationPreflight
{
	namespace
	{
		/** The shape of the stable manifest hash the compiled config contract uses: 64 hexadecimal characters. */
		bool IsSHA256Shape(const FString& Text)
		{
			if (Text.Len() != 64)
			{
				return false;
			}
			for (const TCHAR C : Text)
			{
				if (!FChar::IsHexDigit(C))
				{
					return false;
				}
			}
			return true;
		}

		/** The slot name, or the position in the request list when the slot itself is the problem. Never reads an actor. */
		FString SlotLabel(const FRPGHydrationPreflightRequest& Request, int32 Index)
		{
			return Request.Slot.IsNone() ? FString::Printf(TEXT("#%d"), Index) : Request.Slot.ToString();
		}

		void FailMember(FRPGHydrationResult& Result, const TCHAR* Token, const FString& Slot, const FString& Detail)
		{
			Result.Fail(FString::Printf(TEXT("%s[slot=%s]: %s"), Token, *Slot, *Detail));
		}

		void FailBatch(FRPGHydrationResult& Result, const TCHAR* Token, const FString& Detail)
		{
			Result.Fail(FString::Printf(TEXT("%s: %s"), Token, *Detail));
		}

		/** The plans of one boss-core member in the deterministic legacy order of the selected subset: Phases, Encounter, Posture. Built, never run. */
		TArray<FRPGComponentPlan> MakeBossCorePlans(FName SelectedPhaseId)
		{
			TArray<FRPGComponentPlan> Plans;
			Plans.Add(RPGBossPhaseAdapters::MakePhasePlan(SelectedPhaseId));
			Plans.Add(RPGBossStatsAdapters::MakeEncounterPlan());
			Plans.Add(RPGBossStatsAdapters::MakePosturePlan());
			return Plans;
		}
	}

	TArray<UClass*> ManagedCoreConsumerClasses()
	{
		return {URPGBossPhases::StaticClass(), URPGBossEncounter::StaticClass(), URPGBossPosture::StaticClass(), URPGCombatParticipant::StaticClass()};
	}

	FRPGHydrationResult CompilePreflight(const FRPGHydrationPreflightInput& Input, TSharedPtr<const FRPGHydrationPreflightPlan>& OutPlan)
	{
		// First: no earlier output may survive a compile that fails.
		OutPlan.Reset();
		FRPGHydrationResult Result;

		// ---- Batch level: the expectations themselves must be present and valid.
		if (!IsInGameThread())
		{
			FailBatch(Result, TEXT("Preflight.NotGameThread"), TEXT("the preflight compiles on the game thread only"));
			return Result;
		}
		UWorld* World = Input.ExpectedWorld.Get(); // null for a stale or never-set world
		if (!World || !IsValid(World))
		{
			FailBatch(Result, TEXT("Preflight.NoWorld"), TEXT("the expected world is not set or is no longer valid"));
		}
		if (!Input.EncounterInstance.IsValid())
		{
			FailBatch(Result, TEXT("Preflight.InvalidEncounter"), TEXT("the encounter instance GUID is not valid"));
		}
		if (!Input.ExpectedContent.IsValid() || !Input.ExpectedContent->Id.IsValid())
		{
			FailBatch(Result, TEXT("Preflight.InvalidContent"), TEXT("the expected content lease is missing or its epoch id is not valid"));
		}
		if (Input.Requests.IsEmpty())
		{
			FailBatch(Result, TEXT("Preflight.EmptyBatch"), TEXT("the batch has no participant request"));
		}
		if (!Result.IsReady())
		{
			return Result; // member checks need valid expectations; nothing was produced
		}

		// ---- Pass 1: slots, so every target slot can be resolved against the whole batch.
		TMap<FName, int32> FirstIndexOfSlot;
		for (int32 Index = 0; Index < Input.Requests.Num(); ++Index)
		{
			const FRPGHydrationPreflightRequest& Request = Input.Requests[Index];
			if (Request.Slot.IsNone())
			{
				FailMember(Result, TEXT("Preflight.InvalidSlot"), SlotLabel(Request, Index), TEXT("the slot name is empty"));
			}
			else if (FirstIndexOfSlot.Contains(Request.Slot))
			{
				FailMember(Result, TEXT("Preflight.DuplicateSlot"), SlotLabel(Request, Index), FString::Printf(TEXT("the slot is already used by request #%d"), FirstIndexOfSlot[Request.Slot]));
			}
			else
			{
				FirstIndexOfSlot.Add(Request.Slot, Index);
			}
		}

		// ---- Pass 2: every member, completely, before anything is built.
		TSet<const AActor*> SeenActors;
		for (int32 Index = 0; Index < Input.Requests.Num(); ++Index)
		{
			const FRPGHydrationPreflightRequest& Request = Input.Requests[Index];
			const FString Label = SlotLabel(Request, Index);
			const bool bBossCore = Request.Role == ERPGPreflightRole::BossCore;

			if (Request.Role != ERPGPreflightRole::BossCore && Request.Role != ERPGPreflightRole::TargetOnly)
			{
				FailMember(Result, TEXT("Preflight.InvalidRole"), Label, TEXT("the role is not set (boss-core or target-only is required)"));
			}

			// The actor: a weak identity, resolved only through the weak pointer, so a stale actor is reported and never dereferenced.
			AActor* Actor = nullptr;
			if (Request.Actor.IsExplicitlyNull())
			{
				FailMember(Result, TEXT("Preflight.NullActor"), Label, TEXT("no actor was given"));
			}
			else if (Request.Actor.IsStale())
			{
				FailMember(Result, TEXT("Preflight.StaleActor"), Label, TEXT("the actor was destroyed or collected"));
			}
			else
			{
				Actor = Request.Actor.Get();
				if (!Actor)
				{
					FailMember(Result, TEXT("Preflight.StaleActor"), Label, TEXT("the actor can no longer be resolved"));
				}
				else if (Actor->IsActorBeingDestroyed())
				{
					FailMember(Result, TEXT("Preflight.ActorDestroying"), Label, TEXT("the actor is being destroyed"));
					Actor = nullptr;
				}
			}
			if (Actor)
			{
				if (Actor->GetWorld() != World)
				{
					FailMember(Result, TEXT("Preflight.ForeignWorld"), Label, TEXT("the actor is not in the expected world"));
				}
				if (Actor->HasActorBegunPlay() || Actor->IsActorBeginningPlay())
				{
					FailMember(Result, TEXT("Preflight.ActorBegunPlay"), Label, TEXT("the actor began or is beginning play: configuration is read before BeginPlay"));
				}
				if (SeenActors.Contains(Actor))
				{
					FailMember(Result, TEXT("Preflight.DuplicateActor"), Label, TEXT("the actor appears in more than one request"));
				}
				SeenActors.Add(Actor);
				// An already attached or configured consumer is never adopted silently: the participant component for every member, the three boss-core consumers for a boss-core member.
				const TArray<UClass*> Managed = ManagedCoreConsumerClasses();
				for (int32 ClassIndex = 0; ClassIndex < Managed.Num(); ++ClassIndex)
				{
					const bool bParticipant = Managed[ClassIndex] == URPGCombatParticipant::StaticClass();
					if ((bBossCore || bParticipant) && Actor->FindComponentByClass(Managed[ClassIndex]))
					{
						FailMember(Result, TEXT("Preflight.PreexistingConsumer"), Label, FString::Printf(TEXT("the actor already has a %s"), *Managed[ClassIndex]->GetName()));
					}
				}
			}

			// The target: explicit, another member of this batch, never a default.
			if (Request.TargetSlot.IsNone())
			{
				FailMember(Result, TEXT("Preflight.TargetMissing"), Label, TEXT("no target slot was given (no first-actor or player0 default exists)"));
			}
			else if (Request.TargetSlot == Request.Slot)
			{
				FailMember(Result, TEXT("Preflight.SelfTarget"), Label, TEXT("the target slot is the member's own slot"));
			}
			else if (!FirstIndexOfSlot.Contains(Request.TargetSlot))
			{
				FailMember(Result, TEXT("Preflight.TargetNotInBatch"), Label, FString::Printf(TEXT("the target slot '%s' is not a member of this batch"), *Request.TargetSlot.ToString()));
			}

			// The config lease.
			const FRPGParticipantConfig* Config = Request.Config.Get();
			if (!Config)
			{
				FailMember(Result, TEXT("Preflight.NoConfig"), Label, TEXT("no compiled config lease was given"));
				continue;
			}
			// The SAME lease, not an equal-looking copy of the metadata.
			if (Config->Content.Get() != Input.ExpectedContent.Get())
			{
				FailMember(Result, TEXT("Preflight.ContentLeaseMismatch"), Label, TEXT("the config does not hold the batch's expected content lease"));
			}
			if (Config->Schema != 1 || Config->BossId.IsNone() || Config->PresentationId.IsNone() || !IsSHA256Shape(Config->StableManifestHash) || Config->Fields.IsEmpty()
				|| !Config->Content.IsValid() || !Config->Content->Id.IsValid())
			{
				FailMember(Result, TEXT("Preflight.InvalidManifestIdentity"), Label, TEXT("schema, boss id, presentation id, manifest hash shape, field manifest or content epoch is not valid"));
			}
			// Production prerequisites fail closed; a synthetic fixture is accepted only in a dev-automation build.
			if (Config->bSyntheticFixture)
			{
#if !WITH_DEV_AUTOMATION_TESTS
				FailMember(Result, TEXT("Preflight.SyntheticUnavailable"), Label, TEXT("a synthetic fixture config is not available in this target"));
#endif
			}
			else if (Actor)
			{
				const ACharacter* Character = Cast<ACharacter>(Actor);
				const USkeletalMesh* Mesh = Character && Character->GetMesh() ? Character->GetMesh()->GetSkeletalMeshAsset() : nullptr;
				if (!Config->Skeleton.IsValid() || Config->Animations.IsEmpty() || !Mesh || !Config->Skeleton->IsCompatibleMesh(Mesh))
				{
					FailMember(Result, TEXT("Preflight.ProductionPrerequisite"), Label, TEXT("a production member needs the compiled skeleton and animations and a character whose mesh is compatible with that skeleton"));
				}
			}

			// The role specifics.
			if (bBossCore)
			{
				FString Error;
				if (!RPGBossStatsAdapters::ValidateStats(Config->Stats, Error))
				{
					FailMember(Result, TEXT("Preflight.StatsRejected"), Label, Error);
				}
				if (!RPGBossPhaseAdapters::ValidatePhases(Config->Phases, Request.SelectedPhaseId, Error))
				{
					FailMember(Result, TEXT("Preflight.PhaseRejected"), Label, Error);
				}
				// The union of the typed inputs the three plans read: 4 stats paths and the 4 paths of the selected phase. Membership only; a Value text is never authority.
				TSet<FString> Manifest;
				for (const FRPGParityField& Field : Config->Fields)
				{
					Manifest.Add(Field.FieldPath);
				}
				for (const FRPGComponentPlan& Plan : MakeBossCorePlans(Request.SelectedPhaseId))
				{
					for (const FString& Required : Plan.RequiredFields)
					{
						if (!Manifest.Contains(Required))
						{
							FailMember(Result, TEXT("Preflight.MissingRequiredField"), Label, FString::Printf(TEXT("required manifest path %s is not in the config"), *Required));
						}
					}
				}
			}
			else if (Request.Role == ERPGPreflightRole::TargetOnly && !Request.SelectedPhaseId.IsNone())
			{
				FailMember(Result, TEXT("Preflight.UnexpectedPhaseSelection"), Label, TEXT("a target-only member has no phase to select"));
			}
		}

		if (!Result.IsReady())
		{
			return Result; // whole-batch: one failing member publishes nothing for any member
		}

		// ---- Build: only reached when every member passed. Plans are built from the accepted factories and never run.
		TSharedRef<FRPGHydrationPreflightPlan> Plan = MakeShared<FRPGHydrationPreflightPlan>();
		Plan->EncounterInstance = Input.EncounterInstance;
		Plan->World = World;
		Plan->Content = Input.ExpectedContent;
		for (const FRPGHydrationPreflightRequest& Request : Input.Requests)
		{
			FRPGPreflightParticipantPlan Participant;
			Participant.Actor = Request.Actor;
			Participant.Slot = Request.Slot;
			Participant.TargetSlot = Request.TargetSlot;
			Participant.Role = Request.Role;
			Participant.Config = Request.Config;
			if (Request.Role == ERPGPreflightRole::BossCore)
			{
				Participant.Plans = MakeBossCorePlans(Request.SelectedPhaseId);
				for (const FRPGComponentPlan& ComponentPlan : Participant.Plans)
				{
					Participant.ClassLeases.Emplace(ComponentPlan.Class);
				}
			}
			Plan->Participants.Add(MoveTemp(Participant));
		}
		OutPlan = Plan;
		return Result;
	}
}
