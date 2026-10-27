// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Engine/Engine.h"
#include "Components/SceneComponent.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossPosture.h"
#include "Player/RPGBossStatsAdapters.h"
#include "UObject/Package.h"
#include "UObject/StrongObjectPtr.h"
#include <cmath>
#include <limits>

// These tests prove typed configuration assignment and rejection on isolated native components and actors: no pack asset, no arena, no engine save.
// They do NOT prove the asynchronous application of health to the pack, the first BeginPlay of Posture in a real duel, or any registration chronology.
// The before/after snapshots cover the selected PUBLIC configuration and runtime state of the two components (every field and getter listed in the state structs below), not every private cache.

namespace
{
namespace StatsAdapterTests
{
	constexpr float NaN = std::numeric_limits<float>::quiet_NaN();
	constexpr float Inf = std::numeric_limits<float>::infinity();

	FRPGParticipantConfig MakeStatsConfig(float Health, float Posture, float Delay, float Rate)
	{
		FRPGParticipantConfig Config;
		Config.Stats.MaxHealth = Health;
		Config.Stats.MaxPosture = Posture;
		Config.Stats.PostureRegenDelay = Delay;
		Config.Stats.PostureRegenRate = Rate;
		return Config;
	}

	/** Test-local game world with the same set-up the attach witness used headless; destroyed with the scope. */
	struct FStatsTestWorld
	{
		UWorld* World = nullptr;

		FStatsTestWorld()
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

		~FStatsTestWorld()
		{
			if (World)
			{
				GEngine->DestroyWorldContext(World);
				World->DestroyWorld(/*bInformEngineOfWorld=*/false);
			}
		}

		FStatsTestWorld(const FStatsTestWorld&) = delete;
		FStatsTestWorld& operator=(const FStatsTestWorld&) = delete;

		AActor* SpawnOwner() const { return World ? World->SpawnActor<AActor>() : nullptr; }
	};

	/** Every field a configuration helper could touch, configuration and runtime alike: a failed call must leave all of it equal, a successful one must change only the configuration it names. */
	struct FStatsEncounterState
	{
		float BossMaxHealth;
		float GateRadius;
		bool bTestFreeze, bResetOnPlayerRespawn, bDormant, bWaking;
		int32 Generation, ResetCount, DeathResetRefusals;

		explicit FStatsEncounterState(const URPGBossEncounter& E)
			: BossMaxHealth(E.BossMaxHealth), GateRadius(E.GateRadius), bTestFreeze(E.bTestFreeze), bResetOnPlayerRespawn(E.bResetOnPlayerRespawn)
			, bDormant(E.IsDormant()), bWaking(E.IsWaking()), Generation(E.GetGeneration()), ResetCount(E.GetResetCount()), DeathResetRefusals(E.GetDeathResetRefusals())
		{
		}

		bool operator==(const FStatsEncounterState& O) const
		{
			return BossMaxHealth == O.BossMaxHealth && GateRadius == O.GateRadius && bTestFreeze == O.bTestFreeze && bResetOnPlayerRespawn == O.bResetOnPlayerRespawn
				&& bDormant == O.bDormant && bWaking == O.bWaking && Generation == O.Generation && ResetCount == O.ResetCount && DeathResetRefusals == O.DeathResetRefusals;
		}
	};

	struct FStatsPostureState
	{
		float PostureMax, RegenDelaySeconds, RegenPerSecond, CurrentPosture, LastDrainAmount;
		bool bPinPackPoise, bConfigured;
		int32 DrainCount, SuppressedDrains, BreakRequests, PackStunSuppressed;
		double LastDrainTime;
		FString HoldName, LastBreakResult, LastDrainSource;

		explicit FStatsPostureState(const URPGBossPosture& P)
			: PostureMax(P.PostureMax), RegenDelaySeconds(P.RegenDelaySeconds), RegenPerSecond(P.RegenPerSecond), CurrentPosture(P.GetPosture()), LastDrainAmount(P.GetLastDrainAmount())
			, bPinPackPoise(P.bPinPackPoise), bConfigured(P.IsConfigured()), DrainCount(P.GetDrainCount()), SuppressedDrains(P.GetSuppressedDrainCount()), BreakRequests(P.GetBreakRequestCount())
			, PackStunSuppressed(P.GetPackStunSuppressedCount()), LastDrainTime(P.GetLastDrainTime()), HoldName(P.GetHoldName()), LastBreakResult(P.GetLastBreakResult()), LastDrainSource(P.GetLastDrainSource())
		{
		}

		bool operator==(const FStatsPostureState& O) const
		{
			return PostureMax == O.PostureMax && RegenDelaySeconds == O.RegenDelaySeconds && RegenPerSecond == O.RegenPerSecond && CurrentPosture == O.CurrentPosture
				&& LastDrainAmount == O.LastDrainAmount && bPinPackPoise == O.bPinPackPoise && bConfigured == O.bConfigured && DrainCount == O.DrainCount
				&& SuppressedDrains == O.SuppressedDrains && BreakRequests == O.BreakRequests && PackStunSuppressed == O.PackStunSuppressed && LastDrainTime == O.LastDrainTime
				&& HoldName == O.HoldName && LastBreakResult == O.LastBreakResult && LastDrainSource == O.LastDrainSource;
		}
	};

	/** The documented constructor defaults of the two components; the adapters and these tests must leave them alone. */
	constexpr float DefaultBossMaxHealth = 2000.f;
	constexpr float DefaultPostureMax = 100.f;
	constexpr float DefaultRegenDelay = 6.f;
	constexpr float DefaultRegenRate = 13.f;
}
}

using namespace StatsAdapterTests;

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGStatsAdaptersAssignTest, "OneBossFight.Binding.StatsAdapters.Assign",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGStatsAdaptersAssignTest::RunTest(const FString& Parameters)
{
	FStatsTestWorld Scope;
	if (!TestNotNull(TEXT("test world"), Scope.World))
	{
		return false;
	}
	AActor* Owner = Scope.SpawnOwner();
	if (!TestNotNull(TEXT("owner actor"), Owner))
	{
		return false;
	}
	TStrongObjectPtr<URPGBossEncounter> Encounter(NewObject<URPGBossEncounter>(Owner, TEXT("RPGBossEncounter")));
	TStrongObjectPtr<URPGBossPosture> Posture(NewObject<URPGBossPosture>(Owner, TEXT("RPGBossPosture")));
	if (!TestTrue(TEXT("components created"), Encounter.IsValid() && Posture.IsValid()))
	{
		return false;
	}
	const FStatsEncounterState EncounterBefore(*Encounter);
	const FStatsPostureState PostureBefore(*Posture);
	const int32 OwnedComponentsBefore = Owner->GetComponents().Num();
	TestTrue(TEXT("posture pool is not seeded before BeginPlay"), PostureBefore.CurrentPosture < 0.f);

	// Plan identity: the legacy instance names, the exact classes and the typed field paths as the manifest contract names them.
	const FRPGComponentPlan EncounterPlan = RPGBossStatsAdapters::MakeEncounterPlan();
	const FRPGComponentPlan PosturePlan = RPGBossStatsAdapters::MakePosturePlan();
	TestTrue(TEXT("encounter plan class"), EncounterPlan.Class == URPGBossEncounter::StaticClass());
	TestTrue(TEXT("posture plan class"), PosturePlan.Class == URPGBossPosture::StaticClass());
	TestTrue(TEXT("encounter plan instance name"), EncounterPlan.InstanceName == FName(TEXT("RPGBossEncounter")));
	TestTrue(TEXT("posture plan instance name"), PosturePlan.InstanceName == FName(TEXT("RPGBossPosture")));
	TestTrue(TEXT("encounter plan required fields"), EncounterPlan.RequiredFields == TArray<FString>{TEXT("Stats.MaxHealth")});
	TestTrue(TEXT("posture plan required fields"), PosturePlan.RequiredFields == TArray<FString>{TEXT("Stats.MaxPosture"), TEXT("Stats.PostureRegenDelay"), TEXT("Stats.PostureRegenRate")});
	if (!TestTrue(TEXT("plan callbacks are set"), static_cast<bool>(EncounterPlan.Configure) && static_cast<bool>(PosturePlan.Configure)))
	{
		return false;
	}

	// Non-default valid values (none equals a constructor default), applied through the plan callbacks.
	const FRPGParticipantConfig Config = MakeStatsConfig(3500.f, 73.5f, 4.25f, 9.75f);
	FString Error;
	TestTrue(TEXT("encounter plan callback succeeds"), EncounterPlan.Configure(*Encounter, Config, Error));
	TestTrue(TEXT("no error text on success"), Error.IsEmpty());
	TestTrue(TEXT("posture plan callback succeeds"), PosturePlan.Configure(*Posture, Config, Error));
	TestTrue(TEXT("no error text on success (posture)"), Error.IsEmpty());

	TestTrue(TEXT("BossMaxHealth assigned"), Encounter->BossMaxHealth == 3500.f);
	TestTrue(TEXT("PostureMax assigned"), Posture->PostureMax == 73.5f);
	TestTrue(TEXT("RegenDelaySeconds assigned"), Posture->RegenDelaySeconds == 4.25f);
	TestTrue(TEXT("RegenPerSecond assigned"), Posture->RegenPerSecond == 9.75f);

	// Only the four named fields changed: every other configuration field and every runtime value equals its pre-call value.
	FStatsEncounterState EncounterExpected = EncounterBefore;
	EncounterExpected.BossMaxHealth = 3500.f;
	FStatsPostureState PostureExpected = PostureBefore;
	PostureExpected.PostureMax = 73.5f;
	PostureExpected.RegenDelaySeconds = 4.25f;
	PostureExpected.RegenPerSecond = 9.75f;
	TestTrue(TEXT("encounter: nothing but BossMaxHealth changed (gate, flags, generation, counters, dormant/wake state)"), FStatsEncounterState(*Encounter) == EncounterExpected);
	TestTrue(TEXT("posture: nothing but the three configuration fields changed (current pool, counters, hold, break state)"), FStatsPostureState(*Posture) == PostureExpected);

	// The callbacks created nothing, registered nothing and began nothing.
	TestFalse(TEXT("encounter stays unregistered"), Encounter->IsRegistered());
	TestFalse(TEXT("posture stays unregistered"), Posture->IsRegistered());
	TestFalse(TEXT("encounter did not begin play"), Encounter->HasBegunPlay());
	TestFalse(TEXT("posture did not begin play"), Posture->HasBegunPlay());
	TestFalse(TEXT("owner did not begin play"), Owner->HasActorBegunPlay());
	TestTrue(TEXT("owner gained no component"), Owner->GetComponents().Num() == OwnedComponentsBefore);

	// The direct helpers are the same code the plans call.
	TestTrue(TEXT("ConfigureEncounter helper"), RPGBossStatsAdapters::ConfigureEncounter(*Encounter, MakeStatsConfig(4200.f, 50.f, 1.f, 2.f), Error) && Encounter->BossMaxHealth == 4200.f);
	TestTrue(TEXT("ConfigurePosture helper"), RPGBossStatsAdapters::ConfigurePosture(*Posture, MakeStatsConfig(4200.f, 50.f, 1.f, 2.f), Error) && Posture->PostureMax == 50.f && Posture->RegenDelaySeconds == 1.f && Posture->RegenPerSecond == 2.f);

	AddInfo(TEXT("Typed configuration assignment only; NOT pack health readback, NOT Posture.BeginPlay seeding in a real duel, NOT an arena duel."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGStatsAdaptersIsolationTest, "OneBossFight.Binding.StatsAdapters.Isolation",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGStatsAdaptersIsolationTest::RunTest(const FString& Parameters)
{
	FStatsTestWorld Scope;
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
	TStrongObjectPtr<URPGBossEncounter> EncounterA(NewObject<URPGBossEncounter>(OwnerA, TEXT("RPGBossEncounter")));
	TStrongObjectPtr<URPGBossPosture> PostureA(NewObject<URPGBossPosture>(OwnerA, TEXT("RPGBossPosture")));
	TStrongObjectPtr<URPGBossEncounter> EncounterB(NewObject<URPGBossEncounter>(OwnerB, TEXT("RPGBossEncounter")));
	TStrongObjectPtr<URPGBossPosture> PostureB(NewObject<URPGBossPosture>(OwnerB, TEXT("RPGBossPosture")));
	TStrongObjectPtr<URPGBossEncounter> EncounterC(NewObject<URPGBossEncounter>(OwnerC, TEXT("RPGBossEncounter")));
	TStrongObjectPtr<URPGBossPosture> PostureC(NewObject<URPGBossPosture>(OwnerC, TEXT("RPGBossPosture")));
	if (!TestTrue(TEXT("six components"), EncounterA.IsValid() && PostureA.IsValid() && EncounterB.IsValid() && PostureB.IsValid() && EncounterC.IsValid() && PostureC.IsValid()))
	{
		return false;
	}

	FRPGParticipantConfig ConfigA = MakeStatsConfig(3500.f, 73.5f, 4.25f, 9.75f);
	const FRPGParticipantConfig ConfigB = MakeStatsConfig(1200.f, 55.f, 0.f, 0.f); // zero delay and rate are valid
	FString Error;
	TestTrue(TEXT("A encounter"), RPGBossStatsAdapters::ConfigureEncounter(*EncounterA, ConfigA, Error));
	TestTrue(TEXT("A posture"), RPGBossStatsAdapters::ConfigurePosture(*PostureA, ConfigA, Error));
	const FStatsEncounterState EncounterASnapshot(*EncounterA);
	const FStatsPostureState PostureASnapshot(*PostureA);

	TestTrue(TEXT("B encounter"), RPGBossStatsAdapters::ConfigureEncounter(*EncounterB, ConfigB, Error));
	TestTrue(TEXT("B posture"), RPGBossStatsAdapters::ConfigurePosture(*PostureB, ConfigB, Error));

	TestTrue(TEXT("configuring B did not change A (encounter)"), FStatsEncounterState(*EncounterA) == EncounterASnapshot);
	TestTrue(TEXT("configuring B did not change A (posture)"), FStatsPostureState(*PostureA) == PostureASnapshot);
	TestTrue(TEXT("B has its own values"), EncounterB->BossMaxHealth == 1200.f && PostureB->PostureMax == 55.f && PostureB->RegenDelaySeconds == 0.f && PostureB->RegenPerSecond == 0.f);

	// The assignment copies values: changing the config afterwards changes nothing.
	ConfigA.Stats.MaxHealth = 9.f;
	ConfigA.Stats.MaxPosture = 9.f;
	TestTrue(TEXT("later config change does not reach A"), FStatsEncounterState(*EncounterA) == EncounterASnapshot && FStatsPostureState(*PostureA) == PostureASnapshot);

	// A third owner that was never configured keeps the constructor defaults, and so do the class default objects.
	TestTrue(TEXT("untouched encounter keeps its default"), EncounterC->BossMaxHealth == DefaultBossMaxHealth);
	TestTrue(TEXT("untouched posture keeps its defaults"), PostureC->PostureMax == DefaultPostureMax && PostureC->RegenDelaySeconds == DefaultRegenDelay && PostureC->RegenPerSecond == DefaultRegenRate);
	TestTrue(TEXT("encounter CDO default unchanged"), GetDefault<URPGBossEncounter>()->BossMaxHealth == DefaultBossMaxHealth);
	TestTrue(TEXT("posture CDO defaults unchanged"), GetDefault<URPGBossPosture>()->PostureMax == DefaultPostureMax && GetDefault<URPGBossPosture>()->RegenDelaySeconds == DefaultRegenDelay && GetDefault<URPGBossPosture>()->RegenPerSecond == DefaultRegenRate);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGStatsAdaptersValidationTest, "OneBossFight.Binding.StatsAdapters.Validation",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGStatsAdaptersValidationTest::RunTest(const FString& Parameters)
{
	struct FCase
	{
		const TCHAR* Name;
		float Health, Posture, Delay, Rate;
		const TCHAR* ExpectedToken; // nullptr = valid
	};
	const FCase Cases[] = {
		{TEXT("legacy defaults"), 2000.f, 100.f, 6.f, 13.f, nullptr},
		{TEXT("fractional health above the floor"), 1.5f, 100.f, 6.f, 13.f, nullptr},
		{TEXT("small positive posture maximum"), 2000.f, 0.5f, 6.f, 13.f, nullptr},
		{TEXT("zero delay and rate"), 2000.f, 100.f, 0.f, 0.f, nullptr},
		{TEXT("large finite values"), 1.0e9f, 1.0e9f, 1.0e9f, 1.0e9f, nullptr},
		{TEXT("NaN health"), NaN, 100.f, 6.f, 13.f, TEXT("InvalidStats.NotFinite")},
		{TEXT("NaN posture"), 2000.f, NaN, 6.f, 13.f, TEXT("InvalidStats.NotFinite")},
		{TEXT("NaN delay"), 2000.f, 100.f, NaN, 13.f, TEXT("InvalidStats.NotFinite")},
		{TEXT("NaN rate"), 2000.f, 100.f, 6.f, NaN, TEXT("InvalidStats.NotFinite")},
		{TEXT("+Inf health"), Inf, 100.f, 6.f, 13.f, TEXT("InvalidStats.NotFinite")},
		{TEXT("-Inf health"), -Inf, 100.f, 6.f, 13.f, TEXT("InvalidStats.NotFinite")},
		{TEXT("+Inf posture"), 2000.f, Inf, 6.f, 13.f, TEXT("InvalidStats.NotFinite")},
		{TEXT("+Inf delay"), 2000.f, 100.f, Inf, 13.f, TEXT("InvalidStats.NotFinite")},
		{TEXT("-Inf rate"), 2000.f, 100.f, 6.f, -Inf, TEXT("InvalidStats.NotFinite")},
		{TEXT("zero health"), 0.f, 100.f, 6.f, 13.f, TEXT("InvalidStats.NotPositive")},
		{TEXT("negative health"), -1.f, 100.f, 6.f, 13.f, TEXT("InvalidStats.NotPositive")},
		{TEXT("zero posture"), 2000.f, 0.f, 6.f, 13.f, TEXT("InvalidStats.NotPositive")},
		{TEXT("negative posture"), 2000.f, -5.f, 6.f, 13.f, TEXT("InvalidStats.NotPositive")},
		{TEXT("negative delay"), 2000.f, 100.f, -1.f, 13.f, TEXT("InvalidStats.Negative")},
		{TEXT("negative rate"), 2000.f, 100.f, 6.f, -0.001f, TEXT("InvalidStats.Negative")},
		// Generic validity is checked before the native capability: an invalid record is reported as invalid, not as an unsupported override.
		{TEXT("generic failure outranks native capability"), 0.5f, 100.f, -1.f, 13.f, TEXT("InvalidStats.Negative")},
		{TEXT("non-finite outranks everything"), 0.5f, NaN, -1.f, 13.f, TEXT("InvalidStats.NotFinite")},
	};
	for (const FCase& Case : Cases)
	{
		FString Error;
		const bool bOk = RPGBossStatsAdapters::ValidateStats(MakeStatsConfig(Case.Health, Case.Posture, Case.Delay, Case.Rate).Stats, Error);
		if (!Case.ExpectedToken)
		{
			TestTrue(FString::Printf(TEXT("%s: valid"), Case.Name), bOk && Error.IsEmpty());
		}
		else
		{
			TestFalse(FString::Printf(TEXT("%s: rejected"), Case.Name), bOk);
			TestTrue(FString::Printf(TEXT("%s: named %s (got '%s')"), Case.Name, Case.ExpectedToken, *Error), Error.StartsWith(Case.ExpectedToken));
		}
	}

	// The whole Stats record is validated before any write: a bad value in the OTHER component's fields stops the call and nothing is written.
	FStatsTestWorld Scope;
	if (!TestNotNull(TEXT("test world"), Scope.World))
	{
		return false;
	}
	AActor* Owner = Scope.SpawnOwner();
	if (!TestNotNull(TEXT("owner actor"), Owner))
	{
		return false;
	}
	TStrongObjectPtr<URPGBossEncounter> Encounter(NewObject<URPGBossEncounter>(Owner, TEXT("RPGBossEncounter")));
	TStrongObjectPtr<URPGBossPosture> Posture(NewObject<URPGBossPosture>(Owner, TEXT("RPGBossPosture")));
	if (!TestTrue(TEXT("components created"), Encounter.IsValid() && Posture.IsValid()))
	{
		return false;
	}
	const FStatsEncounterState EncounterBefore(*Encounter);
	const FStatsPostureState PostureBefore(*Posture);
	FString Error;
	TestFalse(TEXT("encounter refuses a record with bad posture stats"), RPGBossStatsAdapters::ConfigureEncounter(*Encounter, MakeStatsConfig(3500.f, -1.f, 6.f, 13.f), Error));
	TestTrue(TEXT("named (encounter, bad posture)"), Error.StartsWith(TEXT("InvalidStats.NotPositive")));
	TestFalse(TEXT("posture refuses a record with bad health"), RPGBossStatsAdapters::ConfigurePosture(*Posture, MakeStatsConfig(0.f, 73.5f, 4.25f, 9.75f), Error));
	TestTrue(TEXT("named (posture, bad health)"), Error.StartsWith(TEXT("InvalidStats.NotPositive")));
	TestFalse(TEXT("posture refuses a NaN regeneration rate"), RPGBossStatsAdapters::ConfigurePosture(*Posture, MakeStatsConfig(3500.f, 73.5f, 4.25f, NaN), Error));
	TestTrue(TEXT("no partial write after rejected records (encounter)"), FStatsEncounterState(*Encounter) == EncounterBefore);
	TestTrue(TEXT("no partial write after rejected records (posture)"), FStatsPostureState(*Posture) == PostureBefore);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGStatsAdaptersHealthOverrideTest, "OneBossFight.Binding.StatsAdapters.HealthOverride",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGStatsAdaptersHealthOverrideTest::RunTest(const FString& Parameters)
{
	FStatsTestWorld Scope;
	if (!TestNotNull(TEXT("test world"), Scope.World))
	{
		return false;
	}
	// Unsupported: the native override runs only for BossMaxHealth above 1. The refusal is named and happens before ANY assignment, in both components, even with valid posture stats.
	const float Unsupported[] = {0.0001f, 0.5f, 1.f};
	for (float Health : Unsupported)
	{
		AActor* Owner = Scope.SpawnOwner();
		if (!TestNotNull(TEXT("owner actor"), Owner))
		{
			return false;
		}
		TStrongObjectPtr<URPGBossEncounter> Encounter(NewObject<URPGBossEncounter>(Owner, TEXT("RPGBossEncounter")));
		TStrongObjectPtr<URPGBossPosture> Posture(NewObject<URPGBossPosture>(Owner, TEXT("RPGBossPosture")));
		if (!TestTrue(TEXT("components created"), Encounter.IsValid() && Posture.IsValid()))
		{
			return false;
		}
		const FStatsEncounterState EncounterBefore(*Encounter);
		const FStatsPostureState PostureBefore(*Posture);
		const FRPGParticipantConfig Config = MakeStatsConfig(Health, 73.5f, 4.25f, 9.75f);
		FString Error;
		const FString Label = LexToString(Health);
		TestFalse(FString::Printf(TEXT("health %s: encounter refused"), *Label), RPGBossStatsAdapters::ConfigureEncounter(*Encounter, Config, Error));
		TestTrue(FString::Printf(TEXT("health %s: encounter failure is UnsupportedNativeHealthOverride (got '%s')"), *Label, *Error), Error.StartsWith(TEXT("UnsupportedNativeHealthOverride")));
		TestFalse(FString::Printf(TEXT("health %s: posture refused too"), *Label), RPGBossStatsAdapters::ConfigurePosture(*Posture, Config, Error));
		TestTrue(FString::Printf(TEXT("health %s: posture failure is UnsupportedNativeHealthOverride"), *Label), Error.StartsWith(TEXT("UnsupportedNativeHealthOverride")));
		TestTrue(FString::Printf(TEXT("health %s: no encounter write"), *Label), FStatsEncounterState(*Encounter) == EncounterBefore);
		TestTrue(FString::Printf(TEXT("health %s: no posture write although its own stats were valid"), *Label), FStatsPostureState(*Posture) == PostureBefore);
	}

	// Supported, including the first float above the floor and a fractional value: not rejected for being fractional.
	const float Supported[] = {std::nextafter(1.f, 2.f), 1.5f, 2000.f, 123456.7f};
	for (float Health : Supported)
	{
		AActor* Owner = Scope.SpawnOwner();
		if (!TestNotNull(TEXT("owner actor"), Owner))
		{
			return false;
		}
		TStrongObjectPtr<URPGBossEncounter> Encounter(NewObject<URPGBossEncounter>(Owner, TEXT("RPGBossEncounter")));
		TStrongObjectPtr<URPGBossPosture> Posture(NewObject<URPGBossPosture>(Owner, TEXT("RPGBossPosture")));
		if (!TestTrue(TEXT("components created"), Encounter.IsValid() && Posture.IsValid()))
		{
			return false;
		}
		const FRPGParticipantConfig Config = MakeStatsConfig(Health, 73.5f, 4.25f, 9.75f);
		FString Error;
		const FString Label = LexToString(Health);
		TestTrue(FString::Printf(TEXT("health %s: encounter accepted (got '%s')"), *Label, *Error), RPGBossStatsAdapters::ConfigureEncounter(*Encounter, Config, Error));
		TestTrue(FString::Printf(TEXT("health %s: value assigned unchanged, no clamp, round or substitute"), *Label), Encounter->BossMaxHealth == Health);
		TestTrue(FString::Printf(TEXT("health %s: posture accepted"), *Label), RPGBossStatsAdapters::ConfigurePosture(*Posture, Config, Error));
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGStatsAdaptersRejectionsTest, "OneBossFight.Binding.StatsAdapters.Rejections",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGStatsAdaptersRejectionsTest::RunTest(const FString& Parameters)
{
	FStatsTestWorld Scope;
	if (!TestNotNull(TEXT("test world"), Scope.World))
	{
		return false;
	}
	const FRPGParticipantConfig Config = MakeStatsConfig(3500.f, 73.5f, 4.25f, 9.75f); // valid: every failure below is about the component or the owner
	FString Error;

	// A rejected call changes nothing and names the reason; one helper runs both adapters against the same component.
	auto ExpectRejected = [&](const TCHAR* Label, UActorComponent& Component, const TCHAR* Token, bool bEncounterAdapter)
	{
		const URPGBossEncounter* AsEncounter = Cast<URPGBossEncounter>(&Component);
		const URPGBossPosture* AsPosture = Cast<URPGBossPosture>(&Component);
		TOptional<FStatsEncounterState> EncounterBefore;
		TOptional<FStatsPostureState> PostureBefore;
		if (AsEncounter) { EncounterBefore.Emplace(*AsEncounter); }
		if (AsPosture) { PostureBefore.Emplace(*AsPosture); }
		const bool bOk = bEncounterAdapter ? RPGBossStatsAdapters::ConfigureEncounter(Component, Config, Error) : RPGBossStatsAdapters::ConfigurePosture(Component, Config, Error);
		TestFalse(FString::Printf(TEXT("%s: rejected"), Label), bOk);
		TestTrue(FString::Printf(TEXT("%s: named %s (got '%s')"), Label, Token, *Error), Error.StartsWith(Token));
		if (EncounterBefore.IsSet()) { TestTrue(FString::Printf(TEXT("%s: encounter unchanged"), Label), FStatsEncounterState(*AsEncounter) == EncounterBefore.GetValue()); }
		if (PostureBefore.IsSet()) { TestTrue(FString::Printf(TEXT("%s: posture unchanged"), Label), FStatsPostureState(*AsPosture) == PostureBefore.GetValue()); }
	};

	AActor* Owner = Scope.SpawnOwner();
	if (!TestNotNull(TEXT("owner actor"), Owner))
	{
		return false;
	}

	// Wrong class: the other component, a concrete unrelated component (UActorComponent itself is abstract and cannot be instantiated), each against each adapter.
	{
		TStrongObjectPtr<URPGBossEncounter> Encounter(NewObject<URPGBossEncounter>(Owner, TEXT("RPGBossEncounter")));
		TStrongObjectPtr<URPGBossPosture> Posture(NewObject<URPGBossPosture>(Owner, TEXT("RPGBossPosture")));
		TStrongObjectPtr<USceneComponent> Plain(NewObject<USceneComponent>(Owner, TEXT("PlainComponent")));
		if (!TestTrue(TEXT("wrong-class components created"), Encounter.IsValid() && Posture.IsValid() && Plain.IsValid()))
		{
			return false;
		}
		ExpectRejected(TEXT("encounter adapter on a posture"), *Posture, TEXT("WrongComponentClass"), true);
		ExpectRejected(TEXT("posture adapter on an encounter"), *Encounter, TEXT("WrongComponentClass"), false);
		ExpectRejected(TEXT("encounter adapter on an unrelated scene component"), *Plain, TEXT("WrongComponentClass"), true);
		ExpectRejected(TEXT("posture adapter on an unrelated scene component"), *Plain, TEXT("WrongComponentClass"), false);
	}

	// Already registered (the owner has not begun play, so registration alone does not begin play for the component).
	{
		TStrongObjectPtr<URPGBossEncounter> Encounter(NewObject<URPGBossEncounter>(Owner, TEXT("RegisteredEncounter")));
		TStrongObjectPtr<URPGBossPosture> Posture(NewObject<URPGBossPosture>(Owner, TEXT("RegisteredPosture")));
		if (!TestTrue(TEXT("registered components created"), Encounter.IsValid() && Posture.IsValid()))
		{
			return false;
		}
		Encounter->RegisterComponent();
		Posture->RegisterComponent();
		if (!TestTrue(TEXT("precondition: registered and not begun"), Encounter->IsRegistered() && Posture->IsRegistered() && !Encounter->HasBegunPlay() && !Posture->HasBegunPlay() && !Owner->HasActorBegunPlay()))
		{
			AddError(TEXT("unsupported precondition: the registered-but-not-begun state could not be built"));
			return false;
		}
		ExpectRejected(TEXT("registered encounter"), *Encounter, TEXT("ComponentAlreadyRegistered"), true);
		ExpectRejected(TEXT("registered posture"), *Posture, TEXT("ComponentAlreadyRegistered"), false);
	}

	// Component already began play: its owner begins play with the components registered. The gate radius of the encounter is 0 first, the way the existing fixture does it, so its BeginPlay does not try to sleep a pawn.
	{
		AActor* BegunOwner = Scope.SpawnOwner();
		if (!TestNotNull(TEXT("begun owner actor"), BegunOwner))
		{
			return false;
		}
		TStrongObjectPtr<URPGBossEncounter> Encounter(NewObject<URPGBossEncounter>(BegunOwner, TEXT("BegunEncounter")));
		TStrongObjectPtr<URPGBossPosture> Posture(NewObject<URPGBossPosture>(BegunOwner, TEXT("BegunPosture")));
		if (!TestTrue(TEXT("begun components created"), Encounter.IsValid() && Posture.IsValid()))
		{
			return false;
		}
		Encounter->GateRadius = 0.f;
		Encounter->RegisterComponent();
		Posture->RegisterComponent();
		BegunOwner->DispatchBeginPlay();
		if (!TestTrue(TEXT("precondition: components and owner began play"), Encounter->HasBegunPlay() && Posture->HasBegunPlay() && BegunOwner->HasActorBegunPlay()))
		{
			AddError(TEXT("unsupported precondition: the begun-play state could not be built"));
			return false;
		}
		ExpectRejected(TEXT("begun encounter"), *Encounter, TEXT("ComponentBegunPlay"), true);
		ExpectRejected(TEXT("begun posture"), *Posture, TEXT("ComponentBegunPlay"), false);
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
		TStrongObjectPtr<URPGBossEncounter> Encounter(NewObject<URPGBossEncounter>(LateOwner, TEXT("LateEncounter")));
		TStrongObjectPtr<URPGBossPosture> Posture(NewObject<URPGBossPosture>(LateOwner, TEXT("LatePosture")));
		if (!TestTrue(TEXT("late components created"), Encounter.IsValid() && Posture.IsValid()))
		{
			return false;
		}
		ExpectRejected(TEXT("encounter under a begun owner"), *Encounter, TEXT("OwnerBegunPlay"), true);
		ExpectRejected(TEXT("posture under a begun owner"), *Posture, TEXT("OwnerBegunPlay"), false);
	}

	// Invalid owner: the component's outer is not an actor.
	{
		TStrongObjectPtr<URPGBossEncounter> Encounter(NewObject<URPGBossEncounter>(GetTransientPackage(), TEXT("OrphanEncounter")));
		TStrongObjectPtr<URPGBossPosture> Posture(NewObject<URPGBossPosture>(GetTransientPackage(), TEXT("OrphanPosture")));
		if (!TestTrue(TEXT("orphan components created"), Encounter.IsValid() && Posture.IsValid() && !Encounter->GetOwner() && !Posture->GetOwner()))
		{
			return false;
		}
		ExpectRejected(TEXT("encounter without an owner"), *Encounter, TEXT("InvalidOwner"), true);
		ExpectRejected(TEXT("posture without an owner"), *Posture, TEXT("InvalidOwner"), false);
	}

	// Destroyed component: DestroyComponent already ran on it (flagged as being destroyed, unregistered, EndPlay cleared, removed from its owner, marked garbage) but the object is still allocated because the
	// test holds it and no garbage collection runs in this test. The owner stays valid and is not being destroyed, so this exercises the component check and not the owner check.
	{
		AActor* LiveOwner = Scope.SpawnOwner();
		if (!TestNotNull(TEXT("live owner actor"), LiveOwner))
		{
			return false;
		}
		TStrongObjectPtr<URPGBossEncounter> Encounter(NewObject<URPGBossEncounter>(LiveOwner, TEXT("DeadEncounter")));
		TStrongObjectPtr<URPGBossPosture> Posture(NewObject<URPGBossPosture>(LiveOwner, TEXT("DeadPosture")));
		if (!TestTrue(TEXT("dead components created"), Encounter.IsValid() && Posture.IsValid()))
		{
			return false;
		}
		Encounter->DestroyComponent();
		Posture->DestroyComponent();
		const bool bRetained = Encounter.Get() != nullptr && Posture.Get() != nullptr && Encounter->GetOuter() == LiveOwner && Posture->GetOuter() == LiveOwner;
		const bool bFlaggedDead = Encounter->IsBeingDestroyed() && Posture->IsBeingDestroyed();
		const bool bOwnerLive = IsValid(LiveOwner) && !LiveOwner->IsActorBeingDestroyed() && !LiveOwner->HasActorBegunPlay();
		if (!TestTrue(TEXT("precondition: destroyed components still allocated and linked to their owner, owner live"), bRetained && bFlaggedDead && bOwnerLive))
		{
			AddError(TEXT("unsupported precondition: the destroyed-but-retained state could not be built"));
			return false;
		}
		// What the old checks would have seen: not registered, not begun. Recorded so a reader sees that only the new check can refuse them.
		TestTrue(TEXT("precondition: a destroyed component looks unregistered and not begun, which is why the earlier checks cannot refuse it"), !Encounter->IsRegistered() && !Encounter->HasBegunPlay() && !Posture->IsRegistered() && !Posture->HasBegunPlay());
		ExpectRejected(TEXT("destroyed encounter"), *Encounter, TEXT("InvalidComponent"), true);
		ExpectRejected(TEXT("destroyed posture"), *Posture, TEXT("InvalidComponent"), false);
		// The component check is first: a destroyed component of the WRONG class is reported as invalid, not as the wrong class.
		ExpectRejected(TEXT("encounter adapter on a destroyed posture"), *Posture, TEXT("InvalidComponent"), true);
		ExpectRejected(TEXT("posture adapter on a destroyed encounter"), *Encounter, TEXT("InvalidComponent"), false);
		TestTrue(TEXT("the owner stayed live through all four calls"), IsValid(LiveOwner) && !LiveOwner->IsActorBeingDestroyed());
	}

	AddInfo(TEXT("Rejection paths on isolated actors; an owner that is being destroyed is covered by the code (IsActorBeingDestroyed) but not exercised here. The destroyed-component case is built from the engine's DestroyComponent while the object is still retained: it is not a garbage-collection or freed-memory test."));
	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
