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
#include "Player/RPGBossPosture.h"
#include "Player/RPGBossStagger.h"
#include "Player/RPGBossStaggerPolicyAdapters.h"
#include "UObject/Package.h"
#include "UObject/StrongObjectPtr.h"
#include "UObject/UnrealType.h"
#include <cmath>
#include <limits>

// These tests prove the typed stagger and riposte scalar policy: its reflected authoring exposure, its copy into the immutable config by the real definition compiler (synthetic path, and the production path's early
// rejection), the shared validator with every scalar boundary, and the typed, lifecycle-safe assignment of exactly fourteen fields on isolated native components. They do NOT prove a serialized asset value, anything seen
// in the Details panel, a production compile with a real skeleton, any clip, montage, effect or mode dependency, a real stance break or riposte, a duel or any wiring. The defaults are the documented authoring defaults of
// the new asset field and are compared with the native declarations only as a baseline. No Stagger tick, break or riposte runs here; the one BeginPlay that runs (the begun-component guard) loads nothing because the four
// clip soft pointers are cleared first.

namespace
{
namespace StaggerTests
{
	using FEpochPtr = TSharedPtr<const RPGCombatRegistry::FEpoch>;
	using FConfigPtr = TSharedPtr<const FRPGParticipantConfig>;
	using FFloatMember = float FRPGStaggerPolicyConfig::*;

	constexpr float QuietNaN = std::numeric_limits<float>::quiet_NaN();
	constexpr float PosInf = std::numeric_limits<float>::infinity();

	/** Test-local game world with the set-up the earlier headless tests used; destroyed with the scope. */
	struct FStaggerTestWorld
	{
		UWorld* World = nullptr;

		FStaggerTestWorld()
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

		~FStaggerTestWorld()
		{
			if (World)
			{
				GEngine->DestroyWorldContext(World);
				World->DestroyWorld(/*bInformEngineOfWorld=*/false);
			}
		}

		FStaggerTestWorld(const FStaggerTestWorld&) = delete;
		FStaggerTestWorld& operator=(const FStaggerTestWorld&) = delete;

		AActor* SpawnOwner() const { return World ? World->SpawnActor<AActor>() : nullptr; }
	};

	/** The thirteen float fields in field order with the domain each one is validated in (0 not negative, 1 strictly positive, 2 angle within [0,360], 3 critical multiplier, at least 1). */
	struct FFloatField
	{
		const TCHAR* Name;
		FFloatMember Member;
		int32 Kind;
	};

	const FFloatField FloatFields[13] = {
		{TEXT("StaggerSeconds"), &FRPGStaggerPolicyConfig::StaggerSeconds, 0},
		{TEXT("FreezeAtPosition"), &FRPGStaggerPolicyConfig::FreezeAtPosition, 0},
		{TEXT("CriticalMultiplier"), &FRPGStaggerPolicyConfig::CriticalMultiplier, 3},
		{TEXT("RiposteRange"), &FRPGStaggerPolicyConfig::RiposteRange, 0},
		{TEXT("RiposteConeDegrees"), &FRPGStaggerPolicyConfig::RiposteConeDegrees, 2},
		{TEXT("RiposteFacingDegrees"), &FRPGStaggerPolicyConfig::RiposteFacingDegrees, 2},
		{TEXT("RiposteArmSeconds"), &FRPGStaggerPolicyConfig::RiposteArmSeconds, 0},
		{TEXT("RipostePlayerStartGap"), &FRPGStaggerPolicyConfig::RipostePlayerStartGap, 0},
		{TEXT("RiposteAlignSeconds"), &FRPGStaggerPolicyConfig::RiposteAlignSeconds, 1},
		{TEXT("RiposteImpactSeconds"), &FRPGStaggerPolicyConfig::RiposteImpactSeconds, 0},
		{TEXT("RiposteBaseDamage"), &FRPGStaggerPolicyConfig::RiposteBaseDamage, 0},
		{TEXT("CooldownSeconds"), &FRPGStaggerPolicyConfig::CooldownSeconds, 0},
		{TEXT("GetUpRate"), &FRPGStaggerPolicyConfig::GetUpRate, 1},
	};

	/** Fourteen distinct non-default values (none equals its declared default); the bool is false (the default is true). */
	FRPGStaggerPolicyConfig NondefaultPolicyA()
	{
		FRPGStaggerPolicyConfig P;
		P.StaggerSeconds = 3.75f;
		P.FreezeAtPosition = 2.25f;
		P.CriticalMultiplier = 3.5f;
		P.RiposteRange = 210.5f;
		P.RiposteConeDegrees = 95.5f;
		P.RiposteFacingDegrees = 80.25f;
		P.RiposteArmSeconds = 1.75f;
		P.RipostePlayerStartGap = 175.5f;
		P.RiposteAlignSeconds = 0.45f;
		P.RiposteImpactSeconds = 1.1f;
		P.RiposteBaseDamage = 55.5f;
		P.CooldownSeconds = 2.5f;
		P.GetUpRate = 0.8f;
		P.bHoldPostureAtZero = false;
		return P;
	}

	/** A second, different record with the bool true, so both truth values are exercised. */
	FRPGStaggerPolicyConfig NondefaultPolicyB()
	{
		FRPGStaggerPolicyConfig P;
		P.StaggerSeconds = 4.5f;
		P.FreezeAtPosition = 0.75f;
		P.CriticalMultiplier = 1.f;
		P.RiposteRange = 0.f;
		P.RiposteConeDegrees = 360.f;
		P.RiposteFacingDegrees = 0.f;
		P.RiposteArmSeconds = 0.f;
		P.RipostePlayerStartGap = 0.f;
		P.RiposteAlignSeconds = 0.05f;
		P.RiposteImpactSeconds = 0.f;
		P.RiposteBaseDamage = 0.f;
		P.CooldownSeconds = 9.5f;
		P.GetUpRate = 2.f;
		P.bHoldPostureAtZero = true;
		return P;
	}

	bool PolicyEquals(const FRPGStaggerPolicyConfig& A, const FRPGStaggerPolicyConfig& B)
	{
		for (const FFloatField& Field : FloatFields)
		{
			if (A.*Field.Member != B.*Field.Member)
			{
				return false;
			}
		}
		return A.bHoldPostureAtZero == B.bHoldPostureAtZero;
	}

	FRPGStaggerPolicyConfig ReadPolicy(const URPGBossStagger& S)
	{
		FRPGStaggerPolicyConfig P;
		P.StaggerSeconds = S.StaggerSeconds;
		P.FreezeAtPosition = S.FreezeAtPosition;
		P.CriticalMultiplier = S.CriticalMultiplier;
		P.RiposteRange = S.RiposteRange;
		P.RiposteConeDegrees = S.RiposteConeDegrees;
		P.RiposteFacingDegrees = S.RiposteFacingDegrees;
		P.RiposteArmSeconds = S.RiposteArmSeconds;
		P.RipostePlayerStartGap = S.RipostePlayerStartGap;
		P.RiposteAlignSeconds = S.RiposteAlignSeconds;
		P.RiposteImpactSeconds = S.RiposteImpactSeconds;
		P.RiposteBaseDamage = S.RiposteBaseDamage;
		P.CooldownSeconds = S.CooldownSeconds;
		P.GetUpRate = S.GetUpRate;
		P.bHoldPostureAtZero = S.bHoldPostureAtZero;
		return P;
	}

	/** Everything a failed call must leave alone and a successful one must leave alone except the fourteen policy fields: the policy, the unrelated configuration (test knobs, mode toggles, class name), the clip, montage and
	 *  effect references and the public runtime state. */
	struct FStaggerState
	{
		FRPGStaggerPolicyConfig Policy;
		bool bCriticalOnEveryHit, bUseClips, bUseRiposteClips;
		FName HitStunAbilityClassName;
		FSoftObjectPath RipostePlayerClip, RiposteBossClip, FallMontage, GetUpMontage, FallClip, DownClip, ImmunityEffect;
		bool bStaggered, bCriticalWindowOpen, bUsingClips, bRiposteExecuting;
		int32 StaggerCount, CriticalHitCount, RiposteCount, RiposteRejectCount, RiposteImpactCount, RiposteAbortCount;
		FString LastRiposteResult, LastBreakResult, ClipStageName;
		double LastEndTime;

		explicit FStaggerState(const URPGBossStagger& S)
			: Policy(ReadPolicy(S)), bCriticalOnEveryHit(S.bCriticalOnEveryHit), bUseClips(S.bUseClips), bUseRiposteClips(S.bUseRiposteClips), HitStunAbilityClassName(S.HitStunAbilityClassName)
			, RipostePlayerClip(S.RipostePlayerClip.ToSoftObjectPath()), RiposteBossClip(S.RiposteBossClip.ToSoftObjectPath()), FallMontage(S.FallMontage.ToSoftObjectPath())
			, GetUpMontage(S.GetUpMontage.ToSoftObjectPath()), FallClip(S.FallClip.ToSoftObjectPath()), DownClip(S.DownClip.ToSoftObjectPath()), ImmunityEffect(S.ImmunityEffect.ToSoftObjectPath())
			, bStaggered(S.IsStaggered()), bCriticalWindowOpen(S.IsCriticalWindowOpen()), bUsingClips(S.IsUsingClips()), bRiposteExecuting(S.IsRiposteExecuting())
			, StaggerCount(S.GetStaggerCount()), CriticalHitCount(S.GetCriticalHitCount()), RiposteCount(S.GetRiposteCount()), RiposteRejectCount(S.GetRiposteRejectCount())
			, RiposteImpactCount(S.GetRiposteImpactCount()), RiposteAbortCount(S.GetRiposteAbortCount()), LastRiposteResult(S.GetLastRiposteResult()), LastBreakResult(S.GetLastBreakResult())
			, ClipStageName(S.GetClipStageName()), LastEndTime(S.GetLastEndTime())
		{
		}

		bool OutsideEquals(const FStaggerState& O) const
		{
			return bCriticalOnEveryHit == O.bCriticalOnEveryHit && bUseClips == O.bUseClips && bUseRiposteClips == O.bUseRiposteClips && HitStunAbilityClassName == O.HitStunAbilityClassName
				&& RipostePlayerClip == O.RipostePlayerClip && RiposteBossClip == O.RiposteBossClip && FallMontage == O.FallMontage && GetUpMontage == O.GetUpMontage && FallClip == O.FallClip
				&& DownClip == O.DownClip && ImmunityEffect == O.ImmunityEffect && bStaggered == O.bStaggered && bCriticalWindowOpen == O.bCriticalWindowOpen && bUsingClips == O.bUsingClips
				&& bRiposteExecuting == O.bRiposteExecuting && StaggerCount == O.StaggerCount && CriticalHitCount == O.CriticalHitCount && RiposteCount == O.RiposteCount
				&& RiposteRejectCount == O.RiposteRejectCount && RiposteImpactCount == O.RiposteImpactCount && RiposteAbortCount == O.RiposteAbortCount && LastRiposteResult == O.LastRiposteResult
				&& LastBreakResult == O.LastBreakResult && ClipStageName == O.ClipStageName && LastEndTime == O.LastEndTime;
		}

		bool operator==(const FStaggerState& O) const { return PolicyEquals(Policy, O.Policy) && OutsideEquals(O); }
	};

	/** Sentinels the policy must never touch: non-default values for the test knob, the two mode toggles and the class name. */
	void ArmSentinels(URPGBossStagger& Stagger)
	{
		Stagger.bCriticalOnEveryHit = true;
		Stagger.bUseClips = false;
		Stagger.bUseRiposteClips = false;
		Stagger.HitStunAbilityClassName = TEXT("SentinelHitStun");
	}

	FRPGParticipantConfig MakeConfig(const FRPGStaggerPolicyConfig& Policy)
	{
		FRPGParticipantConfig Config;
		Config.StaggerPolicy = Policy;
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

	/** A valid definition for the real synthetic compiler, with a typed stagger policy. */
	TStrongObjectPtr<URPGBossDefinition> MakeDefinition(const FRPGStaggerPolicyConfig& Policy)
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
		Definition->StaggerPolicy = Policy;
		Definition->Fields.Add(MakeField(RPGBossStaggerPolicyAdapters::FieldStaggerSeconds, TEXT("synthetic")));
		Definition->Fields.Add(MakeField(RPGBossStaggerPolicyAdapters::FieldHoldPostureAtZero, TEXT("synthetic")));
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

	TStrongObjectPtr<URPGBossStagger> NewStagger(AActor* Owner, const TCHAR* Name)
	{
		return TStrongObjectPtr<URPGBossStagger>(NewObject<URPGBossStagger>(Owner, Name));
	}
}
}

// No file-scope using-directive on purpose: several test files define helpers with the same names in their own namespaces, and two file-scope using-directives in one unity translation unit would make
// those names ambiguous. Each test body names its namespace itself.

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGStaggerPolicyAssignTest, "OneBossFight.Binding.StaggerPolicy.Assign",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGStaggerPolicyAssignTest::RunTest(const FString& Parameters)
{
	using namespace StaggerTests;
	FStaggerTestWorld Scope;
	if (!TestNotNull(TEXT("test world"), Scope.World))
	{
		return false;
	}
	AActor* Owner = Scope.SpawnOwner();
	if (!TestNotNull(TEXT("owner actor"), Owner))
	{
		return false;
	}
	TStrongObjectPtr<URPGBossStagger> Stagger = NewStagger(Owner, TEXT("RPGBossStagger"));
	if (!TestTrue(TEXT("component created"), Stagger.IsValid()))
	{
		return false;
	}
	ArmSentinels(*Stagger);
	const FStaggerState Before(*Stagger);
	const int32 OwnedComponentsBefore = Owner->GetComponents().Num();

	// All fourteen values really are non-default, in both records, and the bool takes both values.
	const FRPGStaggerPolicyConfig Defaults;
	const FRPGStaggerPolicyConfig A = NondefaultPolicyA();
	const FRPGStaggerPolicyConfig B = NondefaultPolicyB();
	bool bAllDifferentFromDefault = A.bHoldPostureAtZero != Defaults.bHoldPostureAtZero;
	for (const FFloatField& Field : FloatFields)
	{
		bAllDifferentFromDefault &= (A.*Field.Member != Defaults.*Field.Member);
	}
	TestTrue(TEXT("record A: all 13 floats and the bool differ from the authoring defaults"), bAllDifferentFromDefault);
	TestTrue(TEXT("record B holds the other truth value of the bool"), B.bHoldPostureAtZero != A.bHoldPostureAtZero);

	// The unwired plan fragment: the legacy instance name, the exact class and the fourteen typed paths in field order.
	const FRPGComponentPlan Plan = RPGBossStaggerPolicyAdapters::MakeStaggerPolicyPlan();
	TestTrue(TEXT("plan class"), Plan.Class == URPGBossStagger::StaticClass());
	TestTrue(TEXT("plan instance name"), Plan.InstanceName == FName(TEXT("RPGBossStagger")));
	TestTrue(TEXT("plan required fields are the fourteen typed paths"), Plan.RequiredFields == TArray<FString>{
		TEXT("StaggerPolicy.StaggerSeconds"), TEXT("StaggerPolicy.FreezeAtPosition"), TEXT("StaggerPolicy.CriticalMultiplier"), TEXT("StaggerPolicy.RiposteRange"),
		TEXT("StaggerPolicy.RiposteConeDegrees"), TEXT("StaggerPolicy.RiposteFacingDegrees"), TEXT("StaggerPolicy.RiposteArmSeconds"), TEXT("StaggerPolicy.RipostePlayerStartGap"),
		TEXT("StaggerPolicy.RiposteAlignSeconds"), TEXT("StaggerPolicy.RiposteImpactSeconds"), TEXT("StaggerPolicy.RiposteBaseDamage"), TEXT("StaggerPolicy.CooldownSeconds"),
		TEXT("StaggerPolicy.GetUpRate"), TEXT("StaggerPolicy.bHoldPostureAtZero")});
	if (!TestTrue(TEXT("plan callback is set"), static_cast<bool>(Plan.Configure)))
	{
		return false;
	}

	// Record A through the plan callback, with a manifest whose Value TEXT says something else: only the typed record counts.
	FRPGParticipantConfig Config = MakeConfig(A);
	Config.Fields.Add(MakeField(RPGBossStaggerPolicyAdapters::FieldStaggerSeconds, TEXT("9999")));
	Config.Fields.Add(MakeField(RPGBossStaggerPolicyAdapters::FieldHoldPostureAtZero, TEXT("true")));
	Config.Fields.Add(MakeField(RPGBossStaggerPolicyAdapters::FieldGetUpRate, TEXT("0.01")));
	FString Error = TEXT("a stale diagnostic from an earlier call");
	TestTrue(TEXT("callback succeeds"), Plan.Configure(*Stagger, Config, Error));
	TestTrue(TEXT("the diagnostic was cleared on success"), Error.IsEmpty());
	TestTrue(TEXT("all fourteen fields are the typed record, not the manifest text"), PolicyEquals(ReadPolicy(*Stagger), A));
	TestTrue(TEXT("the bool is the typed false, not the manifest text true"), !Stagger->bHoldPostureAtZero);

	// Exactly fourteen assignments: the unrelated configuration, the clip references and the runtime state equal their pre-call values.
	FStaggerState Expected = Before;
	Expected.Policy = A;
	TestTrue(TEXT("nothing but the fourteen policy fields changed"), FStaggerState(*Stagger) == Expected);
	TestTrue(TEXT("test knob, mode toggles and class name sentinels untouched"), Stagger->bCriticalOnEveryHit && !Stagger->bUseClips && !Stagger->bUseRiposteClips && Stagger->HitStunAbilityClassName == FName(TEXT("SentinelHitStun")));

	// The callback created nothing, registered nothing and began nothing.
	TestFalse(TEXT("component stays unregistered"), Stagger->IsRegistered());
	TestFalse(TEXT("component did not begin play"), Stagger->HasBegunPlay());
	TestFalse(TEXT("owner did not begin play"), Owner->HasActorBegunPlay());
	TestTrue(TEXT("owner gained no component"), Owner->GetComponents().Num() == OwnedComponentsBefore);

	// Record B through the direct helper: every field replaced, the bool true, zero values valid.
	TestTrue(TEXT("record B"), RPGBossStaggerPolicyAdapters::ConfigureStaggerPolicy(*Stagger, MakeConfig(B), Error) && PolicyEquals(ReadPolicy(*Stagger), B) && Stagger->bHoldPostureAtZero);
	FStaggerState ExpectedB = Before;
	ExpectedB.Policy = B;
	TestTrue(TEXT("again nothing but the fourteen fields changed"), FStaggerState(*Stagger) == ExpectedB);

	AddInfo(TEXT("Typed scalar policy assignment only; NOT a real stance break or riposte, NOT clips or mode policy, NOT a serialized asset value, NOT a duel."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGStaggerPolicyValidationTest, "OneBossFight.Binding.StaggerPolicy.Validation",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGStaggerPolicyValidationTest::RunTest(const FString& Parameters)
{
	using namespace StaggerTests;
	FStaggerTestWorld Scope;
	if (!TestNotNull(TEXT("test world"), Scope.World))
	{
		return false;
	}
	AActor* Owner = Scope.SpawnOwner();
	if (!TestNotNull(TEXT("owner actor"), Owner))
	{
		return false;
	}
	TStrongObjectPtr<URPGBossStagger> Stagger = NewStagger(Owner, TEXT("RPGBossStagger"));
	if (!TestTrue(TEXT("component created"), Stagger.IsValid()))
	{
		return false;
	}
	ArmSentinels(*Stagger);
	const FStaggerState Before(*Stagger);
	const FRPGStaggerPolicyConfig Base = NondefaultPolicyA(); // valid, every field non-default

	// One check: the validator refuses (or accepts) the policy with that token, and the assignment does the same with NO write at all.
	auto Check = [&](const FString& Label, const FRPGStaggerPolicyConfig& Policy, const TCHAR* ExpectedToken, const FString& ExpectedPath)
	{
		FString Error = TEXT("a stale diagnostic");
		const bool bOk = RPGBossStaggerPolicyAdapters::ValidateStaggerPolicy(Policy, Error);
		if (!ExpectedToken)
		{
			TestTrue(FString::Printf(TEXT("%s: valid, and the diagnostic was cleared"), *Label), bOk && Error.IsEmpty());
			return;
		}
		TestFalse(FString::Printf(TEXT("%s: rejected"), *Label), bOk);
		TestTrue(FString::Printf(TEXT("%s: named %s (got '%s')"), *Label, ExpectedToken, *Error), Error.StartsWith(ExpectedToken));
		if (!ExpectedPath.IsEmpty())
		{
			TestTrue(FString::Printf(TEXT("%s: names the field %s"), *Label, *ExpectedPath), Error.Contains(ExpectedPath));
		}
		FString ConfigureError = TEXT("a stale diagnostic");
		TestFalse(FString::Printf(TEXT("%s: the assignment refuses"), *Label), RPGBossStaggerPolicyAdapters::ConfigureStaggerPolicy(*Stagger, MakeConfig(Policy), ConfigureError));
		TestTrue(FString::Printf(TEXT("%s: the assignment names the same token"), *Label), ConfigureError.StartsWith(ExpectedToken));
		TestTrue(FString::Printf(TEXT("%s: no write at all (fourteen fields, sentinels, state)"), *Label), FStaggerState(*Stagger) == Before);
	};

	Check(TEXT("the base record"), Base, nullptr, FString());
	Check(TEXT("the authoring defaults"), FRPGStaggerPolicyConfig(), nullptr, FString());

	// Every scalar, generated: NaN, +Inf and -Inf are refused as not finite wherever they sit.
	for (const FFloatField& Field : FloatFields)
	{
		const FString Path = FString(TEXT("StaggerPolicy.")) + Field.Name;
		for (const float Bad : {QuietNaN, PosInf, -PosInf})
		{
			FRPGStaggerPolicyConfig P = Base;
			P.*Field.Member = Bad;
			Check(FString::Printf(TEXT("%s = %s"), Field.Name, *LexToString(Bad)), P, TEXT("InvalidStagger.NotFinite"), Path);
		}
	}

	// The domain of each kind, at its boundary.
	for (const FFloatField& Field : FloatFields)
	{
		const FString Path = FString(TEXT("StaggerPolicy.")) + Field.Name;
		auto With = [&](float Value) { FRPGStaggerPolicyConfig P = Base; P.*Field.Member = Value; return P; };
		switch (Field.Kind)
		{
		case 0: // not negative: zero is valid (the native immediate, empty-window or no-cooldown meaning), just below zero is not
			Check(FString::Printf(TEXT("%s = 0 (valid)"), Field.Name), With(0.f), nullptr, FString());
			Check(FString::Printf(TEXT("%s = -0.0 (valid, it is zero)"), Field.Name), With(-0.f), nullptr, FString());
			Check(FString::Printf(TEXT("%s = 0.0001 (valid)"), Field.Name), With(0.0001f), nullptr, FString());
			Check(FString::Printf(TEXT("%s = -0.0001"), Field.Name), With(-0.0001f), TEXT("InvalidStagger.Negative"), Path);
			Check(FString::Printf(TEXT("%s = -1"), Field.Name), With(-1.f), TEXT("InvalidStagger.Negative"), Path);
			break;
		case 1: // strictly positive: the native code divides by it
			Check(FString::Printf(TEXT("%s = 0.0001 (valid)"), Field.Name), With(0.0001f), nullptr, FString());
			Check(FString::Printf(TEXT("%s = 0"), Field.Name), With(0.f), TEXT("InvalidStagger.NotPositive"), Path);
			Check(FString::Printf(TEXT("%s = -0.0 (zero)"), Field.Name), With(-0.f), TEXT("InvalidStagger.NotPositive"), Path);
			Check(FString::Printf(TEXT("%s = -1"), Field.Name), With(-1.f), TEXT("InvalidStagger.NotPositive"), Path);
			break;
		case 2: // an angle within [0, 360]
			Check(FString::Printf(TEXT("%s = 0 (valid)"), Field.Name), With(0.f), nullptr, FString());
			Check(FString::Printf(TEXT("%s = 360 (valid, the full cone)"), Field.Name), With(360.f), nullptr, FString());
			Check(FString::Printf(TEXT("%s = 5 (valid, no invented floor)"), Field.Name), With(5.f), nullptr, FString());
			Check(FString::Printf(TEXT("%s = -0.1"), Field.Name), With(-0.1f), TEXT("InvalidStagger.AngleOutOfRange"), Path);
			Check(FString::Printf(TEXT("%s = 360.1"), Field.Name), With(360.1f), TEXT("InvalidStagger.AngleOutOfRange"), Path);
			Check(FString::Printf(TEXT("%s = first float above 360"), Field.Name), With(std::nextafter(360.f, 1000.f)), TEXT("InvalidStagger.AngleOutOfRange"), Path);
			break;
		case 3: // the critical multiplier: at least 1 (a native capability, since below 1 would add health)
			Check(FString::Printf(TEXT("%s = 1 (valid)"), Field.Name), With(1.f), nullptr, FString());
			Check(FString::Printf(TEXT("%s = 1.5 (valid)"), Field.Name), With(1.5f), nullptr, FString());
			Check(FString::Printf(TEXT("%s = first float below 1"), Field.Name), With(std::nextafter(1.f, 0.f)), TEXT("UnsupportedNativeCritical"), Path);
			Check(FString::Printf(TEXT("%s = 0.5"), Field.Name), With(0.5f), TEXT("UnsupportedNativeCritical"), Path);
			Check(FString::Printf(TEXT("%s = 0"), Field.Name), With(0.f), TEXT("UnsupportedNativeCritical"), Path);
			Check(FString::Printf(TEXT("%s = -1"), Field.Name), With(-1.f), TEXT("UnsupportedNativeCritical"), Path);
			break;
		default:
			AddError(TEXT("unsupported precondition: an unknown field kind in the test table"));
			break;
		}
	}

	// No partial write whichever field is invalid: first, middle and last of otherwise valid non-default records.
	{
		FRPGStaggerPolicyConfig Last = Base;
		Last.GetUpRate = 0.f;
		Check(TEXT("only the LAST scalar invalid (GetUpRate 0), thirteen others valid and non-default"), Last, TEXT("InvalidStagger.NotPositive"), TEXT("StaggerPolicy.GetUpRate"));
		FRPGStaggerPolicyConfig First = Base;
		First.StaggerSeconds = QuietNaN;
		Check(TEXT("only the FIRST scalar invalid (StaggerSeconds NaN)"), First, TEXT("InvalidStagger.NotFinite"), TEXT("StaggerPolicy.StaggerSeconds"));
		FRPGStaggerPolicyConfig Middle = Base;
		Middle.RiposteAlignSeconds = 0.f;
		Check(TEXT("only a MIDDLE scalar invalid (RiposteAlignSeconds 0)"), Middle, TEXT("InvalidStagger.NotPositive"), TEXT("StaggerPolicy.RiposteAlignSeconds"));
	}

	// Precedence: every scalar finite first, then the generic domains in field order, then the critical capability.
	{
		FRPGStaggerPolicyConfig P = Base;
		P.CriticalMultiplier = 0.5f;
		P.StaggerSeconds = -1.f;
		Check(TEXT("critical below 1 and a negative duration: the generic domain is reported first"), P, TEXT("InvalidStagger.Negative"), TEXT("StaggerPolicy.StaggerSeconds"));
		P = Base;
		P.CriticalMultiplier = 0.5f;
		P.GetUpRate = 0.f;
		Check(TEXT("critical below 1 and a zero get-up rate: the generic domain is reported first"), P, TEXT("InvalidStagger.NotPositive"), TEXT("StaggerPolicy.GetUpRate"));
		P = Base;
		P.StaggerSeconds = -1.f;
		P.GetUpRate = QuietNaN;
		Check(TEXT("a NaN anywhere outranks a negative value"), P, TEXT("InvalidStagger.NotFinite"), TEXT("StaggerPolicy.GetUpRate"));
		P = Base;
		P.RiposteConeDegrees = 400.f;
		P.RiposteRange = -1.f;
		Check(TEXT("negative range (field order) before an out-of-range cone angle"), P, TEXT("InvalidStagger.Negative"), TEXT("StaggerPolicy.RiposteRange"));
	}

	// The component refused every record above and is still configurable.
	FString Error;
	TestTrue(TEXT("after all refusals a valid record still configures"), RPGBossStaggerPolicyAdapters::ConfigureStaggerPolicy(*Stagger, MakeConfig(Base), Error) && PolicyEquals(ReadPolicy(*Stagger), Base));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGStaggerPolicyIsolationTest, "OneBossFight.Binding.StaggerPolicy.Isolation",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGStaggerPolicyIsolationTest::RunTest(const FString& Parameters)
{
	using namespace StaggerTests;
	FStaggerTestWorld Scope;
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
	TStrongObjectPtr<URPGBossStagger> A = NewStagger(OwnerA, TEXT("RPGBossStagger"));
	TStrongObjectPtr<URPGBossStagger> B = NewStagger(OwnerB, TEXT("RPGBossStagger"));
	TStrongObjectPtr<URPGBossStagger> C = NewStagger(OwnerC, TEXT("RPGBossStagger"));
	if (!TestTrue(TEXT("three components"), A.IsValid() && B.IsValid() && C.IsValid()))
	{
		return false;
	}
	FRPGParticipantConfig ConfigA = MakeConfig(NondefaultPolicyA());
	const FRPGParticipantConfig ConfigB = MakeConfig(NondefaultPolicyB());
	FString Error;
	TestTrue(TEXT("A"), RPGBossStaggerPolicyAdapters::ConfigureStaggerPolicy(*A, ConfigA, Error));
	const FStaggerState SnapshotA(*A);
	TestTrue(TEXT("B"), RPGBossStaggerPolicyAdapters::ConfigureStaggerPolicy(*B, ConfigB, Error));
	TestTrue(TEXT("configuring B did not change A"), FStaggerState(*A) == SnapshotA);
	TestTrue(TEXT("B has its own fourteen values"), PolicyEquals(ReadPolicy(*B), NondefaultPolicyB()));

	// The assignment copies values: changing the config afterwards changes nothing.
	ConfigA.StaggerPolicy.StaggerSeconds = 99.f;
	ConfigA.StaggerPolicy.bHoldPostureAtZero = true;
	TestTrue(TEXT("a later config change does not reach A"), FStaggerState(*A) == SnapshotA);

	// A component that was never configured keeps the native declarations, and so does the class default object.
	const FRPGStaggerPolicyConfig Defaults;
	TestTrue(TEXT("untouched component keeps the declared defaults"), PolicyEquals(ReadPolicy(*C), Defaults));
	TestTrue(TEXT("CDO keeps the declared defaults"), PolicyEquals(ReadPolicy(*GetDefault<URPGBossStagger>()), Defaults));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGStaggerPolicyRejectionsTest, "OneBossFight.Binding.StaggerPolicy.Rejections",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGStaggerPolicyRejectionsTest::RunTest(const FString& Parameters)
{
	using namespace StaggerTests;
	FStaggerTestWorld Scope;
	if (!TestNotNull(TEXT("test world"), Scope.World))
	{
		return false;
	}
	const FRPGParticipantConfig Config = MakeConfig(NondefaultPolicyA()); // valid: every failure below is about the component or the owner
	FString Error;

	// A rejected call changes nothing and names the reason. Wrong-class targets are concrete classes (UActorComponent itself is abstract).
	auto ExpectRejected = [&](const TCHAR* Label, UActorComponent& Component, const TCHAR* Token)
	{
		const URPGBossStagger* AsStagger = Cast<URPGBossStagger>(&Component);
		const URPGBossEncounter* AsEncounter = Cast<URPGBossEncounter>(&Component);
		const URPGBossPosture* AsPosture = Cast<URPGBossPosture>(&Component);
		TOptional<FStaggerState> Before;
		if (AsStagger) { Before.Emplace(*AsStagger); }
		const float EncounterGateBefore = AsEncounter ? AsEncounter->GateRadius : 0.f;
		const float PostureMaxBefore = AsPosture ? AsPosture->PostureMax : 0.f;
		const bool bOk = RPGBossStaggerPolicyAdapters::ConfigureStaggerPolicy(Component, Config, Error);
		TestFalse(FString::Printf(TEXT("%s: rejected"), Label), bOk);
		TestTrue(FString::Printf(TEXT("%s: named %s (got '%s')"), Label, Token, *Error), Error.StartsWith(Token));
		if (Before.IsSet()) { TestTrue(FString::Printf(TEXT("%s: stagger unchanged (sentinels included)"), Label), FStaggerState(*AsStagger) == Before.GetValue()); }
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
		ExpectRejected(TEXT("policy on a posture"), *Posture, TEXT("WrongComponentClass"));
		ExpectRejected(TEXT("policy on an encounter"), *Encounter, TEXT("WrongComponentClass"));
		ExpectRejected(TEXT("policy on a scene component"), *Scene, TEXT("WrongComponentClass"));
	}

	// Already registered (the owner has not begun play, so registration alone does not begin play for the component).
	{
		TStrongObjectPtr<URPGBossStagger> Stagger = NewStagger(Owner, TEXT("RegisteredStagger"));
		if (!TestTrue(TEXT("registered component created"), Stagger.IsValid()))
		{
			return false;
		}
		ArmSentinels(*Stagger);
		Stagger->RegisterComponent();
		if (!TestTrue(TEXT("precondition: registered and not begun"), Stagger->IsRegistered() && !Stagger->HasBegunPlay() && !Owner->HasActorBegunPlay()))
		{
			AddError(TEXT("unsupported precondition: the registered-but-not-begun state could not be built"));
			return false;
		}
		ExpectRejected(TEXT("registered stagger"), *Stagger, TEXT("ComponentAlreadyRegistered"));
	}

	// Component already began play: its owner begins play with the component registered. The stagger BeginPlay only loads its four clip soft pointers, so they are cleared first and nothing is loaded.
	{
		AActor* BegunOwner = Scope.SpawnOwner();
		if (!TestNotNull(TEXT("begun owner actor"), BegunOwner))
		{
			return false;
		}
		TStrongObjectPtr<URPGBossStagger> Stagger = NewStagger(BegunOwner, TEXT("BegunStagger"));
		if (!TestTrue(TEXT("begun component created"), Stagger.IsValid()))
		{
			return false;
		}
		ArmSentinels(*Stagger);
		Stagger->FallClip.Reset();
		Stagger->DownClip.Reset();
		Stagger->RipostePlayerClip.Reset();
		Stagger->RiposteBossClip.Reset();
		Stagger->RegisterComponent();
		BegunOwner->DispatchBeginPlay();
		if (!TestTrue(TEXT("precondition: component and owner began play"), Stagger->HasBegunPlay() && BegunOwner->HasActorBegunPlay()))
		{
			AddError(TEXT("unsupported precondition: the begun-play state could not be built without loading clips"));
			return false;
		}
		ExpectRejected(TEXT("begun stagger"), *Stagger, TEXT("ComponentBegunPlay"));
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
		TStrongObjectPtr<URPGBossStagger> Stagger = NewStagger(LateOwner, TEXT("LateStagger"));
		if (!TestTrue(TEXT("late component created"), Stagger.IsValid()))
		{
			return false;
		}
		ArmSentinels(*Stagger);
		ExpectRejected(TEXT("stagger under a begun owner"), *Stagger, TEXT("OwnerBegunPlay"));
	}

	// Invalid owner: the component's outer is not an actor.
	{
		TStrongObjectPtr<URPGBossStagger> Stagger(NewObject<URPGBossStagger>(GetTransientPackage(), TEXT("OrphanStagger")));
		if (!TestTrue(TEXT("orphan component created"), Stagger.IsValid() && !Stagger->GetOwner()))
		{
			return false;
		}
		ArmSentinels(*Stagger);
		ExpectRejected(TEXT("stagger without an owner"), *Stagger, TEXT("InvalidOwner"));
	}

	// Destroyed component: DestroyComponent already ran (flagged as being destroyed, unregistered, EndPlay cleared, removed from its owner, marked garbage) but the object is still allocated because the test holds it
	// and no garbage collection runs here. The owner stays live, so this is the component check and not the owner check. This is not a freed-memory test.
	{
		AActor* LiveOwner = Scope.SpawnOwner();
		if (!TestNotNull(TEXT("live owner actor"), LiveOwner))
		{
			return false;
		}
		TStrongObjectPtr<URPGBossStagger> Stagger = NewStagger(LiveOwner, TEXT("DeadStagger"));
		TStrongObjectPtr<URPGBossPosture> Posture(NewObject<URPGBossPosture>(LiveOwner, TEXT("DeadPosture")));
		if (!TestTrue(TEXT("dead components created"), Stagger.IsValid() && Posture.IsValid()))
		{
			return false;
		}
		ArmSentinels(*Stagger);
		Stagger->DestroyComponent();
		Posture->DestroyComponent();
		const bool bRetained = Stagger.Get() != nullptr && Posture.Get() != nullptr && Stagger->GetOuter() == LiveOwner && Posture->GetOuter() == LiveOwner;
		const bool bFlaggedDead = Stagger->IsBeingDestroyed() && Posture->IsBeingDestroyed();
		const bool bOwnerLive = IsValid(LiveOwner) && !LiveOwner->IsActorBeingDestroyed() && !LiveOwner->HasActorBegunPlay();
		if (!TestTrue(TEXT("precondition: destroyed components still allocated and linked to their owner, owner live"), bRetained && bFlaggedDead && bOwnerLive))
		{
			AddError(TEXT("unsupported precondition: the destroyed-but-retained state could not be built"));
			return false;
		}
		TestTrue(TEXT("precondition: a destroyed component looks unregistered and not begun, which is why only the first check can refuse it"), !Stagger->IsRegistered() && !Stagger->HasBegunPlay());
		ExpectRejected(TEXT("destroyed stagger"), *Stagger, TEXT("InvalidComponent"));
		// The component check is first: a destroyed component of the WRONG class is reported as invalid, not as the wrong class.
		ExpectRejected(TEXT("policy on a destroyed posture"), *Posture, TEXT("InvalidComponent"));
		TestTrue(TEXT("the owner stayed live through both calls"), IsValid(LiveOwner) && !LiveOwner->IsActorBeingDestroyed());
	}

	AddInfo(TEXT("Rejection paths on isolated actors; an owner that is being destroyed is covered by the code (IsActorBeingDestroyed) but not exercised here."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGStaggerPolicyCompileTest, "OneBossFight.Binding.StaggerPolicy.Compile",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGStaggerPolicyCompileTest::RunTest(const FString& Parameters)
{
	using namespace StaggerTests;
	const FEpochPtr Content = RPGCombatRegistry::Legacy();
	if (!TestTrue(TEXT("content epoch"), Content.IsValid() && Content->Id.IsValid()))
	{
		return false;
	}

	// The real synthetic compiler copies every one of the fourteen fields into the immutable config, with both truth values of the bool.
	{
		const TStrongObjectPtr<URPGBossDefinition> Definition = MakeDefinition(NondefaultPolicyA());
		FConfigPtr Out;
		const FRPGHydrationResult Result = CompileSynthetic(*Definition, Content, Out);
		if (!TestTrue(TEXT("a valid definition compiles"), Result.IsReady() && Out.IsValid()))
		{
			return false;
		}
		TestTrue(TEXT("all fourteen fields copied (bool false)"), PolicyEquals(Out->StaggerPolicy, NondefaultPolicyA()));
		TestTrue(TEXT("established Stats, phase and identity values retained"), Out->Stats.MaxHealth == 3500.f && Out->Phases.Num() == 1 && Out->BossId == FName(TEXT("Synthetic")) && Out->bSyntheticFixture);
		TestTrue(TEXT("the encounter policy still carries its authoring defaults next to it"), Out->EncounterPolicy.GateRadius == 1200.f && Out->EncounterPolicy.bResetOnPlayerRespawn);
		// The config is a value snapshot: changing the definition afterwards changes nothing.
		Definition->StaggerPolicy.StaggerSeconds = 99.f;
		Definition->StaggerPolicy.bHoldPostureAtZero = true;
		TestTrue(TEXT("a later definition change does not reach the compiled config"), PolicyEquals(Out->StaggerPolicy, NondefaultPolicyA()));
	}
	{
		const TStrongObjectPtr<URPGBossDefinition> Definition = MakeDefinition(NondefaultPolicyB());
		FConfigPtr Out;
		TestTrue(TEXT("record B compiles with the bool true and zero values"), CompileSynthetic(*Definition, Content, Out).IsReady() && Out.IsValid() && PolicyEquals(Out->StaggerPolicy, NondefaultPolicyB()) && Out->StaggerPolicy.bHoldPostureAtZero);
	}
	// A definition whose stagger policy was never authored receives the additive authoring defaults, and the compiled config carries them.
	{
		TStrongObjectPtr<URPGBossDefinition> Definition = MakeDefinition(NondefaultPolicyA());
		Definition->StaggerPolicy = FRPGStaggerPolicyConfig(); // what an old schema 1 definition holds: the field's own defaults
		FConfigPtr Out;
		TestTrue(TEXT("untouched policy: the authoring defaults are copied"), CompileSynthetic(*Definition, Content, Out).IsReady() && Out.IsValid() && PolicyEquals(Out->StaggerPolicy, FRPGStaggerPolicyConfig()));
	}

	// An invalid policy fails by name, is NEVER replaced by the defaults and NEVER clamped, and clears a previously valid output; the production compile refuses it before any asset is loaded.
	struct FBad
	{
		const TCHAR* Name;
		TFunction<void(FRPGStaggerPolicyConfig&)> Break;
		const TCHAR* Token;
	};
	const FBad Bad[] = {
		{TEXT("NaN stagger seconds"), [](FRPGStaggerPolicyConfig& P) { P.StaggerSeconds = QuietNaN; }, TEXT("InvalidStagger.NotFinite")},
		{TEXT("negative riposte range"), [](FRPGStaggerPolicyConfig& P) { P.RiposteRange = -1.f; }, TEXT("InvalidStagger.Negative")},
		{TEXT("zero get-up rate"), [](FRPGStaggerPolicyConfig& P) { P.GetUpRate = 0.f; }, TEXT("InvalidStagger.NotPositive")},
		{TEXT("cone angle above 360"), [](FRPGStaggerPolicyConfig& P) { P.RiposteConeDegrees = 361.f; }, TEXT("InvalidStagger.AngleOutOfRange")},
		{TEXT("critical multiplier below 1"), [](FRPGStaggerPolicyConfig& P) { P.CriticalMultiplier = 0.5f; }, TEXT("UnsupportedNativeCritical")},
	};
	for (const FBad& Case : Bad)
	{
		FRPGStaggerPolicyConfig Policy = NondefaultPolicyA();
		Case.Break(Policy);
		const TStrongObjectPtr<URPGBossDefinition> Definition = MakeDefinition(Policy);

		FConfigPtr Out;
		if (!TestTrue(FString::Printf(TEXT("%s: a valid output exists first"), Case.Name), CompileSynthetic(*MakeDefinition(NondefaultPolicyA()), Content, Out).IsReady() && Out.IsValid()))
		{
			return false;
		}
		const FRPGHydrationResult Result = CompileSynthetic(*Definition, Content, Out); // the same output variable
		TestFalse(FString::Printf(TEXT("%s (synthetic compile): refused"), Case.Name), Result.IsReady());
		TestTrue(FString::Printf(TEXT("%s (synthetic compile): named %s"), Case.Name, Case.Token), AnyErrorContains(Result, Case.Token));
		TestFalse(FString::Printf(TEXT("%s (synthetic compile): the earlier valid output was cleared, nothing defaulted or clamped"), Case.Name), Out.IsValid());

		FConfigPtr ProductionOut;
		if (CompileSynthetic(*MakeDefinition(NondefaultPolicyA()), Content, ProductionOut).IsReady() && ProductionOut.IsValid())
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

	// The established checks are retained, with a valid stagger policy; each failure clears a previously valid output.
	auto RunRetained = [&](const TCHAR* Name, const TCHAR* Text, const TFunction<void(URPGBossDefinition&)>& Break, int32 Schema, const FString& Hash, bool bNullContent)
	{
		FConfigPtr Out;
		if (!CompileSynthetic(*MakeDefinition(NondefaultPolicyA()), Content, Out).IsReady() || !Out.IsValid())
		{
			AddError(TEXT("unsupported precondition: a valid output could not be built"));
			return;
		}
		const TStrongObjectPtr<URPGBossDefinition> Definition = MakeDefinition(NondefaultPolicyA()); // a valid stagger policy
		Definition->Schema = Schema;
		Break(*Definition);
		const FRPGHydrationResult Result = CompileSynthetic(*Definition, bNullContent ? FEpochPtr() : Content, Out, Hash);
		TestFalse(FString::Printf(TEXT("%s: still refused with a valid stagger policy"), Name), Result.IsReady());
		TestTrue(FString::Printf(TEXT("%s: the established message '%s'"), Name, Text), AnyErrorContains(Result, Text));
		TestFalse(FString::Printf(TEXT("%s: the earlier valid output was cleared"), Name), Out.IsValid());
	};
	const FString GoodHash = FString::ChrN(64, TEXT('b'));
	RunRetained(TEXT("invalid encounter policy"), TEXT("InvalidPolicy.Negative"), [](URPGBossDefinition& D) { D.EncounterPolicy.GateRadius = -1.f; }, 1, GoodHash, false);
	RunRetained(TEXT("negative posture maximum"), TEXT("invalid stats"), [](URPGBossDefinition& D) { D.Stats.MaxPosture = -1.f; }, 1, GoodHash, false);
	RunRetained(TEXT("phase threshold above 1"), TEXT("invalid/duplicate phase"), [](URPGBossDefinition& D) { D.Phases[0].EntryHealthFraction = 2.f; }, 1, GoodHash, false);
	RunRetained(TEXT("schema 2"), TEXT("identity absent"), [](URPGBossDefinition&) {}, 2, GoodHash, false);
	RunRetained(TEXT("manifest hash that is not 64 hex characters"), TEXT("identity absent"), [](URPGBossDefinition&) {}, 1, TEXT("short"), false);
	RunRetained(TEXT("no content lease"), TEXT("identity absent"), [](URPGBossDefinition&) {}, 1, GoodHash, true);
	RunRetained(TEXT("no field manifest"), TEXT("field manifest required"), [](URPGBossDefinition& D) { D.Fields.Reset(); }, 1, GoodHash, false);

	// Several failures are all reported: an invalid stagger policy together with an invalid encounter policy and invalid stats.
	{
		FRPGStaggerPolicyConfig Policy = NondefaultPolicyA();
		Policy.GetUpRate = -2.f;
		const TStrongObjectPtr<URPGBossDefinition> Definition = MakeDefinition(Policy);
		Definition->EncounterPolicy.GateRadius = -5.f;
		Definition->Stats.MaxPosture = -1.f;
		FConfigPtr Out;
		const FRPGHydrationResult Result = CompileSynthetic(*Definition, Content, Out);
		TestTrue(TEXT("invalid stagger policy, encounter policy and stats are all reported"), !Result.IsReady() && AnyErrorContains(Result, TEXT("InvalidStagger.NotPositive")) && AnyErrorContains(Result, TEXT("InvalidPolicy.Negative")) && AnyErrorContains(Result, TEXT("invalid stats")) && !Out.IsValid());
	}

	AddInfo(TEXT("Real synthetic compiler and the production compile's early rejection; NO production compile with a real skeleton, NO serialized asset."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGStaggerPolicyAuthoringTest, "OneBossFight.Binding.StaggerPolicy.Authoring",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGStaggerPolicyAuthoringTest::RunTest(const FString& Parameters)
{
	using namespace StaggerTests;
	// The reflected record: the thirteen floats and the bool exist with the native names, the right types, and are editable.
	const UScriptStruct* Struct = FRPGStaggerPolicyConfig::StaticStruct();
	if (!TestNotNull(TEXT("the stagger policy struct is reflected"), Struct))
	{
		return false;
	}
	for (const FFloatField& Field : FloatFields)
	{
		const FProperty* Property = Struct->FindPropertyByName(Field.Name);
		TestTrue(FString::Printf(TEXT("%s is a reflected, editable float property"), Field.Name), Property && CastField<FFloatProperty>(Property) && Property->HasAnyPropertyFlags(CPF_Edit));
		// The same name exists on the native component, so the typed record mirrors it.
		TestTrue(FString::Printf(TEXT("%s also exists as a float property of URPGBossStagger"), Field.Name), URPGBossStagger::StaticClass()->FindPropertyByName(Field.Name) != nullptr);
	}
	const FProperty* Hold = Struct->FindPropertyByName(TEXT("bHoldPostureAtZero"));
	TestTrue(TEXT("bHoldPostureAtZero is a reflected, editable bool property"), Hold && CastField<FBoolProperty>(Hold) && Hold->HasAnyPropertyFlags(CPF_Edit));
	TestTrue(TEXT("bHoldPostureAtZero also exists as a bool property of URPGBossStagger"), CastField<FBoolProperty>(URPGBossStagger::StaticClass()->FindPropertyByName(TEXT("bHoldPostureAtZero"))) != nullptr);

	// The Data Asset field: the definition exposes the policy as an editable property of exactly that struct type, and the config-side record is the plain copy.
	const FProperty* Field = URPGBossDefinition::StaticClass()->FindPropertyByName(TEXT("StaggerPolicy"));
	const FStructProperty* AsStruct = CastField<FStructProperty>(Field);
	if (!TestTrue(TEXT("the definition has a StaggerPolicy struct property"), AsStruct != nullptr))
	{
		return false;
	}
	TestTrue(TEXT("it is editable (EditAnywhere)"), AsStruct->HasAnyPropertyFlags(CPF_Edit));
	TestTrue(TEXT("and of the stagger policy struct type"), AsStruct->Struct == Struct);

	// The additive authoring defaults of the NEW field: a fresh struct and a fresh definition hold them; the native declarations are only the baseline they match, not an authority.
	const FRPGStaggerPolicyConfig Fresh;
	TStrongObjectPtr<URPGBossDefinition> Definition(NewObject<URPGBossDefinition>());
	TestTrue(TEXT("a fresh definition holds the authoring defaults (old schema 1 definitions receive them additively)"), PolicyEquals(Definition->StaggerPolicy, Fresh));
	TestTrue(TEXT("baseline: they equal the native declarations of URPGBossStagger, field by field"), PolicyEquals(ReadPolicy(*GetDefault<URPGBossStagger>()), Fresh));
	// The documented values, so a silent change of the declared defaults is noticed.
	TestTrue(TEXT("the declared defaults are the documented ones"), Fresh.StaggerSeconds == 2.5f && Fresh.FreezeAtPosition == 1.55f && Fresh.CriticalMultiplier == 2.5f && Fresh.RiposteRange == 150.f
		&& Fresh.RiposteConeDegrees == 120.f && Fresh.RiposteFacingDegrees == 120.f && Fresh.RiposteArmSeconds == 1.2f && Fresh.RipostePlayerStartGap == 150.f && Fresh.RiposteAlignSeconds == 0.3f
		&& Fresh.RiposteImpactSeconds == 0.8f && Fresh.RiposteBaseDamage == 40.f && Fresh.CooldownSeconds == 0.f && Fresh.GetUpRate == 0.6f && Fresh.bHoldPostureAtZero);
	// The other authored records of the definition were not disturbed by the new field, and the defaults pass their own validator (they are valid, not a fallback for invalid input).
	FString Error;
	TestTrue(TEXT("the authoring defaults pass the shared validator"), RPGBossStaggerPolicyAdapters::ValidateStaggerPolicy(Fresh, Error) && Error.IsEmpty());
	TestTrue(TEXT("the stats record keeps its own defaults (no substitution)"), Definition->Stats.MaxHealth == 0.f && Definition->Stats.MaxPosture == 0.f && Definition->Schema == 1);
	AddInfo(TEXT("Reflection and defaults only; NOT a serialized asset and NOT seen in the Details panel."));
	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
