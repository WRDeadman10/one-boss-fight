// Copyright One Boss Fight. All Rights Reserved.
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
#include "Components/SceneComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"
#include "Player/RPGBossBleed.h"
#include "Player/RPGBossLook.h"
#include "Player/RPGBossLookAdapters.h"
#include "Player/RPGBossPosture.h"
#include "UObject/Package.h"
#include "UObject/StrongObjectPtr.h"
#include "UObject/UnrealType.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMesh.h"
#include "UObject/TopLevelAssetPath.h"

// SOURCE-ONLY until a lead release. No Look BeginPlay, Apply, enable-for-test,
// Revert, mesh loading or runtime appearance operation. Plain begun-owner fixture
// receives its unregistered Look component only AFTER the owner began play.
namespace
{
namespace LookTests
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




	FSoftObjectPath MakePath(const TCHAR* Package, const TCHAR* Asset, const TCHAR* Sub = TEXT(""))
	{
		return FSoftObjectPath(FTopLevelAssetPath(FName(Package), FName(Asset)), FString(Sub));
	}
	TSoftObjectPtr<USkeletalMesh> Mesh(const FSoftObjectPath& Path)
	{
		return TSoftObjectPtr<USkeletalMesh>(Path);
	}
	TSoftObjectPtr<UStaticMesh> Weapon(const FSoftObjectPath& Path)
	{
		return TSoftObjectPtr<UStaticMesh>(Path);
	}
	FRPGLookConfig RecordA()
	{
		FRPGLookConfig R;
		R.bEnabled = false;
		R.Body = Mesh(MakePath(TEXT("/SyntheticMount/Look/A"), TEXT("Body")));
		R.Pieces = {Mesh(MakePath(TEXT("/SyntheticMount/Look/A"), TEXT("Crown"))), Mesh(MakePath(TEXT("/SyntheticMount/Look/A"), TEXT("Mantle")))};
		R.Sword = Weapon(MakePath(TEXT("/SyntheticMount/Look/A"), TEXT("Sword")));
		R.SwordSocket = TEXT("Custom.Grip-A");
		return R;
	}
	FRPGLookConfig RecordB()
	{
		FRPGLookConfig R;
		R.bEnabled = true;
		R.Body = Mesh(MakePath(TEXT("/OtherSynthetic/Look/B"), TEXT("BodyB")));
		R.Pieces = {Mesh(MakePath(TEXT("/OtherSynthetic/Look/B"), TEXT("Gauntlet")))};
		R.Sword = Weapon(MakePath(TEXT("/OtherSynthetic/Look/B"), TEXT("SwordB")));
		R.SwordSocket = TEXT("GripB");
		return R;
	}
	FRPGParticipantConfig Config(const FRPGLookConfig& R)
	{
		FRPGParticipantConfig C;
		C.Look = R;
		return C;
	}
	FRPGLookConfig Read(const URPGBossLook& Look)
	{
		FRPGLookConfig R;
		R.bEnabled = Look.bEnabled;
		R.Body = Look.Body;
		R.Pieces = Look.Pieces;
		R.Sword = Look.Sword;
		R.SwordSocket = Look.SwordSocket;
		return R;
	}
	bool Same(const FRPGLookConfig& A, const FRPGLookConfig& B)
	{
		if (A.bEnabled != B.bEnabled || A.Body.ToSoftObjectPath() != B.Body.ToSoftObjectPath()
			|| A.Sword.ToSoftObjectPath() != B.Sword.ToSoftObjectPath() || A.SwordSocket != B.SwordSocket || A.Pieces.Num() != B.Pieces.Num())
		{
			return false;
		}
		for (int32 Index = 0; Index < A.Pieces.Num(); ++Index)
		{
			if (A.Pieces[Index].ToSoftObjectPath() != B.Pieces[Index].ToSoftObjectPath()) { return false; }
		}
		return true;
	}
	struct FRuntime
	{
		bool Applied, Registered, Begun, TickRegistered, CanTick;
		int32 PieceCount, HiddenWeapons;
		const USkeletalMeshComponent* Body;
		const UStaticMeshComponent* Sword;
		explicit FRuntime(const URPGBossLook& Look)
			: Applied(Look.IsApplied()), Registered(Look.IsRegistered()), Begun(Look.HasBegunPlay()),
			TickRegistered(Look.PrimaryComponentTick.IsTickFunctionRegistered()), CanTick(Look.PrimaryComponentTick.bCanEverTick),
			PieceCount(Look.GetPieceCount()), HiddenWeapons(Look.GetHiddenPackWeaponCount()), Body(Look.GetBodyComponent()), Sword(Look.GetSwordComponent()) {}
		bool SameAs(const FRuntime& O) const
		{
			return Applied == O.Applied && Registered == O.Registered && Begun == O.Begun && TickRegistered == O.TickRegistered
				&& CanTick == O.CanTick && PieceCount == O.PieceCount && HiddenWeapons == O.HiddenWeapons && Body == O.Body && Sword == O.Sword;
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
		return {TEXT("Look.bEnabled"), TEXT("Look.Body"), TEXT("Look.Pieces"), TEXT("Look.Sword"), TEXT("Look.SwordSocket")};
	}
	struct FBad
	{
		FString Name;
		TFunction<void(FRPGLookConfig&)> Mutate;
		const TCHAR* Token;
		const TCHAR* Path;
	};
	TArray<FBad> BadCases()
	{
		TArray<FBad> Cases;
		Cases.Add({TEXT("null body"), [](FRPGLookConfig& R) { R.Body.Reset(); }, TEXT("InvalidDependency.Missing"), TEXT("Look.Body")});
		Cases.Add({TEXT("null sword"), [](FRPGLookConfig& R) { R.Sword.Reset(); }, TEXT("InvalidDependency.Missing"), TEXT("Look.Sword")});
		Cases.Add({TEXT("late null piece"), [](FRPGLookConfig& R) { R.Pieces.Add(TSoftObjectPtr<USkeletalMesh>()); }, TEXT("InvalidDependency.Missing"), TEXT("Look.Pieces[2]")});
		Cases.Add({TEXT("duplicate piece"), [](FRPGLookConfig& R) { R.Pieces.Add(R.Pieces[0]); }, TEXT("InvalidDependency.Duplicate"), TEXT("Look.Pieces[2]")});
		Cases.Add({TEXT("case-insensitive asset identity duplicate"), [](FRPGLookConfig& R) { R.Pieces.Add(Mesh(MakePath(TEXT("/syntheticmount/look/a"), TEXT("crown")))); }, TEXT("InvalidDependency.Duplicate"), TEXT("Look.Pieces[2]")});
		Cases.Add({TEXT("None socket"), [](FRPGLookConfig& R) { R.SwordSocket = NAME_None; }, TEXT("InvalidDependency.Missing"), TEXT("Look.SwordSocket")});
		Cases.Add({TEXT("mixed-case None socket"), [](FRPGLookConfig& R) { R.SwordSocket = TEXT("nOnE"); }, TEXT("InvalidDependency.Missing"), TEXT("Look.SwordSocket")});
		Cases.Add({TEXT("space socket"), [](FRPGLookConfig& R) { R.SwordSocket = TEXT("Grip A"); }, TEXT("InvalidDependency.Malformed"), TEXT("Look.SwordSocket")});
		Cases.Add({TEXT("tab socket"), [](FRPGLookConfig& R) { R.SwordSocket = TEXT("Grip\tA"); }, TEXT("InvalidDependency.Malformed"), TEXT("Look.SwordSocket")});
		Cases.Add({TEXT("control socket"), [](FRPGLookConfig& R) { R.SwordSocket = FName(*FString::Printf(TEXT("Grip%cA"), static_cast<TCHAR>(0x7f))); }, TEXT("InvalidDependency.Malformed"), TEXT("Look.SwordSocket")});
		struct FMalformed { const TCHAR* Name; FSoftObjectPath Path; };
		// Exact accepted Bleed malformed-path fixture set, repeated for each reference slot.
		const FMalformed Malformed[] = {
			{TEXT("whitespace package"), MakePath(TEXT("/SyntheticMount/A B"), TEXT("Mesh"))},
			{TEXT("control object"), MakePath(TEXT("/SyntheticMount/A"), TEXT("Mesh\tX"))},
			{TEXT("subobject"), MakePath(TEXT("/SyntheticMount/A"), TEXT("Mesh"), TEXT("Sub"))},
			{TEXT("relative package"), MakePath(TEXT("Relative/A"), TEXT("Mesh"))},
			{TEXT("no folder"), MakePath(TEXT("/Root"), TEXT("Mesh"))},
			{TEXT("empty mount"), MakePath(TEXT("//Look/A"), TEXT("Mesh"))},
			{TEXT("repeated separator"), MakePath(TEXT("/SyntheticMount//A"), TEXT("Mesh"))},
			{TEXT("object dot"), MakePath(TEXT("/SyntheticMount/A"), TEXT("Mesh.X"))},
			{TEXT("object pipe"), MakePath(TEXT("/SyntheticMount/A"), TEXT("Mesh|X"))},
			{TEXT("package pipe"), MakePath(TEXT("/SyntheticMount/A|B"), TEXT("Mesh"))},
		};
		for (const FMalformed& M : Malformed)
		{
			const FSoftObjectPath Path = M.Path;
			Cases.Add({FString(M.Name) + TEXT(" body"), [Path](FRPGLookConfig& R) { R.Body = Mesh(Path); }, TEXT("InvalidDependency.Malformed"), TEXT("Look.Body")});
			Cases.Add({FString(M.Name) + TEXT(" piece"), [Path](FRPGLookConfig& R) { R.Pieces.Add(Mesh(Path)); }, TEXT("InvalidDependency.Malformed"), TEXT("Look.Pieces[2]")});
			Cases.Add({FString(M.Name) + TEXT(" sword"), [Path](FRPGLookConfig& R) { R.Sword = Weapon(Path); }, TEXT("InvalidDependency.Malformed"), TEXT("Look.Sword")});
		}
		return Cases;
	}
	bool HasError(const FRPGHydrationResult& R, const TCHAR* Token, const TCHAR* Path)
	{
		return R.Errors.ContainsByPredicate([Token, Path](const FString& E) { return E.Contains(Token) && E.Contains(Path); });
	}
	TStrongObjectPtr<URPGBossDefinition> Definition(const FRPGLookConfig& R)
	{
		TStrongObjectPtr<URPGBossDefinition> D(NewObject<URPGBossDefinition>());
		D->Schema = 1; D->DefinitionId = TEXT("LookFixture"); D->PresentationId = TEXT("FixtureLook");
		D->Stats.MaxHealth = 1234.f; D->Stats.MaxPosture = 87.f;
		D->Stats.PostureRegenDelay = 2.f; D->Stats.PostureRegenRate = 3.f;
		D->Look = R;
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

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGLookAssignTest, "OneBossFight.Binding.Look.Assign", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGLookAssignTest::RunTest(const FString& Parameters)
{
	using namespace LookTests;
	FWorldScope Scope;
	AActor* Owner = Scope.Spawn();
	if (!TestNotNull(TEXT("owner"), Owner)) { return false; }
	TStrongObjectPtr<URPGBossLook> Look(NewObject<URPGBossLook>(Owner, TEXT("RPGBossLook")));
	TStrongObjectPtr<URPGBossPosture> Other(NewObject<URPGBossPosture>(Owner));
	const float OtherBefore = Other->PostureMax;
	const auto Before = Owned(Owner);
	const FRuntime Runtime(*Look);
	const FRPGComponentPlan Plan = RPGBossLookAdapters::MakeLookPlan();
	TestTrue(TEXT("exact class/name and five exact paths, without duplicates"), Plan.Class == URPGBossLook::StaticClass()
		&& Plan.InstanceName == FName(TEXT("RPGBossLook")) && Plan.RequiredFields == Paths());
	if (!TestTrue(TEXT("plan callback exists"), static_cast<bool>(Plan.Configure))) { return false; }
	FString Error = TEXT("stale diagnostic");
	TestTrue(TEXT("callback copies all five nondefault fields"), Plan.Configure(*Look, Config(RecordA()), Error) && Error.IsEmpty() && Same(Read(*Look), RecordA()));
	TestTrue(TEXT("runtime, lifecycle, owner component set and unrelated component unchanged"), Runtime.SameAs(FRuntime(*Look))
		&& SameOwned(Before, Owned(Owner)) && Other->PostureMax == OtherBefore && Look->GetOwner() == Owner && Look->GetOuter() == Owner);
	TestTrue(TEXT("second call writes another complete record"), Plan.Configure(*Look, Config(RecordB()), Error) && Same(Read(*Look), RecordB()) && Runtime.SameAs(FRuntime(*Look)));
	AddInfo(TEXT("Soft paths copied without loading; socket existence and runtime look are unresolved."));
	return true;
}


IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGLookValidationTest, "OneBossFight.Binding.Look.Validation", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGLookValidationTest::RunTest(const FString& Parameters)
{
	using namespace LookTests;
	FWorldScope Scope;
	AActor* Owner = Scope.Spawn();
	if (!TestNotNull(TEXT("owner"), Owner)) { return false; }
	TStrongObjectPtr<URPGBossLook> Look(NewObject<URPGBossLook>(Owner));
	const auto Before = Read(*Look);
	const FRuntime Runtime(*Look);
	const auto Components = Owned(Owner);
	for (const FBad& Case : BadCases())
	{
		auto R = RecordA(); // disabled records still validate all five fields
		Case.Mutate(R);
		FString Error;
		TestFalse(Case.Name + TEXT(": validator refuses"), RPGBossLookAdapters::ValidateLook(R, Error));
		TestTrue(Case.Name + TEXT(": named token and indexed field"), Error.StartsWith(Case.Token) && Error.Contains(Case.Path));
		TestFalse(Case.Name + TEXT(": callback refuses"), RPGBossLookAdapters::ConfigureLook(*Look, Config(R), Error));
		TestTrue(Case.Name + TEXT(": no partial writes"), Error.StartsWith(Case.Token) && Error.Contains(Case.Path)
			&& Same(Read(*Look), Before) && Runtime.SameAs(FRuntime(*Look)) && SameOwned(Components, Owned(Owner)));
	}
	TArray<FRPGLookConfig> Valid{RecordA(), RecordB(), FRPGLookConfig()};
	auto Empty = RecordA();
	Empty.Pieces.Reset();
	Valid.Add(Empty);
	auto LongSocket = RecordB();
	LongSocket.SwordSocket = FName(*FString::ChrN(1000, TEXT('x')));
	Valid.Add(LongSocket); // long representable FName; no new record length cap
	for (const FRPGLookConfig& R : Valid)
	{
		FString Error = TEXT("stale");
		TestTrue(TEXT("valid non-mounted paths/empty pieces/defaults/long socket"), RPGBossLookAdapters::ValidateLook(R, Error) && Error.IsEmpty()
			&& RPGBossLookAdapters::ConfigureLook(*Look, Config(R), Error) && Same(Read(*Look), R) && Runtime.SameAs(FRuntime(*Look)));
	}
	auto First = [this](const FRPGLookConfig& R, const TCHAR* Token, const TCHAR* Path)
	{
		FString Error;
		TestFalse(TEXT("multi-invalid record refused"), RPGBossLookAdapters::ValidateLook(R, Error));
		TestTrue(TEXT("first failure order"), Error.StartsWith(Token) && Error.Contains(Path));
	};
	auto R = RecordA();
	R.Body.Reset(); R.Pieces[0].Reset(); R.Sword.Reset(); R.SwordSocket = NAME_None;
	First(R, TEXT("InvalidDependency.Missing"), TEXT("Look.Body"));
	R = RecordA(); R.Pieces[0].Reset(); R.Pieces.Add(R.Pieces[1]); R.Sword.Reset();
	First(R, TEXT("InvalidDependency.Missing"), TEXT("Look.Pieces[0]"));
	R = RecordA(); R.Pieces.Add(R.Pieces[0]); R.Sword.Reset();
	First(R, TEXT("InvalidDependency.Duplicate"), TEXT("Look.Pieces[2]"));
	R = RecordA(); R.Sword.Reset(); R.SwordSocket = NAME_None;
	First(R, TEXT("InvalidDependency.Missing"), TEXT("Look.Sword"));
	AddInfo(TEXT("Structure only; no path is loaded or class/socket existence certified."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGLookIsolationTest, "OneBossFight.Binding.Look.Isolation", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGLookIsolationTest::RunTest(const FString& Parameters)
{
	using namespace LookTests;
	FWorldScope Scope;
	AActor* OwnerA = Scope.Spawn(); AActor* OwnerB = Scope.Spawn();
	if (!TestTrue(TEXT("two owners"), OwnerA && OwnerB)) { return false; }
	TStrongObjectPtr<URPGBossLook> A(NewObject<URPGBossLook>(OwnerA));
	TStrongObjectPtr<URPGBossLook> B(NewObject<URPGBossLook>(OwnerB));
	TStrongObjectPtr<URPGBossLook> Untouched(NewObject<URPGBossLook>(OwnerB));
	TStrongObjectPtr<URPGBossBleed> Other(NewObject<URPGBossBleed>(OwnerA));
	const auto Original = Read(*Untouched); const auto Default = Read(*GetDefault<URPGBossLook>());
	const FRuntime RuntimeA(*A), RuntimeB(*B);
	const auto OwnedA = Owned(OwnerA), OwnedB = Owned(OwnerB);
	const float BleedBefore = Other->InitialThreshold;
	auto Input = Config(RecordA()); FString Error;
	TestTrue(TEXT("A assignment"), RPGBossLookAdapters::ConfigureLook(*A, Input, Error));
	Input.Look.Pieces[0] = Mesh(MakePath(TEXT("/SyntheticMount/Changed"), TEXT("Piece")));
	Input.Look.Pieces.Add(Mesh(MakePath(TEXT("/SyntheticMount/Changed"), TEXT("Extra"))));
	TestTrue(TEXT("native piece array owns an independent copy"),Same(Read(*A),RecordA()));
	Input.Look = RecordB();
	TestTrue(TEXT("input is a value snapshot"), Same(Read(*A), RecordA()));
	TestTrue(TEXT("B assignment"), RPGBossLookAdapters::ConfigureLook(*B, Input, Error));
	auto Invalid = RecordB(); Invalid.Sword.Reset();
	TestFalse(TEXT("late invalid input refuses on configured A"), RPGBossLookAdapters::ConfigureLook(*A, Config(Invalid), Error));
	TestTrue(TEXT("owners and unrelated values fully isolated"), Same(Read(*A), RecordA()) && Same(Read(*B), RecordB())
		&& Same(Read(*Untouched), Original) && Same(Read(*GetDefault<URPGBossLook>()), Default)
		&& RuntimeA.SameAs(FRuntime(*A)) && RuntimeB.SameAs(FRuntime(*B))
		&& SameOwned(OwnedA, Owned(OwnerA)) && SameOwned(OwnedB, Owned(OwnerB)) && Other->InitialThreshold == BleedBefore);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGLookRejectionsTest, "OneBossFight.Binding.Look.Rejections", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGLookRejectionsTest::RunTest(const FString& Parameters)
{
	using namespace LookTests;
	FWorldScope Scope;
	AActor* Owner = Scope.Spawn();
	if (!TestNotNull(TEXT("owner"), Owner)) { return false; }
	auto Check = [this](UActorComponent& C, const TCHAR* Token)
	{
		const bool Registered = C.IsRegistered(), Begun = C.HasBegunPlay();
		const URPGBossLook* Look = Cast<URPGBossLook>(&C);
		const auto Before = Look ? Read(*Look) : FRPGLookConfig();
		FString Error;
		auto Bad = RecordA(); Bad.Body.Reset();
		for (const auto& R : TArray<FRPGLookConfig>{RecordA(), Bad})
		{
			TestFalse(TEXT("lifecycle/class rejection"), RPGBossLookAdapters::ConfigureLook(C, Config(R), Error));
			TestTrue(TEXT("lifecycle before invalid record; no lifecycle write"), Error.StartsWith(Token) && C.IsRegistered() == Registered && C.HasBegunPlay() == Begun);
			if (Look) { TestTrue(TEXT("no partial configuration write on lifecycle refusal"), Same(Read(*Look), Before)); }
		}
	};
	TStrongObjectPtr<USceneComponent> Wrong(NewObject<USceneComponent>(Owner));
	Check(*Wrong, TEXT("WrongComponentClass"));
	TStrongObjectPtr<URPGBossBleed> WrongNative(NewObject<URPGBossBleed>(Owner));
	Check(*WrongNative, TEXT("WrongComponentClass"));
	TStrongObjectPtr<URPGBossLook> Registered(NewObject<URPGBossLook>(Owner));
	Registered->RegisterComponent();
	if (!TestTrue(TEXT("fixture registered but not begun"), Registered->IsRegistered() && !Registered->HasBegunPlay())) { return false; }
	Check(*Registered, TEXT("ComponentAlreadyRegistered"));
	AActor* LateOwner = Scope.Spawn();
	if (!TestNotNull(TEXT("late owner"), LateOwner)) { return false; }
	LateOwner->DispatchBeginPlay(); // plain actor, NO Look component yet
	if (!TestTrue(TEXT("plain owner began"), LateOwner->HasActorBegunPlay())) { return false; }
	TStrongObjectPtr<URPGBossLook> Late(NewObject<URPGBossLook>(LateOwner));
	Check(*Late, TEXT("OwnerBegunPlay"));
	TStrongObjectPtr<URPGBossLook> Orphan(NewObject<URPGBossLook>(GetTransientPackage()));
	Check(*Orphan, TEXT("InvalidOwner"));
	TStrongObjectPtr<URPGBossLook> Destroyed(NewObject<URPGBossLook>(Owner));
	Destroyed->DestroyComponent();
	Check(*Destroyed, TEXT("InvalidComponent")); // retained object, not freed memory
	AddInfo(TEXT("ComponentBegunPlay guard source-only: no Look BeginPlay invoked. Registered and plain begun-owner fixtures do not apply a look."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGLookCompileTest, "OneBossFight.Binding.Look.Compile", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGLookCompileTest::RunTest(const FString& Parameters)
{
	using namespace LookTests;
	const auto Content = RPGCombatRegistry::Legacy(); // accepted dev-only synthetic contract
	if (!TestTrue(TEXT("synthetic content lease exists"), Content.IsValid())) { return false; }
	TSharedPtr<const FRPGParticipantConfig> Out;
	auto D = Definition(RecordA());
	auto Compile = [&Content](const URPGBossDefinition& Def, TSharedPtr<const FRPGParticipantConfig>& Output)
	{
		return RPGCombatHydration::CompileSyntheticParticipant(Def, Content, FString::ChrN(64, TEXT('b')), Output);
	};
	if (!TestTrue(TEXT("synthetic compiler positive control"), Compile(*D, Out).IsReady() && Out.IsValid())) { return false; }
	TestTrue(TEXT("all five typed values copied, dev-only flag, same epoch; manifest Value not parsed"), Same(Out->Look, RecordA()) && Out->bSyntheticFixture && Out->Content.Get() == Content.Get());
	D->Look = RecordB();
	TestTrue(TEXT("compiled config is immutable value snapshot"), Same(Out->Look, RecordA()));
	TestTrue(TEXT("next compile copies independent record"),Compile(*D,Out).IsReady()&&Out.IsValid()&&Same(Out->Look,RecordB()));
	D->Look.Pieces[0] = Mesh(MakePath(TEXT("/SyntheticMount/Changed"), TEXT("Piece")));
	TestTrue(TEXT("compiled piece array owns an independent copy"),Out.IsValid()&&Same(Out->Look,RecordB()));
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
	auto EmptyPieces = Definition(RecordA());
	EmptyPieces->Look.Pieces.Reset();
	TestTrue(TEXT("empty pieces compile without defaults substituted"), Compile(*EmptyPieces, Out).IsReady() && Out.IsValid() && Out->Look.Pieces.IsEmpty());
	auto Defaults = Definition(FRPGLookConfig());
	TestTrue(TEXT("additive defaults compile without substitution"), Compile(*Defaults, Out).IsReady() && Out.IsValid() && Same(Out->Look, FRPGLookConfig()));
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
	AddInfo(TEXT("Synthetic compiler/copy and early production refusal only; no positive real-asset compile or mesh/socket resolution."));
	return true;
}


IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGLookAuthoringTest, "OneBossFight.Binding.Look.Authoring", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGLookAuthoringTest::RunTest(const FString& Parameters)
{
	using namespace LookTests;
	const UScriptStruct* Struct = FRPGLookConfig::StaticStruct();
	int32 Count = 0;
	for (TFieldIterator<FProperty> It(Struct); It; ++It)
	{
		++Count;
		TestTrue(TEXT("authored field editable"), It->HasAnyPropertyFlags(CPF_Edit));
	}
	TestEqual(TEXT("exact five authored properties"), Count, 5);
	TestNotNull(TEXT("enabled bool"), CastField<FBoolProperty>(Struct->FindPropertyByName(TEXT("bEnabled"))));
	TestNotNull(TEXT("socket FName"), CastField<FNameProperty>(Struct->FindPropertyByName(TEXT("SwordSocket"))));
	const FSoftObjectProperty* Body = CastField<FSoftObjectProperty>(Struct->FindPropertyByName(TEXT("Body")));
	const FSoftObjectProperty* Sword = CastField<FSoftObjectProperty>(Struct->FindPropertyByName(TEXT("Sword")));
	const FArrayProperty* Pieces = CastField<FArrayProperty>(Struct->FindPropertyByName(TEXT("Pieces")));
	const FSoftObjectProperty* Inner = Pieces ? CastField<FSoftObjectProperty>(Pieces->Inner) : nullptr;
	TestTrue(TEXT("typed body/sword/piece soft references"), Body && Body->PropertyClass == USkeletalMesh::StaticClass()
		&& Sword && Sword->PropertyClass == UStaticMesh::StaticClass() && Inner && Inner->PropertyClass == USkeletalMesh::StaticClass());
	const FStructProperty* Property = CastField<FStructProperty>(URPGBossDefinition::StaticClass()->FindPropertyByName(TEXT("Look")));
	TestTrue(TEXT("editable Data Asset record"), Property && Property->Struct == Struct && Property->HasAnyPropertyFlags(CPF_Edit));
	const FRPGLookConfig Default;
	TestTrue(TEXT("all five native defaults including constructor soft paths"), Same(Default, Read(*GetDefault<URPGBossLook>())));
	TestTrue(TEXT("explicit declared baseline"), Default.bEnabled && Default.SwordSocket == FName(TEXT("HeavySwordSocket_R")) && Default.Pieces.Num() == 3
		&& Default.Body.ToString().EndsWith(TEXT("/Body/SK_Boss01_Body.SK_Boss01_Body"))
		&& Default.Sword.ToString().EndsWith(TEXT("/Weapons/SM_Boss01_Greatsword.SM_Boss01_Greatsword")));
	for (const TCHAR* N : {TEXT("bApplied"), TEXT("PieceCount"), TEXT("bSavedHidden"), TEXT("BodyComponent"), TEXT("SwordComponent"), TEXT("PieceComponents"), TEXT("HiddenPackWeapons"), TEXT("SavedTickOption")})
	{
		TestNull(FString(N) + TEXT(" not authored"), Struct->FindPropertyByName(N));
	}
	AddInfo(TEXT("Reflection/default comparison only, no mesh load/Apply/serialized Details proof."));
	return true;
}
#endif
