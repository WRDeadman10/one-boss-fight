// Copyright One Boss Fight. All Rights Reserved.
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
#include "Components/SceneComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"
#include "Player/RPGBossBleed.h"
#include "Player/RPGBossCloseClipSwap.h"
#include "Player/RPGBossCloseClipSwapAdapters.h"
#include "Player/RPGBossPosture.h"
#include "UObject/Package.h"
#include "UObject/StrongObjectPtr.h"
#include "UObject/UnrealType.h"
#include "Animation/AnimMontage.h"
#include "UObject/TopLevelAssetPath.h"

// STAGING ONLY, UNRUN. No CloseClipSwap BeginPlay/Tick/ApplyNowForTest,
// ability reflection, montage load, test-enable call or gameplay operation.
namespace
{
namespace CloseClipSwapTests
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
	TSoftObjectPtr<UAnimMontage> Montage(const FSoftObjectPath& Path)
	{
		return TSoftObjectPtr<UAnimMontage>(Path);
	}
	FRPGCloseClipSwapConfig RecordA()
	{
		FRPGCloseClipSwapConfig R;
		R.CloseAbilityClassName = TEXT("Custom.CloseAbility-A");
		R.AttackMontagesName = TEXT("Custom.Montages-A");
		R.A1Montage = Montage(MakePath(TEXT("/SyntheticMount/Close/A"), TEXT("A1")));
		R.A3aMontage = Montage(MakePath(TEXT("/SyntheticMount/Close/A"), TEXT("A3a")));
		R.A3bMontage = Montage(MakePath(TEXT("/SyntheticMount/Close/A"), TEXT("A3b")));
		return R;
	}
	FRPGCloseClipSwapConfig RecordB()
	{
		FRPGCloseClipSwapConfig R;
		R.CloseAbilityClassName = TEXT("CustomAbilityB");
		R.AttackMontagesName = TEXT("CustomMontagesB");
		R.A1Montage = Montage(MakePath(TEXT("/OtherSynthetic/Close/B"), TEXT("A1")));
		R.A3aMontage = Montage(MakePath(TEXT("/OtherSynthetic/Close/B"), TEXT("A3a")));
		R.A3bMontage = Montage(MakePath(TEXT("/OtherSynthetic/Close/B"), TEXT("A3b")));
		return R;
	}
	FRPGParticipantConfig Config(const FRPGCloseClipSwapConfig& R)
	{
		FRPGParticipantConfig C;
		C.CloseClipSwap = R;
		return C;
	}
	FRPGCloseClipSwapConfig Read(const URPGBossCloseClipSwap& CloseClipSwap)
	{
		FRPGCloseClipSwapConfig R;
		R.CloseAbilityClassName = CloseClipSwap.CloseAbilityClassName;
		R.AttackMontagesName = CloseClipSwap.AttackMontagesName;
		R.A1Montage = CloseClipSwap.A1Montage;
		R.A3aMontage = CloseClipSwap.A3aMontage;
		R.A3bMontage = CloseClipSwap.A3bMontage;
		return R;
	}
	bool Same(const FRPGCloseClipSwapConfig& A, const FRPGCloseClipSwapConfig& B)
	{
		return A.CloseAbilityClassName == B.CloseAbilityClassName && A.AttackMontagesName == B.AttackMontagesName && A.A1Montage.ToSoftObjectPath() == B.A1Montage.ToSoftObjectPath() && A.A3aMontage.ToSoftObjectPath() == B.A3aMontage.ToSoftObjectPath() && A.A3bMontage.ToSoftObjectPath() == B.A3bMontage.ToSoftObjectPath();
	}

	struct FRuntime
	{
		bool Applied, Registered, Begun, TickRegistered, CanTick;
		int32 Entries, Applies, Restores;
		FString LastResult;
		explicit FRuntime(const URPGBossCloseClipSwap& C)
			: Applied(C.IsApplied()), Registered(C.IsRegistered()), Begun(C.HasBegunPlay()),
			TickRegistered(C.PrimaryComponentTick.IsTickFunctionRegistered()), CanTick(C.PrimaryComponentTick.bCanEverTick),
			Entries(C.GetAppliedEntryCount()), Applies(C.GetApplyCount()), Restores(C.GetRestoreCount()), LastResult(C.GetLastResult()) {}
		bool SameAs(const FRuntime& O) const
		{
			return Applied == O.Applied && Registered == O.Registered && Begun == O.Begun && TickRegistered == O.TickRegistered
				&& CanTick == O.CanTick && Entries == O.Entries && Applies == O.Applies && Restores == O.Restores && LastResult == O.LastResult;
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
		return {TEXT("CloseClipSwap.CloseAbilityClassName"), TEXT("CloseClipSwap.AttackMontagesName"), TEXT("CloseClipSwap.A1Montage"), TEXT("CloseClipSwap.A3aMontage"), TEXT("CloseClipSwap.A3bMontage")};
	}
	struct FBad
	{
		FString Name;
		TFunction<void(FRPGCloseClipSwapConfig&)> Mutate;
		const TCHAR* Token;
		const TCHAR* Path;
	};
	TArray<FBad> BadCases()
	{
		TArray<FBad> Cases;
		Cases.Add({TEXT("CloseAbilityClassName None"), [](FRPGCloseClipSwapConfig& R) { R.CloseAbilityClassName = NAME_None; }, TEXT("InvalidDependency.Missing"), TEXT("CloseClipSwap.CloseAbilityClassName")});
		Cases.Add({TEXT("CloseAbilityClassName mixed-case None"), [](FRPGCloseClipSwapConfig& R) { R.CloseAbilityClassName = TEXT("nOnE"); }, TEXT("InvalidDependency.Missing"), TEXT("CloseClipSwap.CloseAbilityClassName")});
		Cases.Add({TEXT("CloseAbilityClassName space"), [](FRPGCloseClipSwapConfig& R) { R.CloseAbilityClassName = TEXT("Ability A"); }, TEXT("InvalidDependency.Malformed"), TEXT("CloseClipSwap.CloseAbilityClassName")});
		Cases.Add({TEXT("CloseAbilityClassName tab"), [](FRPGCloseClipSwapConfig& R) { R.CloseAbilityClassName = TEXT("Ability	A"); }, TEXT("InvalidDependency.Malformed"), TEXT("CloseClipSwap.CloseAbilityClassName")});
		Cases.Add({TEXT("CloseAbilityClassName control"), [](FRPGCloseClipSwapConfig& R) { R.CloseAbilityClassName = FName(*FString::Printf(TEXT("Ability%cA"), static_cast<TCHAR>(0x7f))); }, TEXT("InvalidDependency.Malformed"), TEXT("CloseClipSwap.CloseAbilityClassName")});
		Cases.Add({TEXT("AttackMontagesName None"), [](FRPGCloseClipSwapConfig& R) { R.AttackMontagesName = NAME_None; }, TEXT("InvalidDependency.Missing"), TEXT("CloseClipSwap.AttackMontagesName")});
		Cases.Add({TEXT("AttackMontagesName mixed-case None"), [](FRPGCloseClipSwapConfig& R) { R.AttackMontagesName = TEXT("nOnE"); }, TEXT("InvalidDependency.Missing"), TEXT("CloseClipSwap.AttackMontagesName")});
		Cases.Add({TEXT("AttackMontagesName space"), [](FRPGCloseClipSwapConfig& R) { R.AttackMontagesName = TEXT("Ability A"); }, TEXT("InvalidDependency.Malformed"), TEXT("CloseClipSwap.AttackMontagesName")});
		Cases.Add({TEXT("AttackMontagesName tab"), [](FRPGCloseClipSwapConfig& R) { R.AttackMontagesName = TEXT("Ability	A"); }, TEXT("InvalidDependency.Malformed"), TEXT("CloseClipSwap.AttackMontagesName")});
		Cases.Add({TEXT("AttackMontagesName control"), [](FRPGCloseClipSwapConfig& R) { R.AttackMontagesName = FName(*FString::Printf(TEXT("Ability%cA"), static_cast<TCHAR>(0x7f))); }, TEXT("InvalidDependency.Malformed"), TEXT("CloseClipSwap.AttackMontagesName")});
		Cases.Add({TEXT("null A1Montage"), [](FRPGCloseClipSwapConfig& R) { R.A1Montage.Reset(); }, TEXT("InvalidDependency.Missing"), TEXT("CloseClipSwap.A1Montage")});
		Cases.Add({TEXT("null A3aMontage"), [](FRPGCloseClipSwapConfig& R) { R.A3aMontage.Reset(); }, TEXT("InvalidDependency.Missing"), TEXT("CloseClipSwap.A3aMontage")});
		Cases.Add({TEXT("null A3bMontage"), [](FRPGCloseClipSwapConfig& R) { R.A3bMontage.Reset(); }, TEXT("InvalidDependency.Missing"), TEXT("CloseClipSwap.A3bMontage")});
		struct FMalformed { const TCHAR* Name; FSoftObjectPath Path; };
		// Exact accepted Bleed malformed-path fixture set, repeated for each reference slot.
		const FMalformed Malformed[] = {
			{TEXT("whitespace package"), MakePath(TEXT("/SyntheticMount/A B"), TEXT("Montage"))},
			{TEXT("control object"), MakePath(TEXT("/SyntheticMount/A"), TEXT("Montage\tX"))},
			{TEXT("subobject"), MakePath(TEXT("/SyntheticMount/A"), TEXT("Montage"), TEXT("Sub"))},
			{TEXT("relative package"), MakePath(TEXT("Relative/A"), TEXT("Montage"))},
			{TEXT("no folder"), MakePath(TEXT("/Root"), TEXT("Montage"))},
			{TEXT("empty mount"), MakePath(TEXT("//Close/A"), TEXT("Montage"))},
			{TEXT("repeated separator"), MakePath(TEXT("/SyntheticMount//A"), TEXT("Montage"))},
			{TEXT("object dot"), MakePath(TEXT("/SyntheticMount/A"), TEXT("Montage.X"))},
			{TEXT("object pipe"), MakePath(TEXT("/SyntheticMount/A"), TEXT("Montage|X"))},
			{TEXT("package pipe"), MakePath(TEXT("/SyntheticMount/A|B"), TEXT("Montage"))},
		};
		for (const FMalformed& M : Malformed)
		{
			const FSoftObjectPath Path = M.Path;
			Cases.Add({FString(M.Name) + TEXT(" A1Montage"), [Path](FRPGCloseClipSwapConfig& R) { R.A1Montage = Montage(Path); }, TEXT("InvalidDependency.Malformed"), TEXT("CloseClipSwap.A1Montage")});
			Cases.Add({FString(M.Name) + TEXT(" A3aMontage"), [Path](FRPGCloseClipSwapConfig& R) { R.A3aMontage = Montage(Path); }, TEXT("InvalidDependency.Malformed"), TEXT("CloseClipSwap.A3aMontage")});
			Cases.Add({FString(M.Name) + TEXT(" A3bMontage"), [Path](FRPGCloseClipSwapConfig& R) { R.A3bMontage = Montage(Path); }, TEXT("InvalidDependency.Malformed"), TEXT("CloseClipSwap.A3bMontage")});
		}
		return Cases;
	}
	bool HasError(const FRPGHydrationResult& R, const TCHAR* Token, const TCHAR* Path)
	{
		return R.Errors.ContainsByPredicate([Token, Path](const FString& E) { return E.Contains(Token) && E.Contains(Path); });
	}
	TStrongObjectPtr<URPGBossDefinition> Definition(const FRPGCloseClipSwapConfig& R)
	{
		TStrongObjectPtr<URPGBossDefinition> D(NewObject<URPGBossDefinition>());
		D->Schema = 1; D->DefinitionId = TEXT("CloseClipSwapFixture"); D->PresentationId = TEXT("FixtureCloseClipSwap");
		D->Stats.MaxHealth = 1234.f; D->Stats.MaxPosture = 87.f;
		D->Stats.PostureRegenDelay = 2.f; D->Stats.PostureRegenRate = 3.f;
		D->CloseClipSwap = R;
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

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCloseClipSwapAssignTest, "OneBossFight.Binding.CloseClipSwap.Assign", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGCloseClipSwapAssignTest::RunTest(const FString& Parameters)
{
	using namespace CloseClipSwapTests;
	FWorldScope Scope;
	AActor* Owner = Scope.Spawn();
	if (!TestNotNull(TEXT("owner"), Owner)) { return false; }
	TStrongObjectPtr<URPGBossCloseClipSwap> CloseClipSwap(NewObject<URPGBossCloseClipSwap>(Owner, TEXT("RPGBossCloseClipSwap")));
	TStrongObjectPtr<URPGBossPosture> Other(NewObject<URPGBossPosture>(Owner));
	const float OtherBefore = Other->PostureMax;
	const auto Before = Owned(Owner);
	const FRuntime Runtime(*CloseClipSwap);
	const FRPGComponentPlan Plan = RPGBossCloseClipSwapAdapters::MakeCloseClipSwapPlan();
	TestTrue(TEXT("exact class/name and five exact paths, without duplicates"), Plan.Class == URPGBossCloseClipSwap::StaticClass()
		&& Plan.InstanceName == FName(TEXT("RPGBossCloseClipSwap")) && Plan.RequiredFields == Paths());
	if (!TestTrue(TEXT("plan callback exists"), static_cast<bool>(Plan.Configure))) { return false; }
	FString Error = TEXT("stale diagnostic");
	TestTrue(TEXT("callback copies all five nondefault fields"), Plan.Configure(*CloseClipSwap, Config(RecordA()), Error) && Error.IsEmpty() && Same(Read(*CloseClipSwap), RecordA()));
	TestTrue(TEXT("runtime, lifecycle, owner component set and unrelated component unchanged"), Runtime.SameAs(FRuntime(*CloseClipSwap))
		&& SameOwned(Before, Owned(Owner)) && Other->PostureMax == OtherBefore && CloseClipSwap->GetOwner() == Owner && CloseClipSwap->GetOuter() == Owner);
	TestTrue(TEXT("second call writes another complete record"), Plan.Configure(*CloseClipSwap, Config(RecordB()), Error) && Same(Read(*CloseClipSwap), RecordB()) && Runtime.SameAs(FRuntime(*CloseClipSwap)));
	AddInfo(TEXT("Five authored fields assigned; no ability, montage load or swap proof."));
	return true;
}



IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCloseClipSwapValidationTest, "OneBossFight.Binding.CloseClipSwap.Validation", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGCloseClipSwapValidationTest::RunTest(const FString& Parameters)
{
	using namespace CloseClipSwapTests;
	FWorldScope Scope;
	AActor* Owner = Scope.Spawn();
	if (!TestNotNull(TEXT("owner"), Owner)) { return false; }
	TStrongObjectPtr<URPGBossCloseClipSwap> CloseClipSwap(NewObject<URPGBossCloseClipSwap>(Owner));
	const auto Before = Read(*CloseClipSwap);
	const FRuntime Runtime(*CloseClipSwap);
	const auto Components = Owned(Owner);
	for (const FBad& Case : BadCases())
	{
		auto R = RecordA();
		Case.Mutate(R);
		FString Error;
		TestFalse(Case.Name + TEXT(": validator refuses"), RPGBossCloseClipSwapAdapters::ValidateCloseClipSwap(R, Error));
		TestTrue(Case.Name + TEXT(": named first token/field"), Error.StartsWith(Case.Token) && Error.Contains(Case.Path));
		TestFalse(Case.Name + TEXT(": callback refuses"), RPGBossCloseClipSwapAdapters::ConfigureCloseClipSwap(*CloseClipSwap, Config(R), Error));
		TestTrue(Case.Name + TEXT(": no partial write"), Same(Read(*CloseClipSwap), Before) && Runtime.SameAs(FRuntime(*CloseClipSwap)) && SameOwned(Components, Owned(Owner)));
	}
	TArray<FRPGCloseClipSwapConfig> Valid{RecordA(), RecordB(), FRPGCloseClipSwapConfig()};
	auto Repeated = RecordA();
	Repeated.A3aMontage = Repeated.A1Montage;
	Repeated.A3bMontage = Repeated.A1Montage;
	Valid.Add(Repeated); // distinct scalar fields, no container self-alias
	for (const auto& R : Valid)
	{
		FString Error = TEXT("stale");
		TestTrue(TEXT("non-suffix names/synthetic paths/repeated replacement/defaults valid"), RPGBossCloseClipSwapAdapters::ValidateCloseClipSwap(R, Error) && Error.IsEmpty()
			&& RPGBossCloseClipSwapAdapters::ConfigureCloseClipSwap(*CloseClipSwap, Config(R), Error) && Same(Read(*CloseClipSwap), R) && Runtime.SameAs(FRuntime(*CloseClipSwap)));
	}
	auto R = RecordA();
	R.CloseAbilityClassName = NAME_None;
	R.AttackMontagesName = NAME_None;
	R.A1Montage.Reset(); R.A3aMontage.Reset(); R.A3bMontage.Reset();
	FString Error;
	TestFalse(TEXT("multi-invalid fails"), RPGBossCloseClipSwapAdapters::ValidateCloseClipSwap(R, Error));
	TestTrue(TEXT("class name first"), Error.StartsWith(TEXT("InvalidDependency.Missing")) && Error.Contains(TEXT("CloseClipSwap.CloseAbilityClassName")));
	R.CloseAbilityClassName = RecordA().CloseAbilityClassName;
	RPGBossCloseClipSwapAdapters::ValidateCloseClipSwap(R, Error);
	TestTrue(TEXT("property name next"), Error.Contains(TEXT("CloseClipSwap.AttackMontagesName")));
	R.AttackMontagesName = RecordA().AttackMontagesName;
	RPGBossCloseClipSwapAdapters::ValidateCloseClipSwap(R, Error);
	TestTrue(TEXT("A1 before A3a/A3b"), Error.Contains(TEXT("CloseClipSwap.A1Montage")));
	R.A1Montage = RecordA().A1Montage;
	RPGBossCloseClipSwapAdapters::ValidateCloseClipSwap(R, Error);
	TestTrue(TEXT("A3a before A3b"), Error.Contains(TEXT("CloseClipSwap.A3aMontage")));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCloseClipSwapIsolationTest, "OneBossFight.Binding.CloseClipSwap.Isolation", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGCloseClipSwapIsolationTest::RunTest(const FString& Parameters)
{
	using namespace CloseClipSwapTests;
	FWorldScope Scope;
	AActor* OwnerA = Scope.Spawn(); AActor* OwnerB = Scope.Spawn();
	if (!TestTrue(TEXT("two owners"), OwnerA && OwnerB)) { return false; }
	TStrongObjectPtr<URPGBossCloseClipSwap> A(NewObject<URPGBossCloseClipSwap>(OwnerA));
	TStrongObjectPtr<URPGBossCloseClipSwap> B(NewObject<URPGBossCloseClipSwap>(OwnerB));
	TStrongObjectPtr<URPGBossCloseClipSwap> Untouched(NewObject<URPGBossCloseClipSwap>(OwnerB));
	TStrongObjectPtr<URPGBossBleed> Other(NewObject<URPGBossBleed>(OwnerA));
	const auto Original = Read(*Untouched); const auto Default = Read(*GetDefault<URPGBossCloseClipSwap>());
	const FRuntime RuntimeA(*A), RuntimeB(*B);
	const auto OwnedA = Owned(OwnerA), OwnedB = Owned(OwnerB);
	const float BleedBefore = Other->InitialThreshold;
	auto Input = Config(RecordA()); FString Error;
	TestTrue(TEXT("A assignment"), RPGBossCloseClipSwapAdapters::ConfigureCloseClipSwap(*A, Input, Error));
	Input.CloseClipSwap.A1Montage = Montage(MakePath(TEXT("/SyntheticMount/Changed"), TEXT("Montage")));
	TestTrue(TEXT("native soft reference owns independent value"), Same(Read(*A), RecordA()));
	Input.CloseClipSwap = RecordB();
	TestTrue(TEXT("input is a value snapshot"), Same(Read(*A), RecordA()));
	TestTrue(TEXT("B assignment"), RPGBossCloseClipSwapAdapters::ConfigureCloseClipSwap(*B, Input, Error));
	auto Invalid = RecordB(); Invalid.A3bMontage.Reset();
	TestFalse(TEXT("late invalid input refuses on configured A"), RPGBossCloseClipSwapAdapters::ConfigureCloseClipSwap(*A, Config(Invalid), Error));
	TestTrue(TEXT("owners and unrelated values fully isolated"), Same(Read(*A), RecordA()) && Same(Read(*B), RecordB())
		&& Same(Read(*Untouched), Original) && Same(Read(*GetDefault<URPGBossCloseClipSwap>()), Default)
		&& RuntimeA.SameAs(FRuntime(*A)) && RuntimeB.SameAs(FRuntime(*B))
		&& SameOwned(OwnedA, Owned(OwnerA)) && SameOwned(OwnedB, Owned(OwnerB)) && Other->InitialThreshold == BleedBefore);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCloseClipSwapRejectionsTest, "OneBossFight.Binding.CloseClipSwap.Rejections", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGCloseClipSwapRejectionsTest::RunTest(const FString& Parameters)
{
	using namespace CloseClipSwapTests;
	FWorldScope Scope;
	AActor* Owner = Scope.Spawn();
	if (!TestNotNull(TEXT("owner"), Owner)) { return false; }
	auto Check = [this](UActorComponent& C, const TCHAR* Token)
	{
		const bool Registered = C.IsRegistered(), Begun = C.HasBegunPlay();
		const URPGBossCloseClipSwap* CloseClipSwap = Cast<URPGBossCloseClipSwap>(&C);
		const auto Before = CloseClipSwap ? Read(*CloseClipSwap) : FRPGCloseClipSwapConfig();
		FString Error;
		auto Bad = RecordA(); Bad.A1Montage.Reset();
		for (const auto& R : TArray<FRPGCloseClipSwapConfig>{RecordA(), Bad})
		{
			TestFalse(TEXT("lifecycle/class rejection"), RPGBossCloseClipSwapAdapters::ConfigureCloseClipSwap(C, Config(R), Error));
			TestTrue(TEXT("lifecycle before invalid record; no lifecycle write"), Error.StartsWith(Token) && C.IsRegistered() == Registered && C.HasBegunPlay() == Begun);
			if (CloseClipSwap) { TestTrue(TEXT("no partial configuration write on lifecycle refusal"), Same(Read(*CloseClipSwap), Before)); }
		}
	};
	TStrongObjectPtr<USceneComponent> Wrong(NewObject<USceneComponent>(Owner));
	Check(*Wrong, TEXT("WrongComponentClass"));
	TStrongObjectPtr<URPGBossBleed> WrongNative(NewObject<URPGBossBleed>(Owner));
	Check(*WrongNative, TEXT("WrongComponentClass"));
	TStrongObjectPtr<URPGBossCloseClipSwap> Registered(NewObject<URPGBossCloseClipSwap>(Owner));
	Registered->RegisterComponent();
	if (!TestTrue(TEXT("fixture registered but not begun"), Registered->IsRegistered() && !Registered->HasBegunPlay())) { return false; }
	Check(*Registered, TEXT("ComponentAlreadyRegistered"));
	AActor* LateOwner = Scope.Spawn();
	if (!TestNotNull(TEXT("late owner"), LateOwner)) { return false; }
	LateOwner->DispatchBeginPlay(); // plain actor, NO CloseClipSwap component yet
	if (!TestTrue(TEXT("plain owner began"), LateOwner->HasActorBegunPlay())) { return false; }
	TStrongObjectPtr<URPGBossCloseClipSwap> Late(NewObject<URPGBossCloseClipSwap>(LateOwner));
	Check(*Late, TEXT("OwnerBegunPlay"));
	TStrongObjectPtr<URPGBossCloseClipSwap> Orphan(NewObject<URPGBossCloseClipSwap>(GetTransientPackage()));
	Check(*Orphan, TEXT("InvalidOwner"));
	TStrongObjectPtr<URPGBossCloseClipSwap> Destroyed(NewObject<URPGBossCloseClipSwap>(Owner));
	Destroyed->DestroyComponent();
	Check(*Destroyed, TEXT("InvalidComponent")); // retained object, not freed memory
	AddInfo(TEXT("ComponentBegunPlay guard source-only: no CloseClipSwap BeginPlay invoked. Registered and plain begun-owner fixtures do not swap a montage."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCloseClipSwapCompileTest, "OneBossFight.Binding.CloseClipSwap.Compile", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGCloseClipSwapCompileTest::RunTest(const FString& Parameters)
{
	using namespace CloseClipSwapTests;
	const auto Content = RPGCombatRegistry::Legacy(); // accepted dev-only synthetic contract
	if (!TestTrue(TEXT("synthetic content lease exists"), Content.IsValid())) { return false; }
	TSharedPtr<const FRPGParticipantConfig> Out;
	auto D = Definition(RecordA());
	auto Compile = [&Content](const URPGBossDefinition& Def, TSharedPtr<const FRPGParticipantConfig>& Output)
	{
		return RPGCombatHydration::CompileSyntheticParticipant(Def, Content, FString::ChrN(64, TEXT('b')), Output);
	};
	if (!TestTrue(TEXT("synthetic compiler positive control"), Compile(*D, Out).IsReady() && Out.IsValid())) { return false; }
	TestTrue(TEXT("all five typed values copied, dev-only flag, same epoch; manifest Value not parsed"), Same(Out->CloseClipSwap, RecordA()) && Out->bSyntheticFixture && Out->Content.Get() == Content.Get());
	D->CloseClipSwap = RecordB();
	TestTrue(TEXT("compiled config is immutable value snapshot"), Same(Out->CloseClipSwap, RecordA()));
	TestTrue(TEXT("next compile copies independent record"),Compile(*D,Out).IsReady()&&Out.IsValid()&&Same(Out->CloseClipSwap,RecordB()));
	D->CloseClipSwap.A1Montage = Montage(MakePath(TEXT("/SyntheticMount/Changed"), TEXT("Montage")));
	TestTrue(TEXT("compiled soft reference owns an independent value"),Out.IsValid()&&Same(Out->CloseClipSwap,RecordB()));
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
	auto Defaults = Definition(FRPGCloseClipSwapConfig());
	TestTrue(TEXT("additive defaults compile without substitution"), Compile(*Defaults, Out).IsReady() && Out.IsValid() && Same(Out->CloseClipSwap, FRPGCloseClipSwapConfig()));
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
	AddInfo(TEXT("Synthetic compiler/copy and early production refusal only; no positive real-asset compile or ability/montage resolution."));
	return true;
}



IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCloseClipSwapAuthoringTest, "OneBossFight.Binding.CloseClipSwap.Authoring", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGCloseClipSwapAuthoringTest::RunTest(const FString& Parameters)
{
	using namespace CloseClipSwapTests;
	const UScriptStruct* Struct = FRPGCloseClipSwapConfig::StaticStruct();
	int32 Count = 0;
	for (TFieldIterator<FProperty> It(Struct); It; ++It) { ++Count; TestTrue(TEXT("editable"), It->HasAnyPropertyFlags(CPF_Edit)); }
	TestEqual(TEXT("five fields"), Count, 5);
	for (const TCHAR* N : {TEXT("CloseAbilityClassName"), TEXT("AttackMontagesName")})
	{
		TestNotNull(N, CastField<FNameProperty>(Struct->FindPropertyByName(N)));
	}
	for (const TCHAR* N : {TEXT("A1Montage"), TEXT("A3aMontage"), TEXT("A3bMontage")})
	{
		const FSoftObjectProperty* Property = CastField<FSoftObjectProperty>(Struct->FindPropertyByName(N));
		TestTrue(FString(N) + TEXT(" soft montage"), Property && Property->PropertyClass == UAnimMontage::StaticClass());
	}
	const FStructProperty* Property = CastField<FStructProperty>(URPGBossDefinition::StaticClass()->FindPropertyByName(TEXT("CloseClipSwap")));
	TestTrue(TEXT("Data Asset record"), Property && Property->Struct == Struct && Property->HasAnyPropertyFlags(CPF_Edit));
	const FRPGCloseClipSwapConfig Default;
	TestTrue(TEXT("all defaults match native constructor"), Same(Default, Read(*GetDefault<URPGBossCloseClipSwap>())));
	TestTrue(TEXT("default names and montage suffixes"), Default.CloseAbilityClassName == FName(TEXT("GA_GS_Boss_CloseAttack_C")) && Default.AttackMontagesName == FName(TEXT("AttackMontages"))
		&& Default.A1Montage.ToString().EndsWith(TEXT("/Animations/AM_Boss01_A1.AM_Boss01_A1"))
		&& Default.A3aMontage.ToString().EndsWith(TEXT("/Animations/AM_Boss01_A3a.AM_Boss01_A3a"))
		&& Default.A3bMontage.ToString().EndsWith(TEXT("/Animations/AM_Boss01_A3b.AM_Boss01_A3b")));
	for (const TCHAR* N : {TEXT("LoadedA1"), TEXT("LoadedA3a"), TEXT("LoadedA3b"), TEXT("SwappedAbility"), TEXT("Swaps"), TEXT("RetrySeconds"), TEXT("ApplyCount"), TEXT("RestoreCount"), TEXT("bApplied"), TEXT("bEnabledForTest"), TEXT("bPermanentFailure")})
	{
		TestNull(FString(N) + TEXT(" not authored"), Struct->FindPropertyByName(N));
	}
	AddInfo(TEXT("Declaration/reflection only. No live ability, load, swap or serialized/Details proof."));
	return true;
}
#endif
