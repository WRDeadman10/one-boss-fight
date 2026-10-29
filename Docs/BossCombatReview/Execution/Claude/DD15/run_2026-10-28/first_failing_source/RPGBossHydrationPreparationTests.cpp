// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Async/Async.h"
#include "Components/ActorComponent.h"
#include "Components/SceneComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"
#include "Player/RPGBossDormantWake.h"
#include "Player/RPGBossDormantWakeAdapters.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossEncounterClusterAdapters.h"
#include "Player/RPGBossHydrationPreparation.h"
#include "Player/RPGBossPhases.h"
#include "Player/RPGBossPhasesClusterAdapters.h"
#include "Player/RPGBossPosture.h"
#include "Player/RPGBossStagger.h"
#include "Player/RPGBossStaggerClusterAdapters.h"
#include "Player/RPGBossStatsAdapters.h"
#include "UObject/StrongObjectPtr.h"

// These tests prove the unregistered batch preparation primitive on real isolated UE objects (a headless game world, plain native actors, the accepted synthetic config shape): the success shape (ten real owned
// components, unregistered, never begun), whole-batch rejection before any allocation, explicit and scope-exit abort, exclusivity of the owned components, cleanup after an INJECTED failure after real allocations and
// configures (a dev-automation-only ordinal, never an organically reproduced native failure), and the lifetime branches (a component destroyed first, an actor destroyed first, the world torn down first, a component
// registered by someone else, the off-thread refusals).
// They do NOT prove a startup hook, registration, BeginPlay, a context binding, a reservation, a ready context, a legacy suppression, the real game-instance content epoch, an organic native configure failure (the
// accepted callbacks cannot fail for a batch the preflight accepted), a real-asset load (DD14 holds that evidence and this file loads nothing), or the engine's behaviour for a destroyed component whose name is reused
// after garbage collection (no collection is forced here).

namespace
{
namespace PreparationTests
{
	using FEpochPtr = TSharedPtr<const RPGCombatRegistry::FEpoch>;
	using FConfigPtr = TSharedPtr<const FRPGParticipantConfig>;

	const FName PhaseTwo(TEXT("PhaseTwo"));
	const FName PhaseAlt(TEXT("PhaseAlt"));

	/** Test-local game world with the set-up the earlier headless tests used; destroyed with the scope. */
	struct FPreparationWorld
	{
		UWorld* World = nullptr;

		FPreparationWorld()
		{
			if (!GEngine)
			{
				return;
			}
			World = UWorld::CreateWorld(EWorldType::Game, /*bInformEngineOfWorld=*/false);
			if (World)
			{
				FWorldContext& Context = GEngine->CreateNewWorldContext(EWorldType::Game);
				Context.SetCurrentWorld(World);
				World->InitializeActorsForPlay(FURL());
			}
		}

		~FPreparationWorld()
		{
			if (World)
			{
				GEngine->DestroyWorldContext(World);
				World->DestroyWorld(/*bInformEngineOfWorld=*/false);
			}
		}

		FPreparationWorld(const FPreparationWorld&) = delete;
		FPreparationWorld& operator=(const FPreparationWorld&) = delete;

		AActor* SpawnActor() const { return World ? World->SpawnActor<AActor>() : nullptr; }
	};

	/** The manifest paths the five boss-core plans read for a selected phase id (the union of the five accepted factories). DD13 holds the independent literal list; this file does not test membership, it only needs a manifest the preflight accepts. */
	TArray<FString> RequiredPaths(FName PhaseId)
	{
		TArray<FRPGComponentPlan> Plans;
		Plans.Add(RPGBossStaggerClusterAdapters::MakeStaggerClusterPlan());
		Plans.Add(RPGBossPhasesClusterAdapters::MakePhasesClusterPlan(PhaseId));
		Plans.Add(RPGBossEncounterClusterAdapters::MakeEncounterClusterPlan());
		Plans.Add(RPGBossDormantWakeAdapters::MakeDormantWakePlan());
		Plans.Add(RPGBossStatsAdapters::MakePosturePlan());
		TArray<FString> Paths;
		for (const FRPGComponentPlan& ComponentPlan : Plans)
		{
			for (const FString& Path : ComponentPlan.RequiredFields)
			{
				Paths.AddUnique(Path);
			}
		}
		return Paths;
	}

	FRPGParityField MakeField(const FString& Path)
	{
		FRPGParityField Field;
		Field.FieldPath = Path;
		Field.Type = TEXT("float");
		Field.Value = TEXT("synthetic, not authority");
		Field.SourcePath = TEXT("synthetic fixture, not live provenance");
		Field.SourceSHA256 = FString::ChrN(64, TEXT('a'));
		Field.SourceSite = TEXT("fixture");
		Field.Origin = TEXT("harness");
		Field.Precedence = TEXT("fixture");
		Field.Destination = TEXT("fixture");
		Field.FirstRead = TEXT("BeginPlay");
		Field.Witness = TEXT("synthetic only");
		return Field;
	}

	/** A hand-built valid config (the authoring defaults for every record the case does not change), with its own stats, stagger seconds and one phase. */
	FConfigPtr BuildConfig(FEpochPtr Content, const TCHAR* BossId, FName PhaseId, float Threshold, float Health, float Posture, float StaggerSeconds)
	{
		TSharedRef<FRPGParticipantConfig> Value = MakeShared<FRPGParticipantConfig>();
		Value->BossId = FName(BossId);
		Value->PresentationId = FName(TEXT("PreparationLook"));
		Value->Schema = 1;
		Value->StableManifestHash = FString::ChrN(64, TEXT('b'));
		Value->Stats.MaxHealth = Health;
		Value->Stats.MaxPosture = Posture;
		Value->Stats.PostureRegenDelay = 4.25f;
		Value->Stats.PostureRegenRate = 9.75f;
		Value->StaggerPolicy.StaggerSeconds = StaggerSeconds;
		FRPGPhaseConfig Phase;
		Phase.PhaseId = PhaseId;
		Phase.EntryHealthFraction = Threshold;
		Phase.SpeedMultiplier = 1.5f;
		Phase.RateMultiplier = 1.75f;
		Phase.AttackMultiplier = 2.f;
		Value->Phases.Add(Phase);
		for (const FString& Path : RequiredPaths(PhaseId))
		{
			Value->Fields.Add(MakeField(Path));
		}
		Value->Content = Content;
		Value->bSyntheticFixture = true;
		return Value;
	}

	FRPGHydrationPreflightRequest MakeRequest(AActor* Actor, const TCHAR* Slot, const TCHAR* Target, ERPGPreflightRole Role, FConfigPtr Config, FName Phase = NAME_None)
	{
		FRPGHydrationPreflightRequest Request;
		Request.Actor = Actor;
		Request.Slot = FName(Slot);
		Request.TargetSlot = FName(Target);
		Request.Role = Role;
		Request.Config = Config;
		Request.SelectedPhaseId = Phase;
		return Request;
	}

	/** What a compile, a preparation or an abort must leave alone, per actor: the sorted component set, the registered and begun flags of each, the begun flag of the actor. */
	struct FActorState
	{
		TArray<const UActorComponent*> Components;
		TArray<int32> Flags;
		bool bBegun = false;
	};

	struct FWorldState
	{
		TArray<FActorState> Actors; // Boss1, Boss2, Player
		int32 Bound = -1;
		int32 Ready = -1;
	};

	FActorState CaptureActor(const AActor* Actor)
	{
		FActorState State;
		State.bBegun = Actor->HasActorBegunPlay();
		for (const UActorComponent* Component : Actor->GetComponents())
		{
			State.Components.Add(Component);
		}
		State.Components.Sort([](const UActorComponent* A, const UActorComponent* B) { return A < B; });
		for (const UActorComponent* Component : State.Components)
		{
			State.Flags.Add(Component->IsRegistered() ? 1 : 0);
			State.Flags.Add(Component->HasBegunPlay() ? 1 : 0);
		}
		return State;
	}

	bool SameActor(const FActorState& A, const FActorState& B)
	{
		return A.bBegun == B.bBegun && A.Components == B.Components && A.Flags == B.Flags;
	}

	bool SameWorld(const FWorldState& A, const FWorldState& B)
	{
		if (A.Actors.Num() != B.Actors.Num() || A.Bound != B.Bound || A.Ready != B.Ready)
		{
			return false;
		}
		for (int32 Index = 0; Index < A.Actors.Num(); ++Index)
		{
			if (!SameActor(A.Actors[Index], B.Actors[Index]))
			{
				return false;
			}
		}
		return true;
	}

	/** One world, two boss-core actors and a target actor each holding one unrelated unregistered component, the content lease, three configs (the bosses differ in phase id, stats and stagger seconds) and the valid input. */
	struct FFixture
	{
		FPreparationWorld Scope;
		AActor* Boss1 = nullptr;
		AActor* Boss2 = nullptr;
		AActor* Player = nullptr;
		FEpochPtr Content;
		FConfigPtr Config1, Config2, PlayerConfig;
		FGuid Encounter;
		FRPGHydrationPreflightInput Input;
		bool bOk = false;

		FFixture()
		{
			if (!Scope.World)
			{
				return;
			}
			Boss1 = Scope.SpawnActor();
			Boss2 = Scope.SpawnActor();
			Player = Scope.SpawnActor();
			Content = RPGCombatRegistry::Legacy();
			if (!Boss1 || !Boss2 || !Player || !Content.IsValid())
			{
				return;
			}
			// An unrelated, preexisting, unregistered component on every actor: preparation and abort must leave it alone.
			for (AActor* Actor : {Boss1, Boss2, Player})
			{
				if (!NewObject<USceneComponent>(Actor, TEXT("UnrelatedMarker")))
				{
					return;
				}
			}
			Config1 = BuildConfig(Content, TEXT("PrepBossOne"), PhaseTwo, 0.35f, 3500.f, 73.5f, 3.25f);
			Config2 = BuildConfig(Content, TEXT("PrepBossTwo"), PhaseAlt, 0.5f, 4100.f, 88.f, 4.5f);
			PlayerConfig = BuildConfig(Content, TEXT("PrepPlayer"), PhaseTwo, 0.35f, 100.f, 10.f, 2.5f);
			Encounter = FGuid::NewGuid();
			Input.ExpectedWorld = Scope.World;
			Input.EncounterInstance = Encounter;
			Input.ExpectedContent = Content;
			Input.Requests.Add(MakeRequest(Boss1, TEXT("Boss1"), TEXT("Player"), ERPGPreflightRole::BossCore, Config1, PhaseTwo));
			Input.Requests.Add(MakeRequest(Boss2, TEXT("Boss2"), TEXT("Player"), ERPGPreflightRole::BossCore, Config2, PhaseAlt));
			Input.Requests.Add(MakeRequest(Player, TEXT("Player"), TEXT("Boss1"), ERPGPreflightRole::TargetOnly, PlayerConfig));
			bOk = Config1.IsValid() && Config2.IsValid() && PlayerConfig.IsValid();
		}

		FWorldState Capture() const
		{
			FWorldState State;
			for (const AActor* Actor : {Boss1, Boss2, Player})
			{
				State.Actors.Add(CaptureActor(Actor));
			}
			if (const URPGCombatContextSubsystem* Context = Scope.World->GetSubsystem<URPGCombatContextSubsystem>())
			{
				State.Bound = Context->GetBoundCount();
				State.Ready = Context->GetReadyCount();
			}
			return State;
		}
	};

	bool PreconditionOk(FAutomationTestBase& Test, const FFixture& F)
	{
		if (!F.bOk)
		{
			Test.AddError(TEXT("unsupported precondition: the fixture (world, three actors with an unrelated component each, the content lease, three configs) could not be built"));
		}
		return F.bOk;
	}

	struct FExpectedComponent
	{
		UClass* Class;
		const TCHAR* Name;
	};

	/** The five accepted native consumers with the reviewed instance names, written out independently of the preflight. */
	TArray<FExpectedComponent> ExpectedComponents()
	{
		return TArray<FExpectedComponent>{{URPGBossStagger::StaticClass(), TEXT("RPGBossStagger")}, {URPGBossPhases::StaticClass(), TEXT("RPGBossPhases")}, {URPGBossEncounter::StaticClass(), TEXT("RPGBossEncounter")},
			{URPGBossDormantWake::StaticClass(), TEXT("RPGBossDormantWake")}, {URPGBossPosture::StaticClass(), TEXT("RPGBossPosture")}};
	}

	bool NoManagedConsumer(const AActor* Actor)
	{
		for (UClass* Class : RPGBossHydrationPreflight::ManagedCoreConsumerClasses())
		{
			if (Actor->FindComponentByClass(Class))
			{
				return false;
			}
		}
		return true;
	}

	bool AnyErrorStartsWith(const TArray<FString>& Errors, const TCHAR* Token)
	{
		return Errors.ContainsByPredicate([Token](const FString& E) { return E.StartsWith(Token); });
	}

	bool AnyErrorContains(const TArray<FString>& Errors, const TCHAR* Text)
	{
		return Errors.ContainsByPredicate([Text](const FString& E) { return E.Contains(Text); });
	}

	/** One single error that carries BOTH the token at its start and the slot text. */
	bool AnyErrorHas(const TArray<FString>& Errors, const TCHAR* Token, const TCHAR* SlotText)
	{
		return Errors.ContainsByPredicate([Token, SlotText](const FString& E) { return E.StartsWith(Token) && E.Contains(SlotText); });
	}

	/** The exact success shape: ten owned real components (five per boss-core actor, classes, names, owners, configured representative fields), unregistered, never begun, never ticking, nothing for the target, no participant,
	 *  no bound or ready context, the unrelated components untouched, the artifact's read-only summary and the retained plan identities. */
	bool ExpectPrepared(FAutomationTestBase& Test, const FFixture& F, const FRPGPreparedBatch& Batch, const FWorldState& Before)
	{
		bool bOk = true;
		bOk &= Test.TestTrue(TEXT("the artifact reports prepared"), Batch.IsPrepared());
		bOk &= Test.TestEqual(TEXT("ten components are leased"), Batch.GetOwnedComponentCount(), 10);
		const TArray<const UActorComponent*> OwnedList = Batch.OwnedComponentsForTest();
		const TSet<const UActorComponent*> OwnedSet(OwnedList);
		bOk &= Test.TestTrue(TEXT("ten distinct owned component pointers"), OwnedList.Num() == 10 && OwnedSet.Num() == 10);

		struct FBossCase
		{
			AActor* Actor;
			int32 Index;
			float StaggerSeconds, PhaseThreshold, Health, Posture;
		};
		const FBossCase Bosses[] = {{F.Boss1, 0, 3.25f, 0.35f, 3500.f, 73.5f}, {F.Boss2, 1, 4.5f, 0.5f, 4100.f, 88.f}};
		const TArray<FExpectedComponent> Expected = ExpectedComponents();
		for (const FBossCase& Case : Bosses)
		{
			const FString Label = Case.Actor->GetName();
			for (const FExpectedComponent& Wanted : Expected)
			{
				UActorComponent* Component = Case.Actor->FindComponentByClass(Wanted.Class);
				if (!Test.TestNotNull(FString::Printf(TEXT("%s has a %s"), *Label, *Wanted.Class->GetName()), Component))
				{
					bOk = false;
					continue;
				}
				bOk &= Test.TestTrue(FString::Printf(TEXT("%s: %s has the exact class, the reviewed name and the actor as owner and outer"), *Label, Wanted.Name),
					Component->GetClass() == Wanted.Class && Component->GetFName() == FName(Wanted.Name) && Component->GetOwner() == Case.Actor && Component->GetOuter() == Case.Actor);
				bOk &= Test.TestTrue(FString::Printf(TEXT("%s: %s is unregistered, not begun, not initialized and its tick function is not registered"), *Label, Wanted.Name),
					!Component->IsRegistered() && !Component->HasBegunPlay() && !Component->HasBeenInitialized() && !Component->PrimaryComponentTick.IsTickFunctionRegistered());
				bOk &= Test.TestTrue(FString::Printf(TEXT("%s: %s is one of the artifact's owned components"), *Label, Wanted.Name), OwnedSet.Contains(Component));
			}
			const FActorState Now = CaptureActor(Case.Actor);
			const FActorState& Prior = Before.Actors[Case.Index];
			bool bPriorKept = Now.Components.Num() == Prior.Components.Num() + 5 && !Now.bBegun;
			for (const UActorComponent* PriorComponent : Prior.Components)
			{
				bPriorKept = bPriorKept && Now.Components.Contains(PriorComponent) && !OwnedSet.Contains(PriorComponent);
			}
			bOk &= Test.TestTrue(FString::Printf(TEXT("%s: exactly five components were added and every unrelated component is still there"), *Label), bPriorKept);
			bOk &= Test.TestFalse(FString::Printf(TEXT("%s has no participant component"), *Label), Case.Actor->FindComponentByClass<URPGCombatParticipant>() != nullptr);

			// Representative configured fields: the typed records of this member's own config, never the other boss's.
			const URPGBossStagger* Stagger = Case.Actor->FindComponentByClass<URPGBossStagger>();
			const URPGBossPhases* Phases = Case.Actor->FindComponentByClass<URPGBossPhases>();
			const URPGBossEncounter* Encounter = Case.Actor->FindComponentByClass<URPGBossEncounter>();
			const URPGBossPosture* Posture = Case.Actor->FindComponentByClass<URPGBossPosture>();
			bOk &= Test.TestTrue(FString::Printf(TEXT("%s: stagger seconds, the selected phase threshold, boss health and posture maximum are this member's configured values"), *Label),
				Stagger && Phases && Encounter && Posture && Stagger->StaggerSeconds == Case.StaggerSeconds && Phases->PhaseTwoHealthFraction == Case.PhaseThreshold
				&& Encounter->BossMaxHealth == Case.Health && Posture->PostureMax == Case.Posture);
		}
		bOk &= Test.TestTrue(TEXT("the target actor is exactly as before: no consumer, no participant, no component added"), SameActor(CaptureActor(F.Player), Before.Actors[2]) && NoManagedConsumer(F.Player));
		const FWorldState Now = F.Capture();
		bOk &= Test.TestTrue(TEXT("the combat context has no bound or ready participant change"), Now.Bound == Before.Bound && Now.Ready == Before.Ready);

		const TArray<FRPGPreparedParticipantInfo> Infos = Batch.GetParticipants();
		if (Test.TestEqual(TEXT("three participant summaries in the request order"), Infos.Num(), 3))
		{
			bOk &= Test.TestTrue(TEXT("summary: slots, targets, roles, explicit phase ids and owned counts"),
				Infos[0].Slot == FName(TEXT("Boss1")) && Infos[0].TargetSlot == FName(TEXT("Player")) && Infos[0].Role == ERPGPreflightRole::BossCore && Infos[0].SelectedPhaseId == PhaseTwo && Infos[0].OwnedComponentCount == 5
				&& Infos[1].Slot == FName(TEXT("Boss2")) && Infos[1].TargetSlot == FName(TEXT("Player")) && Infos[1].Role == ERPGPreflightRole::BossCore && Infos[1].SelectedPhaseId == PhaseAlt && Infos[1].OwnedComponentCount == 5
				&& Infos[2].Slot == FName(TEXT("Player")) && Infos[2].TargetSlot == FName(TEXT("Boss1")) && Infos[2].Role == ERPGPreflightRole::TargetOnly && Infos[2].SelectedPhaseId.IsNone() && Infos[2].OwnedComponentCount == 0);
		}
		const TSharedPtr<const FRPGHydrationPreflightPlan> Plan = Batch.GetPreflightPlan();
		if (Test.TestTrue(TEXT("the validated preflight plan is retained"), Plan.IsValid() && Plan->Participants.Num() == 3))
		{
			bOk &= Test.TestTrue(TEXT("the plan keeps the world, the encounter, the very content lease and the very config leases"), Plan->World.Get() == F.Scope.World && Plan->EncounterInstance == F.Encounter && Batch.GetEncounterInstance() == F.Encounter
				&& Plan->Content.Get() == F.Content.Get() && Plan->Participants[0].Config.Get() == F.Config1.Get() && Plan->Participants[1].Config.Get() == F.Config2.Get() && Plan->Participants[2].Config.Get() == F.PlayerConfig.Get());
			bOk &= Test.TestTrue(TEXT("the plan is still an incomplete subset: not a complete playable bundle, not a reservation, not ready"), !Plan->IsCompletePlayableBundle() && !Plan->IsReservation() && !Plan->IsReady());
		}
		return bOk;
	}

	/** Weak identities of every owned component, to prove they were destroyed. */
	TArray<TWeakObjectPtr<UActorComponent>> WeakOwned(const FRPGPreparedBatch& Batch)
	{
		TArray<TWeakObjectPtr<UActorComponent>> Weak;
		for (const UActorComponent* Component : Batch.OwnedComponentsForTest())
		{
			Weak.Add(const_cast<UActorComponent*>(Component));
		}
		return Weak;
	}

	/** Every earlier owned component is destroyed: no longer valid, and (the garbage object may still exist until collection) unregistered, not begun and flagged as destroyed. */
	bool ExpectAllDestroyed(FAutomationTestBase& Test, const TArray<TWeakObjectPtr<UActorComponent>>& Weak, const TCHAR* Label)
	{
		bool bGone = true;
		bool bCleanState = true;
		for (const TWeakObjectPtr<UActorComponent>& Pointer : Weak)
		{
			bGone = bGone && !Pointer.IsValid();
			if (const UActorComponent* Garbage = Pointer.Get(/*bEvenIfPendingKill=*/true))
			{
				bCleanState = bCleanState && !Garbage->IsRegistered() && !Garbage->HasBegunPlay() && Garbage->IsBeingDestroyed();
			}
		}
		bool bOk = Test.TestTrue(FString::Printf(TEXT("%s: every owned component is destroyed (none resolves any more)"), Label), Weak.Num() == 10 && bGone);
		bOk &= Test.TestTrue(FString::Printf(TEXT("%s: any destroyed object still awaiting collection is unregistered, not begun and marked destroyed"), Label), bCleanState);
		return bOk;
	}
}
}

using namespace PreparationTests;

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPreparationSuccessTest, "OneBossFight.Binding.Preparation.Success",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPreparationSuccessTest::RunTest(const FString& Parameters)
{
	FFixture F;
	if (!PreconditionOk(*this, F))
	{
		return false;
	}
	const FWorldState Before = F.Capture();
	FRPGPreparationResult Result = RPGBossHydrationPreparation::PrepareBatch(F.Input);
	if (!TestTrue(FString::Printf(TEXT("the batch is prepared (errors: %s)"), *FString::Join(Result.Errors, TEXT(" | "))), Result.Succeeded() && Result.Errors.IsEmpty()))
	{
		return false;
	}
	ExpectPrepared(*this, F, *Result.Batch, Before);

	// A second look: the world state is exactly the state before plus the ten components and nothing else; the abort returns every actor to its prior state.
	const FRPGPreparationAbortReport Report = Result.Batch->Abort();
	TestTrue(TEXT("the abort destroyed ten components and found nothing else"), Report.Destroyed == 10 && Report.AlreadyGone == 0 && Report.ContractViolations == 0 && Report.IsClean());
	TestTrue(TEXT("after the abort every actor is exactly as before"), SameWorld(F.Capture(), Before));
	AddInfo(TEXT("The prepared subset is five owned, unregistered, never begun components per boss-core actor; nothing registers, binds, reserves or activates them, and it is not a complete playable boss."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPreparationAbortTest, "OneBossFight.Binding.Preparation.Abort",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPreparationAbortTest::RunTest(const FString& Parameters)
{
	FFixture F;
	if (!PreconditionOk(*this, F))
	{
		return false;
	}
	const FWorldState Before = F.Capture();

	// Explicit abort, then a repeat.
	{
		FRPGPreparationResult Result = RPGBossHydrationPreparation::PrepareBatch(F.Input);
		if (!TestTrue(TEXT("first preparation succeeds"), Result.Succeeded()))
		{
			return false;
		}
		const TArray<TWeakObjectPtr<UActorComponent>> Weak = WeakOwned(*Result.Batch);
		const FRPGPreparationAbortReport First = Result.Batch->Abort();
		TestTrue(TEXT("explicit abort: ten destroyed, none already gone, no violation, clean"), First.Destroyed == 10 && First.AlreadyGone == 0 && First.ContractViolations == 0 && First.IsClean() && !First.bRefused);
		TestFalse(TEXT("the artifact is no longer prepared"), Result.Batch->IsPrepared());
		TestEqual(TEXT("every lease is released"), Result.Batch->GetOwnedComponentCount(), 0);
		TestTrue(TEXT("the summary reports no owned component"), Result.Batch->GetParticipants().Num() == 3 && Result.Batch->GetParticipants()[0].OwnedComponentCount == 0);
		TestTrue(TEXT("every actor is exactly as before: the unrelated components and the public state restored"), SameWorld(F.Capture(), Before));
		ExpectAllDestroyed(*this, Weak, TEXT("explicit abort"));
		const FRPGPreparationAbortReport Second = Result.Batch->Abort();
		TestTrue(TEXT("a repeated abort is harmless: nothing destroyed, nothing reported"), Second.Destroyed == 0 && Second.AlreadyGone == 0 && Second.ContractViolations == 0 && Second.IsClean());
		TestTrue(TEXT("the repeated abort changed nothing"), SameWorld(F.Capture(), Before));
	}
	// Scope-exit abort: the artifact goes out of scope without an explicit Abort.
	TArray<TWeakObjectPtr<UActorComponent>> ScopeWeak;
	{
		FRPGPreparationResult Result = RPGBossHydrationPreparation::PrepareBatch(F.Input);
		if (!TestTrue(TEXT("preparation succeeds again after the first artifact was aborted"), Result.Succeeded()))
		{
			return false;
		}
		TestTrue(TEXT("the second generation is a full, correct preparation too"), ExpectPrepared(*this, F, *Result.Batch, Before));
		ScopeWeak = WeakOwned(*Result.Batch);
	}
	TestTrue(TEXT("scope exit restored every actor to its prior state"), SameWorld(F.Capture(), Before));
	ExpectAllDestroyed(*this, ScopeWeak, TEXT("scope-exit abort"));
	ScopeWeak.Reset();

	// Release the result: a destroyed, never-moved result owns nothing and nothing in the world moved.
	{
		FRPGPreparationResult Result = RPGBossHydrationPreparation::PrepareBatch(F.Input);
		TestTrue(TEXT("and a third preparation succeeds, the aborted ones left no residue"), Result.Succeeded() && ExpectPrepared(*this, F, *Result.Batch, Before));
		Result.Batch->Abort();
	}
	TestTrue(TEXT("final state is the state before"), SameWorld(F.Capture(), Before));
	AddInfo(TEXT("Names are reused across generations: the engine replaces a same-name garbage object in place when the name is created again before collection, so no reference to a destroyed generation is kept or used."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPreparationExclusiveTest, "OneBossFight.Binding.Preparation.Exclusive",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPreparationExclusiveTest::RunTest(const FString& Parameters)
{
	FFixture F;
	if (!PreconditionOk(*this, F))
	{
		return false;
	}
	const FWorldState Before = F.Capture();
	FRPGPreparationResult First = RPGBossHydrationPreparation::PrepareBatch(F.Input);
	if (!TestTrue(TEXT("first preparation succeeds"), First.Succeeded()))
	{
		return false;
	}
	const TArray<const UActorComponent*> Snapshot = First.Batch->OwnedComponentsForTest();
	const FWorldState AfterFirst = F.Capture();

	// A second preparation over the same actors is refused by the preflight (a preexisting consumer) and touches nothing of the first.
	FRPGPreparationResult Second = RPGBossHydrationPreparation::PrepareBatch(F.Input);
	TestFalse(TEXT("the second preparation fails"), Second.Succeeded());
	TestFalse(TEXT("and returns no artifact"), Second.Batch.IsValid());
	TestTrue(TEXT("named by the preflight for both boss-core members"), AnyErrorHas(Second.Errors, TEXT("Preflight.PreexistingConsumer"), TEXT("slot=Boss1")) && AnyErrorHas(Second.Errors, TEXT("Preflight.PreexistingConsumer"), TEXT("slot=Boss2")));
	TestTrue(TEXT("the first artifact is intact: prepared, the same ten components, still unregistered and not begun"), First.Batch->IsPrepared() && First.Batch->GetOwnedComponentCount() == 10 && First.Batch->OwnedComponentsForTest() == Snapshot);
	TestTrue(TEXT("no actor, component or context state changed by the refused attempt"), SameWorld(F.Capture(), AfterFirst));
	TestTrue(TEXT("the first artifact still has the exact success shape"), ExpectPrepared(*this, F, *First.Batch, Before));

	// Only after the first has aborted does a preparation succeed again.
	const FRPGPreparationAbortReport Report = First.Batch->Abort();
	TestTrue(TEXT("the first artifact aborts cleanly"), Report.Destroyed == 10 && Report.IsClean());
	FRPGPreparationResult Third = RPGBossHydrationPreparation::PrepareBatch(F.Input);
	TestTrue(TEXT("a preparation succeeds again after the abort"), Third.Succeeded());
	if (Third.Batch.IsValid())
	{
		Third.Batch->Abort();
	}
	TestTrue(TEXT("final state is the state before"), SameWorld(F.Capture(), Before));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPreparationRejectionTest, "OneBossFight.Binding.Preparation.WholeBatchRejection",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPreparationRejectionTest::RunTest(const FString& Parameters)
{
	FFixture F;
	if (!PreconditionOk(*this, F))
	{
		return false;
	}
	const FWorldState Before = F.Capture();

	// An invalid LAST member: nothing is allocated for the valid members before it.
	{
		FRPGHydrationPreflightInput Input = F.Input;
		Input.Requests[2].Config.Reset();
		const FRPGPreparationResult Result = RPGBossHydrationPreparation::PrepareBatch(Input);
		TestFalse(TEXT("a target-only member without a config: refused"), Result.Succeeded());
		TestFalse(TEXT("no artifact"), Result.Batch.IsValid());
		TestTrue(TEXT("named by the preflight with the slot of the invalid member only"), AnyErrorHas(Result.Errors, TEXT("Preflight.NoConfig"), TEXT("slot=Player")) && !AnyErrorContains(Result.Errors, TEXT("slot=Boss1")));
		TestTrue(TEXT("no component was created for the valid boss-core members before it"), SameWorld(F.Capture(), Before) && NoManagedConsumer(F.Boss1) && NoManagedConsumer(F.Boss2));
	}
	// An invalid LATE boss-core member (an explicit phase id the config does not hold).
	{
		FRPGHydrationPreflightInput Input = F.Input;
		Input.Requests[1].SelectedPhaseId = PhaseTwo;
		const FRPGPreparationResult Result = RPGBossHydrationPreparation::PrepareBatch(Input);
		TestFalse(TEXT("a late boss-core member with a wrong phase id: refused"), Result.Succeeded());
		TestTrue(TEXT("named by the preflight for that member only"), AnyErrorHas(Result.Errors, TEXT("Preflight.PhaseRejected"), TEXT("slot=Boss2")) && !AnyErrorContains(Result.Errors, TEXT("slot=Boss1")));
		TestTrue(TEXT("nothing was allocated for the valid first boss either"), SameWorld(F.Capture(), Before) && NoManagedConsumer(F.Boss1) && NoManagedConsumer(F.Boss2));
	}
	// The batch-level expectations.
	{
		FRPGHydrationPreflightInput Input = F.Input;
		Input.EncounterInstance.Invalidate();
		const FRPGPreparationResult Result = RPGBossHydrationPreparation::PrepareBatch(Input);
		TestTrue(TEXT("an invalid encounter identity: refused by the preflight, nothing created"), !Result.Succeeded() && AnyErrorStartsWith(Result.Errors, TEXT("Preflight.InvalidEncounter")) && SameWorld(F.Capture(), Before));
	}
	// The control: the unmodified input prepares, so the three refusals were about their changes.
	{
		FRPGPreparationResult Result = RPGBossHydrationPreparation::PrepareBatch(F.Input);
		TestTrue(TEXT("control: the unmodified input prepares"), Result.Succeeded());
		if (Result.Batch.IsValid())
		{
			Result.Batch->Abort();
		}
	}
	TestTrue(TEXT("final state is the state before"), SameWorld(F.Capture(), Before));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPreparationFaultTest, "OneBossFight.Binding.Preparation.InjectedFaults",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPreparationFaultTest::RunTest(const FString& Parameters)
{
	FFixture F;
	if (!PreconditionOk(*this, F))
	{
		return false;
	}
	const FWorldState Before = F.Capture();

	// The steps are counted from 1: allocations 1 to 5 are the first boss, 6 to 10 the second boss, configures 11 to 15 the first boss, 16 to 20 the second boss. The failure is injected right AFTER the step: a real
	// allocation or a real configure had completed.
	const int32 Ordinals[] = {1, 3, 5, 6, 8, 10, 11, 13, 15, 16, 18, 20};
	for (const int32 Ordinal : Ordinals)
	{
		const FString Label = FString::Printf(TEXT("fault after step %d"), Ordinal);
		{
			RPGBossHydrationPreparation::FFaultInjectionScope Fault(Ordinal);
			const FRPGPreparationResult Result = RPGBossHydrationPreparation::PrepareBatch(F.Input);
			TestTrue(FString::Printf(TEXT("%s: the injected failure fired"), *Label), Fault.Fired());
			TestFalse(FString::Printf(TEXT("%s: the preparation failed"), *Label), Result.Succeeded());
			TestFalse(FString::Printf(TEXT("%s: no artifact survives"), *Label), Result.Batch.IsValid());
			TestTrue(FString::Printf(TEXT("%s: named as an injected fault, not an organic failure (got: %s)"), *Label, *FString::Join(Result.Errors, TEXT(" | "))), AnyErrorStartsWith(Result.Errors, TEXT("Preparation.InjectedFault")) && Result.Errors.Num() == 1);
			TestTrue(FString::Printf(TEXT("%s: every component created for every member is destroyed, the unrelated components are retained, the context is untouched"), *Label), SameWorld(F.Capture(), Before));
			TestTrue(FString::Printf(TEXT("%s: no managed consumer survives on any actor"), *Label), NoManagedConsumer(F.Boss1) && NoManagedConsumer(F.Boss2) && NoManagedConsumer(F.Player));
		}
		// The very same actors prepare cleanly afterwards.
		FRPGPreparationResult Again = RPGBossHydrationPreparation::PrepareBatch(F.Input);
		TestTrue(FString::Printf(TEXT("%s: the same actors prepare again afterwards"), *Label), Again.Succeeded());
		if (Again.Batch.IsValid())
		{
			Again.Batch->Abort();
		}
		TestTrue(FString::Printf(TEXT("%s: and abort back to the prior state"), *Label), SameWorld(F.Capture(), Before));
	}
	// The control: an ordinal beyond the twenty real steps never fires and the preparation succeeds.
	{
		RPGBossHydrationPreparation::FFaultInjectionScope Fault(21);
		FRPGPreparationResult Result = RPGBossHydrationPreparation::PrepareBatch(F.Input);
		TestTrue(TEXT("control: an ordinal past the last step does not fire and the preparation succeeds"), !Fault.Fired() && Result.Succeeded());
		if (Result.Batch.IsValid())
		{
			Result.Batch->Abort();
		}
	}
	TestTrue(TEXT("final state is the state before"), SameWorld(F.Capture(), Before));
	AddInfo(TEXT("The failures here are INJECTED by a dev-automation-only step ordinal inside the new preparation source after a real allocation or configure; none is an organically reproduced native failure (the accepted callbacks cannot fail for a batch the preflight accepted)."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPreparationLifetimeTest, "OneBossFight.Binding.Preparation.Lifetime",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPreparationLifetimeTest::RunTest(const FString& Parameters)
{
	// 1. An owned component destroyed by somebody else before the abort: counted once as already gone, the rest destroyed, nothing destroyed twice.
	{
		FFixture F;
		if (!PreconditionOk(*this, F))
		{
			return false;
		}
		const FWorldState Before = F.Capture();
		FRPGPreparationResult Result = RPGBossHydrationPreparation::PrepareBatch(F.Input);
		if (!TestTrue(TEXT("preparation succeeds"), Result.Succeeded()))
		{
			return false;
		}
		UActorComponent* Posture = F.Boss2->FindComponentByClass<URPGBossPosture>();
		if (TestNotNull(TEXT("the second boss's posture component exists"), Posture))
		{
			Posture->DestroyComponent();
		}
		const FRPGPreparationAbortReport Report = Result.Batch->Abort();
		TestTrue(TEXT("component destroyed first: nine destroyed by the abort, one already gone, no violation, clean"), Report.Destroyed == 9 && Report.AlreadyGone == 1 && Report.ContractViolations == 0 && Report.IsClean());
		TestTrue(TEXT("every actor is back to its prior state"), SameWorld(F.Capture(), Before));
	}
	// 2. An owner actor destroyed before the abort: its components are released without being dereferenced as live objects; the other member is cleaned.
	{
		FFixture F;
		if (!PreconditionOk(*this, F))
		{
			return false;
		}
		const FActorState Boss1Before = CaptureActor(F.Boss1);
		const FActorState PlayerBefore = CaptureActor(F.Player);
		FRPGPreparationResult Result = RPGBossHydrationPreparation::PrepareBatch(F.Input);
		if (!TestTrue(TEXT("preparation succeeds"), Result.Succeeded()))
		{
			return false;
		}
		F.Boss2->Destroy();
		const FRPGPreparationAbortReport Report = Result.Batch->Abort();
		TestTrue(TEXT("owner destroyed first: the first boss's five are destroyed, the destroyed owner's five are already gone, no violation"), Report.Destroyed == 5 && Report.AlreadyGone == 5 && Report.ContractViolations == 0 && Report.IsClean());
		TestTrue(TEXT("the surviving actors are exactly as before"), SameActor(CaptureActor(F.Boss1), Boss1Before) && SameActor(CaptureActor(F.Player), PlayerBefore));
	}
	// 3. The whole world torn down before the abort (DestroyWorld does not itself mark the actors or components as garbage, so the abort may find them still valid): no crash and every owned component is accounted for,
	//    whichever of the two branches (destroyed, or already gone) the engine's teardown leaves; the observed split is logged.
	{
		TUniquePtr<FFixture> F(new FFixture());
		if (!PreconditionOk(*this, *F))
		{
			return false;
		}
		FRPGPreparationResult Result = RPGBossHydrationPreparation::PrepareBatch(F->Input);
		if (!TestTrue(TEXT("preparation succeeds"), Result.Succeeded()))
		{
			return false;
		}
		F.Reset(); // the world, its actors and the fixture are gone; the artifact still holds its leases
		const FRPGPreparationAbortReport Report = Result.Batch->Abort();
		TestTrue(TEXT("world torn down first: every owned component is accounted for and nothing is reported as a registration violation"), Report.Destroyed + Report.AlreadyGone == 10 && Report.ContractViolations == 0 && Report.IsClean());
		AddInfo(FString::Printf(TEXT("world torn down first: the abort destroyed %d and found %d already gone"), Report.Destroyed, Report.AlreadyGone));
		TestFalse(TEXT("the artifact is no longer prepared"), Result.Batch->IsPrepared());
	}
	// 4. A component registered by somebody else: not rolled back, not destroyed, reported.
	{
		FFixture F;
		if (!PreconditionOk(*this, F))
		{
			return false;
		}
		const FWorldState Before = F.Capture();
		FRPGPreparationResult Result = RPGBossHydrationPreparation::PrepareBatch(F.Input);
		if (!TestTrue(TEXT("preparation succeeds"), Result.Succeeded()))
		{
			return false;
		}
		UActorComponent* Encounter = F.Boss1->FindComponentByClass<URPGBossEncounter>();
		if (!TestNotNull(TEXT("the first boss's encounter component exists"), Encounter))
		{
			return false;
		}
		Encounter->RegisterComponent();
		if (!TestTrue(TEXT("precondition: the component is now registered by the caller"), Encounter->IsRegistered()))
		{
			AddError(TEXT("unsupported precondition: the component could not be registered by the test"));
			Encounter->DestroyComponent();
			Result.Batch->Abort();
			return false;
		}
		const FRPGPreparationAbortReport Report = Result.Batch->Abort();
		TestTrue(TEXT("registered by somebody else: nine destroyed, one contract violation, not clean"), Report.Destroyed == 9 && Report.ContractViolations == 1 && !Report.IsClean() && AnyErrorStartsWith(Report.Errors, TEXT("Preparation.ContractViolation")) && AnyErrorContains(Report.Errors, TEXT("RPGBossEncounter")));
		TestTrue(TEXT("the registered component was left in place and is still registered (no rollback was pretended)"), IsValid(Encounter) && Encounter->IsRegistered() && Encounter->GetOwner() == F.Boss1);
		Encounter->DestroyComponent(); // the test, which registered it, undoes it
		TestTrue(TEXT("after the test removed its own registered component every actor is back to its prior state"), SameWorld(F.Capture(), Before));
		TestEqual(TEXT("the artifact owns nothing any more"), Result.Batch->GetOwnedComponentCount(), 0);
	}
	// 5. The off-thread refusals: neither a preparation nor an abort touches a UObject on a worker thread.
	{
		FFixture F;
		if (!PreconditionOk(*this, F))
		{
			return false;
		}
		const FWorldState Before = F.Capture();
		TFuture<TArray<FString>> PrepareFuture = Async(EAsyncExecution::ThreadPool, []()
		{
			const FRPGPreparationResult Result = RPGBossHydrationPreparation::PrepareBatch(FRPGHydrationPreflightInput());
			return Result.Errors;
		});
		const TArray<FString> PrepareErrors = PrepareFuture.Get();
		TestTrue(TEXT("a preparation on a worker thread is refused by name, before anything else"), PrepareErrors.Num() == 1 && PrepareErrors[0].StartsWith(TEXT("Preparation.NotGameThread")));

		FRPGPreparationResult Result = RPGBossHydrationPreparation::PrepareBatch(F.Input);
		if (!TestTrue(TEXT("preparation on the game thread succeeds"), Result.Succeeded()))
		{
			return false;
		}
		FRPGPreparedBatch* Raw = Result.Batch.Get();
		TFuture<FRPGPreparationAbortReport> AbortFuture = Async(EAsyncExecution::ThreadPool, [Raw]() { return Raw->Abort(); });
		const FRPGPreparationAbortReport Refused = AbortFuture.Get();
		TestTrue(TEXT("an abort on a worker thread is refused by name and destroys nothing"), Refused.bRefused && Refused.Destroyed == 0 && AnyErrorStartsWith(Refused.Errors, TEXT("Preparation.NotGameThread")));
		TestTrue(TEXT("the artifact is still prepared with its ten components after the refused abort"), Result.Batch->IsPrepared() && Result.Batch->GetOwnedComponentCount() == 10);
		const FRPGPreparationAbortReport Report = Result.Batch->Abort();
		TestTrue(TEXT("the game-thread abort then succeeds"), Report.Destroyed == 10 && Report.IsClean());
		TestTrue(TEXT("final state is the state before"), SameWorld(F.Capture(), Before));
	}
	AddInfo(TEXT("Not exercised: destroying the artifact itself on a worker thread (it would be a flagged contract violation and cannot be exercised safely), and a component the engine collected during preparation (no collection is forced)."));
	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
