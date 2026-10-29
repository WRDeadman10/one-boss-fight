// Copyright One Boss Fight. All Rights Reserved.
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
#include "Components/SceneComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"
#include "Player/RPGBossBleed.h"
#include "Player/RPGBossDeath.h"
#include "Player/RPGBossDeathAdapters.h"
#include "Player/RPGBossPosture.h"
#include "UObject/Package.h"
#include "UObject/StrongObjectPtr.h"
#include "UObject/UnrealType.h"
#include "Animation/AnimMontage.h"
#include "Animation/AnimSequence.h"
#include <limits>
#include <cmath>
#include "UObject/TopLevelAssetPath.h"

// SOURCE-ONLY, UNRUN. No Death BeginPlay/Tick/Attach, remains, pack ability,
// preload/load/playback/pose/test-knob call. Plain actor starts before attachment.
namespace
{
namespace DeathTests
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
	TSoftObjectPtr<UAnimSequence> Clip(const FSoftObjectPath& Path)
	{
		return TSoftObjectPtr<UAnimSequence>(Path);
	}
	TSoftObjectPtr<UAnimMontage> Montage(const FSoftObjectPath& Path)
	{
		return TSoftObjectPtr<UAnimMontage>(Path);
	}
	FRPGDeathConfig RecordA()
	{
		FRPGDeathConfig R;
		R.DeathMode = ERPGBossDeathMode::OwnClip;
		R.DeathClip = Clip(MakePath(TEXT("/SyntheticMount/Death/A"), TEXT("ClipA")));
		R.DeathMontage = Montage(MakePath(TEXT("/SyntheticMount/Death/A"), TEXT("MontageA")));
		R.PackDeathAbilityClassName = TEXT("Custom.DeathAbility-A");
		R.PackDeathMontagesName = TEXT("Custom.Montages-A");
		R.PackPollSeconds = 0.125f;
		R.PackEndTimeMultiplier = 0.f;
		R.HoldAtSeconds = 0.25f;
		R.DyingSeconds = 0.5f;
		R.BlendInSeconds = 0.f;
		R.MaxClipRestarts = 0;
		R.bGuardPackDeath = true;
		return R;
	}
	FRPGDeathConfig RecordB()
	{
		FRPGDeathConfig R;
		R.DeathMode = ERPGBossDeathMode::PackMontage;
		R.DeathClip = Clip(MakePath(TEXT("/OtherSynthetic/Death/B"), TEXT("ClipB")));
		R.DeathMontage = Montage(MakePath(TEXT("/OtherSynthetic/Death/B"), TEXT("MontageB")));
		R.PackDeathAbilityClassName = TEXT("CustomDeathAbilityB");
		R.PackDeathMontagesName = TEXT("CustomMontagesB");
		R.PackPollSeconds = 0.5f;
		R.PackEndTimeMultiplier = 0.75f;
		R.HoldAtSeconds = 1.25f;
		R.DyingSeconds = 1.5f;
		R.BlendInSeconds = 0.125f;
		R.MaxClipRestarts = 17;
		R.bGuardPackDeath = false;
		return R;
	}
	FRPGParticipantConfig Config(const FRPGDeathConfig& R)
	{
		FRPGParticipantConfig C;
		C.Death = R;
		return C;
	}
	FRPGDeathConfig Read(const URPGBossDeath& Death)
	{
		FRPGDeathConfig R;
		R.DeathMode = Death.DeathMode;
		R.DeathClip = Death.DeathClip;
		R.DeathMontage = Death.DeathMontage;
		R.PackDeathAbilityClassName = Death.PackDeathAbilityClassName;
		R.PackDeathMontagesName = Death.PackDeathMontagesName;
		R.PackPollSeconds = Death.PackPollSeconds;
		R.PackEndTimeMultiplier = Death.PackEndTimeMultiplier;
		R.HoldAtSeconds = Death.HoldAtSeconds;
		R.DyingSeconds = Death.DyingSeconds;
		R.BlendInSeconds = Death.BlendInSeconds;
		R.MaxClipRestarts = Death.MaxClipRestarts;
		R.bGuardPackDeath = Death.bGuardPackDeath;
		return R;
	}
	bool Same(const FRPGDeathConfig& A, const FRPGDeathConfig& B)
	{
		return A.DeathMode == B.DeathMode && A.DeathClip.ToSoftObjectPath() == B.DeathClip.ToSoftObjectPath() && A.DeathMontage.ToSoftObjectPath() == B.DeathMontage.ToSoftObjectPath() && A.PackDeathAbilityClassName == B.PackDeathAbilityClassName && A.PackDeathMontagesName == B.PackDeathMontagesName && A.PackPollSeconds == B.PackPollSeconds && A.PackEndTimeMultiplier == B.PackEndTimeMultiplier && A.HoldAtSeconds == B.HoldAtSeconds && A.DyingSeconds == B.DyingSeconds && A.BlendInSeconds == B.BlendInSeconds && A.MaxClipRestarts == B.MaxClipRestarts && A.bGuardPackDeath == B.bGuardPackDeath;
	}

	struct FRuntime
	{
		bool Active, Held, Registered, Begun, TickRegistered, CanTick;
		double Age;
		FString State, LastPack;
		TArray<int32> Counters;
		explicit FRuntime(const URPGBossDeath& C)
			: Active(C.IsDeathActive()), Held(C.IsPoseHeld()), Registered(C.IsRegistered()), Begun(C.HasBegunPlay()),
			TickRegistered(C.PrimaryComponentTick.IsTickFunctionRegistered()), CanTick(C.PrimaryComponentTick.bCanEverTick),
			Age(C.GetDeathAge()), State(C.GetDeathStateName()), LastPack(C.GetLastPackResult()),
			Counters{C.GetDeathCount(), C.GetClipPlayCount(), C.GetClipRestartCount(), C.GetPoseHoldCount(), C.GetPhysicsOffCount(), C.GetPackSetCount()} {}
		bool SameAs(const FRuntime& O) const
		{
			return Active == O.Active && Held == O.Held && Registered == O.Registered && Begun == O.Begun && TickRegistered == O.TickRegistered
				&& CanTick == O.CanTick && Age == O.Age && State == O.State && LastPack == O.LastPack && Counters == O.Counters;
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
		return {TEXT("Death.DeathMode"), TEXT("Death.DeathClip"), TEXT("Death.DeathMontage"), TEXT("Death.PackDeathAbilityClassName"), TEXT("Death.PackDeathMontagesName"), TEXT("Death.PackPollSeconds"), TEXT("Death.PackEndTimeMultiplier"), TEXT("Death.HoldAtSeconds"), TEXT("Death.DyingSeconds"), TEXT("Death.BlendInSeconds"), TEXT("Death.MaxClipRestarts"), TEXT("Death.bGuardPackDeath")};
	}
	struct FBad
	{
		FString Name;
		TFunction<void(FRPGDeathConfig&)> Mutate;
		const TCHAR* Token;
		const TCHAR* Path;
	};
	TArray<FBad> BadCases()
	{
		TArray<FBad> Cases;
		Cases.Add({TEXT("PackPollSeconds NaN"), [](FRPGDeathConfig& R) { R.PackPollSeconds = std::numeric_limits<float>::quiet_NaN(); }, TEXT("InvalidDeath.NotFinite"), TEXT("Death.PackPollSeconds")});
		Cases.Add({TEXT("PackPollSeconds +Inf"), [](FRPGDeathConfig& R) { R.PackPollSeconds = std::numeric_limits<float>::infinity(); }, TEXT("InvalidDeath.NotFinite"), TEXT("Death.PackPollSeconds")});
		Cases.Add({TEXT("PackPollSeconds -Inf"), [](FRPGDeathConfig& R) { R.PackPollSeconds = -std::numeric_limits<float>::infinity(); }, TEXT("InvalidDeath.NotFinite"), TEXT("Death.PackPollSeconds")});
		Cases.Add({TEXT("PackEndTimeMultiplier NaN"), [](FRPGDeathConfig& R) { R.PackEndTimeMultiplier = std::numeric_limits<float>::quiet_NaN(); }, TEXT("InvalidDeath.NotFinite"), TEXT("Death.PackEndTimeMultiplier")});
		Cases.Add({TEXT("PackEndTimeMultiplier +Inf"), [](FRPGDeathConfig& R) { R.PackEndTimeMultiplier = std::numeric_limits<float>::infinity(); }, TEXT("InvalidDeath.NotFinite"), TEXT("Death.PackEndTimeMultiplier")});
		Cases.Add({TEXT("PackEndTimeMultiplier -Inf"), [](FRPGDeathConfig& R) { R.PackEndTimeMultiplier = -std::numeric_limits<float>::infinity(); }, TEXT("InvalidDeath.NotFinite"), TEXT("Death.PackEndTimeMultiplier")});
		Cases.Add({TEXT("HoldAtSeconds NaN"), [](FRPGDeathConfig& R) { R.HoldAtSeconds = std::numeric_limits<float>::quiet_NaN(); }, TEXT("InvalidDeath.NotFinite"), TEXT("Death.HoldAtSeconds")});
		Cases.Add({TEXT("HoldAtSeconds +Inf"), [](FRPGDeathConfig& R) { R.HoldAtSeconds = std::numeric_limits<float>::infinity(); }, TEXT("InvalidDeath.NotFinite"), TEXT("Death.HoldAtSeconds")});
		Cases.Add({TEXT("HoldAtSeconds -Inf"), [](FRPGDeathConfig& R) { R.HoldAtSeconds = -std::numeric_limits<float>::infinity(); }, TEXT("InvalidDeath.NotFinite"), TEXT("Death.HoldAtSeconds")});
		Cases.Add({TEXT("DyingSeconds NaN"), [](FRPGDeathConfig& R) { R.DyingSeconds = std::numeric_limits<float>::quiet_NaN(); }, TEXT("InvalidDeath.NotFinite"), TEXT("Death.DyingSeconds")});
		Cases.Add({TEXT("DyingSeconds +Inf"), [](FRPGDeathConfig& R) { R.DyingSeconds = std::numeric_limits<float>::infinity(); }, TEXT("InvalidDeath.NotFinite"), TEXT("Death.DyingSeconds")});
		Cases.Add({TEXT("DyingSeconds -Inf"), [](FRPGDeathConfig& R) { R.DyingSeconds = -std::numeric_limits<float>::infinity(); }, TEXT("InvalidDeath.NotFinite"), TEXT("Death.DyingSeconds")});
		Cases.Add({TEXT("BlendInSeconds NaN"), [](FRPGDeathConfig& R) { R.BlendInSeconds = std::numeric_limits<float>::quiet_NaN(); }, TEXT("InvalidDeath.NotFinite"), TEXT("Death.BlendInSeconds")});
		Cases.Add({TEXT("BlendInSeconds +Inf"), [](FRPGDeathConfig& R) { R.BlendInSeconds = std::numeric_limits<float>::infinity(); }, TEXT("InvalidDeath.NotFinite"), TEXT("Death.BlendInSeconds")});
		Cases.Add({TEXT("BlendInSeconds -Inf"), [](FRPGDeathConfig& R) { R.BlendInSeconds = -std::numeric_limits<float>::infinity(); }, TEXT("InvalidDeath.NotFinite"), TEXT("Death.BlendInSeconds")});
		Cases.Add({TEXT("bad enum 2"), [](FRPGDeathConfig& R) { R.DeathMode = static_cast<ERPGBossDeathMode>(2); }, TEXT("InvalidDeath.BadMode"), TEXT("Death.DeathMode")});
		Cases.Add({TEXT("bad enum 255"), [](FRPGDeathConfig& R) { R.DeathMode = static_cast<ERPGBossDeathMode>(255); }, TEXT("InvalidDeath.BadMode"), TEXT("Death.DeathMode")});
		Cases.Add({TEXT("PackPollSeconds zero"), [](FRPGDeathConfig& R) { R.PackPollSeconds = 0.f; }, TEXT("InvalidDeath.NotPositive"), TEXT("Death.PackPollSeconds")});
		Cases.Add({TEXT("PackPollSeconds negative"), [](FRPGDeathConfig& R) { R.PackPollSeconds = -1.f; }, TEXT("InvalidDeath.NotPositive"), TEXT("Death.PackPollSeconds")});
		Cases.Add({TEXT("PackPollSeconds nextafter ceiling"), [](FRPGDeathConfig& R) { R.PackPollSeconds = std::nextafter(RPGBossDeathAdapters::MaxAuthoredMagnitude, std::numeric_limits<float>::infinity()); }, TEXT("InvalidDeath.AboveCeiling"), TEXT("Death.PackPollSeconds")});
		Cases.Add({TEXT("PackEndTimeMultiplier negative"), [](FRPGDeathConfig& R) { R.PackEndTimeMultiplier = -1.f; }, TEXT("InvalidDeath.Negative"), TEXT("Death.PackEndTimeMultiplier")});
		Cases.Add({TEXT("PackEndTimeMultiplier nextafter ceiling"), [](FRPGDeathConfig& R) { R.PackEndTimeMultiplier = std::nextafter(RPGBossDeathAdapters::MaxAuthoredMagnitude, std::numeric_limits<float>::infinity()); }, TEXT("InvalidDeath.AboveCeiling"), TEXT("Death.PackEndTimeMultiplier")});
		Cases.Add({TEXT("HoldAtSeconds zero"), [](FRPGDeathConfig& R) { R.HoldAtSeconds = 0.f; }, TEXT("InvalidDeath.NotPositive"), TEXT("Death.HoldAtSeconds")});
		Cases.Add({TEXT("HoldAtSeconds negative"), [](FRPGDeathConfig& R) { R.HoldAtSeconds = -1.f; }, TEXT("InvalidDeath.NotPositive"), TEXT("Death.HoldAtSeconds")});
		Cases.Add({TEXT("HoldAtSeconds nextafter ceiling"), [](FRPGDeathConfig& R) { R.HoldAtSeconds = std::nextafter(RPGBossDeathAdapters::MaxAuthoredMagnitude, std::numeric_limits<float>::infinity()); }, TEXT("InvalidDeath.AboveCeiling"), TEXT("Death.HoldAtSeconds")});
		Cases.Add({TEXT("DyingSeconds zero"), [](FRPGDeathConfig& R) { R.DyingSeconds = 0.f; }, TEXT("InvalidDeath.NotPositive"), TEXT("Death.DyingSeconds")});
		Cases.Add({TEXT("DyingSeconds negative"), [](FRPGDeathConfig& R) { R.DyingSeconds = -1.f; }, TEXT("InvalidDeath.NotPositive"), TEXT("Death.DyingSeconds")});
		Cases.Add({TEXT("DyingSeconds nextafter ceiling"), [](FRPGDeathConfig& R) { R.DyingSeconds = std::nextafter(RPGBossDeathAdapters::MaxAuthoredMagnitude, std::numeric_limits<float>::infinity()); }, TEXT("InvalidDeath.AboveCeiling"), TEXT("Death.DyingSeconds")});
		Cases.Add({TEXT("BlendInSeconds negative"), [](FRPGDeathConfig& R) { R.BlendInSeconds = -1.f; }, TEXT("InvalidDeath.Negative"), TEXT("Death.BlendInSeconds")});
		Cases.Add({TEXT("BlendInSeconds nextafter ceiling"), [](FRPGDeathConfig& R) { R.BlendInSeconds = std::nextafter(RPGBossDeathAdapters::MaxAuthoredMagnitude, std::numeric_limits<float>::infinity()); }, TEXT("InvalidDeath.AboveCeiling"), TEXT("Death.BlendInSeconds")});
		Cases.Add({TEXT("restarts negative"), [](FRPGDeathConfig& R) { R.MaxClipRestarts = -1; }, TEXT("InvalidDeath.Negative"), TEXT("Death.MaxClipRestarts")});
		Cases.Add({TEXT("restarts above ceiling"), [](FRPGDeathConfig& R) { R.MaxClipRestarts = 1000001; }, TEXT("InvalidDeath.AboveCeiling"), TEXT("Death.MaxClipRestarts")});
		Cases.Add({TEXT("restarts INT32_MAX"), [](FRPGDeathConfig& R) { R.MaxClipRestarts = std::numeric_limits<int32>::max(); }, TEXT("InvalidDeath.AboveCeiling"), TEXT("Death.MaxClipRestarts")});
		Cases.Add({TEXT("PackDeathAbilityClassName None"), [](FRPGDeathConfig& R) { R.PackDeathAbilityClassName = NAME_None; }, TEXT("InvalidDependency.Missing"), TEXT("Death.PackDeathAbilityClassName")});
		Cases.Add({TEXT("PackDeathAbilityClassName mixed-case None"), [](FRPGDeathConfig& R) { R.PackDeathAbilityClassName = TEXT("nOnE"); }, TEXT("InvalidDependency.Missing"), TEXT("Death.PackDeathAbilityClassName")});
		Cases.Add({TEXT("PackDeathAbilityClassName space"), [](FRPGDeathConfig& R) { R.PackDeathAbilityClassName = TEXT("Ability A"); }, TEXT("InvalidDependency.Malformed"), TEXT("Death.PackDeathAbilityClassName")});
		Cases.Add({TEXT("PackDeathAbilityClassName tab"), [](FRPGDeathConfig& R) { R.PackDeathAbilityClassName = TEXT("Ability\tA"); }, TEXT("InvalidDependency.Malformed"), TEXT("Death.PackDeathAbilityClassName")});
		Cases.Add({TEXT("PackDeathAbilityClassName control"), [](FRPGDeathConfig& R) { R.PackDeathAbilityClassName = FName(*FString::Printf(TEXT("Ability%cA"), static_cast<TCHAR>(0x7f))); }, TEXT("InvalidDependency.Malformed"), TEXT("Death.PackDeathAbilityClassName")});
		Cases.Add({TEXT("PackDeathMontagesName None"), [](FRPGDeathConfig& R) { R.PackDeathMontagesName = NAME_None; }, TEXT("InvalidDependency.Missing"), TEXT("Death.PackDeathMontagesName")});
		Cases.Add({TEXT("PackDeathMontagesName mixed-case None"), [](FRPGDeathConfig& R) { R.PackDeathMontagesName = TEXT("nOnE"); }, TEXT("InvalidDependency.Missing"), TEXT("Death.PackDeathMontagesName")});
		Cases.Add({TEXT("PackDeathMontagesName space"), [](FRPGDeathConfig& R) { R.PackDeathMontagesName = TEXT("Ability A"); }, TEXT("InvalidDependency.Malformed"), TEXT("Death.PackDeathMontagesName")});
		Cases.Add({TEXT("PackDeathMontagesName tab"), [](FRPGDeathConfig& R) { R.PackDeathMontagesName = TEXT("Ability\tA"); }, TEXT("InvalidDependency.Malformed"), TEXT("Death.PackDeathMontagesName")});
		Cases.Add({TEXT("PackDeathMontagesName control"), [](FRPGDeathConfig& R) { R.PackDeathMontagesName = FName(*FString::Printf(TEXT("Ability%cA"), static_cast<TCHAR>(0x7f))); }, TEXT("InvalidDependency.Malformed"), TEXT("Death.PackDeathMontagesName")});
		Cases.Add({TEXT("null DeathClip"), [](FRPGDeathConfig& R) { R.DeathClip.Reset(); }, TEXT("InvalidDependency.Missing"), TEXT("Death.DeathClip")});
		Cases.Add({TEXT("null DeathMontage"), [](FRPGDeathConfig& R) { R.DeathMontage.Reset(); }, TEXT("InvalidDependency.Missing"), TEXT("Death.DeathMontage")});
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
			Cases.Add({FString(M.Name) + TEXT(" DeathClip"), [Path](FRPGDeathConfig& R) { R.DeathClip = Clip(Path); }, TEXT("InvalidDependency.Malformed"), TEXT("Death.DeathClip")});
			Cases.Add({FString(M.Name) + TEXT(" DeathMontage"), [Path](FRPGDeathConfig& R) { R.DeathMontage = Montage(Path); }, TEXT("InvalidDependency.Malformed"), TEXT("Death.DeathMontage")});
		}
		return Cases;
	}
	bool HasError(const FRPGHydrationResult& R, const TCHAR* Token, const TCHAR* Path)
	{
		return R.Errors.ContainsByPredicate([Token, Path](const FString& E) { return E.Contains(Token) && E.Contains(Path); });
	}
	TStrongObjectPtr<URPGBossDefinition> Definition(const FRPGDeathConfig& R)
	{
		TStrongObjectPtr<URPGBossDefinition> D(NewObject<URPGBossDefinition>());
		D->Schema = 1; D->DefinitionId = TEXT("DeathFixture"); D->PresentationId = TEXT("FixtureDeath");
		D->Stats.MaxHealth = 1234.f; D->Stats.MaxPosture = 87.f;
		D->Stats.PostureRegenDelay = 2.f; D->Stats.PostureRegenRate = 3.f;
		D->Death = R;
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

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGDeathAssignTest, "OneBossFight.Binding.Death.Assign", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGDeathAssignTest::RunTest(const FString& Parameters)
{
	using namespace DeathTests;
	FWorldScope Scope;
	AActor* Owner = Scope.Spawn();
	if (!TestNotNull(TEXT("owner"), Owner)) { return false; }
	TStrongObjectPtr<URPGBossDeath> Death(NewObject<URPGBossDeath>(Owner, TEXT("RPGBossDeath")));
	TStrongObjectPtr<URPGBossPosture> Other(NewObject<URPGBossPosture>(Owner));
	const float OtherBefore = Other->PostureMax;
	const auto Before = Owned(Owner);
	const FRuntime Runtime(*Death);
	const FRPGComponentPlan Plan = RPGBossDeathAdapters::MakeDeathPlan();
	TestTrue(TEXT("exact class/name and twelve exact paths, without duplicates"), Plan.Class == URPGBossDeath::StaticClass()
		&& Plan.InstanceName == FName(TEXT("RPGBossDeath")) && Plan.RequiredFields == Paths());
	if (!TestTrue(TEXT("plan callback exists"), static_cast<bool>(Plan.Configure))) { return false; }
	FString Error = TEXT("stale diagnostic");
	TestTrue(TEXT("callback copies all twelve nondefault fields"), Plan.Configure(*Death, Config(RecordA()), Error) && Error.IsEmpty() && Same(Read(*Death), RecordA()));
	TestTrue(TEXT("runtime, lifecycle, owner component set and unrelated component unchanged"), Runtime.SameAs(FRuntime(*Death))
		&& SameOwned(Before, Owned(Owner)) && Other->PostureMax == OtherBefore && Death->GetOwner() == Owner && Death->GetOuter() == Owner);
	TestTrue(TEXT("second call writes another complete record"), Plan.Configure(*Death, Config(RecordB()), Error) && Same(Read(*Death), RecordB()) && Runtime.SameAs(FRuntime(*Death)));
	AddInfo(TEXT("Twelve authored fields assigned; no native death/playback/remains proof."));
	return true;
}




IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGDeathValidationTest, "OneBossFight.Binding.Death.Validation", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGDeathValidationTest::RunTest(const FString& Parameters)
{
	using namespace DeathTests;
	FWorldScope Scope;
	AActor* Owner = Scope.Spawn();
	if (!TestNotNull(TEXT("owner"), Owner)) { return false; }
	TStrongObjectPtr<URPGBossDeath> Death(NewObject<URPGBossDeath>(Owner));
	const auto Before = Read(*Death);
	const FRuntime Runtime(*Death);
	const auto Components = Owned(Owner);
	for (const FBad& Case : BadCases())
	{
		auto R = RecordA();
		Case.Mutate(R);
		FString Error;
		TestFalse(Case.Name + TEXT(": validator refuses"), RPGBossDeathAdapters::ValidateDeath(R, Error));
		TestTrue(Case.Name + TEXT(": named token/field"), Error.StartsWith(Case.Token) && Error.Contains(Case.Path));
		TestFalse(Case.Name + TEXT(": callback refuses"), RPGBossDeathAdapters::ConfigureDeath(*Death, Config(R), Error));
		TestTrue(Case.Name + TEXT(": no partial write"), Same(Read(*Death), Before) && Runtime.SameAs(FRuntime(*Death)) && SameOwned(Components, Owned(Owner)));
	}
	TArray<FRPGDeathConfig> Valid{RecordA(), RecordB(), FRPGDeathConfig()};
	{ auto R = RecordA(); R.PackPollSeconds = RPGBossDeathAdapters::MaxAuthoredMagnitude; Valid.Add(R); }
	{ auto R = RecordA(); R.PackEndTimeMultiplier = RPGBossDeathAdapters::MaxAuthoredMagnitude; Valid.Add(R); }
	{ auto R = RecordA(); R.HoldAtSeconds = RPGBossDeathAdapters::MaxAuthoredMagnitude; Valid.Add(R); }
	{ auto R = RecordA(); R.DyingSeconds = RPGBossDeathAdapters::MaxAuthoredMagnitude; Valid.Add(R); }
	{ auto R = RecordA(); R.BlendInSeconds = RPGBossDeathAdapters::MaxAuthoredMagnitude; Valid.Add(R); }

	{ auto R = RecordA(); R.MaxClipRestarts = 1000000; Valid.Add(R); }
	{ auto R = RecordA(); R.bGuardPackDeath = false; Valid.Add(R); }
	for (const auto& R : Valid)
	{
		FString Error = TEXT("stale");
		TestTrue(TEXT("both modes/guards/off states/sub-editor floors/inclusive ceilings valid"), RPGBossDeathAdapters::ValidateDeath(R, Error) && Error.IsEmpty()
			&& RPGBossDeathAdapters::ConfigureDeath(*Death, Config(R), Error) && Same(Read(*Death), R) && Runtime.SameAs(FRuntime(*Death)));
	}
	auto First = [this](const FRPGDeathConfig& R, const TCHAR* Token, const TCHAR* Field)
	{
		FString E;
		TestFalse(TEXT("multi-invalid refusal"), RPGBossDeathAdapters::ValidateDeath(R, E));
		TestTrue(TEXT("first error order"), E.StartsWith(Token) && E.Contains(Field));
	};
	auto R = RecordA();
	R.DeathMode = static_cast<ERPGBossDeathMode>(255); R.BlendInSeconds = std::numeric_limits<float>::quiet_NaN();
	First(R, TEXT("InvalidDeath.NotFinite"), TEXT("Death.BlendInSeconds"));
	R = RecordA(); R.PackPollSeconds = 0.f; R.DeathMode = static_cast<ERPGBossDeathMode>(255);
	First(R, TEXT("InvalidDeath.BadMode"), TEXT("Death.DeathMode"));
	R = RecordA(); R.PackPollSeconds = std::numeric_limits<float>::infinity(); R.PackEndTimeMultiplier = std::numeric_limits<float>::quiet_NaN();
	First(R, TEXT("InvalidDeath.NotFinite"), TEXT("Death.PackPollSeconds"));
	R = RecordA(); R.MaxClipRestarts = -1; R.PackDeathAbilityClassName = NAME_None;
	First(R, TEXT("InvalidDeath.Negative"), TEXT("Death.MaxClipRestarts"));
	R = RecordA(); R.PackDeathMontagesName = NAME_None; R.DeathClip.Reset();
	First(R, TEXT("InvalidDependency.Missing"), TEXT("Death.PackDeathMontagesName"));
	R = RecordA(); R.DeathClip.Reset(); R.DeathMontage.Reset();
	First(R, TEXT("InvalidDependency.Missing"), TEXT("Death.DeathClip"));
	R = RecordB(); R.DeathClip.Reset();
	First(R, TEXT("InvalidDependency.Missing"), TEXT("Death.DeathClip")); // uniform both-path contract even PackMontage
	R = RecordA(); R.DeathMontage.Reset();
	First(R, TEXT("InvalidDependency.Missing"), TEXT("Death.DeathMontage")); // uniform both-path contract even OwnClip
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGDeathIsolationTest, "OneBossFight.Binding.Death.Isolation", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGDeathIsolationTest::RunTest(const FString& Parameters)
{
	using namespace DeathTests;
	FWorldScope Scope;
	AActor* OwnerA = Scope.Spawn(); AActor* OwnerB = Scope.Spawn();
	if (!TestTrue(TEXT("two owners"), OwnerA && OwnerB)) { return false; }
	TStrongObjectPtr<URPGBossDeath> A(NewObject<URPGBossDeath>(OwnerA));
	TStrongObjectPtr<URPGBossDeath> B(NewObject<URPGBossDeath>(OwnerB));
	TStrongObjectPtr<URPGBossDeath> Untouched(NewObject<URPGBossDeath>(OwnerB));
	TStrongObjectPtr<URPGBossBleed> Other(NewObject<URPGBossBleed>(OwnerA));
	const auto Original = Read(*Untouched); const auto Default = Read(*GetDefault<URPGBossDeath>());
	const FRuntime RuntimeA(*A), RuntimeB(*B);
	const auto OwnedA = Owned(OwnerA), OwnedB = Owned(OwnerB);
	const float BleedBefore = Other->InitialThreshold;
	auto Input = Config(RecordA()); FString Error;
	TestTrue(TEXT("A assignment"), RPGBossDeathAdapters::ConfigureDeath(*A, Input, Error));
	Input.Death.DeathMontage = Montage(MakePath(TEXT("/SyntheticMount/Changed"), TEXT("Montage")));
	TestTrue(TEXT("native soft reference owns independent value"), Same(Read(*A), RecordA()));
	Input.Death = RecordB();
	TestTrue(TEXT("input is a value snapshot"), Same(Read(*A), RecordA()));
	TestTrue(TEXT("B assignment"), RPGBossDeathAdapters::ConfigureDeath(*B, Input, Error));
	auto Invalid = RecordB(); Invalid.DeathMontage.Reset();
	TestFalse(TEXT("late invalid input refuses on configured A"), RPGBossDeathAdapters::ConfigureDeath(*A, Config(Invalid), Error));
	TestTrue(TEXT("owners and unrelated values fully isolated"), Same(Read(*A), RecordA()) && Same(Read(*B), RecordB())
		&& Same(Read(*Untouched), Original) && Same(Read(*GetDefault<URPGBossDeath>()), Default)
		&& RuntimeA.SameAs(FRuntime(*A)) && RuntimeB.SameAs(FRuntime(*B))
		&& SameOwned(OwnedA, Owned(OwnerA)) && SameOwned(OwnedB, Owned(OwnerB)) && Other->InitialThreshold == BleedBefore);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGDeathRejectionsTest, "OneBossFight.Binding.Death.Rejections", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGDeathRejectionsTest::RunTest(const FString& Parameters)
{
	using namespace DeathTests;
	FWorldScope Scope;
	AActor* Owner = Scope.Spawn();
	if (!TestNotNull(TEXT("owner"), Owner)) { return false; }
	auto Check = [this](UActorComponent& C, const TCHAR* Token)
	{
		const bool Registered = C.IsRegistered(), Begun = C.HasBegunPlay();
		const URPGBossDeath* Death = Cast<URPGBossDeath>(&C);
		const auto Before = Death ? Read(*Death) : FRPGDeathConfig();
		FString Error;
		auto Bad = RecordA(); Bad.DeathClip.Reset();
		for (const auto& R : TArray<FRPGDeathConfig>{RecordA(), Bad})
		{
			TestFalse(TEXT("lifecycle/class rejection"), RPGBossDeathAdapters::ConfigureDeath(C, Config(R), Error));
			TestTrue(TEXT("lifecycle before invalid record; no lifecycle write"), Error.StartsWith(Token) && C.IsRegistered() == Registered && C.HasBegunPlay() == Begun);
			if (Death) { TestTrue(TEXT("no partial configuration write on lifecycle refusal"), Same(Read(*Death), Before)); }
		}
	};
	TStrongObjectPtr<USceneComponent> Wrong(NewObject<USceneComponent>(Owner));
	Check(*Wrong, TEXT("WrongComponentClass"));
	TStrongObjectPtr<URPGBossBleed> WrongNative(NewObject<URPGBossBleed>(Owner));
	Check(*WrongNative, TEXT("WrongComponentClass"));
	TStrongObjectPtr<URPGBossDeath> Registered(NewObject<URPGBossDeath>(Owner));
	Registered->RegisterComponent();
	if (!TestTrue(TEXT("fixture registered but not begun"), Registered->IsRegistered() && !Registered->HasBegunPlay())) { return false; }
	Check(*Registered, TEXT("ComponentAlreadyRegistered"));
	AActor* LateOwner = Scope.Spawn();
	if (!TestNotNull(TEXT("late owner"), LateOwner)) { return false; }
	LateOwner->DispatchBeginPlay(); // plain actor, NO Death component yet
	if (!TestTrue(TEXT("plain owner began"), LateOwner->HasActorBegunPlay())) { return false; }
	TStrongObjectPtr<URPGBossDeath> Late(NewObject<URPGBossDeath>(LateOwner));
	Check(*Late, TEXT("OwnerBegunPlay"));
	TStrongObjectPtr<URPGBossDeath> Orphan(NewObject<URPGBossDeath>(GetTransientPackage()));
	Check(*Orphan, TEXT("InvalidOwner"));
	TStrongObjectPtr<URPGBossDeath> Destroyed(NewObject<URPGBossDeath>(Owner));
	Destroyed->DestroyComponent();
	Check(*Destroyed, TEXT("InvalidComponent")); // retained object, not freed memory
	AddInfo(TEXT("ComponentBegunPlay guard source-only: no Death BeginPlay invoked. Registered and plain begun-owner fixtures do not play a death clip."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGDeathCompileTest, "OneBossFight.Binding.Death.Compile", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGDeathCompileTest::RunTest(const FString& Parameters)
{
	using namespace DeathTests;
	const auto Content = RPGCombatRegistry::Legacy(); // accepted dev-only synthetic contract
	if (!TestTrue(TEXT("synthetic content lease exists"), Content.IsValid())) { return false; }
	TSharedPtr<const FRPGParticipantConfig> Out;
	auto D = Definition(RecordA());
	auto Compile = [&Content](const URPGBossDefinition& Def, TSharedPtr<const FRPGParticipantConfig>& Output)
	{
		return RPGCombatHydration::CompileSyntheticParticipant(Def, Content, FString::ChrN(64, TEXT('b')), Output);
	};
	if (!TestTrue(TEXT("synthetic compiler positive control"), Compile(*D, Out).IsReady() && Out.IsValid())) { return false; }
	TestTrue(TEXT("all twelve typed values copied, dev-only flag, same epoch; manifest Value not parsed"), Same(Out->Death, RecordA()) && Out->bSyntheticFixture && Out->Content.Get() == Content.Get());
	D->Death = RecordB();
	TestTrue(TEXT("compiled config is immutable value snapshot"), Same(Out->Death, RecordA()));
	TestTrue(TEXT("next compile copies independent record"),Compile(*D,Out).IsReady()&&Out.IsValid()&&Same(Out->Death,RecordB()));
	D->Death.DeathMontage = Montage(MakePath(TEXT("/SyntheticMount/Changed"), TEXT("Montage")));
	TestTrue(TEXT("compiled soft reference owns an independent value"),Out.IsValid()&&Same(Out->Death,RecordB()));
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
	auto Defaults = Definition(FRPGDeathConfig());
	TestTrue(TEXT("additive defaults compile without substitution"), Compile(*Defaults, Out).IsReady() && Out.IsValid() && Same(Out->Death, FRPGDeathConfig()));
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




IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGDeathAuthoringTest, "OneBossFight.Binding.Death.Authoring", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGDeathAuthoringTest::RunTest(const FString& Parameters)
{
	using namespace DeathTests;
	const UScriptStruct* Struct = FRPGDeathConfig::StaticStruct();
	int32 Count = 0;
	for (TFieldIterator<FProperty> It(Struct); It; ++It) { ++Count; TestTrue(TEXT("editable"), It->HasAnyPropertyFlags(CPF_Edit)); }
	TestEqual(TEXT("twelve authored fields"), Count, 12);
	const FEnumProperty* Mode = CastField<FEnumProperty>(Struct->FindPropertyByName(TEXT("DeathMode")));
	const FEnumProperty* NativeMode = CastField<FEnumProperty>(URPGBossDeath::StaticClass()->FindPropertyByName(TEXT("DeathMode")));
	TestTrue(TEXT("same reflected native enum"), Mode && NativeMode && Mode->GetEnum() == NativeMode->GetEnum());
	for (const TCHAR* N : {TEXT("PackDeathAbilityClassName"), TEXT("PackDeathMontagesName")}) { TestNotNull(N, CastField<FNameProperty>(Struct->FindPropertyByName(N))); }
	for (const TCHAR* N : {TEXT("PackPollSeconds"), TEXT("PackEndTimeMultiplier"), TEXT("HoldAtSeconds"), TEXT("DyingSeconds"), TEXT("BlendInSeconds")}) { TestNotNull(N, CastField<FFloatProperty>(Struct->FindPropertyByName(N))); }
	TestNotNull(TEXT("int32 restarts"), CastField<FIntProperty>(Struct->FindPropertyByName(TEXT("MaxClipRestarts"))));
	TestNotNull(TEXT("guard bool"), CastField<FBoolProperty>(Struct->FindPropertyByName(TEXT("bGuardPackDeath"))));
	const FSoftObjectProperty* ClipProperty = CastField<FSoftObjectProperty>(Struct->FindPropertyByName(TEXT("DeathClip")));
	const FSoftObjectProperty* MontageProperty = CastField<FSoftObjectProperty>(Struct->FindPropertyByName(TEXT("DeathMontage")));
	TestTrue(TEXT("typed clip and montage"), ClipProperty && ClipProperty->PropertyClass == UAnimSequence::StaticClass() && MontageProperty && MontageProperty->PropertyClass == UAnimMontage::StaticClass());
	const FStructProperty* Property = CastField<FStructProperty>(URPGBossDefinition::StaticClass()->FindPropertyByName(TEXT("Death")));
	TestTrue(TEXT("Data Asset record"), Property && Property->Struct == Struct && Property->HasAnyPropertyFlags(CPF_Edit));
	const FRPGDeathConfig Default;
	TestTrue(TEXT("all native defaults"), Same(Default, Read(*GetDefault<URPGBossDeath>())));
	TestTrue(TEXT("explicit default baseline"), Default.DeathMode == ERPGBossDeathMode::PackMontage && Default.PackDeathAbilityClassName == FName(TEXT("GA_EnemyRagdollDeath_C"))
		&& Default.PackDeathMontagesName == FName(TEXT("DeathMontages")) && Default.PackPollSeconds == 1.f && Default.PackEndTimeMultiplier == 0.f && Default.HoldAtSeconds == 3.f
		&& Default.DyingSeconds == 2.5f && Default.BlendInSeconds == 0.1f && Default.MaxClipRestarts == 8 && !Default.bGuardPackDeath
		&& Default.DeathClip.ToString().EndsWith(TEXT("/Animations/AN_Boss01_DeathLegend.AN_Boss01_DeathLegend"))
		&& Default.DeathMontage.ToString().EndsWith(TEXT("/Animations/AM_Boss01_DeathLegend.AM_Boss01_DeathLegend")));
	for (const TCHAR* N : {TEXT("LoadedClip"), TEXT("LoadedMontage"), TEXT("State"), TEXT("DeathTime"), TEXT("RestartsThisDeath"), TEXT("ClipRestartCount"), TEXT("LoadedRemainsMesh"), TEXT("bPreloaded"), TEXT("NextPackPoll")})
	{
		TestNull(FString(N) + TEXT(" not authored"), Struct->FindPropertyByName(N));
	}
	AddInfo(TEXT("Reflection/defaults only. No pack ability, death flow, clip playback, remains or serialized authoring proof."));
	return true;
}
#endif
