// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossHydrationPreflight.h"
#include "Audio/RPGFootsteps.h"
#include "Audio/RPGBossMusic.h"
#include "Player/RPGDamageResolver.h"
#include "Player/RPGTraceGuard.h"
#include "UI/RPGBossHud.h"
#include "Player/RPGLegend.h"
#include "Sound/SoundBase.h"
#include "Animation/AnimSequenceBase.h"
#include "Animation/Skeleton.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"
#include "GameFramework/Character.h"
#include "Player/RPGBossDormantWake.h"
#include "Player/RPGBossDormantWakeAdapters.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossEncounterClusterAdapters.h"
#include "Player/RPGBossPhases.h"
#include "Player/RPGBossPhasesClusterAdapters.h"
#include "Player/RPGBossPosture.h"
#include "Player/RPGBossStagger.h"
#include "Player/RPGBossStaggerClusterAdapters.h"
#include "Player/RPGBossStatsAdapters.h"
#include "Player/RPGBossBleed.h"
#include "Player/RPGBossBleedAdapters.h"
#include "Player/RPGBossLowSweep.h"
#include "Player/RPGBossLowSweepAdapters.h"
#include "Player/RPGBossShockwave.h"
#include "Player/RPGBossShockwaveAdapters.h"
#include "Player/RPGBossHealPunish.h"
#include "Player/RPGBossHealPunishAdapters.h"
#include "Player/RPGBossLook.h"
#include "Player/RPGBossLookAdapters.h"
#include "Player/RPGBossCloseClipSwap.h"
#include "Player/RPGBossCloseClipSwapAdapters.h"
#include "Player/RPGBossDeath.h"
#include "Player/RPGBossDeathAdapters.h"
#include "Player/RPGBossAttackTrackerAdapters.h"
#include "Player/RPGAttackTracker.h"
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

		template <typename T>
		T* RequireNativeComponent(UActorComponent& Component, FString& Error)
		{
			T* Typed = Cast<T>(&Component);
			if (!Typed)
			{
				Error = FString::Printf(TEXT("WrongComponentClass: expected %s, received %s"), *T::StaticClass()->GetName(), *Component.GetClass()->GetName());
				return nullptr;
			}
			Error.Reset();
			return Typed;
		}

		/** The number of plans of one boss-core member, each exactly once. */
		constexpr int32 BossCorePlanCount = 19;

		/** The fourteen typed plans followed by five configuration-independent legacy parity consumers, in deterministic relative plan order: Stagger, Phases
		 *  (with the explicit selected id, captured by value), Encounter, DormantWake, Posture, Bleed, LowSweep, Shockwave, HealPunish, Look, CloseClipSwap, Death, AttackTracker. The order is a plan order, not an observed registration or BeginPlay chronology. Built, never run. */
		TArray<FRPGComponentPlan> MakeBossCorePlans(FName SelectedPhaseId)
		{
			TArray<FRPGComponentPlan> Plans;
			Plans.Add(RPGBossStaggerClusterAdapters::MakeStaggerClusterPlan());
			Plans.Add(RPGBossPhasesClusterAdapters::MakePhasesClusterPlan(SelectedPhaseId));
			Plans.Add(RPGBossEncounterClusterAdapters::MakeEncounterClusterPlan());
			Plans.Add(RPGBossDormantWakeAdapters::MakeDormantWakePlan());
			Plans.Add(RPGBossStatsAdapters::MakePosturePlan());
			Plans.Add(RPGBossBleedAdapters::MakeBleedPlan());
			Plans.Add(RPGBossLowSweepAdapters::MakeLowSweepPlan());
			Plans.Add(RPGBossShockwaveAdapters::MakeShockwavePlan());
			Plans.Add(RPGBossHealPunishAdapters::MakeHealPunishPlan());
			Plans.Add(RPGBossLookAdapters::MakeLookPlan());
			Plans.Add(RPGBossCloseClipSwapAdapters::MakeCloseClipSwapPlan());
			Plans.Add(RPGBossDeathAdapters::MakeDeathPlan());
			Plans.Add(RPGBossAttackTrackerAdapters::MakeAttackTrackerPlan());
			// These six consumers were historically attached by AttachLegacyBossPrelude/Bundle. They have
			// no authorable definition fields; their exact maintained defaults and asset paths are applied
			// during preparation and their instances share the BossCore lease/cleanup lifecycle.
			auto AddNative = [&Plans](UClass* Class, FName Name, TFunction<bool(UActorComponent&, const FRPGParticipantConfig&, FString&)> Configure)
			{
				FRPGComponentPlan Plan;
				Plan.Class = Class;
				Plan.InstanceName = Name;
				Plan.bConfigurationIndependent = true;
				Plan.Configure = MoveTemp(Configure);
				Plans.Add(MoveTemp(Plan));
			};
			AddNative(URPGFootsteps::StaticClass(), TEXT("RPGFootsteps"), [](UActorComponent& Component, const FRPGParticipantConfig&, FString& Error)
			{
				URPGFootsteps* Steps = RequireNativeComponent<URPGFootsteps>(Component, Error);
				if (!Steps) { return false; }
				Steps->WalkSound = LoadObject<USoundBase>(nullptr, TEXT("/Game/Essential_Foosteps_SK/CUE/Concrete/Footstep_Concrete_Boots_Walk_1_Cue.Footstep_Concrete_Boots_Walk_1_Cue"));
				Steps->JogSound = LoadObject<USoundBase>(nullptr, TEXT("/Game/Essential_Foosteps_SK/CUE/Concrete/Footstep_Concrete_Boots_Jog_8_Cue.Footstep_Concrete_Boots_Jog_8_Cue"));
				Steps->RunSound = LoadObject<USoundBase>(nullptr, TEXT("/Game/Essential_Foosteps_SK/CUE/Concrete/Footstep_Concrete_Boots_Run_8_Cue.Footstep_Concrete_Boots_Run_8_Cue"));
				Steps->LandSound = LoadObject<USoundBase>(nullptr, TEXT("/Game/Essential_Foosteps_SK/CUE/Concrete/Footstep_Concrete_Boots_Land_4_Cue.Footstep_Concrete_Boots_Land_4_Cue"));
				Steps->PitchScale = 0.62f; Steps->VolumeScale = 1.5f; Steps->AudibleRange = 4500.f; Steps->JogSpeed = 200.f; Steps->RunSpeed = 420.f;
				return true;
			});
			AddNative(URPGBossMusic::StaticClass(), TEXT("RPGBossMusic"), [](UActorComponent& Component, const FRPGParticipantConfig&, FString& Error)
			{
				URPGBossMusic* Music = RequireNativeComponent<URPGBossMusic>(Component, Error);
				if (!Music) { return false; }
				Music->Music = LoadObject<USoundBase>(nullptr, TEXT("/Game/OneBossFight/Audio/MX_Boss01_Phase1.MX_Boss01_Phase1"), nullptr, LOAD_NoWarn);
				if (!Music->Music) { Music->Music = LoadObject<USoundBase>(nullptr, TEXT("/Game/StarterContent/Audio/Starter_Music_Cue.Starter_Music_Cue")); }
				Music->PhaseTwoMusic = LoadObject<USoundBase>(nullptr, TEXT("/Game/OneBossFight/Audio/MX_Boss01_Phase2.MX_Boss01_Phase2"), nullptr, LOAD_NoWarn);
				return true;
			});
			AddNative(URPGTraceGuard::StaticClass(), TEXT("RPGTraceGuard"), [](UActorComponent& Component, const FRPGParticipantConfig&, FString& Error) { return RequireNativeComponent<URPGTraceGuard>(Component, Error) != nullptr; });
			AddNative(URPGBossHud::StaticClass(), TEXT("RPGBossHud"), [](UActorComponent& Component, const FRPGParticipantConfig&, FString& Error) { return RequireNativeComponent<URPGBossHud>(Component, Error) != nullptr; });
			FRPGComponentPlan LegendPlan;
			LegendPlan.Class = URPGBossLegend::StaticClass();
			LegendPlan.InstanceName = TEXT("RPGBossLegend");
			LegendPlan.bConfigurationIndependent = true; // additive parry policy has native defaults when an older definition omits it
			LegendPlan.OptionalFields = {
				RPGParrySlowMotionConfigRules::FieldPerfectEnabled, RPGParrySlowMotionConfigRules::FieldPerfectScale,
				RPGParrySlowMotionConfigRules::FieldPerfectSeconds, RPGParrySlowMotionConfigRules::FieldNormalEnabled,
				RPGParrySlowMotionConfigRules::FieldNormalScale, RPGParrySlowMotionConfigRules::FieldNormalSeconds,
				RPGParrySlowMotionConfigRules::FieldCooldownSeconds};
			LegendPlan.Configure = [](UActorComponent& Component, const FRPGParticipantConfig& Config, FString& Error)
			{
				URPGBossLegend* Legend = RequireNativeComponent<URPGBossLegend>(Component, Error);
				if (!Legend) { return false; }
				Legend->ParrySlowMotion = Config.ParrySlowMotion;
				return true;
			};
			Plans.Add(MoveTemp(LegendPlan));
			AddNative(URPGDamageResolver::StaticClass(), TEXT("RPGDamageResolver"), [](UActorComponent& Component, const FRPGParticipantConfig&, FString& Error) { return RequireNativeComponent<URPGDamageResolver>(Component, Error) != nullptr; });
			return Plans;
		}

		/** Every plan is checked before anything is published; nothing invalid or duplicate is silently discarded: the count, a class, an instance name and a bound callback for each plan, no duplicate class or instance
		 *  name, no empty or repeated required path WITHIN a plan (a path named by two different plans is not an error: the union is a set). Pure data checks, no callback is invoked. Returns one message per problem. */
		TArray<FString> CheckPlans(const TArray<FRPGComponentPlan>& Plans)
		{
			TArray<FString> Problems;
			if (Plans.Num() != BossCorePlanCount)
			{
				Problems.Add(FString::Printf(TEXT("%d plans were built, %d are expected"), Plans.Num(), BossCorePlanCount));
			}
			TSet<const UClass*> Classes;
			TSet<FName> Names;
			for (int32 Index = 0; Index < Plans.Num(); ++Index)
			{
				const FRPGComponentPlan& Plan = Plans[Index];
				if (!Plan.Class)
				{
					Problems.Add(FString::Printf(TEXT("plan #%d has no component class"), Index));
				}
				else if (Classes.Contains(Plan.Class))
				{
					Problems.Add(FString::Printf(TEXT("plan #%d repeats the component class %s"), Index, *Plan.Class->GetName()));
				}
				else
				{
					Classes.Add(Plan.Class);
				}
				if (Plan.InstanceName.IsNone())
				{
					Problems.Add(FString::Printf(TEXT("plan #%d has no instance name"), Index));
				}
				else if (Names.Contains(Plan.InstanceName))
				{
					Problems.Add(FString::Printf(TEXT("plan #%d repeats the instance name %s"), Index, *Plan.InstanceName.ToString()));
				}
				else
				{
					Names.Add(Plan.InstanceName);
				}
				if (!Plan.Configure)
				{
					Problems.Add(FString::Printf(TEXT("plan #%d has no configure callback"), Index));
				}
				if (Plan.RequiredFields.IsEmpty() && !Plan.bConfigurationIndependent)
				{
					Problems.Add(FString::Printf(TEXT("plan #%d names no required field"), Index));
				}
				TSet<FString> Paths;
				for (const FString& Path : Plan.RequiredFields)
				{
					if (Path.IsEmpty())
					{
						Problems.Add(FString::Printf(TEXT("plan #%d names an empty required path"), Index));
					}
					else if (Paths.Contains(Path))
					{
						Problems.Add(FString::Printf(TEXT("plan #%d names the required path %s twice"), Index, *Path));
					}
					else
					{
						Paths.Add(Path);
					}
				}
				for (const FString& Path : Plan.OptionalFields)
				{
					if (Path.IsEmpty() || Paths.Contains(Path))
					{
						Problems.Add(FString::Printf(TEXT("plan #%d has an empty, repeated, or required optional path %s"), Index, *Path));
					}
					else
					{
						Paths.Add(Path);
					}
				}
			}
			return Problems;
		}
	}

	TArray<UClass*> ManagedCoreConsumerClasses()
	{
		return {URPGBossPhases::StaticClass(), URPGBossEncounter::StaticClass(), URPGBossPosture::StaticClass(), URPGBossStagger::StaticClass(), URPGBossDormantWake::StaticClass(), URPGCombatParticipant::StaticClass(), URPGBossBleed::StaticClass(), URPGBossLowSweep::StaticClass(), URPGBossShockwave::StaticClass(), URPGBossHealPunish::StaticClass(), URPGBossLook::StaticClass(), URPGBossCloseClipSwap::StaticClass(), URPGBossDeath::StaticClass(), URPGAttackTracker::StaticClass(), URPGFootsteps::StaticClass(), URPGBossMusic::StaticClass(), URPGTraceGuard::StaticClass(), URPGBossHud::StaticClass(), URPGBossLegend::StaticClass(), URPGDamageResolver::StaticClass()};
	}

	bool CheckCompiledDependencies(const FRPGParticipantConfig& Config, FString& OutError)
	{
		OutError.Reset();
		TArray<FString> Problems;
		const USkeleton* Skeleton = Config.Skeleton.Get();
		if (!Skeleton || !IsValid(Skeleton))
		{
			Problems.Add(TEXT("the compiled skeleton is missing or no longer valid"));
		}
		if (Config.Animations.IsEmpty())
		{
			Problems.Add(TEXT("the config holds no compiled animation"));
		}
		// Every entry, not only the first: a non-empty array can still hold a null lease or an animation of another skeleton. Nothing is loaded, retargeted or substituted.
		for (int32 Index = 0; Index < Config.Animations.Num(); ++Index)
		{
			const UAnimSequenceBase* Animation = Config.Animations[Index].Get();
			if (!Animation || !IsValid(Animation))
			{
				Problems.Add(FString::Printf(TEXT("animation lease #%d is not valid"), Index));
			}
			else if (Skeleton && Animation->GetSkeleton() != Skeleton)
			{
				const USkeleton* Own = Animation->GetSkeleton();
				Problems.Add(FString::Printf(TEXT("animation #%d (%s) belongs to skeleton %s, not the compiled skeleton %s; an explicit retargeted dependency must be compiled into the config, none is loaded or substituted here"),
					Index, *Animation->GetName(), Own ? *Own->GetName() : TEXT("none"), *Skeleton->GetName()));
			}
		}
		if (!Problems.IsEmpty())
		{
			OutError = FString::Join(Problems, TEXT("; "));
			return false;
		}
		return true;
	}

	static FRPGHydrationResult CompilePreflightInternal(const FRPGHydrationPreflightInput& Input, TSharedPtr<const FRPGHydrationPreflightPlan>& OutPlan, bool bAllowBegunPlay)
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
				if (Actor->IsActorBeginningPlay() || (Actor->HasActorBegunPlay() && !bAllowBegunPlay))
				{
					FailMember(Result, TEXT("Preflight.ActorBegunPlay"), Label, TEXT("the actor began or is beginning play: configuration is read before BeginPlay"));
				}
				if (SeenActors.Contains(Actor))
				{
					FailMember(Result, TEXT("Preflight.DuplicateActor"), Label, TEXT("the actor appears in more than one request"));
				}
				SeenActors.Add(Actor);
				// An already attached or configured consumer is never adopted silently: the participant component for every member, the five configuration-independent and fourteen typed boss-core consumers for a boss-core member (a target-only member gets no boss plan and is not checked for them).
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
				// Two separate reasons, each reported on its own: the compiled dependencies held by the config (every animation lease and skeleton identity), and the actor's mesh.
				FString DependencyError;
				if (!CheckCompiledDependencies(*Config, DependencyError))
				{
					FailMember(Result, TEXT("Preflight.ProductionPrerequisite"), Label, DependencyError);
				}
				const ACharacter* Character = Cast<ACharacter>(Actor);
				const USkeletalMesh* Mesh = Character && Character->GetMesh() ? Character->GetMesh()->GetSkeletalMeshAsset() : nullptr;
				USkeleton* CompiledSkeleton = Config->Skeleton.Get();
				if (!Mesh || !CompiledSkeleton || !IsValid(CompiledSkeleton) || !CompiledSkeleton->IsCompatibleMesh(Mesh))
				{
					FailMember(Result, TEXT("Preflight.ProductionPrerequisite"), Label, TEXT("a production member must be a character whose mesh is compatible with the compiled skeleton"));
				}
			}

			// The role specifics.
			if (bBossCore)
			{
				// Every cluster is validated with its full accepted validator, in the relative plan order, and EVERY failure is collected with this member's slot (no early return): a backend capability that the generic
				// definition compiler accepts fails here. Nothing is clamped, defaulted, parsed from a manifest Value text or substituted, and the validators are the shared ones, unchanged.
				FString Error;
				if (!RPGBossStaggerClusterAdapters::ValidateStaggerCluster(*Config, Error))
				{
					FailMember(Result, TEXT("Preflight.StaggerRejected"), Label, Error);
				}
				if (!RPGBossPhasesClusterAdapters::ValidatePhasesCluster(*Config, Request.SelectedPhaseId, Error))
				{
					FailMember(Result, TEXT("Preflight.PhaseRejected"), Label, Error);
				}
				// The encounter cluster validates the COMPLETE stats record (so the posture stats are covered too) and then the encounter policy; the token names which record failed, by the accepted
				// validators' own diagnostic prefix (the policy tokens start with InvalidPolicy.).
				if (!RPGBossEncounterClusterAdapters::ValidateEncounterCluster(*Config, Error))
				{
					FailMember(Result, Error.StartsWith(TEXT("InvalidPolicy.")) ? TEXT("Preflight.EncounterPolicyRejected") : TEXT("Preflight.StatsRejected"), Label, Error);
				}
				if (!RPGBossDormantWakeAdapters::ValidateDormantWake(Config->DormantWake, Error))
				{
					FailMember(Result, TEXT("Preflight.DormantWakeRejected"), Label, Error);
				}
				if (!RPGBossAttackTrackerAdapters::ValidateAttackTracker(Config->AttackTracker, Error))
				{
					FailMember(Result, TEXT("Preflight.AttackTrackerRejected"), Label, Error);
				}
				const FRPGParrySlowMotionConfig& Parry = Config->ParrySlowMotion;
				FString ParryError;
				if (!RPGParrySlowMotionConfigRules::Validate(Parry, ParryError))
				{
					FailMember(Result, TEXT("Preflight.ParrySlowMotionRejected"), Label, ParryError);
				}
				const TCHAR* ParryPaths[] = {RPGParrySlowMotionConfigRules::FieldPerfectEnabled, RPGParrySlowMotionConfigRules::FieldPerfectScale,
					RPGParrySlowMotionConfigRules::FieldPerfectSeconds, RPGParrySlowMotionConfigRules::FieldNormalEnabled,
					RPGParrySlowMotionConfigRules::FieldNormalScale, RPGParrySlowMotionConfigRules::FieldNormalSeconds,
					RPGParrySlowMotionConfigRules::FieldCooldownSeconds};
				bool bMissingParryProvenance = false;
				bool bHasAnyParryProvenance = false;
				for (const TCHAR* Path : ParryPaths)
				{
					const bool bPresent = Config->Fields.ContainsByPredicate([Path](const FRPGParityField& Field) { return Field.FieldPath == Path; });
					bHasAnyParryProvenance |= bPresent;
					bMissingParryProvenance |= !bPresent;
				}
				if (bHasAnyParryProvenance && bMissingParryProvenance)
				{
					FailMember(Result, TEXT("Preflight.ParrySlowMotionProvenanceIncomplete"), Label, TEXT("optional policy fields must be supplied as a complete typed group"));
				}
				if (bMissingParryProvenance && !RPGParrySlowMotionConfigRules::IsNativeProposal(Parry))
				{
					FailMember(Result, TEXT("Preflight.ParrySlowMotionProvenanceMissing"), Label, TEXT("non-default parry slow-motion config requires all seven typed source fields"));
				}
				// The plans of this member are built here only to be CHECKED (class, instance name, callback bound, no duplicate) and for the union of 115 required paths plus eight separately counted optional typed paths (seven parry fields and the look sword offset), the selected-phase
				// paths from the explicit selected id. Optional paths are typed inputs. Membership only; a Value text is never authority. No callback is invoked.
				const TArray<FRPGComponentPlan> MemberPlans = MakeBossCorePlans(Request.SelectedPhaseId);
				for (const FString& Problem : CheckPlans(MemberPlans))
				{
					FailMember(Result, TEXT("Preflight.PlanInvalid"), Label, Problem);
				}
				TSet<FString> Manifest;
				for (const FRPGParityField& Field : Config->Fields)
				{
					Manifest.Add(Field.FieldPath);
				}
				TSet<FString> Reported;
				for (const FRPGComponentPlan& Plan : MemberPlans)
				{
					for (const FString& Required : Plan.RequiredFields)
					{
						if (!Manifest.Contains(Required) && !Reported.Contains(Required))
						{
							Reported.Add(Required);
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
		Plan->ParticipantGeneration = Input.ParticipantGeneration;
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

	FRPGHydrationResult CompilePreflight(const FRPGHydrationPreflightInput& Input, TSharedPtr<const FRPGHydrationPreflightPlan>& OutPlan)
	{
		return CompilePreflightInternal(Input, OutPlan, false);
	}

	FRPGHydrationResult CompilePreflightForRebind(const FRPGHydrationPreflightInput& Input, TSharedPtr<const FRPGHydrationPreflightPlan>& OutPlan)
	{
		return CompilePreflightInternal(Input, OutPlan, true);
	}
}
