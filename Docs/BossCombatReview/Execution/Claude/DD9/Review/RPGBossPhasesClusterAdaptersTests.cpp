// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Animation/AnimMontage.h"
#include "Animation/AnimSequence.h"
#include "Components/SceneComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossPhaseAdapters.h"
#include "Player/RPGBossPhaseFlowAdapters.h"
#include "Player/RPGBossPhases.h"
#include "Player/RPGBossPhasesClusterAdapters.h"
#include "Player/RPGBossPosture.h"
#include "UObject/Class.h"
#include "UObject/Package.h"
#include "UObject/SoftObjectPath.h"
#include "UObject/StrongObjectPtr.h"
#include "UObject/UnrealType.h"
#include <limits>

// These tests prove the combined phases cluster: its two new reflected records (fireball policy, dependency references), their copy into the immutable config by the real definition compiler (synthetic path, and
// the production path's early rejection), the shared validators, and the typed, lifecycle-safe, atomic assignment of all eighteen authoring fields on an isolated native component, compared with the sequential use of
// the two older adapters as an oracle. They do NOT prove a serialized asset value, anything seen in the Details panel, a production compile with a real skeleton, that any referenced asset exists, is cooked, is the
// right class or fits the transition time (paths are checked for structure only, with no registry query), a real phase transition, a real fireball, or any wiring. The defaults are the documented defaults of the new
// asset fields, compared with the native constructor values only as a baseline. No Phases tick or transition runs here; the one BeginPlay that runs (the begun-component guard) loads nothing because the three soft
// asset pointers it would load are cleared first.

namespace
{
namespace PhasesClusterTests
{
	using FEpochPtr = TSharedPtr<const RPGCombatRegistry::FEpoch>;
	using FConfigPtr = TSharedPtr<const FRPGParticipantConfig>;

	constexpr double QuietNaN = std::numeric_limits<double>::quiet_NaN();
	constexpr double PosInf = std::numeric_limits<double>::infinity();

	/** Test-local game world with the set-up the earlier headless tests used; destroyed with the scope. */
	struct FClusterTestWorld
	{
		UWorld* World = nullptr;

		FClusterTestWorld()
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

		~FClusterTestWorld()
		{
			if (World)
			{
				GEngine->DestroyWorldContext(World);
				World->DestroyWorld(/*bInformEngineOfWorld=*/false);
			}
		}

		FClusterTestWorld(const FClusterTestWorld&) = delete;
		FClusterTestWorld& operator=(const FClusterTestWorld&) = delete;

		AActor* SpawnOwner() const { return World ? World->SpawnActor<AActor>() : nullptr; }
	};

	/** A soft path built from its parts, so that deliberately malformed forms are never parsed from text (no engine log, no repair). */
	FSoftObjectPath MakePath(const TCHAR* Package, const TCHAR* Asset, const TCHAR* Sub = TEXT(""))
	{
		return FSoftObjectPath(FTopLevelAssetPath(FName(Package), FName(Asset)), FString(Sub));
	}

	TSoftObjectPtr<UAnimSequence> SequencePtr(const FSoftObjectPath& P) { return TSoftObjectPtr<UAnimSequence>(P); }
	TSoftObjectPtr<UAnimMontage> MontagePtr(const FSoftObjectPath& P) { return TSoftObjectPtr<UAnimMontage>(P); }
	TSoftClassPtr<UObject> ClassPtr(const FSoftObjectPath& P) { return TSoftClassPtr<UObject>(P); }

	/** All eighteen authoring fields and the public runtime state of a phases component, with an exact (case-sensitive string) comparison. */
	struct FClusterState
	{
		float PhaseTwoHealthFraction, MovementScale, AttackRateScale, DamageScale;
		float TransitionSeconds;
		bool bUseRoarClip, bPausePostureInTransition, bLockLeapUntilPhaseTwo;
		FString AttackAbilityPrefix;
		FName LeapAbilityTag;
		bool bFireballEnabled;
		FSoftObjectPath FireballAbility, RoarClip, TransitionMontage, ImmunityEffect;
		FVector2D FireballCooldown;
		float FireballMinRange, FireballMaxRange;
		FString RoarSourceName;
		bool bLeapBlocked, bPhaseTwo, bInTransition;
		int32 FireballCount, PhaseTwoCount, QueuedStarts;
		double LastTransitionStart;

		explicit FClusterState(const URPGBossPhases& P)
			: PhaseTwoHealthFraction(P.PhaseTwoHealthFraction), MovementScale(P.MovementScale), AttackRateScale(P.AttackRateScale), DamageScale(P.DamageScale)
			, TransitionSeconds(P.TransitionSeconds), bUseRoarClip(P.bUseRoarClip), bPausePostureInTransition(P.bPausePostureInTransition), bLockLeapUntilPhaseTwo(P.bLockLeapUntilPhaseTwo)
			, AttackAbilityPrefix(P.AttackAbilityPrefix), LeapAbilityTag(P.LeapAbilityTag), bFireballEnabled(P.bFireballEnabled)
			, FireballAbility(P.FireballAbility.ToSoftObjectPath()), RoarClip(P.RoarClip.ToSoftObjectPath()), TransitionMontage(P.TransitionMontage.ToSoftObjectPath()), ImmunityEffect(P.ImmunityEffect.ToSoftObjectPath())
			, FireballCooldown(P.FireballCooldown), FireballMinRange(P.FireballMinRange), FireballMaxRange(P.FireballMaxRange)
			, RoarSourceName(P.GetRoarSourceName()), bLeapBlocked(P.IsLeapBlocked()), bPhaseTwo(P.IsPhaseTwo()), bInTransition(P.IsInTransition()), FireballCount(P.GetFireballCount())
			, PhaseTwoCount(P.GetPhaseTwoCount()), QueuedStarts(P.GetQueuedStartCount()), LastTransitionStart(P.GetLastTransitionStartTime())
		{
		}

		/** The ten fields the older two adapters own (selected phase and flow). */
		bool PhaseAndFlowEquals(const FClusterState& O) const
		{
			return PhaseTwoHealthFraction == O.PhaseTwoHealthFraction && MovementScale == O.MovementScale && AttackRateScale == O.AttackRateScale && DamageScale == O.DamageScale
				&& TransitionSeconds == O.TransitionSeconds && bUseRoarClip == O.bUseRoarClip && bPausePostureInTransition == O.bPausePostureInTransition && bLockLeapUntilPhaseTwo == O.bLockLeapUntilPhaseTwo
				&& AttackAbilityPrefix.Equals(O.AttackAbilityPrefix, ESearchCase::CaseSensitive) && LeapAbilityTag == O.LeapAbilityTag;
		}

		/** The eight new fields (fireball and dependencies). */
		bool FireballAndDependenciesEqual(const FClusterState& O) const
		{
			return bFireballEnabled == O.bFireballEnabled && FireballAbility == O.FireballAbility && FireballCooldown == O.FireballCooldown && FireballMinRange == O.FireballMinRange
				&& FireballMaxRange == O.FireballMaxRange && RoarClip == O.RoarClip && TransitionMontage == O.TransitionMontage && ImmunityEffect == O.ImmunityEffect;
		}

		bool RuntimeEquals(const FClusterState& O) const
		{
			return RoarSourceName.Equals(O.RoarSourceName, ESearchCase::CaseSensitive) && bLeapBlocked == O.bLeapBlocked && bPhaseTwo == O.bPhaseTwo && bInTransition == O.bInTransition
				&& FireballCount == O.FireballCount && PhaseTwoCount == O.PhaseTwoCount && QueuedStarts == O.QueuedStarts && LastTransitionStart == O.LastTransitionStart;
		}

		bool operator==(const FClusterState& O) const { return PhaseAndFlowEquals(O) && FireballAndDependenciesEqual(O) && RuntimeEquals(O); }
	};

	/** The selected phase of every config below. */
	const FName SelectedId(TEXT("PhaseTwo"));

	FRPGPhaseConfig MakePhase(float Entry, float Speed, float Rate, float Attack)
	{
		FRPGPhaseConfig Phase;
		Phase.PhaseId = SelectedId;
		Phase.EntryHealthFraction = Entry;
		Phase.SpeedMultiplier = Speed;
		Phase.RateMultiplier = Rate;
		Phase.AttackMultiplier = Attack;
		return Phase;
	}

	/** Config A: every one of the 18 fields differs from the authoring defaults; the roar clip is used and a fireball is enabled. */
	FRPGParticipantConfig ConfigA()
	{
		FRPGParticipantConfig C;
		C.Phases.Add(MakePhase(0.35f, 1.5f, 1.75f, 2.f));
		C.PhaseFlow.TransitionSeconds = 2.75f;
		C.PhaseFlow.bUseRoarClip = true;
		C.PhaseFlow.bPausePostureInTransition = false;
		C.PhaseFlow.bLockLeapUntilPhaseTwo = false;
		C.PhaseFlow.AttackAbilityPrefix = TEXT("GA_Custom_Boss_");
		C.PhaseFlow.LeapAbilityTag = TEXT("Custom.Leap.Tag");
		C.Fireball.bFireballEnabled = true;
		C.Fireball.FireballAbility = ClassPtr(MakePath(TEXT("/SyntheticMount/Test/Custom/GA_TestFireball"), TEXT("GA_TestFireball_C")));
		C.Fireball.FireballCooldown = FVector2D(2.0, 3.0);
		C.Fireball.FireballMinRange = 111.f;
		C.Fireball.FireballMaxRange = 999.f;
		C.PhaseDependencies.RoarClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Test/Custom/AN_TestRoar"), TEXT("AN_TestRoar")));
		C.PhaseDependencies.TransitionMontage = MontagePtr(MakePath(TEXT("/SyntheticMount/Test/Custom/AM_TestIntro"), TEXT("AM_TestIntro")));
		C.PhaseDependencies.ImmunityEffect = ClassPtr(MakePath(TEXT("/SyntheticMount/Test/Custom/GE_TestImmune"), TEXT("GE_TestImmune_C")));
		return C;
	}

	/** Config B: the other truth values and edge values: the montage is the roar (no clip), zero duration, a spaced prefix and an unregistered tag, the fireball disabled with no ability and zero windows. */
	FRPGParticipantConfig ConfigB()
	{
		FRPGParticipantConfig C;
		C.Phases.Add(MakePhase(1.f, 3.25f, 4.5f, 1.f));
		C.PhaseFlow.TransitionSeconds = 0.f;
		C.PhaseFlow.bUseRoarClip = false;
		C.PhaseFlow.bPausePostureInTransition = true;
		C.PhaseFlow.bLockLeapUntilPhaseTwo = true;
		C.PhaseFlow.AttackAbilityPrefix = TEXT(" GA_Spaced_ ");
		C.PhaseFlow.LeapAbilityTag = TEXT("Never.Registered.Test.Tag");
		C.Fireball.bFireballEnabled = false;
		C.Fireball.FireballAbility = ClassPtr(FSoftObjectPath());
		C.Fireball.FireballCooldown = FVector2D(0.0, 0.0);
		C.Fireball.FireballMinRange = 0.f;
		C.Fireball.FireballMaxRange = 0.f;
		C.PhaseDependencies.RoarClip = SequencePtr(FSoftObjectPath());
		C.PhaseDependencies.TransitionMontage = MontagePtr(MakePath(TEXT("/SyntheticMount/Test/Other/AM_OtherIntro"), TEXT("AM_OtherIntro")));
		C.PhaseDependencies.ImmunityEffect = ClassPtr(MakePath(TEXT("/SyntheticMount/Test/Other/GE_OtherImmune"), TEXT("GE_OtherImmune_C")));
		return C;
	}

	FRPGParityField MakeField(const FString& Path, const FString& ValueText)
	{
		FRPGParityField Field;
		Field.FieldPath = Path;
		Field.Type = TEXT("float");
		Field.Value = ValueText;
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

	/** A valid definition for the real synthetic compiler built from a config (phases, flow, fireball, dependencies). */
	TStrongObjectPtr<URPGBossDefinition> MakeDefinition(const FRPGParticipantConfig& C)
	{
		TStrongObjectPtr<URPGBossDefinition> Definition(NewObject<URPGBossDefinition>());
		Definition->DefinitionId = TEXT("Synthetic");
		Definition->PresentationId = TEXT("SyntheticLook");
		Definition->Stats.MaxHealth = 3500.f;
		Definition->Stats.MaxPosture = 73.5f;
		Definition->Stats.PostureRegenDelay = 4.25f;
		Definition->Stats.PostureRegenRate = 9.75f;
		Definition->Phases = C.Phases;
		Definition->PhaseFlow = C.PhaseFlow;
		Definition->Fireball = C.Fireball;
		Definition->PhaseDependencies = C.PhaseDependencies;
		Definition->Fields.Add(MakeField(RPGBossPhasesClusterAdapters::FieldFireballCooldown, TEXT("synthetic")));
		Definition->Fields.Add(MakeField(RPGBossPhasesClusterAdapters::FieldImmunityEffect, TEXT("synthetic")));
		Definition->Fields.Add(MakeField(TEXT("Stats.MaxHealth"), TEXT("synthetic")));
		return Definition;
	}

	FRPGHydrationResult CompileSynthetic(const URPGBossDefinition& Definition, FEpochPtr Content, FConfigPtr& Out, const FString& Hash = FString::ChrN(64, TEXT('b')))
	{
		return RPGCombatHydration::CompileSyntheticParticipant(Definition, Content, Hash, Out);
	}

	bool AnyErrorContains(const FRPGHydrationResult& Result, const TCHAR* Text)
	{
		return Result.Errors.ContainsByPredicate([Text](const FString& E) { return E.Contains(Text); });
	}

	TStrongObjectPtr<URPGBossPhases> NewPhases(AActor* Owner, const TCHAR* Name)
	{
		return TStrongObjectPtr<URPGBossPhases>(NewObject<URPGBossPhases>(Owner, Name));
	}

	/** Runtime-state sentinels cannot be armed (they are private); the authoring fields are all written by the cluster, so a distinct starting state is made by writing the opposite values. */
	void ArmDistinctStart(URPGBossPhases& P)
	{
		P.PhaseTwoHealthFraction = 0.42f;
		P.MovementScale = 1.7f;
		P.AttackRateScale = 1.8f;
		P.DamageScale = 1.9f;
		P.TransitionSeconds = 7.f;
		P.bUseRoarClip = !ConfigA().PhaseFlow.bUseRoarClip;
		P.bFireballEnabled = !ConfigA().Fireball.bFireballEnabled;
		P.FireballCooldown = FVector2D(30.0, 40.0);
		P.FireballMinRange = 70.f;
		P.FireballMaxRange = 80.f;
		P.AttackAbilityPrefix = TEXT("START_");
		P.LeapAbilityTag = TEXT("Start.Tag");
		P.RoarClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Test/Start/AN_Start"), TEXT("AN_Start")));
		P.TransitionMontage = MontagePtr(MakePath(TEXT("/SyntheticMount/Test/Start/AM_Start"), TEXT("AM_Start")));
		P.ImmunityEffect = ClassPtr(MakePath(TEXT("/SyntheticMount/Test/Start/GE_Start"), TEXT("GE_Start_C")));
		P.FireballAbility = ClassPtr(MakePath(TEXT("/SyntheticMount/Test/Start/GA_Start"), TEXT("GA_Start_C")));
	}
}
}

// No file-scope using-directive on purpose: each test body names its namespace itself.

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPhasesClusterAssignTest, "OneBossFight.Binding.PhasesCluster.Assign",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPhasesClusterAssignTest::RunTest(const FString& Parameters)
{
	using namespace PhasesClusterTests;
	FClusterTestWorld Scope;
	if (!TestNotNull(TEXT("test world"), Scope.World))
	{
		return false;
	}
	AActor* Owner = Scope.SpawnOwner();
	if (!TestNotNull(TEXT("owner actor"), Owner))
	{
		return false;
	}
	TStrongObjectPtr<URPGBossPhases> Phases = NewPhases(Owner, TEXT("RPGBossPhases"));
	if (!TestTrue(TEXT("component created"), Phases.IsValid()))
	{
		return false;
	}
	ArmDistinctStart(*Phases);
	const FClusterState Before(*Phases);
	const int32 OwnedComponentsBefore = Owner->GetComponents().Num();

	// The unwired plan fragment: legacy instance name, exact class, the 18 typed paths in the documented order; with no selection only the 14 that do not depend on it.
	FName Selected = SelectedId;
	const FRPGComponentPlan Plan = RPGBossPhasesClusterAdapters::MakePhasesClusterPlan(Selected);
	Selected = FName(TEXT("ChangedAfterwards")); // the id is captured by value
	TestTrue(TEXT("plan class"), Plan.Class == URPGBossPhases::StaticClass());
	TestTrue(TEXT("plan instance name"), Plan.InstanceName == FName(TEXT("RPGBossPhases")));
	const TArray<FString> ExpectedFields = {
		TEXT("Phases[PhaseTwo].EntryHealthFraction"), TEXT("Phases[PhaseTwo].SpeedMultiplier"), TEXT("Phases[PhaseTwo].RateMultiplier"), TEXT("Phases[PhaseTwo].AttackMultiplier"),
		TEXT("PhaseFlow.TransitionSeconds"), TEXT("PhaseFlow.bUseRoarClip"), TEXT("PhaseFlow.bPausePostureInTransition"), TEXT("PhaseFlow.bLockLeapUntilPhaseTwo"), TEXT("PhaseFlow.AttackAbilityPrefix"), TEXT("PhaseFlow.LeapAbilityTag"),
		TEXT("Fireball.bFireballEnabled"), TEXT("Fireball.FireballAbility"), TEXT("Fireball.FireballCooldown"), TEXT("Fireball.FireballMinRange"), TEXT("Fireball.FireballMaxRange"),
		TEXT("PhaseDependencies.RoarClip"), TEXT("PhaseDependencies.TransitionMontage"), TEXT("PhaseDependencies.ImmunityEffect")};
	TestTrue(TEXT("plan required fields are the 18 typed paths in order"), Plan.RequiredFields == ExpectedFields);
	const FRPGComponentPlan NoSelectionPlan = RPGBossPhasesClusterAdapters::MakePhasesClusterPlan(NAME_None);
	TestTrue(TEXT("no selection: the 14 independent paths only"), NoSelectionPlan.RequiredFields.Num() == 14 && NoSelectionPlan.RequiredFields[0] == TEXT("PhaseFlow.TransitionSeconds"));
	if (!TestTrue(TEXT("plan callback is set"), static_cast<bool>(Plan.Configure)))
	{
		return false;
	}

	// Config A through the plan callback, with manifest Value text that says something else: only the typed records count.
	FRPGParticipantConfig Config = ConfigA();
	Config.Fields.Add(MakeField(RPGBossPhasesClusterAdapters::FieldFireballCooldown, TEXT("9999")));
	Config.Fields.Add(MakeField(RPGBossPhasesClusterAdapters::FieldImmunityEffect, TEXT("/SyntheticMount/FromTheManifest.FromTheManifest_C")));
	FString Error = TEXT("a stale diagnostic from an earlier call");
	TestTrue(TEXT("callback succeeds"), Plan.Configure(*Phases, Config, Error));
	TestTrue(TEXT("the diagnostic was cleared on success"), Error.IsEmpty());
	const FClusterState After(*Phases);
	TestTrue(TEXT("selected phase assigned (threshold and three multipliers)"), After.PhaseTwoHealthFraction == 0.35f && After.MovementScale == 1.5f && After.AttackRateScale == 1.75f && After.DamageScale == 2.f);
	TestTrue(TEXT("phase flow assigned (duration, three bools, prefix exactly, tag)"), After.TransitionSeconds == 2.75f && After.bUseRoarClip && !After.bPausePostureInTransition && !After.bLockLeapUntilPhaseTwo
		&& After.AttackAbilityPrefix.Equals(TEXT("GA_Custom_Boss_"), ESearchCase::CaseSensitive) && After.LeapAbilityTag == FName(TEXT("Custom.Leap.Tag")));
	TestTrue(TEXT("fireball assigned (enable, ability path, cooldown pair, both ranges)"), After.bFireballEnabled && After.FireballAbility == Config.Fireball.FireballAbility.ToSoftObjectPath()
		&& After.FireballCooldown == FVector2D(2.0, 3.0) && After.FireballMinRange == 111.f && After.FireballMaxRange == 999.f);
	TestTrue(TEXT("the three dependency references assigned as soft paths, the manifest text ignored"), After.RoarClip == Config.PhaseDependencies.RoarClip.ToSoftObjectPath()
		&& After.TransitionMontage == Config.PhaseDependencies.TransitionMontage.ToSoftObjectPath() && After.ImmunityEffect == Config.PhaseDependencies.ImmunityEffect.ToSoftObjectPath());
	TestFalse(TEXT("both groups (selected phase and flow, fireball and dependencies) differ from the distinct start state"), After.PhaseAndFlowEquals(Before) || After.FireballAndDependenciesEqual(Before));
	TestTrue(TEXT("the public runtime state is unchanged"), After.RuntimeEquals(Before));
	TestFalse(TEXT("no phase trigger: not phase two, not in transition, leap not blocked by this call"), Phases->IsPhaseTwo() || Phases->IsInTransition() || Phases->IsLeapBlocked());

	// Nothing created, registered or begun.
	TestFalse(TEXT("component stays unregistered"), Phases->IsRegistered());
	TestFalse(TEXT("component did not begin play"), Phases->HasBegunPlay());
	TestFalse(TEXT("owner did not begin play"), Owner->HasActorBegunPlay());
	TestTrue(TEXT("owner gained no component"), Owner->GetComponents().Num() == OwnedComponentsBefore);

	// Config B directly: zero duration, no clip, a spaced prefix, an unregistered tag, a disabled fireball without an ability and zero windows are all valid and stored as authored.
	const FRPGParticipantConfig B = ConfigB();
	TestTrue(TEXT("config B"), RPGBossPhasesClusterAdapters::ConfigurePhasesCluster(*Phases, B, SelectedId, Error) && Error.IsEmpty());
	const FClusterState AfterB(*Phases);
	TestTrue(TEXT("B: edge values stored as authored"), AfterB.TransitionSeconds == 0.f && !AfterB.bUseRoarClip && AfterB.AttackAbilityPrefix.Equals(TEXT(" GA_Spaced_ "), ESearchCase::CaseSensitive)
		&& AfterB.LeapAbilityTag == FName(TEXT("Never.Registered.Test.Tag")) && !AfterB.bFireballEnabled && AfterB.FireballAbility.IsNull() && AfterB.FireballCooldown == FVector2D(0.0, 0.0)
		&& AfterB.FireballMinRange == 0.f && AfterB.FireballMaxRange == 0.f && AfterB.RoarClip.IsNull() && AfterB.TransitionMontage == B.PhaseDependencies.TransitionMontage.ToSoftObjectPath());
	TestTrue(TEXT("B: runtime state still unchanged"), AfterB.RuntimeEquals(Before));

	// The id captured by value: the plan made from "PhaseTwo" still configures PhaseTwo although the caller's variable changed; a plan for a missing id fails by name and writes nothing.
	const FClusterState BeforeMissing(*Phases);
	const FRPGComponentPlan MissingPlan = RPGBossPhasesClusterAdapters::MakePhasesClusterPlan(FName(TEXT("NoSuchPhase")));
	TestFalse(TEXT("a plan for an id that is not in the record fails"), MissingPlan.Configure(*Phases, ConfigA(), Error));
	TestTrue(TEXT("named InvalidPhase.NotFound or UnsupportedNativePhaseSet"), Error.StartsWith(TEXT("InvalidPhase.NotFound")) || Error.StartsWith(TEXT("UnsupportedNativePhaseSet")));
	TestTrue(TEXT("and nothing was written"), FClusterState(*Phases) == BeforeMissing);

	AddInfo(TEXT("Typed cluster assignment only; NOT a phase transition, NOT a fireball, NOT asset existence or cooking, NOT a serialized asset value, NOT a duel."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPhasesClusterValidationTest, "OneBossFight.Binding.PhasesCluster.Validation",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPhasesClusterValidationTest::RunTest(const FString& Parameters)
{
	using namespace PhasesClusterTests;
	FClusterTestWorld Scope;
	if (!TestNotNull(TEXT("test world"), Scope.World))
	{
		return false;
	}
	AActor* Owner = Scope.SpawnOwner();
	if (!TestNotNull(TEXT("owner actor"), Owner))
	{
		return false;
	}
	TStrongObjectPtr<URPGBossPhases> Phases = NewPhases(Owner, TEXT("RPGBossPhases"));
	if (!TestTrue(TEXT("component created"), Phases.IsValid()))
	{
		return false;
	}
	ArmDistinctStart(*Phases);
	const FClusterState Before(*Phases);

	// One whole-cluster check: the cluster validator and the assignment both refuse (or accept) with the same token and field path, and a refusal writes NOTHING (all 18 fields and the state equal the start state).
	auto Check = [&](const FString& Label, const FRPGParticipantConfig& Config, const TCHAR* ExpectedToken, const FString& ExpectedPath)
	{
		FString Error = TEXT("a stale diagnostic");
		const bool bOk = RPGBossPhasesClusterAdapters::ValidatePhasesCluster(Config, SelectedId, Error);
		if (!ExpectedToken)
		{
			TestTrue(FString::Printf(TEXT("%s: valid, and the diagnostic was cleared"), *Label), bOk && Error.IsEmpty());
			return;
		}
		TestFalse(FString::Printf(TEXT("%s: rejected"), *Label), bOk);
		TestTrue(FString::Printf(TEXT("%s: named %s (got '%s')"), *Label, ExpectedToken, *Error), Error.StartsWith(ExpectedToken));
		TestTrue(FString::Printf(TEXT("%s: names the field %s"), *Label, *ExpectedPath), Error.Contains(ExpectedPath));
		FString ConfigureError = TEXT("a stale diagnostic");
		TestFalse(FString::Printf(TEXT("%s: the assignment refuses"), *Label), RPGBossPhasesClusterAdapters::ConfigurePhasesCluster(*Phases, Config, SelectedId, ConfigureError));
		TestTrue(FString::Printf(TEXT("%s: the assignment names the same token"), *Label), ConfigureError.StartsWith(ExpectedToken));
		TestTrue(FString::Printf(TEXT("%s: no write at all (18 fields and state)"), *Label), FClusterState(*Phases) == Before);
	};
	const FString CooldownPath = RPGBossPhasesClusterAdapters::FieldFireballCooldown;
	const FString MinRangePath = RPGBossPhasesClusterAdapters::FieldFireballMinRange;
	const FString MaxRangePath = RPGBossPhasesClusterAdapters::FieldFireballMaxRange;
	const FString AbilityPath = RPGBossPhasesClusterAdapters::FieldFireballAbility;
	const FString RoarPath = RPGBossPhasesClusterAdapters::FieldRoarClip;
	const FString MontagePath = RPGBossPhasesClusterAdapters::FieldTransitionMontage;
	const FString ImmunityPath = RPGBossPhasesClusterAdapters::FieldImmunityEffect;
	auto Fire = [](TFunction<void(FRPGFireballConfig&)> Edit) { FRPGParticipantConfig C = ConfigA(); Edit(C.Fireball); return C; };
	auto Deps = [](TFunction<void(FRPGParticipantConfig&)> Edit) { FRPGParticipantConfig C = ConfigA(); Edit(C); return C; };

	Check(TEXT("config A"), ConfigA(), nullptr, FString());
	Check(TEXT("config B"), ConfigB(), nullptr, FString());
	{
		// The authoring defaults of every record, with the selected phase of A: valid.
		FRPGParticipantConfig Defaults;
		Defaults.Phases = ConfigA().Phases;
		Check(TEXT("the authoring defaults of flow, fireball and dependencies"), Defaults, nullptr, FString());
	}

	// Fireball numbers: each non-finite and each negative value in field order, then zero and equal windows valid.
	Check(TEXT("cooldown X NaN"), Fire([](FRPGFireballConfig& F) { F.FireballCooldown.X = QuietNaN; }), TEXT("InvalidFireball.NotFinite"), CooldownPath);
	Check(TEXT("cooldown Y NaN"), Fire([](FRPGFireballConfig& F) { F.FireballCooldown.Y = QuietNaN; }), TEXT("InvalidFireball.NotFinite"), CooldownPath);
	Check(TEXT("cooldown X +Inf"), Fire([](FRPGFireballConfig& F) { F.FireballCooldown.X = PosInf; }), TEXT("InvalidFireball.NotFinite"), CooldownPath);
	Check(TEXT("cooldown Y -Inf"), Fire([](FRPGFireballConfig& F) { F.FireballCooldown.Y = -PosInf; }), TEXT("InvalidFireball.NotFinite"), CooldownPath);
	Check(TEXT("min range NaN"), Fire([](FRPGFireballConfig& F) { F.FireballMinRange = static_cast<float>(QuietNaN); }), TEXT("InvalidFireball.NotFinite"), MinRangePath);
	Check(TEXT("max range +Inf"), Fire([](FRPGFireballConfig& F) { F.FireballMaxRange = static_cast<float>(PosInf); }), TEXT("InvalidFireball.NotFinite"), MaxRangePath);
	Check(TEXT("cooldown X negative"), Fire([](FRPGFireballConfig& F) { F.FireballCooldown.X = -0.001; }), TEXT("InvalidFireball.Negative"), CooldownPath);
	Check(TEXT("cooldown Y negative"), Fire([](FRPGFireballConfig& F) { F.FireballCooldown.Y = -1.0; }), TEXT("InvalidFireball.Negative"), CooldownPath);
	Check(TEXT("min range negative"), Fire([](FRPGFireballConfig& F) { F.FireballMinRange = -1.f; }), TEXT("InvalidFireball.Negative"), MinRangePath);
	Check(TEXT("max range negative"), Fire([](FRPGFireballConfig& F) { F.FireballMaxRange = -0.5f; }), TEXT("InvalidFireball.Negative"), MaxRangePath);
	Check(TEXT("cooldown pair zero (valid)"), Fire([](FRPGFireballConfig& F) { F.FireballCooldown = FVector2D(0.0, 0.0); }), nullptr, FString());
	Check(TEXT("cooldown pair equal (valid)"), Fire([](FRPGFireballConfig& F) { F.FireballCooldown = FVector2D(4.0, 4.0); }), nullptr, FString());
	Check(TEXT("cooldown minimum above the maximum"), Fire([](FRPGFireballConfig& F) { F.FireballCooldown = FVector2D(5.0, 4.0); }), TEXT("InvalidFireball.CooldownOrder"), CooldownPath);
	Check(TEXT("range window equal (valid)"), Fire([](FRPGFireballConfig& F) { F.FireballMinRange = 700.f; F.FireballMaxRange = 700.f; }), nullptr, FString());
	Check(TEXT("range minimum above the maximum"), Fire([](FRPGFireballConfig& F) { F.FireballMinRange = 900.f; F.FireballMaxRange = 800.f; }), TEXT("InvalidFireball.RangeOrder"), MinRangePath);
	Check(TEXT("a huge range (valid, no invented ceiling)"), Fire([](FRPGFireballConfig& F) { F.FireballMaxRange = 1.0e9f; }), nullptr, FString());

	// The fireball ability: required only when enabled; a path that is set must be a well-formed class path either way.
	Check(TEXT("enabled without an ability"), Fire([](FRPGFireballConfig& F) { F.FireballAbility = ClassPtr(FSoftObjectPath()); }), TEXT("InvalidFireball.NoAbility"), AbilityPath);
	Check(TEXT("disabled without an ability (valid)"), Fire([](FRPGFireballConfig& F) { F.bFireballEnabled = false; F.FireballAbility = ClassPtr(FSoftObjectPath()); }), nullptr, FString());
	Check(TEXT("ability with whitespace"), Fire([](FRPGFireballConfig& F) { F.FireballAbility = ClassPtr(MakePath(TEXT("/SyntheticMount/A B"), TEXT("GA_C"))); }), TEXT("InvalidFireball.AbilityPath"), AbilityPath);
	Check(TEXT("ability with a control character"), Fire([](FRPGFireballConfig& F) { F.FireballAbility = ClassPtr(MakePath(TEXT("/SyntheticMount/A"), TEXT("GA\tX_C"))); }), TEXT("InvalidFireball.AbilityPath"), AbilityPath);
	Check(TEXT("ability naming a sub-object"), Fire([](FRPGFireballConfig& F) { F.FireballAbility = ClassPtr(MakePath(TEXT("/SyntheticMount/A"), TEXT("GA_C"), TEXT("Sub"))); }), TEXT("InvalidFireball.AbilityPath"), AbilityPath);
	Check(TEXT("ability path not starting with a slash, disabled but set"), Fire([](FRPGFireballConfig& F) { F.bFireballEnabled = false; F.FireballAbility = ClassPtr(MakePath(TEXT("Relative/A"), TEXT("GA_C"))); }), TEXT("InvalidFireball.AbilityPath"), AbilityPath);
	Check(TEXT("ability with no package folder"), Fire([](FRPGFireballConfig& F) { F.FireballAbility = ClassPtr(MakePath(TEXT("/Root"), TEXT("GA_C"))); }), TEXT("InvalidFireball.AbilityPath"), AbilityPath);
	Check(TEXT("ability that is not a generated class"), Fire([](FRPGFireballConfig& F) { F.FireballAbility = ClassPtr(MakePath(TEXT("/SyntheticMount/A"), TEXT("GA"))); }), TEXT("InvalidFireball.AbilityPath"), AbilityPath);
	Check(TEXT("ability that is only the suffix"), Fire([](FRPGFireballConfig& F) { F.FireballAbility = ClassPtr(MakePath(TEXT("/SyntheticMount/A"), TEXT("_C"))); }), TEXT("InvalidFireball.AbilityPath"), AbilityPath);
	Check(TEXT("a native class path under /Script/ (valid)"), Fire([](FRPGFireballConfig& F) { F.FireballAbility = ClassPtr(MakePath(TEXT("/Script/GameplayAbilities"), TEXT("GameplayAbility"))); }), nullptr, FString());
	Check(TEXT("a /Script/ path with a sub-object is still refused"), Fire([](FRPGFireballConfig& F) { F.FireballAbility = ClassPtr(MakePath(TEXT("/Script/GameplayAbilities"), TEXT("GameplayAbility"), TEXT("Sub"))); }), TEXT("InvalidFireball.AbilityPath"), AbilityPath);
	Check(TEXT("a well-formed ability path of a class that exists nowhere (valid: structure only)"), Fire([](FRPGFireballConfig& F) { F.FireballAbility = ClassPtr(MakePath(TEXT("/SyntheticMount/Nowhere/At/All"), TEXT("GA_Nope_C"))); }), nullptr, FString());

	// The dependencies: required by the roar choice; a set optional reference must still be well-formed; the immunity effect is always required and a class path.
	Check(TEXT("roar clip missing while it is used"), Deps([](FRPGParticipantConfig& C) { C.PhaseDependencies.RoarClip = SequencePtr(FSoftObjectPath()); }), TEXT("InvalidDependency.Missing"), RoarPath);
	Check(TEXT("montage missing while it is the roar"), Deps([](FRPGParticipantConfig& C) { C.PhaseFlow.bUseRoarClip = false; C.PhaseDependencies.TransitionMontage = MontagePtr(FSoftObjectPath()); }), TEXT("InvalidDependency.Missing"), MontagePath);
	Check(TEXT("montage missing but only the fallback (valid)"), Deps([](FRPGParticipantConfig& C) { C.PhaseDependencies.TransitionMontage = MontagePtr(FSoftObjectPath()); }), nullptr, FString());
	Check(TEXT("roar clip missing but unused (valid)"), Deps([](FRPGParticipantConfig& C) { C.PhaseFlow.bUseRoarClip = false; C.PhaseDependencies.RoarClip = SequencePtr(FSoftObjectPath()); }), nullptr, FString());
	Check(TEXT("immunity effect missing"), Deps([](FRPGParticipantConfig& C) { C.PhaseDependencies.ImmunityEffect = ClassPtr(FSoftObjectPath()); }), TEXT("InvalidDependency.Missing"), ImmunityPath);
	Check(TEXT("roar clip malformed (whitespace)"), Deps([](FRPGParticipantConfig& C) { C.PhaseDependencies.RoarClip = SequencePtr(MakePath(TEXT("/SyntheticMount/A B"), TEXT("AN_X"))); }), TEXT("InvalidDependency.Malformed"), RoarPath);
	Check(TEXT("montage malformed although only the fallback"), Deps([](FRPGParticipantConfig& C) { C.PhaseDependencies.TransitionMontage = MontagePtr(MakePath(TEXT("Relative"), TEXT("AM_X"))); }), TEXT("InvalidDependency.Malformed"), MontagePath);
	Check(TEXT("roar clip malformed although unused"), Deps([](FRPGParticipantConfig& C) { C.PhaseFlow.bUseRoarClip = false; C.PhaseDependencies.RoarClip = SequencePtr(MakePath(TEXT("/SyntheticMount/A"), TEXT("AN_X"), TEXT("Sub"))); }), TEXT("InvalidDependency.Malformed"), RoarPath);
	Check(TEXT("immunity effect as a native class path under /Script/ (valid)"), Deps([](FRPGParticipantConfig& C) { C.PhaseDependencies.ImmunityEffect = ClassPtr(MakePath(TEXT("/Script/GameplayAbilities"), TEXT("GameplayEffect"))); }), nullptr, FString());
	Check(TEXT("immunity effect that is not a class path"), Deps([](FRPGParticipantConfig& C) { C.PhaseDependencies.ImmunityEffect = ClassPtr(MakePath(TEXT("/SyntheticMount/A"), TEXT("GE_X"))); }), TEXT("InvalidDependency.NotClassPath"), ImmunityPath);
	Check(TEXT("immunity effect malformed (control character)"), Deps([](FRPGParticipantConfig& C) { C.PhaseDependencies.ImmunityEffect = ClassPtr(MakePath(TEXT("/SyntheticMount/A"), TEXT("GE\nX_C"))); }), TEXT("InvalidDependency.Malformed"), ImmunityPath);
	Check(TEXT("clip and montage that exist nowhere (valid: structure only, no registry query)"), Deps([](FRPGParticipantConfig& C) {
		C.PhaseDependencies.RoarClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Nowhere/Clip"), TEXT("AN_Nope")));
		C.PhaseDependencies.TransitionMontage = MontagePtr(MakePath(TEXT("/SyntheticMount/Nowhere/Montage"), TEXT("AM_Nope"))); }), nullptr, FString());

	// No partial write whichever sub-record is invalid, each with the other three valid and non-default: first (phase), then flow, fireball and (last) dependencies.
	{
		FRPGParticipantConfig C1 = ConfigA();
		C1.Phases[0].EntryHealthFraction = 2.f;
		Check(TEXT("only the selected phase invalid"), C1, TEXT("InvalidPhase.ThresholdOutOfRange"), TEXT("Phases[PhaseTwo].EntryHealthFraction"));
		FRPGParticipantConfig C2 = ConfigA();
		C2.PhaseFlow.LeapAbilityTag = NAME_None;
		Check(TEXT("only the flow invalid"), C2, TEXT("InvalidPhaseFlow.NoLeapTag"), TEXT("PhaseFlow.LeapAbilityTag"));
		FRPGParticipantConfig C3 = ConfigA();
		C3.Fireball.FireballMinRange = 5000.f;
		Check(TEXT("only the fireball invalid"), C3, TEXT("InvalidFireball.RangeOrder"), MinRangePath);
		FRPGParticipantConfig C4 = ConfigA();
		C4.PhaseDependencies.ImmunityEffect = ClassPtr(FSoftObjectPath());
		Check(TEXT("only the dependencies invalid (the last record, everything before it valid and non-default)"), C4, TEXT("InvalidDependency.Missing"), ImmunityPath);
	}

	// Precedence: phase, then flow, then fireball, then dependencies.
	{
		FRPGParticipantConfig C = ConfigA();
		C.PhaseDependencies.ImmunityEffect = ClassPtr(FSoftObjectPath());
		C.Fireball.FireballMinRange = 5000.f;
		C.PhaseFlow.LeapAbilityTag = NAME_None;
		C.Phases[0].EntryHealthFraction = 2.f;
		Check(TEXT("all four invalid: the phase is reported first"), C, TEXT("InvalidPhase.ThresholdOutOfRange"), TEXT("Phases[PhaseTwo].EntryHealthFraction"));
		C.Phases[0].EntryHealthFraction = 0.35f;
		Check(TEXT("flow, fireball and dependencies invalid: the flow is reported first"), C, TEXT("InvalidPhaseFlow.NoLeapTag"), TEXT("PhaseFlow.LeapAbilityTag"));
		C.PhaseFlow.LeapAbilityTag = TEXT("Custom.Leap.Tag");
		Check(TEXT("fireball and dependencies invalid: the fireball is reported first"), C, TEXT("InvalidFireball.RangeOrder"), MinRangePath);
		// Within the fireball: finite, then negative, then the cooldown order, then the range order, then the ability.
		FRPGParticipantConfig F = ConfigA();
		F.Fireball.FireballCooldown = FVector2D(5.0, -4.0);
		F.Fireball.FireballMinRange = 900.f;
		F.Fireball.FireballMaxRange = 800.f;
		F.Fireball.FireballAbility = ClassPtr(FSoftObjectPath());
		Check(TEXT("negative cooldown Y outranks the cooldown order, the range order and the ability"), F, TEXT("InvalidFireball.Negative"), CooldownPath);
		F.Fireball.FireballCooldown = FVector2D(5.0, 4.0);
		Check(TEXT("cooldown order outranks the range order and the ability"), F, TEXT("InvalidFireball.CooldownOrder"), CooldownPath);
		F.Fireball.FireballCooldown = FVector2D(2.0, 3.0);
		Check(TEXT("range order outranks the ability"), F, TEXT("InvalidFireball.RangeOrder"), MinRangePath);
	}

	// The selection is part of the cluster: none, an id that does not exist.
	{
		FString Error;
		TestFalse(TEXT("no selected phase id"), RPGBossPhasesClusterAdapters::ValidatePhasesCluster(ConfigA(), NAME_None, Error));
		TestTrue(TEXT("named InvalidPhase.NoSelection"), Error.StartsWith(TEXT("InvalidPhase.NoSelection")));
		TestFalse(TEXT("an id that is not in the record"), RPGBossPhasesClusterAdapters::ValidatePhasesCluster(ConfigA(), FName(TEXT("Missing")), Error));
		TestTrue(TEXT("named InvalidPhase.NotFound or UnsupportedNativePhaseSet"), Error.StartsWith(TEXT("InvalidPhase.NotFound")) || Error.StartsWith(TEXT("UnsupportedNativePhaseSet")));
	}

	// The component refused every record above and is still configurable.
	FString Error;
	TestTrue(TEXT("after all refusals a valid cluster still configures"), RPGBossPhasesClusterAdapters::ConfigurePhasesCluster(*Phases, ConfigA(), SelectedId, Error) && FClusterState(*Phases).TransitionSeconds == 2.75f
		&& FClusterState(*Phases).FireballMaxRange == 999.f);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPhasesClusterIsolationTest, "OneBossFight.Binding.PhasesCluster.Isolation",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPhasesClusterIsolationTest::RunTest(const FString& Parameters)
{
	using namespace PhasesClusterTests;
	FClusterTestWorld Scope;
	if (!TestNotNull(TEXT("test world"), Scope.World))
	{
		return false;
	}
	AActor* OwnerA = Scope.SpawnOwner();
	AActor* OwnerB = Scope.SpawnOwner();
	AActor* OwnerC = Scope.SpawnOwner();
	if (!TestTrue(TEXT("three owners"), OwnerA && OwnerB && OwnerC))
	{
		return false;
	}
	TStrongObjectPtr<URPGBossPhases> A = NewPhases(OwnerA, TEXT("RPGBossPhases"));
	TStrongObjectPtr<URPGBossPhases> B = NewPhases(OwnerB, TEXT("RPGBossPhases"));
	TStrongObjectPtr<URPGBossPhases> C = NewPhases(OwnerC, TEXT("RPGBossPhases"));
	if (!TestTrue(TEXT("three components"), A.IsValid() && B.IsValid() && C.IsValid()))
	{
		return false;
	}
	const FClusterState UntouchedC(*C);
	FRPGParticipantConfig ConfigForA = ConfigA();
	const FRPGParticipantConfig ConfigForB = ConfigB();
	FString Error;
	TestTrue(TEXT("A"), RPGBossPhasesClusterAdapters::ConfigurePhasesCluster(*A, ConfigForA, SelectedId, Error));
	const FClusterState SnapshotA(*A);
	TestTrue(TEXT("B"), RPGBossPhasesClusterAdapters::ConfigurePhasesCluster(*B, ConfigForB, SelectedId, Error));
	TestTrue(TEXT("configuring B did not change A"), FClusterState(*A) == SnapshotA);
	TestFalse(TEXT("B really differs from A in the phase, flow, fireball and dependency groups"), FClusterState(*B).PhaseAndFlowEquals(SnapshotA) || FClusterState(*B).FireballAndDependenciesEqual(SnapshotA));

	// The assignment copies values: changing the config afterwards changes nothing (strings, names, paths and the cooldown pair included).
	ConfigForA.Phases[0].EntryHealthFraction = 0.9f;
	ConfigForA.PhaseFlow.AttackAbilityPrefix = TEXT("CHANGED_AFTERWARDS");
	ConfigForA.PhaseFlow.LeapAbilityTag = TEXT("Changed.Afterwards");
	ConfigForA.Fireball.FireballCooldown = FVector2D(70.0, 80.0);
	ConfigForA.Fireball.FireballAbility = ClassPtr(MakePath(TEXT("/SyntheticMount/Changed"), TEXT("Afterwards_C")));
	ConfigForA.PhaseDependencies.ImmunityEffect = ClassPtr(MakePath(TEXT("/SyntheticMount/Changed"), TEXT("Immune_C")));
	TestTrue(TEXT("a later config change does not reach A"), FClusterState(*A) == SnapshotA);

	// A component that was never configured keeps the native declarations and constructor values, and so does the class default object.
	TestTrue(TEXT("untouched component unchanged"), FClusterState(*C) == UntouchedC);
	TestTrue(TEXT("CDO is a component of the same native values as the untouched one"), FClusterState(*GetDefault<URPGBossPhases>()) == UntouchedC);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPhasesClusterRejectionsTest, "OneBossFight.Binding.PhasesCluster.Rejections",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPhasesClusterRejectionsTest::RunTest(const FString& Parameters)
{
	using namespace PhasesClusterTests;
	FClusterTestWorld Scope;
	if (!TestNotNull(TEXT("test world"), Scope.World))
	{
		return false;
	}
	const FRPGParticipantConfig Config = ConfigA(); // valid: every failure below is about the component or the owner
	FString Error;

	// A rejected call changes nothing and names the reason. Wrong-class targets are concrete classes (UActorComponent itself is abstract).
	auto ExpectRejected = [&](const TCHAR* Label, UActorComponent& Component, const TCHAR* Token)
	{
		const URPGBossPhases* AsPhases = Cast<URPGBossPhases>(&Component);
		const URPGBossEncounter* AsEncounter = Cast<URPGBossEncounter>(&Component);
		const URPGBossPosture* AsPosture = Cast<URPGBossPosture>(&Component);
		TOptional<FClusterState> Before;
		if (AsPhases) { Before.Emplace(*AsPhases); }
		const float EncounterGateBefore = AsEncounter ? AsEncounter->GateRadius : 0.f;
		const float PostureMaxBefore = AsPosture ? AsPosture->PostureMax : 0.f;
		const bool bOk = RPGBossPhasesClusterAdapters::ConfigurePhasesCluster(Component, Config, SelectedId, Error);
		TestFalse(FString::Printf(TEXT("%s: rejected"), Label), bOk);
		TestTrue(FString::Printf(TEXT("%s: named %s (got '%s')"), Label, Token, *Error), Error.StartsWith(Token));
		if (Before.IsSet()) { TestTrue(FString::Printf(TEXT("%s: phases unchanged (all 18 fields and state)"), Label), FClusterState(*AsPhases) == Before.GetValue()); }
		if (AsEncounter) { TestTrue(FString::Printf(TEXT("%s: encounter configuration untouched"), Label), AsEncounter->GateRadius == EncounterGateBefore); }
		if (AsPosture) { TestTrue(FString::Printf(TEXT("%s: posture configuration untouched"), Label), AsPosture->PostureMax == PostureMaxBefore); }
	};

	AActor* Owner = Scope.SpawnOwner();
	if (!TestNotNull(TEXT("owner actor"), Owner))
	{
		return false;
	}

	// Wrong class: two other native components and a concrete engine component.
	{
		TStrongObjectPtr<URPGBossPosture> Posture(NewObject<URPGBossPosture>(Owner, TEXT("RPGBossPosture")));
		TStrongObjectPtr<URPGBossEncounter> Encounter(NewObject<URPGBossEncounter>(Owner, TEXT("RPGBossEncounter")));
		TStrongObjectPtr<USceneComponent> Scene(NewObject<USceneComponent>(Owner, TEXT("UnrelatedScene")));
		if (!TestTrue(TEXT("wrong-class components created"), Posture.IsValid() && Encounter.IsValid() && Scene.IsValid()))
		{
			return false;
		}
		ExpectRejected(TEXT("cluster on a posture"), *Posture, TEXT("WrongComponentClass"));
		ExpectRejected(TEXT("cluster on an encounter"), *Encounter, TEXT("WrongComponentClass"));
		ExpectRejected(TEXT("cluster on a scene component"), *Scene, TEXT("WrongComponentClass"));
	}

	// Already registered (the owner has not begun play, so registration alone does not begin play for the component).
	{
		TStrongObjectPtr<URPGBossPhases> Phases = NewPhases(Owner, TEXT("RegisteredPhases"));
		if (!TestTrue(TEXT("registered component created"), Phases.IsValid()))
		{
			return false;
		}
		ArmDistinctStart(*Phases);
		Phases->RegisterComponent();
		if (!TestTrue(TEXT("precondition: registered and not begun"), Phases->IsRegistered() && !Phases->HasBegunPlay() && !Owner->HasActorBegunPlay()))
		{
			AddError(TEXT("unsupported precondition: the registered-but-not-begun state could not be built"));
			return false;
		}
		ExpectRejected(TEXT("registered phases"), *Phases, TEXT("ComponentAlreadyRegistered"));
	}

	// Component already began play: its owner begins play with the component registered. The phases BeginPlay only loads three soft pointers (and uses the owner through guarded casts), so they are cleared first
	// and nothing is loaded.
	{
		AActor* BegunOwner = Scope.SpawnOwner();
		if (!TestNotNull(TEXT("begun owner actor"), BegunOwner))
		{
			return false;
		}
		TStrongObjectPtr<URPGBossPhases> Phases = NewPhases(BegunOwner, TEXT("BegunPhases"));
		if (!TestTrue(TEXT("begun component created"), Phases.IsValid()))
		{
			return false;
		}
		ArmDistinctStart(*Phases);
		Phases->RoarClip.Reset();
		Phases->TransitionMontage.Reset();
		Phases->ImmunityEffect.Reset();
		Phases->RegisterComponent();
		BegunOwner->DispatchBeginPlay();
		if (!TestTrue(TEXT("precondition: component and owner began play"), Phases->HasBegunPlay() && BegunOwner->HasActorBegunPlay()))
		{
			AddError(TEXT("unsupported precondition: the begun-play state could not be built without loading assets"));
			return false;
		}
		ExpectRejected(TEXT("begun phases"), *Phases, TEXT("ComponentBegunPlay"));
	}

	// Owner already began play, the component itself is a fresh unregistered one.
	{
		AActor* LateOwner = Scope.SpawnOwner();
		if (!TestNotNull(TEXT("late owner actor"), LateOwner))
		{
			return false;
		}
		LateOwner->DispatchBeginPlay();
		if (!TestTrue(TEXT("precondition: owner began play"), LateOwner->HasActorBegunPlay()))
		{
			AddError(TEXT("unsupported precondition: the owner could not be put into the begun state"));
			return false;
		}
		TStrongObjectPtr<URPGBossPhases> Phases = NewPhases(LateOwner, TEXT("LatePhases"));
		if (!TestTrue(TEXT("late component created"), Phases.IsValid()))
		{
			return false;
		}
		ArmDistinctStart(*Phases);
		ExpectRejected(TEXT("phases under a begun owner"), *Phases, TEXT("OwnerBegunPlay"));
	}

	// Invalid owner: the component's outer is not an actor.
	{
		TStrongObjectPtr<URPGBossPhases> Phases(NewObject<URPGBossPhases>(GetTransientPackage(), TEXT("OrphanPhases")));
		if (!TestTrue(TEXT("orphan component created"), Phases.IsValid() && !Phases->GetOwner()))
		{
			return false;
		}
		ArmDistinctStart(*Phases);
		ExpectRejected(TEXT("phases without an owner"), *Phases, TEXT("InvalidOwner"));
	}

	// Destroyed component: DestroyComponent already ran (flagged as being destroyed, unregistered, EndPlay cleared, removed from its owner, marked garbage) but the object is still allocated because the test holds it
	// and no garbage collection runs here. The owner stays live, so this is the component check and not the owner check. This is not a freed-memory test.
	{
		AActor* LiveOwner = Scope.SpawnOwner();
		if (!TestNotNull(TEXT("live owner actor"), LiveOwner))
		{
			return false;
		}
		TStrongObjectPtr<URPGBossPhases> Phases = NewPhases(LiveOwner, TEXT("DeadPhases"));
		TStrongObjectPtr<URPGBossPosture> Posture(NewObject<URPGBossPosture>(LiveOwner, TEXT("DeadPosture")));
		if (!TestTrue(TEXT("dead components created"), Phases.IsValid() && Posture.IsValid()))
		{
			return false;
		}
		ArmDistinctStart(*Phases);
		Phases->DestroyComponent();
		Posture->DestroyComponent();
		const bool bRetained = Phases.Get() != nullptr && Posture.Get() != nullptr && Phases->GetOuter() == LiveOwner && Posture->GetOuter() == LiveOwner;
		const bool bFlaggedDead = Phases->IsBeingDestroyed() && Posture->IsBeingDestroyed();
		const bool bOwnerLive = IsValid(LiveOwner) && !LiveOwner->IsActorBeingDestroyed() && !LiveOwner->HasActorBegunPlay();
		if (!TestTrue(TEXT("precondition: destroyed components still allocated and linked to their owner, owner live"), bRetained && bFlaggedDead && bOwnerLive))
		{
			AddError(TEXT("unsupported precondition: the destroyed-but-retained state could not be built"));
			return false;
		}
		TestTrue(TEXT("precondition: a destroyed component looks unregistered and not begun, which is why only the first check can refuse it"), !Phases->IsRegistered() && !Phases->HasBegunPlay());
		ExpectRejected(TEXT("destroyed phases"), *Phases, TEXT("InvalidComponent"));
		// The component check is first: a destroyed component of the WRONG class is reported as invalid, not as the wrong class.
		ExpectRejected(TEXT("cluster on a destroyed posture"), *Posture, TEXT("InvalidComponent"));
		TestTrue(TEXT("the owner stayed live through both calls"), IsValid(LiveOwner) && !LiveOwner->IsActorBeingDestroyed());
	}

	AddInfo(TEXT("Rejection paths on isolated actors; an owner that is being destroyed is covered by the code (IsActorBeingDestroyed) but not exercised here."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPhasesClusterCompileTest, "OneBossFight.Binding.PhasesCluster.Compile",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPhasesClusterCompileTest::RunTest(const FString& Parameters)
{
	using namespace PhasesClusterTests;
	const FEpochPtr Content = RPGCombatRegistry::Legacy();
	if (!TestTrue(TEXT("content epoch"), Content.IsValid() && Content->Id.IsValid()))
	{
		return false;
	}

	// The real synthetic compiler copies both new records into the immutable config, all paths and the cooldown pair included.
	{
		const FRPGParticipantConfig A = ConfigA();
		const TStrongObjectPtr<URPGBossDefinition> Definition = MakeDefinition(A);
		FConfigPtr Out;
		const FRPGHydrationResult Result = CompileSynthetic(*Definition, Content, Out);
		if (!TestTrue(TEXT("a valid definition compiles"), Result.IsReady() && Out.IsValid()))
		{
			return false;
		}
		TestTrue(TEXT("fireball copied (record A)"), Out->Fireball.bFireballEnabled && Out->Fireball.FireballAbility.ToSoftObjectPath() == A.Fireball.FireballAbility.ToSoftObjectPath()
			&& Out->Fireball.FireballCooldown == FVector2D(2.0, 3.0) && Out->Fireball.FireballMinRange == 111.f && Out->Fireball.FireballMaxRange == 999.f);
		TestTrue(TEXT("dependencies copied (record A)"), Out->PhaseDependencies.RoarClip.ToSoftObjectPath() == A.PhaseDependencies.RoarClip.ToSoftObjectPath()
			&& Out->PhaseDependencies.TransitionMontage.ToSoftObjectPath() == A.PhaseDependencies.TransitionMontage.ToSoftObjectPath()
			&& Out->PhaseDependencies.ImmunityEffect.ToSoftObjectPath() == A.PhaseDependencies.ImmunityEffect.ToSoftObjectPath());
		TestTrue(TEXT("established Stats, phase, flow and identity values retained"), Out->Stats.MaxHealth == 3500.f && Out->Phases.Num() == 1 && Out->PhaseFlow.TransitionSeconds == 2.75f
			&& Out->PhaseFlow.AttackAbilityPrefix.Equals(TEXT("GA_Custom_Boss_"), ESearchCase::CaseSensitive) && Out->BossId == FName(TEXT("Synthetic")) && Out->bSyntheticFixture);
		TestTrue(TEXT("the encounter and stagger policies still carry their authoring defaults next to it"), Out->EncounterPolicy.GateRadius == 1200.f && Out->StaggerPolicy.StaggerSeconds == 2.5f);
		// The config is a value snapshot: changing the definition afterwards changes nothing.
		Definition->Fireball.FireballCooldown = FVector2D(70.0, 80.0);
		Definition->PhaseDependencies.ImmunityEffect = ClassPtr(MakePath(TEXT("/SyntheticMount/Changed"), TEXT("Immune_C")));
		TestTrue(TEXT("a later definition change does not reach the compiled config"), Out->Fireball.FireballCooldown == FVector2D(2.0, 3.0)
			&& Out->PhaseDependencies.ImmunityEffect.ToSoftObjectPath() == A.PhaseDependencies.ImmunityEffect.ToSoftObjectPath());
	}
	{
		const FRPGParticipantConfig B = ConfigB();
		const TStrongObjectPtr<URPGBossDefinition> Definition = MakeDefinition(B);
		FConfigPtr Out;
		TestTrue(TEXT("record B compiles (montage is the roar, null clip and ability, zero windows)"), CompileSynthetic(*Definition, Content, Out).IsReady() && Out.IsValid()
			&& !Out->Fireball.bFireballEnabled && Out->Fireball.FireballAbility.IsNull() && Out->PhaseDependencies.RoarClip.IsNull() && Out->PhaseDependencies.TransitionMontage.ToSoftObjectPath() == B.PhaseDependencies.TransitionMontage.ToSoftObjectPath());
	}
	// A definition whose new records were never authored receives the additive authoring defaults, and the compiled config carries them.
	{
		TStrongObjectPtr<URPGBossDefinition> Definition = MakeDefinition(ConfigA());
		Definition->PhaseFlow = FRPGPhaseFlowConfig();
		Definition->Fireball = FRPGFireballConfig();
		Definition->PhaseDependencies = FRPGPhaseDependencyConfig();
		FConfigPtr Out;
		const FRPGFireballConfig DefaultFireball;
		const FRPGPhaseDependencyConfig DefaultDependencies;
		TestTrue(TEXT("untouched records: the authoring defaults are copied"), CompileSynthetic(*Definition, Content, Out).IsReady() && Out.IsValid()
			&& !Out->Fireball.bFireballEnabled && Out->Fireball.FireballAbility.ToSoftObjectPath() == DefaultFireball.FireballAbility.ToSoftObjectPath()
			&& Out->Fireball.FireballCooldown == DefaultFireball.FireballCooldown && Out->Fireball.FireballMinRange == 500.f && Out->Fireball.FireballMaxRange == 1800.f
			&& Out->PhaseDependencies.RoarClip.ToSoftObjectPath() == DefaultDependencies.RoarClip.ToSoftObjectPath()
			&& Out->PhaseDependencies.TransitionMontage.ToSoftObjectPath() == DefaultDependencies.TransitionMontage.ToSoftObjectPath()
			&& Out->PhaseDependencies.ImmunityEffect.ToSoftObjectPath() == DefaultDependencies.ImmunityEffect.ToSoftObjectPath());
	}

	// An invalid record fails by name, is NEVER replaced by the defaults, reordered or repaired, and clears a previously valid output; the production compile refuses it before any asset is loaded.
	struct FBad
	{
		const TCHAR* Name;
		TFunction<void(FRPGParticipantConfig&)> Break;
		const TCHAR* Token;
	};
	const FBad Bad[] = {
		{TEXT("NaN cooldown"), [](FRPGParticipantConfig& C) { C.Fireball.FireballCooldown.X = QuietNaN; }, TEXT("InvalidFireball.NotFinite")},
		{TEXT("negative range"), [](FRPGParticipantConfig& C) { C.Fireball.FireballMinRange = -1.f; }, TEXT("InvalidFireball.Negative")},
		{TEXT("inverted cooldown"), [](FRPGParticipantConfig& C) { C.Fireball.FireballCooldown = FVector2D(5.0, 4.0); }, TEXT("InvalidFireball.CooldownOrder")},
		{TEXT("inverted ranges"), [](FRPGParticipantConfig& C) { C.Fireball.FireballMinRange = 900.f; C.Fireball.FireballMaxRange = 800.f; }, TEXT("InvalidFireball.RangeOrder")},
		{TEXT("enabled fireball without an ability"), [](FRPGParticipantConfig& C) { C.Fireball.FireballAbility = ClassPtr(FSoftObjectPath()); }, TEXT("InvalidFireball.NoAbility")},
		{TEXT("malformed ability path"), [](FRPGParticipantConfig& C) { C.Fireball.FireballAbility = ClassPtr(MakePath(TEXT("/SyntheticMount/A B"), TEXT("GA_C"))); }, TEXT("InvalidFireball.AbilityPath")},
		{TEXT("roar clip missing while used"), [](FRPGParticipantConfig& C) { C.PhaseDependencies.RoarClip = SequencePtr(FSoftObjectPath()); }, TEXT("InvalidDependency.Missing")},
		{TEXT("immunity effect missing"), [](FRPGParticipantConfig& C) { C.PhaseDependencies.ImmunityEffect = ClassPtr(FSoftObjectPath()); }, TEXT("InvalidDependency.Missing")},
		{TEXT("malformed montage"), [](FRPGParticipantConfig& C) { C.PhaseDependencies.TransitionMontage = MontagePtr(MakePath(TEXT("Relative"), TEXT("AM_X"))); }, TEXT("InvalidDependency.Malformed")},
		{TEXT("immunity effect that is not a class path"), [](FRPGParticipantConfig& C) { C.PhaseDependencies.ImmunityEffect = ClassPtr(MakePath(TEXT("/SyntheticMount/A"), TEXT("GE_X"))); }, TEXT("InvalidDependency.NotClassPath")},
		{TEXT("montage missing while it is the roar"), [](FRPGParticipantConfig& C) { C.PhaseFlow.bUseRoarClip = false; C.PhaseDependencies.TransitionMontage = MontagePtr(FSoftObjectPath()); }, TEXT("InvalidDependency.Missing")},
	};
	for (const FBad& Case : Bad)
	{
		FRPGParticipantConfig Broken = ConfigA();
		Case.Break(Broken);
		const TStrongObjectPtr<URPGBossDefinition> Definition = MakeDefinition(Broken);

		FConfigPtr Out;
		if (!TestTrue(FString::Printf(TEXT("%s: a valid output exists first"), Case.Name), CompileSynthetic(*MakeDefinition(ConfigA()), Content, Out).IsReady() && Out.IsValid()))
		{
			return false;
		}
		const FRPGHydrationResult Result = CompileSynthetic(*Definition, Content, Out); // the same output variable
		TestFalse(FString::Printf(TEXT("%s (synthetic compile): refused"), Case.Name), Result.IsReady());
		TestTrue(FString::Printf(TEXT("%s (synthetic compile): named %s"), Case.Name, Case.Token), AnyErrorContains(Result, Case.Token));
		TestFalse(FString::Printf(TEXT("%s (synthetic compile): the earlier valid output was cleared, nothing defaulted"), Case.Name), Out.IsValid());

		FConfigPtr ProductionOut;
		if (CompileSynthetic(*MakeDefinition(ConfigA()), Content, ProductionOut).IsReady() && ProductionOut.IsValid())
		{
			const FRPGHydrationResult Production = RPGCombatHydration::CompileParticipant(*Definition, Content, FString::ChrN(64, TEXT('b')), ProductionOut);
			TestFalse(FString::Printf(TEXT("%s (production compile): refused"), Case.Name), Production.IsReady());
			TestTrue(FString::Printf(TEXT("%s (production compile): named %s"), Case.Name, Case.Token), AnyErrorContains(Production, Case.Token));
			TestFalse(FString::Printf(TEXT("%s (production compile): the earlier output was cleared"), Case.Name), ProductionOut.IsValid());
		}
		else
		{
			AddError(TEXT("unsupported precondition: a valid output for the production compile could not be built"));
		}
	}

	// The established checks are retained, with valid new records; each failure clears a previously valid output.
	auto RunRetained = [&](const TCHAR* Name, const TCHAR* Text, const TFunction<void(URPGBossDefinition&)>& Break, int32 Schema, const FString& Hash, bool bNullContent)
	{
		FConfigPtr Out;
		if (!CompileSynthetic(*MakeDefinition(ConfigA()), Content, Out).IsReady() || !Out.IsValid())
		{
			AddError(TEXT("unsupported precondition: a valid output could not be built"));
			return;
		}
		const TStrongObjectPtr<URPGBossDefinition> Definition = MakeDefinition(ConfigA()); // valid new records
		Definition->Schema = Schema;
		Break(*Definition);
		const FRPGHydrationResult Result = CompileSynthetic(*Definition, bNullContent ? FEpochPtr() : Content, Out, Hash);
		TestFalse(FString::Printf(TEXT("%s: still refused with valid new records"), Name), Result.IsReady());
		TestTrue(FString::Printf(TEXT("%s: the established message '%s'"), Name, Text), AnyErrorContains(Result, Text));
		TestFalse(FString::Printf(TEXT("%s: the earlier valid output was cleared"), Name), Out.IsValid());
	};
	const FString GoodHash = FString::ChrN(64, TEXT('b'));
	RunRetained(TEXT("invalid phase flow"), TEXT("InvalidPhaseFlow.NoLeapTag"), [](URPGBossDefinition& D) { D.PhaseFlow.LeapAbilityTag = NAME_None; }, 1, GoodHash, false);
	RunRetained(TEXT("invalid stagger policy"), TEXT("InvalidStagger.NotPositive"), [](URPGBossDefinition& D) { D.StaggerPolicy.GetUpRate = 0.f; }, 1, GoodHash, false);
	RunRetained(TEXT("invalid encounter policy"), TEXT("InvalidPolicy.Negative"), [](URPGBossDefinition& D) { D.EncounterPolicy.GateRadius = -1.f; }, 1, GoodHash, false);
	RunRetained(TEXT("negative posture maximum"), TEXT("invalid stats"), [](URPGBossDefinition& D) { D.Stats.MaxPosture = -1.f; }, 1, GoodHash, false);
	RunRetained(TEXT("phase threshold above 1"), TEXT("invalid/duplicate phase"), [](URPGBossDefinition& D) { D.Phases[0].EntryHealthFraction = 2.f; }, 1, GoodHash, false);
	RunRetained(TEXT("schema 2"), TEXT("identity absent"), [](URPGBossDefinition&) {}, 2, GoodHash, false);
	RunRetained(TEXT("manifest hash that is not 64 hex characters"), TEXT("identity absent"), [](URPGBossDefinition&) {}, 1, TEXT("short"), false);
	RunRetained(TEXT("no content lease"), TEXT("identity absent"), [](URPGBossDefinition&) {}, 1, GoodHash, true);
	RunRetained(TEXT("no field manifest"), TEXT("field manifest required"), [](URPGBossDefinition& D) { D.Fields.Reset(); }, 1, GoodHash, false);

	// Several failures are all reported: an invalid dependency together with an invalid fireball, flow, stagger policy, encounter policy and stats.
	{
		FRPGParticipantConfig Broken = ConfigA();
		Broken.PhaseDependencies.ImmunityEffect = ClassPtr(FSoftObjectPath());
		Broken.Fireball.FireballMinRange = 5000.f;
		Broken.PhaseFlow.LeapAbilityTag = NAME_None;
		const TStrongObjectPtr<URPGBossDefinition> Definition = MakeDefinition(Broken);
		Definition->StaggerPolicy.GetUpRate = -2.f;
		Definition->EncounterPolicy.GateRadius = -5.f;
		Definition->Stats.MaxPosture = -1.f;
		FConfigPtr Out;
		const FRPGHydrationResult Result = CompileSynthetic(*Definition, Content, Out);
		TestTrue(TEXT("invalid dependency, fireball, flow, stagger policy, encounter policy and stats are all reported"),
			!Result.IsReady() && AnyErrorContains(Result, TEXT("InvalidDependency.Missing")) && AnyErrorContains(Result, TEXT("InvalidFireball.RangeOrder")) && AnyErrorContains(Result, TEXT("InvalidPhaseFlow.NoLeapTag"))
			&& AnyErrorContains(Result, TEXT("InvalidStagger.NotPositive")) && AnyErrorContains(Result, TEXT("InvalidPolicy.Negative")) && AnyErrorContains(Result, TEXT("invalid stats")) && !Out.IsValid());
	}

	AddInfo(TEXT("Real synthetic compiler and the production compile's early rejection; NO production compile with a real skeleton, NO serialized asset."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPhasesClusterAuthoringTest, "OneBossFight.Binding.PhasesCluster.Authoring",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPhasesClusterAuthoringTest::RunTest(const FString& Parameters)
{
	using namespace PhasesClusterTests;
	const UClass* Native = URPGBossPhases::StaticClass();

	// The fireball record: five properties with the native names and types, editable, and ALSO present with the same name and kind on URPGBossPhases.
	const UScriptStruct* FireballStruct = FRPGFireballConfig::StaticStruct();
	const UScriptStruct* DependencyStruct = FRPGPhaseDependencyConfig::StaticStruct();
	if (!TestTrue(TEXT("both new structs are reflected"), FireballStruct != nullptr && DependencyStruct != nullptr))
	{
		return false;
	}
	{
		const FProperty* Enabled = FireballStruct->FindPropertyByName(TEXT("bFireballEnabled"));
		TestTrue(TEXT("bFireballEnabled: reflected editable bool"), Enabled && CastField<FBoolProperty>(Enabled) && Enabled->HasAnyPropertyFlags(CPF_Edit));
		TestTrue(TEXT("bFireballEnabled also a bool of URPGBossPhases"), CastField<FBoolProperty>(Native->FindPropertyByName(TEXT("bFireballEnabled"))) != nullptr);
		const FProperty* Ability = FireballStruct->FindPropertyByName(TEXT("FireballAbility"));
		TestTrue(TEXT("FireballAbility: reflected editable soft class"), Ability && CastField<FSoftClassProperty>(Ability) && Ability->HasAnyPropertyFlags(CPF_Edit));
		TestTrue(TEXT("FireballAbility also a soft class of URPGBossPhases"), CastField<FSoftClassProperty>(Native->FindPropertyByName(TEXT("FireballAbility"))) != nullptr);
		const FStructProperty* Cooldown = CastField<FStructProperty>(FireballStruct->FindPropertyByName(TEXT("FireballCooldown")));
		TestTrue(TEXT("FireballCooldown: reflected editable FVector2D"), Cooldown && Cooldown->Struct == TBaseStructure<FVector2D>::Get() && Cooldown->HasAnyPropertyFlags(CPF_Edit));
		const FStructProperty* NativeCooldown = CastField<FStructProperty>(Native->FindPropertyByName(TEXT("FireballCooldown")));
		TestTrue(TEXT("FireballCooldown also an FVector2D of URPGBossPhases"), NativeCooldown && NativeCooldown->Struct == TBaseStructure<FVector2D>::Get());
		for (const TCHAR* Name : {TEXT("FireballMinRange"), TEXT("FireballMaxRange")})
		{
			const FProperty* Property = FireballStruct->FindPropertyByName(Name);
			TestTrue(FString::Printf(TEXT("%s: reflected editable float"), Name), Property && CastField<FFloatProperty>(Property) && Property->HasAnyPropertyFlags(CPF_Edit));
			TestTrue(FString::Printf(TEXT("%s also a float of URPGBossPhases"), Name), CastField<FFloatProperty>(Native->FindPropertyByName(Name)) != nullptr);
		}
	}
	{
		// A soft class property derives from the soft object property, so the clip and the montage must be soft object properties that are NOT soft class properties.
		for (const TCHAR* Name : {TEXT("RoarClip"), TEXT("TransitionMontage")})
		{
			const FProperty* Property = DependencyStruct->FindPropertyByName(Name);
			TestTrue(FString::Printf(TEXT("%s: reflected editable soft object reference"), Name), Property && CastField<FSoftObjectProperty>(Property) && !CastField<FSoftClassProperty>(Property) && Property->HasAnyPropertyFlags(CPF_Edit));
			const FProperty* NativeProperty = Native->FindPropertyByName(Name);
			TestTrue(FString::Printf(TEXT("%s also a soft object reference of URPGBossPhases"), Name), NativeProperty && CastField<FSoftObjectProperty>(NativeProperty) && !CastField<FSoftClassProperty>(NativeProperty));
		}
		const FProperty* Immunity = DependencyStruct->FindPropertyByName(TEXT("ImmunityEffect"));
		TestTrue(TEXT("ImmunityEffect: reflected editable soft class"), Immunity && CastField<FSoftClassProperty>(Immunity) && Immunity->HasAnyPropertyFlags(CPF_Edit));
		TestTrue(TEXT("ImmunityEffect also a soft class of URPGBossPhases"), CastField<FSoftClassProperty>(Native->FindPropertyByName(TEXT("ImmunityEffect"))) != nullptr);
	}

	// The Data Asset fields: the definition exposes both records as editable properties of exactly those struct types.
	const FStructProperty* FireballField = CastField<FStructProperty>(URPGBossDefinition::StaticClass()->FindPropertyByName(TEXT("Fireball")));
	const FStructProperty* DependencyField = CastField<FStructProperty>(URPGBossDefinition::StaticClass()->FindPropertyByName(TEXT("PhaseDependencies")));
	if (!TestTrue(TEXT("the definition has Fireball and PhaseDependencies struct properties"), FireballField != nullptr && DependencyField != nullptr))
	{
		return false;
	}
	TestTrue(TEXT("both are editable (EditAnywhere) and of the new struct types"), FireballField->HasAnyPropertyFlags(CPF_Edit) && DependencyField->HasAnyPropertyFlags(CPF_Edit)
		&& FireballField->Struct == FireballStruct && DependencyField->Struct == DependencyStruct);

	// The additive authoring defaults of the NEW fields: fresh structs and a fresh definition hold them; the native constructor values are only the baseline they match, not an authority.
	const FRPGFireballConfig Fireball;
	const FRPGPhaseDependencyConfig Dependencies;
	TStrongObjectPtr<URPGBossDefinition> Definition(NewObject<URPGBossDefinition>());
	TestTrue(TEXT("a fresh definition holds the authoring defaults (old schema 1 definitions receive them additively)"), Definition->Fireball.FireballCooldown == Fireball.FireballCooldown
		&& Definition->Fireball.FireballAbility.ToSoftObjectPath() == Fireball.FireballAbility.ToSoftObjectPath() && Definition->PhaseDependencies.RoarClip.ToSoftObjectPath() == Dependencies.RoarClip.ToSoftObjectPath());
	const URPGBossPhases* Cdo = GetDefault<URPGBossPhases>();
	TestTrue(TEXT("baseline: the fireball defaults equal the native constructor values, field by field"), Fireball.bFireballEnabled == Cdo->bFireballEnabled
		&& Fireball.FireballAbility.ToSoftObjectPath() == Cdo->FireballAbility.ToSoftObjectPath() && Fireball.FireballCooldown == Cdo->FireballCooldown && Fireball.FireballMinRange == Cdo->FireballMinRange
		&& Fireball.FireballMaxRange == Cdo->FireballMaxRange);
	TestTrue(TEXT("baseline: the dependency defaults equal the native constructor values, field by field"), Dependencies.RoarClip.ToSoftObjectPath() == Cdo->RoarClip.ToSoftObjectPath()
		&& Dependencies.TransitionMontage.ToSoftObjectPath() == Cdo->TransitionMontage.ToSoftObjectPath() && Dependencies.ImmunityEffect.ToSoftObjectPath() == Cdo->ImmunityEffect.ToSoftObjectPath());
	// The documented values, so a silent change of the declared defaults is noticed.
	TestTrue(TEXT("the fireball defaults are the documented ones"), !Fireball.bFireballEnabled && Fireball.FireballCooldown == FVector2D(6.0, 10.0) && Fireball.FireballMinRange == 500.f && Fireball.FireballMaxRange == 1800.f
		&& Fireball.FireballAbility.ToSoftObjectPath().ToString().EndsWith(TEXT("GA_Fireball_Enemy.GA_Fireball_Enemy_C")));
	TestTrue(TEXT("the dependency defaults are the documented ones"), Dependencies.RoarClip.ToSoftObjectPath().ToString().EndsWith(TEXT("/AN_Boss01_PhaseRoar.AN_Boss01_PhaseRoar"))
		&& Dependencies.TransitionMontage.ToSoftObjectPath().ToString().EndsWith(TEXT("/Ability_R_Intro_Anim_Montage.Ability_R_Intro_Anim_Montage"))
		&& Dependencies.ImmunityEffect.ToSoftObjectPath().ToString().EndsWith(TEXT("/GE_HitStunImmune.GE_HitStunImmune_C")));
	// The defaults pass their own validators (they are valid, not a fallback for invalid input).
	FString Error;
	TestTrue(TEXT("the authoring defaults pass the shared validators"), RPGBossPhasesClusterAdapters::ValidateFireball(Fireball, Error) && Error.IsEmpty()
		&& RPGBossPhasesClusterAdapters::ValidatePhaseDependencies(Dependencies, FRPGPhaseFlowConfig().bUseRoarClip, Error) && Error.IsEmpty());
	AddInfo(TEXT("Reflection and defaults only; NOT a serialized asset and NOT seen in the Details panel."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPhasesClusterOracleTest, "OneBossFight.Binding.PhasesCluster.Oracle",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPhasesClusterOracleTest::RunTest(const FString& Parameters)
{
	using namespace PhasesClusterTests;
	FClusterTestWorld Scope;
	if (!TestNotNull(TEXT("test world"), Scope.World))
	{
		return false;
	}
	// The ten fields the older adapters own must receive exactly what their sequential use writes: the oracle is the accepted DD4 plus DD8 behavior, run on a second component from the same start state.
	struct FCase { const TCHAR* Name; FRPGParticipantConfig Config; };
	const auto DefaultsWithPhase = []() { FRPGParticipantConfig D; D.Phases = ConfigA().Phases; return D; };
	const FCase Cases[] = {{TEXT("config A"), ConfigA()}, {TEXT("config B"), ConfigB()}, {TEXT("authoring defaults with the selected phase of A"), DefaultsWithPhase()}};
	for (const FCase& Case : Cases)
	{
		AActor* OwnerOracle = Scope.SpawnOwner();
		AActor* OwnerCluster = Scope.SpawnOwner();
		if (!TestTrue(TEXT("two owners"), OwnerOracle && OwnerCluster))
		{
			return false;
		}
		TStrongObjectPtr<URPGBossPhases> Oracle = NewPhases(OwnerOracle, TEXT("RPGBossPhases"));
		TStrongObjectPtr<URPGBossPhases> Cluster = NewPhases(OwnerCluster, TEXT("RPGBossPhases"));
		if (!TestTrue(TEXT("two components"), Oracle.IsValid() && Cluster.IsValid()))
		{
			return false;
		}
		ArmDistinctStart(*Oracle);
		ArmDistinctStart(*Cluster);
		const FClusterState Start(*Cluster);
		FString OracleError;
		FString ClusterError;
		const bool bPhase = RPGBossPhaseAdapters::ConfigurePhases(*Oracle, Case.Config, SelectedId, OracleError);
		const bool bFlow = RPGBossPhaseFlowAdapters::ConfigurePhaseFlow(*Oracle, Case.Config, OracleError);
		const bool bCluster = RPGBossPhasesClusterAdapters::ConfigurePhasesCluster(*Cluster, Case.Config, SelectedId, ClusterError);
		TestTrue(FString::Printf(TEXT("%s: the older adapters and the cluster all accept"), Case.Name), bPhase && bFlow && bCluster);
		const FClusterState OracleState(*Oracle);
		const FClusterState ClusterState(*Cluster);
		TestTrue(FString::Printf(TEXT("%s: the ten phase and flow fields equal the sequential use of the older adapters"), Case.Name), ClusterState.PhaseAndFlowEquals(OracleState));
		TestTrue(FString::Printf(TEXT("%s: the older adapters leave the eight new fields at the start state, the cluster writes them"), Case.Name), OracleState.FireballAndDependenciesEqual(Start));
		TestTrue(FString::Printf(TEXT("%s: the cluster's eight new fields are the config's"), Case.Name), ClusterState.bFireballEnabled == Case.Config.Fireball.bFireballEnabled
			&& ClusterState.FireballAbility == Case.Config.Fireball.FireballAbility.ToSoftObjectPath() && ClusterState.FireballCooldown == Case.Config.Fireball.FireballCooldown
			&& ClusterState.FireballMinRange == Case.Config.Fireball.FireballMinRange && ClusterState.FireballMaxRange == Case.Config.Fireball.FireballMaxRange
			&& ClusterState.RoarClip == Case.Config.PhaseDependencies.RoarClip.ToSoftObjectPath() && ClusterState.TransitionMontage == Case.Config.PhaseDependencies.TransitionMontage.ToSoftObjectPath()
			&& ClusterState.ImmunityEffect == Case.Config.PhaseDependencies.ImmunityEffect.ToSoftObjectPath());
		TestTrue(FString::Printf(TEXT("%s: runtime state equal on both and equal to the start"), Case.Name), ClusterState.RuntimeEquals(OracleState) && ClusterState.RuntimeEquals(Start));
	}

	// Nothing is loaded: assigning the real default asset paths loads no object (the presence of each object in memory is the same before and after).
	{
		AActor* Owner = Scope.SpawnOwner();
		if (!TestNotNull(TEXT("owner actor"), Owner))
		{
			return false;
		}
		TStrongObjectPtr<URPGBossPhases> Phases = NewPhases(Owner, TEXT("RPGBossPhases"));
		if (!TestTrue(TEXT("component created"), Phases.IsValid()))
		{
			return false;
		}
		ArmDistinctStart(*Phases);
		const FRPGPhaseDependencyConfig RealDefaults;
		const FRPGFireballConfig RealFireball;
		const FSoftObjectPath RealPaths[] = {RealDefaults.RoarClip.ToSoftObjectPath(), RealDefaults.TransitionMontage.ToSoftObjectPath(), RealDefaults.ImmunityEffect.ToSoftObjectPath(), RealFireball.FireballAbility.ToSoftObjectPath()};
		bool bLoadedBefore[4];
		bool bPackageBefore[4];
		for (int32 Index = 0; Index < 4; ++Index)
		{
			bLoadedBefore[Index] = RealPaths[Index].ResolveObject() != nullptr;
			bPackageBefore[Index] = FindPackage(nullptr, *RealPaths[Index].GetLongPackageName()) != nullptr;
		}
		FRPGParticipantConfig Config = ConfigA();
		Config.PhaseDependencies = RealDefaults;
		Config.Fireball = RealFireball;
		FString Error;
		TestTrue(TEXT("the real default asset paths are accepted"), RPGBossPhasesClusterAdapters::ConfigurePhasesCluster(*Phases, Config, SelectedId, Error));
		bool bSame = true;
		for (int32 Index = 0; Index < 4; ++Index)
		{
			bSame = bSame && ((RealPaths[Index].ResolveObject() != nullptr) == bLoadedBefore[Index]) && ((FindPackage(nullptr, *RealPaths[Index].GetLongPackageName()) != nullptr) == bPackageBefore[Index]);
		}
		// Presence before and after is the witness: an asset that is already in memory proves nothing for its own path, but no path may gain an object or a package from the assignment.
		TestTrue(TEXT("neither an object nor a package of the referenced assets appeared during the assignment"), bSame);
	}
	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
