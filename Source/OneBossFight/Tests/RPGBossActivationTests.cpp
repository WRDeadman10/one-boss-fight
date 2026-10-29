// Copyright One Boss Fight. All Rights Reserved.

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

// DD28 staged tests: transient never-begun fixtures; synthetic config/epoch, no authored asset or gameplay proof.
namespace
{
namespace ActivationTests
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

	/** The manifest paths the twelve boss-core plans read for a selected phase id (the union of the twelve accepted factories). DD13 holds the independent literal list; this file does not test membership, it only needs a manifest the preflight accepts. */
	TArray<FString> RequiredPaths(FName PhaseId)
	{
		TArray<FRPGComponentPlan> Plans;
		Plans.Add(RPGBossStaggerClusterAdapters::MakeStaggerClusterPlan());
		Plans.Add(RPGBossPhasesClusterAdapters::MakePhasesClusterPlan(PhaseId));
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
		State.Components.Sort([](const UActorComponent& A, const UActorComponent& B) { return &A < &B; }); // a pointer array is sorted through dereferenced references
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

}
}
using namespace ActivationTests;

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGActivationSuccessTest, "OneBossFight.Binding.Activation.Success", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGActivationSuccessTest::RunTest(const FString& Parameters)
{
	FFixture F; if (!PreconditionOk(*this, F)) { return false; }
	const FWorldState Before = F.Capture();
	auto Result = RPGBossHydrationPreparation::PrepareBatch(F.Input);
	if (!TestTrue(TEXT("prepared"), Result.Succeeded())) { return false; }
	FRPGRegistrationReport Report;
	if (!TestTrue(TEXT("registration succeeded"), Result.Batch->RegisterOwnedComponents(Report))) { return false; }
	TestTrue(TEXT("state remains prepared and registered"), Result.Batch->IsPrepared() && Result.Batch->IsRegistered() && Report.bSucceeded && Report.Errors.IsEmpty());
	const TCHAR* Expected[] = {TEXT("RPGBossStagger"), TEXT("RPGBossPhases"), TEXT("RPGBossEncounter"), TEXT("RPGBossDormantWake"), TEXT("RPGBossPosture"), TEXT("RPGBossBleed"), TEXT("RPGBossLowSweep"), TEXT("RPGBossShockwave"), TEXT("RPGBossHealPunish"), TEXT("RPGBossLook"), TEXT("RPGBossCloseClipSwap"), TEXT("RPGBossDeath")};
	if (TestEqual(TEXT("two bosses times twelve"), Report.Registered.Num(), 24))
	{
		for (int32 Index = 0; Index < 24; ++Index)
		{
			const FRPGRegisteredComponentInfo& Entry = Report.Registered[Index];
			TestTrue(TEXT("actual registered order matches independent legacy-relative list"), Entry.MemberIndex == Index / 12 && Entry.PlanIndex == Index % 12 && Entry.ClassName == FName(Expected[Index % 12]));
		}
	}
	for (const UActorComponent* C : Result.Batch->OwnedComponentsForTest())
	{ TestTrue(TEXT("registered and never begun"), C && C->IsRegistered() && !C->HasBegunPlay()); }
	TestTrue(TEXT("target and context untouched"), SameActor(CaptureActor(F.Player), Before.Actors[2]) && F.Capture().Bound == Before.Bound && F.Capture().Ready == Before.Ready);
	const auto Cleanup = Result.Batch->Abort();
	TestTrue(TEXT("clean cleanup restores actors"), Cleanup.IsClean() && Cleanup.Destroyed == 24 && SameWorld(F.Capture(), Before));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGActivationThreadTest, "OneBossFight.Binding.Activation.NotGameThread", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGActivationThreadTest::RunTest(const FString& Parameters)
{
	FFixture F; if (!PreconditionOk(*this, F)) { return false; }
	auto Result = RPGBossHydrationPreparation::PrepareBatch(F.Input);
	if (!TestTrue(TEXT("prepared"), Result.Succeeded())) { return false; }
	const FWorldState Before = F.Capture();
	FRPGRegistrationReport Report;
	const bool bAccepted = Async(EAsyncExecution::ThreadPool, [&]() { return Result.Batch->RegisterOwnedComponents(Report); }).Get();
	TestTrue(TEXT("named refusal and no UObject mutation"), !bAccepted && Report.Errors.Num() == 1 && Report.Errors[0].StartsWith(TEXT("Activation.NotGameThread")) && SameWorld(F.Capture(), Before) && Result.Batch->IsPrepared() && !Result.Batch->IsRegistered());
	Result.Batch->Abort();
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGActivationBegunTest, "OneBossFight.Binding.Activation.OwnerBegun", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGActivationBegunTest::RunTest(const FString& Parameters)
{
	FFixture F; if (!PreconditionOk(*this, F)) { return false; }
	auto Result = RPGBossHydrationPreparation::PrepareBatch(F.Input);
	if (!TestTrue(TEXT("prepared"), Result.Succeeded())) { return false; }
	// The components are still unregistered: actor BeginPlay cannot begin them.
	F.Boss2->DispatchBeginPlay();
	if (!TestTrue(TEXT("late boss actually begun"), F.Boss2->HasActorBegunPlay())) { return false; }
	FRPGRegistrationReport Report;
	TestFalse(TEXT("begun owner refused"), Result.Batch->RegisterOwnedComponents(Report));
	TestTrue(TEXT("whole-batch refusal before first registration"), Report.Registered.IsEmpty() && Report.FailedMemberIndex == 1 && Report.Errors.Num() > 0 && Report.Errors[0].StartsWith(TEXT("Activation.MemberInvalid")));
	TestTrue(TEXT("failure abort destroyed all twenty-four unregistered consumers"), Report.Cleanup.IsClean() && Report.Cleanup.Destroyed == 24 && !Result.Batch->IsPrepared());
	TestEqual(TEXT("all owned leases gone"), Result.Batch->GetOwnedComponentCount(), 0);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGActivationStateTest, "OneBossFight.Binding.Activation.StateRefusals", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGActivationStateTest::RunTest(const FString& Parameters)
{
	FFixture F; if (!PreconditionOk(*this, F)) { return false; }
	const FWorldState Before = F.Capture();
	auto Result = RPGBossHydrationPreparation::PrepareBatch(F.Input);
	if (!TestTrue(TEXT("prepared"), Result.Succeeded())) { return false; }
	FRPGRegistrationReport Report;
	if (!TestTrue(TEXT("first succeeds"), Result.Batch->RegisterOwnedComponents(Report))) { return false; }
	const FWorldState Registered = F.Capture();
	TestFalse(TEXT("second refused"), Result.Batch->RegisterOwnedComponents(Report));
	TestTrue(TEXT("existing registration preserved, stale report cleared"), Report.Registered.IsEmpty() && Report.Errors.Num() == 1 && Report.Errors[0].StartsWith(TEXT("Activation.AlreadyRegistered")) && Result.Batch->IsRegistered() && SameWorld(F.Capture(), Registered));
	Result.Batch->Abort();
	TestFalse(TEXT("aborted refused"), Result.Batch->RegisterOwnedComponents(Report));
	TestTrue(TEXT("named aborted refusal"), Report.Errors.Num() == 1 && Report.Errors[0].StartsWith(TEXT("Activation.NotPrepared")) && SameWorld(F.Capture(), Before));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGActivationFaultTest, "OneBossFight.Binding.Activation.InjectedFaults", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGActivationFaultTest::RunTest(const FString& Parameters)
{
	FFixture F; if (!PreconditionOk(*this, F)) { return false; }
	const FWorldState Before = F.Capture();
	for (int32 Ordinal = 1; Ordinal <= 24; ++Ordinal)
	{
		auto Result = RPGBossHydrationPreparation::PrepareBatch(F.Input);
		if (!TestTrue(TEXT("fresh preparation for ordinal"), Result.Succeeded())) { return false; }
		RPGBossActivation::FRegistrationFaultScope Fault(Ordinal);
		FRPGRegistrationReport Report;
		TestFalse(TEXT("injected registration failure"), Result.Batch->RegisterOwnedComponents(Report));
		TestTrue(TEXT("failure fired at exact member and plan"), Fault.Fired() && Report.FailedMemberIndex == (Ordinal - 1) / 12 && Report.FailedPlanIndex == (Ordinal - 1) % 12 && Report.Registered.Num() == Ordinal);
		TestTrue(TEXT("reverse unregister then clean full abort"), Report.Cleanup.Destroyed == 24 && Report.Cleanup.IsClean() && !Result.Batch->IsPrepared() && !Result.Batch->IsRegistered() && SameWorld(F.Capture(), Before));
		for (const AActor* Actor : {F.Boss1, F.Boss2, F.Player})
		{
			for (UClass* Class : RPGBossHydrationPreflight::ManagedCoreConsumerClasses())
			{ TestTrue(TEXT("no managed consumer left on any actor"), Actor->FindComponentByClass(Class) == nullptr); }
		}
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGActivationLifetimeTest, "OneBossFight.Binding.Activation.Lifetime", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGActivationLifetimeTest::RunTest(const FString& Parameters)
{
	FFixture F; if (!PreconditionOk(*this, F)) { return false; }
	const FWorldState Before = F.Capture();
	{
		auto Result = RPGBossHydrationPreparation::PrepareBatch(F.Input);
		if (!TestTrue(TEXT("prepared"), Result.Succeeded())) { return false; }
		FRPGRegistrationReport Report;
		if (!TestTrue(TEXT("registered"), Result.Batch->RegisterOwnedComponents(Report))) { return false; }
		const auto Abort = Result.Batch->Abort();
		TestTrue(TEXT("owned registration abort is clean"), Abort.Destroyed == 24 && Abort.ContractViolations == 0 && Abort.IsClean() && !Result.Batch->IsRegistered() && SameWorld(F.Capture(), Before));
		const auto Again = Result.Batch->Abort();
		TestTrue(TEXT("repeated abort empty"), Again.Destroyed == 0 && Again.AlreadyGone == 0 && Again.ContractViolations == 0 && Again.IsClean());
	}
	{
		auto Result = RPGBossHydrationPreparation::PrepareBatch(F.Input);
		if (!TestTrue(TEXT("prepared for scope exit"), Result.Succeeded())) { return false; }
		FRPGRegistrationReport Report;
		if (!TestTrue(TEXT("registered for scope exit"), Result.Batch->RegisterOwnedComponents(Report))) { return false; }
	}
	TestTrue(TEXT("existing destructor Abort now cleans its own registrations"), SameWorld(F.Capture(), Before));
	return true;
}

#endif
