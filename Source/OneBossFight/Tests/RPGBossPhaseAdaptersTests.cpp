// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Animation/AnimMontage.h"
#include "Animation/AnimSequence.h"
#include "Components/SceneComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"
#include "Player/RPGBossPhaseAdapters.h"
#include "Player/RPGBossPhases.h"
#include "Player/RPGBossPosture.h"
#include "UObject/Package.h"
#include "UObject/StrongObjectPtr.h"
#include <cmath>
#include <limits>

// These tests prove typed assignment and rejection of ONE selected phase on isolated native components and actors: no pack asset, no arena, no engine save.
// They do NOT prove a phase transition, the effective movement speed, attack rate or damage, a reset, or a duel. The native defaults 0.6 / 1.2 / 1.2 / 1.25 are only comparison baselines.
// The before/after snapshots cover the selected PUBLIC configuration and runtime state of the component (every field and getter in the state struct), not every private cache.

namespace
{
namespace PhaseAdapterTests
{
	constexpr float QuietNaN = std::numeric_limits<float>::quiet_NaN();
	constexpr float PosInf = std::numeric_limits<float>::infinity();

	// The documented native defaults of URPGBossPhases (comparison baselines, never substituted for a missing input).
	constexpr float DefaultThreshold = 0.6f;
	constexpr float DefaultSpeed = 1.2f;
	constexpr float DefaultRate = 1.2f;
	constexpr float DefaultDamage = 1.25f;

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

	FRPGParticipantConfig MakeConfigOf(FName Id, float Threshold, float Speed, float Rate, float Attack)
	{
		FRPGParticipantConfig Config;
		Config.Phases.Add(MakePhase(Id, Threshold, Speed, Rate, Attack));
		return Config;
	}

	/** Test-local game world with the set-up the attach witness used headless; destroyed with the scope. */
	struct FPhaseTestWorld
	{
		UWorld* World = nullptr;

		FPhaseTestWorld()
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

		~FPhaseTestWorld()
		{
			if (World)
			{
				GEngine->DestroyWorldContext(World);
				World->DestroyWorld(/*bInformEngineOfWorld=*/false);
			}
		}

		FPhaseTestWorld(const FPhaseTestWorld&) = delete;
		FPhaseTestWorld& operator=(const FPhaseTestWorld&) = delete;

		AActor* SpawnOwner() const { return World ? World->SpawnActor<AActor>() : nullptr; }
	};

	/** Every public configuration field and runtime getter of the component: a failed call must leave all of it equal, a successful one must change only the four named fields. */
	struct FPhaseState
	{
		float PhaseTwoHealthFraction, TransitionSeconds, MovementScale, AttackRateScale, DamageScale, FireballMinRange, FireballMaxRange;
		bool bUseRoarClip, bFireballEnabled, bLockLeapUntilPhaseTwo, bPausePostureInTransition;
		FSoftObjectPath RoarClip, TransitionMontage, ImmunityEffect, FireballAbility;
		FVector2D FireballCooldown;
		FString AttackAbilityPrefix, RoarSourceName;
		FName LeapAbilityTag;
		bool bLeapBlocked, bPhaseTwo, bInTransition;
		int32 FireballCount, PhaseTwoCount, QueuedStarts;
		double LastTransitionStart;

		explicit FPhaseState(const URPGBossPhases& P)
			: PhaseTwoHealthFraction(P.PhaseTwoHealthFraction), TransitionSeconds(P.TransitionSeconds), MovementScale(P.MovementScale), AttackRateScale(P.AttackRateScale), DamageScale(P.DamageScale)
			, FireballMinRange(P.FireballMinRange), FireballMaxRange(P.FireballMaxRange), bUseRoarClip(P.bUseRoarClip), bFireballEnabled(P.bFireballEnabled)
			, bLockLeapUntilPhaseTwo(P.bLockLeapUntilPhaseTwo), bPausePostureInTransition(P.bPausePostureInTransition), RoarClip(P.RoarClip.ToSoftObjectPath())
			, TransitionMontage(P.TransitionMontage.ToSoftObjectPath()), ImmunityEffect(P.ImmunityEffect.ToSoftObjectPath()), FireballAbility(P.FireballAbility.ToSoftObjectPath())
			, FireballCooldown(P.FireballCooldown), AttackAbilityPrefix(P.AttackAbilityPrefix), RoarSourceName(P.GetRoarSourceName()), LeapAbilityTag(P.LeapAbilityTag)
			, bLeapBlocked(P.IsLeapBlocked()), bPhaseTwo(P.IsPhaseTwo()), bInTransition(P.IsInTransition()), FireballCount(P.GetFireballCount()), PhaseTwoCount(P.GetPhaseTwoCount())
			, QueuedStarts(P.GetQueuedStartCount()), LastTransitionStart(P.GetLastTransitionStartTime())
		{
		}

		bool operator==(const FPhaseState& O) const
		{
			return PhaseTwoHealthFraction == O.PhaseTwoHealthFraction && TransitionSeconds == O.TransitionSeconds && MovementScale == O.MovementScale && AttackRateScale == O.AttackRateScale
				&& DamageScale == O.DamageScale && FireballMinRange == O.FireballMinRange && FireballMaxRange == O.FireballMaxRange && bUseRoarClip == O.bUseRoarClip
				&& bFireballEnabled == O.bFireballEnabled && bLockLeapUntilPhaseTwo == O.bLockLeapUntilPhaseTwo && bPausePostureInTransition == O.bPausePostureInTransition
				&& RoarClip == O.RoarClip && TransitionMontage == O.TransitionMontage && ImmunityEffect == O.ImmunityEffect && FireballAbility == O.FireballAbility
				&& FireballCooldown == O.FireballCooldown && AttackAbilityPrefix == O.AttackAbilityPrefix && RoarSourceName == O.RoarSourceName && LeapAbilityTag == O.LeapAbilityTag
				&& bLeapBlocked == O.bLeapBlocked && bPhaseTwo == O.bPhaseTwo && bInTransition == O.bInTransition && FireballCount == O.FireballCount && PhaseTwoCount == O.PhaseTwoCount
				&& QueuedStarts == O.QueuedStarts && LastTransitionStart == O.LastTransitionStart;
		}
	};

	TStrongObjectPtr<URPGBossPhases> NewPhases(AActor* Owner, const TCHAR* Name)
	{
		return TStrongObjectPtr<URPGBossPhases>(NewObject<URPGBossPhases>(Owner, Name));
	}
}
}

using namespace PhaseAdapterTests;

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPhaseAdaptersAssignTest, "OneBossFight.Binding.PhaseAdapters.Assign",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPhaseAdaptersAssignTest::RunTest(const FString& Parameters)
{
	FPhaseTestWorld Scope;
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
	const FPhaseState Before(*Phases);
	const int32 OwnedComponentsBefore = Owner->GetComponents().Num();
	TestTrue(TEXT("baseline: the native defaults are the documented ones"), Before.PhaseTwoHealthFraction == DefaultThreshold && Before.MovementScale == DefaultSpeed && Before.AttackRateScale == DefaultRate && Before.DamageScale == DefaultDamage);

	// Plan identity: the legacy instance name, the exact class, the selected id in the four typed manifest paths, the id captured by value.
	FName SelectedId(TEXT("PhaseTwo"));
	const FRPGComponentPlan Plan = RPGBossPhaseAdapters::MakePhasePlan(SelectedId);
	SelectedId = FName(TEXT("Elsewhere")); // must not affect the plan
	TestTrue(TEXT("plan class"), Plan.Class == URPGBossPhases::StaticClass());
	TestTrue(TEXT("plan instance name"), Plan.InstanceName == FName(TEXT("RPGBossPhases")));
	TestTrue(TEXT("plan required fields name the four typed inputs of the selected id"),
		Plan.RequiredFields == TArray<FString>{TEXT("Phases[PhaseTwo].EntryHealthFraction"), TEXT("Phases[PhaseTwo].SpeedMultiplier"), TEXT("Phases[PhaseTwo].RateMultiplier"), TEXT("Phases[PhaseTwo].AttackMultiplier")});
	if (!TestTrue(TEXT("plan callback is set"), static_cast<bool>(Plan.Configure)))
	{
		return false;
	}
	TestTrue(TEXT("a plan without a selected id lists no required field"), RPGBossPhaseAdapters::MakePhasePlan(NAME_None).RequiredFields.IsEmpty());

	// Non-default valid values (none equals a native default), applied through the plan callback; the selected id inside the plan is the captured one.
	const FRPGParticipantConfig Config = MakeConfigOf(FName(TEXT("PhaseTwo")), 0.35f, 1.5f, 1.75f, 2.f);
	FString Error;
	TestTrue(TEXT("plan callback succeeds (captured id, not the later variable)"), Plan.Configure(*Phases, Config, Error));
	TestTrue(TEXT("no error text on success"), Error.IsEmpty());
	TestTrue(TEXT("PhaseTwoHealthFraction assigned from EntryHealthFraction"), Phases->PhaseTwoHealthFraction == 0.35f);
	TestTrue(TEXT("MovementScale assigned from SpeedMultiplier"), Phases->MovementScale == 1.5f);
	TestTrue(TEXT("AttackRateScale assigned from RateMultiplier"), Phases->AttackRateScale == 1.75f);
	TestTrue(TEXT("DamageScale assigned from AttackMultiplier"), Phases->DamageScale == 2.f);

	// Only the four named fields changed: every other configuration field (transition seconds, clips, immunity, leap lock, fireball settings and their disabled default, ability prefix) and every runtime value is equal.
	FPhaseState Expected = Before;
	Expected.PhaseTwoHealthFraction = 0.35f;
	Expected.MovementScale = 1.5f;
	Expected.AttackRateScale = 1.75f;
	Expected.DamageScale = 2.f;
	TestTrue(TEXT("nothing but the four assignment fields changed"), FPhaseState(*Phases) == Expected);
	TestFalse(TEXT("fireball stays disabled"), Phases->bFireballEnabled);
	TestFalse(TEXT("no phase trigger: not phase two, not in transition"), Phases->IsPhaseTwo() || Phases->IsInTransition());

	// The callback created nothing, registered nothing and began nothing.
	TestFalse(TEXT("component stays unregistered"), Phases->IsRegistered());
	TestFalse(TEXT("component did not begin play"), Phases->HasBegunPlay());
	TestFalse(TEXT("owner did not begin play"), Owner->HasActorBegunPlay());
	TestTrue(TEXT("owner gained no component"), Owner->GetComponents().Num() == OwnedComponentsBefore);

	// The direct helper is the code the plan calls; selection is by id.
	TestTrue(TEXT("ConfigurePhases helper"), RPGBossPhaseAdapters::ConfigurePhases(*Phases, MakeConfigOf(FName(TEXT("Rage")), 0.5f, 0.75f, 0.5f, 1.f), FName(TEXT("Rage")), Error)
		&& Phases->PhaseTwoHealthFraction == 0.5f && Phases->MovementScale == 0.75f && Phases->AttackRateScale == 0.5f && Phases->DamageScale == 1.f);

	AddInfo(TEXT("Typed assignment of one selected phase only; NOT a phase transition, NOT effective speed/rate/damage, NOT a reset or a duel."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPhaseAdaptersSelectionTest, "OneBossFight.Binding.PhaseAdapters.Selection",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPhaseAdaptersSelectionTest::RunTest(const FString& Parameters)
{
	FPhaseTestWorld Scope;
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
	const FPhaseState Before(*Phases);
	const FName A(TEXT("A")), B(TEXT("B"));

	// The configs are built once and the cases point at them (no copy of a config is needed).
	const FRPGParticipantConfig OneRecord = MakeConfigOf(A, 0.5f, 1.5f, 1.5f, 1.5f);
	const FRPGParticipantConfig NoRecords;
	FRPGParticipantConfig Two = MakeConfigOf(A, 0.5f, 1.5f, 1.5f, 1.5f);
	Two.Phases.Add(MakePhase(B, 0.3f, 2.f, 2.f, 2.f));
	FRPGParticipantConfig Duplicate = MakeConfigOf(A, 0.5f, 1.5f, 1.5f, 1.5f);
	Duplicate.Phases.Add(MakePhase(A, 0.3f, 2.f, 2.f, 2.f));

	struct FCase
	{
		const TCHAR* Name;
		const FRPGParticipantConfig* Config;
		FName Selected;
		const TCHAR* ExpectedToken;
	};
	TArray<FCase> Cases;
	Cases.Add({TEXT("no selected id"), &OneRecord, NAME_None, TEXT("InvalidPhase.NoSelection")});
	Cases.Add({TEXT("zero records"), &NoRecords, A, TEXT("InvalidPhase.NoRecords")});
	// Selection is by id, never the first or the only record: a different id is not found even when exactly one record exists.
	Cases.Add({TEXT("mismatched id, one record"), &OneRecord, B, TEXT("InvalidPhase.NotFound")});
	Cases.Add({TEXT("extra transition, selecting the first"), &Two, A, TEXT("UnsupportedNativePhaseSet")});
	Cases.Add({TEXT("extra transition, selecting the last"), &Two, B, TEXT("UnsupportedNativePhaseSet")});
	Cases.Add({TEXT("duplicate id"), &Duplicate, A, TEXT("UnsupportedNativePhaseSet")});
	Cases.Add({TEXT("selected id missing from a longer set"), &Two, FName(TEXT("C")), TEXT("InvalidPhase.NotFound")});

	for (const FCase& Case : Cases)
	{
		FString Error;
		TestFalse(FString::Printf(TEXT("%s: validation refuses"), Case.Name), RPGBossPhaseAdapters::ValidatePhases(Case.Config->Phases, Case.Selected, Error));
		TestTrue(FString::Printf(TEXT("%s: named %s (got '%s')"), Case.Name, Case.ExpectedToken, *Error), Error.StartsWith(Case.ExpectedToken));
		FString ConfigureError;
		TestFalse(FString::Printf(TEXT("%s: configure refuses"), Case.Name), RPGBossPhaseAdapters::ConfigurePhases(*Phases, *Case.Config, Case.Selected, ConfigureError));
		TestTrue(FString::Printf(TEXT("%s: configure names the same token"), Case.Name), ConfigureError.StartsWith(Case.ExpectedToken));
		TestTrue(FString::Printf(TEXT("%s: no write"), Case.Name), FPhaseState(*Phases) == Before);
		// The plan factory does not hide the failure either.
		FString PlanError;
		TestFalse(FString::Printf(TEXT("%s: plan callback refuses"), Case.Name), RPGBossPhaseAdapters::MakePhasePlan(Case.Selected).Configure(*Phases, *Case.Config, PlanError));
		TestTrue(FString::Printf(TEXT("%s: plan names the same token"), Case.Name), PlanError.StartsWith(Case.ExpectedToken));
	}

	// The control: exactly one record with the selected id works on the very component that was refused above.
	FString Error;
	TestTrue(TEXT("control: one record with the selected id"), RPGBossPhaseAdapters::ConfigurePhases(*Phases, MakeConfigOf(B, 0.4f, 1.4f, 1.6f, 1.8f), B, Error));
	TestTrue(TEXT("control assigned"), Phases->PhaseTwoHealthFraction == 0.4f && Phases->MovementScale == 1.4f && Phases->AttackRateScale == 1.6f && Phases->DamageScale == 1.8f);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPhaseAdaptersValidationTest, "OneBossFight.Binding.PhaseAdapters.Validation",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPhaseAdaptersValidationTest::RunTest(const FString& Parameters)
{
	struct FCase
	{
		const TCHAR* Name;
		float Threshold, Speed, Rate, Attack;
		const TCHAR* ExpectedToken; // nullptr = valid
	};
	const float TinyNormal = std::numeric_limits<float>::min();      // inverse about 8.5e37: finite
	const float Denormal = std::numeric_limits<float>::denorm_min(); // inverse overflows to infinity
	const FCase Cases[] = {
		{TEXT("native defaults"), 0.6f, 1.2f, 1.2f, 1.25f, nullptr},
		{TEXT("threshold exactly 1"), 1.f, 1.2f, 1.2f, 1.25f, nullptr},
		{TEXT("tiny positive threshold"), 0.0001f, 1.2f, 1.2f, 1.25f, nullptr},
		{TEXT("fractional speed and rate below 1"), 0.6f, 0.5f, 0.25f, 1.f, nullptr},
		{TEXT("damage factor exactly 1"), 0.6f, 1.2f, 1.2f, 1.f, nullptr},
		{TEXT("large finite values"), 0.5f, 1.0e9f, 1.0e9f, 1.0e9f, nullptr},
		{TEXT("smallest normal speed and rate (finite inverse)"), 0.6f, TinyNormal, TinyNormal, 1.25f, nullptr},
		{TEXT("NaN threshold"), QuietNaN, 1.2f, 1.2f, 1.25f, TEXT("InvalidPhase.NotFinite")},
		{TEXT("NaN speed"), 0.6f, QuietNaN, 1.2f, 1.25f, TEXT("InvalidPhase.NotFinite")},
		{TEXT("NaN rate"), 0.6f, 1.2f, QuietNaN, 1.25f, TEXT("InvalidPhase.NotFinite")},
		{TEXT("NaN attack"), 0.6f, 1.2f, 1.2f, QuietNaN, TEXT("InvalidPhase.NotFinite")},
		{TEXT("+Inf threshold"), PosInf, 1.2f, 1.2f, 1.25f, TEXT("InvalidPhase.NotFinite")},
		{TEXT("+Inf speed"), 0.6f, PosInf, 1.2f, 1.25f, TEXT("InvalidPhase.NotFinite")},
		{TEXT("+Inf rate"), 0.6f, 1.2f, PosInf, 1.25f, TEXT("InvalidPhase.NotFinite")},
		{TEXT("-Inf attack"), 0.6f, 1.2f, 1.2f, -PosInf, TEXT("InvalidPhase.NotFinite")},
		{TEXT("zero threshold"), 0.f, 1.2f, 1.2f, 1.25f, TEXT("InvalidPhase.ThresholdOutOfRange")},
		{TEXT("negative threshold"), -0.1f, 1.2f, 1.2f, 1.25f, TEXT("InvalidPhase.ThresholdOutOfRange")},
		{TEXT("threshold above 1"), 1.0001f, 1.2f, 1.2f, 1.25f, TEXT("InvalidPhase.ThresholdOutOfRange")},
		{TEXT("first float above 1"), std::nextafter(1.f, 2.f), 1.2f, 1.2f, 1.25f, TEXT("InvalidPhase.ThresholdOutOfRange")},
		{TEXT("zero speed"), 0.6f, 0.f, 1.2f, 1.25f, TEXT("InvalidPhase.NotPositive")},
		{TEXT("negative speed"), 0.6f, -1.f, 1.2f, 1.25f, TEXT("InvalidPhase.NotPositive")},
		{TEXT("zero rate"), 0.6f, 1.2f, 0.f, 1.25f, TEXT("InvalidPhase.NotPositive")},
		{TEXT("negative rate"), 0.6f, 1.2f, -1.f, 1.25f, TEXT("InvalidPhase.NotPositive")},
		{TEXT("zero attack"), 0.6f, 1.2f, 1.2f, 0.f, TEXT("InvalidPhase.NotPositive")},
		{TEXT("negative attack"), 0.6f, 1.2f, 1.2f, -1.f, TEXT("InvalidPhase.NotPositive")},
		{TEXT("speed without a finite inverse"), 0.6f, Denormal, 1.2f, 1.25f, TEXT("UnsupportedNativeInverse")},
		{TEXT("rate without a finite inverse"), 0.6f, 1.2f, Denormal, 1.25f, TEXT("UnsupportedNativeInverse")},
		{TEXT("damage factor below 1 (never reversed by the native reset)"), 0.6f, 1.2f, 1.2f, 0.5f, TEXT("UnsupportedNativeDamageScale")},
		{TEXT("first float below 1 for damage"), 0.6f, 1.2f, 1.2f, std::nextafter(1.f, 0.f), TEXT("UnsupportedNativeDamageScale")},
		// Precedence: non-finite, then generic validity, then native arithmetic, then the damage capability.
		{TEXT("non-finite outranks everything"), QuietNaN, Denormal, 1.2f, 0.5f, TEXT("InvalidPhase.NotFinite")},
		{TEXT("threshold outranks native arithmetic"), 2.f, Denormal, 1.2f, 0.5f, TEXT("InvalidPhase.ThresholdOutOfRange")},
		{TEXT("generic positivity outranks native arithmetic"), 0.6f, Denormal, 1.2f, 0.f, TEXT("InvalidPhase.NotPositive")},
		{TEXT("inverse outranks the damage capability"), 0.6f, Denormal, 1.2f, 0.5f, TEXT("UnsupportedNativeInverse")},
	};

	FPhaseTestWorld Scope;
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
	const FPhaseState Before(*Phases);
	const FName Id(TEXT("PhaseTwo"));
	for (const FCase& Case : Cases)
	{
		const FRPGParticipantConfig Config = MakeConfigOf(Id, Case.Threshold, Case.Speed, Case.Rate, Case.Attack);
		FString Error;
		const bool bOk = RPGBossPhaseAdapters::ValidatePhases(Config.Phases, Id, Error);
		if (!Case.ExpectedToken)
		{
			TestTrue(FString::Printf(TEXT("%s: valid"), Case.Name), bOk && Error.IsEmpty());
			continue;
		}
		TestFalse(FString::Printf(TEXT("%s: rejected"), Case.Name), bOk);
		TestTrue(FString::Printf(TEXT("%s: named %s (got '%s')"), Case.Name, Case.ExpectedToken, *Error), Error.StartsWith(Case.ExpectedToken));
		// Every invalid record leaves all four assignment fields and the accessible native state unchanged.
		FString ConfigureError;
		TestFalse(FString::Printf(TEXT("%s: configure refuses"), Case.Name), RPGBossPhaseAdapters::ConfigurePhases(*Phases, Config, Id, ConfigureError));
		TestTrue(FString::Printf(TEXT("%s: configure names the same token"), Case.Name), ConfigureError.StartsWith(Case.ExpectedToken));
		TestTrue(FString::Printf(TEXT("%s: no partial write"), Case.Name), FPhaseState(*Phases) == Before);
	}
	// The component refused every record above and is still configurable.
	FString Error;
	TestTrue(TEXT("after all refusals a valid record still configures"), RPGBossPhaseAdapters::ConfigurePhases(*Phases, MakeConfigOf(Id, 0.45f, 0.5f, 0.25f, 3.f), Id, Error) && Phases->MovementScale == 0.5f && Phases->AttackRateScale == 0.25f);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPhaseAdaptersIsolationTest, "OneBossFight.Binding.PhaseAdapters.Isolation",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPhaseAdaptersIsolationTest::RunTest(const FString& Parameters)
{
	FPhaseTestWorld Scope;
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
	TStrongObjectPtr<URPGBossPhases> PhasesA = NewPhases(OwnerA, TEXT("RPGBossPhases"));
	TStrongObjectPtr<URPGBossPhases> PhasesB = NewPhases(OwnerB, TEXT("RPGBossPhases"));
	TStrongObjectPtr<URPGBossPhases> PhasesC = NewPhases(OwnerC, TEXT("RPGBossPhases"));
	if (!TestTrue(TEXT("three components"), PhasesA.IsValid() && PhasesB.IsValid() && PhasesC.IsValid()))
	{
		return false;
	}
	const FName IdA(TEXT("RageA")), IdB(TEXT("RageB"));
	FRPGParticipantConfig ConfigA = MakeConfigOf(IdA, 0.35f, 1.5f, 1.75f, 2.f);
	const FRPGParticipantConfig ConfigB = MakeConfigOf(IdB, 0.8f, 0.6f, 0.9f, 1.f); // fractional speed and rate, factor exactly 1
	// Two plans with two captured ids, each used on its own owner and its own config.
	const FRPGComponentPlan PlanA = RPGBossPhaseAdapters::MakePhasePlan(IdA);
	const FRPGComponentPlan PlanB = RPGBossPhaseAdapters::MakePhasePlan(IdB);
	FString Error;
	TestTrue(TEXT("A through its plan"), PlanA.Configure(*PhasesA, ConfigA, Error));
	const FPhaseState SnapshotA(*PhasesA);
	TestTrue(TEXT("B through its plan"), PlanB.Configure(*PhasesB, ConfigB, Error));
	TestTrue(TEXT("configuring B did not change A"), FPhaseState(*PhasesA) == SnapshotA);
	TestTrue(TEXT("B has its own values"), PhasesB->PhaseTwoHealthFraction == 0.8f && PhasesB->MovementScale == 0.6f && PhasesB->AttackRateScale == 0.9f && PhasesB->DamageScale == 1.f);

	// A plan is bound to its id: the other config does not satisfy it.
	FString CrossError;
	TestFalse(TEXT("plan A refuses config B (its id is not there)"), PlanA.Configure(*PhasesC, ConfigB, CrossError));
	TestTrue(TEXT("named not found"), CrossError.StartsWith(TEXT("InvalidPhase.NotFound")));

	// The assignment copies values: changing the config afterwards changes nothing.
	ConfigA.Phases[0].EntryHealthFraction = 0.01f;
	ConfigA.Phases[0].SpeedMultiplier = 9.f;
	TestTrue(TEXT("later config change does not reach A"), FPhaseState(*PhasesA) == SnapshotA);

	// A third owner that was refused keeps the constructor defaults, and so does the class default object.
	TestTrue(TEXT("refused component keeps the defaults"), PhasesC->PhaseTwoHealthFraction == DefaultThreshold && PhasesC->MovementScale == DefaultSpeed && PhasesC->AttackRateScale == DefaultRate && PhasesC->DamageScale == DefaultDamage);
	const URPGBossPhases* Default = GetDefault<URPGBossPhases>();
	TestTrue(TEXT("CDO defaults unchanged"), Default->PhaseTwoHealthFraction == DefaultThreshold && Default->MovementScale == DefaultSpeed && Default->AttackRateScale == DefaultRate && Default->DamageScale == DefaultDamage);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPhaseAdaptersRejectionsTest, "OneBossFight.Binding.PhaseAdapters.Rejections",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPhaseAdaptersRejectionsTest::RunTest(const FString& Parameters)
{
	FPhaseTestWorld Scope;
	if (!TestNotNull(TEXT("test world"), Scope.World))
	{
		return false;
	}
	const FName Id(TEXT("PhaseTwo"));
	const FRPGParticipantConfig Config = MakeConfigOf(Id, 0.35f, 1.5f, 1.75f, 2.f); // valid: every failure below is about the component or the owner
	FString Error;

	// A rejected call changes nothing and names the reason. Wrong-class targets are concrete classes (UActorComponent itself is abstract).
	auto ExpectRejected = [&](const TCHAR* Label, UActorComponent& Component, const TCHAR* Token)
	{
		const URPGBossPhases* AsPhases = Cast<URPGBossPhases>(&Component);
		const URPGBossPosture* AsPosture = Cast<URPGBossPosture>(&Component);
		TOptional<FPhaseState> PhasesBefore;
		if (AsPhases) { PhasesBefore.Emplace(*AsPhases); }
		const float PostureMaxBefore = AsPosture ? AsPosture->PostureMax : 0.f;
		const float PostureDelayBefore = AsPosture ? AsPosture->RegenDelaySeconds : 0.f;
		const float PostureRateBefore = AsPosture ? AsPosture->RegenPerSecond : 0.f;
		const bool bOk = RPGBossPhaseAdapters::ConfigurePhases(Component, Config, Id, Error);
		TestFalse(FString::Printf(TEXT("%s: rejected"), Label), bOk);
		TestTrue(FString::Printf(TEXT("%s: named %s (got '%s')"), Label, Token, *Error), Error.StartsWith(Token));
		if (PhasesBefore.IsSet()) { TestTrue(FString::Printf(TEXT("%s: phases unchanged"), Label), FPhaseState(*AsPhases) == PhasesBefore.GetValue()); }
		if (AsPosture) { TestTrue(FString::Printf(TEXT("%s: posture configuration untouched"), Label), AsPosture->PostureMax == PostureMaxBefore && AsPosture->RegenDelaySeconds == PostureDelayBefore && AsPosture->RegenPerSecond == PostureRateBefore); }
	};

	AActor* Owner = Scope.SpawnOwner();
	if (!TestNotNull(TEXT("owner actor"), Owner))
	{
		return false;
	}

	// Wrong class: a concrete native component of another kind and a concrete engine component.
	{
		TStrongObjectPtr<URPGBossPosture> Posture(NewObject<URPGBossPosture>(Owner, TEXT("RPGBossPosture")));
		TStrongObjectPtr<USceneComponent> Scene(NewObject<USceneComponent>(Owner, TEXT("UnrelatedScene")));
		if (!TestTrue(TEXT("wrong-class components created"), Posture.IsValid() && Scene.IsValid()))
		{
			return false;
		}
		ExpectRejected(TEXT("phase adapter on a posture"), *Posture, TEXT("WrongComponentClass"));
		ExpectRejected(TEXT("phase adapter on a scene component"), *Scene, TEXT("WrongComponentClass"));
	}

	// Already registered (the owner has not begun play, so registration alone does not begin play for the component).
	{
		TStrongObjectPtr<URPGBossPhases> Phases = NewPhases(Owner, TEXT("RegisteredPhases"));
		if (!TestTrue(TEXT("registered component created"), Phases.IsValid()))
		{
			return false;
		}
		Phases->RegisterComponent();
		if (!TestTrue(TEXT("precondition: registered and not begun"), Phases->IsRegistered() && !Phases->HasBegunPlay() && !Owner->HasActorBegunPlay()))
		{
			AddError(TEXT("unsupported precondition: the registered-but-not-begun state could not be built"));
			return false;
		}
		ExpectRejected(TEXT("registered phases"), *Phases, TEXT("ComponentAlreadyRegistered"));
	}

	// Component already began play: its owner begins play with the component registered. The three soft asset references are cleared first so the component's BeginPlay loads nothing in this isolated test.
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
		Phases->RoarClip.Reset();
		Phases->TransitionMontage.Reset();
		Phases->ImmunityEffect.Reset();
		Phases->RegisterComponent();
		BegunOwner->DispatchBeginPlay();
		if (!TestTrue(TEXT("precondition: component and owner began play"), Phases->HasBegunPlay() && BegunOwner->HasActorBegunPlay()))
		{
			AddError(TEXT("unsupported precondition: the begun-play state could not be built"));
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
		ExpectRejected(TEXT("phases under a begun owner"), *Phases, TEXT("OwnerBegunPlay"));
	}

	// Invalid owner: the component's outer is not an actor.
	{
		TStrongObjectPtr<URPGBossPhases> Phases(NewObject<URPGBossPhases>(GetTransientPackage(), TEXT("OrphanPhases")));
		if (!TestTrue(TEXT("orphan component created"), Phases.IsValid() && !Phases->GetOwner()))
		{
			return false;
		}
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
		ExpectRejected(TEXT("phase adapter on a destroyed posture"), *Posture, TEXT("InvalidComponent"));
		TestTrue(TEXT("the owner stayed live through both calls"), IsValid(LiveOwner) && !LiveOwner->IsActorBeingDestroyed());
	}

	AddInfo(TEXT("Rejection paths on isolated actors; an owner that is being destroyed is covered by the code (IsActorBeingDestroyed) but not exercised here."));
	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
