// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Animation/AnimSequence.h"
#include "Animation/Skeleton.h"
#include "Components/SceneComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Actor.h"
#include "Player/RPGBossDormantWake.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossHydrationPreflight.h"
#include "Player/RPGBossPhases.h"
#include "Player/RPGBossPosture.h"
#include "Player/RPGBossStagger.h"
#include "UObject/Package.h"
#include "UObject/StrongObjectPtr.h"
#include <limits>

// These tests prove the whole-batch expanded native subset preflight kernel (five combined plans per boss-core member) on real isolated UE objects (a headless game world, plain actors, the existing synthetic config factory): validation of the whole batch, named failures,
// the plan order and leases of a success, clearing of earlier output, and that a failed or successful compile changes no actor, component or combat context.
// They do NOT prove a duel, PIE, a startup chronology, the real game-instance provenance of a content lease, a production skeleton/mesh pairing (no real pack mesh is used: a production member is only shown to FAIL CLOSED),
// or the not-game-thread rule (the tests run on the game thread) and the synthetic-fixture-unavailable rule of a non-test target (compiled out here).
// The production dependency predicate (compiled skeleton, every animation lease, every animation skeleton identity) is tested on its own with transient native skeletons and animations and nothing is loaded;
// that is NOT a positive production batch: no production-compatible character mesh is built, so a production member is only ever shown to fail closed.

namespace
{
namespace PreflightTests
{
	using FEpochPtr = TSharedPtr<const RPGCombatRegistry::FEpoch>;
	using FConfigPtr = TSharedPtr<const FRPGParticipantConfig>;
	using FPlanPtr = TSharedPtr<const FRPGHydrationPreflightPlan>;

	const FName PhaseTwo(TEXT("PhaseTwo"));

	/** Test-local game world with the set-up the earlier headless tests used; destroyed with the scope. */
	struct FPreflightWorld
	{
		UWorld* World = nullptr;

		FPreflightWorld()
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

		~FPreflightWorld()
		{
			if (World)
			{
				GEngine->DestroyWorldContext(World);
				World->DestroyWorld(/*bInformEngineOfWorld=*/false);
			}
		}

		FPreflightWorld(const FPreflightWorld&) = delete;
		FPreflightWorld& operator=(const FPreflightWorld&) = delete;

		AActor* SpawnActor() const { return World ? World->SpawnActor<AActor>() : nullptr; }
	};

	/** The 51 unique manifest paths the five combined boss-core plans read, written out as INDEPENDENT literals (not derived from the factories under test): stagger 25 (14 policy + 11 profile), phases 18 (the 4 paths of
	 *  the selected phase + 6 flow + 5 fireball + 3 dependencies), encounter 3, dormant wake 2, posture 3. Membership only; the fixtures' manifests are built from this list and the plans' own required fields are what the
	 *  implementation produces and is compared against it. */
	TArray<FString> AllRequiredPaths(FName PhaseId)
	{
		const FString Id = PhaseId.ToString();
		return TArray<FString>{
			// stagger policy (14)
			TEXT("StaggerPolicy.StaggerSeconds"), TEXT("StaggerPolicy.FreezeAtPosition"), TEXT("StaggerPolicy.CriticalMultiplier"), TEXT("StaggerPolicy.RiposteRange"), TEXT("StaggerPolicy.RiposteConeDegrees"),
			TEXT("StaggerPolicy.RiposteFacingDegrees"), TEXT("StaggerPolicy.RiposteArmSeconds"), TEXT("StaggerPolicy.RipostePlayerStartGap"), TEXT("StaggerPolicy.RiposteAlignSeconds"), TEXT("StaggerPolicy.RiposteImpactSeconds"),
			TEXT("StaggerPolicy.RiposteBaseDamage"), TEXT("StaggerPolicy.CooldownSeconds"), TEXT("StaggerPolicy.GetUpRate"), TEXT("StaggerPolicy.bHoldPostureAtZero"),
			// stagger profile (11)
			TEXT("StaggerProfile.bUseClips"), TEXT("StaggerProfile.bUseRiposteClips"), TEXT("StaggerProfile.bCriticalOnEveryHit"), TEXT("StaggerProfile.HitStunAbilityClassName"), TEXT("StaggerProfile.FallMontage"),
			TEXT("StaggerProfile.GetUpMontage"), TEXT("StaggerProfile.FallClip"), TEXT("StaggerProfile.DownClip"), TEXT("StaggerProfile.RipostePlayerClip"), TEXT("StaggerProfile.RiposteBossClip"), TEXT("StaggerProfile.ImmunityEffect"),
			// selected phase (4)
			FString::Printf(TEXT("Phases[%s].EntryHealthFraction"), *Id), FString::Printf(TEXT("Phases[%s].SpeedMultiplier"), *Id), FString::Printf(TEXT("Phases[%s].RateMultiplier"), *Id), FString::Printf(TEXT("Phases[%s].AttackMultiplier"), *Id),
			// phase flow (6)
			TEXT("PhaseFlow.TransitionSeconds"), TEXT("PhaseFlow.bUseRoarClip"), TEXT("PhaseFlow.bPausePostureInTransition"), TEXT("PhaseFlow.bLockLeapUntilPhaseTwo"), TEXT("PhaseFlow.AttackAbilityPrefix"), TEXT("PhaseFlow.LeapAbilityTag"),
			// fireball (5)
			TEXT("Fireball.bFireballEnabled"), TEXT("Fireball.FireballAbility"), TEXT("Fireball.FireballCooldown"), TEXT("Fireball.FireballMinRange"), TEXT("Fireball.FireballMaxRange"),
			// phase dependencies (3)
			TEXT("PhaseDependencies.RoarClip"), TEXT("PhaseDependencies.TransitionMontage"), TEXT("PhaseDependencies.ImmunityEffect"),
			// encounter (3), dormant wake (2), posture (3)
			TEXT("Stats.MaxHealth"), TEXT("EncounterPolicy.GateRadius"), TEXT("EncounterPolicy.bResetOnPlayerRespawn"),
			TEXT("DormantWake.DormantClip"), TEXT("DormantWake.WakeClip"),
			TEXT("Stats.MaxPosture"), TEXT("Stats.PostureRegenDelay"), TEXT("Stats.PostureRegenRate")};
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

	FRPGPhaseConfig MakePhase(FName Id, float Threshold, float Speed, float Rate, float Attack)
	{
		FRPGPhaseConfig Phase;
		Phase.PhaseId = Id;
		Phase.EntryHealthFraction = Threshold;
		Phase.SpeedMultiplier = Speed;
		Phase.RateMultiplier = Rate;
		Phase.AttackMultiplier = Attack;
		return Phase;
	}

	/** A hand-built config for the adversarial cases (the real factory refuses most of them). Non-default valid values unless a case changes them. */
	struct FConfigSpec
	{
		float Health = 3500.f, Posture = 73.5f, Delay = 4.25f, Rate = 9.75f;
		TArray<FRPGPhaseConfig> Phases;
		FName FieldPhaseId = PhaseTwo; // the id the manifest paths are written for
		TSet<FString> OmitFields;
		bool bNoFields = false;
		int32 Schema = 1;
		FName BossId = FName(TEXT("Boss01"));
		FName PresentationId = FName(TEXT("Boss01Look"));
		FString Hash = FString::ChrN(64, TEXT('b'));
		bool bSynthetic = true;
		FEpochPtr Content;
	};

	FConfigSpec DefaultSpec(FEpochPtr Content)
	{
		FConfigSpec Spec;
		Spec.Content = Content;
		Spec.Phases.Add(MakePhase(PhaseTwo, 0.35f, 1.5f, 1.75f, 2.f));
		return Spec;
	}

	FConfigPtr BuildConfigWith(const FConfigSpec& Spec, const TFunction<void(FRPGParticipantConfig&)>& Mutate)
	{
		TSharedRef<FRPGParticipantConfig> Value = MakeShared<FRPGParticipantConfig>();
		Value->BossId = Spec.BossId;
		Value->PresentationId = Spec.PresentationId;
		Value->Schema = Spec.Schema;
		Value->StableManifestHash = Spec.Hash;
		Value->Stats.MaxHealth = Spec.Health;
		Value->Stats.MaxPosture = Spec.Posture;
		Value->Stats.PostureRegenDelay = Spec.Delay;
		Value->Stats.PostureRegenRate = Spec.Rate;
		Value->Phases = Spec.Phases;
		if (!Spec.bNoFields)
		{
			for (const FString& Path : AllRequiredPaths(Spec.FieldPhaseId))
			{
				if (!Spec.OmitFields.Contains(Path))
				{
					Value->Fields.Add(MakeField(Path));
				}
			}
		}
		Value->Content = Spec.Content;
		Value->bSyntheticFixture = Spec.bSynthetic;
		if (Mutate)
		{
			Mutate(*Value);
		}
		return Value;
	}

	FConfigPtr BuildConfig(const FConfigSpec& Spec)
	{
		return BuildConfigWith(Spec, TFunction<void(FRPGParticipantConfig&)>());
	}

	/** The real dev-automation synthetic factory, the way the existing binding test uses it. */
	FConfigPtr FactoryConfig(FEpochPtr Content)
	{
		TStrongObjectPtr<URPGBossDefinition> Definition(NewObject<URPGBossDefinition>());
		Definition->DefinitionId = TEXT("Synthetic");
		Definition->PresentationId = TEXT("SyntheticLook");
		Definition->Stats.MaxHealth = 3500.f;
		Definition->Stats.MaxPosture = 73.5f;
		Definition->Stats.PostureRegenDelay = 4.25f;
		Definition->Stats.PostureRegenRate = 9.75f;
		Definition->Phases.Add(MakePhase(PhaseTwo, 0.35f, 1.5f, 1.75f, 2.f));
		for (const FString& Path : AllRequiredPaths(PhaseTwo))
		{
			Definition->Fields.Add(MakeField(Path));
		}
		FConfigPtr Out;
		const FRPGHydrationResult Compiled = RPGCombatHydration::CompileSyntheticParticipant(*Definition, Content, FString::ChrN(64, TEXT('b')), Out);
		return Compiled.IsReady() ? Out : FConfigPtr();
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

	/** One world, a boss and a player actor, a content lease, two factory configs, the valid input and a valid prior plan used to prove that failures clear the output. */
	struct FFixture
	{
		FPreflightWorld Scope;
		AActor* Boss = nullptr;
		AActor* Player = nullptr;
		FEpochPtr Content;
		FConfigPtr BossConfig, PlayerConfig;
		FGuid Encounter;
		FRPGHydrationPreflightInput Valid;
		FPlanPtr PriorPlan;
		bool bOk = false;

		FFixture()
		{
			if (!Scope.World)
			{
				return;
			}
			Boss = Scope.SpawnActor();
			Player = Scope.SpawnActor();
			Content = RPGCombatRegistry::Legacy();
			BossConfig = FactoryConfig(Content);
			PlayerConfig = FactoryConfig(Content);
			if (!Boss || !Player || !Content.IsValid() || !BossConfig.IsValid() || !PlayerConfig.IsValid())
			{
				return;
			}
			Encounter = FGuid::NewGuid();
			Valid.ExpectedWorld = Scope.World;
			Valid.EncounterInstance = Encounter;
			Valid.ExpectedContent = Content;
			Valid.Requests.Add(MakeRequest(Boss, TEXT("Boss"), TEXT("Player"), ERPGPreflightRole::BossCore, BossConfig, PhaseTwo));
			Valid.Requests.Add(MakeRequest(Player, TEXT("Player"), TEXT("Boss"), ERPGPreflightRole::TargetOnly, PlayerConfig));
			bOk = RPGBossHydrationPreflight::CompilePreflight(Valid, PriorPlan).IsReady() && PriorPlan.IsValid();
		}
	};

	/** Everything a compile must leave alone: per actor the component count, the begun flag and the presence of each managed consumer; and the world's combat context counts. */
	TArray<int32> CaptureState(UWorld* World)
	{
		TArray<int32> State;
		const TArray<UClass*> Managed = RPGBossHydrationPreflight::ManagedCoreConsumerClasses();
		for (TActorIterator<AActor> It(World); It; ++It)
		{
			State.Add(It->GetComponents().Num());
			State.Add(It->HasActorBegunPlay() ? 1 : 0);
			for (UClass* Class : Managed)
			{
				State.Add(It->FindComponentByClass(Class) ? 1 : 0);
			}
		}
		if (const URPGCombatContextSubsystem* Context = World->GetSubsystem<URPGCombatContextSubsystem>())
		{
			State.Add(Context->GetBoundCount());
			State.Add(Context->GetReadyCount());
		}
		return State;
	}

	bool AnyErrorStartsWith(const FRPGHydrationResult& Result, const TCHAR* Token)
	{
		return Result.Errors.ContainsByPredicate([Token](const FString& E) { return E.StartsWith(Token); });
	}

	bool AnyErrorContains(const FRPGHydrationResult& Result, const FString& Text)
	{
		return Result.Errors.ContainsByPredicate([&Text](const FString& E) { return E.Contains(Text); });
	}

	/** A failing compile: refused with the named token (and the detail text when given), the output that held a valid prior plan is cleared, nothing in the world changed. */
	bool ExpectRejected(FAutomationTestBase& Test, FFixture& F, const TCHAR* Label, const FRPGHydrationPreflightInput& Input, const TCHAR* Token, const TCHAR* Detail = nullptr)
	{
		FPlanPtr Out = F.PriorPlan; // a previous valid plan: a failure must not leave it in place
		const TArray<int32> Before = CaptureState(F.Scope.World);
		const FRPGHydrationResult Result = RPGBossHydrationPreflight::CompilePreflight(Input, Out);
		bool bOk = true;
		bOk &= Test.TestFalse(FString::Printf(TEXT("%s: refused"), Label), Result.IsReady());
		bOk &= Test.TestFalse(FString::Printf(TEXT("%s: the earlier output was cleared and no plan was published"), Label), Out.IsValid());
		const bool bNamed = AnyErrorStartsWith(Result, Token);
		bOk &= Test.TestTrue(FString::Printf(TEXT("%s: a failure named %s (errors: %d, first: '%s')"), Label, Token, Result.Errors.Num(), Result.Errors.Num() ? *Result.Errors[0] : TEXT("")), bNamed);
		if (Detail)
		{
			bOk &= Test.TestTrue(FString::Printf(TEXT("%s: the failure carries '%s'"), Label, Detail), AnyErrorContains(Result, FString(Detail)));
		}
		bOk &= Test.TestTrue(FString::Printf(TEXT("%s: no actor, component or combat context changed"), Label), CaptureState(F.Scope.World) == Before);
		return bOk;
	}

	bool PreconditionOk(FAutomationTestBase& Test, const FFixture& F)
	{
		if (!F.bOk)
		{
			Test.AddError(TEXT("unsupported precondition: the fixture (world, two actors, content lease, two factory configs, a valid prior plan) could not be built"));
		}
		return F.bOk;
	}
}
}

using namespace PreflightTests;

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPreflightValidTest, "OneBossFight.Binding.Preflight.Valid",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPreflightValidTest::RunTest(const FString& Parameters)
{
	FFixture F;
	if (!PreconditionOk(*this, F))
	{
		return false;
	}
	TestTrue(TEXT("the boss config came from the real synthetic factory"), F.BossConfig->bSyntheticFixture && F.BossConfig->Content.Get() == F.Content.Get());

	// A three-member batch: the order of the requests is the order of the plan; the boss target is named by slot, not found by position.
	AActor* Extra = F.Scope.SpawnActor();
	if (!TestNotNull(TEXT("third actor"), Extra))
	{
		return false;
	}
	FRPGHydrationPreflightInput Input = F.Valid;
	Input.Requests.Insert(MakeRequest(Extra, TEXT("Extra"), TEXT("Boss"), ERPGPreflightRole::TargetOnly, F.PlayerConfig), 0);
	const TArray<int32> Before = CaptureState(F.Scope.World);

	FPlanPtr Plan;
	const FRPGHydrationResult Result = RPGBossHydrationPreflight::CompilePreflight(Input, Plan);
	if (!TestTrue(TEXT("valid batch compiles"), Result.IsReady() && Result.Errors.IsEmpty() && Plan.IsValid()))
	{
		return false;
	}

	// Explicit scope: an expanded native subset preflight, nothing more.
	TestTrue(TEXT("scope name"), FString(FRPGHydrationPreflightPlan::ScopeName()) == TEXT("ExpandedNativeSubsetPreflight"));
	TestFalse(TEXT("not a complete playable bundle"), Plan->IsCompletePlayableBundle());
	TestFalse(TEXT("not a reservation"), Plan->IsReservation());
	TestFalse(TEXT("not ready"), Plan->IsReady());

	// Identity: copied encounter identity, the world, and the SAME content lease that was validated.
	TestTrue(TEXT("encounter identity copied"), Plan->EncounterInstance == F.Encounter);
	TestTrue(TEXT("world retained"), Plan->World.Get() == F.Scope.World);
	TestTrue(TEXT("the very content lease, not a copy"), Plan->Content.Get() == F.Content.Get());
	if (!TestEqual(TEXT("three participants"), Plan->Participants.Num(), 3))
	{
		return false;
	}
	TestTrue(TEXT("participants keep the order of the requests"), Plan->Participants[0].Slot == FName(TEXT("Extra")) && Plan->Participants[1].Slot == FName(TEXT("Boss")) && Plan->Participants[2].Slot == FName(TEXT("Player")));
	TestTrue(TEXT("target slots copied as given"), Plan->Participants[0].TargetSlot == FName(TEXT("Boss")) && Plan->Participants[1].TargetSlot == FName(TEXT("Player")) && Plan->Participants[2].TargetSlot == FName(TEXT("Boss")));
	TestTrue(TEXT("roles copied"), Plan->Participants[0].Role == ERPGPreflightRole::TargetOnly && Plan->Participants[1].Role == ERPGPreflightRole::BossCore && Plan->Participants[2].Role == ERPGPreflightRole::TargetOnly);
	TestTrue(TEXT("weak actor identities resolve to the input actors"), Plan->Participants[0].Actor.Get() == Extra && Plan->Participants[1].Actor.Get() == F.Boss && Plan->Participants[2].Actor.Get() == F.Player);
	TestTrue(TEXT("config leases are the very leases validated"), Plan->Participants[1].Config.Get() == F.BossConfig.Get() && Plan->Participants[2].Config.Get() == F.PlayerConfig.Get());

	// Boss-core: Stagger, Phases, Encounter, DormantWake, Posture, built from the five accepted combined factories; target-only: no boss plan.
	const FRPGPreflightParticipantPlan& Boss = Plan->Participants[1];
	if (!TestEqual(TEXT("boss-core has five plans"), Boss.Plans.Num(), 5))
	{
		return false;
	}
	TestTrue(TEXT("plan classes in the deterministic relative order Stagger, Phases, Encounter, DormantWake, Posture"), Boss.Plans[0].Class == URPGBossStagger::StaticClass() && Boss.Plans[1].Class == URPGBossPhases::StaticClass()
		&& Boss.Plans[2].Class == URPGBossEncounter::StaticClass() && Boss.Plans[3].Class == URPGBossDormantWake::StaticClass() && Boss.Plans[4].Class == URPGBossPosture::StaticClass());
	TestTrue(TEXT("plan instance names are the legacy names"), Boss.Plans[0].InstanceName == FName(TEXT("RPGBossStagger")) && Boss.Plans[1].InstanceName == FName(TEXT("RPGBossPhases")) && Boss.Plans[2].InstanceName == FName(TEXT("RPGBossEncounter"))
		&& Boss.Plans[3].InstanceName == FName(TEXT("RPGBossDormantWake")) && Boss.Plans[4].InstanceName == FName(TEXT("RPGBossPosture")));
	TestTrue(TEXT("the callbacks exist (they were built, never run)"), static_cast<bool>(Boss.Plans[0].Configure) && static_cast<bool>(Boss.Plans[1].Configure) && static_cast<bool>(Boss.Plans[2].Configure)
		&& static_cast<bool>(Boss.Plans[3].Configure) && static_cast<bool>(Boss.Plans[4].Configure));
	TSet<FString> Required;
	for (const FRPGComponentPlan& ComponentPlan : Boss.Plans)
	{
		for (const FString& Path : ComponentPlan.RequiredFields)
		{
			Required.Add(Path);
		}
	}
	TestEqual(TEXT("the union of required manifest paths is fifty-one"), Required.Num(), 51);
	for (const FString& Path : AllRequiredPaths(PhaseTwo))
	{
		TestTrue(FString::Printf(TEXT("required path %s is named by a plan"), *Path), Required.Contains(Path));
	}
	TestEqual(TEXT("one class lease per boss plan"), Boss.ClassLeases.Num(), 5);
	TestTrue(TEXT("the class leases are the plan classes"), Boss.ClassLeases.Num() == 5 && Boss.ClassLeases[0].Get() == Boss.Plans[0].Class && Boss.ClassLeases[1].Get() == Boss.Plans[1].Class && Boss.ClassLeases[2].Get() == Boss.Plans[2].Class
		&& Boss.ClassLeases[3].Get() == Boss.Plans[3].Class && Boss.ClassLeases[4].Get() == Boss.Plans[4].Class);
	TestTrue(TEXT("target-only members get no boss plan and no class lease"), Plan->Participants[0].Plans.IsEmpty() && Plan->Participants[2].Plans.IsEmpty() && Plan->Participants[0].ClassLeases.IsEmpty() && Plan->Participants[2].ClassLeases.IsEmpty());

	// Deterministic: a second compile of the same input gives the same plan names, classes and order, as a different object.
	FPlanPtr Again;
	TestTrue(TEXT("second compile"), RPGBossHydrationPreflight::CompilePreflight(Input, Again).IsReady() && Again.IsValid());
	if (Again.IsValid() && Again->Participants.Num() == 3 && Again->Participants[1].Plans.Num() == 5)
	{
		TestTrue(TEXT("a different plan object"), Again.Get() != Plan.Get());
		bool bSame = true;
		for (int32 Index = 0; Index < 5; ++Index)
		{
			bSame = bSame && Again->Participants[1].Plans[Index].InstanceName == Boss.Plans[Index].InstanceName && Again->Participants[1].Plans[Index].Class == Boss.Plans[Index].Class;
		}
		TestTrue(TEXT("same order and names"), bSame);
	}

	// A success touches nothing either: no component, no begun actor, no bound or ready context. The kernel ran no Configure callback and created no component.
	TestTrue(TEXT("compiling changed no actor, component or combat context"), CaptureState(F.Scope.World) == Before);
	TestTrue(TEXT("no managed consumer exists on any actor"), !F.Boss->FindComponentByClass<URPGBossPhases>() && !F.Boss->FindComponentByClass<URPGBossEncounter>() && !F.Boss->FindComponentByClass<URPGBossPosture>()
		&& !F.Boss->FindComponentByClass<URPGBossStagger>() && !F.Boss->FindComponentByClass<URPGBossDormantWake>() && !F.Boss->FindComponentByClass<URPGCombatParticipant>());
	const URPGCombatContextSubsystem* Context = F.Scope.World->GetSubsystem<URPGCombatContextSubsystem>();
	TestTrue(TEXT("the context exists and stays empty"), Context && Context->GetBoundCount() == 0 && Context->GetReadyCount() == 0);

	AddInfo(TEXT("Expanded native subset preflight only: NOT a complete playable bundle, a reservation, a hydrated context or a duel; the expected content lease is not game-instance provenance."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPreflightIndependenceTest, "OneBossFight.Binding.Preflight.Independence",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPreflightIndependenceTest::RunTest(const FString& Parameters)
{
	FFixture F;
	if (!PreconditionOk(*this, F))
	{
		return false;
	}
	// Batch B: another encounter, another content lease, other actors, other configs, in the same world.
	AActor* BossB = F.Scope.SpawnActor();
	AActor* PlayerB = F.Scope.SpawnActor();
	const FEpochPtr ContentB = RPGCombatRegistry::Legacy(); // a new epoch with a new id on every call
	const FConfigPtr BossConfigB = FactoryConfig(ContentB);
	const FConfigPtr PlayerConfigB = FactoryConfig(ContentB);
	if (!TestTrue(TEXT("batch B built"), BossB && PlayerB && ContentB.IsValid() && BossConfigB.IsValid() && PlayerConfigB.IsValid()))
	{
		return false;
	}
	TestTrue(TEXT("two independent content leases: different instance and different epoch id"), ContentB.Get() != F.Content.Get() && ContentB->Id != F.Content->Id);
	FRPGHydrationPreflightInput InputB;
	InputB.ExpectedWorld = F.Scope.World;
	InputB.EncounterInstance = FGuid::NewGuid();
	InputB.ExpectedContent = ContentB;
	InputB.Requests.Add(MakeRequest(BossB, TEXT("Boss"), TEXT("Player"), ERPGPreflightRole::BossCore, BossConfigB, PhaseTwo));
	InputB.Requests.Add(MakeRequest(PlayerB, TEXT("Player"), TEXT("Boss"), ERPGPreflightRole::TargetOnly, PlayerConfigB));

	FPlanPtr PlanA = F.PriorPlan;
	FPlanPtr PlanB;
	TestTrue(TEXT("batch B compiles"), RPGBossHydrationPreflight::CompilePreflight(InputB, PlanB).IsReady() && PlanB.IsValid());
	if (!PlanB.IsValid())
	{
		return false;
	}
	TestTrue(TEXT("each plan retains its own encounter, content lease and config leases"),
		PlanA->EncounterInstance == F.Encounter && PlanB->EncounterInstance == InputB.EncounterInstance && PlanA->EncounterInstance != PlanB->EncounterInstance
		&& PlanA->Content.Get() == F.Content.Get() && PlanB->Content.Get() == ContentB.Get()
		&& PlanA->Participants[0].Config.Get() == F.BossConfig.Get() && PlanB->Participants[0].Config.Get() == BossConfigB.Get());
	TestTrue(TEXT("compiling B did not touch the plan of A"), PlanA->Participants.Num() == 2 && PlanA->Participants[0].Actor.Get() == F.Boss && PlanA->Participants[1].Actor.Get() == F.Player);

	// Batches do not mix: A's input with B's boss config is a lease mismatch, the other way round too.
	FRPGHydrationPreflightInput Mixed = F.Valid;
	Mixed.Requests[0].Config = BossConfigB;
	ExpectRejected(*this, F, TEXT("batch A with a config of batch B"), Mixed, TEXT("Preflight.ContentLeaseMismatch"));
	FRPGHydrationPreflightInput MixedB = InputB;
	MixedB.Requests[1].Config = F.PlayerConfig;
	FPlanPtr Out = PlanB;
	const FRPGHydrationResult MixedResult = RPGBossHydrationPreflight::CompilePreflight(MixedB, Out);
	TestTrue(TEXT("batch B with a config of batch A: refused with a lease mismatch, output cleared"), !MixedResult.IsReady() && AnyErrorStartsWith(MixedResult, TEXT("Preflight.ContentLeaseMismatch")) && !Out.IsValid());
	TestTrue(TEXT("the other holders of the plans are unaffected by the cleared output"), PlanA.IsValid() && PlanB.IsValid() && PlanB->Content.Get() == ContentB.Get());

	// Stale output: an output that holds a valid plan is cleared by a failing compile, and replaced by a succeeding one.
	FPlanPtr Held = PlanA;
	FRPGHydrationPreflightInput Empty = F.Valid;
	Empty.Requests.Reset();
	const FRPGHydrationResult EmptyResult = RPGBossHydrationPreflight::CompilePreflight(Empty, Held);
	TestTrue(TEXT("empty batch refused, held plan cleared"), !EmptyResult.IsReady() && AnyErrorStartsWith(EmptyResult, TEXT("Preflight.EmptyBatch")) && !Held.IsValid());
	FPlanPtr Replaced = PlanA;
	TestTrue(TEXT("a succeeding compile replaces the held plan with the new one"), RPGBossHydrationPreflight::CompilePreflight(F.Valid, Replaced).IsReady() && Replaced.IsValid() && Replaced.Get() != PlanA.Get());

	// A failure after a valid member: the boss is valid and first, the player is not, and nothing at all is published, not even the boss.
	FRPGHydrationPreflightInput FailAfterValid = F.Valid;
	FailAfterValid.Requests[1].Config.Reset();
	ExpectRejected(*this, F, TEXT("valid boss then a member without a config"), FailAfterValid, TEXT("Preflight.NoConfig"));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPreflightBatchTest, "OneBossFight.Binding.Preflight.BatchAndActors",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPreflightBatchTest::RunTest(const FString& Parameters)
{
	FFixture F;
	if (!PreconditionOk(*this, F))
	{
		return false;
	}
	FPreflightWorld OtherWorld;
	AActor* Foreign = OtherWorld.SpawnActor();
	if (!TestTrue(TEXT("a second world with an actor"), OtherWorld.World && Foreign))
	{
		return false;
	}

	// Batch level.
	{
		FRPGHydrationPreflightInput In = F.Valid;
		In.ExpectedWorld.Reset();
		ExpectRejected(*this, F, TEXT("no expected world"), In, TEXT("Preflight.NoWorld"));
	}
	{
		FRPGHydrationPreflightInput In = F.Valid;
		In.EncounterInstance = FGuid();
		ExpectRejected(*this, F, TEXT("invalid encounter guid"), In, TEXT("Preflight.InvalidEncounter"));
	}
	{
		FRPGHydrationPreflightInput In = F.Valid;
		In.ExpectedContent.Reset();
		ExpectRejected(*this, F, TEXT("no expected content lease"), In, TEXT("Preflight.InvalidContent"));
	}
	{
		FRPGHydrationPreflightInput In = F.Valid;
		In.ExpectedContent = MakeShared<RPGCombatRegistry::FEpoch>(); // a default epoch has no valid id
		ExpectRejected(*this, F, TEXT("content epoch without a valid id"), In, TEXT("Preflight.InvalidContent"));
	}
	{
		FRPGHydrationPreflightInput In = F.Valid;
		In.Requests.Reset();
		ExpectRejected(*this, F, TEXT("empty batch"), In, TEXT("Preflight.EmptyBatch"));
	}

	// Slots and roles.
	{
		FRPGHydrationPreflightInput In = F.Valid;
		In.Requests[1].Slot = NAME_None;
		ExpectRejected(*this, F, TEXT("empty slot"), In, TEXT("Preflight.InvalidSlot"));
	}
	{
		FRPGHydrationPreflightInput In = F.Valid;
		In.Requests[1].Slot = In.Requests[0].Slot;
		In.Requests[1].TargetSlot = FName(TEXT("Boss"));
		ExpectRejected(*this, F, TEXT("duplicate slot"), In, TEXT("Preflight.DuplicateSlot"));
	}
	{
		FRPGHydrationPreflightInput In = F.Valid;
		In.Requests[1].Role = ERPGPreflightRole::None;
		ExpectRejected(*this, F, TEXT("role not set"), In, TEXT("Preflight.InvalidRole"));
	}

	// Actors.
	{
		FRPGHydrationPreflightInput In = F.Valid;
		In.Requests[1].Actor.Reset();
		ExpectRejected(*this, F, TEXT("null actor"), In, TEXT("Preflight.NullActor"));
	}
	{
		AActor* Dead = F.Scope.SpawnActor();
		FRPGHydrationPreflightInput In = F.Valid;
		In.Requests[1].Actor = Dead;
		const bool bDestroyed = Dead && Dead->Destroy();
		const bool bStale = In.Requests[1].Actor.IsStale();
		if (!TestTrue(TEXT("precondition: the actor was destroyed"), bDestroyed))
		{
			AddError(TEXT("unsupported precondition: the actor could not be destroyed"));
		}
		else if (bStale)
		{
			// The engine marked the destroyed actor garbage: the weak pointer is stale and must be reported without a dereference.
			ExpectRejected(*this, F, TEXT("destroyed actor (stale weak pointer)"), In, TEXT("Preflight.StaleActor"));
		}
		else if (In.Requests[1].Actor.IsValid() && In.Requests[1].Actor->IsActorBeingDestroyed())
		{
			ExpectRejected(*this, F, TEXT("destroyed actor (still resolvable, being destroyed)"), In, TEXT("Preflight.ActorDestroying"));
		}
		else
		{
			AddError(TEXT("unsupported precondition: a destroyed actor is neither stale nor flagged as being destroyed"));
		}
	}
	{
		AActor* Begun = F.Scope.SpawnActor();
		FRPGHydrationPreflightInput In = F.Valid;
		In.Requests[1].Actor = Begun;
		if (!TestNotNull(TEXT("actor to begin play"), Begun))
		{
			return false;
		}
		Begun->DispatchBeginPlay();
		if (TestTrue(TEXT("precondition: the actor began play"), Begun->HasActorBegunPlay()))
		{
			ExpectRejected(*this, F, TEXT("actor that began play"), In, TEXT("Preflight.ActorBegunPlay"));
		}
		else
		{
			AddError(TEXT("unsupported precondition: the actor could not be put into the begun state"));
		}
	}
	{
		FRPGHydrationPreflightInput In = F.Valid;
		In.Requests[1].Actor = Foreign;
		ExpectRejected(*this, F, TEXT("actor of another world"), In, TEXT("Preflight.ForeignWorld"));
	}
	{
		FRPGHydrationPreflightInput In = F.Valid;
		In.Requests[1].Actor = F.Boss;
		ExpectRejected(*this, F, TEXT("the same actor in two requests"), In, TEXT("Preflight.DuplicateActor"));
	}

	// Several failures are all reported, with their slots, and a stale actor is never dereferenced.
	{
		AActor* Dead = F.Scope.SpawnActor();
		FRPGHydrationPreflightInput In = F.Valid;
		In.Requests[0].Actor.Reset();
		In.Requests[1].Actor = Dead;
		if (Dead && Dead->Destroy())
		{
			FPlanPtr Out = F.PriorPlan;
			const FRPGHydrationResult Result = RPGBossHydrationPreflight::CompilePreflight(In, Out);
			TestFalse(TEXT("two bad members: refused"), Result.IsReady());
			TestTrue(TEXT("two bad members: both are reported with their slots"), AnyErrorContains(Result, TEXT("[slot=Boss]")) && AnyErrorContains(Result, TEXT("[slot=Player]")) && Result.Errors.Num() >= 2);
			TestFalse(TEXT("two bad members: nothing published"), Out.IsValid());
		}
		else
		{
			AddError(TEXT("unsupported precondition: the second bad member could not be built"));
		}
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPreflightConfigTest, "OneBossFight.Binding.Preflight.ConfigAndFields",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPreflightConfigTest::RunTest(const FString& Parameters)
{
	FFixture F;
	if (!PreconditionOk(*this, F))
	{
		return false;
	}
	// A case replaces the boss config (request 0) by one built from a spec; the rest of the batch stays valid.
	auto WithBossConfig = [&](const FConfigSpec& Spec)
	{
		FRPGHydrationPreflightInput In = F.Valid;
		In.Requests[0].Config = BuildConfig(Spec);
		return In;
	};
	const FConfigSpec Base = DefaultSpec(F.Content);
	{
		FRPGHydrationPreflightInput In = WithBossConfig(Base);
		FPlanPtr Out;
		TestTrue(TEXT("control: a hand-built config of the same shape is accepted like the factory one"), RPGBossHydrationPreflight::CompilePreflight(In, Out).IsReady() && Out.IsValid());
	}

	{
		FRPGHydrationPreflightInput In = F.Valid;
		In.Requests[1].Config.Reset();
		ExpectRejected(*this, F, TEXT("no config"), In, TEXT("Preflight.NoConfig"));
	}

	// The lease: the same instance, never an equal-looking one.
	{
		FConfigSpec Spec = Base;
		Spec.Content = RPGCombatRegistry::Legacy();
		ExpectRejected(*this, F, TEXT("config compiled against another content epoch"), WithBossConfig(Spec), TEXT("Preflight.ContentLeaseMismatch"));
	}
	{
		TSharedRef<RPGCombatRegistry::FEpoch> Lookalike = MakeShared<RPGCombatRegistry::FEpoch>();
		Lookalike->Id = F.Content->Id;
		Lookalike->Source = F.Content->Source;
		FConfigSpec Spec = Base;
		Spec.Content = Lookalike;
		ExpectRejected(*this, F, TEXT("equal-looking content (same id and source, different lease)"), WithBossConfig(Spec), TEXT("Preflight.ContentLeaseMismatch"));
	}
	{
		FConfigSpec Spec = Base;
		Spec.Content.Reset();
		ExpectRejected(*this, F, TEXT("config without a content lease"), WithBossConfig(Spec), TEXT("Preflight.ContentLeaseMismatch"));
	}

	// Manifest identity shape.
	{
		FConfigSpec Spec = Base; Spec.Schema = 2;
		ExpectRejected(*this, F, TEXT("schema 2"), WithBossConfig(Spec), TEXT("Preflight.InvalidManifestIdentity"));
	}
	{
		FConfigSpec Spec = Base; Spec.BossId = NAME_None;
		ExpectRejected(*this, F, TEXT("no boss id"), WithBossConfig(Spec), TEXT("Preflight.InvalidManifestIdentity"));
	}
	{
		FConfigSpec Spec = Base; Spec.PresentationId = NAME_None;
		ExpectRejected(*this, F, TEXT("no presentation id"), WithBossConfig(Spec), TEXT("Preflight.InvalidManifestIdentity"));
	}
	{
		FConfigSpec Spec = Base; Spec.Hash = FString::ChrN(63, TEXT('b'));
		ExpectRejected(*this, F, TEXT("manifest hash of 63 characters"), WithBossConfig(Spec), TEXT("Preflight.InvalidManifestIdentity"));
	}
	{
		FConfigSpec Spec = Base; Spec.Hash = FString::ChrN(64, TEXT('z'));
		ExpectRejected(*this, F, TEXT("manifest hash that is not hexadecimal"), WithBossConfig(Spec), TEXT("Preflight.InvalidManifestIdentity"));
	}
	{
		FConfigSpec Spec = Base; Spec.bNoFields = true;
		ExpectRejected(*this, F, TEXT("empty field manifest"), WithBossConfig(Spec), TEXT("Preflight.InvalidManifestIdentity"));
	}

	// Typed stats and phase, through the accepted validators; their own named failure is carried.
	{
		FConfigSpec Spec = Base; Spec.Posture = -1.f;
		ExpectRejected(*this, F, TEXT("negative posture maximum"), WithBossConfig(Spec), TEXT("Preflight.StatsRejected"), TEXT("InvalidStats.NotPositive"));
	}
	{
		FConfigSpec Spec = Base; Spec.Health = 0.5f;
		ExpectRejected(*this, F, TEXT("health the native override cannot apply"), WithBossConfig(Spec), TEXT("Preflight.StatsRejected"), TEXT("UnsupportedNativeHealthOverride"));
	}
	{
		FConfigSpec Spec = Base; Spec.Delay = std::numeric_limits<float>::quiet_NaN();
		ExpectRejected(*this, F, TEXT("NaN regeneration delay"), WithBossConfig(Spec), TEXT("Preflight.StatsRejected"), TEXT("InvalidStats.NotFinite"));
	}
	{
		FRPGHydrationPreflightInput In = WithBossConfig(Base);
		In.Requests[0].SelectedPhaseId = NAME_None;
		ExpectRejected(*this, F, TEXT("no selected phase id"), In, TEXT("Preflight.PhaseRejected"), TEXT("InvalidPhase.NoSelection"));
	}
	{
		FRPGHydrationPreflightInput In = WithBossConfig(Base);
		In.Requests[0].SelectedPhaseId = FName(TEXT("Other"));
		ExpectRejected(*this, F, TEXT("selected phase id not in the config"), In, TEXT("Preflight.PhaseRejected"), TEXT("InvalidPhase.NotFound"));
	}
	{
		FConfigSpec Spec = Base; Spec.Phases.Add(MakePhase(FName(TEXT("PhaseThree")), 0.2f, 2.f, 2.f, 2.f));
		ExpectRejected(*this, F, TEXT("a second transition (unsupported phase set)"), WithBossConfig(Spec), TEXT("Preflight.PhaseRejected"), TEXT("UnsupportedNativePhaseSet"));
	}
	{
		FConfigSpec Spec = Base; Spec.Phases[0].AttackMultiplier = 0.5f;
		ExpectRejected(*this, F, TEXT("attack multiplier below 1 (unsupported by the native reset)"), WithBossConfig(Spec), TEXT("Preflight.PhaseRejected"), TEXT("UnsupportedNativeDamageScale"));
	}

	// Each of the fifty-one required manifest paths of the five combined plans, one at a time.
	for (const FString& Path : AllRequiredPaths(PhaseTwo))
	{
		FConfigSpec Spec = Base;
		Spec.OmitFields.Add(Path);
		ExpectRejected(*this, F, *FString::Printf(TEXT("manifest without %s"), *Path), WithBossConfig(Spec), TEXT("Preflight.MissingRequiredField"), *Path);
	}

	// A preexisting consumer is never adopted: each managed class on a fresh boss, and the participant component on a target-only member.
	{
		const TArray<UClass*> Managed = RPGBossHydrationPreflight::ManagedCoreConsumerClasses();
		for (UClass* Class : Managed)
		{
			const bool bParticipant = Class == URPGCombatParticipant::StaticClass();
			AActor* Host = F.Scope.SpawnActor();
			if (!Host)
			{
				AddError(TEXT("unsupported precondition: a host actor could not be spawned"));
				continue;
			}
			UActorComponent* Existing = NewObject<UActorComponent>(Host, Class);
			Existing->RegisterComponent();
			if (!TestTrue(FString::Printf(TEXT("precondition: %s is on the actor"), *Class->GetName()), Host->FindComponentByClass(Class) != nullptr))
			{
				AddError(TEXT("unsupported precondition: the preexisting consumer could not be attached"));
				continue;
			}
			FRPGHydrationPreflightInput In = F.Valid;
			In.Requests[bParticipant ? 1 : 0].Actor = Host;
			ExpectRejected(*this, F, *FString::Printf(TEXT("preexisting %s"), *Class->GetName()), In, TEXT("Preflight.PreexistingConsumer"), *Class->GetName());
		}
	}

	// A target-only member has no phase to select; a production member (not a synthetic fixture) fails closed without a compiled skeleton and a compatible character mesh.
	{
		FRPGHydrationPreflightInput In = F.Valid;
		In.Requests[1].SelectedPhaseId = PhaseTwo;
		ExpectRejected(*this, F, TEXT("target-only with a selected phase"), In, TEXT("Preflight.UnexpectedPhaseSelection"));
	}
	{
		FConfigSpec Spec = Base; Spec.bSynthetic = false;
		ExpectRejected(*this, F, TEXT("production config without a skeleton, animations or a character mesh"), WithBossConfig(Spec), TEXT("Preflight.ProductionPrerequisite"));
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPreflightTargetsTest, "OneBossFight.Binding.Preflight.Targets",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPreflightTargetsTest::RunTest(const FString& Parameters)
{
	FFixture F;
	if (!PreconditionOk(*this, F))
	{
		return false;
	}
	{
		FRPGHydrationPreflightInput In = F.Valid;
		In.Requests[0].TargetSlot = NAME_None;
		ExpectRejected(*this, F, TEXT("boss without a target slot"), In, TEXT("Preflight.TargetMissing"));
	}
	{
		FRPGHydrationPreflightInput In = F.Valid;
		In.Requests[0].TargetSlot = In.Requests[0].Slot;
		ExpectRejected(*this, F, TEXT("boss targeting itself"), In, TEXT("Preflight.SelfTarget"));
	}
	{
		FRPGHydrationPreflightInput In = F.Valid;
		In.Requests[0].TargetSlot = FName(TEXT("Nobody"));
		ExpectRejected(*this, F, TEXT("boss targeting a slot that is not in the batch"), In, TEXT("Preflight.TargetNotInBatch"));
	}
	{
		FRPGHydrationPreflightInput In = F.Valid;
		In.Requests[1].TargetSlot = In.Requests[1].Slot;
		ExpectRejected(*this, F, TEXT("target-only member targeting itself"), In, TEXT("Preflight.SelfTarget"));
	}
	// The target is resolved by slot, never by position: the same two members in the other order still compile, with their target slots as given.
	{
		FRPGHydrationPreflightInput In = F.Valid;
		In.Requests.Swap(0, 1);
		FPlanPtr Out;
		const FRPGHydrationResult Result = RPGBossHydrationPreflight::CompilePreflight(In, Out);
		TestTrue(TEXT("members in the other order compile"), Result.IsReady() && Out.IsValid() && Out->Participants.Num() == 2);
		if (Out.IsValid() && Out->Participants.Num() == 2)
		{
			TestTrue(TEXT("the plan follows the request order, the player first"), Out->Participants[0].Slot == FName(TEXT("Player")) && Out->Participants[1].Slot == FName(TEXT("Boss")));
			TestTrue(TEXT("the boss target slot is still the explicit one, not 'the first member'"), Out->Participants[1].TargetSlot == FName(TEXT("Player")) && Out->Participants[0].TargetSlot == FName(TEXT("Boss")));
			TestTrue(TEXT("only the boss has plans"), Out->Participants[0].Plans.IsEmpty() && Out->Participants[1].Plans.Num() == 5);
		}
	}
	// A target that is a member but is itself invalid: the batch fails on that member, and no plan exists for the valid boss either.
	{
		FRPGHydrationPreflightInput In = F.Valid;
		In.Requests[1].Actor.Reset();
		ExpectRejected(*this, F, TEXT("a valid boss whose target member has no actor"), In, TEXT("Preflight.NullActor"));
	}
	// A batch of two bosses that target each other is allowed by the contract (any other member), each with its own plans.
	{
		AActor* SecondBoss = F.Scope.SpawnActor();
		FRPGHydrationPreflightInput In = F.Valid;
		if (!TestNotNull(TEXT("second boss actor"), SecondBoss))
		{
			return false;
		}
		In.Requests[1] = MakeRequest(SecondBoss, TEXT("Boss2"), TEXT("Boss"), ERPGPreflightRole::BossCore, F.PlayerConfig, PhaseTwo);
		In.Requests[0].TargetSlot = FName(TEXT("Boss2"));
		FPlanPtr Out;
		const FRPGHydrationResult Result = RPGBossHydrationPreflight::CompilePreflight(In, Out);
		TestTrue(TEXT("two boss-core members targeting each other compile"), Result.IsReady() && Out.IsValid() && Out->Participants.Num() == 2 && Out->Participants[0].Plans.Num() == 5 && Out->Participants[1].Plans.Num() == 5);
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPreflightDependenciesTest, "OneBossFight.Binding.Preflight.Dependencies",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPreflightDependenciesTest::RunTest(const FString& Parameters)
{
	// Transient native fixtures only: two skeletons and animations bound to them. Nothing is loaded, no pack asset, no retargeting.
	TStrongObjectPtr<USkeleton> SkeletonA(NewObject<USkeleton>(GetTransientPackage(), TEXT("DepSkeletonA")));
	TStrongObjectPtr<USkeleton> SkeletonB(NewObject<USkeleton>(GetTransientPackage(), TEXT("DepSkeletonB")));
	TStrongObjectPtr<UAnimSequence> OnA(NewObject<UAnimSequence>(GetTransientPackage(), TEXT("DepAnimOnA")));
	TStrongObjectPtr<UAnimSequence> OnA2(NewObject<UAnimSequence>(GetTransientPackage(), TEXT("DepAnimOnA2")));
	TStrongObjectPtr<UAnimSequence> OnB(NewObject<UAnimSequence>(GetTransientPackage(), TEXT("DepAnimOnB")));
	TStrongObjectPtr<UAnimSequence> NoSkeleton(NewObject<UAnimSequence>(GetTransientPackage(), TEXT("DepAnimNoSkeleton")));
	TStrongObjectPtr<UAnimSequence> Dead(NewObject<UAnimSequence>(GetTransientPackage(), TEXT("DepAnimDead")));
	if (!TestTrue(TEXT("dependency fixtures created"), SkeletonA.IsValid() && SkeletonB.IsValid() && OnA.IsValid() && OnA2.IsValid() && OnB.IsValid() && NoSkeleton.IsValid() && Dead.IsValid()))
	{
		AddError(TEXT("unsupported precondition: the transient skeletons and animations could not be created"));
		return false;
	}
	OnA->SetSkeleton(SkeletonA.Get());
	OnA2->SetSkeleton(SkeletonA.Get());
	OnB->SetSkeleton(SkeletonB.Get());
	Dead->SetSkeleton(SkeletonA.Get());
	if (!TestTrue(TEXT("precondition: the animations hold the intended skeletons (and one holds none)"),
		OnA->GetSkeleton() == SkeletonA.Get() && OnA2->GetSkeleton() == SkeletonA.Get() && OnB->GetSkeleton() == SkeletonB.Get() && NoSkeleton->GetSkeleton() == nullptr && Dead->GetSkeleton() == SkeletonA.Get()))
	{
		AddError(TEXT("unsupported precondition: SetSkeleton did not bind the fixture animations as expected"));
		return false;
	}

	auto Fill = [](FRPGParticipantConfig& Config, USkeleton* Skeleton, const TArray<UAnimSequenceBase*>& Animations)
	{
		Config.Skeleton.Reset(Skeleton);
		for (UAnimSequenceBase* Animation : Animations)
		{
			Config.Animations.Emplace(Animation); // a null pointer makes a null lease on purpose
		}
	};
	struct FCase
	{
		const TCHAR* Name;
		USkeleton* Skeleton;
		TArray<UAnimSequenceBase*> Animations;
		bool bExpectOk;
		const TCHAR* Detail;
		const TCHAR* Detail2;
	};
	TArray<FCase> Cases;
	Cases.Add({TEXT("control: one animation on the compiled skeleton"), SkeletonA.Get(), {OnA.Get()}, true, nullptr, nullptr});
	Cases.Add({TEXT("control: two animations on the compiled skeleton"), SkeletonA.Get(), {OnA.Get(), OnA2.Get()}, true, nullptr, nullptr});
	Cases.Add({TEXT("no compiled skeleton"), nullptr, {OnA.Get()}, false, TEXT("compiled skeleton is missing"), nullptr});
	Cases.Add({TEXT("no animation at all"), SkeletonA.Get(), {}, false, TEXT("no compiled animation"), nullptr});
	Cases.Add({TEXT("a null lease as the only entry (the array is not empty)"), SkeletonA.Get(), {nullptr}, false, TEXT("animation lease #0 is not valid"), nullptr});
	Cases.Add({TEXT("a null lease after a valid animation"), SkeletonA.Get(), {OnA.Get(), nullptr}, false, TEXT("animation lease #1 is not valid"), nullptr});
	Cases.Add({TEXT("an animation of another skeleton"), SkeletonA.Get(), {OnB.Get()}, false, TEXT("belongs to skeleton"), TEXT("DepSkeletonB")});
	Cases.Add({TEXT("an animation with no skeleton"), SkeletonA.Get(), {NoSkeleton.Get()}, false, TEXT("belongs to skeleton none"), nullptr});
	Cases.Add({TEXT("a valid animation then a mismatched one"), SkeletonA.Get(), {OnA.Get(), OnB.Get()}, false, TEXT("animation #1 (DepAnimOnB)"), nullptr});
	Cases.Add({TEXT("every problem is reported: null, valid, mismatched"), SkeletonA.Get(), {nullptr, OnA.Get(), OnB.Get()}, false, TEXT("animation lease #0 is not valid"), TEXT("animation #2 (DepAnimOnB)")});
	for (const FCase& Case : Cases)
	{
		FRPGParticipantConfig Config;
		Fill(Config, Case.Skeleton, Case.Animations);
		FString Error;
		const bool bOk = RPGBossHydrationPreflight::CheckCompiledDependencies(Config, Error);
		if (Case.bExpectOk)
		{
			TestTrue(FString::Printf(TEXT("%s: accepted"), Case.Name), bOk && Error.IsEmpty());
			continue;
		}
		TestFalse(FString::Printf(TEXT("%s: refused"), Case.Name), bOk);
		TestTrue(FString::Printf(TEXT("%s: names the problem '%s' (got '%s')"), Case.Name, Case.Detail, *Error), Error.Contains(Case.Detail));
		if (Case.Detail2)
		{
			TestTrue(FString::Printf(TEXT("%s: also names '%s'"), Case.Name, Case.Detail2), Error.Contains(Case.Detail2));
		}
	}
	// A garbage-marked animation is an invalid lease too (the object is still allocated: the fixture holds it and no collection runs here).
	{
		Dead->MarkAsGarbage();
		if (TestFalse(TEXT("precondition: the marked animation is no longer valid"), IsValid(Dead.Get())))
		{
			FRPGParticipantConfig Config;
			Fill(Config, SkeletonA.Get(), {OnA.Get(), Dead.Get()});
			FString Error;
			TestFalse(TEXT("a garbage-marked animation lease is refused"), RPGBossHydrationPreflight::CheckCompiledDependencies(Config, Error));
			TestTrue(TEXT("and named by its position"), Error.Contains(TEXT("animation lease #1 is not valid")));
		}
		else
		{
			AddError(TEXT("unsupported precondition: the animation could not be marked garbage"));
		}
	}

	// In a batch: a production-style member is still refused on a plain actor (no character mesh), and the dependency reasons are reported separately from the mesh reason.
	FFixture F;
	if (!PreconditionOk(*this, F))
	{
		return false;
	}
	FConfigSpec Production = DefaultSpec(F.Content);
	Production.bSynthetic = false;
	auto BatchWith = [&](const TFunction<void(FRPGParticipantConfig&)>& Mutate)
	{
		FRPGHydrationPreflightInput In = F.Valid;
		In.Requests[0].Config = BuildConfigWith(Production, Mutate);
		return In;
	};
	{
		// Valid dependencies: only the mesh reason remains. The dependency predicate accepts, the actor is not a production-compatible character: fail closed, and NOT a positive production batch.
		FRPGHydrationPreflightInput In = BatchWith([&](FRPGParticipantConfig& C) { Fill(C, SkeletonA.Get(), {OnA.Get()}); });
		FPlanPtr Out = F.PriorPlan;
		const FRPGHydrationResult Result = RPGBossHydrationPreflight::CompilePreflight(In, Out);
		TestTrue(TEXT("valid dependencies on a plain actor: refused for the mesh only"), !Result.IsReady() && !Out.IsValid() && AnyErrorContains(Result, TEXT("character whose mesh")) && !AnyErrorContains(Result, TEXT("animation")));
	}
	{
		FRPGHydrationPreflightInput In = BatchWith([&](FRPGParticipantConfig& C) { Fill(C, SkeletonA.Get(), {nullptr}); });
		FPlanPtr Out = F.PriorPlan;
		const FRPGHydrationResult Result = RPGBossHydrationPreflight::CompilePreflight(In, Out);
		TestTrue(TEXT("a null animation lease in a batch: refused with the animation reason AND the mesh reason, output cleared"),
			!Result.IsReady() && !Out.IsValid() && AnyErrorStartsWith(Result, TEXT("Preflight.ProductionPrerequisite")) && AnyErrorContains(Result, TEXT("animation lease #0 is not valid")) && AnyErrorContains(Result, TEXT("character whose mesh")));
	}
	{
		FRPGHydrationPreflightInput In = BatchWith([&](FRPGParticipantConfig& C) { Fill(C, SkeletonA.Get(), {OnB.Get()}); });
		ExpectRejected(*this, F, TEXT("an animation of another skeleton in a batch"), In, TEXT("Preflight.ProductionPrerequisite"), TEXT("belongs to skeleton"));
	}

	AddInfo(TEXT("Dependency predicate on transient native fixtures; NO positive production batch (no production-compatible character mesh is built here)."));
	return true;
}

// ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
// DD13: the expanded native subset (five combined plans per boss-core member). The expected classes, names, counts and the 51-path union are written as independent literals in this file (AllRequiredPaths),
// not derived from the factories under test; the manifest the fixtures carry comes from the same literal list, the plans' own required fields are what the implementation produces.
// ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPreflightExpandedTest, "OneBossFight.Binding.Preflight.ExpandedSubset",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPreflightExpandedTest::RunTest(const FString& Parameters)
{
	FFixture F;
	if (!PreconditionOk(*this, F))
	{
		return false;
	}
	// Two boss-core members with DIFFERENT selected phase ids and different configs, and one target-only member: the request order is Boss, Boss2, Player.
	const FName PhaseAlt(TEXT("PhaseAlt"));
	AActor* Boss2 = F.Scope.SpawnActor();
	FConfigSpec SpecB = DefaultSpec(F.Content);
	SpecB.Phases.Reset();
	SpecB.Phases.Add(MakePhase(PhaseAlt, 0.5f, 2.f, 2.5f, 3.f));
	SpecB.FieldPhaseId = PhaseAlt;
	SpecB.Health = 4100.f;
	SpecB.Posture = 88.f;
	const FConfigPtr Boss2Config = BuildConfig(SpecB);
	if (!TestTrue(TEXT("second boss actor and config"), Boss2 && Boss2Config.IsValid()))
	{
		return false;
	}
	FRPGHydrationPreflightInput Input = F.Valid;
	Input.Requests.Insert(MakeRequest(Boss2, TEXT("Boss2"), TEXT("Boss"), ERPGPreflightRole::BossCore, Boss2Config, PhaseAlt), 1);
	const TArray<int32> Before = CaptureState(F.Scope.World);

	FPlanPtr Plan;
	const FRPGHydrationResult Result = RPGBossHydrationPreflight::CompilePreflight(Input, Plan);
	if (!TestTrue(TEXT("a batch of two boss-core members and a target compiles"), Result.IsReady() && Result.Errors.IsEmpty() && Plan.IsValid() && Plan->Participants.Num() == 3))
	{
		return false;
	}
	TestTrue(TEXT("the scope marker names the expanded native subset and nothing more"), FString(FRPGHydrationPreflightPlan::ScopeName()) == TEXT("ExpandedNativeSubsetPreflight")
		&& !Plan->IsCompletePlayableBundle() && !Plan->IsReservation() && !Plan->IsReady());

	// Independent expectations: the five classes and the legacy instance names, each exactly once, in the relative plan order.
	const TArray<UClass*> ExpectedClasses = {URPGBossStagger::StaticClass(), URPGBossPhases::StaticClass(), URPGBossEncounter::StaticClass(), URPGBossDormantWake::StaticClass(), URPGBossPosture::StaticClass()};
	const TArray<FName> ExpectedNames = {FName(TEXT("RPGBossStagger")), FName(TEXT("RPGBossPhases")), FName(TEXT("RPGBossEncounter")), FName(TEXT("RPGBossDormantWake")), FName(TEXT("RPGBossPosture"))};
	for (int32 Member = 0; Member < 2; ++Member)
	{
		const FRPGPreflightParticipantPlan& BossPlan = Plan->Participants[Member];
		const FName Selected = Member == 0 ? PhaseTwo : PhaseAlt;
		const FName Other = Member == 0 ? PhaseAlt : PhaseTwo;
		const FString Who = Member == 0 ? TEXT("boss with PhaseTwo") : TEXT("boss with PhaseAlt");
		if (!TestTrue(FString::Printf(TEXT("%s: exactly five plans, a boss-core role and five class leases"), *Who), BossPlan.Role == ERPGPreflightRole::BossCore && BossPlan.Plans.Num() == 5 && BossPlan.ClassLeases.Num() == 5))
		{
			return false;
		}
		bool bClasses = true, bNames = true, bCallbacks = true, bLeases = true;
		TSet<const UClass*> DistinctClasses;
		TSet<FName> DistinctNames;
		int32 SumOfRequired = 0;
		TSet<FString> Union;
		for (int32 Index = 0; Index < 5; ++Index)
		{
			bClasses = bClasses && BossPlan.Plans[Index].Class == ExpectedClasses[Index];
			bNames = bNames && BossPlan.Plans[Index].InstanceName == ExpectedNames[Index];
			bCallbacks = bCallbacks && static_cast<bool>(BossPlan.Plans[Index].Configure);
			bLeases = bLeases && BossPlan.ClassLeases[Index].Get() == BossPlan.Plans[Index].Class;
			DistinctClasses.Add(BossPlan.Plans[Index].Class);
			DistinctNames.Add(BossPlan.Plans[Index].InstanceName);
			SumOfRequired += BossPlan.Plans[Index].RequiredFields.Num();
			for (const FString& Path : BossPlan.Plans[Index].RequiredFields)
			{
				Union.Add(Path);
			}
		}
		TestTrue(FString::Printf(TEXT("%s: the classes are Stagger, Phases, Encounter, DormantWake, Posture in this order"), *Who), bClasses);
		TestTrue(FString::Printf(TEXT("%s: the instance names are the legacy names in the same order"), *Who), bNames);
		TestTrue(FString::Printf(TEXT("%s: every plan has its callback (built, never run) and the class leases are the plan classes"), *Who), bCallbacks && bLeases);
		TestTrue(FString::Printf(TEXT("%s: no native class and no instance name appears twice"), *Who), DistinctClasses.Num() == 5 && DistinctNames.Num() == 5);
		// The separate scalar, profile, flow and policy plans are gone: no plan names a class twice and the five plans together name each of the 51 paths exactly once.
		const TArray<FString> ExpectedPaths = AllRequiredPaths(Selected);
		bool bUnion = ExpectedPaths.Num() == 51 && Union.Num() == 51 && SumOfRequired == 51;
		for (const FString& Path : ExpectedPaths)
		{
			bUnion = bUnion && Union.Contains(Path);
		}
		TestTrue(FString::Printf(TEXT("%s: the union of the plans' required paths is exactly the 51 independent literal paths, each named by exactly one plan"), *Who), bUnion);
		// The selected phase decides the phase paths: no default first or last phase.
		TestTrue(FString::Printf(TEXT("%s: the selected phase paths are named and the other phase's are not"), *Who),
			Union.Contains(FString::Printf(TEXT("Phases[%s].EntryHealthFraction"), *Selected.ToString())) && !Union.Contains(FString::Printf(TEXT("Phases[%s].EntryHealthFraction"), *Other.ToString())));
	}
	TestTrue(TEXT("each boss keeps its own config lease and phase: the configs are retained independently"), Plan->Participants[0].Config.Get() == F.BossConfig.Get() && Plan->Participants[1].Config.Get() == Boss2Config.Get()
		&& Plan->Participants[0].Config->Phases.Num() == 1 && Plan->Participants[0].Config->Phases[0].PhaseId == PhaseTwo && Plan->Participants[1].Config->Phases.Num() == 1 && Plan->Participants[1].Config->Phases[0].PhaseId == PhaseAlt
		&& Plan->Participants[0].Config->Stats.MaxHealth != Plan->Participants[1].Config->Stats.MaxHealth);
	TestTrue(TEXT("the target-only member has no plan and no class lease"), Plan->Participants[2].Role == ERPGPreflightRole::TargetOnly && Plan->Participants[2].Plans.IsEmpty() && Plan->Participants[2].ClassLeases.IsEmpty());

	// A second compile of the same input gives the same classes, names, order and required fields, as a different object.
	FPlanPtr Again;
	TestTrue(TEXT("second compile"), RPGBossHydrationPreflight::CompilePreflight(Input, Again).IsReady() && Again.IsValid() && Again.Get() != Plan.Get() && Again->Participants.Num() == 3);
	if (Again.IsValid() && Again->Participants.Num() == 3)
	{
		bool bStable = true;
		for (int32 Member = 0; Member < 2; ++Member)
		{
			bStable = bStable && Again->Participants[Member].Plans.Num() == 5;
			for (int32 Index = 0; bStable && Index < 5; ++Index)
			{
				bStable = bStable && Again->Participants[Member].Plans[Index].Class == Plan->Participants[Member].Plans[Index].Class
					&& Again->Participants[Member].Plans[Index].InstanceName == Plan->Participants[Member].Plans[Index].InstanceName
					&& Again->Participants[Member].Plans[Index].RequiredFields == Plan->Participants[Member].Plans[Index].RequiredFields;
			}
		}
		TestTrue(TEXT("the second compile has the same order, classes, names and required fields"), bStable);
	}

	// A success touches nothing: no component (no Stagger or DormantWake either), no begun actor, no bound or ready context.
	TestTrue(TEXT("compiling changed no actor, component or combat context"), CaptureState(F.Scope.World) == Before);
	bool bNoConsumers = true;
	for (UClass* Class : RPGBossHydrationPreflight::ManagedCoreConsumerClasses())
	{
		bNoConsumers = bNoConsumers && !F.Boss->FindComponentByClass(Class) && !Boss2->FindComponentByClass(Class) && !F.Player->FindComponentByClass(Class);
	}
	TestTrue(TEXT("no managed consumer (no Stagger, DormantWake, Phases, Encounter, Posture or participant component) exists on any actor"), bNoConsumers);
	TestTrue(TEXT("the managed consumers are the six expected classes"), RPGBossHydrationPreflight::ManagedCoreConsumerClasses().Num() == 6);

	AddInfo(TEXT("Expanded native subset: a plan order only (NOT a BeginPlay chronology), structural soft references (NOT production fit, load or cook proof), NOT a complete playable bundle, reservation or ready context."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPreflightClustersTest, "OneBossFight.Binding.Preflight.Clusters",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPreflightClustersTest::RunTest(const FString& Parameters)
{
	FFixture F;
	if (!PreconditionOk(*this, F))
	{
		return false;
	}
	const FConfigSpec Base = DefaultSpec(F.Content);
	const auto WithMutation = [&](const TFunction<void(FRPGParticipantConfig&)>& Mutate)
	{
		FRPGHydrationPreflightInput In = F.Valid;
		In.Requests[0].Config = BuildConfigWith(Base, Mutate);
		return In;
	};
	{
		FPlanPtr Out;
		TestTrue(TEXT("control: the hand-built boss config with every new record at its authoring default is accepted"), RPGBossHydrationPreflight::CompilePreflight(WithMutation(TFunction<void(FRPGParticipantConfig&)>()), Out).IsReady() && Out.IsValid());
	}
	const auto MissingPath = []() { return FSoftObjectPath(); };
	const auto BadPath = []() { return FSoftObjectPath(FTopLevelAssetPath(FName(TEXT("/SyntheticMount/A B")), FName(TEXT("AN_X"))), FString()); };

	// Each newly integrated cluster, with every other record valid: the accepted validator's own named failure is carried, the earlier good output is cleared and nothing in the world changes.
	ExpectRejected(*this, F, TEXT("stagger policy: a divisor field at 0"), WithMutation([](FRPGParticipantConfig& C) { C.StaggerPolicy.GetUpRate = 0.f; }), TEXT("Preflight.StaggerRejected"), TEXT("InvalidStagger.NotPositive"));
	ExpectRejected(*this, F, TEXT("stagger policy: a backend capability the generic compiler accepts (critical multiplier below 1)"), WithMutation([](FRPGParticipantConfig& C) { C.StaggerPolicy.CriticalMultiplier = 0.5f; }), TEXT("Preflight.StaggerRejected"), TEXT("UnsupportedNativeCritical"));
	ExpectRejected(*this, F, TEXT("stagger profile: no hit stun class"), WithMutation([](FRPGParticipantConfig& C) { C.StaggerProfile.HitStunAbilityClassName = NAME_None; }), TEXT("Preflight.StaggerRejected"), TEXT("InvalidStaggerProfile.NoHitStunClass"));
	ExpectRejected(*this, F, TEXT("stagger profile: a required clip missing while clips are used"), WithMutation([](FRPGParticipantConfig& C) { C.StaggerProfile.FallClip = TSoftObjectPtr<UAnimSequence>(); }), TEXT("Preflight.StaggerRejected"), TEXT("StaggerProfile.FallClip"));
	ExpectRejected(*this, F, TEXT("phase flow: no leap tag"), WithMutation([](FRPGParticipantConfig& C) { C.PhaseFlow.LeapAbilityTag = NAME_None; }), TEXT("Preflight.PhaseRejected"), TEXT("InvalidPhaseFlow.NoLeapTag"));
	ExpectRejected(*this, F, TEXT("fireball: an inverted cooldown"), WithMutation([](FRPGParticipantConfig& C) { C.Fireball.FireballCooldown = FVector2D(5.0, 4.0); }), TEXT("Preflight.PhaseRejected"), TEXT("InvalidFireball.CooldownOrder"));
	ExpectRejected(*this, F, TEXT("phase dependencies: no immunity effect"), WithMutation([](FRPGParticipantConfig& C) { C.PhaseDependencies.ImmunityEffect = TSoftClassPtr<UObject>(); }), TEXT("Preflight.PhaseRejected"), TEXT("PhaseDependencies.ImmunityEffect"));
	// The encounter cluster: a VALID stats record with an invalid policy, and an invalid stats record with a valid policy, each caught (so a premature or one-sided check would be found).
	ExpectRejected(*this, F, TEXT("valid stats with a NaN gate radius"), WithMutation([](FRPGParticipantConfig& C) { C.EncounterPolicy.GateRadius = std::numeric_limits<float>::quiet_NaN(); }), TEXT("Preflight.EncounterPolicyRejected"), TEXT("InvalidPolicy.NotFinite"));
	ExpectRejected(*this, F, TEXT("valid stats with a negative gate radius"), WithMutation([](FRPGParticipantConfig& C) { C.EncounterPolicy.GateRadius = -1.f; }), TEXT("Preflight.EncounterPolicyRejected"), TEXT("InvalidPolicy.Negative"));
	{
		FConfigSpec Spec = Base;
		Spec.Health = 0.5f; // a native capability the generic compiler accepts; the policy of this config is valid
		FRPGHydrationPreflightInput In = F.Valid;
		In.Requests[0].Config = BuildConfig(Spec);
		ExpectRejected(*this, F, TEXT("invalid stats (native health capability) with a valid policy"), In, TEXT("Preflight.StatsRejected"), TEXT("UnsupportedNativeHealthOverride"));
		FConfigSpec Spec2 = Base;
		Spec2.Delay = -1.f; // a posture stat: the complete stats record is validated, not only the health
		In.Requests[0].Config = BuildConfig(Spec2);
		ExpectRejected(*this, F, TEXT("a posture stat invalid (the whole stats record is validated)"), In, TEXT("Preflight.StatsRejected"), TEXT("InvalidStats.Negative"));
	}
	// The dormant wake references.
	ExpectRejected(*this, F, TEXT("dormant wake: no dormant clip"), WithMutation([&](FRPGParticipantConfig& C) { C.DormantWake.DormantClip = TSoftObjectPtr<UAnimSequence>(MissingPath()); }), TEXT("Preflight.DormantWakeRejected"), TEXT("DormantWake.DormantClip"));
	ExpectRejected(*this, F, TEXT("dormant wake: a malformed wake clip path"), WithMutation([&](FRPGParticipantConfig& C) { C.DormantWake.WakeClip = TSoftObjectPtr<UAnimSequence>(BadPath()); }), TEXT("Preflight.DormantWakeRejected"), TEXT("InvalidDependency.Malformed"));

	// Several clusters invalid in one member: all are reported with the member's slot, none is hidden by another.
	{
		FPlanPtr Out = F.PriorPlan;
		const FRPGHydrationResult Several = RPGBossHydrationPreflight::CompilePreflight(WithMutation([&](FRPGParticipantConfig& C)
			{
				C.StaggerProfile.HitStunAbilityClassName = NAME_None;
				C.DormantWake.WakeClip = TSoftObjectPtr<UAnimSequence>(MissingPath());
				C.EncounterPolicy.GateRadius = -2.f;
			}), Out);
		TestTrue(TEXT("a stagger, an encounter policy and a dormant wake failure in one member are all reported with the slot, and nothing is published"),
			!Several.IsReady() && !Out.IsValid() && AnyErrorStartsWith(Several, TEXT("Preflight.StaggerRejected[slot=Boss]")) && AnyErrorStartsWith(Several, TEXT("Preflight.EncounterPolicyRejected[slot=Boss]"))
			&& AnyErrorStartsWith(Several, TEXT("Preflight.DormantWakeRejected[slot=Boss]")));
	}

	// A late invalid last participant: the first boss is completely valid, the second (last boss) has one invalid cluster: the earlier good output is cleared and NOTHING is published, not even for the valid boss.
	{
		AActor* Boss2 = F.Scope.SpawnActor();
		const FName PhaseAlt(TEXT("PhaseAlt"));
		FConfigSpec SpecB = Base;
		SpecB.Phases.Reset();
		SpecB.Phases.Add(MakePhase(PhaseAlt, 0.5f, 2.f, 2.5f, 3.f));
		SpecB.FieldPhaseId = PhaseAlt;
		const FConfigPtr LateConfig = BuildConfigWith(SpecB, [&](FRPGParticipantConfig& C) { C.DormantWake.WakeClip = TSoftObjectPtr<UAnimSequence>(MissingPath()); });
		if (!TestTrue(TEXT("late participant built"), Boss2 && LateConfig.IsValid()))
		{
			return false;
		}
		FRPGHydrationPreflightInput In = F.Valid;
		In.Requests.Insert(MakeRequest(Boss2, TEXT("Boss2"), TEXT("Boss"), ERPGPreflightRole::BossCore, LateConfig, PhaseAlt), 1); // Boss, Boss2 (invalid), Player
		ExpectRejected(*this, F, TEXT("valid first boss, invalid second boss"), In, TEXT("Preflight.DormantWakeRejected"), TEXT("[slot=Boss2]"));
		FPlanPtr Out = F.PriorPlan;
		const FRPGHydrationResult Late = RPGBossHydrationPreflight::CompilePreflight(In, Out);
		TestTrue(TEXT("only the invalid member is named: nothing is reported for the valid first boss and no plan exists for it"), !Late.IsReady() && !Out.IsValid() && !AnyErrorContains(Late, TEXT("[slot=Boss]")) && AnyErrorContains(Late, TEXT("[slot=Boss2]")));
	}

	// Manifest membership: the first and the last path of EACH combined cluster, one at a time (the message names the slot and the path).
	struct FClusterEdge
	{
		const TCHAR* Name;
		const TCHAR* First;
		const TCHAR* Last;
	};
	const FClusterEdge Edges[] = {
		{TEXT("stagger"), TEXT("StaggerPolicy.StaggerSeconds"), TEXT("StaggerProfile.ImmunityEffect")},
		{TEXT("phases"), TEXT("Phases[PhaseTwo].EntryHealthFraction"), TEXT("PhaseDependencies.ImmunityEffect")},
		{TEXT("encounter"), TEXT("Stats.MaxHealth"), TEXT("EncounterPolicy.bResetOnPlayerRespawn")},
		{TEXT("dormant wake"), TEXT("DormantWake.DormantClip"), TEXT("DormantWake.WakeClip")},
		{TEXT("posture"), TEXT("Stats.MaxPosture"), TEXT("Stats.PostureRegenRate")},
	};
	for (const FClusterEdge& Edge : Edges)
	{
		for (const TCHAR* Path : {Edge.First, Edge.Last})
		{
			FConfigSpec Spec = Base;
			Spec.OmitFields.Add(Path);
			FRPGHydrationPreflightInput In = F.Valid;
			In.Requests[0].Config = BuildConfig(Spec);
			ExpectRejected(*this, F, *FString::Printf(TEXT("manifest without the %s path %s"), Edge.Name, Path), In, TEXT("Preflight.MissingRequiredField"), Path);
		}
	}
	// A whole new group missing: every required path of the dormant wake group at once is reported, one failure per path.
	{
		FConfigSpec Spec = Base;
		Spec.OmitFields.Add(TEXT("DormantWake.DormantClip"));
		Spec.OmitFields.Add(TEXT("DormantWake.WakeClip"));
		FRPGHydrationPreflightInput In = F.Valid;
		In.Requests[0].Config = BuildConfig(Spec);
		FPlanPtr Out = F.PriorPlan;
		const FRPGHydrationResult Result = RPGBossHydrationPreflight::CompilePreflight(In, Out);
		TestTrue(TEXT("both dormant wake paths missing: both are named with the slot, nothing published"), !Result.IsReady() && !Out.IsValid() && AnyErrorContains(Result, TEXT("[slot=Boss]: required manifest path DormantWake.DormantClip"))
			&& AnyErrorContains(Result, TEXT("[slot=Boss]: required manifest path DormantWake.WakeClip")));
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPreflightConsumersTest, "OneBossFight.Binding.Preflight.Consumers",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPreflightConsumersTest::RunTest(const FString& Parameters)
{
	FFixture F;
	if (!PreconditionOk(*this, F))
	{
		return false;
	}
	// An ALREADY OWNED Stagger or DormantWake (created on the actor, NOT registered and NOT begun) is refused by name for a boss-core actor, and no member is mutated.
	for (UClass* Class : {URPGBossStagger::StaticClass(), URPGBossDormantWake::StaticClass()})
	{
		AActor* Host = F.Scope.SpawnActor();
		if (!Host)
		{
			AddError(TEXT("unsupported precondition: a host actor could not be spawned"));
			continue;
		}
		UActorComponent* Existing = NewObject<UActorComponent>(Host, Class);
		if (!TestTrue(FString::Printf(TEXT("precondition: %s is owned by the actor, unregistered and not begun"), *Class->GetName()),
			Existing && Host->FindComponentByClass(Class) == Existing && !Existing->IsRegistered() && !Existing->HasBegunPlay() && !Host->HasActorBegunPlay()))
		{
			AddError(TEXT("unsupported precondition: the preexisting consumer could not be attached unregistered"));
			continue;
		}
		const int32 ComponentCount = Host->GetComponents().Num();
		FRPGHydrationPreflightInput In = F.Valid;
		In.Requests[0].Actor = Host;
		ExpectRejected(*this, F, *FString::Printf(TEXT("preexisting unregistered %s on a boss-core actor"), *Class->GetName()), In, TEXT("Preflight.PreexistingConsumer"), *Class->GetName());
		TestTrue(FString::Printf(TEXT("the refused %s is untouched: still owned, still unregistered, still not begun, no component added or removed"), *Class->GetName()),
			Host->FindComponentByClass(Class) == Existing && !Existing->IsRegistered() && !Existing->HasBegunPlay() && Host->GetComponents().Num() == ComponentCount);
	}
	// A boss consumer on a TARGET-ONLY member is not this kernel's business (no boss plan is ever assigned to a target): the batch still compiles, and the component is left alone.
	{
		UActorComponent* OnTarget = NewObject<UActorComponent>(F.Player, URPGBossStagger::StaticClass());
		FPlanPtr Out;
		const FRPGHydrationResult Result = RPGBossHydrationPreflight::CompilePreflight(F.Valid, Out);
		TestTrue(TEXT("a Stagger on the target-only member does not stop the batch; the target gets no boss plan"), Result.IsReady() && Out.IsValid() && Out->Participants.Num() == 2 && Out->Participants[1].Plans.IsEmpty());
		TestTrue(TEXT("and that component is untouched (unregistered, not begun)"), OnTarget && F.Player->FindComponentByClass(URPGBossStagger::StaticClass()) == OnTarget && !OnTarget->IsRegistered() && !OnTarget->HasBegunPlay());
	}

	// Callback binding, confirmed OUTSIDE CompilePreflight and explicitly separate from it: the compile invokes no callback (nothing on the boss actor changes), and afterwards each plan's callback, applied by this test to a
	// fresh isolated component of that plan's class, writes the typed record and refuses a component of the wrong class.
	FPlanPtr Plan;
	const TArray<int32> Before = CaptureState(F.Scope.World);
	const int32 BossComponentsBefore = F.Boss->GetComponents().Num();
	if (!TestTrue(TEXT("the batch compiles"), RPGBossHydrationPreflight::CompilePreflight(F.Valid, Plan).IsReady() && Plan.IsValid() && Plan->Participants.Num() == 2 && Plan->Participants[0].Plans.Num() == 5))
	{
		return false;
	}
	TestTrue(TEXT("no component was added to the boss actor and nothing in the world changed by the compile (a state check: the kernel holds no component to hand to a callback, so this is not an instrumentation of the callbacks)"), CaptureState(F.Scope.World) == Before && F.Boss->GetComponents().Num() == BossComponentsBefore);
	const FRPGPreflightParticipantPlan& BossPlan = Plan->Participants[0];
	for (int32 Index = 0; Index < BossPlan.Plans.Num(); ++Index)
	{
		AActor* Host = F.Scope.SpawnActor();
		if (!Host)
		{
			AddError(TEXT("unsupported precondition: a host actor could not be spawned"));
			continue;
		}
		UActorComponent* Fresh = NewObject<UActorComponent>(Host, BossPlan.Plans[Index].Class);
		URPGBossStagger* AsStagger = Cast<URPGBossStagger>(Fresh);
		URPGBossPhases* AsPhases = Cast<URPGBossPhases>(Fresh);
		URPGBossEncounter* AsEncounter = Cast<URPGBossEncounter>(Fresh);
		URPGBossPosture* AsPosture = Cast<URPGBossPosture>(Fresh);
		if (AsStagger) { AsStagger->StaggerSeconds = 99.f; }
		if (AsPhases) { AsPhases->PhaseTwoHealthFraction = 0.9f; }
		if (AsEncounter) { AsEncounter->BossMaxHealth = 111.f; }
		if (AsPosture) { AsPosture->PostureMax = 222.f; }
		FString Error = TEXT("a stale diagnostic");
		const FString Label = BossPlan.Plans[Index].Class->GetName();
		TestTrue(FString::Printf(TEXT("%s: the plan's callback (applied outside the compile) accepts a fresh isolated component of its class and clears the diagnostic"), *Label), Fresh && BossPlan.Plans[Index].Configure(*Fresh, *F.BossConfig, Error) && Error.IsEmpty());
		TestTrue(FString::Printf(TEXT("%s: the typed record of the config was written (and the component is still unregistered and not begun)"), *Label),
			Fresh && !Fresh->IsRegistered() && !Fresh->HasBegunPlay()
			&& (!AsStagger || AsStagger->StaggerSeconds == F.BossConfig->StaggerPolicy.StaggerSeconds) && (!AsPhases || AsPhases->PhaseTwoHealthFraction == 0.35f)
			&& (!AsEncounter || AsEncounter->BossMaxHealth == 3500.f) && (!AsPosture || AsPosture->PostureMax == 73.5f));
		TStrongObjectPtr<USceneComponent> Wrong(NewObject<USceneComponent>(Host, TEXT("WrongClass")));
		FString WrongError;
		TestTrue(FString::Printf(TEXT("%s: the callback refuses a component of the wrong class by name"), *Label), Wrong.IsValid() && !BossPlan.Plans[Index].Configure(*Wrong, *F.BossConfig, WrongError) && WrongError.StartsWith(TEXT("WrongComponentClass")));
	}
	AddInfo(TEXT("The binding check observes one value per plan (stagger seconds, the phase threshold, the boss health, the posture maximum); the dormant wake fields are private, so only acceptance and the wrong-class refusal are observable. PlanInvalid cannot be provoked with the fixed factories and has no negative test."));
	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
