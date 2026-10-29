// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Animation/AnimSequence.h"
#include "Components/SceneComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"
#include "Player/RPGBossDormantWake.h"
#include "Player/RPGBossDormantWakeAdapters.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossPosture.h"
#include "UObject/Class.h"
#include "UObject/Package.h"
#include "UObject/SoftObjectPath.h"
#include "UObject/StrongObjectPtr.h"
#include "UObject/UnrealType.h"

// These tests prove the typed dormant and wake clip references: the reflected record and its authoring defaults, its copy into the immutable config by the real definition compiler (synthetic path, and the
// production path's early rejection), the shared validator, and the typed, lifecycle-safe assignment of exactly two private soft references on an isolated native component through the friend function.
// They do NOT prove a serialized asset value, anything seen in the Details panel, a production compile with a real skeleton, that either path names an existing, cooked or correctly typed asset, that a clip fits
// the skeleton or the timing, a real dormant loop or wake, or any wiring. The two private native properties are only READ (and, for one begun-play fixture, cleared) through typed reflection by the tests
// themselves; the adapter under test uses no reflection. The one BeginPlay that runs (the begun-component guard) loads nothing: the native BeginPlay only calls LoadSynchronous on the two soft references,
// which the fixture clears first, and the fixture owner is a plain actor (no encounter, no character), so no playback, tick or encounter lookup does anything.

namespace
{
namespace DormantWakeTests
{
	using FEpochPtr = TSharedPtr<const RPGCombatRegistry::FEpoch>;
	using FConfigPtr = TSharedPtr<const FRPGParticipantConfig>;

	/** Test-local game world with the set-up the earlier headless tests used; destroyed with the scope. */
	struct FDormantWakeTestWorld
	{
		UWorld* World = nullptr;

		FDormantWakeTestWorld()
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

		~FDormantWakeTestWorld()
		{
			if (World)
			{
				GEngine->DestroyWorldContext(World);
				World->DestroyWorld(/*bInformEngineOfWorld=*/false);
			}
		}

		FDormantWakeTestWorld(const FDormantWakeTestWorld&) = delete;
		FDormantWakeTestWorld& operator=(const FDormantWakeTestWorld&) = delete;

		AActor* SpawnOwner() const { return World ? World->SpawnActor<AActor>() : nullptr; }
	};

	/** A soft path built from its parts, so that deliberately malformed forms are never parsed from text (no engine log, no repair). */
	FSoftObjectPath MakePath(const TCHAR* Package, const TCHAR* Asset, const TCHAR* Sub = TEXT(""))
	{
		return FSoftObjectPath(FTopLevelAssetPath(FName(Package), FName(Asset)), FString(Sub));
	}

	TSoftObjectPtr<UAnimSequence> SequencePtr(const FSoftObjectPath& Path) { return TSoftObjectPtr<UAnimSequence>(Path); }

	/** The native reference is private: the TEST reads it through typed reflection (the adapter under test does not use reflection). Returns false when the property is not the expected soft object property. */
	bool ReadClip(const URPGBossDormantWake& Component, const TCHAR* Name, FSoftObjectPath& Out)
	{
		const FSoftObjectProperty* Property = CastField<FSoftObjectProperty>(URPGBossDormantWake::StaticClass()->FindPropertyByName(Name));
		if (!Property)
		{
			return false;
		}
		Out = Property->ContainerPtrToValuePtr<FSoftObjectPtr>(&Component)->ToSoftObjectPath();
		return true;
	}

	/** Test-only fixture helper: writes (or clears, with a null path) the private soft reference through typed reflection. Never used by the adapter. */
	bool WriteClip(URPGBossDormantWake& Component, const TCHAR* Name, const FSoftObjectPath& Path)
	{
		const FSoftObjectProperty* Property = CastField<FSoftObjectProperty>(URPGBossDormantWake::StaticClass()->FindPropertyByName(Name));
		if (!Property)
		{
			return false;
		}
		*Property->ContainerPtrToValuePtr<FSoftObjectPtr>(&Component) = Path.IsNull() ? FSoftObjectPtr() : FSoftObjectPtr(Path);
		return true;
	}

	/** Both references and the public runtime state of the component, with an exact comparison. */
	struct FDormantWakeState
	{
		FSoftObjectPath DormantClip;
		FSoftObjectPath WakeClip;
		bool bReadable = false;
		bool bWaking;
		FString StageName;
		int32 DormantPlayCount, WakePlayCount;

		explicit FDormantWakeState(const URPGBossDormantWake& C)
			: bWaking(C.IsWaking()), StageName(C.GetStageName()), DormantPlayCount(C.GetDormantPlayCount()), WakePlayCount(C.GetWakePlayCount())
		{
			bReadable = ReadClip(C, TEXT("DormantClip"), DormantClip) && ReadClip(C, TEXT("WakeClip"), WakeClip);
		}

		bool RuntimeEquals(const FDormantWakeState& O) const
		{
			return bWaking == O.bWaking && StageName.Equals(O.StageName, ESearchCase::CaseSensitive) && DormantPlayCount == O.DormantPlayCount && WakePlayCount == O.WakePlayCount;
		}

		bool operator==(const FDormantWakeState& O) const { return DormantClip == O.DormantClip && WakeClip == O.WakeClip && RuntimeEquals(O); }
	};

	FRPGParticipantConfig ConfigA()
	{
		FRPGParticipantConfig C;
		C.DormantWake.DormantClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Dormant/Custom"), TEXT("AN_TestDormant")));
		C.DormantWake.WakeClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Wake/Custom"), TEXT("AN_TestWake")));
		return C;
	}

	FRPGParticipantConfig ConfigB()
	{
		FRPGParticipantConfig C;
		C.DormantWake.DormantClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Other/Dormant"), TEXT("AN_OtherDormant")));
		C.DormantWake.WakeClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Other/Wake"), TEXT("AN_OtherWake")));
		return C;
	}

	/** A distinct starting state, different from both configs and from the native defaults. */
	void ArmDistinctStart(URPGBossDormantWake& C)
	{
		WriteClip(C, TEXT("DormantClip"), MakePath(TEXT("/SyntheticMount/Start/Dormant"), TEXT("AN_StartDormant")));
		WriteClip(C, TEXT("WakeClip"), MakePath(TEXT("/SyntheticMount/Start/Wake"), TEXT("AN_StartWake")));
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

	/** A valid definition for the real synthetic compiler with the given dormant wake record (every other record is the authoring default or a valid fixture value). */
	TStrongObjectPtr<URPGBossDefinition> MakeDefinition(const FRPGDormantWakeConfig& DormantWake)
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
		Definition->DormantWake = DormantWake;
		Definition->Fields.Add(MakeField(RPGBossDormantWakeAdapters::FieldDormantClip, TEXT("synthetic")));
		Definition->Fields.Add(MakeField(RPGBossDormantWakeAdapters::FieldWakeClip, TEXT("synthetic")));
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

	TStrongObjectPtr<URPGBossDormantWake> NewDormantWake(AActor* Owner, const TCHAR* Name)
	{
		return TStrongObjectPtr<URPGBossDormantWake>(NewObject<URPGBossDormantWake>(Owner, Name));
	}
}
}

// No file-scope using-directive on purpose: each test body names its namespace itself.

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGDormantWakeAssignTest, "OneBossFight.Binding.DormantWake.Assign",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGDormantWakeAssignTest::RunTest(const FString& Parameters)
{
	using namespace DormantWakeTests;
	FDormantWakeTestWorld Scope;
	if (!TestNotNull(TEXT("test world"), Scope.World))
	{
		return false;
	}
	AActor* Owner = Scope.SpawnOwner();
	if (!TestNotNull(TEXT("owner actor"), Owner))
	{
		return false;
	}
	TStrongObjectPtr<URPGBossDormantWake> Component = NewDormantWake(Owner, TEXT("RPGBossDormantWake"));
	if (!TestTrue(TEXT("component created"), Component.IsValid()))
	{
		return false;
	}
	ArmDistinctStart(*Component);
	const FDormantWakeState Before(*Component);
	if (!TestTrue(TEXT("precondition: the private references are readable through typed reflection and hold the distinct start values"), Before.bReadable && !Before.DormantClip.IsNull() && !Before.WakeClip.IsNull()))
	{
		return false;
	}

	// Measurement boundary: NewDormantWake already added the component to its outer actor, so the owner's component set (identity and count) is captured AFTER the fixture and immediately BEFORE each configure call.
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

	// The unwired plan fragment: the legacy instance name, the exact class and the two typed paths in field order.
	const FRPGComponentPlan Plan = RPGBossDormantWakeAdapters::MakeDormantWakePlan();
	TestTrue(TEXT("plan class"), Plan.Class == URPGBossDormantWake::StaticClass());
	TestTrue(TEXT("plan instance name is the legacy attachment name"), Plan.InstanceName == FName(TEXT("RPGBossDormantWake")));
	TestTrue(TEXT("plan required fields are the two typed paths in order"), Plan.RequiredFields == TArray<FString>{TEXT("DormantWake.DormantClip"), TEXT("DormantWake.WakeClip")});
	if (!TestTrue(TEXT("plan callback is set"), static_cast<bool>(Plan.Configure)))
	{
		return false;
	}

	// Config A through the plan callback, with manifest Value text that says something else: only the typed record counts.
	FRPGParticipantConfig Config = ConfigA();
	Config.Fields.Add(MakeField(RPGBossDormantWakeAdapters::FieldDormantClip, TEXT("/SyntheticMount/FromTheManifest/Dormant.AN_Manifest")));
	Config.Fields.Add(MakeField(RPGBossDormantWakeAdapters::FieldWakeClip, TEXT("9999")));
	FString Error = TEXT("a stale diagnostic from an earlier call");
	const TSet<const UActorComponent*> OwnedBeforeA = CaptureOwned();
	TestTrue(TEXT("fixture: the component is already in the owner's component set before the callback"), OwnedBeforeA.Contains(Component.Get()));
	TestTrue(TEXT("callback succeeds"), Plan.Configure(*Component, Config, Error));
	TestTrue(TEXT("callback created no component: the owner's component set (identity and count) is unchanged by it"), SameOwned(OwnedBeforeA, CaptureOwned()));
	TestTrue(TEXT("the diagnostic was cleared on success"), Error.IsEmpty());
	const FDormantWakeState After(*Component);
	TestTrue(TEXT("both private references are the typed record, not the manifest text"), After.bReadable && After.DormantClip == Config.DormantWake.DormantClip.ToSoftObjectPath() && After.WakeClip == Config.DormantWake.WakeClip.ToSoftObjectPath());
	TestFalse(TEXT("both references differ from the distinct start state"), After.DormantClip == Before.DormantClip || After.WakeClip == Before.WakeClip);
	TestTrue(TEXT("the runtime state is unchanged (waking, stage, play counts)"), After.RuntimeEquals(Before));
	TestFalse(TEXT("component stays unregistered"), Component->IsRegistered());
	TestFalse(TEXT("component did not begin play"), Component->HasBegunPlay());
	TestFalse(TEXT("owner did not begin play"), Owner->HasActorBegunPlay());

	// Config B directly: a second record, again with no component created.
	const FRPGParticipantConfig B = ConfigB();
	const TSet<const UActorComponent*> OwnedBeforeB = CaptureOwned();
	TestTrue(TEXT("config B succeeds"), RPGBossDormantWakeAdapters::ConfigureDormantWake(*Component, B, Error) && Error.IsEmpty());
	TestTrue(TEXT("direct config B created no component: the owner's component set (identity and count) is unchanged by it"), SameOwned(OwnedBeforeB, CaptureOwned()));
	const FDormantWakeState AfterB(*Component);
	TestTrue(TEXT("B: both references assigned"), AfterB.DormantClip == B.DormantWake.DormantClip.ToSoftObjectPath() && AfterB.WakeClip == B.DormantWake.WakeClip.ToSoftObjectPath() && AfterB.RuntimeEquals(Before));

	// No load: assigning the REAL native default paths loads no object and creates no package. The witness is presence before and after (ResolveObject, FindPackage): an asset already in memory proves nothing for
	// its own path (stated limitation), but no path may gain an object or a package from the assignment. Nothing is loaded, unloaded or registered here.
	{
		AActor* WitnessOwner = Scope.SpawnOwner();
		if (!TestNotNull(TEXT("no-load witness: owner actor"), WitnessOwner))
		{
			return false;
		}
		TStrongObjectPtr<URPGBossDormantWake> Witness = NewDormantWake(WitnessOwner, TEXT("WitnessDormantWake"));
		if (!TestTrue(TEXT("no-load witness: component created"), Witness.IsValid()))
		{
			return false;
		}
		ArmDistinctStart(*Witness);
		const FRPGParticipantConfig WitnessConfig; // the authoring defaults: the real native default paths
		const FSoftObjectPath WitnessPaths[] = {WitnessConfig.DormantWake.DormantClip.ToSoftObjectPath(), WitnessConfig.DormantWake.WakeClip.ToSoftObjectPath()};
		bool ObjectPresentBefore[2];
		bool PackagePresentBefore[2];
		bool bAllPathsSet = true;
		for (int32 PathIndex = 0; PathIndex < 2; ++PathIndex)
		{
			bAllPathsSet = bAllPathsSet && !WitnessPaths[PathIndex].IsNull();
			ObjectPresentBefore[PathIndex] = WitnessPaths[PathIndex].ResolveObject() != nullptr;
			PackagePresentBefore[PathIndex] = FindPackage(nullptr, *WitnessPaths[PathIndex].GetLongPackageName()) != nullptr;
		}
		TestTrue(TEXT("no-load witness: the two native default references are set"), bAllPathsSet);
		FString WitnessError;
		TestTrue(TEXT("no-load witness: the native default record is accepted"), RPGBossDormantWakeAdapters::ConfigureDormantWake(*Witness, WitnessConfig, WitnessError) && WitnessError.IsEmpty());
		bool bNothingAppeared = true;
		for (int32 PathIndex = 0; PathIndex < 2; ++PathIndex)
		{
			bNothingAppeared = bNothingAppeared && ((WitnessPaths[PathIndex].ResolveObject() != nullptr) == ObjectPresentBefore[PathIndex])
				&& ((FindPackage(nullptr, *WitnessPaths[PathIndex].GetLongPackageName()) != nullptr) == PackagePresentBefore[PathIndex]);
		}
		TestTrue(TEXT("no-load witness: neither an object nor a package of the referenced assets appeared during the assignment"), bNothingAppeared);
		const FDormantWakeState WitnessState(*Witness);
		TestTrue(TEXT("no-load witness: the references were assigned as paths"), WitnessState.DormantClip == WitnessPaths[0] && WitnessState.WakeClip == WitnessPaths[1]);
	}

	AddInfo(TEXT("Typed assignment of two private soft references through the friend function only; NOT a dormant loop or wake, NOT asset existence, type or cooking, NOT a serialized asset value."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGDormantWakeValidationTest, "OneBossFight.Binding.DormantWake.Validation",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGDormantWakeValidationTest::RunTest(const FString& Parameters)
{
	using namespace DormantWakeTests;
	FDormantWakeTestWorld Scope;
	if (!TestNotNull(TEXT("test world"), Scope.World))
	{
		return false;
	}
	AActor* Owner = Scope.SpawnOwner();
	if (!TestNotNull(TEXT("owner actor"), Owner))
	{
		return false;
	}
	TStrongObjectPtr<URPGBossDormantWake> Component = NewDormantWake(Owner, TEXT("RPGBossDormantWake"));
	if (!TestTrue(TEXT("component created"), Component.IsValid()))
	{
		return false;
	}
	ArmDistinctStart(*Component);
	const FDormantWakeState Before(*Component);
	if (!TestTrue(TEXT("precondition: both private references readable"), Before.bReadable))
	{
		return false;
	}

	// One whole-record check: the validator and the assignment both refuse (or accept) with the same token and field path, and a refusal writes NOTHING (both references and the runtime state equal the start state).
	auto Check = [&](const FString& Label, const FRPGParticipantConfig& Config, const TCHAR* ExpectedToken, const FString& ExpectedPath)
	{
		FString Error = TEXT("a stale diagnostic");
		const bool bOk = RPGBossDormantWakeAdapters::ValidateDormantWake(Config.DormantWake, Error);
		if (!ExpectedToken)
		{
			TestTrue(FString::Printf(TEXT("%s: valid, and the diagnostic was cleared"), *Label), bOk && Error.IsEmpty());
			return;
		}
		TestFalse(FString::Printf(TEXT("%s: rejected"), *Label), bOk);
		TestTrue(FString::Printf(TEXT("%s: named %s (got '%s')"), *Label, ExpectedToken, *Error), Error.StartsWith(ExpectedToken));
		TestTrue(FString::Printf(TEXT("%s: names the field %s"), *Label, *ExpectedPath), Error.Contains(ExpectedPath));
		FString ConfigureError = TEXT("a stale diagnostic");
		TestFalse(FString::Printf(TEXT("%s: the assignment refuses"), *Label), RPGBossDormantWakeAdapters::ConfigureDormantWake(*Component, Config, ConfigureError));
		TestTrue(FString::Printf(TEXT("%s: the assignment names the same token"), *Label), ConfigureError.StartsWith(ExpectedToken));
		TestTrue(FString::Printf(TEXT("%s: no write at all (both references and state)"), *Label), FDormantWakeState(*Component) == Before);
	};
	const FString DormantPath = RPGBossDormantWakeAdapters::FieldDormantClip;
	const FString WakePath = RPGBossDormantWakeAdapters::FieldWakeClip;
	auto WithDormant = [](const FSoftObjectPath& Path) { FRPGParticipantConfig C = ConfigA(); C.DormantWake.DormantClip = SequencePtr(Path); return C; };
	auto WithWake = [](const FSoftObjectPath& Path) { FRPGParticipantConfig C = ConfigA(); C.DormantWake.WakeClip = SequencePtr(Path); return C; };

	Check(TEXT("config A"), ConfigA(), nullptr, FString());
	Check(TEXT("config B"), ConfigB(), nullptr, FString());
	{
		const FRPGParticipantConfig Defaults; // the authoring defaults of the record
		Check(TEXT("the authoring defaults"), Defaults, nullptr, FString());
	}

	// Missing: null, for each field.
	Check(TEXT("dormant clip null"), WithDormant(FSoftObjectPath()), TEXT("InvalidDependency.Missing"), DormantPath);
	Check(TEXT("wake clip null"), WithWake(FSoftObjectPath()), TEXT("InvalidDependency.Missing"), WakePath);

	// Malformed forms, for each field, built from parts (never parsed from text).
	struct FMalformed
	{
		const TCHAR* Name;
		FSoftObjectPath Path;
	};
	const FMalformed Malformed[] = {
		{TEXT("whitespace in the package"), MakePath(TEXT("/SyntheticMount/A B"), TEXT("AN_X"))},
		{TEXT("a control character in the asset"), MakePath(TEXT("/SyntheticMount/A"), TEXT("AN\tX"))},
		{TEXT("a sub-object"), MakePath(TEXT("/SyntheticMount/A"), TEXT("AN_X"), TEXT("Sub"))},
		{TEXT("no leading slash"), MakePath(TEXT("Relative/A"), TEXT("AN_X"))},
		{TEXT("no package folder"), MakePath(TEXT("/Root"), TEXT("AN_X"))},
	};
	for (const FMalformed& Case : Malformed)
	{
		Check(FString::Printf(TEXT("dormant clip with %s"), Case.Name), WithDormant(Case.Path), TEXT("InvalidDependency.Malformed"), DormantPath);
		Check(FString::Printf(TEXT("wake clip with %s"), Case.Name), WithWake(Case.Path), TEXT("InvalidDependency.Malformed"), WakePath);
	}

	// Structure only: well-formed paths of assets that exist nowhere are valid (no registry query, no load); a native class path is not an animation but nothing here checks the type.
	Check(TEXT("well-formed paths of assets that exist nowhere (valid: structure only)"), [] { FRPGParticipantConfig C = ConfigA();
		C.DormantWake.DormantClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Nowhere/At/All"), TEXT("AN_Nope")));
		C.DormantWake.WakeClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Nowhere/Wake"), TEXT("AN_Nope")));
		return C; }(), nullptr, FString());

	// Whole-record no partial write: the FIRST field invalid while the LAST is valid and non-default, and the LAST invalid while the FIRST is valid and non-default.
	Check(TEXT("only the FIRST field invalid, the wake clip valid and non-default"), WithDormant(MakePath(TEXT("/SyntheticMount/A B"), TEXT("AN_X"))), TEXT("InvalidDependency.Malformed"), DormantPath);
	Check(TEXT("only the LAST field invalid, the dormant clip valid and non-default"), WithWake(MakePath(TEXT("/SyntheticMount/A"), TEXT("AN_X"), TEXT("Sub"))), TEXT("InvalidDependency.Malformed"), WakePath);

	// Precedence: the dormant clip is reported first, whatever is wrong with the wake clip.
	{
		FRPGParticipantConfig C = ConfigA();
		C.DormantWake.DormantClip = SequencePtr(FSoftObjectPath());
		C.DormantWake.WakeClip = SequencePtr(MakePath(TEXT("/SyntheticMount/A B"), TEXT("AN_X")));
		Check(TEXT("dormant clip null and wake clip malformed: the dormant clip is reported first"), C, TEXT("InvalidDependency.Missing"), DormantPath);
		FRPGParticipantConfig Both = ConfigA();
		Both.DormantWake.DormantClip = SequencePtr(MakePath(TEXT("/SyntheticMount/A B"), TEXT("AN_X")));
		Both.DormantWake.WakeClip = SequencePtr(FSoftObjectPath());
		Check(TEXT("dormant clip malformed and wake clip null: the dormant clip is reported first"), Both, TEXT("InvalidDependency.Malformed"), DormantPath);
	}

	// The component refused every record above and is still configurable.
	FString Error;
	TestTrue(TEXT("after all refusals a valid record still configures"), RPGBossDormantWakeAdapters::ConfigureDormantWake(*Component, ConfigA(), Error)
		&& FDormantWakeState(*Component).DormantClip == ConfigA().DormantWake.DormantClip.ToSoftObjectPath());
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGDormantWakeIsolationTest, "OneBossFight.Binding.DormantWake.Isolation",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGDormantWakeIsolationTest::RunTest(const FString& Parameters)
{
	using namespace DormantWakeTests;
	FDormantWakeTestWorld Scope;
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
	TStrongObjectPtr<URPGBossDormantWake> A = NewDormantWake(OwnerA, TEXT("RPGBossDormantWake"));
	TStrongObjectPtr<URPGBossDormantWake> B = NewDormantWake(OwnerB, TEXT("RPGBossDormantWake"));
	TStrongObjectPtr<URPGBossDormantWake> C = NewDormantWake(OwnerC, TEXT("RPGBossDormantWake"));
	if (!TestTrue(TEXT("three components"), A.IsValid() && B.IsValid() && C.IsValid()))
	{
		return false;
	}
	const FDormantWakeState UntouchedC(*C);
	FRPGParticipantConfig ConfigForA = ConfigA();
	const FRPGParticipantConfig ConfigForB = ConfigB();
	FString Error;
	TestTrue(TEXT("A"), RPGBossDormantWakeAdapters::ConfigureDormantWake(*A, ConfigForA, Error));
	const FDormantWakeState SnapshotA(*A);
	TestTrue(TEXT("B"), RPGBossDormantWakeAdapters::ConfigureDormantWake(*B, ConfigForB, Error));
	TestTrue(TEXT("configuring B did not change A"), FDormantWakeState(*A) == SnapshotA);
	TestFalse(TEXT("B really differs from A"), FDormantWakeState(*B).DormantClip == SnapshotA.DormantClip || FDormantWakeState(*B).WakeClip == SnapshotA.WakeClip);

	// The assignment copies values: changing the config afterwards changes nothing.
	ConfigForA.DormantWake.DormantClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Changed"), TEXT("AN_Afterwards")));
	ConfigForA.DormantWake.WakeClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Changed"), TEXT("AN_Afterwards2")));
	TestTrue(TEXT("a later config change does not reach A"), FDormantWakeState(*A) == SnapshotA);

	// A refused call leaves an otherwise configured component alone (no partial write, no state change).
	FRPGParticipantConfig Refused = ConfigB();
	Refused.DormantWake.WakeClip = SequencePtr(FSoftObjectPath());
	TestFalse(TEXT("a refused record is refused"), RPGBossDormantWakeAdapters::ConfigureDormantWake(*A, Refused, Error));
	TestTrue(TEXT("and leaves A exactly as it was"), FDormantWakeState(*A) == SnapshotA);

	// A component that was never configured keeps the native values, and so does the class default object.
	TestTrue(TEXT("untouched component unchanged"), FDormantWakeState(*C) == UntouchedC);
	TestTrue(TEXT("CDO is a component of the same native values as the untouched one"), FDormantWakeState(*GetDefault<URPGBossDormantWake>()) == UntouchedC);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGDormantWakeRejectionsTest, "OneBossFight.Binding.DormantWake.Rejections",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGDormantWakeRejectionsTest::RunTest(const FString& Parameters)
{
	using namespace DormantWakeTests;
	FDormantWakeTestWorld Scope;
	if (!TestNotNull(TEXT("test world"), Scope.World))
	{
		return false;
	}
	const FRPGParticipantConfig Config = ConfigA(); // valid: every failure below is about the component or the owner
	FString Error;

	// A rejected call changes nothing and names the reason. Wrong-class targets are concrete classes (UActorComponent itself is abstract).
	auto ExpectRejected = [&](const TCHAR* Label, UActorComponent& Component, const TCHAR* Token)
	{
		const URPGBossDormantWake* AsDormantWake = Cast<URPGBossDormantWake>(&Component);
		const URPGBossEncounter* AsEncounter = Cast<URPGBossEncounter>(&Component);
		const URPGBossPosture* AsPosture = Cast<URPGBossPosture>(&Component);
		TOptional<FDormantWakeState> Before;
		if (AsDormantWake) { Before.Emplace(*AsDormantWake); }
		const float EncounterGateBefore = AsEncounter ? AsEncounter->GateRadius : 0.f;
		const float PostureMaxBefore = AsPosture ? AsPosture->PostureMax : 0.f;
		const bool bOk = RPGBossDormantWakeAdapters::ConfigureDormantWake(Component, Config, Error);
		TestFalse(FString::Printf(TEXT("%s: rejected"), Label), bOk);
		TestTrue(FString::Printf(TEXT("%s: named %s (got '%s')"), Label, Token, *Error), Error.StartsWith(Token));
		if (Before.IsSet()) { TestTrue(FString::Printf(TEXT("%s: dormant wake unchanged (both references and state)"), Label), FDormantWakeState(*AsDormantWake) == Before.GetValue()); }
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
		ExpectRejected(TEXT("dormant wake on a posture"), *Posture, TEXT("WrongComponentClass"));
		ExpectRejected(TEXT("dormant wake on an encounter"), *Encounter, TEXT("WrongComponentClass"));
		ExpectRejected(TEXT("dormant wake on a scene component"), *Scene, TEXT("WrongComponentClass"));
	}

	// Already registered (the owner has not begun play, so registration alone does not begin play for the component).
	{
		TStrongObjectPtr<URPGBossDormantWake> Registered = NewDormantWake(Owner, TEXT("RegisteredDormantWake"));
		if (!TestTrue(TEXT("registered component created"), Registered.IsValid()))
		{
			return false;
		}
		ArmDistinctStart(*Registered);
		Registered->RegisterComponent();
		if (!TestTrue(TEXT("precondition: registered and not begun"), Registered->IsRegistered() && !Registered->HasBegunPlay() && !Owner->HasActorBegunPlay()))
		{
			AddError(TEXT("unsupported precondition: the registered-but-not-begun state could not be built"));
			return false;
		}
		ExpectRejected(TEXT("registered dormant wake"), *Registered, TEXT("ComponentAlreadyRegistered"));
	}

	// Component already began play: the native BeginPlay only calls LoadSynchronous on the two soft references (and looks for an encounter on the owner, which this plain actor does not have), so both references
	// are cleared through the test helper first (a null soft path loads nothing) and the prerequisites are asserted before BeginPlay runs. No wake, no tick and no playback happens.
	{
		AActor* BegunOwner = Scope.SpawnOwner();
		if (!TestNotNull(TEXT("begun owner actor"), BegunOwner))
		{
			return false;
		}
		TStrongObjectPtr<URPGBossDormantWake> Begun = NewDormantWake(BegunOwner, TEXT("BegunDormantWake"));
		if (!TestTrue(TEXT("begun component created"), Begun.IsValid()))
		{
			return false;
		}
		const bool bCleared = WriteClip(*Begun, TEXT("DormantClip"), FSoftObjectPath()) && WriteClip(*Begun, TEXT("WakeClip"), FSoftObjectPath());
		const FDormantWakeState Cleared(*Begun);
		if (!TestTrue(TEXT("precondition: both references are cleared (BeginPlay will load nothing) and the owner is a plain actor without an encounter"),
			bCleared && Cleared.bReadable && Cleared.DormantClip.IsNull() && Cleared.WakeClip.IsNull() && !BegunOwner->FindComponentByClass<URPGBossEncounter>()))
		{
			AddError(TEXT("unsupported precondition: the begun-play fixture could not be made asset-free"));
			return false;
		}
		Begun->RegisterComponent();
		BegunOwner->DispatchBeginPlay();
		if (!TestTrue(TEXT("precondition: component and owner began play"), Begun->HasBegunPlay() && BegunOwner->HasActorBegunPlay()))
		{
			AddError(TEXT("unsupported precondition: the begun-play state could not be built without loading assets"));
			return false;
		}
		ExpectRejected(TEXT("begun dormant wake"), *Begun, TEXT("ComponentBegunPlay"));
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
		TStrongObjectPtr<URPGBossDormantWake> Late = NewDormantWake(LateOwner, TEXT("LateDormantWake"));
		if (!TestTrue(TEXT("late component created"), Late.IsValid()))
		{
			return false;
		}
		ArmDistinctStart(*Late);
		ExpectRejected(TEXT("dormant wake under a begun owner"), *Late, TEXT("OwnerBegunPlay"));
	}

	// Invalid owner: the component's outer is not an actor.
	{
		TStrongObjectPtr<URPGBossDormantWake> Orphan(NewObject<URPGBossDormantWake>(GetTransientPackage(), TEXT("OrphanDormantWake")));
		if (!TestTrue(TEXT("orphan component created"), Orphan.IsValid() && !Orphan->GetOwner()))
		{
			return false;
		}
		ArmDistinctStart(*Orphan);
		ExpectRejected(TEXT("dormant wake without an owner"), *Orphan, TEXT("InvalidOwner"));
	}

	// Destroyed component: DestroyComponent already ran (flagged as being destroyed, unregistered, EndPlay cleared, removed from its owner, marked garbage) but the object is still allocated because the test holds it
	// and no garbage collection runs here. The owner stays live, so this is the component check and not the owner check. This is not a freed-memory test.
	{
		AActor* LiveOwner = Scope.SpawnOwner();
		if (!TestNotNull(TEXT("live owner actor"), LiveOwner))
		{
			return false;
		}
		TStrongObjectPtr<URPGBossDormantWake> Dead = NewDormantWake(LiveOwner, TEXT("DeadDormantWake"));
		TStrongObjectPtr<URPGBossPosture> DeadPosture(NewObject<URPGBossPosture>(LiveOwner, TEXT("DeadPosture")));
		if (!TestTrue(TEXT("dead components created"), Dead.IsValid() && DeadPosture.IsValid()))
		{
			return false;
		}
		ArmDistinctStart(*Dead);
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
		ExpectRejected(TEXT("destroyed dormant wake"), *Dead, TEXT("InvalidComponent"));
		// The component check is first: a destroyed component of the WRONG class is reported as invalid, not as the wrong class.
		ExpectRejected(TEXT("dormant wake on a destroyed posture"), *DeadPosture, TEXT("InvalidComponent"));
		TestTrue(TEXT("the owner stayed live through both calls"), IsValid(LiveOwner) && !LiveOwner->IsActorBeingDestroyed());
	}

	AddInfo(TEXT("Rejection paths on isolated actors; an owner that is being destroyed is covered by the code (IsActorBeingDestroyed) but not exercised here."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGDormantWakeCompileTest, "OneBossFight.Binding.DormantWake.Compile",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGDormantWakeCompileTest::RunTest(const FString& Parameters)
{
	using namespace DormantWakeTests;
	const FEpochPtr Content = RPGCombatRegistry::Legacy();
	if (!TestTrue(TEXT("content epoch"), Content.IsValid() && Content->Id.IsValid()))
	{
		return false;
	}

	// The real synthetic compiler copies the record into the immutable config (both paths, exactly).
	{
		const FRPGParticipantConfig A = ConfigA();
		const TStrongObjectPtr<URPGBossDefinition> Definition = MakeDefinition(A.DormantWake);
		FConfigPtr Out;
		const FRPGHydrationResult Result = CompileSynthetic(*Definition, Content, Out);
		if (!TestTrue(TEXT("a valid definition compiles"), Result.IsReady() && Out.IsValid()))
		{
			return false;
		}
		TestTrue(TEXT("both references copied (record A)"), Out->DormantWake.DormantClip.ToSoftObjectPath() == A.DormantWake.DormantClip.ToSoftObjectPath()
			&& Out->DormantWake.WakeClip.ToSoftObjectPath() == A.DormantWake.WakeClip.ToSoftObjectPath());
		TestTrue(TEXT("established Stats, phase and identity values retained"), Out->Stats.MaxHealth == 3500.f && Out->Phases.Num() == 1 && Out->BossId == FName(TEXT("Synthetic")) && Out->bSyntheticFixture);
		TestTrue(TEXT("the encounter policy, stagger policy, flow, fireball, dependencies and stagger profile still carry their authoring defaults next to it"),
			Out->EncounterPolicy.GateRadius == 1200.f && Out->StaggerPolicy.StaggerSeconds == 2.5f && Out->PhaseFlow.TransitionSeconds == 1.8f && !Out->Fireball.bFireballEnabled
			&& Out->Fireball.FireballMaxRange == 1800.f && Out->PhaseDependencies.RoarClip.ToSoftObjectPath() == FRPGPhaseDependencyConfig().RoarClip.ToSoftObjectPath() && Out->StaggerProfile.bUseClips);
		// The config is a value snapshot: changing the definition afterwards changes nothing.
		Definition->DormantWake.DormantClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Changed"), TEXT("AN_Afterwards")));
		TestTrue(TEXT("a later definition change does not reach the compiled config"), Out->DormantWake.DormantClip.ToSoftObjectPath() == A.DormantWake.DormantClip.ToSoftObjectPath());
	}
	{
		const FRPGParticipantConfig B = ConfigB();
		const TStrongObjectPtr<URPGBossDefinition> Definition = MakeDefinition(B.DormantWake);
		FConfigPtr Out;
		TestTrue(TEXT("record B compiles"), CompileSynthetic(*Definition, Content, Out).IsReady() && Out.IsValid()
			&& Out->DormantWake.DormantClip.ToSoftObjectPath() == B.DormantWake.DormantClip.ToSoftObjectPath() && Out->DormantWake.WakeClip.ToSoftObjectPath() == B.DormantWake.WakeClip.ToSoftObjectPath());
	}
	// A definition whose record was never authored receives the additive authoring defaults, and the compiled config carries them.
	{
		const TStrongObjectPtr<URPGBossDefinition> Definition = MakeDefinition(FRPGDormantWakeConfig()); // what an old schema 1 definition holds: the field's own defaults
		FConfigPtr Out;
		const FRPGDormantWakeConfig Defaults;
		TestTrue(TEXT("untouched record: the authoring defaults are copied"), CompileSynthetic(*Definition, Content, Out).IsReady() && Out.IsValid()
			&& Out->DormantWake.DormantClip.ToSoftObjectPath() == Defaults.DormantClip.ToSoftObjectPath() && Out->DormantWake.WakeClip.ToSoftObjectPath() == Defaults.WakeClip.ToSoftObjectPath());
	}

	// An invalid record fails by name (with its field path), is NEVER replaced by the defaults, and clears a previously valid output; the production compile refuses it before any asset is loaded.
	struct FBad
	{
		const TCHAR* Name;
		TFunction<void(FRPGDormantWakeConfig&)> Break;
		const TCHAR* Token;
		const TCHAR* FieldPath;
	};
	const FBad Bad[] = {
		{TEXT("null dormant clip"), [](FRPGDormantWakeConfig& R) { R.DormantClip = SequencePtr(FSoftObjectPath()); }, TEXT("InvalidDependency.Missing"), TEXT("DormantWake.DormantClip")},
		{TEXT("null wake clip"), [](FRPGDormantWakeConfig& R) { R.WakeClip = SequencePtr(FSoftObjectPath()); }, TEXT("InvalidDependency.Missing"), TEXT("DormantWake.WakeClip")},
		{TEXT("dormant clip with whitespace"), [](FRPGDormantWakeConfig& R) { R.DormantClip = SequencePtr(MakePath(TEXT("/SyntheticMount/A B"), TEXT("AN_X"))); }, TEXT("InvalidDependency.Malformed"), TEXT("DormantWake.DormantClip")},
		{TEXT("wake clip naming a sub-object"), [](FRPGDormantWakeConfig& R) { R.WakeClip = SequencePtr(MakePath(TEXT("/SyntheticMount/A"), TEXT("AN_X"), TEXT("Sub"))); }, TEXT("InvalidDependency.Malformed"), TEXT("DormantWake.WakeClip")},
		{TEXT("wake clip without a leading slash"), [](FRPGDormantWakeConfig& R) { R.WakeClip = SequencePtr(MakePath(TEXT("Relative/A"), TEXT("AN_X"))); }, TEXT("InvalidDependency.Malformed"), TEXT("DormantWake.WakeClip")},
	};
	for (const FBad& Case : Bad)
	{
		FRPGDormantWakeConfig Broken = ConfigA().DormantWake;
		Case.Break(Broken);
		const TStrongObjectPtr<URPGBossDefinition> Definition = MakeDefinition(Broken);

		FConfigPtr Out;
		if (!TestTrue(FString::Printf(TEXT("%s: a valid output exists first"), Case.Name), CompileSynthetic(*MakeDefinition(ConfigA().DormantWake), Content, Out).IsReady() && Out.IsValid()))
		{
			return false;
		}
		const FRPGHydrationResult Result = CompileSynthetic(*Definition, Content, Out); // the same output variable
		TestFalse(FString::Printf(TEXT("%s (synthetic compile): refused"), Case.Name), Result.IsReady());
		TestTrue(FString::Printf(TEXT("%s (synthetic compile): named %s with the path %s"), Case.Name, Case.Token, Case.FieldPath), AnyErrorContains(Result, Case.Token) && AnyErrorContains(Result, Case.FieldPath));
		TestFalse(FString::Printf(TEXT("%s (synthetic compile): the earlier valid output was cleared, nothing defaulted"), Case.Name), Out.IsValid());

		FConfigPtr ProductionOut;
		const bool bPrecondition = CompileSynthetic(*MakeDefinition(ConfigA().DormantWake), Content, ProductionOut).IsReady() && ProductionOut.IsValid();
		if (!TestTrue(FString::Printf(TEXT("%s (production compile): a valid output exists first"), Case.Name), bPrecondition))
		{
			return false;
		}
		const FRPGHydrationResult Production = RPGCombatHydration::CompileParticipant(*Definition, Content, FString::ChrN(64, TEXT('b')), ProductionOut);
		TestFalse(FString::Printf(TEXT("%s (production compile): refused"), Case.Name), Production.IsReady());
		TestTrue(FString::Printf(TEXT("%s (production compile): named %s with the path %s"), Case.Name, Case.Token, Case.FieldPath), AnyErrorContains(Production, Case.Token) && AnyErrorContains(Production, Case.FieldPath));
		TestFalse(FString::Printf(TEXT("%s (production compile): the earlier output was cleared"), Case.Name), ProductionOut.IsValid());
	}

	// The established checks are retained, with a valid dormant wake record; each failure clears a previously valid output.
	auto RunRetained = [&](const TCHAR* Name, const TCHAR* Text, const TFunction<void(URPGBossDefinition&)>& Break, int32 Schema, const FString& Hash, bool bNullContent)
	{
		FConfigPtr Out;
		if (!CompileSynthetic(*MakeDefinition(ConfigA().DormantWake), Content, Out).IsReady() || !Out.IsValid())
		{
			AddError(TEXT("unsupported precondition: a valid output could not be built"));
			return;
		}
		const TStrongObjectPtr<URPGBossDefinition> Definition = MakeDefinition(ConfigA().DormantWake); // a valid dormant wake record
		Definition->Schema = Schema;
		Break(*Definition);
		const FRPGHydrationResult Result = CompileSynthetic(*Definition, bNullContent ? FEpochPtr() : Content, Out, Hash);
		TestFalse(FString::Printf(TEXT("%s: still refused with a valid dormant wake record"), Name), Result.IsReady());
		TestTrue(FString::Printf(TEXT("%s: the established message '%s'"), Name, Text), AnyErrorContains(Result, Text));
		TestFalse(FString::Printf(TEXT("%s: the earlier valid output was cleared"), Name), Out.IsValid());
	};
	const FString GoodHash = FString::ChrN(64, TEXT('b'));
	RunRetained(TEXT("invalid stagger profile"), TEXT("InvalidStaggerProfile.NoHitStunClass"), [](URPGBossDefinition& D) { D.StaggerProfile.HitStunAbilityClassName = NAME_None; }, 1, GoodHash, false);
	RunRetained(TEXT("invalid phase dependencies"), TEXT("InvalidDependency.Missing"), [](URPGBossDefinition& D) { D.PhaseDependencies.ImmunityEffect = TSoftClassPtr<UObject>(FSoftObjectPath()); }, 1, GoodHash, false);
	RunRetained(TEXT("invalid fireball"), TEXT("InvalidFireball.CooldownOrder"), [](URPGBossDefinition& D) { D.Fireball.FireballCooldown = FVector2D(5.0, 4.0); }, 1, GoodHash, false);
	RunRetained(TEXT("invalid phase flow"), TEXT("InvalidPhaseFlow.NoLeapTag"), [](URPGBossDefinition& D) { D.PhaseFlow.LeapAbilityTag = NAME_None; }, 1, GoodHash, false);
	RunRetained(TEXT("invalid stagger policy"), TEXT("InvalidStagger.NotPositive"), [](URPGBossDefinition& D) { D.StaggerPolicy.GetUpRate = 0.f; }, 1, GoodHash, false);
	RunRetained(TEXT("invalid encounter policy"), TEXT("InvalidPolicy.Negative"), [](URPGBossDefinition& D) { D.EncounterPolicy.GateRadius = -1.f; }, 1, GoodHash, false);
	RunRetained(TEXT("negative posture maximum"), TEXT("invalid stats"), [](URPGBossDefinition& D) { D.Stats.MaxPosture = -1.f; }, 1, GoodHash, false);
	RunRetained(TEXT("phase threshold above 1"), TEXT("invalid/duplicate phase"), [](URPGBossDefinition& D) { D.Phases[0].EntryHealthFraction = 2.f; }, 1, GoodHash, false);
	RunRetained(TEXT("schema 2"), TEXT("identity absent"), [](URPGBossDefinition&) {}, 2, GoodHash, false);
	RunRetained(TEXT("manifest hash that is not 64 hex characters"), TEXT("identity absent"), [](URPGBossDefinition&) {}, 1, TEXT("short"), false);
	RunRetained(TEXT("no content lease"), TEXT("identity absent"), [](URPGBossDefinition&) {}, 1, GoodHash, true);
	RunRetained(TEXT("no field manifest"), TEXT("field manifest required"), [](URPGBossDefinition& D) { D.Fields.Reset(); }, 1, GoodHash, false);

	// Several failures are all reported: an invalid dormant wake record together with an invalid stagger profile, stagger policy, encounter policy and stats.
	{
		FRPGDormantWakeConfig Broken = ConfigA().DormantWake;
		Broken.WakeClip = SequencePtr(FSoftObjectPath());
		const TStrongObjectPtr<URPGBossDefinition> Definition = MakeDefinition(Broken);
		Definition->StaggerProfile.HitStunAbilityClassName = NAME_None;
		Definition->StaggerPolicy.GetUpRate = -2.f;
		Definition->EncounterPolicy.GateRadius = -5.f;
		Definition->Stats.MaxPosture = -1.f;
		FConfigPtr Out;
		const FRPGHydrationResult Result = CompileSynthetic(*Definition, Content, Out);
		TestTrue(TEXT("invalid dormant wake record, stagger profile, stagger policy, encounter policy and stats are all reported"),
			!Result.IsReady() && AnyErrorContains(Result, TEXT("DormantWake.WakeClip")) && AnyErrorContains(Result, TEXT("InvalidStaggerProfile.NoHitStunClass")) && AnyErrorContains(Result, TEXT("InvalidStagger.NotPositive"))
			&& AnyErrorContains(Result, TEXT("InvalidPolicy.Negative")) && AnyErrorContains(Result, TEXT("invalid stats")) && !Out.IsValid());
	}

	AddInfo(TEXT("Real synthetic compiler and the production compile's early rejection; NO production compile with a real skeleton, NO serialized asset."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGDormantWakeAuthoringTest, "OneBossFight.Binding.DormantWake.Authoring",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGDormantWakeAuthoringTest::RunTest(const FString& Parameters)
{
	using namespace DormantWakeTests;
	const UScriptStruct* Struct = FRPGDormantWakeConfig::StaticStruct();
	if (!TestNotNull(TEXT("the dormant wake struct is reflected"), Struct))
	{
		return false;
	}
	const UClass* Native = URPGBossDormantWake::StaticClass();

	// The record: two editable soft object references (NOT soft class references) with the names of the native private properties, which have the same kind and are editable too. Declarations only.
	for (const TCHAR* Name : {TEXT("DormantClip"), TEXT("WakeClip")})
	{
		const FProperty* Property = Struct->FindPropertyByName(Name);
		TestTrue(FString::Printf(TEXT("%s: a reflected, editable soft object reference of the record"), Name), Property && CastField<FSoftObjectProperty>(Property) && !CastField<FSoftClassProperty>(Property) && Property->HasAnyPropertyFlags(CPF_Edit));
		const FProperty* NativeProperty = Native->FindPropertyByName(Name);
		TestTrue(FString::Printf(TEXT("%s: the same name and kind (soft object reference, editable) on URPGBossDormantWake"), Name),
			NativeProperty && CastField<FSoftObjectProperty>(NativeProperty) && !CastField<FSoftClassProperty>(NativeProperty) && NativeProperty->HasAnyPropertyFlags(CPF_Edit));
	}

	// The Data Asset field: the definition exposes the record as an editable property of exactly that struct type.
	const FStructProperty* Field = CastField<FStructProperty>(URPGBossDefinition::StaticClass()->FindPropertyByName(TEXT("DormantWake")));
	if (!TestTrue(TEXT("the definition has a DormantWake struct property"), Field != nullptr))
	{
		return false;
	}
	TestTrue(TEXT("it is editable (EditAnywhere) and of the dormant wake struct type"), Field->HasAnyPropertyFlags(CPF_Edit) && Field->Struct == Struct);

	// The additive authoring defaults of the NEW field: a fresh struct and a fresh definition hold them; the native constructor values are only the baseline they match, not an authority.
	const FRPGDormantWakeConfig Fresh;
	TStrongObjectPtr<URPGBossDefinition> Definition(NewObject<URPGBossDefinition>());
	TestTrue(TEXT("a fresh definition holds the authoring defaults (old schema 1 definitions receive them additively)"),
		Definition->DormantWake.DormantClip.ToSoftObjectPath() == Fresh.DormantClip.ToSoftObjectPath() && Definition->DormantWake.WakeClip.ToSoftObjectPath() == Fresh.WakeClip.ToSoftObjectPath());
	FSoftObjectPath NativeDormant;
	FSoftObjectPath NativeWake;
	const bool bRead = ReadClip(*GetDefault<URPGBossDormantWake>(), TEXT("DormantClip"), NativeDormant) && ReadClip(*GetDefault<URPGBossDormantWake>(), TEXT("WakeClip"), NativeWake);
	TestTrue(TEXT("baseline: the defaults equal the native constructor values of URPGBossDormantWake (read through typed reflection), field by field"), bRead && Fresh.DormantClip.ToSoftObjectPath() == NativeDormant && Fresh.WakeClip.ToSoftObjectPath() == NativeWake);
	// The documented values, so a silent change of the declared defaults is noticed (suffix compares: the sources keep no quoted /Game/ literal in this file).
	TestTrue(TEXT("the defaults are the documented ones"), Fresh.DormantClip.ToSoftObjectPath().ToString().EndsWith(TEXT("/Boss01/Animations/AN_Boss01_DormantIdle.AN_Boss01_DormantIdle"), ESearchCase::CaseSensitive)
		&& Fresh.WakeClip.ToSoftObjectPath().ToString().EndsWith(TEXT("/Boss01/Animations/AN_Boss01_Wake.AN_Boss01_Wake"), ESearchCase::CaseSensitive));
	// The defaults pass their own validator (they are valid, not a fallback for invalid input).
	FString Error;
	TestTrue(TEXT("the authoring defaults pass the shared validator"), RPGBossDormantWakeAdapters::ValidateDormantWake(Fresh, Error) && Error.IsEmpty());
	AddInfo(TEXT("Reflection and defaults only; NOT a serialized asset and NOT seen in the Details panel."));
	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
