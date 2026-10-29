// Copyright One Boss Fight. All Rights Reserved.
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
#include "Components/SceneComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"
#include "Player/RPGBossBleed.h"
#include "Player/RPGBossLowSweep.h"
#include "Player/RPGBossLowSweepAdapters.h"
#include "Player/RPGBossPosture.h"
#include "UObject/Package.h"
#include "UObject/StrongObjectPtr.h"
#include "UObject/UnrealType.h"
#include <limits>

// SOURCE-ONLY until the lead releases execution. No LowSweep BeginPlay, Tick,
// StartForTest or Cancel is invoked. No tracker or damage resolver is created.
// These fixtures cannot prove a tracker entry/window, collision, damage, authored
// asset/Details value, wrapped angles, or an operational sweep. The only begun
// actor is a plain fixture owner BEFORE it receives an unregistered component.
namespace
{
namespace LowSweepTests
{
	struct FWorldScope
	{
		UWorld* World = nullptr;
		FWorldScope()
		{
			if (GEngine)
			{
				World = UWorld::CreateWorld(EWorldType::Game, false);
				if (World)
				{
					GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
					World->InitializeActorsForPlay(FURL());
				}
			}
		}
		~FWorldScope()
		{
			if (World)
			{
				GEngine->DestroyWorldContext(World);
				World->DestroyWorld(false);
			}
		}
		FWorldScope(const FWorldScope&) = delete;
		FWorldScope& operator=(const FWorldScope&) = delete;
		AActor* Spawn() const { return World ? World->SpawnActor<AActor>() : nullptr; }
	};

	FRPGLowSweepConfig RecordA()
	{
		FRPGLowSweepConfig R;
		R.bEnabled = false;
		R.MoveId = TEXT("UnresolvedSweepIdentity");
		R.Damage = 0.f;
		R.Reach = 0.5f;
		R.InnerRadius = 0.f;
		R.BladeHeight = 0.25f;
		R.SweepFromDegrees = -360.f;
		R.SweepToDegrees = 360.f;
		return R;
	}
	FRPGLowSweepConfig RecordB()
	{
		FRPGLowSweepConfig R;
		R.bEnabled = true;
		R.MoveId = TEXT("AnotherSweepIdentity");
		R.Damage = 31.25f;
		R.Reach = 491.5f;
		R.InnerRadius = 73.25f;
		R.BladeHeight = 22.75f;
		R.SweepFromDegrees = 135.f;
		R.SweepToDegrees = -42.f;
		return R;
	}
	FRPGParticipantConfig Config(const FRPGLowSweepConfig& R)
	{
		FRPGParticipantConfig C;
		C.LowSweep = R;
		return C;
	}
	FRPGLowSweepConfig Read(const URPGBossLowSweep& C)
	{
		FRPGLowSweepConfig R;
		R.bEnabled = C.bEnabled; R.MoveId = C.MoveId; R.Damage = C.Damage;
		R.Reach = C.Reach; R.InnerRadius = C.InnerRadius; R.BladeHeight = C.BladeHeight;
		R.SweepFromDegrees = C.SweepFromDegrees; R.SweepToDegrees = C.SweepToDegrees;
		return R;
	}
	bool Same(const FRPGLowSweepConfig& A, const FRPGLowSweepConfig& B)
	{
		return A.bEnabled == B.bEnabled && A.MoveId == B.MoveId && A.Damage == B.Damage
			&& A.Reach == B.Reach && A.InnerRadius == B.InnerRadius && A.BladeHeight == B.BladeHeight
			&& A.SweepFromDegrees == B.SweepFromDegrees && A.SweepToDegrees == B.SweepToDegrees;
	}
	struct FRuntime
	{
		bool Active, Registered, Begun, TickRegistered, CanTick;
		float Angle;
		int32 Sweeps, Hits, Jumps, Invulnerable, Blocked;
		explicit FRuntime(const URPGBossLowSweep& C)
			: Active(C.IsBladeActive()), Registered(C.IsRegistered()), Begun(C.HasBegunPlay()),
			  TickRegistered(C.PrimaryComponentTick.IsTickFunctionRegistered()), CanTick(C.PrimaryComponentTick.bCanEverTick),
			  Angle(C.GetBladeAngle()), Sweeps(C.GetSweepCount()), Hits(C.GetHitCount()), Jumps(C.GetJumpedCount()),
			  Invulnerable(C.GetInvulnerableCount()), Blocked(C.GetBlockedCount()) {}
		bool SameAs(const FRuntime& O) const
		{
			return Active == O.Active && Registered == O.Registered && Begun == O.Begun
				&& TickRegistered == O.TickRegistered && CanTick == O.CanTick && Angle == O.Angle
				&& Sweeps == O.Sweeps && Hits == O.Hits && Jumps == O.Jumps && Invulnerable == O.Invulnerable && Blocked == O.Blocked;
		}
	};
	TArray<const UActorComponent*> Owned(const AActor* Owner)
	{
		TArray<const UActorComponent*> Result;
		for (const UActorComponent* C : Owner->GetComponents()) { Result.Add(C); }
		return Result;
	}
	bool SameOwned(const TArray<const UActorComponent*>& A, const TArray<const UActorComponent*>& B)
	{
		if (A.Num() != B.Num()) { return false; }
		for (const UActorComponent* C : A) { if (!B.Contains(C)) { return false; } }
		return true;
	}
	TArray<FString> Paths()
	{
		// Written independently of the plan, in public authored-field order.
		return {TEXT("LowSweep.bEnabled"), TEXT("LowSweep.MoveId"), TEXT("LowSweep.Damage"),
			TEXT("LowSweep.Reach"), TEXT("LowSweep.InnerRadius"), TEXT("LowSweep.BladeHeight"),
			TEXT("LowSweep.SweepFromDegrees"), TEXT("LowSweep.SweepToDegrees")};
	}
	struct FBad
	{
		FString Name;
		TFunction<void(FRPGLowSweepConfig&)> Mutate;
		const TCHAR* Token;
		const TCHAR* Path;
	};
	TArray<FBad> BadCases()
	{
		TArray<FBad> Cases;
		struct FMember { const TCHAR* Name; float FRPGLowSweepConfig::*Value; };
		const FMember Members[] = {
			{TEXT("Damage"), &FRPGLowSweepConfig::Damage}, {TEXT("Reach"), &FRPGLowSweepConfig::Reach},
			{TEXT("InnerRadius"), &FRPGLowSweepConfig::InnerRadius}, {TEXT("BladeHeight"), &FRPGLowSweepConfig::BladeHeight},
			{TEXT("SweepFromDegrees"), &FRPGLowSweepConfig::SweepFromDegrees}, {TEXT("SweepToDegrees"), &FRPGLowSweepConfig::SweepToDegrees}
		};
		const float Values[] = {std::numeric_limits<float>::quiet_NaN(), std::numeric_limits<float>::infinity(), -std::numeric_limits<float>::infinity()};
		const TCHAR* Names[] = {TEXT("NaN"), TEXT("+Inf"), TEXT("-Inf")};
		// Field path constants are stable beyond this local array.
		const TCHAR* FieldPaths[] = {RPGBossLowSweepAdapters::FieldDamage, RPGBossLowSweepAdapters::FieldReach,
			RPGBossLowSweepAdapters::FieldInnerRadius, RPGBossLowSweepAdapters::FieldBladeHeight,
			RPGBossLowSweepAdapters::FieldSweepFromDegrees, RPGBossLowSweepAdapters::FieldSweepToDegrees};
		for (int32 I = 0; I < 6; ++I)
		{
			for (int32 J = 0; J < 3; ++J)
			{
				const auto Member = Members[I].Value;
				const float Value = Values[J];
				Cases.Add({FString::Printf(TEXT("%s %s"), Members[I].Name, Names[J]),
					[Member, Value](FRPGLowSweepConfig& R) { R.*Member = Value; }, TEXT("InvalidLowSweep.NotFinite"), FieldPaths[I]});
			}
		}
		Cases.Add({TEXT("negative damage"), [](FRPGLowSweepConfig& R) { R.Damage = -1.f; }, TEXT("InvalidLowSweep.Negative"), RPGBossLowSweepAdapters::FieldDamage});
		Cases.Add({TEXT("zero reach"), [](FRPGLowSweepConfig& R) { R.Reach = 0.f; }, TEXT("InvalidLowSweep.NotPositive"), RPGBossLowSweepAdapters::FieldReach});
		Cases.Add({TEXT("negative reach"), [](FRPGLowSweepConfig& R) { R.Reach = -0.25f; }, TEXT("InvalidLowSweep.NotPositive"), RPGBossLowSweepAdapters::FieldReach});
		Cases.Add({TEXT("negative inner"), [](FRPGLowSweepConfig& R) { R.InnerRadius = -0.25f; }, TEXT("InvalidLowSweep.Negative"), RPGBossLowSweepAdapters::FieldInnerRadius});
		Cases.Add({TEXT("inner equals reach"), [](FRPGLowSweepConfig& R) { R.InnerRadius = R.Reach; }, TEXT("InvalidLowSweep.InnerNotBelowReach"), RPGBossLowSweepAdapters::FieldInnerRadius});
		Cases.Add({TEXT("inner exceeds reach"), [](FRPGLowSweepConfig& R) { R.InnerRadius = R.Reach + 1.f; }, TEXT("InvalidLowSweep.InnerNotBelowReach"), RPGBossLowSweepAdapters::FieldInnerRadius});
		Cases.Add({TEXT("zero height"), [](FRPGLowSweepConfig& R) { R.BladeHeight = 0.f; }, TEXT("InvalidLowSweep.NotPositive"), RPGBossLowSweepAdapters::FieldBladeHeight});
		Cases.Add({TEXT("negative height"), [](FRPGLowSweepConfig& R) { R.BladeHeight = -0.5f; }, TEXT("InvalidLowSweep.NotPositive"), RPGBossLowSweepAdapters::FieldBladeHeight});
		Cases.Add({TEXT("from below range"), [](FRPGLowSweepConfig& R) { R.SweepFromDegrees = -360.25f; }, TEXT("InvalidLowSweep.AngleOutOfRange"), RPGBossLowSweepAdapters::FieldSweepFromDegrees});
		Cases.Add({TEXT("from above range"), [](FRPGLowSweepConfig& R) { R.SweepFromDegrees = 360.25f; }, TEXT("InvalidLowSweep.AngleOutOfRange"), RPGBossLowSweepAdapters::FieldSweepFromDegrees});
		Cases.Add({TEXT("to below range"), [](FRPGLowSweepConfig& R) { R.SweepToDegrees = -360.25f; }, TEXT("InvalidLowSweep.AngleOutOfRange"), RPGBossLowSweepAdapters::FieldSweepToDegrees});
		Cases.Add({TEXT("to above range"), [](FRPGLowSweepConfig& R) { R.SweepToDegrees = 360.25f; }, TEXT("InvalidLowSweep.AngleOutOfRange"), RPGBossLowSweepAdapters::FieldSweepToDegrees});
		Cases.Add({TEXT("None move"), [](FRPGLowSweepConfig& R) { R.MoveId = NAME_None; }, TEXT("InvalidDependency.Missing"), RPGBossLowSweepAdapters::FieldMoveId});
		Cases.Add({TEXT("space in move"), [](FRPGLowSweepConfig& R) { R.MoveId = TEXT("Move Id"); }, TEXT("InvalidDependency.Malformed"), RPGBossLowSweepAdapters::FieldMoveId});
		Cases.Add({TEXT("tab in move"), [](FRPGLowSweepConfig& R) { R.MoveId = TEXT("Move\tId"); }, TEXT("InvalidDependency.Malformed"), RPGBossLowSweepAdapters::FieldMoveId});
		Cases.Add({TEXT("control in move"), [](FRPGLowSweepConfig& R) { R.MoveId = FName(*FString::Printf(TEXT("Move%cId"), static_cast<TCHAR>(0x7f))); }, TEXT("InvalidDependency.Malformed"), RPGBossLowSweepAdapters::FieldMoveId});
		return Cases;
	}
	bool HasError(const FRPGHydrationResult& R, const TCHAR* Token, const TCHAR* Path)
	{
		return R.Errors.ContainsByPredicate([Token, Path](const FString& E) { return E.Contains(Token) && E.Contains(Path); });
	}
	TStrongObjectPtr<URPGBossDefinition> Definition(const FRPGLowSweepConfig& R)
	{
		TStrongObjectPtr<URPGBossDefinition> D(NewObject<URPGBossDefinition>());
		D->Schema = 1; D->DefinitionId = TEXT("LowSweepFixture"); D->PresentationId = TEXT("FixtureLook");
		D->Stats.MaxHealth = 1234.f; D->Stats.MaxPosture = 87.f;
		D->Stats.PostureRegenDelay = 2.f; D->Stats.PostureRegenRate = 3.f;
		D->LowSweep = R;
		for (const FString& Path : Paths())
		{
			FRPGParityField Field;
			Field.FieldPath = Path; Field.Value = TEXT("not parsed as config"); Field.Type = TEXT("fixture");
			Field.SourcePath = TEXT("synthetic only"); Field.SourceSHA256 = FString::ChrN(64, TEXT('a'));
			Field.SourceSite = TEXT("fixture"); Field.Origin = TEXT("test"); Field.Precedence = TEXT("fixture");
			Field.Destination = TEXT("fixture"); Field.FirstRead = TEXT("not runtime"); Field.Witness = TEXT("none");
			D->Fields.Add(Field);
		}
		return D;
	}
}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGLowSweepAssignTest, "OneBossFight.Binding.LowSweep.Assign", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGLowSweepAssignTest::RunTest(const FString& Parameters)
{
	using namespace LowSweepTests;
	FWorldScope Scope;
	AActor* Owner = Scope.Spawn();
	if (!TestNotNull(TEXT("owner"), Owner)) { return false; }
	TStrongObjectPtr<URPGBossLowSweep> Sweep(NewObject<URPGBossLowSweep>(Owner, TEXT("RPGBossLowSweep")));
	TStrongObjectPtr<URPGBossPosture> Other(NewObject<URPGBossPosture>(Owner));
	const float OtherBefore = Other->PostureMax;
	const auto Before = Owned(Owner);
	const FRuntime Runtime(*Sweep);
	const FRPGComponentPlan Plan = RPGBossLowSweepAdapters::MakeLowSweepPlan();
	TestTrue(TEXT("exact class/name and eight exact paths, without duplicates"), Plan.Class == URPGBossLowSweep::StaticClass()
		&& Plan.InstanceName == FName(TEXT("RPGBossLowSweep")) && Plan.RequiredFields == Paths());
	if (!TestTrue(TEXT("plan callback exists"), static_cast<bool>(Plan.Configure))) { return false; }
	FString Error = TEXT("stale diagnostic");
	TestTrue(TEXT("callback copies all eight nondefault fields"), Plan.Configure(*Sweep, Config(RecordA()), Error) && Error.IsEmpty() && Same(Read(*Sweep), RecordA()));
	TestTrue(TEXT("runtime, lifecycle, owner component set and unrelated component unchanged"), Runtime.SameAs(FRuntime(*Sweep))
		&& SameOwned(Before, Owned(Owner)) && Other->PostureMax == OtherBefore && Sweep->GetOwner() == Owner && Sweep->GetOuter() == Owner);
	TestTrue(TEXT("second call writes another complete record"), Plan.Configure(*Sweep, Config(RecordB()), Error) && Same(Read(*Sweep), RecordB()) && Runtime.SameAs(FRuntime(*Sweep)));
	AddInfo(TEXT("MoveId copied as syntactic identity only; no tracker lookup or sweep execution."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGLowSweepValidationTest, "OneBossFight.Binding.LowSweep.Validation", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGLowSweepValidationTest::RunTest(const FString& Parameters)
{
	using namespace LowSweepTests;
	FWorldScope Scope;
	AActor* Owner = Scope.Spawn();
	if (!TestNotNull(TEXT("owner"), Owner)) { return false; }
	TStrongObjectPtr<URPGBossLowSweep> Sweep(NewObject<URPGBossLowSweep>(Owner));
	const auto Before = Read(*Sweep);
	const FRuntime Runtime(*Sweep);
	const auto Components = Owned(Owner);
	for (const FBad& Case : BadCases())
	{
		auto R = RecordA(); // deliberately disabled; disabled must NOT bypass validation
		Case.Mutate(R);
		FString Error;
		TestFalse(Case.Name + TEXT(": validator rejects"), RPGBossLowSweepAdapters::ValidateLowSweep(R, Error));
		TestTrue(Case.Name + TEXT(": named validator field"), Error.StartsWith(Case.Token) && Error.Contains(Case.Path));
		TestFalse(Case.Name + TEXT(": callback rejects"), RPGBossLowSweepAdapters::ConfigureLowSweep(*Sweep, Config(R), Error));
		TestTrue(Case.Name + TEXT(": complete no-write and matching reason"), Error.StartsWith(Case.Token) && Error.Contains(Case.Path)
			&& Same(Read(*Sweep), Before) && Runtime.SameAs(FRuntime(*Sweep)) && SameOwned(Components, Owned(Owner)));
	}
	TArray<FRPGLowSweepConfig> Valid{RecordA(), RecordB(), FRPGLowSweepConfig()};
	auto Equal = RecordB(); Equal.SweepFromDegrees = 12.5f; Equal.SweepToDegrees = 12.5f; Valid.Add(Equal);
	auto Reverse = RecordB(); Reverse.SweepFromDegrees = 360.f; Reverse.SweepToDegrees = -360.f; Valid.Add(Reverse);
	auto Fractional = RecordA(); Fractional.Reach = 0.125f; Fractional.InnerRadius = 0.0625f; Fractional.BladeHeight = 0.0625f; Valid.Add(Fractional);
	for (const auto& R : Valid)
	{
		FString Error = TEXT("stale");
		TestTrue(TEXT("valid equality/reversal/boundary/fractional record validates and assigns"), RPGBossLowSweepAdapters::ValidateLowSweep(R, Error)
			&& Error.IsEmpty() && RPGBossLowSweepAdapters::ConfigureLowSweep(*Sweep, Config(R), Error) && Same(Read(*Sweep), R) && Runtime.SameAs(FRuntime(*Sweep)));
	}
	auto CheckFirst = [this](const FRPGLowSweepConfig& R, const TCHAR* Token, const TCHAR* Path)
	{
		FString E; RPGBossLowSweepAdapters::ValidateLowSweep(R, E);
		TestTrue(TEXT("first failure token and field precedence"), E.StartsWith(Token) && E.Contains(Path));
	};
	auto R = RecordB(); R.Damage = -1.f; R.SweepToDegrees = std::numeric_limits<float>::quiet_NaN();
	CheckFirst(R, TEXT("InvalidLowSweep.NotFinite"), RPGBossLowSweepAdapters::FieldSweepToDegrees);
	R = RecordB(); R.Reach = std::numeric_limits<float>::infinity(); R.SweepFromDegrees = std::numeric_limits<float>::quiet_NaN();
	CheckFirst(R, TEXT("InvalidLowSweep.NotFinite"), RPGBossLowSweepAdapters::FieldReach);
	R = RecordB(); R.Damage = -1.f; R.Reach = 0.f; R.MoveId = NAME_None;
	CheckFirst(R, TEXT("InvalidLowSweep.Negative"), RPGBossLowSweepAdapters::FieldDamage);
	R = RecordB(); R.InnerRadius = R.Reach; R.BladeHeight = 0.f;
	CheckFirst(R, TEXT("InvalidLowSweep.InnerNotBelowReach"), RPGBossLowSweepAdapters::FieldInnerRadius);
	R = RecordB(); R.SweepToDegrees = 361.f; R.MoveId = NAME_None;
	CheckFirst(R, TEXT("InvalidLowSweep.AngleOutOfRange"), RPGBossLowSweepAdapters::FieldSweepToDegrees);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGLowSweepIsolationTest, "OneBossFight.Binding.LowSweep.Isolation", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGLowSweepIsolationTest::RunTest(const FString& Parameters)
{
	using namespace LowSweepTests;
	FWorldScope Scope;
	AActor* OwnerA = Scope.Spawn(); AActor* OwnerB = Scope.Spawn();
	if (!TestTrue(TEXT("two owners"), OwnerA && OwnerB)) { return false; }
	TStrongObjectPtr<URPGBossLowSweep> A(NewObject<URPGBossLowSweep>(OwnerA));
	TStrongObjectPtr<URPGBossLowSweep> B(NewObject<URPGBossLowSweep>(OwnerB));
	TStrongObjectPtr<URPGBossLowSweep> Untouched(NewObject<URPGBossLowSweep>(OwnerB));
	TStrongObjectPtr<URPGBossBleed> Other(NewObject<URPGBossBleed>(OwnerA));
	const auto Original = Read(*Untouched); const auto Default = Read(*GetDefault<URPGBossLowSweep>());
	const FRuntime RuntimeA(*A), RuntimeB(*B);
	const auto OwnedA = Owned(OwnerA), OwnedB = Owned(OwnerB);
	const float BleedBefore = Other->InitialThreshold;
	auto Input = Config(RecordA()); FString Error;
	TestTrue(TEXT("A assignment"), RPGBossLowSweepAdapters::ConfigureLowSweep(*A, Input, Error));
	Input.LowSweep = RecordB();
	TestTrue(TEXT("input is a value snapshot"), Same(Read(*A), RecordA()));
	TestTrue(TEXT("B assignment"), RPGBossLowSweepAdapters::ConfigureLowSweep(*B, Input, Error));
	auto Invalid = RecordB(); Invalid.MoveId = NAME_None;
	TestFalse(TEXT("late invalid input refuses on configured A"), RPGBossLowSweepAdapters::ConfigureLowSweep(*A, Config(Invalid), Error));
	TestTrue(TEXT("owners and unrelated values fully isolated"), Same(Read(*A), RecordA()) && Same(Read(*B), RecordB())
		&& Same(Read(*Untouched), Original) && Same(Read(*GetDefault<URPGBossLowSweep>()), Default)
		&& RuntimeA.SameAs(FRuntime(*A)) && RuntimeB.SameAs(FRuntime(*B))
		&& SameOwned(OwnedA, Owned(OwnerA)) && SameOwned(OwnedB, Owned(OwnerB)) && Other->InitialThreshold == BleedBefore);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGLowSweepRejectionsTest, "OneBossFight.Binding.LowSweep.Rejections", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGLowSweepRejectionsTest::RunTest(const FString& Parameters)
{
	using namespace LowSweepTests;
	FWorldScope Scope;
	AActor* Owner = Scope.Spawn();
	if (!TestNotNull(TEXT("owner"), Owner)) { return false; }
	auto Check = [this](UActorComponent& C, const TCHAR* Token)
	{
		const bool Registered = C.IsRegistered(), Begun = C.HasBegunPlay();
		const URPGBossLowSweep* Sweep = Cast<URPGBossLowSweep>(&C);
		const auto Before = Sweep ? Read(*Sweep) : FRPGLowSweepConfig();
		FString Error;
		auto Bad = RecordA(); Bad.MoveId = NAME_None;
		for (const auto& R : TArray<FRPGLowSweepConfig>{RecordA(), Bad})
		{
			TestFalse(TEXT("lifecycle/class rejection"), RPGBossLowSweepAdapters::ConfigureLowSweep(C, Config(R), Error));
			TestTrue(TEXT("lifecycle before invalid record; no lifecycle write"), Error.StartsWith(Token) && C.IsRegistered() == Registered && C.HasBegunPlay() == Begun);
			if (Sweep) { TestTrue(TEXT("no partial configuration write on lifecycle refusal"), Same(Read(*Sweep), Before)); }
		}
	};
	TStrongObjectPtr<USceneComponent> Wrong(NewObject<USceneComponent>(Owner));
	Check(*Wrong, TEXT("WrongComponentClass"));
	TStrongObjectPtr<URPGBossBleed> WrongNative(NewObject<URPGBossBleed>(Owner));
	Check(*WrongNative, TEXT("WrongComponentClass"));
	TStrongObjectPtr<URPGBossLowSweep> Registered(NewObject<URPGBossLowSweep>(Owner));
	Registered->RegisterComponent();
	if (!TestTrue(TEXT("fixture registered but not begun"), Registered->IsRegistered() && !Registered->HasBegunPlay())) { return false; }
	Check(*Registered, TEXT("ComponentAlreadyRegistered"));
	AActor* LateOwner = Scope.Spawn();
	if (!TestNotNull(TEXT("late owner"), LateOwner)) { return false; }
	LateOwner->DispatchBeginPlay(); // plain actor, NO LowSweep component yet
	if (!TestTrue(TEXT("plain owner began"), LateOwner->HasActorBegunPlay())) { return false; }
	TStrongObjectPtr<URPGBossLowSweep> Late(NewObject<URPGBossLowSweep>(LateOwner));
	Check(*Late, TEXT("OwnerBegunPlay"));
	TStrongObjectPtr<URPGBossLowSweep> Orphan(NewObject<URPGBossLowSweep>(GetTransientPackage()));
	Check(*Orphan, TEXT("InvalidOwner"));
	TStrongObjectPtr<URPGBossLowSweep> Destroyed(NewObject<URPGBossLowSweep>(Owner));
	Destroyed->DestroyComponent();
	Check(*Destroyed, TEXT("InvalidComponent")); // retained object, not freed memory
	AddInfo(TEXT("ComponentBegunPlay guard source-only: no LowSweep BeginPlay invoked. Registered and plain begun-owner fixtures do not start a sweep."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGLowSweepCompileTest, "OneBossFight.Binding.LowSweep.Compile", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGLowSweepCompileTest::RunTest(const FString& Parameters)
{
	using namespace LowSweepTests;
	const auto Content = RPGCombatRegistry::Legacy(); // accepted dev-only synthetic contract
	if (!TestTrue(TEXT("synthetic content lease exists"), Content.IsValid())) { return false; }
	TSharedPtr<const FRPGParticipantConfig> Out;
	auto D = Definition(RecordA());
	auto Compile = [&Content](const URPGBossDefinition& Def, TSharedPtr<const FRPGParticipantConfig>& Output)
	{
		return RPGCombatHydration::CompileSyntheticParticipant(Def, Content, FString::ChrN(64, TEXT('b')), Output);
	};
	if (!TestTrue(TEXT("synthetic compiler positive control"), Compile(*D, Out).IsReady() && Out.IsValid())) { return false; }
	TestTrue(TEXT("all eight typed values copied, dev-only flag, same epoch; manifest Value not parsed"), Same(Out->LowSweep, RecordA()) && Out->bSyntheticFixture && Out->Content.Get() == Content.Get());
	D->LowSweep = RecordB();
	TestTrue(TEXT("compiled config is immutable value snapshot"), Same(Out->LowSweep, RecordA()));
	TestTrue(TEXT("next compile copies independent record"), Compile(*D, Out).IsReady() && Out.IsValid() && Same(Out->LowSweep, RecordB()));
	for (const FBad& Case : BadCases())
	{
		auto R = RecordA(); Case.Mutate(R);
		auto Broken = Definition(R);
		if (!Compile(*Definition(RecordA()), Out).IsReady() || !Out.IsValid()) { AddError(TEXT("valid sentinel failed")); return false; }
		auto Result = Compile(*Broken, Out);
		TestTrue(Case.Name + TEXT(": synthetic rejection clears old output with named field"), !Result.IsReady() && !Out.IsValid() && HasError(Result, Case.Token, Case.Path));
		if (!Compile(*Definition(RecordA()), Out).IsReady() || !Out.IsValid()) { AddError(TEXT("production sentinel failed")); return false; }
		Result = RPGCombatHydration::CompileParticipant(*Broken, Content, FString::ChrN(64, TEXT('b')), Out);
		TestTrue(Case.Name + TEXT(": production rejects before dependency loads, clears old output"), !Result.IsReady() && !Out.IsValid() && HasError(Result, Case.Token, Case.Path));
	}
	auto Defaults = Definition(FRPGLowSweepConfig());
	TestTrue(TEXT("additive defaults compile without substitution"), Compile(*Defaults, Out).IsReady() && Out.IsValid() && Same(Out->LowSweep, FRPGLowSweepConfig()));
	auto Retained = [this, &Compile, &Out](const TCHAR* Label, const TCHAR* Token, const TFunction<void(URPGBossDefinition&)>& Break)
	{
		if (!TestTrue(TEXT("fresh valid sentinel before retained rejection"), Compile(*Definition(RecordA()), Out).IsReady() && Out.IsValid())) { return; }
		auto Broken = Definition(RecordA()); Break(*Broken);
		const FRPGHydrationResult Result = Compile(*Broken, Out);
		TestTrue(Label, !Result.IsReady() && !Out.IsValid() && HasError(Result, Token, TEXT("")));
	};
	Retained(TEXT("existing Bleed validation retained"), TEXT("InvalidBleed.NotPositive"), [](URPGBossDefinition& D) { D.Bleed.InitialThreshold = 0.f; });
	Retained(TEXT("existing stats validation retained"), TEXT("invalid stats"), [](URPGBossDefinition& D) { D.Stats.MaxHealth = -1.f; });
	Retained(TEXT("existing manifest requirement retained"), TEXT("field manifest required"), [](URPGBossDefinition& D) { D.Fields.Reset(); });
	AddInfo(TEXT("Synthetic compiler/copy and early production refusal only; no positive real-asset compile or move-table resolution."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGLowSweepAuthoringTest, "OneBossFight.Binding.LowSweep.Authoring", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGLowSweepAuthoringTest::RunTest(const FString& Parameters)
{
	using namespace LowSweepTests;
	const UScriptStruct* Struct = FRPGLowSweepConfig::StaticStruct();
	int32 Count = 0;
	for (TFieldIterator<FProperty> It(Struct); It; ++It) { ++Count; TestTrue(TEXT("all record properties editable"), It->HasAnyPropertyFlags(CPF_Edit)); }
	TestEqual(TEXT("exact eight authored properties"), Count, 8);
	TestNotNull(TEXT("enabled reflected bool"), CastField<FBoolProperty>(Struct->FindPropertyByName(TEXT("bEnabled"))));
	TestNotNull(TEXT("MoveId reflected name"), CastField<FNameProperty>(Struct->FindPropertyByName(TEXT("MoveId"))));
	TestNotNull(TEXT("enabled has same native bool kind"), CastField<FBoolProperty>(URPGBossLowSweep::StaticClass()->FindPropertyByName(TEXT("bEnabled"))));
	TestNotNull(TEXT("MoveId has same native name kind"), CastField<FNameProperty>(URPGBossLowSweep::StaticClass()->FindPropertyByName(TEXT("MoveId"))));
	for (const TCHAR* Name : {TEXT("Damage"), TEXT("Reach"), TEXT("InnerRadius"), TEXT("BladeHeight"), TEXT("SweepFromDegrees"), TEXT("SweepToDegrees")})
	{
		TestNotNull(Name, CastField<FFloatProperty>(Struct->FindPropertyByName(Name)));
		TestNotNull(FString(Name) + TEXT(": same native float name"), CastField<FFloatProperty>(URPGBossLowSweep::StaticClass()->FindPropertyByName(Name)));
	}
	const FStructProperty* Property = CastField<FStructProperty>(URPGBossDefinition::StaticClass()->FindPropertyByName(TEXT("LowSweep")));
	TestTrue(TEXT("Data Asset exposes exact editable struct"), Property && Property->Struct == Struct && Property->HasAnyPropertyFlags(CPF_Edit));
	const FRPGLowSweepConfig Default;
	TestTrue(TEXT("native declaration defaults exactly matched"), Same(Default, Read(*GetDefault<URPGBossLowSweep>())));
	TestTrue(TEXT("explicit native default baseline"), Default.bEnabled && Default.MoveId == FName(TEXT("A4")) && Default.Damage == 20.f && Default.Reach == 380.f
		&& Default.InnerRadius == 60.f && Default.BladeHeight == 40.f && Default.SweepFromDegrees == 90.f && Default.SweepToDegrees == -90.f);
	auto D = Definition(Default);
	TestTrue(TEXT("fresh Data Asset record default"), Same(D->LowSweep, Default));
	for (const TCHAR* Name : {TEXT("bActive"), TEXT("BladeAngle"), TEXT("PreviousAngle"), TEXT("LastInstance"), TEXT("SweepGeneration"), TEXT("SweepCount"), TEXT("HitCount")})
	{
		TestNull(FString(Name) + TEXT(": runtime state absent from record"), Struct->FindPropertyByName(Name));
	}
	AddInfo(TEXT("Reflection/default declarations only, not a serialized asset, Details observation or tracker capability."));
	return true;
}
#endif
