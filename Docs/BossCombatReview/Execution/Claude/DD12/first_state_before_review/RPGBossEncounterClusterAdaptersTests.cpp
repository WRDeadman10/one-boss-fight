// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Components/SceneComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossEncounterClusterAdapters.h"
#include "Player/RPGBossEncounterPolicyAdapters.h"
#include "Player/RPGBossPosture.h"
#include "Player/RPGBossStatsAdapters.h"
#include "UObject/Package.h"
#include "UObject/StrongObjectPtr.h"
#include <limits>

// These tests prove the combined encounter cluster: its one plan for the one native class and instance, the whole-record validation that reuses the accepted stats and policy validators and writes nothing
// when either record is invalid, and the typed, lifecycle-safe assignment of exactly three values (BossMaxHealth, GateRadius, bResetOnPlayerRespawn) with one call on isolated native components. They do NOT
// prove an effective gate, reset or pack health (nothing is registered, begun or ticked beyond the one begun-guard fixture, and no attribute is read or written), a duel, any wiring, a preflight composition or
// a startup order. No compile test exists on purpose: this package adds no schema or compiler API, so the cluster is exercised only through its own refusals and assignments. The one BeginPlay that runs
// (the begun-component guard) does so on a plain actor with the gate radius set to 0 first, exactly as the earlier encounter tests do, so the native BeginPlay stores the home transform and does not put anything
// to sleep; no tick runs.

namespace
{
namespace EncounterClusterTests
{
	constexpr float QuietNaN = std::numeric_limits<float>::quiet_NaN();
	constexpr float PosInf = std::numeric_limits<float>::infinity();

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

	/** Every public configuration field and runtime getter of the encounter component: a failed call must leave all of it equal, a successful one must change only the three typed fields. */
	struct FEncounterState
	{
		float BossMaxHealth;
		float GateRadius;
		bool bTestFreeze, bResetOnPlayerRespawn, bDormant, bWaking;
		int32 Generation, ResetCount, DeathResetRefusals;

		explicit FEncounterState(const URPGBossEncounter& E)
			: BossMaxHealth(E.BossMaxHealth), GateRadius(E.GateRadius), bTestFreeze(E.bTestFreeze), bResetOnPlayerRespawn(E.bResetOnPlayerRespawn)
			, bDormant(E.IsDormant()), bWaking(E.IsWaking()), Generation(E.GetGeneration()), ResetCount(E.GetResetCount()), DeathResetRefusals(E.GetDeathResetRefusals())
		{
		}

		/** Everything except the three typed fields. */
		bool OtherStateEquals(const FEncounterState& O) const
		{
			return bTestFreeze == O.bTestFreeze && bDormant == O.bDormant && bWaking == O.bWaking && Generation == O.Generation && ResetCount == O.ResetCount && DeathResetRefusals == O.DeathResetRefusals;
		}

		bool operator==(const FEncounterState& O) const
		{
			return BossMaxHealth == O.BossMaxHealth && GateRadius == O.GateRadius && bResetOnPlayerRespawn == O.bResetOnPlayerRespawn && OtherStateEquals(O);
		}
	};

	/** A distinct starting state for all three typed fields (none equals config A, and the test freeze flag is a sentinel that must survive every call). */
	void ArmStart(URPGBossEncounter& Encounter)
	{
		Encounter.BossMaxHealth = 777.f;
		Encounter.GateRadius = 555.f;
		Encounter.bResetOnPlayerRespawn = true;
		Encounter.bTestFreeze = true;
	}

	/** A valid four-stat record (the posture fields are validated by the cluster but written by the posture plan, not here) plus the policy. */
	FRPGParticipantConfig MakeConfig(float Health, float Gate, bool bReset)
	{
		FRPGParticipantConfig Config;
		Config.Stats.MaxHealth = Health;
		Config.Stats.MaxPosture = 73.5f;
		Config.Stats.PostureRegenDelay = 4.25f;
		Config.Stats.PostureRegenRate = 9.75f;
		Config.EncounterPolicy.GateRadius = Gate;
		Config.EncounterPolicy.bResetOnPlayerRespawn = bReset;
		return Config;
	}

	FRPGParticipantConfig ConfigA() { return MakeConfig(3500.f, 850.5f, false); }
	FRPGParticipantConfig ConfigB() { return MakeConfig(1.5f, 0.f, true); }

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

	TStrongObjectPtr<URPGBossEncounter> NewEncounter(AActor* Owner, const TCHAR* Name)
	{
		return TStrongObjectPtr<URPGBossEncounter>(NewObject<URPGBossEncounter>(Owner, Name));
	}
}
}

// No file-scope using-directive on purpose: each test body names its namespace itself.

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterClusterAssignTest, "OneBossFight.Binding.EncounterCluster.Assign",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterClusterAssignTest::RunTest(const FString& Parameters)
{
	using namespace EncounterClusterTests;
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
	TStrongObjectPtr<URPGBossEncounter> Encounter = NewEncounter(Owner, TEXT("RPGBossEncounter"));
	if (!TestTrue(TEXT("component created"), Encounter.IsValid()))
	{
		return false;
	}
	ArmStart(*Encounter);
	const FEncounterState Before(*Encounter);

	// Measurement boundary: NewEncounter already added the component to its outer actor, so the owner's component set (identity and count) is captured only AFTER the fixture and immediately BEFORE each
	// configure call. This has the allocation limit of any snapshot: it observes the owner's component set, not every allocation.
	const auto CaptureOwned = [Owner]()
	{
		TSet<const UActorComponent*> OwnedSet;
		for (const UActorComponent* OwnedComponent : Owner->GetComponents())
		{
			OwnedSet.Add(OwnedComponent);
		}
		return OwnedSet;
	};
	const auto SameOwned = [](const TSet<const UActorComponent*>& Left, const TSet<const UActorComponent*>& Right)
	{
		if (Left.Num() != Right.Num())
		{
			return false;
		}
		for (const UActorComponent* LeftComponent : Left)
		{
			if (!Right.Contains(LeftComponent))
			{
				return false;
			}
		}
		return true;
	};

	// The ONE plan: the same class and legacy instance name as the two older encounter factories (which stay separate and unchanged), the three typed paths in order, and exactly their union.
	const FRPGComponentPlan Plan = RPGBossEncounterClusterAdapters::MakeEncounterClusterPlan();
	const FRPGComponentPlan StatsPlan = RPGBossStatsAdapters::MakeEncounterPlan();
	const FRPGComponentPlan PolicyPlan = RPGBossEncounterPolicyAdapters::MakeEncounterPolicyPlan();
	TestTrue(TEXT("plan class is URPGBossEncounter"), Plan.Class == URPGBossEncounter::StaticClass());
	TestTrue(TEXT("plan instance name is the legacy name"), Plan.InstanceName == FName(TEXT("RPGBossEncounter")));
	TestTrue(TEXT("the cluster plan describes the SAME class and instance as both older encounter plans (so only one of them may ever be inserted)"),
		Plan.Class == StatsPlan.Class && Plan.Class == PolicyPlan.Class && Plan.InstanceName == StatsPlan.InstanceName && Plan.InstanceName == PolicyPlan.InstanceName);
	TestTrue(TEXT("required fields are exactly the three typed paths in order"), Plan.RequiredFields == TArray<FString>{TEXT("Stats.MaxHealth"), TEXT("EncounterPolicy.GateRadius"), TEXT("EncounterPolicy.bResetOnPlayerRespawn")});
	bool bUnion = Plan.RequiredFields.Num() == StatsPlan.RequiredFields.Num() + PolicyPlan.RequiredFields.Num();
	for (const FString& Path : StatsPlan.RequiredFields) { bUnion = bUnion && Plan.RequiredFields.Contains(Path); }
	for (const FString& Path : PolicyPlan.RequiredFields) { bUnion = bUnion && Plan.RequiredFields.Contains(Path); }
	TestTrue(TEXT("and exactly the union of the required fields of the two older encounter plans"), bUnion);
	if (!TestTrue(TEXT("plan callback is set"), static_cast<bool>(Plan.Configure)))
	{
		return false;
	}

	// Config A through the plan callback, with manifest Value text that contradicts the typed record: only the typed record counts, one call writes all three destinations.
	FRPGParticipantConfig Config = ConfigA();
	Config.Fields.Add(MakeField(RPGBossStatsAdapters::FieldMaxHealth, TEXT("9999")));
	Config.Fields.Add(MakeField(RPGBossEncounterPolicyAdapters::FieldGateRadius, TEXT("1")));
	Config.Fields.Add(MakeField(RPGBossEncounterPolicyAdapters::FieldResetOnPlayerRespawn, TEXT("true")));
	FString Error = TEXT("a stale diagnostic from an earlier call");
	const TSet<const UActorComponent*> OwnedBeforeA = CaptureOwned();
	TestTrue(TEXT("fixture: the component is already in the owner's component set before the callback"), OwnedBeforeA.Contains(Encounter.Get()));
	TestTrue(TEXT("callback succeeds"), Plan.Configure(*Encounter, Config, Error));
	TestTrue(TEXT("callback created no component: the owner's component set (identity and count) is unchanged by it; no second encounter exists"), SameOwned(OwnedBeforeA, CaptureOwned()));
	TestTrue(TEXT("the diagnostic was cleared on success"), Error.IsEmpty());
	TestTrue(TEXT("all three destinations equal the typed record (health, gate radius, reset), not the manifest text"),
		Encounter->BossMaxHealth == 3500.f && Encounter->GateRadius == 850.5f && !Encounter->bResetOnPlayerRespawn);
	TestFalse(TEXT("all three differ from the distinct start values"), Encounter->BossMaxHealth == Before.BossMaxHealth || Encounter->GateRadius == Before.GateRadius || Encounter->bResetOnPlayerRespawn == Before.bResetOnPlayerRespawn);
	TestTrue(TEXT("every other field and the runtime state (test freeze sentinel, dormancy, waking, generation, counters) are unchanged"), FEncounterState(*Encounter).OtherStateEquals(Before));
	TestFalse(TEXT("component stays unregistered"), Encounter->IsRegistered());
	TestFalse(TEXT("component did not begin play"), Encounter->HasBegunPlay());
	TestFalse(TEXT("owner did not begin play"), Owner->HasActorBegunPlay());

	// Config B directly: fractional health above the native floor, gate radius 0 (the native no-gate), reset true; again no component created.
	const FRPGParticipantConfig B = ConfigB();
	const TSet<const UActorComponent*> OwnedBeforeB = CaptureOwned();
	TestTrue(TEXT("config B succeeds"), RPGBossEncounterClusterAdapters::ConfigureEncounterCluster(*Encounter, B, Error) && Error.IsEmpty());
	TestTrue(TEXT("direct config B created no component: the owner's component set (identity and count) is unchanged by it"), SameOwned(OwnedBeforeB, CaptureOwned()));
	TestTrue(TEXT("B: health 1.5 (above the native override floor), gate radius 0 (no gate), reset true"), Encounter->BossMaxHealth == 1.5f && Encounter->GateRadius == 0.f && Encounter->bResetOnPlayerRespawn);
	TestTrue(TEXT("B: every other field and the runtime state unchanged"), FEncounterState(*Encounter).OtherStateEquals(Before));

	// A fractional gate radius and an explicit negative zero, each with a different health and reset, through the direct helper.
	TestTrue(TEXT("fractional gate radius"), RPGBossEncounterClusterAdapters::ConfigureEncounterCluster(*Encounter, MakeConfig(2.25f, 0.125f, false), Error) && Encounter->GateRadius == 0.125f && Encounter->BossMaxHealth == 2.25f && !Encounter->bResetOnPlayerRespawn);
	TestTrue(TEXT("negative zero gate radius is zero (valid)"), RPGBossEncounterClusterAdapters::ConfigureEncounterCluster(*Encounter, MakeConfig(5000.f, -0.f, true), Error) && Encounter->GateRadius == 0.f && Encounter->BossMaxHealth == 5000.f && Encounter->bResetOnPlayerRespawn);

	AddInfo(TEXT("One typed assignment of three values on an isolated component; NOT an effective gate, reset or pack health, NOT a startup order, NOT readiness."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterClusterValidationTest, "OneBossFight.Binding.EncounterCluster.Validation",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterClusterValidationTest::RunTest(const FString& Parameters)
{
	using namespace EncounterClusterTests;
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
	TStrongObjectPtr<URPGBossEncounter> Encounter = NewEncounter(Owner, TEXT("RPGBossEncounter"));
	if (!TestTrue(TEXT("component created"), Encounter.IsValid()))
	{
		return false;
	}
	ArmStart(*Encounter);
	const FEncounterState Before(*Encounter);

	// One whole-record check: the validator and the assignment both refuse (or accept) with the same exact token and field path, and a refusal writes NOTHING: all three typed fields and every other state
	// value equal the start state.
	auto Check = [&](const FString& Label, const FRPGParticipantConfig& Config, const TCHAR* ExpectedToken, const TCHAR* ExpectedPath)
	{
		FString Error = TEXT("a stale diagnostic");
		const bool bOk = RPGBossEncounterClusterAdapters::ValidateEncounterCluster(Config, Error);
		if (!ExpectedToken)
		{
			TestTrue(FString::Printf(TEXT("%s: valid, and the diagnostic was cleared"), *Label), bOk && Error.IsEmpty());
			return;
		}
		TestFalse(FString::Printf(TEXT("%s: rejected"), *Label), bOk);
		TestTrue(FString::Printf(TEXT("%s: named %s with the path %s (got '%s')"), *Label, ExpectedToken, ExpectedPath, *Error), Error.StartsWith(ExpectedToken) && Error.Contains(ExpectedPath));
		FString ConfigureError = TEXT("a stale diagnostic");
		TestFalse(FString::Printf(TEXT("%s: the assignment refuses"), *Label), RPGBossEncounterClusterAdapters::ConfigureEncounterCluster(*Encounter, Config, ConfigureError));
		TestTrue(FString::Printf(TEXT("%s: the assignment names the same token and path"), *Label), ConfigureError.StartsWith(ExpectedToken) && ConfigureError.Contains(ExpectedPath));
		TestTrue(FString::Printf(TEXT("%s: no write at all (health, gate radius, reset and every other state)"), *Label), FEncounterState(*Encounter) == Before);
	};

	Check(TEXT("config A"), ConfigA(), nullptr, nullptr);
	Check(TEXT("config B"), ConfigB(), nullptr, nullptr);
	Check(TEXT("the authoring defaults of both records with a health above the floor"), []() { FRPGParticipantConfig C; C.Stats.MaxHealth = 2000.f; C.Stats.MaxPosture = 100.f; return C; }(), nullptr, nullptr);

	// Reused boundaries, valid: gate radius 0, -0.0 and fractional; health fractional above the native floor; posture fractional and the regeneration rules at zero. No editor floor is invented.
	Check(TEXT("gate radius 0 (valid: the native no-gate)"), MakeConfig(3500.f, 0.f, false), nullptr, nullptr);
	Check(TEXT("gate radius -0.0 (valid, it is zero)"), MakeConfig(3500.f, -0.f, false), nullptr, nullptr);
	Check(TEXT("gate radius 0.001 (valid, fractional)"), MakeConfig(3500.f, 0.001f, true), nullptr, nullptr);
	Check(TEXT("health 1.5 (valid: above the native override floor of 1)"), MakeConfig(1.5f, 850.5f, false), nullptr, nullptr);
	Check(TEXT("health 1.0001 (valid: just above the floor)"), MakeConfig(1.0001f, 850.5f, false), nullptr, nullptr);
	{
		FRPGParticipantConfig C = ConfigA();
		C.Stats.MaxPosture = 0.25f;
		C.Stats.PostureRegenDelay = 0.f;
		C.Stats.PostureRegenRate = 0.f;
		Check(TEXT("fractional posture maximum with zero regeneration delay and rate (valid)"), C, nullptr, nullptr);
	}

	// Invalid STATS with a valid, non-default policy: the whole record is refused, no write (so a premature health write would be caught).
	Check(TEXT("health NaN"), MakeConfig(QuietNaN, 850.5f, false), TEXT("InvalidStats.NotFinite"), TEXT("Stats.MaxHealth"));
	Check(TEXT("health +Inf"), MakeConfig(PosInf, 850.5f, false), TEXT("InvalidStats.NotFinite"), TEXT("Stats.MaxHealth"));
	Check(TEXT("health 0"), MakeConfig(0.f, 850.5f, false), TEXT("InvalidStats.NotPositive"), TEXT("Stats.MaxHealth"));
	Check(TEXT("health negative"), MakeConfig(-5.f, 850.5f, false), TEXT("InvalidStats.NotPositive"), TEXT("Stats.MaxHealth"));
	Check(TEXT("health 1.0 (refused: the native health override only runs above 1)"), MakeConfig(1.f, 850.5f, false), TEXT("UnsupportedNativeHealthOverride"), TEXT("Stats.MaxHealth"));
	Check(TEXT("health 0.5 (refused: at or below the native override floor)"), MakeConfig(0.5f, 850.5f, false), TEXT("UnsupportedNativeHealthOverride"), TEXT("Stats.MaxHealth"));
	{
		FRPGParticipantConfig C = ConfigA();
		C.Stats.MaxPosture = 0.f;
		Check(TEXT("posture maximum 0 (the whole stats record is validated, not only the health)"), C, TEXT("InvalidStats.NotPositive"), TEXT("Stats.MaxPosture"));
		FRPGParticipantConfig D = ConfigA();
		D.Stats.PostureRegenDelay = -1.f;
		Check(TEXT("negative posture regeneration delay"), D, TEXT("InvalidStats.Negative"), TEXT("Stats.PostureRegenDelay"));
		FRPGParticipantConfig E = ConfigA();
		E.Stats.PostureRegenRate = QuietNaN;
		Check(TEXT("posture regeneration rate NaN"), E, TEXT("InvalidStats.NotFinite"), TEXT("Stats.PostureRegenRate"));
	}

	// Invalid POLICY with a valid, non-default health: the whole record is refused, no write (so a premature policy or health write would be caught, in either order).
	Check(TEXT("gate radius NaN"), MakeConfig(3500.f, QuietNaN, false), TEXT("InvalidPolicy.NotFinite"), TEXT("EncounterPolicy.GateRadius"));
	Check(TEXT("gate radius +Inf"), MakeConfig(3500.f, PosInf, false), TEXT("InvalidPolicy.NotFinite"), TEXT("EncounterPolicy.GateRadius"));
	Check(TEXT("gate radius -Inf"), MakeConfig(3500.f, -PosInf, false), TEXT("InvalidPolicy.NotFinite"), TEXT("EncounterPolicy.GateRadius"));
	Check(TEXT("gate radius -0.0001"), MakeConfig(3500.f, -0.0001f, true), TEXT("InvalidPolicy.Negative"), TEXT("EncounterPolicy.GateRadius"));
	Check(TEXT("gate radius -1"), MakeConfig(3500.f, -1.f, true), TEXT("InvalidPolicy.Negative"), TEXT("EncounterPolicy.GateRadius"));

	// Precedence: the stats record first, then the policy.
	Check(TEXT("invalid health and invalid gate radius: the stats are reported first"), MakeConfig(0.f, -1.f, false), TEXT("InvalidStats.NotPositive"), TEXT("Stats.MaxHealth"));
	Check(TEXT("NaN health and NaN gate radius: the stats are reported first"), MakeConfig(QuietNaN, QuietNaN, false), TEXT("InvalidStats.NotFinite"), TEXT("Stats.MaxHealth"));
	{
		FRPGParticipantConfig C = MakeConfig(3500.f, -1.f, false);
		C.Stats.PostureRegenDelay = -1.f;
		Check(TEXT("invalid posture delay and invalid gate radius: the stats record is still first"), C, TEXT("InvalidStats.Negative"), TEXT("Stats.PostureRegenDelay"));
	}

	// The component refused every record above and is still configurable.
	FString Error;
	TestTrue(TEXT("after all refusals a valid record still configures"), RPGBossEncounterClusterAdapters::ConfigureEncounterCluster(*Encounter, ConfigA(), Error) && Encounter->BossMaxHealth == 3500.f && Encounter->GateRadius == 850.5f);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterClusterIsolationTest, "OneBossFight.Binding.EncounterCluster.Isolation",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterClusterIsolationTest::RunTest(const FString& Parameters)
{
	using namespace EncounterClusterTests;
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
	TStrongObjectPtr<URPGBossEncounter> A = NewEncounter(OwnerA, TEXT("RPGBossEncounter"));
	TStrongObjectPtr<URPGBossEncounter> B = NewEncounter(OwnerB, TEXT("RPGBossEncounter"));
	TStrongObjectPtr<URPGBossEncounter> C = NewEncounter(OwnerC, TEXT("RPGBossEncounter"));
	if (!TestTrue(TEXT("three components"), A.IsValid() && B.IsValid() && C.IsValid()))
	{
		return false;
	}
	ArmStart(*A);
	ArmStart(*B);
	const FEncounterState UntouchedC(*C);
	FRPGParticipantConfig ConfigForA = ConfigA();
	const FRPGParticipantConfig ConfigForB = ConfigB();
	FString Error;
	TestTrue(TEXT("A"), RPGBossEncounterClusterAdapters::ConfigureEncounterCluster(*A, ConfigForA, Error));
	const FEncounterState SnapshotA(*A);
	TestTrue(TEXT("B"), RPGBossEncounterClusterAdapters::ConfigureEncounterCluster(*B, ConfigForB, Error));
	TestTrue(TEXT("configuring B did not change A"), FEncounterState(*A) == SnapshotA);
	TestTrue(TEXT("B has its own three values and kept its own sentinel"), B->BossMaxHealth == 1.5f && B->GateRadius == 0.f && B->bResetOnPlayerRespawn && B->bTestFreeze);

	// The assignment copies values: changing the config afterwards changes nothing.
	ConfigForA.Stats.MaxHealth = 99999.f;
	ConfigForA.EncounterPolicy.GateRadius = 1.f;
	ConfigForA.EncounterPolicy.bResetOnPlayerRespawn = true;
	TestTrue(TEXT("a later config change does not reach A"), FEncounterState(*A) == SnapshotA);

	// A refused record leaves an otherwise configured component exactly as it was (no partial write), with each record invalid in turn.
	TestFalse(TEXT("a record with a valid health and an invalid policy is refused"), RPGBossEncounterClusterAdapters::ConfigureEncounterCluster(*A, MakeConfig(4242.f, -3.f, true), Error));
	TestTrue(TEXT("and leaves A exactly as it was"), FEncounterState(*A) == SnapshotA);
	TestFalse(TEXT("a record with an invalid health and a valid policy is refused"), RPGBossEncounterClusterAdapters::ConfigureEncounterCluster(*A, MakeConfig(0.f, 321.f, true), Error));
	TestTrue(TEXT("and leaves A exactly as it was"), FEncounterState(*A) == SnapshotA);

	// A component that was never configured keeps the native values, and so does the class default object; unrelated fields are untouched everywhere.
	TestTrue(TEXT("untouched component unchanged"), FEncounterState(*C) == UntouchedC);
	TestTrue(TEXT("CDO is a component of the same native values as the untouched one"), FEncounterState(*GetDefault<URPGBossEncounter>()) == UntouchedC);
	TestTrue(TEXT("the native defaults are the documented ones (health 2000, gate radius 1200, reset true)"), UntouchedC.BossMaxHealth == 2000.f && UntouchedC.GateRadius == 1200.f && UntouchedC.bResetOnPlayerRespawn);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterClusterRejectionsTest, "OneBossFight.Binding.EncounterCluster.Rejections",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterClusterRejectionsTest::RunTest(const FString& Parameters)
{
	using namespace EncounterClusterTests;
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
		const URPGBossEncounter* AsEncounter = Cast<URPGBossEncounter>(&Component);
		const URPGBossPosture* AsPosture = Cast<URPGBossPosture>(&Component);
		TOptional<FEncounterState> Before;
		if (AsEncounter) { Before.Emplace(*AsEncounter); }
		const float PostureMaxBefore = AsPosture ? AsPosture->PostureMax : 0.f;
		const bool bOk = RPGBossEncounterClusterAdapters::ConfigureEncounterCluster(Component, Config, Error);
		TestFalse(FString::Printf(TEXT("%s: rejected"), Label), bOk);
		TestTrue(FString::Printf(TEXT("%s: named %s (got '%s')"), Label, Token, *Error), Error.StartsWith(Token));
		if (Before.IsSet()) { TestTrue(FString::Printf(TEXT("%s: encounter unchanged (health, gate radius, reset and every other state)"), Label), FEncounterState(*AsEncounter) == Before.GetValue()); }
		if (AsPosture) { TestTrue(FString::Printf(TEXT("%s: posture configuration untouched"), Label), AsPosture->PostureMax == PostureMaxBefore); }
	};

	AActor* Owner = Scope.SpawnOwner();
	if (!TestNotNull(TEXT("owner actor"), Owner))
	{
		return false;
	}

	// Wrong class: another native component and a concrete engine component.
	{
		TStrongObjectPtr<URPGBossPosture> Posture(NewObject<URPGBossPosture>(Owner, TEXT("RPGBossPosture")));
		TStrongObjectPtr<USceneComponent> Scene(NewObject<USceneComponent>(Owner, TEXT("UnrelatedScene")));
		if (!TestTrue(TEXT("wrong-class components created"), Posture.IsValid() && Scene.IsValid()))
		{
			return false;
		}
		ExpectRejected(TEXT("cluster on a posture"), *Posture, TEXT("WrongComponentClass"));
		ExpectRejected(TEXT("cluster on a scene component"), *Scene, TEXT("WrongComponentClass"));
	}

	// Already registered (the owner has not begun play, so registration alone does not begin play for the component).
	{
		TStrongObjectPtr<URPGBossEncounter> Registered = NewEncounter(Owner, TEXT("RegisteredEncounter"));
		if (!TestTrue(TEXT("registered component created"), Registered.IsValid()))
		{
			return false;
		}
		ArmStart(*Registered);
		Registered->RegisterComponent();
		if (!TestTrue(TEXT("precondition: registered and not begun"), Registered->IsRegistered() && !Registered->HasBegunPlay() && !Owner->HasActorBegunPlay()))
		{
			AddError(TEXT("unsupported precondition: the registered-but-not-begun state could not be built"));
			return false;
		}
		ExpectRejected(TEXT("registered encounter"), *Registered, TEXT("ComponentAlreadyRegistered"));
	}

	// Component already began play: its owner begins play with the component registered. The native BeginPlay stores the home transform and puts the boss to sleep only when the gate radius is above 0, so the
	// gate radius is 0 first, the way the earlier encounter fixture does it (a plain actor owner, no pawn, no dormant wake component, nothing else); no tick runs.
	{
		AActor* BegunOwner = Scope.SpawnOwner();
		if (!TestNotNull(TEXT("begun owner actor"), BegunOwner))
		{
			return false;
		}
		TStrongObjectPtr<URPGBossEncounter> Begun = NewEncounter(BegunOwner, TEXT("BegunEncounter"));
		if (!TestTrue(TEXT("begun component created"), Begun.IsValid()))
		{
			return false;
		}
		ArmStart(*Begun);
		Begun->GateRadius = 0.f;
		if (!TestTrue(TEXT("precondition: the gate radius is 0 (BeginPlay will not sleep) and the owner is a plain actor"), Begun->GateRadius == 0.f && BegunOwner->GetClass() == AActor::StaticClass()))
		{
			AddError(TEXT("unsupported precondition: the begun-play fixture could not be made safe"));
			return false;
		}
		Begun->RegisterComponent();
		BegunOwner->DispatchBeginPlay();
		if (!TestTrue(TEXT("precondition: component and owner began play"), Begun->HasBegunPlay() && BegunOwner->HasActorBegunPlay()))
		{
			AddError(TEXT("unsupported precondition: the begun-play state could not be built"));
			return false;
		}
		ExpectRejected(TEXT("begun encounter"), *Begun, TEXT("ComponentBegunPlay"));
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
		TStrongObjectPtr<URPGBossEncounter> Late = NewEncounter(LateOwner, TEXT("LateEncounter"));
		if (!TestTrue(TEXT("late component created"), Late.IsValid()))
		{
			return false;
		}
		ArmStart(*Late);
		ExpectRejected(TEXT("encounter under a begun owner"), *Late, TEXT("OwnerBegunPlay"));
	}

	// Invalid owner: the component's outer is not an actor.
	{
		TStrongObjectPtr<URPGBossEncounter> Orphan(NewObject<URPGBossEncounter>(GetTransientPackage(), TEXT("OrphanEncounter")));
		if (!TestTrue(TEXT("orphan component created"), Orphan.IsValid() && !Orphan->GetOwner()))
		{
			return false;
		}
		ArmStart(*Orphan);
		ExpectRejected(TEXT("encounter without an owner"), *Orphan, TEXT("InvalidOwner"));
	}

	// Destroyed component: DestroyComponent already ran (flagged as being destroyed, unregistered, EndPlay cleared, removed from its owner, marked garbage) but the object is still allocated because the test holds it
	// and no garbage collection runs here. The owner stays live, so this is the component check and not the owner check. This is not a freed-memory test.
	{
		AActor* LiveOwner = Scope.SpawnOwner();
		if (!TestNotNull(TEXT("live owner actor"), LiveOwner))
		{
			return false;
		}
		TStrongObjectPtr<URPGBossEncounter> Dead = NewEncounter(LiveOwner, TEXT("DeadEncounter"));
		TStrongObjectPtr<URPGBossPosture> DeadPosture(NewObject<URPGBossPosture>(LiveOwner, TEXT("DeadPosture")));
		if (!TestTrue(TEXT("dead components created"), Dead.IsValid() && DeadPosture.IsValid()))
		{
			return false;
		}
		ArmStart(*Dead);
		Dead->DestroyComponent();
		DeadPosture->DestroyComponent();
		const bool bRetained = Dead.Get() != nullptr && DeadPosture.Get() != nullptr && Dead->GetOuter() == LiveOwner && DeadPosture->GetOuter() == LiveOwner;
		const bool bFlaggedDead = Dead->IsBeingDestroyed() && DeadPosture->IsBeingDestroyed();
		const bool bOwnerLive = IsValid(LiveOwner) && !LiveOwner->IsActorBeingDestroyed() && !LiveOwner->HasActorBegunPlay();
		if (!TestTrue(TEXT("precondition: destroyed components still allocated and linked to their owner, owner live"), bRetained && bFlaggedDead && bOwnerLive))
		{
			AddError(TEXT("unsupported precondition: the destroyed-but-retained state could not be built"));
			return false;
		}
		TestTrue(TEXT("precondition: a destroyed component looks unregistered and not begun, which is why only the first check can refuse it"), !Dead->IsRegistered() && !Dead->HasBegunPlay());
		ExpectRejected(TEXT("destroyed encounter"), *Dead, TEXT("InvalidComponent"));
		// The component check is first: a destroyed component of the WRONG class is reported as invalid, not as the wrong class.
		ExpectRejected(TEXT("cluster on a destroyed posture"), *DeadPosture, TEXT("InvalidComponent"));
		TestTrue(TEXT("the owner stayed live through both calls"), IsValid(LiveOwner) && !LiveOwner->IsActorBeingDestroyed());
	}

	AddInfo(TEXT("Rejection paths on isolated plain actors; an owner that is being destroyed is covered by the code (IsActorBeingDestroyed) but not exercised here; the begun fixture is not a real startup."));
	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
