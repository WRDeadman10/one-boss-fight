// Copyright One Boss Fight. All Rights Reserved.
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
#include "Components/SceneComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"
#include "Player/RPGBossBleed.h"
#include "Player/RPGBossShockwave.h"
#include "Player/RPGBossShockwaveAdapters.h"
#include "Player/RPGBossPosture.h"
#include "UObject/Package.h"
#include "UObject/StrongObjectPtr.h"
#include "UObject/UnrealType.h"
#include <limits>
#include <cmath>

// SOURCE-ONLY until the lead releases execution. No Shockwave BeginPlay, Tick,
// LaunchForTest or Cancel is invoked. No tracker or damage resolver is created.
// These fixtures cannot prove a tracker entry/window, collision, damage, authored
// asset/Details value, wave traversal, or an operational sweep. The only begun
// actor is a plain fixture owner BEFORE it receives an unregistered component.
namespace
{
namespace ShockwaveTests
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


	FRPGShockwaveConfig RecordA()
	{
		FRPGShockwaveConfig R;
		R.bEnabled=false; R.MoveId=TEXT("UnresolvedWaveIdentity");
		R.Damage=0.f; R.StartRadius=0.f; R.MaxRadius=0.5f; R.Speed=0.25f; R.Thickness=0.125f; R.JumpClearance=0.5f;
		return R;
	}
	FRPGShockwaveConfig RecordB()
	{
		FRPGShockwaveConfig R;
		R.bEnabled=true; R.MoveId=TEXT("AnotherWaveIdentity");
		R.Damage=53.25f; R.StartRadius=17.5f; R.MaxRadius=1111.f; R.Speed=876.f; R.Thickness=7.25f; R.JumpClearance=2.5f;
		return R;
	}

	FRPGParticipantConfig Config(const FRPGShockwaveConfig& R)
	{
		FRPGParticipantConfig C;
		C.Shockwave = R;
		return C;
	}
	FRPGShockwaveConfig Read(const URPGBossShockwave& C)
	{
		FRPGShockwaveConfig R;
		R.bEnabled = C.bEnabled; R.MoveId = C.MoveId; R.Damage = C.Damage;
		R.StartRadius = C.StartRadius; R.MaxRadius = C.MaxRadius; R.Speed = C.Speed;
		R.Thickness = C.Thickness; R.JumpClearance = C.JumpClearance;
		return R;
	}
	bool Same(const FRPGShockwaveConfig& A, const FRPGShockwaveConfig& B)
	{
		return A.bEnabled == B.bEnabled && A.MoveId == B.MoveId && A.Damage == B.Damage
			&& A.StartRadius == B.StartRadius && A.MaxRadius == B.MaxRadius && A.Speed == B.Speed
			&& A.Thickness == B.Thickness && A.JumpClearance == B.JumpClearance;
	}
	struct FRuntime
	{
		bool Active, Registered, Begun, TickRegistered, CanTick;
		float Angle;
		int32 Sweeps, Hits, Jumps, Invulnerable, Blocked;
		explicit FRuntime(const URPGBossShockwave& C)
			: Active(C.IsWaveActive()), Registered(C.IsRegistered()), Begun(C.HasBegunPlay()),
			  TickRegistered(C.PrimaryComponentTick.IsTickFunctionRegistered()), CanTick(C.PrimaryComponentTick.bCanEverTick),
			  Angle(C.GetRadius()), Sweeps(C.GetLaunchCount()), Hits(C.GetHitCount()), Jumps(C.GetJumpedCount()),
			  Invulnerable(C.GetInvulnerableCount()), Blocked(C.GetCentralPriorityCount()) {}
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
		return {TEXT("Shockwave.bEnabled"), TEXT("Shockwave.MoveId"), TEXT("Shockwave.Damage"),
			TEXT("Shockwave.StartRadius"), TEXT("Shockwave.MaxRadius"), TEXT("Shockwave.Speed"),
			TEXT("Shockwave.Thickness"), TEXT("Shockwave.JumpClearance")};
	}
	struct FBad
	{
		FString Name;
		TFunction<void(FRPGShockwaveConfig&)> Mutate;
		const TCHAR* Token;
		const TCHAR* Path;
	};
	TArray<FBad> BadCases()
	{
		TArray<FBad> Cases;
		struct FMember { const TCHAR* Name; float FRPGShockwaveConfig::*Value; };
		const FMember Members[] = {
			{TEXT("Damage"), &FRPGShockwaveConfig::Damage}, {TEXT("StartRadius"), &FRPGShockwaveConfig::StartRadius},
			{TEXT("MaxRadius"), &FRPGShockwaveConfig::MaxRadius}, {TEXT("Speed"), &FRPGShockwaveConfig::Speed},
			{TEXT("Thickness"), &FRPGShockwaveConfig::Thickness}, {TEXT("JumpClearance"), &FRPGShockwaveConfig::JumpClearance}
		};
		const float Values[] = {std::numeric_limits<float>::quiet_NaN(), std::numeric_limits<float>::infinity(), -std::numeric_limits<float>::infinity()};
		const TCHAR* Names[] = {TEXT("NaN"), TEXT("+Inf"), TEXT("-Inf")};
		// Field path constants are stable beyond this local array.
		const TCHAR* FieldPaths[] = {RPGBossShockwaveAdapters::FieldDamage, RPGBossShockwaveAdapters::FieldStartRadius,
			RPGBossShockwaveAdapters::FieldMaxRadius, RPGBossShockwaveAdapters::FieldSpeed,
			RPGBossShockwaveAdapters::FieldThickness, RPGBossShockwaveAdapters::FieldJumpClearance};
		for (int32 I = 0; I < 6; ++I)
		{
			for (int32 J = 0; J < 3; ++J)
			{
				const auto Member = Members[I].Value;
				const float Value = Values[J];
				Cases.Add({FString::Printf(TEXT("%s %s"), Members[I].Name, Names[J]),
					[Member, Value](FRPGShockwaveConfig& R) { R.*Member = Value; }, TEXT("InvalidShockwave.NotFinite"), FieldPaths[I]});
			}
		}
		Cases.Add({TEXT("negative damage"), [](FRPGShockwaveConfig& R) { R.Damage=-1.f; }, TEXT("InvalidShockwave.Negative"), RPGBossShockwaveAdapters::FieldDamage});
		Cases.Add({TEXT("negative start"), [](FRPGShockwaveConfig& R) { R.StartRadius=-0.25f; }, TEXT("InvalidShockwave.Negative"), RPGBossShockwaveAdapters::FieldStartRadius});
		Cases.Add({TEXT("zero max"), [](FRPGShockwaveConfig& R) { R.MaxRadius=0.f; }, TEXT("InvalidShockwave.NotPositive"), RPGBossShockwaveAdapters::FieldMaxRadius});
		Cases.Add({TEXT("negative max"), [](FRPGShockwaveConfig& R) { R.MaxRadius=-1.f; }, TEXT("InvalidShockwave.NotPositive"), RPGBossShockwaveAdapters::FieldMaxRadius});
		Cases.Add({TEXT("max equal start"), [](FRPGShockwaveConfig& R) { R.StartRadius=1.f; R.MaxRadius=1.f; }, TEXT("InvalidShockwave.MaxNotAboveStart"), RPGBossShockwaveAdapters::FieldMaxRadius});
		Cases.Add({TEXT("max below start"), [](FRPGShockwaveConfig& R) { R.StartRadius=2.f; R.MaxRadius=1.f; }, TEXT("InvalidShockwave.MaxNotAboveStart"), RPGBossShockwaveAdapters::FieldMaxRadius});
		Cases.Add({TEXT("Speed zero"), [](FRPGShockwaveConfig& R) { R.Speed=0.f; }, TEXT("InvalidShockwave.NotPositive"), RPGBossShockwaveAdapters::FieldSpeed});
		Cases.Add({TEXT("Speed negative"), [](FRPGShockwaveConfig& R) { R.Speed=-0.25f; }, TEXT("InvalidShockwave.NotPositive"), RPGBossShockwaveAdapters::FieldSpeed});
		Cases.Add({TEXT("Thickness zero"), [](FRPGShockwaveConfig& R) { R.Thickness=0.f; }, TEXT("InvalidShockwave.NotPositive"), RPGBossShockwaveAdapters::FieldThickness});
		Cases.Add({TEXT("Thickness negative"), [](FRPGShockwaveConfig& R) { R.Thickness=-0.25f; }, TEXT("InvalidShockwave.NotPositive"), RPGBossShockwaveAdapters::FieldThickness});
		Cases.Add({TEXT("JumpClearance zero"), [](FRPGShockwaveConfig& R) { R.JumpClearance=0.f; }, TEXT("InvalidShockwave.NotPositive"), RPGBossShockwaveAdapters::FieldJumpClearance});
		Cases.Add({TEXT("JumpClearance negative"), [](FRPGShockwaveConfig& R) { R.JumpClearance=-0.25f; }, TEXT("InvalidShockwave.NotPositive"), RPGBossShockwaveAdapters::FieldJumpClearance});
		Cases.Add({TEXT("StartRadius next float above ceiling"), [](FRPGShockwaveConfig& R) { R.StartRadius=std::nextafter(RPGBossShockwaveAdapters::MaxAuthoredMagnitude,std::numeric_limits<float>::infinity()); }, TEXT("InvalidShockwave.AboveCeiling"), RPGBossShockwaveAdapters::FieldStartRadius});
		Cases.Add({TEXT("MaxRadius next float above ceiling"), [](FRPGShockwaveConfig& R) { R.MaxRadius=std::nextafter(RPGBossShockwaveAdapters::MaxAuthoredMagnitude,std::numeric_limits<float>::infinity()); }, TEXT("InvalidShockwave.AboveCeiling"), RPGBossShockwaveAdapters::FieldMaxRadius});
		Cases.Add({TEXT("Speed next float above ceiling"), [](FRPGShockwaveConfig& R) { R.Speed=std::nextafter(RPGBossShockwaveAdapters::MaxAuthoredMagnitude,std::numeric_limits<float>::infinity()); }, TEXT("InvalidShockwave.AboveCeiling"), RPGBossShockwaveAdapters::FieldSpeed});
		Cases.Add({TEXT("Thickness next float above ceiling"), [](FRPGShockwaveConfig& R) { R.Thickness=std::nextafter(RPGBossShockwaveAdapters::MaxAuthoredMagnitude,std::numeric_limits<float>::infinity()); }, TEXT("InvalidShockwave.AboveCeiling"), RPGBossShockwaveAdapters::FieldThickness});
		Cases.Add({TEXT("JumpClearance next float above ceiling"), [](FRPGShockwaveConfig& R) { R.JumpClearance=std::nextafter(RPGBossShockwaveAdapters::MaxAuthoredMagnitude,std::numeric_limits<float>::infinity()); }, TEXT("InvalidShockwave.AboveCeiling"), RPGBossShockwaveAdapters::FieldJumpClearance});
		Cases.Add({TEXT("X301 radius overflow inputs"), [](FRPGShockwaveConfig& R) { R.StartRadius=3.36879526214505e38f; R.MaxRadius=std::numeric_limits<float>::max(); R.Speed=3.36879526214505e38f; R.Thickness=1.f; }, TEXT("InvalidShockwave.AboveCeiling"), RPGBossShockwaveAdapters::FieldStartRadius});
		Cases.Add({TEXT("X301 band overflow inputs"), [](FRPGShockwaveConfig& R) { R.StartRadius=2.5521175490829424e38f; R.MaxRadius=std::numeric_limits<float>::max(); R.Speed=1.f; R.Thickness=std::numeric_limits<float>::max(); }, TEXT("InvalidShockwave.AboveCeiling"), RPGBossShockwaveAdapters::FieldStartRadius});
		Cases.Add({TEXT("None move"), [](FRPGShockwaveConfig& R) { R.MoveId=NAME_None; }, TEXT("InvalidDependency.Missing"), RPGBossShockwaveAdapters::FieldMoveId});
		Cases.Add({TEXT("space move"), [](FRPGShockwaveConfig& R) { R.MoveId=TEXT("Wave Id"); }, TEXT("InvalidDependency.Malformed"), RPGBossShockwaveAdapters::FieldMoveId});
		Cases.Add({TEXT("tab move"), [](FRPGShockwaveConfig& R) { R.MoveId=TEXT("Wave\tId"); }, TEXT("InvalidDependency.Malformed"), RPGBossShockwaveAdapters::FieldMoveId});
		Cases.Add({TEXT("control move"), [](FRPGShockwaveConfig& R) { R.MoveId=FName(*FString::Printf(TEXT("Wave%cId"),static_cast<TCHAR>(0x7f))); }, TEXT("InvalidDependency.Malformed"), RPGBossShockwaveAdapters::FieldMoveId});

		return Cases;
	}
	bool HasError(const FRPGHydrationResult& R, const TCHAR* Token, const TCHAR* Path)
	{
		return R.Errors.ContainsByPredicate([Token, Path](const FString& E) { return E.Contains(Token) && E.Contains(Path); });
	}
	TStrongObjectPtr<URPGBossDefinition> Definition(const FRPGShockwaveConfig& R)
	{
		TStrongObjectPtr<URPGBossDefinition> D(NewObject<URPGBossDefinition>());
		D->Schema = 1; D->DefinitionId = TEXT("ShockwaveFixture"); D->PresentationId = TEXT("FixtureLook");
		D->Stats.MaxHealth = 1234.f; D->Stats.MaxPosture = 87.f;
		D->Stats.PostureRegenDelay = 2.f; D->Stats.PostureRegenRate = 3.f;
		D->Shockwave = R;
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

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGShockwaveAssignTest, "OneBossFight.Binding.Shockwave.Assign", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGShockwaveAssignTest::RunTest(const FString& Parameters)
{
	using namespace ShockwaveTests;
	FWorldScope Scope;
	AActor* Owner = Scope.Spawn();
	if (!TestNotNull(TEXT("owner"), Owner)) { return false; }
	TStrongObjectPtr<URPGBossShockwave> Sweep(NewObject<URPGBossShockwave>(Owner, TEXT("RPGBossShockwave")));
	TStrongObjectPtr<URPGBossPosture> Other(NewObject<URPGBossPosture>(Owner));
	const float OtherBefore = Other->PostureMax;
	const auto Before = Owned(Owner);
	const FRuntime Runtime(*Sweep);
	const FRPGComponentPlan Plan = RPGBossShockwaveAdapters::MakeShockwavePlan();
	TestTrue(TEXT("exact class/name and eight exact paths, without duplicates"), Plan.Class == URPGBossShockwave::StaticClass()
		&& Plan.InstanceName == FName(TEXT("RPGBossShockwave")) && Plan.RequiredFields == Paths());
	if (!TestTrue(TEXT("plan callback exists"), static_cast<bool>(Plan.Configure))) { return false; }
	FString Error = TEXT("stale diagnostic");
	TestTrue(TEXT("callback copies all eight nondefault fields"), Plan.Configure(*Sweep, Config(RecordA()), Error) && Error.IsEmpty() && Same(Read(*Sweep), RecordA()));
	TestTrue(TEXT("runtime, lifecycle, owner component set and unrelated component unchanged"), Runtime.SameAs(FRuntime(*Sweep))
		&& SameOwned(Before, Owned(Owner)) && Other->PostureMax == OtherBefore && Sweep->GetOwner() == Owner && Sweep->GetOuter() == Owner);
	TestTrue(TEXT("second call writes another complete record"), Plan.Configure(*Sweep, Config(RecordB()), Error) && Same(Read(*Sweep), RecordB()) && Runtime.SameAs(FRuntime(*Sweep)));
	AddInfo(TEXT("MoveId copied as syntactic identity only; no tracker lookup or sweep execution."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGShockwaveValidationTest, "OneBossFight.Binding.Shockwave.Validation", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGShockwaveValidationTest::RunTest(const FString& Parameters)
{
	using namespace ShockwaveTests;
	FWorldScope Scope;
	AActor* Owner = Scope.Spawn();
	if (!TestNotNull(TEXT("owner"), Owner)) { return false; }
	TStrongObjectPtr<URPGBossShockwave> Sweep(NewObject<URPGBossShockwave>(Owner));
	const auto Before = Read(*Sweep);
	const FRuntime Runtime(*Sweep);
	const auto Components = Owned(Owner);
	for (const FBad& Case : BadCases())
	{
		auto R = RecordA(); // deliberately disabled; disabled must NOT bypass validation
		Case.Mutate(R);
		FString Error;
		TestFalse(Case.Name + TEXT(": validator rejects"), RPGBossShockwaveAdapters::ValidateShockwave(R, Error));
		TestTrue(Case.Name + TEXT(": named validator field"), Error.StartsWith(Case.Token) && Error.Contains(Case.Path));
		TestFalse(Case.Name + TEXT(": callback rejects"), RPGBossShockwaveAdapters::ConfigureShockwave(*Sweep, Config(R), Error));
		TestTrue(Case.Name + TEXT(": complete no-write and matching reason"), Error.StartsWith(Case.Token) && Error.Contains(Case.Path)
			&& Same(Read(*Sweep), Before) && Runtime.SameAs(FRuntime(*Sweep)) && SameOwned(Components, Owned(Owner)));
	}

	TArray<FRPGShockwaveConfig> Valid{RecordA(),RecordB(),FRPGShockwaveConfig()};
	const float Ceiling=RPGBossShockwaveAdapters::MaxAuthoredMagnitude;
	auto Pair=RecordB(); Pair.StartRadius=std::nextafter(Ceiling,0.f); Pair.MaxRadius=Ceiling; Valid.Add(Pair);
	auto Max=RecordA(); Max.MaxRadius=Ceiling; Valid.Add(Max);
	auto Fast=RecordA(); Fast.Speed=Ceiling; Valid.Add(Fast);
	auto Wide=RecordA(); Wide.Thickness=Ceiling; Valid.Add(Wide);
	auto High=RecordA(); High.JumpClearance=Ceiling; Valid.Add(High);
	auto Damage=RecordA(); Damage.Damage=std::numeric_limits<float>::max(); Valid.Add(Damage); // finite health-damage payload, not wave arithmetic
	for (const auto& R : Valid)
	{
		FString E=TEXT("stale");
		TestTrue(TEXT("valid sub-1/zero/inclusive-ceiling/Damage-FLT_MAX record validates and assigns"),
			RPGBossShockwaveAdapters::ValidateShockwave(R,E)&&E.IsEmpty()
			&&RPGBossShockwaveAdapters::ConfigureShockwave(*Sweep,Config(R),E)&&Same(Read(*Sweep),R)&&Runtime.SameAs(FRuntime(*Sweep)));
	}
	auto CheckFirst=[this](const FRPGShockwaveConfig& R,const TCHAR* Token,const TCHAR* Path)
	{
		FString E; RPGBossShockwaveAdapters::ValidateShockwave(R,E);
		TestTrue(TEXT("validation precedence"),E.StartsWith(Token)&&E.Contains(Path));
	};
	auto R=RecordB(); R.Damage=-1.f; R.JumpClearance=std::numeric_limits<float>::quiet_NaN();
	CheckFirst(R,TEXT("InvalidShockwave.NotFinite"),RPGBossShockwaveAdapters::FieldJumpClearance);
	R=RecordB(); R.StartRadius=std::numeric_limits<float>::infinity(); R.Speed=std::numeric_limits<float>::quiet_NaN();
	CheckFirst(R,TEXT("InvalidShockwave.NotFinite"),RPGBossShockwaveAdapters::FieldStartRadius);
	R=RecordB(); R.StartRadius=Ceiling; R.MaxRadius=Ceiling;
	CheckFirst(R,TEXT("InvalidShockwave.MaxNotAboveStart"),RPGBossShockwaveAdapters::FieldMaxRadius); // inclusive Start ceiling itself passes, but no legal greater Max exists
	R=RecordB(); R.MaxRadius=Ceiling*2.f; R.Speed=0.f;
	CheckFirst(R,TEXT("InvalidShockwave.AboveCeiling"),RPGBossShockwaveAdapters::FieldMaxRadius);
	R=RecordB(); R.JumpClearance=0.f; R.MoveId=NAME_None;
	CheckFirst(R,TEXT("InvalidShockwave.NotPositive"),RPGBossShockwaveAdapters::FieldJumpClearance);

	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGShockwaveIsolationTest, "OneBossFight.Binding.Shockwave.Isolation", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGShockwaveIsolationTest::RunTest(const FString& Parameters)
{
	using namespace ShockwaveTests;
	FWorldScope Scope;
	AActor* OwnerA = Scope.Spawn(); AActor* OwnerB = Scope.Spawn();
	if (!TestTrue(TEXT("two owners"), OwnerA && OwnerB)) { return false; }
	TStrongObjectPtr<URPGBossShockwave> A(NewObject<URPGBossShockwave>(OwnerA));
	TStrongObjectPtr<URPGBossShockwave> B(NewObject<URPGBossShockwave>(OwnerB));
	TStrongObjectPtr<URPGBossShockwave> Untouched(NewObject<URPGBossShockwave>(OwnerB));
	TStrongObjectPtr<URPGBossBleed> Other(NewObject<URPGBossBleed>(OwnerA));
	const auto Original = Read(*Untouched); const auto Default = Read(*GetDefault<URPGBossShockwave>());
	const FRuntime RuntimeA(*A), RuntimeB(*B);
	const auto OwnedA = Owned(OwnerA), OwnedB = Owned(OwnerB);
	const float BleedBefore = Other->InitialThreshold;
	auto Input = Config(RecordA()); FString Error;
	TestTrue(TEXT("A assignment"), RPGBossShockwaveAdapters::ConfigureShockwave(*A, Input, Error));
	Input.Shockwave = RecordB();
	TestTrue(TEXT("input is a value snapshot"), Same(Read(*A), RecordA()));
	TestTrue(TEXT("B assignment"), RPGBossShockwaveAdapters::ConfigureShockwave(*B, Input, Error));
	auto Invalid = RecordB(); Invalid.MoveId = NAME_None;
	TestFalse(TEXT("late invalid input refuses on configured A"), RPGBossShockwaveAdapters::ConfigureShockwave(*A, Config(Invalid), Error));
	TestTrue(TEXT("owners and unrelated values fully isolated"), Same(Read(*A), RecordA()) && Same(Read(*B), RecordB())
		&& Same(Read(*Untouched), Original) && Same(Read(*GetDefault<URPGBossShockwave>()), Default)
		&& RuntimeA.SameAs(FRuntime(*A)) && RuntimeB.SameAs(FRuntime(*B))
		&& SameOwned(OwnedA, Owned(OwnerA)) && SameOwned(OwnedB, Owned(OwnerB)) && Other->InitialThreshold == BleedBefore);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGShockwaveRejectionsTest, "OneBossFight.Binding.Shockwave.Rejections", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGShockwaveRejectionsTest::RunTest(const FString& Parameters)
{
	using namespace ShockwaveTests;
	FWorldScope Scope;
	AActor* Owner = Scope.Spawn();
	if (!TestNotNull(TEXT("owner"), Owner)) { return false; }
	auto Check = [this](UActorComponent& C, const TCHAR* Token)
	{
		const bool Registered = C.IsRegistered(), Begun = C.HasBegunPlay();
		const URPGBossShockwave* Sweep = Cast<URPGBossShockwave>(&C);
		const auto Before = Sweep ? Read(*Sweep) : FRPGShockwaveConfig();
		FString Error;
		auto Bad = RecordA(); Bad.MoveId = NAME_None;
		for (const auto& R : TArray<FRPGShockwaveConfig>{RecordA(), Bad})
		{
			TestFalse(TEXT("lifecycle/class rejection"), RPGBossShockwaveAdapters::ConfigureShockwave(C, Config(R), Error));
			TestTrue(TEXT("lifecycle before invalid record; no lifecycle write"), Error.StartsWith(Token) && C.IsRegistered() == Registered && C.HasBegunPlay() == Begun);
			if (Sweep) { TestTrue(TEXT("no partial configuration write on lifecycle refusal"), Same(Read(*Sweep), Before)); }
		}
	};
	TStrongObjectPtr<USceneComponent> Wrong(NewObject<USceneComponent>(Owner));
	Check(*Wrong, TEXT("WrongComponentClass"));
	TStrongObjectPtr<URPGBossBleed> WrongNative(NewObject<URPGBossBleed>(Owner));
	Check(*WrongNative, TEXT("WrongComponentClass"));
	TStrongObjectPtr<URPGBossShockwave> Registered(NewObject<URPGBossShockwave>(Owner));
	Registered->RegisterComponent();
	if (!TestTrue(TEXT("fixture registered but not begun"), Registered->IsRegistered() && !Registered->HasBegunPlay())) { return false; }
	Check(*Registered, TEXT("ComponentAlreadyRegistered"));
	AActor* LateOwner = Scope.Spawn();
	if (!TestNotNull(TEXT("late owner"), LateOwner)) { return false; }
	LateOwner->DispatchBeginPlay(); // plain actor, NO Shockwave component yet
	if (!TestTrue(TEXT("plain owner began"), LateOwner->HasActorBegunPlay())) { return false; }
	TStrongObjectPtr<URPGBossShockwave> Late(NewObject<URPGBossShockwave>(LateOwner));
	Check(*Late, TEXT("OwnerBegunPlay"));
	TStrongObjectPtr<URPGBossShockwave> Orphan(NewObject<URPGBossShockwave>(GetTransientPackage()));
	Check(*Orphan, TEXT("InvalidOwner"));
	TStrongObjectPtr<URPGBossShockwave> Destroyed(NewObject<URPGBossShockwave>(Owner));
	Destroyed->DestroyComponent();
	Check(*Destroyed, TEXT("InvalidComponent")); // retained object, not freed memory
	AddInfo(TEXT("ComponentBegunPlay guard source-only: no Shockwave BeginPlay invoked. Registered and plain begun-owner fixtures do not start a sweep."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGShockwaveCompileTest, "OneBossFight.Binding.Shockwave.Compile", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGShockwaveCompileTest::RunTest(const FString& Parameters)
{
	using namespace ShockwaveTests;
	const auto Content = RPGCombatRegistry::Legacy(); // accepted dev-only synthetic contract
	if (!TestTrue(TEXT("synthetic content lease exists"), Content.IsValid())) { return false; }
	TSharedPtr<const FRPGParticipantConfig> Out;
	auto D = Definition(RecordA());
	auto Compile = [&Content](const URPGBossDefinition& Def, TSharedPtr<const FRPGParticipantConfig>& Output)
	{
		return RPGCombatHydration::CompileSyntheticParticipant(Def, Content, FString::ChrN(64, TEXT('b')), Output);
	};
	if (!TestTrue(TEXT("synthetic compiler positive control"), Compile(*D, Out).IsReady() && Out.IsValid())) { return false; }
	TestTrue(TEXT("all eight typed values copied, dev-only flag, same epoch; manifest Value not parsed"), Same(Out->Shockwave, RecordA()) && Out->bSyntheticFixture && Out->Content.Get() == Content.Get());
	D->Shockwave = RecordB();
	TestTrue(TEXT("compiled config is immutable value snapshot"), Same(Out->Shockwave, RecordA()));
	TestTrue(TEXT("next compile copies independent record"), Compile(*D, Out).IsReady() && Out.IsValid() && Same(Out->Shockwave, RecordB()));
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
	auto Defaults = Definition(FRPGShockwaveConfig());
	TestTrue(TEXT("additive defaults compile without substitution"), Compile(*Defaults, Out).IsReady() && Out.IsValid() && Same(Out->Shockwave, FRPGShockwaveConfig()));
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

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGShockwaveAuthoringTest, "OneBossFight.Binding.Shockwave.Authoring", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGShockwaveAuthoringTest::RunTest(const FString& Parameters)
{
	using namespace ShockwaveTests;
	const UScriptStruct* Struct = FRPGShockwaveConfig::StaticStruct();
	int32 Count = 0;
	for (TFieldIterator<FProperty> It(Struct); It; ++It) { ++Count; TestTrue(TEXT("all record properties editable"), It->HasAnyPropertyFlags(CPF_Edit)); }
	TestEqual(TEXT("exact eight authored properties"), Count, 8);
	TestNotNull(TEXT("enabled reflected bool"), CastField<FBoolProperty>(Struct->FindPropertyByName(TEXT("bEnabled"))));
	TestNotNull(TEXT("MoveId reflected name"), CastField<FNameProperty>(Struct->FindPropertyByName(TEXT("MoveId"))));
	TestNotNull(TEXT("enabled has same native bool kind"), CastField<FBoolProperty>(URPGBossShockwave::StaticClass()->FindPropertyByName(TEXT("bEnabled"))));
	TestNotNull(TEXT("MoveId has same native name kind"), CastField<FNameProperty>(URPGBossShockwave::StaticClass()->FindPropertyByName(TEXT("MoveId"))));
	for (const TCHAR* Name : {TEXT("Damage"), TEXT("StartRadius"), TEXT("MaxRadius"), TEXT("Speed"), TEXT("Thickness"), TEXT("JumpClearance")})
	{
		TestNotNull(Name, CastField<FFloatProperty>(Struct->FindPropertyByName(Name)));
		TestNotNull(FString(Name) + TEXT(": same native float name"), CastField<FFloatProperty>(URPGBossShockwave::StaticClass()->FindPropertyByName(Name)));
	}
	const FStructProperty* Property = CastField<FStructProperty>(URPGBossDefinition::StaticClass()->FindPropertyByName(TEXT("Shockwave")));
	TestTrue(TEXT("Data Asset exposes exact editable struct"), Property && Property->Struct == Struct && Property->HasAnyPropertyFlags(CPF_Edit));
	const FRPGShockwaveConfig Default;
	TestTrue(TEXT("native declaration defaults exactly matched"), Same(Default, Read(*GetDefault<URPGBossShockwave>())));

	TestTrue(TEXT("explicit native default baseline"),Default.bEnabled&&Default.MoveId==FName(TEXT("A6"))
		&&Default.Damage==48.f&&Default.StartRadius==200.f&&Default.MaxRadius==1100.f&&Default.Speed==1000.f&&Default.Thickness==180.f&&Default.JumpClearance==50.f);

	auto D = Definition(Default);
	TestTrue(TEXT("fresh Data Asset record default"), Same(D->Shockwave, Default));
	for (const TCHAR* Name : {TEXT("bActive"), TEXT("bClearedBand"), TEXT("bResolved"), TEXT("Radius"), TEXT("Origin"), TEXT("GroundZ"), TEXT("LaunchGeneration"), TEXT("LaunchCount"), TEXT("HitCount")})
	{
		TestNull(FString(Name) + TEXT(": runtime state absent from record"), Struct->FindPropertyByName(Name));
	}
	AddInfo(TEXT("Reflection/default declarations only, not a serialized asset, Details observation or tracker capability."));
	return true;
}
#endif
