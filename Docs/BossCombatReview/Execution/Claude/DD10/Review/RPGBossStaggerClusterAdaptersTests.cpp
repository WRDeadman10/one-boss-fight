// Copyright Epic Games, Inc. All Rights Reserved.

#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Player/RPGBossStaggerClusterAdapters.h"
#include "Player/RPGBossStaggerPolicyAdapters.h"
#include "Player/RPGEncounterBinding.h"
#include "Player/RPGCombatCatalog.h"
#include "Player/RPGBossStagger.h"
#include "Player/RPGBossPosture.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossPhases.h"
#include "Animation/AnimMontage.h"
#include "Animation/AnimSequence.h"
#include "Animation/Skeleton.h"
#include "GameFramework/Actor.h"
#include "Engine/World.h"
#include "UObject/Class.h"
#include "UObject/UnrealType.h"
#include "UObject/SoftObjectPath.h"
#include "UObject/Package.h"
#include "UObject/StrongObjectPtr.h"

namespace StaggerClusterTests
{
	using FEpochPtr = TSharedPtr<const RPGCombatRegistry::FEpoch>;
	using FConfigPtr = TSharedPtr<const FRPGParticipantConfig>;
	static TSoftObjectPtr<UAnimMontage> MontagePtr(const FSoftObjectPath& Path)
	{
		return TSoftObjectPtr<UAnimMontage>(Path);
	}

	static TSoftObjectPtr<UAnimSequence> SequencePtr(const FSoftObjectPath& Path)
	{
		return TSoftObjectPtr<UAnimSequence>(Path);
	}

	static TSoftClassPtr<UObject> ClassPtr(const FSoftObjectPath& Path)
	{
		return TSoftClassPtr<UObject>(Path);
	}

	static FSoftObjectPath MakePath(const TCHAR* Package, const TCHAR* Asset, const TCHAR* Sub = nullptr)
	{
		const FTopLevelAssetPath Top(Package, Asset);
		return FSoftObjectPath(Top, Sub ? FString(Sub) : FString());
	}

	static FRPGParityField MakeField(const FString& FieldPath, const FString& Value)
	{
		FRPGParityField E;
		E.FieldPath = FieldPath;
		E.Type = TEXT("FString");
		E.SourcePath = TEXT("Test/Source");
		E.SourceSHA256 = FString::ChrN(64, TEXT('a'));
		E.SourceSite = TEXT("TestSite");
		E.Origin = TEXT("Config");
		E.Precedence = TEXT("100");
		E.Destination = TEXT("TestDestination");
		E.FirstRead = TEXT("Hydrate");
		E.Witness = TEXT("TestWitness");
		E.Value = Value;
		return E;
	}

	struct FClusterTestWorld
	{
		UWorld* World = nullptr;
		FClusterTestWorld()
		{
			World = UWorld::CreateWorld(EWorldType::Game, false, TEXT("StaggerClusterTestWorld"));
		}
		~FClusterTestWorld()
		{
			if (World)
			{
				World->DestroyWorld(false);
			}
		}
		AActor* SpawnOwner()
		{
			if (!World)
			{
				return nullptr;
			}
			FActorSpawnParameters P;
			return World->SpawnActor<AActor>(AActor::StaticClass(), P);
		}
	};

	static TStrongObjectPtr<URPGBossStagger> NewStagger(AActor* Owner, const TCHAR* Name)
	{
		return TStrongObjectPtr<URPGBossStagger>(NewObject<URPGBossStagger>(Owner, Name));
	}

	struct FStaggerClusterState
	{
		// 14 StaggerPolicy fields
		float StaggerSeconds = 0.f;
		float FreezeAtPosition = 0.f;
		float CriticalMultiplier = 0.f;
		float RiposteRange = 0.f;
		float RiposteConeDegrees = 0.f;
		float RiposteFacingDegrees = 0.f;
		float RiposteArmSeconds = 0.f;
		float RipostePlayerStartGap = 0.f;
		float RiposteAlignSeconds = 0.f;
		float RiposteImpactSeconds = 0.f;
		float RiposteBaseDamage = 0.f;
		float CooldownSeconds = 0.f;
		float GetUpRate = 0.f;
		bool bHoldPostureAtZero = false;

		// 11 StaggerProfile fields
		bool bUseClips = false;
		bool bUseRiposteClips = false;
		bool bCriticalOnEveryHit = false;
		FName HitStunAbilityClassName;
		FSoftObjectPath FallMontage;
		FSoftObjectPath GetUpMontage;
		FSoftObjectPath FallClip;
		FSoftObjectPath DownClip;
		FSoftObjectPath RipostePlayerClip;
		FSoftObjectPath RiposteBossClip;
		FSoftObjectPath ImmunityEffect;

		// Runtime getters
		bool bStaggered = false;
		bool bCriticalWindowOpen = false;
		bool bRiposteExecuting = false;

		FStaggerClusterState() = default;
		explicit FStaggerClusterState(const URPGBossStagger& S)
			: StaggerSeconds(S.StaggerSeconds)
			, FreezeAtPosition(S.FreezeAtPosition)
			, CriticalMultiplier(S.CriticalMultiplier)
			, RiposteRange(S.RiposteRange)
			, RiposteConeDegrees(S.RiposteConeDegrees)
			, RiposteFacingDegrees(S.RiposteFacingDegrees)
			, RiposteArmSeconds(S.RiposteArmSeconds)
			, RipostePlayerStartGap(S.RipostePlayerStartGap)
			, RiposteAlignSeconds(S.RiposteAlignSeconds)
			, RiposteImpactSeconds(S.RiposteImpactSeconds)
			, RiposteBaseDamage(S.RiposteBaseDamage)
			, CooldownSeconds(S.CooldownSeconds)
			, GetUpRate(S.GetUpRate)
			, bHoldPostureAtZero(S.bHoldPostureAtZero)
			, bUseClips(S.bUseClips)
			, bUseRiposteClips(S.bUseRiposteClips)
			, bCriticalOnEveryHit(S.bCriticalOnEveryHit)
			, HitStunAbilityClassName(S.HitStunAbilityClassName)
			, FallMontage(S.FallMontage.ToSoftObjectPath())
			, GetUpMontage(S.GetUpMontage.ToSoftObjectPath())
			, FallClip(S.FallClip.ToSoftObjectPath())
			, DownClip(S.DownClip.ToSoftObjectPath())
			, RipostePlayerClip(S.RipostePlayerClip.ToSoftObjectPath())
			, RiposteBossClip(S.RiposteBossClip.ToSoftObjectPath())
			, ImmunityEffect(S.ImmunityEffect.ToSoftObjectPath())
			, bStaggered(S.IsStaggered())
			, bCriticalWindowOpen(S.IsCriticalWindowOpen())
			, bRiposteExecuting(S.IsRiposteExecuting())
		{
		}

		bool PolicyEquals(const FStaggerClusterState& O) const
		{
			return StaggerSeconds == O.StaggerSeconds && FreezeAtPosition == O.FreezeAtPosition
				&& CriticalMultiplier == O.CriticalMultiplier && RiposteRange == O.RiposteRange
				&& RiposteConeDegrees == O.RiposteConeDegrees && RiposteFacingDegrees == O.RiposteFacingDegrees
				&& RiposteArmSeconds == O.RiposteArmSeconds && RipostePlayerStartGap == O.RipostePlayerStartGap
				&& RiposteAlignSeconds == O.RiposteAlignSeconds && RiposteImpactSeconds == O.RiposteImpactSeconds
				&& RiposteBaseDamage == O.RiposteBaseDamage && CooldownSeconds == O.CooldownSeconds
				&& GetUpRate == O.GetUpRate && bHoldPostureAtZero == O.bHoldPostureAtZero;
		}

		bool ProfileEquals(const FStaggerClusterState& O) const
		{
			return bUseClips == O.bUseClips && bUseRiposteClips == O.bUseRiposteClips
				&& bCriticalOnEveryHit == O.bCriticalOnEveryHit
				&& HitStunAbilityClassName == O.HitStunAbilityClassName
				&& FallMontage == O.FallMontage && GetUpMontage == O.GetUpMontage
				&& FallClip == O.FallClip && DownClip == O.DownClip
				&& RipostePlayerClip == O.RipostePlayerClip && RiposteBossClip == O.RiposteBossClip
				&& ImmunityEffect == O.ImmunityEffect;
		}

		bool RuntimeEquals(const FStaggerClusterState& O) const
		{
			return bStaggered == O.bStaggered
				&& bCriticalWindowOpen == O.bCriticalWindowOpen
				&& bRiposteExecuting == O.bRiposteExecuting;
		}

		bool operator==(const FStaggerClusterState& O) const
		{
			return PolicyEquals(O) && ProfileEquals(O) && RuntimeEquals(O);
		}
	};

	static FRPGParticipantConfig ConfigA()
	{
		FRPGParticipantConfig C;
		// 14 Policy fields (all differ from native defaults)
		C.StaggerPolicy.StaggerSeconds = 4.25f;
		C.StaggerPolicy.FreezeAtPosition = 2.1f;
		C.StaggerPolicy.CriticalMultiplier = 3.5f;
		C.StaggerPolicy.RiposteRange = 220.f;
		C.StaggerPolicy.RiposteConeDegrees = 90.f;
		C.StaggerPolicy.RiposteFacingDegrees = 85.f;
		C.StaggerPolicy.RiposteArmSeconds = 1.75f;
		C.StaggerPolicy.RipostePlayerStartGap = 175.f;
		C.StaggerPolicy.RiposteAlignSeconds = 0.45f;
		C.StaggerPolicy.RiposteImpactSeconds = 1.15f;
		C.StaggerPolicy.RiposteBaseDamage = 65.f;
		C.StaggerPolicy.CooldownSeconds = 5.f;
		C.StaggerPolicy.GetUpRate = 0.85f;
		C.StaggerPolicy.bHoldPostureAtZero = false;

		// 11 Profile fields (all differ from native defaults: bUseClips=false, bUseRiposteClips=false, bCriticalOnEveryHit=true)
		C.StaggerProfile.bUseClips = false;
		C.StaggerProfile.bUseRiposteClips = false;
		C.StaggerProfile.bCriticalOnEveryHit = true;
		C.StaggerProfile.HitStunAbilityClassName = TEXT("GA_Custom_HitStun_C");
		C.StaggerProfile.FallMontage = MontagePtr(MakePath(TEXT("/SyntheticMount/Stagger/AM_CustomFall"), TEXT("AM_CustomFall")));
		C.StaggerProfile.GetUpMontage = MontagePtr(MakePath(TEXT("/SyntheticMount/Stagger/AM_CustomGetUp"), TEXT("AM_CustomGetUp")));
		C.StaggerProfile.FallClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Stagger/AN_CustomFall"), TEXT("AN_CustomFall")));
		C.StaggerProfile.DownClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Stagger/AN_CustomDown"), TEXT("AN_CustomDown")));
		C.StaggerProfile.RipostePlayerClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Stagger/AN_CustomRipP"), TEXT("AN_CustomRipP")));
		C.StaggerProfile.RiposteBossClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Stagger/AN_CustomRipB"), TEXT("AN_CustomRipB")));
		C.StaggerProfile.ImmunityEffect = ClassPtr(MakePath(TEXT("/SyntheticMount/Stagger/GE_CustomImmune"), TEXT("GE_CustomImmune_C")));

		return C;
	}

	static FRPGParticipantConfig ConfigB()
	{
		FRPGParticipantConfig C;
		// Non-default policy
		C.StaggerPolicy.StaggerSeconds = 3.0f;
		C.StaggerPolicy.FreezeAtPosition = 1.5f;
		C.StaggerPolicy.CriticalMultiplier = 2.0f;
		C.StaggerPolicy.RiposteRange = 180.f;
		C.StaggerPolicy.RiposteConeDegrees = 60.f;
		C.StaggerPolicy.RiposteFacingDegrees = 60.f;
		C.StaggerPolicy.RiposteArmSeconds = 1.0f;
		C.StaggerPolicy.RipostePlayerStartGap = 120.f;
		C.StaggerPolicy.RiposteAlignSeconds = 0.25f;
		C.StaggerPolicy.RiposteImpactSeconds = 0.75f;
		C.StaggerPolicy.RiposteBaseDamage = 40.f;
		C.StaggerPolicy.CooldownSeconds = 4.0f;
		C.StaggerPolicy.GetUpRate = 1.2f;
		C.StaggerPolicy.bHoldPostureAtZero = true;

		// Profile in clip mode: bUseClips=true, bUseRiposteClips=true, bCriticalOnEveryHit=false
		C.StaggerProfile.bUseClips = true;
		C.StaggerProfile.bUseRiposteClips = true;
		C.StaggerProfile.bCriticalOnEveryHit = false;
		C.StaggerProfile.HitStunAbilityClassName = TEXT("GA_B_HitStun_C");
		C.StaggerProfile.FallMontage = MontagePtr(FSoftObjectPath()); // optional in clip mode
		C.StaggerProfile.GetUpMontage = MontagePtr(FSoftObjectPath()); // optional in clip mode
		C.StaggerProfile.FallClip = SequencePtr(MakePath(TEXT("/SyntheticMount/StaggerB/AN_BFall"), TEXT("AN_BFall")));
		C.StaggerProfile.DownClip = SequencePtr(MakePath(TEXT("/SyntheticMount/StaggerB/AN_BDown"), TEXT("AN_BDown")));
		C.StaggerProfile.RipostePlayerClip = SequencePtr(MakePath(TEXT("/SyntheticMount/StaggerB/AN_BRipP"), TEXT("AN_BRipP")));
		C.StaggerProfile.RiposteBossClip = SequencePtr(MakePath(TEXT("/SyntheticMount/StaggerB/AN_BRipB"), TEXT("AN_BRipB")));
		C.StaggerProfile.ImmunityEffect = ClassPtr(MakePath(TEXT("/SyntheticMount/StaggerB/GE_BImmune"), TEXT("GE_BImmune_C")));

		return C;
	}

	static void ArmDistinctStart(URPGBossStagger& S)
	{
		S.StaggerSeconds = 12.f;
		S.FreezeAtPosition = 6.f;
		S.CriticalMultiplier = 9.f;
		S.RiposteRange = 500.f;
		S.RiposteConeDegrees = 45.f;
		S.RiposteFacingDegrees = 45.f;
		S.RiposteArmSeconds = 3.f;
		S.RipostePlayerStartGap = 300.f;
		S.RiposteAlignSeconds = 1.f;
		S.RiposteImpactSeconds = 2.f;
		S.RiposteBaseDamage = 100.f;
		S.CooldownSeconds = 15.f;
		S.GetUpRate = 2.5f;

		// Inverted from ConfigA (which has false, false, false, true)
		S.bHoldPostureAtZero = true;
		S.bUseClips = true;
		S.bUseRiposteClips = true;
		S.bCriticalOnEveryHit = false;

		S.HitStunAbilityClassName = TEXT("GA_Start_HitStun_C");
		S.FallMontage = MontagePtr(MakePath(TEXT("/SyntheticMount/Start/AM_StartFall"), TEXT("AM_StartFall")));
		S.GetUpMontage = MontagePtr(MakePath(TEXT("/SyntheticMount/Start/AM_StartGetUp"), TEXT("AM_StartGetUp")));
		S.FallClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Start/AN_StartFall"), TEXT("AN_StartFall")));
		S.DownClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Start/AN_StartDown"), TEXT("AN_StartDown")));
		S.RipostePlayerClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Start/AN_StartRipP"), TEXT("AN_StartRipP")));
		S.RiposteBossClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Start/AN_StartRipB"), TEXT("AN_StartRipB")));
		S.ImmunityEffect = ClassPtr(MakePath(TEXT("/SyntheticMount/Start/GE_StartImmune"), TEXT("GE_StartImmune_C")));
	}

	static TStrongObjectPtr<URPGBossDefinition> MakeDefinition(const FRPGParticipantConfig& C)
	{
		TStrongObjectPtr<URPGBossDefinition> Definition(NewObject<URPGBossDefinition>());
		Definition->DefinitionId = TEXT("Synthetic");
		Definition->PresentationId = TEXT("SyntheticLook");
		Definition->Stats.MaxHealth = 3500.f;
		Definition->Stats.MaxPosture = 73.5f;
		Definition->Stats.PostureRegenDelay = 4.25f;
		Definition->Stats.PostureRegenRate = 9.75f;
		Definition->EncounterPolicy.GateRadius = 200.f;
		Definition->EncounterPolicy.bResetOnPlayerRespawn = true;
		Definition->StaggerPolicy = C.StaggerPolicy;
		Definition->PhaseFlow = C.PhaseFlow;
		Definition->Fireball = C.Fireball;
		Definition->PhaseDependencies = C.PhaseDependencies;
		Definition->StaggerProfile = C.StaggerProfile;

		if (C.Phases.Num() > 0)
		{
			Definition->Phases = C.Phases;
		}
		else
		{
			FRPGPhaseConfig P1;
			P1.PhaseId = TEXT("PhaseOne");
			P1.EntryHealthFraction = 1.0f;
			P1.SpeedMultiplier = 1.0f;
			P1.RateMultiplier = 1.0f;
			P1.AttackMultiplier = 1.0f;
			Definition->Phases.Add(P1);
		}

		Definition->Fields.Add(MakeField(RPGBossStaggerClusterAdapters::FieldHitStunAbilityClassName, TEXT("synthetic")));
		Definition->Fields.Add(MakeField(RPGBossStaggerClusterAdapters::FieldImmunityEffect, TEXT("synthetic")));

		return Definition;
	}

	static bool AnyErrorContains(const FRPGHydrationResult& Result, const TCHAR* Needle)
	{
		for (const FString& E : Result.Errors)
		{
			if (E.Contains(Needle))
			{
				return true;
			}
		}
		return false;
	}

	static FRPGHydrationResult CompileSynthetic(
		const URPGBossDefinition& Definition,
		const FEpochPtr& Content,
		FConfigPtr& OutConfig,
		const FString& ExpectedManifestHash = FString::ChrN(64, TEXT('b')))
	{
		return RPGCombatHydration::CompileSyntheticParticipant(
			Definition,
			Content,
			ExpectedManifestHash,
			OutConfig);
	}
}

// --------------------------------------------------------------------------------------------------
// 1. Assign Test
// --------------------------------------------------------------------------------------------------
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGStaggerClusterAssignTest, "OneBossFight.Binding.StaggerCluster.Assign",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGStaggerClusterAssignTest::RunTest(const FString& Parameters)
{
	using namespace StaggerClusterTests;
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
	const int32 OwnedComponentsBefore = Owner->GetComponents().Num();

	TStrongObjectPtr<URPGBossStagger> Stagger = NewStagger(Owner, TEXT("StaggerComp"));
	if (!TestNotNull(TEXT("stagger component"), Stagger.Get()))
	{
		return false;
	}
	ArmDistinctStart(*Stagger);
	const FStaggerClusterState Before(*Stagger);

	// Plan identity
	const FRPGComponentPlan Plan = RPGBossStaggerClusterAdapters::MakeStaggerClusterPlan();
	TestTrue(TEXT("plan target class is URPGBossStagger"), Plan.Class == URPGBossStagger::StaticClass());
	TestTrue(TEXT("plan legacy instance name matches"), Plan.InstanceName == FName(TEXT("RPGBossStagger")));
	TestTrue(TEXT("plan has 25 required fields"), Plan.RequiredFields.Num() == 25);
	TestTrue(TEXT("plan callback set"), (bool)Plan.Configure);

	// Verify all 25 fields of ConfigA differ from native defaults
	{
		const URPGBossStagger* CDO = GetDefault<URPGBossStagger>();
		const FRPGParticipantConfig CA = ConfigA();
		TestTrue(TEXT("CA StaggerSeconds differs"), CA.StaggerPolicy.StaggerSeconds != CDO->StaggerSeconds);
		TestTrue(TEXT("CA FreezeAtPosition differs"), CA.StaggerPolicy.FreezeAtPosition != CDO->FreezeAtPosition);
		TestTrue(TEXT("CA CriticalMultiplier differs"), CA.StaggerPolicy.CriticalMultiplier != CDO->CriticalMultiplier);
		TestTrue(TEXT("CA RiposteRange differs"), CA.StaggerPolicy.RiposteRange != CDO->RiposteRange);
		TestTrue(TEXT("CA RiposteConeDegrees differs"), CA.StaggerPolicy.RiposteConeDegrees != CDO->RiposteConeDegrees);
		TestTrue(TEXT("CA RiposteFacingDegrees differs"), CA.StaggerPolicy.RiposteFacingDegrees != CDO->RiposteFacingDegrees);
		TestTrue(TEXT("CA RiposteArmSeconds differs"), CA.StaggerPolicy.RiposteArmSeconds != CDO->RiposteArmSeconds);
		TestTrue(TEXT("CA RipostePlayerStartGap differs"), CA.StaggerPolicy.RipostePlayerStartGap != CDO->RipostePlayerStartGap);
		TestTrue(TEXT("CA RiposteAlignSeconds differs"), CA.StaggerPolicy.RiposteAlignSeconds != CDO->RiposteAlignSeconds);
		TestTrue(TEXT("CA RiposteImpactSeconds differs"), CA.StaggerPolicy.RiposteImpactSeconds != CDO->RiposteImpactSeconds);
		TestTrue(TEXT("CA RiposteBaseDamage differs"), CA.StaggerPolicy.RiposteBaseDamage != CDO->RiposteBaseDamage);
		TestTrue(TEXT("CA CooldownSeconds differs"), CA.StaggerPolicy.CooldownSeconds != CDO->CooldownSeconds);
		TestTrue(TEXT("CA GetUpRate differs"), CA.StaggerPolicy.GetUpRate != CDO->GetUpRate);
		TestTrue(TEXT("CA bHoldPostureAtZero differs"), CA.StaggerPolicy.bHoldPostureAtZero != CDO->bHoldPostureAtZero);
		TestTrue(TEXT("CA bUseClips differs"), CA.StaggerProfile.bUseClips != CDO->bUseClips);
		TestTrue(TEXT("CA bUseRiposteClips differs"), CA.StaggerProfile.bUseRiposteClips != CDO->bUseRiposteClips);
		TestTrue(TEXT("CA bCriticalOnEveryHit differs"), CA.StaggerProfile.bCriticalOnEveryHit != CDO->bCriticalOnEveryHit);
		TestTrue(TEXT("CA HitStunAbilityClassName differs"), CA.StaggerProfile.HitStunAbilityClassName != CDO->HitStunAbilityClassName);
		TestTrue(TEXT("CA FallMontage differs"), CA.StaggerProfile.FallMontage.ToSoftObjectPath() != CDO->FallMontage.ToSoftObjectPath());
		TestTrue(TEXT("CA GetUpMontage differs"), CA.StaggerProfile.GetUpMontage.ToSoftObjectPath() != CDO->GetUpMontage.ToSoftObjectPath());
		TestTrue(TEXT("CA FallClip differs"), CA.StaggerProfile.FallClip.ToSoftObjectPath() != CDO->FallClip.ToSoftObjectPath());
		TestTrue(TEXT("CA DownClip differs"), CA.StaggerProfile.DownClip.ToSoftObjectPath() != CDO->DownClip.ToSoftObjectPath());
		TestTrue(TEXT("CA RipostePlayerClip differs"), CA.StaggerProfile.RipostePlayerClip.ToSoftObjectPath() != CDO->RipostePlayerClip.ToSoftObjectPath());
		TestTrue(TEXT("CA RiposteBossClip differs"), CA.StaggerProfile.RiposteBossClip.ToSoftObjectPath() != CDO->RiposteBossClip.ToSoftObjectPath());
		TestTrue(TEXT("CA ImmunityEffect differs"), CA.StaggerProfile.ImmunityEffect.ToSoftObjectPath() != CDO->ImmunityEffect.ToSoftObjectPath());
	}

	// Config A through the plan callback, with misleading manifest Value text: only the typed records count.
	FRPGParticipantConfig Config = ConfigA();
	Config.Fields.Add(MakeField(RPGBossStaggerClusterAdapters::FieldHitStunAbilityClassName, TEXT("MisleadingClass_9999")));
	Config.Fields.Add(MakeField(RPGBossStaggerClusterAdapters::FieldImmunityEffect, TEXT("/SyntheticMount/Misleading.Misleading_C")));
	FString Error = TEXT("stale diagnostic");
	TestTrue(TEXT("callback succeeds"), Plan.Configure(*Stagger, Config, Error));
	TestTrue(TEXT("diagnostic cleared on success"), Error.IsEmpty());

	const FStaggerClusterState After(*Stagger);
	// Verify 14 policy fields assigned
	TestTrue(TEXT("StaggerSeconds assigned"), After.StaggerSeconds == 4.25f);
	TestTrue(TEXT("FreezeAtPosition assigned"), After.FreezeAtPosition == 2.1f);
	TestTrue(TEXT("CriticalMultiplier assigned"), After.CriticalMultiplier == 3.5f);
	TestTrue(TEXT("RiposteRange assigned"), After.RiposteRange == 220.f);
	TestTrue(TEXT("RiposteConeDegrees assigned"), After.RiposteConeDegrees == 90.f);
	TestTrue(TEXT("RiposteFacingDegrees assigned"), After.RiposteFacingDegrees == 85.f);
	TestTrue(TEXT("RiposteArmSeconds assigned"), After.RiposteArmSeconds == 1.75f);
	TestTrue(TEXT("RipostePlayerStartGap assigned"), After.RipostePlayerStartGap == 175.f);
	TestTrue(TEXT("RiposteAlignSeconds assigned"), After.RiposteAlignSeconds == 0.45f);
	TestTrue(TEXT("RiposteImpactSeconds assigned"), After.RiposteImpactSeconds == 1.15f);
	TestTrue(TEXT("RiposteBaseDamage assigned"), After.RiposteBaseDamage == 65.f);
	TestTrue(TEXT("CooldownSeconds assigned"), After.CooldownSeconds == 5.f);
	TestTrue(TEXT("GetUpRate assigned"), After.GetUpRate == 0.85f);
	TestTrue(TEXT("bHoldPostureAtZero assigned"), !After.bHoldPostureAtZero);

	// Verify 11 profile fields assigned
	TestTrue(TEXT("bUseClips assigned"), !After.bUseClips);
	TestTrue(TEXT("bUseRiposteClips assigned"), !After.bUseRiposteClips);
	TestTrue(TEXT("bCriticalOnEveryHit assigned"), After.bCriticalOnEveryHit);
	TestTrue(TEXT("HitStunAbilityClassName assigned, manifest ignored"), After.HitStunAbilityClassName == FName(TEXT("GA_Custom_HitStun_C")));
	TestTrue(TEXT("FallMontage assigned"), After.FallMontage == Config.StaggerProfile.FallMontage.ToSoftObjectPath());
	TestTrue(TEXT("GetUpMontage assigned"), After.GetUpMontage == Config.StaggerProfile.GetUpMontage.ToSoftObjectPath());
	TestTrue(TEXT("FallClip assigned"), After.FallClip == Config.StaggerProfile.FallClip.ToSoftObjectPath());
	TestTrue(TEXT("DownClip assigned"), After.DownClip == Config.StaggerProfile.DownClip.ToSoftObjectPath());
	TestTrue(TEXT("RipostePlayerClip assigned"), After.RipostePlayerClip == Config.StaggerProfile.RipostePlayerClip.ToSoftObjectPath());
	TestTrue(TEXT("RiposteBossClip assigned"), After.RiposteBossClip == Config.StaggerProfile.RiposteBossClip.ToSoftObjectPath());
	TestTrue(TEXT("ImmunityEffect assigned, manifest ignored"), After.ImmunityEffect == Config.StaggerProfile.ImmunityEffect.ToSoftObjectPath());

	// Per-field assertion that all 25 fields differ from start state
	TestTrue(TEXT("StaggerSeconds differs from Before"), After.StaggerSeconds != Before.StaggerSeconds);
	TestTrue(TEXT("FreezeAtPosition differs from Before"), After.FreezeAtPosition != Before.FreezeAtPosition);
	TestTrue(TEXT("CriticalMultiplier differs from Before"), After.CriticalMultiplier != Before.CriticalMultiplier);
	TestTrue(TEXT("RiposteRange differs from Before"), After.RiposteRange != Before.RiposteRange);
	TestTrue(TEXT("RiposteConeDegrees differs from Before"), After.RiposteConeDegrees != Before.RiposteConeDegrees);
	TestTrue(TEXT("RiposteFacingDegrees differs from Before"), After.RiposteFacingDegrees != Before.RiposteFacingDegrees);
	TestTrue(TEXT("RiposteArmSeconds differs from Before"), After.RiposteArmSeconds != Before.RiposteArmSeconds);
	TestTrue(TEXT("RipostePlayerStartGap differs from Before"), After.RipostePlayerStartGap != Before.RipostePlayerStartGap);
	TestTrue(TEXT("RiposteAlignSeconds differs from Before"), After.RiposteAlignSeconds != Before.RiposteAlignSeconds);
	TestTrue(TEXT("RiposteImpactSeconds differs from Before"), After.RiposteImpactSeconds != Before.RiposteImpactSeconds);
	TestTrue(TEXT("RiposteBaseDamage differs from Before"), After.RiposteBaseDamage != Before.RiposteBaseDamage);
	TestTrue(TEXT("CooldownSeconds differs from Before"), After.CooldownSeconds != Before.CooldownSeconds);
	TestTrue(TEXT("GetUpRate differs from Before"), After.GetUpRate != Before.GetUpRate);
	TestTrue(TEXT("bHoldPostureAtZero differs from Before"), After.bHoldPostureAtZero != Before.bHoldPostureAtZero);
	TestTrue(TEXT("bUseClips differs from Before"), After.bUseClips != Before.bUseClips);
	TestTrue(TEXT("bUseRiposteClips differs from Before"), After.bUseRiposteClips != Before.bUseRiposteClips);
	TestTrue(TEXT("bCriticalOnEveryHit differs from Before"), After.bCriticalOnEveryHit != Before.bCriticalOnEveryHit);
	TestTrue(TEXT("HitStunAbilityClassName differs from Before"), After.HitStunAbilityClassName != Before.HitStunAbilityClassName);
	TestTrue(TEXT("FallMontage differs from Before"), After.FallMontage != Before.FallMontage);
	TestTrue(TEXT("GetUpMontage differs from Before"), After.GetUpMontage != Before.GetUpMontage);
	TestTrue(TEXT("FallClip differs from Before"), After.FallClip != Before.FallClip);
	TestTrue(TEXT("DownClip differs from Before"), After.DownClip != Before.DownClip);
	TestTrue(TEXT("RipostePlayerClip differs from Before"), After.RipostePlayerClip != Before.RipostePlayerClip);
	TestTrue(TEXT("RiposteBossClip differs from Before"), After.RiposteBossClip != Before.RiposteBossClip);
	TestTrue(TEXT("ImmunityEffect differs from Before"), After.ImmunityEffect != Before.ImmunityEffect);

	TestTrue(TEXT("runtime state untouched"), After.RuntimeEquals(Before));
	TestFalse(TEXT("no stagger trigger"), Stagger->IsStaggered() || Stagger->IsCriticalWindowOpen() || Stagger->IsRiposteExecuting());

	// Nothing created, registered or begun
	TestFalse(TEXT("component stays unregistered"), Stagger->IsRegistered());
	TestFalse(TEXT("component did not begin play"), Stagger->HasBegunPlay());
	TestFalse(TEXT("owner did not begin play"), Owner->HasActorBegunPlay());
	TestTrue(TEXT("owner gained no component"), Owner->GetComponents().Num() == OwnedComponentsBefore);

	// Config B directly: clip mode (bUseClips=true, bUseRiposteClips=true), montages null as authored, non-default policy
	const FRPGParticipantConfig B = ConfigB();
	TestTrue(TEXT("config B succeeds"), RPGBossStaggerClusterAdapters::ConfigureStaggerCluster(*Stagger, B, Error) && Error.IsEmpty());
	const FStaggerClusterState AfterB(*Stagger);
	TestTrue(TEXT("B: StaggerSeconds"), AfterB.StaggerSeconds == 3.0f);
	TestTrue(TEXT("B: bHoldPostureAtZero"), AfterB.bHoldPostureAtZero);
	TestTrue(TEXT("B: bUseClips true"), AfterB.bUseClips);
	TestTrue(TEXT("B: bUseRiposteClips true"), AfterB.bUseRiposteClips);
	TestFalse(TEXT("B: bCriticalOnEveryHit false"), AfterB.bCriticalOnEveryHit);
	TestTrue(TEXT("B: HitStunAbilityClassName"), AfterB.HitStunAbilityClassName == FName(TEXT("GA_B_HitStun_C")));
	TestTrue(TEXT("B: FallMontage null"), AfterB.FallMontage.IsNull());
	TestTrue(TEXT("B: GetUpMontage null"), AfterB.GetUpMontage.IsNull());
	TestTrue(TEXT("B: FallClip assigned"), AfterB.FallClip == B.StaggerProfile.FallClip.ToSoftObjectPath());
	TestTrue(TEXT("B: DownClip assigned"), AfterB.DownClip == B.StaggerProfile.DownClip.ToSoftObjectPath());
	TestTrue(TEXT("B: RipostePlayerClip assigned"), AfterB.RipostePlayerClip == B.StaggerProfile.RipostePlayerClip.ToSoftObjectPath());
	TestTrue(TEXT("B: RiposteBossClip assigned"), AfterB.RiposteBossClip == B.StaggerProfile.RiposteBossClip.ToSoftObjectPath());
	TestTrue(TEXT("B: ImmunityEffect assigned"), AfterB.ImmunityEffect == B.StaggerProfile.ImmunityEffect.ToSoftObjectPath());
	TestTrue(TEXT("B: runtime state untouched"), AfterB.RuntimeEquals(Before));

	return true;
}

// --------------------------------------------------------------------------------------------------
// 2. Validation Test
// --------------------------------------------------------------------------------------------------
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGStaggerClusterValidationTest, "OneBossFight.Binding.StaggerCluster.Validation",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGStaggerClusterValidationTest::RunTest(const FString& Parameters)
{
	using namespace StaggerClusterTests;
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
	TStrongObjectPtr<URPGBossStagger> Stagger = NewStagger(Owner, TEXT("ValidationStagger"));
	if (!TestNotNull(TEXT("stagger component"), Stagger.Get()))
	{
		return false;
	}

	auto Check = [&](const FString& Label, const FRPGParticipantConfig& C, const TCHAR* ExpectedToken, const FString& ExpectedField)
	{
		FString Error = TEXT("stale");
		const bool bOk = RPGBossStaggerClusterAdapters::ValidateStaggerCluster(C, Error);
		if (ExpectedToken == nullptr)
		{
			TestTrue(FString::Printf(TEXT("%s: valid"), *Label), bOk && Error.IsEmpty());
		}
		else
		{
			TestFalse(FString::Printf(TEXT("%s: rejected"), *Label), bOk);
			TestTrue(FString::Printf(TEXT("%s: named %s (got '%s')"), *Label, ExpectedToken, *Error), Error.StartsWith(ExpectedToken));
			if (!ExpectedField.IsEmpty())
			{
				TestTrue(FString::Printf(TEXT("%s: named field %s"), *Label, *ExpectedField), Error.Contains(ExpectedField));
			}

			// Atomic rejection: ConfigureStaggerCluster must refuse and not mutate component
			ArmDistinctStart(*Stagger);
			const FStaggerClusterState Before(*Stagger);
			FString ConfigError = TEXT("stale");
			TestFalse(FString::Printf(TEXT("%s: config refused"), *Label), RPGBossStaggerClusterAdapters::ConfigureStaggerCluster(*Stagger, C, ConfigError));
			TestTrue(FString::Printf(TEXT("%s: no mutation on failure"), *Label), FStaggerClusterState(*Stagger) == Before);
		}
	};

	// 1. HitStunAbilityClassName None
	{
		FRPGParticipantConfig C = ConfigA();
		C.StaggerProfile.HitStunAbilityClassName = NAME_None;
		Check(TEXT("HitStun class None"), C, TEXT("InvalidStaggerProfile.NoHitStunClass"), RPGBossStaggerClusterAdapters::FieldHitStunAbilityClassName);
	}

	// 2. Both values of bCriticalOnEveryHit valid
	{
		FRPGParticipantConfig C1 = ConfigA();
		C1.StaggerProfile.bCriticalOnEveryHit = true;
		Check(TEXT("bCriticalOnEveryHit true"), C1, nullptr, FString());
		FRPGParticipantConfig C2 = ConfigA();
		C2.StaggerProfile.bCriticalOnEveryHit = false;
		Check(TEXT("bCriticalOnEveryHit false"), C2, nullptr, FString());
	}

	// 3. Mode combinations: bUseClips x bUseRiposteClips (fresh config instances built without lvalue copy)
	{
		// True x True: all clips required, montages optional
		FRPGParticipantConfig C = ConfigA();
		C.StaggerProfile.bUseClips = true;
		C.StaggerProfile.bUseRiposteClips = true;
		C.StaggerProfile.FallClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Stagger/AN_FC"), TEXT("AN_FC")));
		C.StaggerProfile.DownClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Stagger/AN_DC"), TEXT("AN_DC")));
		C.StaggerProfile.RipostePlayerClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Stagger/AN_RP"), TEXT("AN_RP")));
		C.StaggerProfile.RiposteBossClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Stagger/AN_RB"), TEXT("AN_RB")));
		C.StaggerProfile.FallMontage = MontagePtr(FSoftObjectPath()); // optional
		C.StaggerProfile.GetUpMontage = MontagePtr(FSoftObjectPath()); // optional
		Check(TEXT("True x True: montages optional"), C, nullptr, FString());

		FRPGParticipantConfig CMissingClip = ConfigA();
		CMissingClip.StaggerProfile.bUseClips = true;
		CMissingClip.StaggerProfile.bUseRiposteClips = true;
		CMissingClip.StaggerProfile.FallClip = SequencePtr(FSoftObjectPath()); // required
		CMissingClip.StaggerProfile.DownClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Stagger/AN_DC"), TEXT("AN_DC")));
		CMissingClip.StaggerProfile.RipostePlayerClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Stagger/AN_RP"), TEXT("AN_RP")));
		CMissingClip.StaggerProfile.RiposteBossClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Stagger/AN_RB"), TEXT("AN_RB")));
		CMissingClip.StaggerProfile.FallMontage = MontagePtr(FSoftObjectPath()); // optional
		CMissingClip.StaggerProfile.GetUpMontage = MontagePtr(FSoftObjectPath()); // optional
		Check(TEXT("True x True: FallClip missing"), CMissingClip, TEXT("InvalidDependency.Missing"), RPGBossStaggerClusterAdapters::FieldFallClip);
	}
	{
		// True x False: fall/down clip required, riposte clips optional
		FRPGParticipantConfig C = ConfigA();
		C.StaggerProfile.bUseClips = true;
		C.StaggerProfile.bUseRiposteClips = false;
		C.StaggerProfile.FallClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Stagger/AN_FC"), TEXT("AN_FC")));
		C.StaggerProfile.DownClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Stagger/AN_DC"), TEXT("AN_DC")));
		C.StaggerProfile.RipostePlayerClip = SequencePtr(FSoftObjectPath()); // optional
		C.StaggerProfile.RiposteBossClip = SequencePtr(FSoftObjectPath());   // optional
		Check(TEXT("True x False: riposte clips optional"), C, nullptr, FString());

		FRPGParticipantConfig CMissingDown = ConfigA();
		CMissingDown.StaggerProfile.bUseClips = true;
		CMissingDown.StaggerProfile.bUseRiposteClips = false;
		CMissingDown.StaggerProfile.FallClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Stagger/AN_FC"), TEXT("AN_FC")));
		CMissingDown.StaggerProfile.DownClip = SequencePtr(FSoftObjectPath()); // required
		CMissingDown.StaggerProfile.RipostePlayerClip = SequencePtr(FSoftObjectPath()); // optional
		CMissingDown.StaggerProfile.RiposteBossClip = SequencePtr(FSoftObjectPath());   // optional
		Check(TEXT("True x False: DownClip missing"), CMissingDown, TEXT("InvalidDependency.Missing"), RPGBossStaggerClusterAdapters::FieldDownClip);
	}
	{
		// False x True: montages required, fall/down clips optional, riposte clips required
		FRPGParticipantConfig C = ConfigA();
		C.StaggerProfile.bUseClips = false;
		C.StaggerProfile.bUseRiposteClips = true;
		C.StaggerProfile.FallMontage = MontagePtr(MakePath(TEXT("/SyntheticMount/Stagger/AM_CustomFall"), TEXT("AM_CustomFall")));
		C.StaggerProfile.GetUpMontage = MontagePtr(MakePath(TEXT("/SyntheticMount/Stagger/AM_CustomGetUp"), TEXT("AM_CustomGetUp")));
		C.StaggerProfile.FallClip = SequencePtr(FSoftObjectPath()); // optional
		C.StaggerProfile.DownClip = SequencePtr(FSoftObjectPath()); // optional
		C.StaggerProfile.RipostePlayerClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Stagger/AN_RP"), TEXT("AN_RP")));
		C.StaggerProfile.RiposteBossClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Stagger/AN_RB"), TEXT("AN_RB")));
		Check(TEXT("False x True: fall/down clips optional"), C, nullptr, FString());

		FRPGParticipantConfig CMissingMontage = ConfigA();
		CMissingMontage.StaggerProfile.bUseClips = false;
		CMissingMontage.StaggerProfile.bUseRiposteClips = true;
		CMissingMontage.StaggerProfile.FallMontage = MontagePtr(FSoftObjectPath()); // required
		CMissingMontage.StaggerProfile.GetUpMontage = MontagePtr(MakePath(TEXT("/SyntheticMount/Stagger/AM_CustomGetUp"), TEXT("AM_CustomGetUp")));
		CMissingMontage.StaggerProfile.FallClip = SequencePtr(FSoftObjectPath()); // optional
		CMissingMontage.StaggerProfile.DownClip = SequencePtr(FSoftObjectPath()); // optional
		CMissingMontage.StaggerProfile.RipostePlayerClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Stagger/AN_RP"), TEXT("AN_RP")));
		CMissingMontage.StaggerProfile.RiposteBossClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Stagger/AN_RB"), TEXT("AN_RB")));
		Check(TEXT("False x True: FallMontage missing"), CMissingMontage, TEXT("InvalidDependency.Missing"), RPGBossStaggerClusterAdapters::FieldFallMontage);

		FRPGParticipantConfig CMissingRiposte = ConfigA();
		CMissingRiposte.StaggerProfile.bUseClips = false;
		CMissingRiposte.StaggerProfile.bUseRiposteClips = true;
		CMissingRiposte.StaggerProfile.FallMontage = MontagePtr(MakePath(TEXT("/SyntheticMount/Stagger/AM_CustomFall"), TEXT("AM_CustomFall")));
		CMissingRiposte.StaggerProfile.GetUpMontage = MontagePtr(MakePath(TEXT("/SyntheticMount/Stagger/AM_CustomGetUp"), TEXT("AM_CustomGetUp")));
		CMissingRiposte.StaggerProfile.FallClip = SequencePtr(FSoftObjectPath()); // optional
		CMissingRiposte.StaggerProfile.DownClip = SequencePtr(FSoftObjectPath()); // optional
		CMissingRiposte.StaggerProfile.RipostePlayerClip = SequencePtr(FSoftObjectPath()); // required
		CMissingRiposte.StaggerProfile.RiposteBossClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Stagger/AN_RB"), TEXT("AN_RB")));
		Check(TEXT("False x True: RipostePlayerClip missing"), CMissingRiposte, TEXT("InvalidDependency.Missing"), RPGBossStaggerClusterAdapters::FieldRipostePlayerClip);
	}
	{
		// False x False: montages required, all clips optional
		FRPGParticipantConfig C = ConfigA();
		C.StaggerProfile.bUseClips = false;
		C.StaggerProfile.bUseRiposteClips = false;
		C.StaggerProfile.FallMontage = MontagePtr(MakePath(TEXT("/SyntheticMount/Stagger/AM_CustomFall"), TEXT("AM_CustomFall")));
		C.StaggerProfile.GetUpMontage = MontagePtr(MakePath(TEXT("/SyntheticMount/Stagger/AM_CustomGetUp"), TEXT("AM_CustomGetUp")));
		C.StaggerProfile.FallClip = SequencePtr(FSoftObjectPath());
		C.StaggerProfile.DownClip = SequencePtr(FSoftObjectPath());
		C.StaggerProfile.RipostePlayerClip = SequencePtr(FSoftObjectPath());
		C.StaggerProfile.RiposteBossClip = SequencePtr(FSoftObjectPath());
		Check(TEXT("False x False: all clips optional"), C, nullptr, FString());

		FRPGParticipantConfig CMissingGetUp = ConfigA();
		CMissingGetUp.StaggerProfile.bUseClips = false;
		CMissingGetUp.StaggerProfile.bUseRiposteClips = false;
		CMissingGetUp.StaggerProfile.FallMontage = MontagePtr(MakePath(TEXT("/SyntheticMount/Stagger/AM_CustomFall"), TEXT("AM_CustomFall")));
		CMissingGetUp.StaggerProfile.GetUpMontage = MontagePtr(FSoftObjectPath()); // required
		CMissingGetUp.StaggerProfile.FallClip = SequencePtr(FSoftObjectPath());
		CMissingGetUp.StaggerProfile.DownClip = SequencePtr(FSoftObjectPath());
		CMissingGetUp.StaggerProfile.RipostePlayerClip = SequencePtr(FSoftObjectPath());
		CMissingGetUp.StaggerProfile.RiposteBossClip = SequencePtr(FSoftObjectPath());
		Check(TEXT("False x False: GetUpMontage missing"), CMissingGetUp, TEXT("InvalidDependency.Missing"), RPGBossStaggerClusterAdapters::FieldGetUpMontage);
	}

	// 4. ImmunityEffect always required
	{
		FRPGParticipantConfig C = ConfigA();
		C.StaggerProfile.ImmunityEffect = ClassPtr(FSoftObjectPath());
		Check(TEXT("ImmunityEffect missing"), C, TEXT("InvalidDependency.Missing"), RPGBossStaggerClusterAdapters::FieldImmunityEffect);
	}

	// 5. Structural path validation for EACH of the 7 references (malformed: whitespace, control, sub-object, no leading slash, no package)
	const struct FRefTest
	{
		const TCHAR* FieldName;
		TFunction<void(FRPGParticipantConfig&, const FSoftObjectPath&)> SetPath;
	} RefTests[] = {
		{RPGBossStaggerClusterAdapters::FieldFallMontage, [](FRPGParticipantConfig& C, const FSoftObjectPath& P) { C.StaggerProfile.bUseClips = false; C.StaggerProfile.FallMontage = MontagePtr(P); }},
		{RPGBossStaggerClusterAdapters::FieldGetUpMontage, [](FRPGParticipantConfig& C, const FSoftObjectPath& P) { C.StaggerProfile.bUseClips = false; C.StaggerProfile.GetUpMontage = MontagePtr(P); }},
		{RPGBossStaggerClusterAdapters::FieldFallClip, [](FRPGParticipantConfig& C, const FSoftObjectPath& P) { C.StaggerProfile.bUseClips = true; C.StaggerProfile.FallClip = SequencePtr(P); }},
		{RPGBossStaggerClusterAdapters::FieldDownClip, [](FRPGParticipantConfig& C, const FSoftObjectPath& P) { C.StaggerProfile.bUseClips = true; C.StaggerProfile.DownClip = SequencePtr(P); }},
		{RPGBossStaggerClusterAdapters::FieldRipostePlayerClip, [](FRPGParticipantConfig& C, const FSoftObjectPath& P) { C.StaggerProfile.bUseRiposteClips = true; C.StaggerProfile.RipostePlayerClip = SequencePtr(P); }},
		{RPGBossStaggerClusterAdapters::FieldRiposteBossClip, [](FRPGParticipantConfig& C, const FSoftObjectPath& P) { C.StaggerProfile.bUseRiposteClips = true; C.StaggerProfile.RiposteBossClip = SequencePtr(P); }},
		{RPGBossStaggerClusterAdapters::FieldImmunityEffect, [](FRPGParticipantConfig& C, const FSoftObjectPath& P) { C.StaggerProfile.ImmunityEffect = ClassPtr(P); }}
	};

	for (const FRefTest& RT : RefTests)
	{
		// Malformed: whitespace
		{
			FRPGParticipantConfig C = ConfigA();
			RT.SetPath(C, MakePath(TEXT("/SyntheticMount/A B"), TEXT("Asset")));
			Check(FString::Printf(TEXT("%s: whitespace"), RT.FieldName), C, TEXT("InvalidDependency.Malformed"), RT.FieldName);
		}
		// Malformed: control character
		{
			FRPGParticipantConfig C = ConfigA();
			RT.SetPath(C, MakePath(TEXT("/SyntheticMount/A	B"), TEXT("Asset")));
			Check(FString::Printf(TEXT("%s: control character"), RT.FieldName), C, TEXT("InvalidDependency.Malformed"), RT.FieldName);
		}
		// Malformed: sub-object
		{
			FRPGParticipantConfig C = ConfigA();
			RT.SetPath(C, MakePath(TEXT("/SyntheticMount/Pkg"), TEXT("Asset"), TEXT("SubObj")));
			Check(FString::Printf(TEXT("%s: sub-object"), RT.FieldName), C, TEXT("InvalidDependency.Malformed"), RT.FieldName);
		}
		// Malformed: no leading slash
		{
			FRPGParticipantConfig C = ConfigA();
			RT.SetPath(C, MakePath(TEXT("RelativePkg"), TEXT("Asset")));
			Check(FString::Printf(TEXT("%s: no leading slash"), RT.FieldName), C, TEXT("InvalidDependency.Malformed"), RT.FieldName);
		}
		// Malformed: no package folder
		{
			FRPGParticipantConfig C = ConfigA();
			RT.SetPath(C, MakePath(TEXT("/AssetOnly"), TEXT("AssetOnly")));
			Check(FString::Printf(TEXT("%s: no package folder"), RT.FieldName), C, TEXT("InvalidDependency.Malformed"), RT.FieldName);
		}
	}

	// 6. ImmunityEffect class path checks: not a class path (ends with no _C), and /Script/ native class valid
	{
		FRPGParticipantConfig C = ConfigA();
		C.StaggerProfile.ImmunityEffect = ClassPtr(MakePath(TEXT("/SyntheticMount/Effects"), TEXT("GE_HitStunImmune")));
		Check(TEXT("ImmunityEffect not a class path"), C, TEXT("InvalidDependency.NotClassPath"), RPGBossStaggerClusterAdapters::FieldImmunityEffect);

		// /Script/ native class path: valid
		FRPGParticipantConfig CNative = ConfigA();
		CNative.StaggerProfile.ImmunityEffect = ClassPtr(MakePath(TEXT("/Script/GameplayAbilities"), TEXT("GameplayEffect")));
		Check(TEXT("ImmunityEffect native /Script/ class valid"), CNative, nullptr, FString());
	}

	// 7. Whole-cluster precedence: policy first (StaggerSeconds < 0 produces InvalidStagger.Negative per DD7)
	{
		FRPGParticipantConfig C = ConfigA();
		C.StaggerPolicy.StaggerSeconds = -1.f; // policy invalid
		C.StaggerProfile.HitStunAbilityClassName = NAME_None; // profile invalid
		Check(TEXT("precedence: policy first"), C, TEXT("InvalidStagger.Negative"), TEXT("StaggerPolicy.StaggerSeconds"));
	}

	// 8. No partial write when FIRST (policy) and LAST (profile reference) are invalid
	{
		FRPGParticipantConfig C = ConfigA();
		C.StaggerPolicy.StaggerSeconds = -5.f;
		Check(TEXT("policy first invalid: no partial write"), C, TEXT("InvalidStagger.Negative"), TEXT("StaggerPolicy.StaggerSeconds"));

		FRPGParticipantConfig CLast = ConfigA();
		CLast.StaggerProfile.ImmunityEffect = ClassPtr(FSoftObjectPath());
		Check(TEXT("profile last invalid: no partial write"), CLast, TEXT("InvalidDependency.Missing"), RPGBossStaggerClusterAdapters::FieldImmunityEffect);
	}

	return true;
}

// --------------------------------------------------------------------------------------------------
// 3. Isolation Test
// --------------------------------------------------------------------------------------------------
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGStaggerClusterIsolationTest, "OneBossFight.Binding.StaggerCluster.Isolation",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGStaggerClusterIsolationTest::RunTest(const FString& Parameters)
{
	using namespace StaggerClusterTests;
	FClusterTestWorld Scope;
	if (!TestNotNull(TEXT("test world"), Scope.World))
	{
		return false;
	}
	AActor* OwnerA = Scope.SpawnOwner();
	AActor* OwnerB = Scope.SpawnOwner();
	if (!TestTrue(TEXT("owners created"), OwnerA && OwnerB))
	{
		return false;
	}
	TStrongObjectPtr<URPGBossStagger> StaggerA = NewStagger(OwnerA, TEXT("StaggerA"));
	TStrongObjectPtr<URPGBossStagger> StaggerB = NewStagger(OwnerB, TEXT("StaggerB"));
	if (!TestTrue(TEXT("stagger components created"), StaggerA.IsValid() && StaggerB.IsValid()))
	{
		return false;
	}
	ArmDistinctStart(*StaggerA);
	ArmDistinctStart(*StaggerB);
	const FStaggerClusterState StartA(*StaggerA);
	const FStaggerClusterState StartB(*StaggerB);
	const FStaggerClusterState CDOState(*GetDefault<URPGBossStagger>());

	// Configure StaggerA with ConfigA
	FString Error;
	FRPGParticipantConfig ConfigForA = ConfigA();
	TestTrue(TEXT("configure A"), RPGBossStaggerClusterAdapters::ConfigureStaggerCluster(*StaggerA, ConfigForA, Error));
	const FStaggerClusterState ConfiguredA(*StaggerA);
	TestFalse(TEXT("StaggerA changed"), ConfiguredA == StartA);

	// A later config change does not reach the first
	ConfigForA.StaggerPolicy.StaggerSeconds = 99.f;
	ConfigForA.StaggerProfile.bCriticalOnEveryHit = false;
	ConfigForA.StaggerProfile.HitStunAbilityClassName = TEXT("MutatedAfter");
	TestTrue(TEXT("StaggerA unchanged by mutation of config object"), FStaggerClusterState(*StaggerA) == ConfiguredA);

	// Untouched component keeps its initial values
	TestTrue(TEXT("StaggerB untouched"), FStaggerClusterState(*StaggerB) == StartB);

	// CDO keeps the native constructor values
	TestTrue(TEXT("CDO untouched"), FStaggerClusterState(*GetDefault<URPGBossStagger>()) == CDOState);

	// Configure B with ConfigB()
	FRPGParticipantConfig ConfigForB = ConfigB();
	TestTrue(TEXT("configure B"), RPGBossStaggerClusterAdapters::ConfigureStaggerCluster(*StaggerB, ConfigForB, Error));
	const FStaggerClusterState ConfiguredB(*StaggerB);
	TestFalse(TEXT("StaggerB changed"), ConfiguredB == StartB);
	TestTrue(TEXT("StaggerA still holds ConfiguredA after B configured"), FStaggerClusterState(*StaggerA) == ConfiguredA);

	// Mutate ConfigForB afterwards
	ConfigForB.StaggerPolicy.StaggerSeconds = 88.f;
	TestTrue(TEXT("StaggerA still holds ConfiguredA after ConfigForB mutated"), FStaggerClusterState(*StaggerA) == ConfiguredA);
	TestTrue(TEXT("StaggerB still holds ConfiguredB after ConfigForB mutated"), FStaggerClusterState(*StaggerB) == ConfiguredB);

	// Failed validation on StaggerA does not mutate StaggerA
	FRPGParticipantConfig Broken = ConfigA();
	Broken.StaggerPolicy.StaggerSeconds = -10.f;
	TestFalse(TEXT("configure broken fails"), RPGBossStaggerClusterAdapters::ConfigureStaggerCluster(*StaggerA, Broken, Error));
	TestTrue(TEXT("StaggerA still holds ConfiguredA values"), FStaggerClusterState(*StaggerA) == ConfiguredA);

	// Lifecycle failure on wrong component does not mutate either component or the CDO
	TStrongObjectPtr<URPGBossPosture> Posture(NewObject<URPGBossPosture>(OwnerA, TEXT("Posture")));
	TestFalse(TEXT("wrong component rejected"), RPGBossStaggerClusterAdapters::ConfigureStaggerCluster(*Posture, ConfigA(), Error));
	TestTrue(TEXT("StaggerA still holds ConfiguredA"), FStaggerClusterState(*StaggerA) == ConfiguredA);
	TestTrue(TEXT("StaggerB still holds ConfiguredB"), FStaggerClusterState(*StaggerB) == ConfiguredB);
	TestTrue(TEXT("CDO still untouched"), FStaggerClusterState(*GetDefault<URPGBossStagger>()) == CDOState);

	return true;
}

// --------------------------------------------------------------------------------------------------
// 4. Rejections Test
// --------------------------------------------------------------------------------------------------
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGStaggerClusterRejectionsTest, "OneBossFight.Binding.StaggerCluster.Rejections",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGStaggerClusterRejectionsTest::RunTest(const FString& Parameters)
{
	using namespace StaggerClusterTests;
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

	auto ExpectRejected = [&](const FString& Label, UActorComponent& Comp, const TCHAR* ExpectedToken)
	{
		const URPGBossStagger* AsStagger = Cast<URPGBossStagger>(&Comp);
		const URPGBossEncounter* AsEncounter = Cast<URPGBossEncounter>(&Comp);
		const URPGBossPosture* AsPosture = Cast<URPGBossPosture>(&Comp);
		TOptional<FStaggerClusterState> BeforeStagger;
		if (AsStagger) { BeforeStagger.Emplace(*AsStagger); }
		const float EncounterGateBefore = AsEncounter ? AsEncounter->GateRadius : 0.f;
		const float PostureMaxBefore = AsPosture ? AsPosture->PostureMax : 0.f;

		FString Error = TEXT("stale");
		const bool bOk = RPGBossStaggerClusterAdapters::ConfigureStaggerCluster(Comp, ConfigA(), Error);
		TestFalse(FString::Printf(TEXT("%s: rejected"), *Label), bOk);
		TestTrue(FString::Printf(TEXT("%s: named %s (got '%s')"), *Label, ExpectedToken, *Error), Error.StartsWith(ExpectedToken));

		if (AsStagger && BeforeStagger.IsSet())
		{
			TestTrue(FString::Printf(TEXT("%s: stagger state unchanged after rejection"), *Label), FStaggerClusterState(*AsStagger) == BeforeStagger.GetValue());
		}
		if (AsEncounter)
		{
			TestTrue(FString::Printf(TEXT("%s: encounter unchanged after rejection"), *Label), AsEncounter->GateRadius == EncounterGateBefore);
		}
		if (AsPosture)
		{
			TestTrue(FString::Printf(TEXT("%s: posture unchanged after rejection"), *Label), AsPosture->PostureMax == PostureMaxBefore);
		}
	};

	// 1. Wrong component class: concrete fixtures
	{
		TStrongObjectPtr<USceneComponent> SceneComp(NewObject<USceneComponent>(Owner, TEXT("SceneComp")));
		TStrongObjectPtr<URPGBossPosture> PostureComp(NewObject<URPGBossPosture>(Owner, TEXT("PostureComp")));
		TStrongObjectPtr<URPGBossEncounter> EncounterComp(NewObject<URPGBossEncounter>(Owner, TEXT("EncounterComp")));
		ExpectRejected(TEXT("USceneComponent"), *SceneComp, TEXT("WrongComponentClass"));
		ExpectRejected(TEXT("URPGBossPosture"), *PostureComp, TEXT("WrongComponentClass"));
		ExpectRejected(TEXT("URPGBossEncounter"), *EncounterComp, TEXT("WrongComponentClass"));
	}

	// 2. Component already registered
	{
		TStrongObjectPtr<URPGBossStagger> Stagger = NewStagger(Owner, TEXT("RegStagger"));
		ArmDistinctStart(*Stagger);
		Stagger->RegisterComponent();
		TestTrue(TEXT("component registered"), Stagger->IsRegistered());
		ExpectRejected(TEXT("registered component"), *Stagger, TEXT("ComponentAlreadyRegistered"));
	}

	// 3. Component begun play under begun owner (clearing all 4 clip soft pointers before Register + DispatchBeginPlay)
	{
		AActor* BegunOwner = Scope.SpawnOwner();
		if (!TestNotNull(TEXT("begun owner actor"), BegunOwner))
		{
			return false;
		}
		TStrongObjectPtr<URPGBossStagger> Stagger = NewStagger(BegunOwner, TEXT("BegunStagger"));
		ArmDistinctStart(*Stagger);
		Stagger->FallClip.Reset();
		Stagger->DownClip.Reset();
		Stagger->RipostePlayerClip.Reset();
		Stagger->RiposteBossClip.Reset();
		Stagger->RegisterComponent();
		BegunOwner->DispatchBeginPlay();
		TestTrue(TEXT("component and owner began play"), Stagger->HasBegunPlay() && BegunOwner->HasActorBegunPlay());
		ExpectRejected(TEXT("begun stagger"), *Stagger, TEXT("ComponentBegunPlay"));
	}

	// 4. Owner already begun play, component fresh unregistered
	{
		AActor* LateOwner = Scope.SpawnOwner();
		if (!TestNotNull(TEXT("late owner"), LateOwner))
		{
			return false;
		}
		LateOwner->DispatchBeginPlay();
		TestTrue(TEXT("owner began play"), LateOwner->HasActorBegunPlay());
		TStrongObjectPtr<URPGBossStagger> Stagger = NewStagger(LateOwner, TEXT("LateStagger"));
		ArmDistinctStart(*Stagger);
		ExpectRejected(TEXT("unregistered on begun owner"), *Stagger, TEXT("OwnerBegunPlay"));
	}

	// 5. Invalid owner: orphan component
	{
		TStrongObjectPtr<URPGBossStagger> Orphan(NewObject<URPGBossStagger>(GetTransientPackage(), TEXT("OrphanStagger")));
		ArmDistinctStart(*Orphan);
		ExpectRejected(TEXT("orphan component"), *Orphan, TEXT("InvalidOwner"));
	}

	// 6. Invalid component: destroyed-retained component
	{
		TStrongObjectPtr<URPGBossStagger> DestroyedComp = NewStagger(Owner, TEXT("DestroyedComp"));
		ArmDistinctStart(*DestroyedComp);
		DestroyedComp->DestroyComponent();
		TestTrue(TEXT("stagger component destroyed"), !IsValid(DestroyedComp.Get()));
		ExpectRejected(TEXT("destroyed stagger"), *DestroyedComp, TEXT("InvalidComponent"));

		TStrongObjectPtr<URPGBossPosture> DestroyedPosture(NewObject<URPGBossPosture>(Owner, TEXT("DestroyedPosture")));
		DestroyedPosture->DestroyComponent();
		TestTrue(TEXT("posture component destroyed"), !IsValid(DestroyedPosture.Get()));
		ExpectRejected(TEXT("destroyed wrong-class component"), *DestroyedPosture, TEXT("InvalidComponent"));
	}

	return true;
}

// --------------------------------------------------------------------------------------------------
// 5. Compile Test
// --------------------------------------------------------------------------------------------------
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGStaggerClusterCompileTest, "OneBossFight.Binding.StaggerCluster.Compile",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGStaggerClusterCompileTest::RunTest(const FString& Parameters)
{
	using namespace StaggerClusterTests;
	const FEpochPtr Content = RPGCombatRegistry::Legacy();
	if (!TestTrue(TEXT("content epoch"), Content.IsValid() && Content->Id.IsValid()))
	{
		return false;
	}

	// 1. Real synthetic compiler copies the new record and retains established values
	{
		const FRPGParticipantConfig CA = ConfigA();
		const TStrongObjectPtr<URPGBossDefinition> DefinitionA = MakeDefinition(CA);
		FConfigPtr Out;
		const FRPGHydrationResult ResultA = CompileSynthetic(*DefinitionA, Content, Out);
		TestTrue(TEXT("synthetic compile succeeds for ConfigA"), ResultA.IsReady() && Out.IsValid());
		if (Out.IsValid())
		{
			// Positive established values check (DD9 pattern line ~767)
			TestTrue(TEXT("stats MaxHealth retained"), Out->Stats.MaxHealth == 3500.f);
			TestTrue(TEXT("stats MaxPosture retained"), Out->Stats.MaxPosture == 73.5f);
			TestTrue(TEXT("encounter policy GateRadius retained"), Out->EncounterPolicy.GateRadius == 200.f);
			TestTrue(TEXT("encounter policy bResetOnPlayerRespawn retained"), Out->EncounterPolicy.bResetOnPlayerRespawn);
			TestTrue(TEXT("stagger policy StaggerSeconds retained"), Out->StaggerPolicy.StaggerSeconds == CA.StaggerPolicy.StaggerSeconds);
			TestTrue(TEXT("phase count retained"), Out->Phases.Num() == 1);
			TestTrue(TEXT("identity retained"), Out->BossId.ToString().Equals(TEXT("Synthetic"), ESearchCase::CaseSensitive));

			const FRPGPhaseFlowConfig DefaultFlow;
			const FRPGFireballConfig DefaultFireball;
			const FRPGPhaseDependencyConfig DefaultDeps;
			TestTrue(TEXT("PhaseFlow defaults carried"), Out->PhaseFlow.TransitionSeconds == DefaultFlow.TransitionSeconds && Out->PhaseFlow.AttackAbilityPrefix.Equals(DefaultFlow.AttackAbilityPrefix, ESearchCase::CaseSensitive));
			TestTrue(TEXT("Fireball defaults carried"), Out->Fireball.bFireballEnabled == DefaultFireball.bFireballEnabled && Out->Fireball.FireballCooldown == DefaultFireball.FireballCooldown);
			TestTrue(TEXT("PhaseDependencies defaults carried"), Out->PhaseDependencies.RoarClip.ToSoftObjectPath() == DefaultDeps.RoarClip.ToSoftObjectPath());

			// Stagger profile fields carried
			TestTrue(TEXT("Out bUseClips"), Out->StaggerProfile.bUseClips == CA.StaggerProfile.bUseClips);
			TestTrue(TEXT("Out bUseRiposteClips"), Out->StaggerProfile.bUseRiposteClips == CA.StaggerProfile.bUseRiposteClips);
			TestTrue(TEXT("Out bCriticalOnEveryHit"), Out->StaggerProfile.bCriticalOnEveryHit == CA.StaggerProfile.bCriticalOnEveryHit);
			TestTrue(TEXT("Out HitStunAbilityClassName"), Out->StaggerProfile.HitStunAbilityClassName == CA.StaggerProfile.HitStunAbilityClassName);
			TestTrue(TEXT("Out FallMontage"), Out->StaggerProfile.FallMontage.ToSoftObjectPath() == CA.StaggerProfile.FallMontage.ToSoftObjectPath());
			TestTrue(TEXT("Out GetUpMontage"), Out->StaggerProfile.GetUpMontage.ToSoftObjectPath() == CA.StaggerProfile.GetUpMontage.ToSoftObjectPath());
			TestTrue(TEXT("Out FallClip"), Out->StaggerProfile.FallClip.ToSoftObjectPath() == CA.StaggerProfile.FallClip.ToSoftObjectPath());
			TestTrue(TEXT("Out DownClip"), Out->StaggerProfile.DownClip.ToSoftObjectPath() == CA.StaggerProfile.DownClip.ToSoftObjectPath());
			TestTrue(TEXT("Out RipostePlayerClip"), Out->StaggerProfile.RipostePlayerClip.ToSoftObjectPath() == CA.StaggerProfile.RipostePlayerClip.ToSoftObjectPath());
			TestTrue(TEXT("Out RiposteBossClip"), Out->StaggerProfile.RiposteBossClip.ToSoftObjectPath() == CA.StaggerProfile.RiposteBossClip.ToSoftObjectPath());
			TestTrue(TEXT("Out ImmunityEffect"), Out->StaggerProfile.ImmunityEffect.ToSoftObjectPath() == CA.StaggerProfile.ImmunityEffect.ToSoftObjectPath());
		}

		// ConfigB
		const FRPGParticipantConfig CB = ConfigB();
		const TStrongObjectPtr<URPGBossDefinition> DefinitionB = MakeDefinition(CB);
		FConfigPtr OutB;
		const FRPGHydrationResult ResultB = CompileSynthetic(*DefinitionB, Content, OutB);
		TestTrue(TEXT("synthetic compile succeeds for ConfigB"), ResultB.IsReady() && OutB.IsValid());
		if (OutB.IsValid())
		{
			TestTrue(TEXT("OutB bUseClips true"), OutB->StaggerProfile.bUseClips);
			TestTrue(TEXT("OutB montages null"), OutB->StaggerProfile.FallMontage.IsNull() && OutB->StaggerProfile.GetUpMontage.IsNull());
		}

		// Default definition without explicit profile: authoring defaults copied
		const TStrongObjectPtr<URPGBossDefinition> DefDefault = MakeDefinition(ConfigA());
		DefDefault->StaggerProfile = FRPGStaggerProfileConfig();
		FConfigPtr OutDef;
		TestTrue(TEXT("default profile copied"), CompileSynthetic(*DefDefault, Content, OutDef).IsReady() && OutDef.IsValid());
		if (OutDef.IsValid())
		{
			const FRPGStaggerProfileConfig DocumentedDefaults;
			TestTrue(TEXT("default bUseClips"), OutDef->StaggerProfile.bUseClips == DocumentedDefaults.bUseClips);
			TestTrue(TEXT("default HitStun"), OutDef->StaggerProfile.HitStunAbilityClassName == DocumentedDefaults.HitStunAbilityClassName);
			TestTrue(TEXT("default Immunity"), OutDef->StaggerProfile.ImmunityEffect.ToSoftObjectPath() == DocumentedDefaults.ImmunityEffect.ToSoftObjectPath());
		}
	}

	// 2. FBad[] invalid cases on BOTH synthetic and production CompileParticipant
	struct FBad
	{
		const TCHAR* Name;
		TFunction<void(FRPGParticipantConfig&)> Break;
		const TCHAR* Token;
		const TCHAR* FieldSubstr;
	};
	const FBad Bad[] = {
		{TEXT("HitStun None"), [](FRPGParticipantConfig& C) { C.StaggerProfile.HitStunAbilityClassName = NAME_None; }, TEXT("InvalidStaggerProfile.NoHitStunClass"), TEXT("StaggerProfile.HitStunAbilityClassName")},
		{TEXT("FallClip missing when bUseClips true"), [](FRPGParticipantConfig& C) { C.StaggerProfile.bUseClips = true; C.StaggerProfile.FallClip = SequencePtr(FSoftObjectPath()); }, TEXT("InvalidDependency.Missing"), TEXT("StaggerProfile.FallClip")},
		{TEXT("FallMontage missing when bUseClips false"), [](FRPGParticipantConfig& C) { C.StaggerProfile.bUseClips = false; C.StaggerProfile.FallMontage = MontagePtr(FSoftObjectPath()); }, TEXT("InvalidDependency.Missing"), TEXT("StaggerProfile.FallMontage")},
		{TEXT("Riposte clip missing when bUseRiposteClips true"), [](FRPGParticipantConfig& C) { C.StaggerProfile.bUseRiposteClips = true; C.StaggerProfile.RipostePlayerClip = SequencePtr(FSoftObjectPath()); }, TEXT("InvalidDependency.Missing"), TEXT("StaggerProfile.RipostePlayerClip")},
		{TEXT("ImmunityEffect missing"), [](FRPGParticipantConfig& C) { C.StaggerProfile.ImmunityEffect = ClassPtr(FSoftObjectPath()); }, TEXT("InvalidDependency.Missing"), TEXT("StaggerProfile.ImmunityEffect")},
		{TEXT("Malformed path with whitespace"), [](FRPGParticipantConfig& C) { C.StaggerProfile.FallMontage = MontagePtr(MakePath(TEXT("/SyntheticMount/Bad Path"), TEXT("AM_Fall"))); }, TEXT("InvalidDependency.Malformed"), TEXT("StaggerProfile.FallMontage")},
		{TEXT("Immunity not a class path"), [](FRPGParticipantConfig& C) { C.StaggerProfile.ImmunityEffect = ClassPtr(MakePath(TEXT("/SyntheticMount/Effects"), TEXT("GE_HitStunImmune"))); }, TEXT("InvalidDependency.NotClassPath"), TEXT("StaggerProfile.ImmunityEffect")},
	};

	for (const FBad& Case : Bad)
	{
		FRPGParticipantConfig Broken = ConfigA();
		Case.Break(Broken);
		const TStrongObjectPtr<URPGBossDefinition> Definition = MakeDefinition(Broken);

		// Synthetic compile
		FConfigPtr Out;
		if (!TestTrue(FString::Printf(TEXT("%s: valid output exists first"), Case.Name), CompileSynthetic(*MakeDefinition(ConfigA()), Content, Out).IsReady() && Out.IsValid()))
		{
			return false;
		}
		const FRPGHydrationResult Result = CompileSynthetic(*Definition, Content, Out);
		TestFalse(FString::Printf(TEXT("%s (synthetic): refused"), Case.Name), Result.IsReady());
		TestTrue(FString::Printf(TEXT("%s (synthetic): named %s"), Case.Name, Case.Token), AnyErrorContains(Result, Case.Token));
		TestTrue(FString::Printf(TEXT("%s (synthetic): field path %s"), Case.Name, Case.FieldSubstr), AnyErrorContains(Result, Case.FieldSubstr));
		TestFalse(FString::Printf(TEXT("%s (synthetic): earlier output cleared"), Case.Name), Out.IsValid());

		// Production compile
		FConfigPtr ProductionOut;
		if (!TestTrue(FString::Printf(TEXT("%s (production): valid output exists first"), Case.Name),
			CompileSynthetic(*MakeDefinition(ConfigA()), Content, ProductionOut).IsReady() && ProductionOut.IsValid()))
		{
			return false;
		}
		const FRPGHydrationResult Production = RPGCombatHydration::CompileParticipant(*Definition, Content, FString::ChrN(64, TEXT('b')), ProductionOut);
		TestFalse(FString::Printf(TEXT("%s (production): refused"), Case.Name), Production.IsReady());
		TestTrue(FString::Printf(TEXT("%s (production): named %s"), Case.Name, Case.Token), AnyErrorContains(Production, Case.Token));
		TestTrue(FString::Printf(TEXT("%s (production): field path %s"), Case.Name, Case.FieldSubstr), AnyErrorContains(Production, Case.FieldSubstr));
		TestFalse(FString::Printf(TEXT("%s (production): earlier output cleared"), Case.Name), ProductionOut.IsValid());
	}

	// 3. RunRetained for established checks with valid stagger profile (11 cases)
	auto RunRetained = [&](const TCHAR* Name, const TCHAR* Text, const TFunction<void(URPGBossDefinition&)>& Break, int32 Schema, const FString& Hash, bool bNullContent)
	{
		FConfigPtr Out;
		if (!CompileSynthetic(*MakeDefinition(ConfigA()), Content, Out).IsReady() || !Out.IsValid())
		{
			AddError(TEXT("unsupported precondition: valid output could not be built"));
			return;
		}
		const TStrongObjectPtr<URPGBossDefinition> Definition = MakeDefinition(ConfigA());
		Definition->Schema = Schema;
		Break(*Definition);
		const FRPGHydrationResult Result = CompileSynthetic(*Definition, bNullContent ? FEpochPtr() : Content, Out, Hash);
		TestFalse(FString::Printf(TEXT("%s: refused"), Name), Result.IsReady());
		TestTrue(FString::Printf(TEXT("%s: established message '%s'"), Name, Text), AnyErrorContains(Result, Text));
		TestFalse(FString::Printf(TEXT("%s: earlier output cleared"), Name), Out.IsValid());
	};

	const FString GoodHash = FString::ChrN(64, TEXT('b'));
	RunRetained(TEXT("invalid phase flow"), TEXT("InvalidPhaseFlow.NoLeapTag"), [](URPGBossDefinition& D) { D.PhaseFlow.LeapAbilityTag = NAME_None; }, 1, GoodHash, false);
	RunRetained(TEXT("invalid fireball cooldown"), TEXT("InvalidFireball.CooldownOrder"), [](URPGBossDefinition& D) { D.Fireball.bFireballEnabled = true; D.Fireball.FireballCooldown = FVector2D(5.0, 4.0); }, 1, GoodHash, false);
	RunRetained(TEXT("invalid phase dependencies"), TEXT("InvalidDependency.Missing"), [](URPGBossDefinition& D) { D.PhaseFlow.bUseRoarClip = true; D.PhaseDependencies.RoarClip = SequencePtr(FSoftObjectPath()); }, 1, GoodHash, false);
	RunRetained(TEXT("invalid stagger policy"), TEXT("InvalidStagger.NotPositive"), [](URPGBossDefinition& D) { D.StaggerPolicy.GetUpRate = 0.f; }, 1, GoodHash, false);
	RunRetained(TEXT("invalid encounter policy"), TEXT("InvalidPolicy.Negative"), [](URPGBossDefinition& D) { D.EncounterPolicy.GateRadius = -1.f; }, 1, GoodHash, false);
	RunRetained(TEXT("negative posture maximum"), TEXT("invalid stats"), [](URPGBossDefinition& D) { D.Stats.MaxPosture = -1.f; }, 1, GoodHash, false);
	RunRetained(TEXT("phase threshold above 1"), TEXT("invalid/duplicate phase"), [](URPGBossDefinition& D) { D.Phases[0].EntryHealthFraction = 2.f; }, 1, GoodHash, false);
	RunRetained(TEXT("schema 2"), TEXT("identity absent"), [](URPGBossDefinition&) {}, 2, GoodHash, false);
	RunRetained(TEXT("manifest hash not 64 hex"), TEXT("identity absent"), [](URPGBossDefinition&) {}, 1, TEXT("short"), false);
	RunRetained(TEXT("no content lease"), TEXT("identity absent"), [](URPGBossDefinition&) {}, 1, GoodHash, true);
	RunRetained(TEXT("no field manifest"), TEXT("field manifest required"), [](URPGBossDefinition& D) { D.Fields.Reset(); }, 1, GoodHash, false);

	// 4. Several failures together
	{
		const TStrongObjectPtr<URPGBossDefinition> Definition = MakeDefinition(ConfigA());
		Definition->StaggerProfile.HitStunAbilityClassName = NAME_None;
		Definition->PhaseFlow.LeapAbilityTag = NAME_None;
		Definition->StaggerPolicy.GetUpRate = -1.f;
		Definition->Stats.MaxPosture = -1.f;

		FConfigPtr Out;
		const FRPGHydrationResult Result = CompileSynthetic(*Definition, Content, Out);
		TestTrue(TEXT("multiple errors reported"),
			!Result.IsReady() && AnyErrorContains(Result, TEXT("InvalidStaggerProfile.NoHitStunClass"))
			&& AnyErrorContains(Result, TEXT("InvalidPhaseFlow.NoLeapTag"))
			&& AnyErrorContains(Result, TEXT("InvalidStagger.NotPositive"))
			&& AnyErrorContains(Result, TEXT("invalid stats"))
			&& !Out.IsValid());
	}

	return true;
}

// --------------------------------------------------------------------------------------------------
// 6. Authoring Test
// --------------------------------------------------------------------------------------------------
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGStaggerClusterAuthoringTest, "OneBossFight.Binding.StaggerCluster.Authoring",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGStaggerClusterAuthoringTest::RunTest(const FString& Parameters)
{
	using namespace StaggerClusterTests;
	const UClass* Native = URPGBossStagger::StaticClass();

	// Struct reflection verification
	const UScriptStruct* ProfileStruct = FRPGStaggerProfileConfig::StaticStruct();
	if (!TestNotNull(TEXT("FRPGStaggerProfileConfig reflected"), ProfileStruct))
	{
		return false;
	}

	// 1. Check three bools
	for (const TCHAR* Name : {TEXT("bUseClips"), TEXT("bUseRiposteClips"), TEXT("bCriticalOnEveryHit")})
	{
		const FProperty* Prop = ProfileStruct->FindPropertyByName(Name);
		TestTrue(FString::Printf(TEXT("%s: reflected editable bool in struct"), Name), Prop && CastField<FBoolProperty>(Prop) && Prop->HasAnyPropertyFlags(CPF_Edit));
		const FProperty* NativeProp = Native->FindPropertyByName(Name);
		TestTrue(FString::Printf(TEXT("%s: also a bool of URPGBossStagger"), Name), NativeProp && CastField<FBoolProperty>(NativeProp));
	}

	// 2. Check HitStunAbilityClassName
	{
		const FProperty* Prop = ProfileStruct->FindPropertyByName(TEXT("HitStunAbilityClassName"));
		TestTrue(TEXT("HitStunAbilityClassName: reflected editable FName in struct"), Prop && CastField<FNameProperty>(Prop) && Prop->HasAnyPropertyFlags(CPF_Edit));
		const FProperty* NativeProp = Native->FindPropertyByName(TEXT("HitStunAbilityClassName"));
		TestTrue(TEXT("HitStunAbilityClassName: also an FName of URPGBossStagger"), NativeProp && CastField<FNameProperty>(NativeProp));
	}

	// 3. Check 6 soft object references (not soft class)
	for (const TCHAR* Name : {TEXT("FallMontage"), TEXT("GetUpMontage"), TEXT("FallClip"), TEXT("DownClip"), TEXT("RipostePlayerClip"), TEXT("RiposteBossClip")})
	{
		const FProperty* Prop = ProfileStruct->FindPropertyByName(Name);
		TestTrue(FString::Printf(TEXT("%s: reflected editable soft object (not class) in struct"), Name), Prop && CastField<FSoftObjectProperty>(Prop) && !CastField<FSoftClassProperty>(Prop) && Prop->HasAnyPropertyFlags(CPF_Edit));
		const FProperty* NativeProp = Native->FindPropertyByName(Name);
		TestTrue(FString::Printf(TEXT("%s: also a soft object (not class) of URPGBossStagger"), Name), NativeProp && CastField<FSoftObjectProperty>(NativeProp) && !CastField<FSoftClassProperty>(NativeProp));
	}

	// 4. Check ImmunityEffect soft class
	{
		const FProperty* Prop = ProfileStruct->FindPropertyByName(TEXT("ImmunityEffect"));
		TestTrue(TEXT("ImmunityEffect: reflected editable soft class in struct"), Prop && CastField<FSoftClassProperty>(Prop) && Prop->HasAnyPropertyFlags(CPF_Edit));
		const FProperty* NativeProp = Native->FindPropertyByName(TEXT("ImmunityEffect"));
		TestTrue(TEXT("ImmunityEffect: also a soft class of URPGBossStagger"), NativeProp && CastField<FSoftClassProperty>(NativeProp));
	}

	// Definition member verification
	const FStructProperty* DefProp = CastField<FStructProperty>(URPGBossDefinition::StaticClass()->FindPropertyByName(TEXT("StaggerProfile")));
	TestTrue(TEXT("URPGBossDefinition has StaggerProfile struct property"), DefProp && DefProp->Struct == ProfileStruct && DefProp->HasAnyPropertyFlags(CPF_Edit));

	// Documented defaults check
	const FRPGStaggerProfileConfig DocDefaults;
	TestTrue(TEXT("default bUseClips is true"), DocDefaults.bUseClips);
	TestTrue(TEXT("default bUseRiposteClips is true"), DocDefaults.bUseRiposteClips);
	TestFalse(TEXT("default bCriticalOnEveryHit is false"), DocDefaults.bCriticalOnEveryHit);
	TestTrue(TEXT("default HitStunAbilityClassName is GA_GS_Boss_HitStun_C"), DocDefaults.HitStunAbilityClassName == FName(TEXT("GA_GS_Boss_HitStun_C")));
	TestTrue(TEXT("literal FallMontage path"), DocDefaults.FallMontage.ToSoftObjectPath().ToString().EndsWith(TEXT("/KnockdownStart_Anim_Montage.KnockdownStart_Anim_Montage"), ESearchCase::CaseSensitive));
	TestTrue(TEXT("literal GetUpMontage path"), DocDefaults.GetUpMontage.ToSoftObjectPath().ToString().EndsWith(TEXT("/Knockdown_Getup_Anim_Montage.Knockdown_Getup_Anim_Montage"), ESearchCase::CaseSensitive));
	TestTrue(TEXT("literal FallClip path"), DocDefaults.FallClip.ToSoftObjectPath().ToString().EndsWith(TEXT("/AN_Boss01_StaggerFall.AN_Boss01_StaggerFall"), ESearchCase::CaseSensitive));
	TestTrue(TEXT("literal DownClip path"), DocDefaults.DownClip.ToSoftObjectPath().ToString().EndsWith(TEXT("/AN_Boss01_StaggerDown.AN_Boss01_StaggerDown"), ESearchCase::CaseSensitive));
	TestTrue(TEXT("literal RipostePlayerClip path"), DocDefaults.RipostePlayerClip.ToSoftObjectPath().ToString().EndsWith(TEXT("/AN_Riposte_Player_Front.AN_Riposte_Player_Front"), ESearchCase::CaseSensitive));
	TestTrue(TEXT("literal RiposteBossClip path"), DocDefaults.RiposteBossClip.ToSoftObjectPath().ToString().EndsWith(TEXT("/AN_Riposte_Boss_Reaction.AN_Riposte_Boss_Reaction"), ESearchCase::CaseSensitive));
	TestTrue(TEXT("literal ImmunityEffect path"), DocDefaults.ImmunityEffect.ToSoftObjectPath().ToString().EndsWith(TEXT("/GE_HitStunImmune.GE_HitStunImmune_C"), ESearchCase::CaseSensitive));

	// Compare defaults with native CDO
	const URPGBossStagger* CDO = GetDefault<URPGBossStagger>();
	if (TestNotNull(TEXT("URPGBossStagger CDO"), CDO))
	{
		TestTrue(TEXT("CDO bUseClips"), DocDefaults.bUseClips == CDO->bUseClips);
		TestTrue(TEXT("CDO bUseRiposteClips"), DocDefaults.bUseRiposteClips == CDO->bUseRiposteClips);
		TestTrue(TEXT("CDO bCriticalOnEveryHit"), DocDefaults.bCriticalOnEveryHit == CDO->bCriticalOnEveryHit);
		TestTrue(TEXT("CDO HitStunAbilityClassName"), DocDefaults.HitStunAbilityClassName == CDO->HitStunAbilityClassName);
		TestTrue(TEXT("CDO FallMontage"), DocDefaults.FallMontage.ToSoftObjectPath() == CDO->FallMontage.ToSoftObjectPath());
		TestTrue(TEXT("CDO GetUpMontage"), DocDefaults.GetUpMontage.ToSoftObjectPath() == CDO->GetUpMontage.ToSoftObjectPath());
		TestTrue(TEXT("CDO FallClip"), DocDefaults.FallClip.ToSoftObjectPath() == CDO->FallClip.ToSoftObjectPath());
		TestTrue(TEXT("CDO DownClip"), DocDefaults.DownClip.ToSoftObjectPath() == CDO->DownClip.ToSoftObjectPath());
		TestTrue(TEXT("CDO RipostePlayerClip"), DocDefaults.RipostePlayerClip.ToSoftObjectPath() == CDO->RipostePlayerClip.ToSoftObjectPath());
		TestTrue(TEXT("CDO RiposteBossClip"), DocDefaults.RiposteBossClip.ToSoftObjectPath() == CDO->RiposteBossClip.ToSoftObjectPath());
		TestTrue(TEXT("CDO ImmunityEffect"), DocDefaults.ImmunityEffect.ToSoftObjectPath() == CDO->ImmunityEffect.ToSoftObjectPath());
	}

	// MakeStaggerClusterPlan contract
	const FRPGComponentPlan Plan = RPGBossStaggerClusterAdapters::MakeStaggerClusterPlan();
	TestTrue(TEXT("plan has 25 required paths in exact order"), Plan.RequiredFields.Num() == 25);
	TestTrue(TEXT("plan first path is StaggerPolicy.StaggerSeconds"), Plan.RequiredFields[0].Equals(TEXT("StaggerPolicy.StaggerSeconds"), ESearchCase::CaseSensitive));
	TestTrue(TEXT("plan last path is StaggerProfile.ImmunityEffect"), Plan.RequiredFields[24].Equals(TEXT("StaggerProfile.ImmunityEffect"), ESearchCase::CaseSensitive));

	return true;
}

// --------------------------------------------------------------------------------------------------
// 7. Oracle Test
// --------------------------------------------------------------------------------------------------
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGStaggerClusterOracleTest, "OneBossFight.Binding.StaggerCluster.Oracle",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGStaggerClusterOracleTest::RunTest(const FString& Parameters)
{
	using namespace StaggerClusterTests;
	FClusterTestWorld Scope;
	if (!TestNotNull(TEXT("test world"), Scope.World))
	{
		return false;
	}
	AActor* ClusterOwner = Scope.SpawnOwner();
	AActor* OracleOwner = Scope.SpawnOwner();
	if (!TestTrue(TEXT("oracle owners created"), ClusterOwner && OracleOwner))
	{
		return false;
	}
	TStrongObjectPtr<URPGBossStagger> ClusterComp = NewStagger(ClusterOwner, TEXT("ClusterComp"));
	TStrongObjectPtr<URPGBossStagger> OracleComp = NewStagger(OracleOwner, TEXT("OracleComp"));
	if (!TestTrue(TEXT("stagger components created"), ClusterComp.IsValid() && OracleComp.IsValid()))
	{
		return false;
	}

	const struct FCase
	{
		const TCHAR* Name;
		FRPGParticipantConfig Config;
	} Cases[] = {
		{TEXT("ConfigA"), ConfigA()},
		{TEXT("ConfigB"), ConfigB()}
	};

	for (const FCase& Case : Cases)
	{
		ArmDistinctStart(*ClusterComp);
		ArmDistinctStart(*OracleComp);
		const FStaggerClusterState Start(*ClusterComp);

		// Cluster configure
		FString ClusterError;
		TestTrue(FString::Printf(TEXT("%s: cluster configure succeeds"), Case.Name),
			RPGBossStaggerClusterAdapters::ConfigureStaggerCluster(*ClusterComp, Case.Config, ClusterError));

		// Oracle configure (DD7 policy adapter alone)
		FString OracleError;
		TestTrue(FString::Printf(TEXT("%s: oracle configure succeeds"), Case.Name),
			RPGBossStaggerPolicyAdapters::ConfigureStaggerPolicy(*OracleComp, Case.Config, OracleError));

		const FStaggerClusterState ClusterState(*ClusterComp);
		const FStaggerClusterState OracleState(*OracleComp);

		// Policy fields identical between oracle and cluster
		TestTrue(FString::Printf(TEXT("%s: 14 policy fields identical between oracle and cluster"), Case.Name),
			ClusterState.PolicyEquals(OracleState));

		// Oracle leaves profile fields at start
		TestTrue(FString::Printf(TEXT("%s: oracle leaves profile fields at start"), Case.Name),
			OracleState.ProfileEquals(Start));

		// Cluster changed profile fields according to config
		TestTrue(FString::Printf(TEXT("%s: cluster applied profile bUseClips"), Case.Name),
			ClusterState.bUseClips == Case.Config.StaggerProfile.bUseClips);
		TestTrue(FString::Printf(TEXT("%s: cluster applied profile bUseRiposteClips"), Case.Name),
			ClusterState.bUseRiposteClips == Case.Config.StaggerProfile.bUseRiposteClips);
		TestTrue(FString::Printf(TEXT("%s: cluster applied profile bCriticalOnEveryHit"), Case.Name),
			ClusterState.bCriticalOnEveryHit == Case.Config.StaggerProfile.bCriticalOnEveryHit);
		TestTrue(FString::Printf(TEXT("%s: cluster applied profile HitStunAbilityClassName"), Case.Name),
			ClusterState.HitStunAbilityClassName == Case.Config.StaggerProfile.HitStunAbilityClassName);
		TestTrue(FString::Printf(TEXT("%s: cluster applied profile ImmunityEffect"), Case.Name),
			ClusterState.ImmunityEffect == Case.Config.StaggerProfile.ImmunityEffect.ToSoftObjectPath());

		// Runtime state untouched on both
		TestTrue(FString::Printf(TEXT("%s: runtime state untouched"), Case.Name),
			ClusterState.RuntimeEquals(OracleState) && ClusterState.RuntimeEquals(Start));
	}

	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
