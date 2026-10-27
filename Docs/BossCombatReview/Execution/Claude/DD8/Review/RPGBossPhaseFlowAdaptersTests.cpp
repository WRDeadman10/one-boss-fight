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
#include "Player/RPGBossPhaseFlowAdapters.h"
#include "Player/RPGBossPhases.h"
#include "Player/RPGBossPosture.h"
#include "UObject/Package.h"
#include "UObject/StrongObjectPtr.h"
#include "UObject/UnrealType.h"
#include <limits>

// These tests prove the typed phase flow policy: its reflected authoring exposure, its copy into the immutable config by the real definition compiler (synthetic path, and the production path's early rejection),
// the shared validator, and the typed, lifecycle-safe assignment of exactly six fields on isolated native components. They do NOT prove a serialized asset value, anything seen in the Details panel, a production
// compile with a real skeleton, that any ability matches the prefix or that the leap tag is registered (the prefix and the tag are explicit identity only), the roar and montage dependencies, a real phase transition,
// a duel or any wiring. The defaults are the documented source-declaration defaults of the new asset field, compared with the native declarations only as a baseline. No Phases tick or transition runs here; the one
// BeginPlay that runs (the begun-component guard) loads nothing because the three soft asset pointers it would load are cleared first.

namespace
{
namespace PhaseFlowTests
{
	using FEpochPtr = TSharedPtr<const RPGCombatRegistry::FEpoch>;
	using FConfigPtr = TSharedPtr<const FRPGParticipantConfig>;

	constexpr float QuietNaN = std::numeric_limits<float>::quiet_NaN();
	constexpr float PosInf = std::numeric_limits<float>::infinity();

	/** Test-local game world with the set-up the earlier headless tests used; destroyed with the scope. */
	struct FPhaseFlowTestWorld
	{
		UWorld* World = nullptr;

		FPhaseFlowTestWorld()
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

		~FPhaseFlowTestWorld()
		{
			if (World)
			{
				GEngine->DestroyWorldContext(World);
				World->DestroyWorld(/*bInformEngineOfWorld=*/false);
			}
		}

		FPhaseFlowTestWorld(const FPhaseFlowTestWorld&) = delete;
		FPhaseFlowTestWorld& operator=(const FPhaseFlowTestWorld&) = delete;

		AActor* SpawnOwner() const { return World ? World->SpawnActor<AActor>() : nullptr; }
	};

	/** Exact comparison of the six fields: the string is compared CASE-SENSITIVELY (FString operator== ignores case), so "stored exactly as authored" is really tested. */
	bool FlowEquals(const FRPGPhaseFlowConfig& A, const FRPGPhaseFlowConfig& B)
	{
		return A.TransitionSeconds == B.TransitionSeconds && A.bUseRoarClip == B.bUseRoarClip && A.bPausePostureInTransition == B.bPausePostureInTransition
			&& A.bLockLeapUntilPhaseTwo == B.bLockLeapUntilPhaseTwo && A.AttackAbilityPrefix.Equals(B.AttackAbilityPrefix, ESearchCase::CaseSensitive) && A.LeapAbilityTag == B.LeapAbilityTag;
	}

	FRPGPhaseFlowConfig ReadFlow(const URPGBossPhases& P)
	{
		FRPGPhaseFlowConfig F;
		F.TransitionSeconds = P.TransitionSeconds;
		F.bUseRoarClip = P.bUseRoarClip;
		F.bPausePostureInTransition = P.bPausePostureInTransition;
		F.bLockLeapUntilPhaseTwo = P.bLockLeapUntilPhaseTwo;
		F.AttackAbilityPrefix = P.AttackAbilityPrefix;
		F.LeapAbilityTag = P.LeapAbilityTag;
		return F;
	}

	/** Seven distinct non-default values in one record: duration, prefix, tag and all three bools differ from the defaults (the bools are all false, the defaults true). */
	FRPGPhaseFlowConfig NondefaultFlowA()
	{
		FRPGPhaseFlowConfig F;
		F.TransitionSeconds = 3.25f;
		F.bUseRoarClip = false;
		F.bPausePostureInTransition = false;
		F.bLockLeapUntilPhaseTwo = false;
		F.AttackAbilityPrefix = TEXT("GA_Custom_Boss_");
		F.LeapAbilityTag = TEXT("Custom.Leap.Tag");
		return F;
	}

	/** A second, different record: zero duration (valid), a prefix with surrounding spaces (kept exactly), a tag that is registered nowhere, and a different bool mix. */
	FRPGPhaseFlowConfig NondefaultFlowB()
	{
		FRPGPhaseFlowConfig F;
		F.TransitionSeconds = 0.f;
		F.bUseRoarClip = true;
		F.bPausePostureInTransition = false;
		F.bLockLeapUntilPhaseTwo = true;
		F.AttackAbilityPrefix = TEXT(" GA_Spaced_ ");
		F.LeapAbilityTag = TEXT("Never.Registered.Test.Tag");
		return F;
	}

	/** Everything a failed call must leave alone and a successful one must leave alone except the six flow fields: the selected phase record (owned by the phase adapter), the fireball fields, the soft asset
	 *  references and the public runtime state. */
	struct FPhaseState
	{
		FRPGPhaseFlowConfig Flow;
		float PhaseTwoHealthFraction, MovementScale, AttackRateScale, DamageScale, FireballMinRange, FireballMaxRange;
		bool bFireballEnabled;
		FVector2D FireballCooldown;
		FSoftObjectPath RoarClip, TransitionMontage, ImmunityEffect, FireballAbility;
		FString RoarSourceName;
		bool bLeapBlocked, bPhaseTwo, bInTransition;
		int32 FireballCount, PhaseTwoCount, QueuedStarts;
		double LastTransitionStart;

		explicit FPhaseState(const URPGBossPhases& P)
			: Flow(ReadFlow(P)), PhaseTwoHealthFraction(P.PhaseTwoHealthFraction), MovementScale(P.MovementScale), AttackRateScale(P.AttackRateScale), DamageScale(P.DamageScale)
			, FireballMinRange(P.FireballMinRange), FireballMaxRange(P.FireballMaxRange), bFireballEnabled(P.bFireballEnabled), FireballCooldown(P.FireballCooldown)
			, RoarClip(P.RoarClip.ToSoftObjectPath()), TransitionMontage(P.TransitionMontage.ToSoftObjectPath()), ImmunityEffect(P.ImmunityEffect.ToSoftObjectPath()), FireballAbility(P.FireballAbility.ToSoftObjectPath())
			, RoarSourceName(P.GetRoarSourceName()), bLeapBlocked(P.IsLeapBlocked()), bPhaseTwo(P.IsPhaseTwo()), bInTransition(P.IsInTransition()), FireballCount(P.GetFireballCount())
			, PhaseTwoCount(P.GetPhaseTwoCount()), QueuedStarts(P.GetQueuedStartCount()), LastTransitionStart(P.GetLastTransitionStartTime())
		{
		}

		bool OutsideEquals(const FPhaseState& O) const
		{
			return PhaseTwoHealthFraction == O.PhaseTwoHealthFraction && MovementScale == O.MovementScale && AttackRateScale == O.AttackRateScale && DamageScale == O.DamageScale
				&& FireballMinRange == O.FireballMinRange && FireballMaxRange == O.FireballMaxRange && bFireballEnabled == O.bFireballEnabled && FireballCooldown == O.FireballCooldown
				&& RoarClip == O.RoarClip && TransitionMontage == O.TransitionMontage && ImmunityEffect == O.ImmunityEffect && FireballAbility == O.FireballAbility
				&& RoarSourceName.Equals(O.RoarSourceName, ESearchCase::CaseSensitive) && bLeapBlocked == O.bLeapBlocked && bPhaseTwo == O.bPhaseTwo && bInTransition == O.bInTransition
				&& FireballCount == O.FireballCount && PhaseTwoCount == O.PhaseTwoCount && QueuedStarts == O.QueuedStarts && LastTransitionStart == O.LastTransitionStart;
		}

		bool operator==(const FPhaseState& O) const { return FlowEquals(Flow, O.Flow) && OutsideEquals(O); }
	};

	/** Sentinels the flow policy must never touch: non-default values for the phase-adapter-owned scalars and for the fireball fields. */
	void ArmSentinels(URPGBossPhases& Phases)
	{
		Phases.PhaseTwoHealthFraction = 0.42f;
		Phases.MovementScale = 1.7f;
		Phases.AttackRateScale = 1.8f;
		Phases.DamageScale = 1.9f;
		Phases.bFireballEnabled = true;
		Phases.FireballMinRange = 777.f;
		Phases.FireballMaxRange = 888.f;
		Phases.FireballCooldown = FVector2D(3.f, 4.f);
	}

	FRPGParticipantConfig MakeConfig(const FRPGPhaseFlowConfig& Flow)
	{
		FRPGParticipantConfig Config;
		Config.PhaseFlow = Flow;
		return Config;
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

	/** A valid definition for the real synthetic compiler, with a typed phase flow. */
	TStrongObjectPtr<URPGBossDefinition> MakeDefinition(const FRPGPhaseFlowConfig& Flow)
	{
		TStrongObjectPtr<URPGBossDefinition> Definition(NewObject<URPGBossDefinition>());
		Definition->DefinitionId = TEXT("Synthetic");
		Definition->PresentationId = TEXT("SyntheticLook");
		Definition->Stats.MaxHealth = 3500.f;
		Definition->Stats.MaxPosture = 73.5f;
		Definition->Stats.PostureRegenDelay = 4.25f;
		Definition->Stats.PostureRegenRate = 9.75f;
		FRPGPhaseConfig Phase;
		Phase.PhaseId = TEXT("PhaseTwo");
		Phase.EntryHealthFraction = 0.35f;
		Phase.SpeedMultiplier = 1.5f;
		Phase.RateMultiplier = 1.75f;
		Phase.AttackMultiplier = 2.f;
		Definition->Phases.Add(Phase);
		Definition->PhaseFlow = Flow;
		Definition->Fields.Add(MakeField(RPGBossPhaseFlowAdapters::FieldTransitionSeconds, TEXT("synthetic")));
		Definition->Fields.Add(MakeField(RPGBossPhaseFlowAdapters::FieldLeapAbilityTag, TEXT("synthetic")));
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
}
}

// No file-scope using-directive on purpose (the module builds without unity, but a local using-directive costs nothing): each test body names its namespace itself.

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPhaseFlowAssignTest, "OneBossFight.Binding.PhaseFlow.Assign",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPhaseFlowAssignTest::RunTest(const FString& Parameters)
{
	using namespace PhaseFlowTests;
	FPhaseFlowTestWorld Scope;
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
	ArmSentinels(*Phases);
	const FPhaseState Before(*Phases);
	const int32 OwnedComponentsBefore = Owner->GetComponents().Num();

	// Record A really differs from the defaults in every field, and record B in the bool mix.
	const FRPGPhaseFlowConfig Defaults;
	const FRPGPhaseFlowConfig A = NondefaultFlowA();
	const FRPGPhaseFlowConfig B = NondefaultFlowB();
	TestTrue(TEXT("record A: the duration, the three bools, the prefix and the tag all differ from the authoring defaults"),
		A.TransitionSeconds != Defaults.TransitionSeconds && A.bUseRoarClip != Defaults.bUseRoarClip && A.bPausePostureInTransition != Defaults.bPausePostureInTransition
		&& A.bLockLeapUntilPhaseTwo != Defaults.bLockLeapUntilPhaseTwo && !A.AttackAbilityPrefix.Equals(Defaults.AttackAbilityPrefix, ESearchCase::CaseSensitive) && A.LeapAbilityTag != Defaults.LeapAbilityTag);

	// The unwired plan fragment: the legacy instance name, the exact class and the six typed paths in field order.
	const FRPGComponentPlan Plan = RPGBossPhaseFlowAdapters::MakePhaseFlowPlan();
	TestTrue(TEXT("plan class"), Plan.Class == URPGBossPhases::StaticClass());
	TestTrue(TEXT("plan instance name"), Plan.InstanceName == FName(TEXT("RPGBossPhases")));
	TestTrue(TEXT("plan required fields are the six typed paths"), Plan.RequiredFields == TArray<FString>{
		TEXT("PhaseFlow.TransitionSeconds"), TEXT("PhaseFlow.bUseRoarClip"), TEXT("PhaseFlow.bPausePostureInTransition"), TEXT("PhaseFlow.bLockLeapUntilPhaseTwo"),
		TEXT("PhaseFlow.AttackAbilityPrefix"), TEXT("PhaseFlow.LeapAbilityTag")});
	if (!TestTrue(TEXT("plan callback is set"), static_cast<bool>(Plan.Configure)))
	{
		return false;
	}

	// Record A through the plan callback, with a manifest whose Value TEXT says something else: only the typed record counts.
	FRPGParticipantConfig Config = MakeConfig(A);
	Config.Fields.Add(MakeField(RPGBossPhaseFlowAdapters::FieldTransitionSeconds, TEXT("9999")));
	Config.Fields.Add(MakeField(RPGBossPhaseFlowAdapters::FieldAttackAbilityPrefix, TEXT("FROM_THE_MANIFEST_")));
	Config.Fields.Add(MakeField(RPGBossPhaseFlowAdapters::FieldUseRoarClip, TEXT("true")));
	FString Error = TEXT("a stale diagnostic from an earlier call");
	TestTrue(TEXT("callback succeeds"), Plan.Configure(*Phases, Config, Error));
	TestTrue(TEXT("the diagnostic was cleared on success"), Error.IsEmpty());
	TestTrue(TEXT("all six fields are the typed record, not the manifest text"), FlowEquals(ReadFlow(*Phases), A));

	// Exactly six assignments: the selected phase record, the fireball fields, the soft references and the runtime state equal their pre-call values (sentinels included).
	FPhaseState Expected = Before;
	Expected.Flow = A;
	TestTrue(TEXT("nothing but the six flow fields changed"), FPhaseState(*Phases) == Expected);
	TestTrue(TEXT("phase-adapter-owned scalars and fireball sentinels untouched"), Phases->PhaseTwoHealthFraction == 0.42f && Phases->MovementScale == 1.7f && Phases->AttackRateScale == 1.8f && Phases->DamageScale == 1.9f
		&& Phases->bFireballEnabled && Phases->FireballMinRange == 777.f && Phases->FireballMaxRange == 888.f && Phases->FireballCooldown == FVector2D(3.f, 4.f));
	TestFalse(TEXT("no phase trigger: not phase two, not in transition, leap not blocked by this call"), Phases->IsPhaseTwo() || Phases->IsInTransition() || Phases->IsLeapBlocked());

	// The callback created nothing, registered nothing and began nothing.
	TestFalse(TEXT("component stays unregistered"), Phases->IsRegistered());
	TestFalse(TEXT("component did not begin play"), Phases->HasBegunPlay());
	TestFalse(TEXT("owner did not begin play"), Owner->HasActorBegunPlay());
	TestTrue(TEXT("owner gained no component"), Owner->GetComponents().Num() == OwnedComponentsBefore);

	// Record B through the direct helper: zero duration valid, the prefix with surrounding spaces stored exactly as authored (never trimmed), a tag that is registered nowhere accepted (identity only).
	TestTrue(TEXT("record B"), RPGBossPhaseFlowAdapters::ConfigurePhaseFlow(*Phases, MakeConfig(B), Error) && FlowEquals(ReadFlow(*Phases), B));
	TestTrue(TEXT("the authored prefix is stored exactly, spaces and case included"), Phases->AttackAbilityPrefix.Equals(TEXT(" GA_Spaced_ "), ESearchCase::CaseSensitive));
	TestTrue(TEXT("zero duration stored"), Phases->TransitionSeconds == 0.f);

	// All eight combinations of the three bools are copied, each with the other three fields kept distinct from the defaults.
	for (int32 Mask = 0; Mask < 8; ++Mask)
	{
		FRPGPhaseFlowConfig Flow = A;
		Flow.bUseRoarClip = (Mask & 1) != 0;
		Flow.bPausePostureInTransition = (Mask & 2) != 0;
		Flow.bLockLeapUntilPhaseTwo = (Mask & 4) != 0;
		TestTrue(FString::Printf(TEXT("bool combination %d copied"), Mask), RPGBossPhaseFlowAdapters::ConfigurePhaseFlow(*Phases, MakeConfig(Flow), Error) && FlowEquals(ReadFlow(*Phases), Flow));
	}
	FPhaseState ExpectedLast = Before;
	ExpectedLast.Flow = ReadFlow(*Phases);
	TestTrue(TEXT("still nothing but the six fields changed after all combinations"), FPhaseState(*Phases) == ExpectedLast);

	AddInfo(TEXT("Typed phase flow assignment only; NOT a phase transition, NOT the roar or montage dependencies, NOT an ability or tag match, NOT a serialized asset value, NOT a duel."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPhaseFlowValidationTest, "OneBossFight.Binding.PhaseFlow.Validation",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPhaseFlowValidationTest::RunTest(const FString& Parameters)
{
	using namespace PhaseFlowTests;
	FPhaseFlowTestWorld Scope;
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
	ArmSentinels(*Phases);
	const FPhaseState Before(*Phases);
	const FRPGPhaseFlowConfig Base = NondefaultFlowA(); // valid, every field non-default

	// One check: the validator refuses (or accepts) the record with that token and field path, and the assignment does the same with NO write at all.
	auto Check = [&](const FString& Label, const FRPGPhaseFlowConfig& Flow, const TCHAR* ExpectedToken, const FString& ExpectedPath)
	{
		FString Error = TEXT("a stale diagnostic");
		const bool bOk = RPGBossPhaseFlowAdapters::ValidatePhaseFlow(Flow, Error);
		if (!ExpectedToken)
		{
			TestTrue(FString::Printf(TEXT("%s: valid, and the diagnostic was cleared"), *Label), bOk && Error.IsEmpty());
			return;
		}
		TestFalse(FString::Printf(TEXT("%s: rejected"), *Label), bOk);
		TestTrue(FString::Printf(TEXT("%s: named %s (got '%s')"), *Label, ExpectedToken, *Error), Error.StartsWith(ExpectedToken));
		TestTrue(FString::Printf(TEXT("%s: names the field %s"), *Label, *ExpectedPath), Error.Contains(ExpectedPath));
		FString ConfigureError = TEXT("a stale diagnostic");
		TestFalse(FString::Printf(TEXT("%s: the assignment refuses"), *Label), RPGBossPhaseFlowAdapters::ConfigurePhaseFlow(*Phases, MakeConfig(Flow), ConfigureError));
		TestTrue(FString::Printf(TEXT("%s: the assignment names the same token"), *Label), ConfigureError.StartsWith(ExpectedToken));
		TestTrue(FString::Printf(TEXT("%s: no write at all (six fields, sentinels, state)"), *Label), FPhaseState(*Phases) == Before);
	};
	auto WithSeconds = [&](float V) { FRPGPhaseFlowConfig F = Base; F.TransitionSeconds = V; return F; };
	auto WithPrefix = [&](const TCHAR* V) { FRPGPhaseFlowConfig F = Base; F.AttackAbilityPrefix = V; return F; };
	auto WithTag = [&](FName V) { FRPGPhaseFlowConfig F = Base; F.LeapAbilityTag = V; return F; };
	const FString Seconds = RPGBossPhaseFlowAdapters::FieldTransitionSeconds;
	const FString Prefix = RPGBossPhaseFlowAdapters::FieldAttackAbilityPrefix;
	const FString Tag = RPGBossPhaseFlowAdapters::FieldLeapAbilityTag;

	Check(TEXT("the base record"), Base, nullptr, FString());
	Check(TEXT("the authoring defaults"), FRPGPhaseFlowConfig(), nullptr, FString());

	// The duration: not finite wherever it is, negative just below zero, and valid at zero and at values below the native editor minimum (no invented floor).
	Check(TEXT("TransitionSeconds NaN"), WithSeconds(QuietNaN), TEXT("InvalidPhaseFlow.NotFinite"), Seconds);
	Check(TEXT("TransitionSeconds +Inf"), WithSeconds(PosInf), TEXT("InvalidPhaseFlow.NotFinite"), Seconds);
	Check(TEXT("TransitionSeconds -Inf"), WithSeconds(-PosInf), TEXT("InvalidPhaseFlow.NotFinite"), Seconds);
	Check(TEXT("TransitionSeconds -0.0001"), WithSeconds(-0.0001f), TEXT("InvalidPhaseFlow.Negative"), Seconds);
	Check(TEXT("TransitionSeconds -1"), WithSeconds(-1.f), TEXT("InvalidPhaseFlow.Negative"), Seconds);
	Check(TEXT("TransitionSeconds 0 (valid)"), WithSeconds(0.f), nullptr, FString());
	Check(TEXT("TransitionSeconds -0.0 (valid, it is zero)"), WithSeconds(-0.f), nullptr, FString());
	Check(TEXT("TransitionSeconds 0.001 (valid, fractional)"), WithSeconds(0.001f), nullptr, FString());
	Check(TEXT("TransitionSeconds 0.19 (valid: below the native editor ClampMin 0.2, no invented floor)"), WithSeconds(0.19f), nullptr, FString());
	Check(TEXT("TransitionSeconds 1.8 (valid, the default)"), WithSeconds(1.8f), nullptr, FString());
	Check(TEXT("TransitionSeconds 1e6 (valid, no invented ceiling)"), WithSeconds(1.0e6f), nullptr, FString());

	// The prefix: empty or only whitespace is refused; everything else is valid, whatever it looks like (identity only).
	Check(TEXT("prefix empty"), WithPrefix(TEXT("")), TEXT("InvalidPhaseFlow.EmptyPrefix"), Prefix);
	Check(TEXT("prefix one space"), WithPrefix(TEXT(" ")), TEXT("InvalidPhaseFlow.EmptyPrefix"), Prefix);
	Check(TEXT("prefix several spaces"), WithPrefix(TEXT("     ")), TEXT("InvalidPhaseFlow.EmptyPrefix"), Prefix);
	Check(TEXT("prefix a tab"), WithPrefix(TEXT("\t")), TEXT("InvalidPhaseFlow.EmptyPrefix"), Prefix);
	Check(TEXT("prefix a newline"), WithPrefix(TEXT("\n")), TEXT("InvalidPhaseFlow.EmptyPrefix"), Prefix);
	Check(TEXT("prefix mixed whitespace"), WithPrefix(TEXT(" \t\r\n ")), TEXT("InvalidPhaseFlow.EmptyPrefix"), Prefix);
	Check(TEXT("prefix one character (valid)"), WithPrefix(TEXT("G")), nullptr, FString());
	Check(TEXT("prefix with surrounding spaces (valid, kept as authored)"), WithPrefix(TEXT("  GA_  ")), nullptr, FString());
	Check(TEXT("prefix with an inner space (valid)"), WithPrefix(TEXT("GA B")), nullptr, FString());

	// The tag: None is refused; any other name is valid, registered or not (identity only, nothing is registered or requested).
	Check(TEXT("tag None"), WithTag(NAME_None), TEXT("InvalidPhaseFlow.NoLeapTag"), Tag);
	Check(TEXT("tag default-constructed name"), WithTag(FName()), TEXT("InvalidPhaseFlow.NoLeapTag"), Tag);
	Check(TEXT("tag Ability.Melee.LeapAttack (valid)"), WithTag(FName(TEXT("Ability.Melee.LeapAttack"))), nullptr, FString());
	Check(TEXT("tag that is registered nowhere (valid: identity only)"), WithTag(FName(TEXT("Never.Registered.Test.Tag"))), nullptr, FString());
	Check(TEXT("tag one plain word (valid)"), WithTag(FName(TEXT("X"))), nullptr, FString());

	// No partial write whichever field is invalid: first, middle and last of otherwise valid non-default records, with the scalar, the three bools, the prefix and the tag all non-default.
	Check(TEXT("only the FIRST field invalid (TransitionSeconds NaN), five others valid and non-default"), WithSeconds(QuietNaN), TEXT("InvalidPhaseFlow.NotFinite"), Seconds);
	Check(TEXT("only a MIDDLE field invalid (empty prefix), the duration and three bools valid and non-default"), WithPrefix(TEXT("")), TEXT("InvalidPhaseFlow.EmptyPrefix"), Prefix);
	Check(TEXT("only the LAST field invalid (tag None), the scalar, three bools and prefix valid and non-default"), WithTag(NAME_None), TEXT("InvalidPhaseFlow.NoLeapTag"), Tag);

	// Precedence: finite, then not negative, then the prefix, then the tag.
	{
		FRPGPhaseFlowConfig F = Base;
		F.TransitionSeconds = -1.f;
		F.AttackAbilityPrefix = TEXT("");
		F.LeapAbilityTag = NAME_None;
		Check(TEXT("negative duration, empty prefix and no tag: the duration is reported first"), F, TEXT("InvalidPhaseFlow.Negative"), Seconds);
		F.TransitionSeconds = QuietNaN;
		Check(TEXT("NaN duration outranks everything"), F, TEXT("InvalidPhaseFlow.NotFinite"), Seconds);
		F = Base;
		F.AttackAbilityPrefix = TEXT("   ");
		F.LeapAbilityTag = NAME_None;
		Check(TEXT("whitespace prefix and no tag: the prefix is reported first"), F, TEXT("InvalidPhaseFlow.EmptyPrefix"), Prefix);
	}

	// The component refused every record above and is still configurable.
	FString Error;
	TestTrue(TEXT("after all refusals a valid record still configures"), RPGBossPhaseFlowAdapters::ConfigurePhaseFlow(*Phases, MakeConfig(Base), Error) && FlowEquals(ReadFlow(*Phases), Base));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPhaseFlowIsolationTest, "OneBossFight.Binding.PhaseFlow.Isolation",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPhaseFlowIsolationTest::RunTest(const FString& Parameters)
{
	using namespace PhaseFlowTests;
	FPhaseFlowTestWorld Scope;
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
	FRPGParticipantConfig ConfigA = MakeConfig(NondefaultFlowA());
	const FRPGParticipantConfig ConfigB = MakeConfig(NondefaultFlowB());
	FString Error;
	TestTrue(TEXT("A"), RPGBossPhaseFlowAdapters::ConfigurePhaseFlow(*A, ConfigA, Error));
	const FPhaseState SnapshotA(*A);
	TestTrue(TEXT("B"), RPGBossPhaseFlowAdapters::ConfigurePhaseFlow(*B, ConfigB, Error));
	TestTrue(TEXT("configuring B did not change A"), FPhaseState(*A) == SnapshotA);
	TestTrue(TEXT("B has its own six values"), FlowEquals(ReadFlow(*B), NondefaultFlowB()));

	// The assignment copies values: changing the config afterwards changes nothing (the string included).
	ConfigA.PhaseFlow.TransitionSeconds = 99.f;
	ConfigA.PhaseFlow.AttackAbilityPrefix = TEXT("CHANGED_AFTERWARDS");
	ConfigA.PhaseFlow.LeapAbilityTag = TEXT("Changed.Afterwards");
	ConfigA.PhaseFlow.bUseRoarClip = true;
	TestTrue(TEXT("a later config change does not reach A"), FPhaseState(*A) == SnapshotA);

	// A component that was never configured keeps the native declarations, and so does the class default object.
	const FRPGPhaseFlowConfig Defaults;
	TestTrue(TEXT("untouched component keeps the declared defaults"), FlowEquals(ReadFlow(*C), Defaults));
	TestTrue(TEXT("CDO keeps the declared defaults"), FlowEquals(ReadFlow(*GetDefault<URPGBossPhases>()), Defaults));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPhaseFlowRejectionsTest, "OneBossFight.Binding.PhaseFlow.Rejections",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPhaseFlowRejectionsTest::RunTest(const FString& Parameters)
{
	using namespace PhaseFlowTests;
	FPhaseFlowTestWorld Scope;
	if (!TestNotNull(TEXT("test world"), Scope.World))
	{
		return false;
	}
	const FRPGParticipantConfig Config = MakeConfig(NondefaultFlowA()); // valid: every failure below is about the component or the owner
	FString Error;

	// A rejected call changes nothing and names the reason. Wrong-class targets are concrete classes (UActorComponent itself is abstract).
	auto ExpectRejected = [&](const TCHAR* Label, UActorComponent& Component, const TCHAR* Token)
	{
		const URPGBossPhases* AsPhases = Cast<URPGBossPhases>(&Component);
		const URPGBossEncounter* AsEncounter = Cast<URPGBossEncounter>(&Component);
		const URPGBossPosture* AsPosture = Cast<URPGBossPosture>(&Component);
		TOptional<FPhaseState> Before;
		if (AsPhases) { Before.Emplace(*AsPhases); }
		const float EncounterGateBefore = AsEncounter ? AsEncounter->GateRadius : 0.f;
		const float PostureMaxBefore = AsPosture ? AsPosture->PostureMax : 0.f;
		const bool bOk = RPGBossPhaseFlowAdapters::ConfigurePhaseFlow(Component, Config, Error);
		TestFalse(FString::Printf(TEXT("%s: rejected"), Label), bOk);
		TestTrue(FString::Printf(TEXT("%s: named %s (got '%s')"), Label, Token, *Error), Error.StartsWith(Token));
		if (Before.IsSet()) { TestTrue(FString::Printf(TEXT("%s: phases unchanged (sentinels included)"), Label), FPhaseState(*AsPhases) == Before.GetValue()); }
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
		ExpectRejected(TEXT("flow on a posture"), *Posture, TEXT("WrongComponentClass"));
		ExpectRejected(TEXT("flow on an encounter"), *Encounter, TEXT("WrongComponentClass"));
		ExpectRejected(TEXT("flow on a scene component"), *Scene, TEXT("WrongComponentClass"));
	}

	// Already registered (the owner has not begun play, so registration alone does not begin play for the component).
	{
		TStrongObjectPtr<URPGBossPhases> Phases = NewPhases(Owner, TEXT("RegisteredPhases"));
		if (!TestTrue(TEXT("registered component created"), Phases.IsValid()))
		{
			return false;
		}
		ArmSentinels(*Phases);
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
		ArmSentinels(*Phases);
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
		ArmSentinels(*Phases);
		ExpectRejected(TEXT("phases under a begun owner"), *Phases, TEXT("OwnerBegunPlay"));
	}

	// Invalid owner: the component's outer is not an actor.
	{
		TStrongObjectPtr<URPGBossPhases> Phases(NewObject<URPGBossPhases>(GetTransientPackage(), TEXT("OrphanPhases")));
		if (!TestTrue(TEXT("orphan component created"), Phases.IsValid() && !Phases->GetOwner()))
		{
			return false;
		}
		ArmSentinels(*Phases);
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
		ArmSentinels(*Phases);
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
		ExpectRejected(TEXT("flow on a destroyed posture"), *Posture, TEXT("InvalidComponent"));
		TestTrue(TEXT("the owner stayed live through both calls"), IsValid(LiveOwner) && !LiveOwner->IsActorBeingDestroyed());
	}

	AddInfo(TEXT("Rejection paths on isolated actors; an owner that is being destroyed is covered by the code (IsActorBeingDestroyed) but not exercised here."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPhaseFlowCompileTest, "OneBossFight.Binding.PhaseFlow.Compile",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPhaseFlowCompileTest::RunTest(const FString& Parameters)
{
	using namespace PhaseFlowTests;
	const FEpochPtr Content = RPGCombatRegistry::Legacy();
	if (!TestTrue(TEXT("content epoch"), Content.IsValid() && Content->Id.IsValid()))
	{
		return false;
	}

	// The real synthetic compiler copies all six fields into the immutable config; the string is compared case-sensitively and keeps its surrounding spaces.
	{
		const TStrongObjectPtr<URPGBossDefinition> Definition = MakeDefinition(NondefaultFlowA());
		FConfigPtr Out;
		const FRPGHydrationResult Result = CompileSynthetic(*Definition, Content, Out);
		if (!TestTrue(TEXT("a valid definition compiles"), Result.IsReady() && Out.IsValid()))
		{
			return false;
		}
		TestTrue(TEXT("all six fields copied (record A)"), FlowEquals(Out->PhaseFlow, NondefaultFlowA()));
		TestTrue(TEXT("established Stats, phase and identity values retained"), Out->Stats.MaxHealth == 3500.f && Out->Phases.Num() == 1 && Out->BossId == FName(TEXT("Synthetic")) && Out->bSyntheticFixture);
		TestTrue(TEXT("the encounter policy and the stagger policy still carry their authoring defaults next to it"), Out->EncounterPolicy.GateRadius == 1200.f && Out->StaggerPolicy.StaggerSeconds == 2.5f);
		// The config is a value snapshot: changing the definition afterwards changes nothing.
		Definition->PhaseFlow.TransitionSeconds = 99.f;
		Definition->PhaseFlow.AttackAbilityPrefix = TEXT("CHANGED_AFTERWARDS");
		TestTrue(TEXT("a later definition change does not reach the compiled config"), FlowEquals(Out->PhaseFlow, NondefaultFlowA()));
	}
	{
		const TStrongObjectPtr<URPGBossDefinition> Definition = MakeDefinition(NondefaultFlowB());
		FConfigPtr Out;
		TestTrue(TEXT("record B compiles (zero duration, spaced prefix kept exactly, an unregistered tag)"), CompileSynthetic(*Definition, Content, Out).IsReady() && Out.IsValid() && FlowEquals(Out->PhaseFlow, NondefaultFlowB()));
	}
	// A definition whose phase flow was never authored receives the additive authoring defaults, and the compiled config carries them.
	{
		TStrongObjectPtr<URPGBossDefinition> Definition = MakeDefinition(NondefaultFlowA());
		Definition->PhaseFlow = FRPGPhaseFlowConfig(); // what an old schema 1 definition holds: the field's own defaults
		FConfigPtr Out;
		TestTrue(TEXT("untouched flow: the authoring defaults are copied"), CompileSynthetic(*Definition, Content, Out).IsReady() && Out.IsValid() && FlowEquals(Out->PhaseFlow, FRPGPhaseFlowConfig()));
	}

	// An invalid flow fails by name, is NEVER replaced by the defaults, trimmed or normalized, and clears a previously valid output; the production compile refuses it before any asset is loaded.
	struct FBad
	{
		const TCHAR* Name;
		TFunction<void(FRPGPhaseFlowConfig&)> Break;
		const TCHAR* Token;
	};
	const FBad Bad[] = {
		{TEXT("NaN transition seconds"), [](FRPGPhaseFlowConfig& F) { F.TransitionSeconds = QuietNaN; }, TEXT("InvalidPhaseFlow.NotFinite")},
		{TEXT("negative transition seconds"), [](FRPGPhaseFlowConfig& F) { F.TransitionSeconds = -1.f; }, TEXT("InvalidPhaseFlow.Negative")},
		{TEXT("empty prefix"), [](FRPGPhaseFlowConfig& F) { F.AttackAbilityPrefix = TEXT(""); }, TEXT("InvalidPhaseFlow.EmptyPrefix")},
		{TEXT("whitespace-only prefix"), [](FRPGPhaseFlowConfig& F) { F.AttackAbilityPrefix = TEXT("  \t "); }, TEXT("InvalidPhaseFlow.EmptyPrefix")},
		{TEXT("no leap tag"), [](FRPGPhaseFlowConfig& F) { F.LeapAbilityTag = NAME_None; }, TEXT("InvalidPhaseFlow.NoLeapTag")},
	};
	for (const FBad& Case : Bad)
	{
		FRPGPhaseFlowConfig Flow = NondefaultFlowA();
		Case.Break(Flow);
		const TStrongObjectPtr<URPGBossDefinition> Definition = MakeDefinition(Flow);

		FConfigPtr Out;
		if (!TestTrue(FString::Printf(TEXT("%s: a valid output exists first"), Case.Name), CompileSynthetic(*MakeDefinition(NondefaultFlowA()), Content, Out).IsReady() && Out.IsValid()))
		{
			return false;
		}
		const FRPGHydrationResult Result = CompileSynthetic(*Definition, Content, Out); // the same output variable
		TestFalse(FString::Printf(TEXT("%s (synthetic compile): refused"), Case.Name), Result.IsReady());
		TestTrue(FString::Printf(TEXT("%s (synthetic compile): named %s"), Case.Name, Case.Token), AnyErrorContains(Result, Case.Token));
		TestFalse(FString::Printf(TEXT("%s (synthetic compile): the earlier valid output was cleared, nothing defaulted"), Case.Name), Out.IsValid());

		FConfigPtr ProductionOut;
		if (CompileSynthetic(*MakeDefinition(NondefaultFlowA()), Content, ProductionOut).IsReady() && ProductionOut.IsValid())
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

	// The established checks are retained, with a valid phase flow; each failure clears a previously valid output.
	auto RunRetained = [&](const TCHAR* Name, const TCHAR* Text, const TFunction<void(URPGBossDefinition&)>& Break, int32 Schema, const FString& Hash, bool bNullContent)
	{
		FConfigPtr Out;
		if (!CompileSynthetic(*MakeDefinition(NondefaultFlowA()), Content, Out).IsReady() || !Out.IsValid())
		{
			AddError(TEXT("unsupported precondition: a valid output could not be built"));
			return;
		}
		const TStrongObjectPtr<URPGBossDefinition> Definition = MakeDefinition(NondefaultFlowA()); // a valid phase flow
		Definition->Schema = Schema;
		Break(*Definition);
		const FRPGHydrationResult Result = CompileSynthetic(*Definition, bNullContent ? FEpochPtr() : Content, Out, Hash);
		TestFalse(FString::Printf(TEXT("%s: still refused with a valid phase flow"), Name), Result.IsReady());
		TestTrue(FString::Printf(TEXT("%s: the established message '%s'"), Name, Text), AnyErrorContains(Result, Text));
		TestFalse(FString::Printf(TEXT("%s: the earlier valid output was cleared"), Name), Out.IsValid());
	};
	const FString GoodHash = FString::ChrN(64, TEXT('b'));
	RunRetained(TEXT("invalid stagger policy"), TEXT("InvalidStagger.NotPositive"), [](URPGBossDefinition& D) { D.StaggerPolicy.GetUpRate = 0.f; }, 1, GoodHash, false);
	RunRetained(TEXT("invalid encounter policy"), TEXT("InvalidPolicy.Negative"), [](URPGBossDefinition& D) { D.EncounterPolicy.GateRadius = -1.f; }, 1, GoodHash, false);
	RunRetained(TEXT("negative posture maximum"), TEXT("invalid stats"), [](URPGBossDefinition& D) { D.Stats.MaxPosture = -1.f; }, 1, GoodHash, false);
	RunRetained(TEXT("phase threshold above 1"), TEXT("invalid/duplicate phase"), [](URPGBossDefinition& D) { D.Phases[0].EntryHealthFraction = 2.f; }, 1, GoodHash, false);
	RunRetained(TEXT("schema 2"), TEXT("identity absent"), [](URPGBossDefinition&) {}, 2, GoodHash, false);
	RunRetained(TEXT("manifest hash that is not 64 hex characters"), TEXT("identity absent"), [](URPGBossDefinition&) {}, 1, TEXT("short"), false);
	RunRetained(TEXT("no content lease"), TEXT("identity absent"), [](URPGBossDefinition&) {}, 1, GoodHash, true);
	RunRetained(TEXT("no field manifest"), TEXT("field manifest required"), [](URPGBossDefinition& D) { D.Fields.Reset(); }, 1, GoodHash, false);

	// Several failures are all reported: an invalid phase flow together with an invalid stagger policy, encounter policy and stats.
	{
		FRPGPhaseFlowConfig Flow = NondefaultFlowA();
		Flow.LeapAbilityTag = NAME_None;
		const TStrongObjectPtr<URPGBossDefinition> Definition = MakeDefinition(Flow);
		Definition->StaggerPolicy.GetUpRate = -2.f;
		Definition->EncounterPolicy.GateRadius = -5.f;
		Definition->Stats.MaxPosture = -1.f;
		FConfigPtr Out;
		const FRPGHydrationResult Result = CompileSynthetic(*Definition, Content, Out);
		TestTrue(TEXT("invalid phase flow, stagger policy, encounter policy and stats are all reported"),
			!Result.IsReady() && AnyErrorContains(Result, TEXT("InvalidPhaseFlow.NoLeapTag")) && AnyErrorContains(Result, TEXT("InvalidStagger.NotPositive")) && AnyErrorContains(Result, TEXT("InvalidPolicy.Negative"))
			&& AnyErrorContains(Result, TEXT("invalid stats")) && !Out.IsValid());
	}

	AddInfo(TEXT("Real synthetic compiler and the production compile's early rejection; NO production compile with a real skeleton, NO serialized asset."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPhaseFlowAuthoringTest, "OneBossFight.Binding.PhaseFlow.Authoring",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPhaseFlowAuthoringTest::RunTest(const FString& Parameters)
{
	using namespace PhaseFlowTests;
	// The reflected record: the six fields exist with the native names, the right types, and are editable.
	const UScriptStruct* Struct = FRPGPhaseFlowConfig::StaticStruct();
	if (!TestNotNull(TEXT("the phase flow struct is reflected"), Struct))
	{
		return false;
	}
	const UClass* Native = URPGBossPhases::StaticClass();
	const FProperty* Seconds = Struct->FindPropertyByName(TEXT("TransitionSeconds"));
	TestTrue(TEXT("TransitionSeconds is a reflected, editable float property"), Seconds && CastField<FFloatProperty>(Seconds) && Seconds->HasAnyPropertyFlags(CPF_Edit));
	TestTrue(TEXT("TransitionSeconds also exists as a float property of URPGBossPhases"), CastField<FFloatProperty>(Native->FindPropertyByName(TEXT("TransitionSeconds"))) != nullptr);
	for (const TCHAR* BoolName : {TEXT("bUseRoarClip"), TEXT("bPausePostureInTransition"), TEXT("bLockLeapUntilPhaseTwo")})
	{
		const FProperty* Property = Struct->FindPropertyByName(BoolName);
		TestTrue(FString::Printf(TEXT("%s is a reflected, editable bool property"), BoolName), Property && CastField<FBoolProperty>(Property) && Property->HasAnyPropertyFlags(CPF_Edit));
		TestTrue(FString::Printf(TEXT("%s also exists as a bool property of URPGBossPhases"), BoolName), CastField<FBoolProperty>(Native->FindPropertyByName(BoolName)) != nullptr);
	}
	const FProperty* Prefix = Struct->FindPropertyByName(TEXT("AttackAbilityPrefix"));
	TestTrue(TEXT("AttackAbilityPrefix is a reflected, editable string property"), Prefix && CastField<FStrProperty>(Prefix) && Prefix->HasAnyPropertyFlags(CPF_Edit));
	TestTrue(TEXT("AttackAbilityPrefix also exists as a string property of URPGBossPhases"), CastField<FStrProperty>(Native->FindPropertyByName(TEXT("AttackAbilityPrefix"))) != nullptr);
	const FProperty* TagProperty = Struct->FindPropertyByName(TEXT("LeapAbilityTag"));
	TestTrue(TEXT("LeapAbilityTag is a reflected, editable name property"), TagProperty && CastField<FNameProperty>(TagProperty) && TagProperty->HasAnyPropertyFlags(CPF_Edit));
	TestTrue(TEXT("LeapAbilityTag also exists as a name property of URPGBossPhases"), CastField<FNameProperty>(Native->FindPropertyByName(TEXT("LeapAbilityTag"))) != nullptr);

	// The Data Asset field: the definition exposes the flow as an editable property of exactly that struct type.
	const FProperty* Field = URPGBossDefinition::StaticClass()->FindPropertyByName(TEXT("PhaseFlow"));
	const FStructProperty* AsStruct = CastField<FStructProperty>(Field);
	if (!TestTrue(TEXT("the definition has a PhaseFlow struct property"), AsStruct != nullptr))
	{
		return false;
	}
	TestTrue(TEXT("it is editable (EditAnywhere)"), AsStruct->HasAnyPropertyFlags(CPF_Edit));
	TestTrue(TEXT("and of the phase flow struct type"), AsStruct->Struct == Struct);

	// The additive authoring defaults of the NEW field: a fresh struct and a fresh definition hold them; the native declarations are only the baseline they match, not an authority.
	const FRPGPhaseFlowConfig Fresh;
	TStrongObjectPtr<URPGBossDefinition> Definition(NewObject<URPGBossDefinition>());
	TestTrue(TEXT("a fresh definition holds the authoring defaults (old schema 1 definitions receive them additively)"), FlowEquals(Definition->PhaseFlow, Fresh));
	TestTrue(TEXT("baseline: they equal the native declarations of URPGBossPhases, field by field"), FlowEquals(ReadFlow(*GetDefault<URPGBossPhases>()), Fresh));
	// The documented values, so a silent change of the declared defaults is noticed.
	TestTrue(TEXT("the declared defaults are the documented ones"), Fresh.TransitionSeconds == 1.8f && Fresh.bUseRoarClip && Fresh.bPausePostureInTransition && Fresh.bLockLeapUntilPhaseTwo
		&& Fresh.AttackAbilityPrefix.Equals(TEXT("GA_GS_Boss_"), ESearchCase::CaseSensitive) && Fresh.LeapAbilityTag == FName(TEXT("Ability.Melee.LeapAttack")));
	// The defaults pass their own validator (they are valid, not a fallback for invalid input), and the other authored records of the definition were not disturbed by the new field.
	FString Error;
	TestTrue(TEXT("the authoring defaults pass the shared validator"), RPGBossPhaseFlowAdapters::ValidatePhaseFlow(Fresh, Error) && Error.IsEmpty());
	TestTrue(TEXT("the stats record keeps its own defaults (no substitution)"), Definition->Stats.MaxHealth == 0.f && Definition->Stats.MaxPosture == 0.f && Definition->Schema == 1);
	AddInfo(TEXT("Reflection and defaults only; NOT a serialized asset and NOT seen in the Details panel."));
	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
