// Copyright One Boss Fight. All Rights Reserved.

#include "CoreMinimal.h"
#include "Misc/AutomationTest.h"
#include "Animation/AnimMontage.h"
#include "Animation/AnimSequence.h"
#include "Components/SceneComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"
#include "Player/RPGCombatRegistry.h"
#include "Player/RPGEncounterBinding.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossPosture.h"
#include "Player/RPGBossStagger.h"
#include "Player/RPGBossStaggerPolicyAdapters.h"
#include "Player/RPGBossStaggerClusterAdapters.h"
#include "UObject/Package.h"
#include "UObject/StrongObjectPtr.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGStaggerClusterAssignTest, "OneBossFight.Binding.StaggerCluster.Assign",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGStaggerClusterValidationTest, "OneBossFight.Binding.StaggerCluster.Validation",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGStaggerClusterIsolationTest, "OneBossFight.Binding.StaggerCluster.Isolation",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGStaggerClusterRejectionsTest, "OneBossFight.Binding.StaggerCluster.Rejections",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGStaggerClusterCompileTest, "OneBossFight.Binding.StaggerCluster.Compile",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGStaggerClusterAuthoringTest, "OneBossFight.Binding.StaggerCluster.Authoring",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGStaggerClusterOracleTest, "OneBossFight.Binding.StaggerCluster.Oracle",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

namespace
{
namespace StaggerClusterTests
{
	using FEpochPtr = TSharedPtr<const RPGCombatRegistry::FEpoch>;
	using FConfigPtr = TSharedPtr<const FRPGParticipantConfig>;

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

	FSoftObjectPath MakePath(const TCHAR* Package, const TCHAR* Asset, const TCHAR* Sub = TEXT(""))
	{
		return FSoftObjectPath(FTopLevelAssetPath(FName(Package), FName(Asset)), FString(Sub));
	}

	TSoftObjectPtr<UAnimSequence> SequencePtr(const FSoftObjectPath& P) { return TSoftObjectPtr<UAnimSequence>(P); }
	TSoftObjectPtr<UAnimMontage> MontagePtr(const FSoftObjectPath& P) { return TSoftObjectPtr<UAnimMontage>(P); }
	TSoftClassPtr<UObject> ClassPtr(const FSoftObjectPath& P) { return TSoftClassPtr<UObject>(P); }

	struct FStaggerState
	{
		// 14 policy fields
		float StaggerSeconds, FreezeAtPosition, CriticalMultiplier, RiposteRange, RiposteConeDegrees, RiposteFacingDegrees;
		float RiposteArmSeconds, RipostePlayerStartGap, RiposteAlignSeconds, RiposteImpactSeconds, RiposteBaseDamage, CooldownSeconds, GetUpRate;
		bool bHoldPostureAtZero;

		// 11 profile fields
		bool bUseClips, bUseRiposteClips, bCriticalOnEveryHit;
		FName HitStunAbilityClassName;
		FSoftObjectPath FallMontage, GetUpMontage, FallClip, DownClip, RipostePlayerClip, RiposteBossClip, ImmunityEffect;

		// Runtime state
		bool bStaggered, bCriticalWindowOpen, bUsingClips, bRiposteExecuting;
		int32 StaggerCount, CriticalHitCount, RiposteCount, RiposteRejectCount, RiposteImpactCount, RiposteAbortCount;
		FString LastRiposteResult, LastBreakResult, ClipStageName;
		double LastEndTime;

		explicit FStaggerState(const URPGBossStagger& S)
			: StaggerSeconds(S.StaggerSeconds), FreezeAtPosition(S.FreezeAtPosition), CriticalMultiplier(S.CriticalMultiplier)
			, RiposteRange(S.RiposteRange), RiposteConeDegrees(S.RiposteConeDegrees), RiposteFacingDegrees(S.RiposteFacingDegrees)
			, RiposteArmSeconds(S.RiposteArmSeconds), RipostePlayerStartGap(S.RipostePlayerStartGap), RiposteAlignSeconds(S.RiposteAlignSeconds)
			, RiposteImpactSeconds(S.RiposteImpactSeconds), RiposteBaseDamage(S.RiposteBaseDamage), CooldownSeconds(S.CooldownSeconds), GetUpRate(S.GetUpRate)
			, bHoldPostureAtZero(S.bHoldPostureAtZero)
			, bUseClips(S.bUseClips), bUseRiposteClips(S.bUseRiposteClips), bCriticalOnEveryHit(S.bCriticalOnEveryHit)
			, HitStunAbilityClassName(S.HitStunAbilityClassName)
			, FallMontage(S.FallMontage.ToSoftObjectPath()), GetUpMontage(S.GetUpMontage.ToSoftObjectPath())
			, FallClip(S.FallClip.ToSoftObjectPath()), DownClip(S.DownClip.ToSoftObjectPath())
			, RipostePlayerClip(S.RipostePlayerClip.ToSoftObjectPath()), RiposteBossClip(S.RiposteBossClip.ToSoftObjectPath())
			, ImmunityEffect(S.ImmunityEffect.ToSoftObjectPath())
			, bStaggered(S.IsStaggered()), bCriticalWindowOpen(S.IsCriticalWindowOpen()), bUsingClips(S.IsUsingClips()), bRiposteExecuting(S.IsRiposteExecuting())
			, StaggerCount(S.GetStaggerCount()), CriticalHitCount(S.GetCriticalHitCount()), RiposteCount(S.GetRiposteCount()), RiposteRejectCount(S.GetRiposteRejectCount())
			, RiposteImpactCount(S.GetRiposteImpactCount()), RiposteAbortCount(S.GetRiposteAbortCount()), LastRiposteResult(S.GetLastRiposteResult()), LastBreakResult(S.GetLastBreakResult())
			, ClipStageName(S.GetClipStageName()), LastEndTime(S.GetLastEndTime())
		{
		}

		FStaggerState(const FRPGStaggerPolicyConfig& P, const FRPGStaggerProfileConfig& Prof)
			: StaggerSeconds(P.StaggerSeconds), FreezeAtPosition(P.FreezeAtPosition), CriticalMultiplier(P.CriticalMultiplier)
			, RiposteRange(P.RiposteRange), RiposteConeDegrees(P.RiposteConeDegrees), RiposteFacingDegrees(P.RiposteFacingDegrees)
			, RiposteArmSeconds(P.RiposteArmSeconds), RipostePlayerStartGap(P.RipostePlayerStartGap), RiposteAlignSeconds(P.RiposteAlignSeconds)
			, RiposteImpactSeconds(P.RiposteImpactSeconds), RiposteBaseDamage(P.RiposteBaseDamage), CooldownSeconds(P.CooldownSeconds), GetUpRate(P.GetUpRate)
			, bHoldPostureAtZero(P.bHoldPostureAtZero)
			, bUseClips(Prof.bUseClips), bUseRiposteClips(Prof.bUseRiposteClips), bCriticalOnEveryHit(Prof.bCriticalOnEveryHit)
			, HitStunAbilityClassName(Prof.HitStunAbilityClassName)
			, FallMontage(Prof.FallMontage.ToSoftObjectPath()), GetUpMontage(Prof.GetUpMontage.ToSoftObjectPath())
			, FallClip(Prof.FallClip.ToSoftObjectPath()), DownClip(Prof.DownClip.ToSoftObjectPath())
			, RipostePlayerClip(Prof.RipostePlayerClip.ToSoftObjectPath()), RiposteBossClip(Prof.RiposteBossClip.ToSoftObjectPath())
			, ImmunityEffect(Prof.ImmunityEffect.ToSoftObjectPath())
			, bStaggered(false), bCriticalWindowOpen(false), bUsingClips(false), bRiposteExecuting(false)
			, StaggerCount(0), CriticalHitCount(0), RiposteCount(0), RiposteRejectCount(0)
			, RiposteImpactCount(0), RiposteAbortCount(0), LastRiposteResult(), LastBreakResult()
			, ClipStageName(), LastEndTime(0.0)
		{
		}

		bool PolicyEquals(const FStaggerState& O) const
		{
			return StaggerSeconds == O.StaggerSeconds && FreezeAtPosition == O.FreezeAtPosition && CriticalMultiplier == O.CriticalMultiplier
				&& RiposteRange == O.RiposteRange && RiposteConeDegrees == O.RiposteConeDegrees && RiposteFacingDegrees == O.RiposteFacingDegrees
				&& RiposteArmSeconds == O.RiposteArmSeconds && RipostePlayerStartGap == O.RipostePlayerStartGap && RiposteAlignSeconds == O.RiposteAlignSeconds
				&& RiposteImpactSeconds == O.RiposteImpactSeconds && RiposteBaseDamage == O.RiposteBaseDamage && CooldownSeconds == O.CooldownSeconds
				&& GetUpRate == O.GetUpRate && bHoldPostureAtZero == O.bHoldPostureAtZero;
		}

		bool ProfileEquals(const FStaggerState& O) const
		{
			return bUseClips == O.bUseClips && bUseRiposteClips == O.bUseRiposteClips && bCriticalOnEveryHit == O.bCriticalOnEveryHit
				&& HitStunAbilityClassName == O.HitStunAbilityClassName
				&& FallMontage == O.FallMontage && GetUpMontage == O.GetUpMontage
				&& FallClip == O.FallClip && DownClip == O.DownClip
				&& RipostePlayerClip == O.RipostePlayerClip && RiposteBossClip == O.RiposteBossClip
				&& ImmunityEffect == O.ImmunityEffect;
		}

		bool RuntimeEquals(const FStaggerState& O) const
		{
			return bStaggered == O.bStaggered && bCriticalWindowOpen == O.bCriticalWindowOpen && bUsingClips == O.bUsingClips && bRiposteExecuting == O.bRiposteExecuting
				&& StaggerCount == O.StaggerCount && CriticalHitCount == O.CriticalHitCount && RiposteCount == O.RiposteCount && RiposteRejectCount == O.RiposteRejectCount
				&& RiposteImpactCount == O.RiposteImpactCount && RiposteAbortCount == O.RiposteAbortCount && LastRiposteResult.Equals(O.LastRiposteResult, ESearchCase::CaseSensitive)
				&& LastBreakResult.Equals(O.LastBreakResult, ESearchCase::CaseSensitive) && ClipStageName.Equals(O.ClipStageName, ESearchCase::CaseSensitive) && LastEndTime == O.LastEndTime;
		}

		bool operator==(const FStaggerState& O) const
		{
			return PolicyEquals(O) && ProfileEquals(O) && RuntimeEquals(O);
		}
	};

	FRPGStaggerPolicyConfig NondefaultPolicyA()
	{
		FRPGStaggerPolicyConfig P;
		P.StaggerSeconds = 4.2f;
		P.FreezeAtPosition = 2.1f;
		P.CriticalMultiplier = 3.5f;
		P.RiposteRange = 220.f;
		P.RiposteConeDegrees = 90.f;
		P.RiposteFacingDegrees = 80.f;
		P.RiposteArmSeconds = 2.0f;
		P.RipostePlayerStartGap = 190.f;
		P.RiposteAlignSeconds = 0.5f;
		P.RiposteImpactSeconds = 1.1f;
		P.RiposteBaseDamage = 65.f;
		P.CooldownSeconds = 3.0f;
		P.GetUpRate = 1.2f;
		P.bHoldPostureAtZero = false;
		return P;
	}

	FRPGStaggerProfileConfig NondefaultProfileA()
	{
		FRPGStaggerProfileConfig P;
		P.bUseClips = false;
		P.bUseRiposteClips = false;
		P.bCriticalOnEveryHit = true;
		P.HitStunAbilityClassName = TEXT("GA_TestHitStun_C");
		P.FallMontage = MontagePtr(MakePath(TEXT("/SyntheticMount/Custom"), TEXT("AM_TestFall")));
		P.GetUpMontage = MontagePtr(MakePath(TEXT("/SyntheticMount/Custom"), TEXT("AM_TestGetUp")));
		P.FallClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Custom"), TEXT("AN_TestFall")));
		P.DownClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Custom"), TEXT("AN_TestDown")));
		P.RipostePlayerClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Custom"), TEXT("AN_TestRipostePlayer")));
		P.RiposteBossClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Custom"), TEXT("AN_TestRiposteBoss")));
		P.ImmunityEffect = ClassPtr(MakePath(TEXT("/SyntheticMount/Custom"), TEXT("GE_TestImmune_C")));
		return P;
	}

	FRPGStaggerPolicyConfig NondefaultPolicyB()
	{
		FRPGStaggerPolicyConfig P;
		P.StaggerSeconds = 1.8f;
		P.FreezeAtPosition = 0.9f;
		P.CriticalMultiplier = 1.5f;
		P.RiposteRange = 110.f;
		P.RiposteConeDegrees = 60.f;
		P.RiposteFacingDegrees = 45.f;
		P.RiposteArmSeconds = 0.8f;
		P.RipostePlayerStartGap = 120.f;
		P.RiposteAlignSeconds = 0.2f;
		P.RiposteImpactSeconds = 0.6f;
		P.RiposteBaseDamage = 25.f;
		P.CooldownSeconds = 1.5f;
		P.GetUpRate = 0.8f;
		P.bHoldPostureAtZero = true;
		return P;
	}

	FRPGStaggerProfileConfig NondefaultProfileB()
	{
		FRPGStaggerProfileConfig P;
		P.bUseClips = true;
		P.bUseRiposteClips = true;
		P.bCriticalOnEveryHit = false;
		P.HitStunAbilityClassName = TEXT("GA_OtherHitStun_C");
		P.FallMontage.Reset();
		P.GetUpMontage.Reset();
		P.FallClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Other"), TEXT("AN_OtherFall")));
		P.DownClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Other"), TEXT("AN_OtherDown")));
		P.RipostePlayerClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Other"), TEXT("AN_OtherRipostePlayer")));
		P.RiposteBossClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Other"), TEXT("AN_OtherRiposteBoss")));
		P.ImmunityEffect = ClassPtr(MakePath(TEXT("/SyntheticMount/Other"), TEXT("GE_OtherImmune_C")));
		return P;
	}

	FRPGParticipantConfig ConfigA()
	{
		FRPGParticipantConfig C;
		C.BossId = TEXT("SyntheticBoss");
		C.PresentationId = TEXT("SyntheticLook");
		C.StableManifestHash = TEXT("0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef");
		C.Stats.MaxHealth = 3500.f;
		C.Stats.MaxPosture = 73.5f;
		C.Stats.PostureRegenDelay = 4.25f;
		C.Stats.PostureRegenRate = 9.75f;
		C.EncounterPolicy.GateRadius = 1200.f;
		C.EncounterPolicy.bResetOnPlayerRespawn = true;
		C.PhaseFlow.TransitionSeconds = 1.8f;
		C.PhaseFlow.bUseRoarClip = true;
		C.PhaseFlow.bPausePostureInTransition = true;
		C.PhaseFlow.bLockLeapUntilPhaseTwo = true;
		C.PhaseFlow.AttackAbilityPrefix = TEXT("GA_GS_Boss_");
		C.PhaseFlow.LeapAbilityTag = FName(TEXT("Ability.Melee.LeapAttack"));
		C.Fireball.bFireballEnabled = false;
		C.Fireball.FireballCooldown = FVector2D(6.0, 10.0);
		C.Fireball.FireballMinRange = 500.f;
		C.Fireball.FireballMaxRange = 1800.f;
		C.PhaseDependencies = FRPGPhaseDependencyConfig();
		C.StaggerPolicy = NondefaultPolicyA();
		C.StaggerProfile = NondefaultProfileA();
		FRPGPhaseConfig Phase;
		Phase.PhaseId = TEXT("PhaseTwo");
		Phase.EntryHealthFraction = 0.35f;
		Phase.SpeedMultiplier = 1.5f;
		Phase.RateMultiplier = 1.75f;
		Phase.AttackMultiplier = 2.f;
		C.Phases.Add(Phase);
		C.bSyntheticFixture = true;
		return C;
	}

	FRPGParticipantConfig ConfigB()
	{
		FRPGParticipantConfig C;
		C.BossId = TEXT("SyntheticBossB");
		C.PresentationId = TEXT("SyntheticLookB");
		C.StableManifestHash = TEXT("fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210");
		C.Stats.MaxHealth = 3500.f;
		C.Stats.MaxPosture = 73.5f;
		C.Stats.PostureRegenDelay = 4.25f;
		C.Stats.PostureRegenRate = 9.75f;
		C.EncounterPolicy.GateRadius = 1200.f;
		C.EncounterPolicy.bResetOnPlayerRespawn = true;
		C.PhaseFlow.TransitionSeconds = 1.8f;
		C.PhaseFlow.bUseRoarClip = true;
		C.PhaseFlow.bPausePostureInTransition = true;
		C.PhaseFlow.bLockLeapUntilPhaseTwo = true;
		C.PhaseFlow.AttackAbilityPrefix = TEXT("GA_GS_Boss_");
		C.PhaseFlow.LeapAbilityTag = FName(TEXT("Ability.Melee.LeapAttack"));
		C.Fireball.bFireballEnabled = false;
		C.Fireball.FireballCooldown = FVector2D(6.0, 10.0);
		C.Fireball.FireballMinRange = 500.f;
		C.Fireball.FireballMaxRange = 1800.f;
		C.PhaseDependencies = FRPGPhaseDependencyConfig();
		C.StaggerPolicy = NondefaultPolicyB();
		C.StaggerProfile = NondefaultProfileB();
		FRPGPhaseConfig Phase;
		Phase.PhaseId = TEXT("PhaseTwo");
		Phase.EntryHealthFraction = 0.35f;
		Phase.SpeedMultiplier = 1.5f;
		Phase.RateMultiplier = 1.75f;
		Phase.AttackMultiplier = 2.f;
		C.Phases.Add(Phase);
		C.bSyntheticFixture = true;
		return C;
	}

	FRPGParityField MakeField(const TCHAR* Path, const TCHAR* Value)
	{
		FRPGParityField F;
		F.Path = Path;
		F.Value = Value;
		return F;
	}

	TStrongObjectPtr<URPGBossDefinition> MakeDefinition(const FRPGParticipantConfig& Config)
	{
		TStrongObjectPtr<URPGBossDefinition> Definition(NewObject<URPGBossDefinition>());
		Definition->Schema = 1;
		Definition->DefinitionId = Config.BossId;
		Definition->PresentationId = Config.PresentationId;
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
		Definition->EncounterPolicy = Config.EncounterPolicy;
		Definition->StaggerPolicy = Config.StaggerPolicy;
		Definition->PhaseFlow = Config.PhaseFlow;
		Definition->Fireball = Config.Fireball;
		Definition->PhaseDependencies = Config.PhaseDependencies;
		Definition->StaggerProfile = Config.StaggerProfile;
		Definition->Fields.Add(MakeField(RPGBossStaggerPolicyAdapters::FieldStaggerSeconds, TEXT("synthetic")));
		Definition->Fields.Add(MakeField(RPGBossStaggerClusterAdapters::FieldHitStunAbilityClassName, TEXT("synthetic")));
		return Definition;
	}

	FRPGHydrationResult CompileSynthetic(const URPGBossDefinition& Definition, FEpochPtr Content, FConfigPtr& Out)
	{
		return RPGCombatHydration::CompileSyntheticParticipant(Definition, Content, TEXT("0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"), Out);
	}

	TStrongObjectPtr<URPGBossStagger> NewStagger(AActor* Owner, const TCHAR* Name)
	{
		return TStrongObjectPtr<URPGBossStagger>(NewObject<URPGBossStagger>(Owner, FName(Name)));
	}

	void ArmDistinctStart(URPGBossStagger& S)
	{
		S.StaggerSeconds = 77.f;
		S.FreezeAtPosition = 77.f;
		S.CriticalMultiplier = 77.f;
		S.RiposteRange = 777.f;
		S.RiposteConeDegrees = 77.f;
		S.RiposteFacingDegrees = 77.f;
		S.RiposteArmSeconds = 77.f;
		S.RipostePlayerStartGap = 777.f;
		S.RiposteAlignSeconds = 7.7f;
		S.RiposteImpactSeconds = 7.7f;
		S.RiposteBaseDamage = 777.f;
		S.CooldownSeconds = 77.f;
		S.GetUpRate = 7.7f;
		S.bHoldPostureAtZero = false;

		S.bUseClips = false;
		S.bUseRiposteClips = false;
		S.bCriticalOnEveryHit = true;
		S.HitStunAbilityClassName = TEXT("GA_SentinelHitStun_C");
		S.FallMontage = MontagePtr(MakePath(TEXT("/SyntheticMount/Sentinel"), TEXT("AM_SentFall")));
		S.GetUpMontage = MontagePtr(MakePath(TEXT("/SyntheticMount/Sentinel"), TEXT("AM_SentGetUp")));
		S.FallClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Sentinel"), TEXT("AN_SentFall")));
		S.DownClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Sentinel"), TEXT("AN_SentDown")));
		S.RipostePlayerClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Sentinel"), TEXT("AN_SentRipostePlayer")));
		S.RiposteBossClip = SequencePtr(MakePath(TEXT("/SyntheticMount/Sentinel"), TEXT("AN_SentRiposteBoss")));
		S.ImmunityEffect = ClassPtr(MakePath(TEXT("/SyntheticMount/Sentinel"), TEXT("GE_SentImmune_C")));
	}
}
}

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
	TStrongObjectPtr<URPGBossStagger> Stagger = NewStagger(Owner, TEXT("RPGBossStagger"));
	if (!TestTrue(TEXT("component created"), Stagger.IsValid()))
	{
		return false;
	}

	const FRPGComponentPlan Plan = RPGBossStaggerClusterAdapters::MakeStaggerClusterPlan();
	TestTrue(TEXT("plan class is URPGBossStagger"), Plan.Class == URPGBossStagger::StaticClass());
	TestEqual(TEXT("legacy instance name"), Plan.InstanceName, FString(TEXT("RPGBossStagger")));
	TestTrue(TEXT("configure callback set"), static_cast<bool>(Plan.Configure));
	TestEqual(TEXT("twenty-five required fields"), Plan.RequiredFields.Num(), 25);
	if (Plan.RequiredFields.Num() == 25)
	{
		TestEqual(TEXT("path 0"), Plan.RequiredFields[0], FString(RPGBossStaggerPolicyAdapters::FieldStaggerSeconds));
		TestEqual(TEXT("path 13"), Plan.RequiredFields[13], FString(RPGBossStaggerPolicyAdapters::FieldHoldPostureAtZero));
		TestEqual(TEXT("path 14"), Plan.RequiredFields[14], FString(RPGBossStaggerClusterAdapters::FieldUseClips));
		TestEqual(TEXT("path 15"), Plan.RequiredFields[15], FString(RPGBossStaggerClusterAdapters::FieldUseRiposteClips));
		TestEqual(TEXT("path 16"), Plan.RequiredFields[16], FString(RPGBossStaggerClusterAdapters::FieldCriticalOnEveryHit));
		TestEqual(TEXT("path 17"), Plan.RequiredFields[17], FString(RPGBossStaggerClusterAdapters::FieldHitStunAbilityClassName));
		TestEqual(TEXT("path 18"), Plan.RequiredFields[18], FString(RPGBossStaggerClusterAdapters::FieldFallMontage));
		TestEqual(TEXT("path 19"), Plan.RequiredFields[19], FString(RPGBossStaggerClusterAdapters::FieldGetUpMontage));
		TestEqual(TEXT("path 20"), Plan.RequiredFields[20], FString(RPGBossStaggerClusterAdapters::FieldFallClip));
		TestEqual(TEXT("path 21"), Plan.RequiredFields[21], FString(RPGBossStaggerClusterAdapters::FieldDownClip));
		TestEqual(TEXT("path 22"), Plan.RequiredFields[22], FString(RPGBossStaggerClusterAdapters::FieldRipostePlayerClip));
		TestEqual(TEXT("path 23"), Plan.RequiredFields[23], FString(RPGBossStaggerClusterAdapters::FieldRiposteBossClip));
		TestEqual(TEXT("path 24"), Plan.RequiredFields[24], FString(RPGBossStaggerClusterAdapters::FieldImmunityEffect));
	}

	const URPGBossStagger* CDO = GetDefault<URPGBossStagger>();
	const FRPGParticipantConfig A = ConfigA();
	TestTrue(TEXT("A differs: StaggerSeconds"), A.StaggerPolicy.StaggerSeconds != CDO->StaggerSeconds);
	TestTrue(TEXT("A differs: FreezeAtPosition"), A.StaggerPolicy.FreezeAtPosition != CDO->FreezeAtPosition);
	TestTrue(TEXT("A differs: CriticalMultiplier"), A.StaggerPolicy.CriticalMultiplier != CDO->CriticalMultiplier);
	TestTrue(TEXT("A differs: RiposteRange"), A.StaggerPolicy.RiposteRange != CDO->RiposteRange);
	TestTrue(TEXT("A differs: RiposteConeDegrees"), A.StaggerPolicy.RiposteConeDegrees != CDO->RiposteConeDegrees);
	TestTrue(TEXT("A differs: RiposteFacingDegrees"), A.StaggerPolicy.RiposteFacingDegrees != CDO->RiposteFacingDegrees);
	TestTrue(TEXT("A differs: RiposteArmSeconds"), A.StaggerPolicy.RiposteArmSeconds != CDO->RiposteArmSeconds);
	TestTrue(TEXT("A differs: RipostePlayerStartGap"), A.StaggerPolicy.RipostePlayerStartGap != CDO->RipostePlayerStartGap);
	TestTrue(TEXT("A differs: RiposteAlignSeconds"), A.StaggerPolicy.RiposteAlignSeconds != CDO->RiposteAlignSeconds);
	TestTrue(TEXT("A differs: RiposteImpactSeconds"), A.StaggerPolicy.RiposteImpactSeconds != CDO->RiposteImpactSeconds);
	TestTrue(TEXT("A differs: RiposteBaseDamage"), A.StaggerPolicy.RiposteBaseDamage != CDO->RiposteBaseDamage);
	TestTrue(TEXT("A differs: CooldownSeconds"), A.StaggerPolicy.CooldownSeconds != CDO->CooldownSeconds);
	TestTrue(TEXT("A differs: GetUpRate"), A.StaggerPolicy.GetUpRate != CDO->GetUpRate);
	TestTrue(TEXT("A differs: bHoldPostureAtZero"), A.StaggerPolicy.bHoldPostureAtZero != CDO->bHoldPostureAtZero);
	TestTrue(TEXT("A differs: bUseClips"), A.StaggerProfile.bUseClips != CDO->bUseClips);
	TestTrue(TEXT("A differs: bUseRiposteClips"), A.StaggerProfile.bUseRiposteClips != CDO->bUseRiposteClips);
	TestTrue(TEXT("A differs: bCriticalOnEveryHit"), A.StaggerProfile.bCriticalOnEveryHit != CDO->bCriticalOnEveryHit);
	TestTrue(TEXT("A differs: HitStunAbilityClassName"), A.StaggerProfile.HitStunAbilityClassName != CDO->HitStunAbilityClassName);
	TestTrue(TEXT("A differs: FallMontage"), A.StaggerProfile.FallMontage.ToSoftObjectPath() != CDO->FallMontage.ToSoftObjectPath());
	TestTrue(TEXT("A differs: GetUpMontage"), A.StaggerProfile.GetUpMontage.ToSoftObjectPath() != CDO->GetUpMontage.ToSoftObjectPath());
	TestTrue(TEXT("A differs: FallClip"), A.StaggerProfile.FallClip.ToSoftObjectPath() != CDO->FallClip.ToSoftObjectPath());
	TestTrue(TEXT("A differs: DownClip"), A.StaggerProfile.DownClip.ToSoftObjectPath() != CDO->DownClip.ToSoftObjectPath());
	TestTrue(TEXT("A differs: RipostePlayerClip"), A.StaggerProfile.RipostePlayerClip.ToSoftObjectPath() != CDO->RipostePlayerClip.ToSoftObjectPath());
	TestTrue(TEXT("A differs: RiposteBossClip"), A.StaggerProfile.RiposteBossClip.ToSoftObjectPath() != CDO->RiposteBossClip.ToSoftObjectPath());
	TestTrue(TEXT("A differs: ImmunityEffect"), A.StaggerProfile.ImmunityEffect.ToSoftObjectPath() != CDO->ImmunityEffect.ToSoftObjectPath());

	const FStaggerState RuntimeBefore(*Stagger);
	FString Error;
	const bool bAssignedA = Plan.Configure(*Stagger, A, Error);
	TestTrue(TEXT("Config A written through plan callback"), bAssignedA && Error.IsEmpty());
	const FStaggerState StateA(*Stagger);
	const FStaggerState ExpectedA(A.StaggerPolicy, A.StaggerProfile);
	TestTrue(TEXT("14 policy fields equal Config A"), StateA.PolicyEquals(ExpectedA));
	TestTrue(TEXT("11 profile fields equal Config A"), StateA.ProfileEquals(ExpectedA));
	TestTrue(TEXT("runtime state unchanged by assignment"), StateA.RuntimeEquals(RuntimeBefore));
	TestFalse(TEXT("component unregistered"), Stagger->IsRegistered());
	TestFalse(TEXT("component not begun"), Stagger->HasBegunPlay());

	const FRPGParticipantConfig B = ConfigB();
	const bool bAssignedB = Plan.Configure(*Stagger, B, Error);
	TestTrue(TEXT("Config B written through plan callback"), bAssignedB && Error.IsEmpty());
	const FStaggerState StateB(*Stagger);
	const FStaggerState ExpectedB(B.StaggerPolicy, B.StaggerProfile);
	TestTrue(TEXT("14 policy fields equal Config B"), StateB.PolicyEquals(ExpectedB));
	TestTrue(TEXT("11 profile fields equal Config B"), StateB.ProfileEquals(ExpectedB));
	TestTrue(TEXT("optional FallMontage is null in StateB"), Stagger->FallMontage.IsNull());
	TestTrue(TEXT("optional GetUpMontage is null in StateB"), Stagger->GetUpMontage.IsNull());
	TestTrue(TEXT("runtime state still unchanged"), StateB.RuntimeEquals(RuntimeBefore));

	return true;
}

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
	TStrongObjectPtr<URPGBossStagger> Stagger = NewStagger(Owner, TEXT("RPGBossStagger"));
	if (!TestTrue(TEXT("component created"), Stagger.IsValid()))
	{
		return false;
	}

	FString Error;

	auto ExpectProfileError = [&](const TCHAR* Label, const FRPGStaggerProfileConfig& Profile, const TCHAR* ExpectedToken)
	{
		Error.Reset();
		const bool bOk = RPGBossStaggerClusterAdapters::ValidateStaggerProfile(Profile, Error);
		TestFalse(FString::Printf(TEXT("%s: rejected"), Label), bOk);
		TestTrue(FString::Printf(TEXT("%s: named %s (got '%s')"), Label, ExpectedToken, *Error), Error.StartsWith(ExpectedToken));
	};

	auto ExpectClusterError = [&](const TCHAR* Label, const FRPGParticipantConfig& Config, const TCHAR* ExpectedToken)
	{
		Error.Reset();
		const FStaggerState Before(*Stagger);
		const bool bValOk = RPGBossStaggerClusterAdapters::ValidateStaggerCluster(Config, Error);
		TestFalse(FString::Printf(TEXT("%s: validate rejected"), Label), bValOk);
		TestTrue(FString::Printf(TEXT("%s: validate named %s (got '%s')"), Label, ExpectedToken, *Error), Error.StartsWith(ExpectedToken));
		FString AssignError;
		const bool bAssignOk = RPGBossStaggerClusterAdapters::ConfigureStaggerCluster(*Stagger, Config, AssignError);
		TestFalse(FString::Printf(TEXT("%s: assign rejected"), Label), bAssignOk);
		TestEqual(FString::Printf(TEXT("%s: errors identical"), Label), AssignError, Error);
		const FStaggerState After(*Stagger);
		TestTrue(FString::Printf(TEXT("%s: component unmodified"), Label), After == Before);
	};

	// 1. HitStunAbilityClassName None
	{
		FRPGStaggerProfileConfig P = NondefaultProfileA();
		P.HitStunAbilityClassName = NAME_None;
		ExpectProfileError(TEXT("HitStun None"), P, TEXT("InvalidStaggerProfile.NoHitStunClass"));
	}

	// 2. Required references missing when bUseClips is false
	{
		FRPGStaggerProfileConfig P = NondefaultProfileA(); // bUseClips = false
		P.FallMontage.Reset();
		ExpectProfileError(TEXT("FallMontage missing when !bUseClips"), P, TEXT("InvalidDependency.Missing"));
		TestTrue(TEXT("names FallMontage"), Error.Contains(RPGBossStaggerClusterAdapters::FieldFallMontage));
	}
	{
		FRPGStaggerProfileConfig P = NondefaultProfileA();
		P.GetUpMontage.Reset();
		ExpectProfileError(TEXT("GetUpMontage missing when !bUseClips"), P, TEXT("InvalidDependency.Missing"));
		TestTrue(TEXT("names GetUpMontage"), Error.Contains(RPGBossStaggerClusterAdapters::FieldGetUpMontage));
	}

	// 3. Required references missing when bUseClips is true
	{
		FRPGStaggerProfileConfig P = NondefaultProfileB(); // bUseClips = true
		P.FallClip.Reset();
		ExpectProfileError(TEXT("FallClip missing when bUseClips"), P, TEXT("InvalidDependency.Missing"));
		TestTrue(TEXT("names FallClip"), Error.Contains(RPGBossStaggerClusterAdapters::FieldFallClip));
	}
	{
		FRPGStaggerProfileConfig P = NondefaultProfileB();
		P.DownClip.Reset();
		ExpectProfileError(TEXT("DownClip missing when bUseClips"), P, TEXT("InvalidDependency.Missing"));
		TestTrue(TEXT("names DownClip"), Error.Contains(RPGBossStaggerClusterAdapters::FieldDownClip));
	}

	// 4. Required references missing when bUseRiposteClips is true
	{
		FRPGStaggerProfileConfig P = NondefaultProfileB(); // bUseRiposteClips = true
		P.RipostePlayerClip.Reset();
		ExpectProfileError(TEXT("RipostePlayerClip missing when bUseRiposteClips"), P, TEXT("InvalidDependency.Missing"));
		TestTrue(TEXT("names RipostePlayerClip"), Error.Contains(RPGBossStaggerClusterAdapters::FieldRipostePlayerClip));
	}
	{
		FRPGStaggerProfileConfig P = NondefaultProfileB();
		P.RiposteBossClip.Reset();
		ExpectProfileError(TEXT("RiposteBossClip missing when bUseRiposteClips"), P, TEXT("InvalidDependency.Missing"));
		TestTrue(TEXT("names RiposteBossClip"), Error.Contains(RPGBossStaggerClusterAdapters::FieldRiposteBossClip));
	}

	// 5. ImmunityEffect always required
	{
		FRPGStaggerProfileConfig P = NondefaultProfileA();
		P.ImmunityEffect.Reset();
		ExpectProfileError(TEXT("ImmunityEffect missing"), P, TEXT("InvalidDependency.Missing"));
		TestTrue(TEXT("names ImmunityEffect"), Error.Contains(RPGBossStaggerClusterAdapters::FieldImmunityEffect));
	}

	// 6. Optional references null are VALID
	{
		FRPGStaggerProfileConfig P = NondefaultProfileB(); // bUseClips = true, bUseRiposteClips = true
		P.FallMontage.Reset();
		P.GetUpMontage.Reset();
		TestTrue(TEXT("null montages valid when bUseClips is true"), RPGBossStaggerClusterAdapters::ValidateStaggerProfile(P, Error));
	}
	{
		FRPGStaggerProfileConfig P = NondefaultProfileA(); // bUseClips = false, bUseRiposteClips = false
		P.RipostePlayerClip.Reset();
		P.RiposteBossClip.Reset();
		P.FallClip.Reset();
		P.DownClip.Reset();
		TestTrue(TEXT("null clips valid when !bUseClips and !bUseRiposteClips"), RPGBossStaggerClusterAdapters::ValidateStaggerProfile(P, Error));
	}

	// 7. Malformed path structures
	{
		FRPGStaggerProfileConfig P = NondefaultProfileA();
		P.FallMontage = MontagePtr(MakePath(TEXT("/SyntheticMount/Bad Path"), TEXT("AM_Fall")));
		ExpectProfileError(TEXT("whitespace in path"), P, TEXT("InvalidDependency.Malformed"));
	}
	{
		FRPGStaggerProfileConfig P = NondefaultProfileA();
		P.FallMontage = MontagePtr(MakePath(TEXT("/SyntheticMount/Sub"), TEXT("AM_Fall"), TEXT("SubObj")));
		ExpectProfileError(TEXT("subobject in path"), P, TEXT("InvalidDependency.Malformed"));
	}
	{
		FRPGStaggerProfileConfig P = NondefaultProfileA();
		P.ImmunityEffect = ClassPtr(MakePath(TEXT("/SyntheticMount/BadClass"), TEXT("GE_Effect")));
		ExpectProfileError(TEXT("not class path"), P, TEXT("InvalidDependency.NotClassPath"));
	}
	{
		FRPGStaggerProfileConfig P = NondefaultProfileA();
		P.ImmunityEffect = ClassPtr(MakePath(TEXT("/Script/GameplayAbilities"), TEXT("GameplayEffect")));
		TestTrue(TEXT("/Script/ class path accepted"), RPGBossStaggerClusterAdapters::ValidateStaggerProfile(P, Error));
	}

	// 8. Both values of bCriticalOnEveryHit valid
	{
		FRPGStaggerProfileConfig P = NondefaultProfileA();
		P.bCriticalOnEveryHit = true;
		TestTrue(TEXT("bCriticalOnEveryHit true is valid"), RPGBossStaggerClusterAdapters::ValidateStaggerProfile(P, Error));
		P.bCriticalOnEveryHit = false;
		TestTrue(TEXT("bCriticalOnEveryHit false is valid"), RPGBossStaggerClusterAdapters::ValidateStaggerProfile(P, Error));
	}

	// 9. Whole-cluster precedence: Policy checked before Profile
	{
		FRPGParticipantConfig C = ConfigA();
		C.StaggerPolicy.StaggerSeconds = -1.f;
		C.StaggerProfile.HitStunAbilityClassName = NAME_None;
		ExpectClusterError(TEXT("policy error precedes profile error"), C, TEXT("InvalidStagger.Negative"));
	}
	{
		FRPGParticipantConfig C = ConfigA();
		C.StaggerPolicy.CriticalMultiplier = 0.5f;
		C.StaggerProfile.ImmunityEffect.Reset();
		ExpectClusterError(TEXT("unsupported critical precedes missing profile dependency"), C, TEXT("UnsupportedNativeCritical"));
	}
	{
		FRPGParticipantConfig C = ConfigA();
		C.StaggerProfile.HitStunAbilityClassName = NAME_None;
		ExpectClusterError(TEXT("profile error reported when policy is valid"), C, TEXT("InvalidStaggerProfile.NoHitStunClass"));
	}

	return true;
}

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
	AActor* OwnerC = Scope.SpawnOwner();
	if (!TestTrue(TEXT("three owners"), OwnerA && OwnerB && OwnerC))
	{
		return false;
	}

	TStrongObjectPtr<URPGBossStagger> StaggerA = NewStagger(OwnerA, TEXT("StaggerA"));
	TStrongObjectPtr<URPGBossStagger> StaggerB = NewStagger(OwnerB, TEXT("StaggerB"));
	TStrongObjectPtr<URPGBossStagger> StaggerUntouched = NewStagger(OwnerC, TEXT("StaggerUntouched"));
	if (!TestTrue(TEXT("components created"), StaggerA.IsValid() && StaggerB.IsValid() && StaggerUntouched.IsValid()))
	{
		return false;
	}

	ArmDistinctStart(*StaggerA);
	ArmDistinctStart(*StaggerB);
	const FStaggerState StartB(*StaggerB);
	const FStaggerState StartUntouched(*StaggerUntouched);

	FRPGParticipantConfig Config = ConfigA();
	FString Error;
	TestTrue(TEXT("configure A"), RPGBossStaggerClusterAdapters::ConfigureStaggerCluster(*StaggerA, Config, Error));

	const FStaggerState StateB(*StaggerB);
	TestTrue(TEXT("component B unchanged by configuration of A"), StateB == StartB);

	const FStaggerState StateUntouched(*StaggerUntouched);
	TestTrue(TEXT("untouched component keeps initial state"), StateUntouched == StartUntouched);
	const URPGBossStagger* CDO = GetDefault<URPGBossStagger>();
	TestTrue(TEXT("CDO untouched: bUseClips"), CDO->bUseClips);
	TestTrue(TEXT("CDO untouched: HitStun"), CDO->HitStunAbilityClassName == FName(TEXT("GA_GS_Boss_HitStun_C")));
	TestTrue(TEXT("CDO untouched: CriticalMultiplier"), CDO->CriticalMultiplier == 2.5f);

	const FStaggerState StateABeforeMutation(*StaggerA);
	Config.StaggerPolicy.StaggerSeconds = 999.f;
	Config.StaggerProfile.bUseClips = !Config.StaggerProfile.bUseClips;
	const FStaggerState StateAAfterMutation(*StaggerA);
	TestTrue(TEXT("mutation of config does not reach StaggerA"), StateAAfterMutation == StateABeforeMutation);

	return true;
}

bool FRPGStaggerClusterRejectionsTest::RunTest(const FString& Parameters)
{
	using namespace StaggerClusterTests;
	FClusterTestWorld Scope;
	if (!TestNotNull(TEXT("test world"), Scope.World))
	{
		return false;
	}
	const FRPGParticipantConfig Config = ConfigA();
	FString Error;

	auto ExpectRejected = [&](const TCHAR* Label, UActorComponent& Component, const TCHAR* Token)
	{
		const URPGBossStagger* AsStagger = Cast<URPGBossStagger>(&Component);
		const URPGBossEncounter* AsEncounter = Cast<URPGBossEncounter>(&Component);
		const URPGBossPosture* AsPosture = Cast<URPGBossPosture>(&Component);
		TOptional<FStaggerState> Before;
		if (AsStagger) { Before.Emplace(*AsStagger); }
		const float EncounterGateBefore = AsEncounter ? AsEncounter->GateRadius : 0.f;
		const float PostureMaxBefore = AsPosture ? AsPosture->PostureMax : 0.f;
		const bool bOk = RPGBossStaggerClusterAdapters::ConfigureStaggerCluster(Component, Config, Error);
		TestFalse(FString::Printf(TEXT("%s: rejected"), Label), bOk);
		TestTrue(FString::Printf(TEXT("%s: named %s (got '%s')"), Label, Token, *Error), Error.StartsWith(Token));
		if (Before.IsSet()) { TestTrue(FString::Printf(TEXT("%s: stagger unchanged"), Label), FStaggerState(*AsStagger) == Before.GetValue()); }
		if (AsEncounter) { TestTrue(FString::Printf(TEXT("%s: encounter configuration untouched"), Label), AsEncounter->GateRadius == EncounterGateBefore); }
		if (AsPosture) { TestTrue(FString::Printf(TEXT("%s: posture configuration untouched"), Label), AsPosture->PostureMax == PostureMaxBefore); }
	};

	AActor* Owner = Scope.SpawnOwner();
	if (!TestNotNull(TEXT("owner actor"), Owner))
	{
		return false;
	}

	// Wrong class: concrete fixtures
	{
		TStrongObjectPtr<URPGBossPosture> Posture(NewObject<URPGBossPosture>(Owner, TEXT("WrongPosture")));
		if (TestTrue(TEXT("posture created"), Posture.IsValid()))
		{
			ExpectRejected(TEXT("wrong class: posture"), *Posture, TEXT("WrongComponentClass"));
		}
	}
	{
		TStrongObjectPtr<URPGBossEncounter> Encounter(NewObject<URPGBossEncounter>(Owner, TEXT("WrongEncounter")));
		if (TestTrue(TEXT("encounter created"), Encounter.IsValid()))
		{
			ExpectRejected(TEXT("wrong class: encounter"), *Encounter, TEXT("WrongComponentClass"));
		}
	}
	{
		TStrongObjectPtr<USceneComponent> Scene(NewObject<USceneComponent>(Owner, TEXT("WrongScene")));
		if (TestTrue(TEXT("scene component created"), Scene.IsValid()))
		{
			ExpectRejected(TEXT("wrong class: scene component"), *Scene, TEXT("WrongComponentClass"));
		}
	}

	// Already registered
	{
		TStrongObjectPtr<URPGBossStagger> Stagger = NewStagger(Owner, TEXT("RegStagger"));
		if (TestTrue(TEXT("stagger created"), Stagger.IsValid()))
		{
			ArmDistinctStart(*Stagger);
			Stagger->RegisterComponent();
			ExpectRejected(TEXT("registered stagger"), *Stagger, TEXT("ComponentAlreadyRegistered"));
		}
	}

	// Component already begun play (clear all 4 clips so begin play does not load assets)
	{
		AActor* BegunOwner = Scope.SpawnOwner();
		if (!TestNotNull(TEXT("begun owner actor"), BegunOwner))
		{
			return false;
		}
		TStrongObjectPtr<URPGBossStagger> Stagger = NewStagger(BegunOwner, TEXT("BegunStagger"));
		if (!TestTrue(TEXT("stagger created"), Stagger.IsValid()))
		{
			return false;
		}
		ArmDistinctStart(*Stagger);
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

	// Owner begun play, component fresh
	{
		AActor* LateOwner = Scope.SpawnOwner();
		if (!TestNotNull(TEXT("late owner actor"), LateOwner))
		{
			return false;
		}
		LateOwner->DispatchBeginPlay();
		if (!TestTrue(TEXT("precondition: owner began play"), LateOwner->HasActorBegunPlay()))
		{
			AddError(TEXT("unsupported precondition: the owner could not be put into begun state"));
			return false;
		}
		TStrongObjectPtr<URPGBossStagger> Stagger = NewStagger(LateOwner, TEXT("LateStagger"));
		if (TestTrue(TEXT("late stagger created"), Stagger.IsValid()))
		{
			ArmDistinctStart(*Stagger);
			ExpectRejected(TEXT("stagger under begun owner"), *Stagger, TEXT("OwnerBegunPlay"));
		}
	}

	// Destroyed retained component
	{
		TStrongObjectPtr<URPGBossStagger> Stagger = NewStagger(Owner, TEXT("DestroyedStagger"));
		if (TestTrue(TEXT("stagger created"), Stagger.IsValid()))
		{
			ArmDistinctStart(*Stagger);
			Stagger->DestroyComponent();
			ExpectRejected(TEXT("destroyed stagger"), *Stagger, TEXT("InvalidComponent"));
		}
	}

	// Destroyed wrong class reported as InvalidComponent
	{
		TStrongObjectPtr<URPGBossPosture> Posture(NewObject<URPGBossPosture>(Owner, TEXT("DestroyedPosture")));
		if (TestTrue(TEXT("posture created"), Posture.IsValid()))
		{
			Posture->DestroyComponent();
			ExpectRejected(TEXT("destroyed wrong-class posture"), *Posture, TEXT("InvalidComponent"));
		}
	}

	return true;
}

bool FRPGStaggerClusterCompileTest::RunTest(const FString& Parameters)
{
	using namespace StaggerClusterTests;
	const FEpochPtr Content = RPGCombatRegistry::Legacy();
	if (!TestTrue(TEXT("content epoch"), Content.IsValid() && Content->Id.IsValid()))
	{
		return false;
	}

	// Synthetic compiler copies both policy and profile records
	{
		const FRPGParticipantConfig A = ConfigA();
		const TStrongObjectPtr<URPGBossDefinition> Definition = MakeDefinition(A);
		FConfigPtr Out;
		const FRPGHydrationResult Result = CompileSynthetic(*Definition, Content, Out);
		if (!TestTrue(TEXT("valid definition compiles"), Result.IsReady() && Out.IsValid()))
		{
			return false;
		}
		TestTrue(TEXT("policy copied"), Out->StaggerPolicy.StaggerSeconds == A.StaggerPolicy.StaggerSeconds && Out->StaggerPolicy.bHoldPostureAtZero == A.StaggerPolicy.bHoldPostureAtZero);
		TestTrue(TEXT("profile copied: bools"), Out->StaggerProfile.bUseClips == A.StaggerProfile.bUseClips && Out->StaggerProfile.bUseRiposteClips == A.StaggerProfile.bUseRiposteClips && Out->StaggerProfile.bCriticalOnEveryHit == A.StaggerProfile.bCriticalOnEveryHit);
		TestTrue(TEXT("profile copied: hit stun"), Out->StaggerProfile.HitStunAbilityClassName == A.StaggerProfile.HitStunAbilityClassName);
		TestTrue(TEXT("profile copied: montages"), Out->StaggerProfile.FallMontage.ToSoftObjectPath() == A.StaggerProfile.FallMontage.ToSoftObjectPath() && Out->StaggerProfile.GetUpMontage.ToSoftObjectPath() == A.StaggerProfile.GetUpMontage.ToSoftObjectPath());
		TestTrue(TEXT("profile copied: clips"), Out->StaggerProfile.FallClip.ToSoftObjectPath() == A.StaggerProfile.FallClip.ToSoftObjectPath() && Out->StaggerProfile.DownClip.ToSoftObjectPath() == A.StaggerProfile.DownClip.ToSoftObjectPath());
		TestTrue(TEXT("profile copied: riposte"), Out->StaggerProfile.RipostePlayerClip.ToSoftObjectPath() == A.StaggerProfile.RipostePlayerClip.ToSoftObjectPath() && Out->StaggerProfile.RiposteBossClip.ToSoftObjectPath() == A.StaggerProfile.RiposteBossClip.ToSoftObjectPath());
		TestTrue(TEXT("profile copied: immunity"), Out->StaggerProfile.ImmunityEffect.ToSoftObjectPath() == A.StaggerProfile.ImmunityEffect.ToSoftObjectPath());
	}

	// Untouched definition copies authoring defaults
	{
		FRPGParticipantConfig DefConfig = ConfigA();
		DefConfig.StaggerProfile = FRPGStaggerProfileConfig();
		const TStrongObjectPtr<URPGBossDefinition> Definition = MakeDefinition(DefConfig);
		FConfigPtr Out;
		const FRPGHydrationResult Result = CompileSynthetic(*Definition, Content, Out);
		TestTrue(TEXT("default profile compiles"), Result.IsReady() && Out.IsValid());
		if (Out.IsValid())
		{
			TestTrue(TEXT("defaults copied: bUseClips"), Out->StaggerProfile.bUseClips == true);
			TestTrue(TEXT("defaults copied: HitStun"), Out->StaggerProfile.HitStunAbilityClassName == FName(TEXT("GA_GS_Boss_HitStun_C")));
		}
	}

	// Invalid cases fail compile by name and clear output
	auto ExpectCompileFail = [&](const TCHAR* Label, const FRPGParticipantConfig& BadConfig, const TCHAR* ExpectedToken)
	{
		const TStrongObjectPtr<URPGBossDefinition> Definition = MakeDefinition(BadConfig);
		FConfigPtr Out = MakeShared<FRPGParticipantConfig>(ConfigA());
		const FRPGHydrationResult Result = CompileSynthetic(*Definition, Content, Out);
		TestFalse(FString::Printf(TEXT("%s: compile failed"), Label), Result.IsReady());
		TestFalse(FString::Printf(TEXT("%s: output cleared"), Label), Out.IsValid());
		bool bFound = false;
		for (const FString& Err : Result.Errors)
		{
			if (Err.Contains(ExpectedToken))
			{
				bFound = true;
				break;
			}
		}
		TestTrue(FString::Printf(TEXT("%s: contains %s"), Label, ExpectedToken), bFound);
	};

	{
		FRPGParticipantConfig Bad = ConfigA();
		Bad.StaggerProfile.HitStunAbilityClassName = NAME_None;
		ExpectCompileFail(TEXT("HitStun None"), Bad, TEXT("InvalidStaggerProfile.NoHitStunClass"));
	}
	{
		FRPGParticipantConfig Bad = ConfigA();
		Bad.StaggerProfile.ImmunityEffect.Reset();
		ExpectCompileFail(TEXT("ImmunityEffect missing"), Bad, TEXT("InvalidDependency.Missing"));
	}
	{
		FRPGParticipantConfig Bad = ConfigA();
		Bad.StaggerPolicy.StaggerSeconds = -5.f;
		ExpectCompileFail(TEXT("negative stagger seconds"), Bad, TEXT("InvalidStagger.Negative"));
	}

	return true;
}

bool FRPGStaggerClusterAuthoringTest::RunTest(const FString& Parameters)
{
	using namespace StaggerClusterTests;
	const UClass* Native = URPGBossStagger::StaticClass();

	const UScriptStruct* ProfileStruct = FRPGStaggerProfileConfig::StaticStruct();
	if (!TestTrue(TEXT("FRPGStaggerProfileConfig reflected"), ProfileStruct != nullptr))
	{
		return false;
	}

	auto CheckBool = [&](const TCHAR* PropName)
	{
		const FProperty* P = ProfileStruct->FindPropertyByName(PropName);
		TestTrue(FString::Printf(TEXT("struct %s: bool editable"), PropName), P && CastField<FBoolProperty>(P) && P->HasAnyPropertyFlags(CPF_Edit));
		const FProperty* NP = Native->FindPropertyByName(PropName);
		TestTrue(FString::Printf(TEXT("native %s: bool editable"), PropName), NP && CastField<FBoolProperty>(NP) && NP->HasAnyPropertyFlags(CPF_Edit));
	};

	CheckBool(TEXT("bUseClips"));
	CheckBool(TEXT("bUseRiposteClips"));
	CheckBool(TEXT("bCriticalOnEveryHit"));

	{
		const FProperty* P = ProfileStruct->FindPropertyByName(TEXT("HitStunAbilityClassName"));
		TestTrue(TEXT("struct HitStun: name editable"), P && CastField<FNameProperty>(P) && P->HasAnyPropertyFlags(CPF_Edit));
		const FProperty* NP = Native->FindPropertyByName(TEXT("HitStunAbilityClassName"));
		TestTrue(TEXT("native HitStun: name editable"), NP && CastField<FNameProperty>(NP) && NP->HasAnyPropertyFlags(CPF_Edit));
	}

	auto CheckSoftObject = [&](const TCHAR* PropName)
	{
		const FProperty* P = ProfileStruct->FindPropertyByName(PropName);
		TestTrue(FString::Printf(TEXT("struct %s: soft object (not class)"), PropName), P && CastField<FSoftObjectProperty>(P) && !CastField<FSoftClassProperty>(P) && P->HasAnyPropertyFlags(CPF_Edit));
		const FProperty* NP = Native->FindPropertyByName(PropName);
		TestTrue(FString::Printf(TEXT("native %s: soft object (not class)"), PropName), NP && CastField<FSoftObjectProperty>(NP) && !CastField<FSoftClassProperty>(NP) && NP->HasAnyPropertyFlags(CPF_Edit));
	};

	CheckSoftObject(TEXT("FallMontage"));
	CheckSoftObject(TEXT("GetUpMontage"));
	CheckSoftObject(TEXT("FallClip"));
	CheckSoftObject(TEXT("DownClip"));
	CheckSoftObject(TEXT("RipostePlayerClip"));
	CheckSoftObject(TEXT("RiposteBossClip"));

	{
		const FProperty* P = ProfileStruct->FindPropertyByName(TEXT("ImmunityEffect"));
		TestTrue(TEXT("struct ImmunityEffect: soft class"), P && CastField<FSoftClassProperty>(P) && P->HasAnyPropertyFlags(CPF_Edit));
		const FProperty* NP = Native->FindPropertyByName(TEXT("ImmunityEffect"));
		TestTrue(TEXT("native ImmunityEffect: soft class"), NP && CastField<FSoftClassProperty>(NP) && NP->HasAnyPropertyFlags(CPF_Edit));
	}

	const UClass* DefClass = URPGBossDefinition::StaticClass();
	const FProperty* DefProp = DefClass->FindPropertyByName(TEXT("StaggerProfile"));
	TestTrue(TEXT("URPGBossDefinition::StaggerProfile reflected"), DefProp && CastField<FStructProperty>(DefProp) && CastField<FStructProperty>(DefProp)->Struct == ProfileStruct && DefProp->HasAnyPropertyFlags(CPF_Edit));

	const URPGBossStagger* CDO = GetDefault<URPGBossStagger>();
	const FRPGStaggerProfileConfig DefProfile;
	TestTrue(TEXT("default bUseClips equals CDO"), DefProfile.bUseClips == CDO->bUseClips);
	TestTrue(TEXT("default bUseRiposteClips equals CDO"), DefProfile.bUseRiposteClips == CDO->bUseRiposteClips);
	TestTrue(TEXT("default bCriticalOnEveryHit equals CDO"), DefProfile.bCriticalOnEveryHit == CDO->bCriticalOnEveryHit);
	TestTrue(TEXT("default HitStun equals CDO"), DefProfile.HitStunAbilityClassName == CDO->HitStunAbilityClassName);
	TestTrue(TEXT("default FallMontage equals CDO"), DefProfile.FallMontage.ToSoftObjectPath() == CDO->FallMontage.ToSoftObjectPath());
	TestTrue(TEXT("default GetUpMontage equals CDO"), DefProfile.GetUpMontage.ToSoftObjectPath() == CDO->GetUpMontage.ToSoftObjectPath());
	TestTrue(TEXT("default FallClip equals CDO"), DefProfile.FallClip.ToSoftObjectPath() == CDO->FallClip.ToSoftObjectPath());
	TestTrue(TEXT("default DownClip equals CDO"), DefProfile.DownClip.ToSoftObjectPath() == CDO->DownClip.ToSoftObjectPath());
	TestTrue(TEXT("default RipostePlayerClip equals CDO"), DefProfile.RipostePlayerClip.ToSoftObjectPath() == CDO->RipostePlayerClip.ToSoftObjectPath());
	TestTrue(TEXT("default RiposteBossClip equals CDO"), DefProfile.RiposteBossClip.ToSoftObjectPath() == CDO->RiposteBossClip.ToSoftObjectPath());
	TestTrue(TEXT("default ImmunityEffect equals CDO"), DefProfile.ImmunityEffect.ToSoftObjectPath() == CDO->ImmunityEffect.ToSoftObjectPath());

	FString ValError;
	TestTrue(TEXT("default profile passes validator"), RPGBossStaggerClusterAdapters::ValidateStaggerProfile(DefProfile, ValError));

	return true;
}

bool FRPGStaggerClusterOracleTest::RunTest(const FString& Parameters)
{
	using namespace StaggerClusterTests;
	FClusterTestWorld Scope;
	if (!TestNotNull(TEXT("test world"), Scope.World))
	{
		return false;
	}

	struct FCase { const TCHAR* Name; FRPGParticipantConfig Config; };
	const FRPGParticipantConfig DefConfig;
	const FCase Cases[] = {
		{TEXT("config A"), ConfigA()},
		{TEXT("config B"), ConfigB()},
		{TEXT("authoring defaults"), DefConfig}
	};

	for (const FCase& Case : Cases)
	{
		AActor* OwnerOracle = Scope.SpawnOwner();
		AActor* OwnerCluster = Scope.SpawnOwner();
		if (!TestTrue(TEXT("two owners"), OwnerOracle && OwnerCluster))
		{
			return false;
		}

		TStrongObjectPtr<URPGBossStagger> Oracle = NewStagger(OwnerOracle, TEXT("OracleStagger"));
		TStrongObjectPtr<URPGBossStagger> Cluster = NewStagger(OwnerCluster, TEXT("ClusterStagger"));
		if (!TestTrue(TEXT("two components"), Oracle.IsValid() && Cluster.IsValid()))
		{
			return false;
		}

		ArmDistinctStart(*Oracle);
		ArmDistinctStart(*Cluster);
		const FStaggerState Start(*Cluster);

		FString OracleError;
		FString ClusterError;
		const bool bOracleOk = RPGBossStaggerPolicyAdapters::ConfigureStaggerPolicy(*Oracle, Case.Config, OracleError);
		const bool bClusterOk = RPGBossStaggerClusterAdapters::ConfigureStaggerCluster(*Cluster, Case.Config, ClusterError);
		TestTrue(FString::Printf(TEXT("%s: older adapter and cluster both accept"), Case.Name), bOracleOk && bClusterOk);

		const FStaggerState OracleState(*Oracle);
		const FStaggerState ClusterState(*Cluster);

		TestTrue(FString::Printf(TEXT("%s: 14 policy fields equal older adapter"), Case.Name), ClusterState.PolicyEquals(OracleState));
		TestTrue(FString::Printf(TEXT("%s: older adapter leaves profile fields at start"), Case.Name), OracleState.ProfileEquals(Start));

		TestTrue(FString::Printf(TEXT("%s: cluster profile fields match config"), Case.Name),
			ClusterState.bUseClips == Case.Config.StaggerProfile.bUseClips
			&& ClusterState.bUseRiposteClips == Case.Config.StaggerProfile.bUseRiposteClips
			&& ClusterState.bCriticalOnEveryHit == Case.Config.StaggerProfile.bCriticalOnEveryHit
			&& ClusterState.HitStunAbilityClassName == Case.Config.StaggerProfile.HitStunAbilityClassName
			&& ClusterState.FallMontage == Case.Config.StaggerProfile.FallMontage.ToSoftObjectPath()
			&& ClusterState.GetUpMontage == Case.Config.StaggerProfile.GetUpMontage.ToSoftObjectPath()
			&& ClusterState.FallClip == Case.Config.StaggerProfile.FallClip.ToSoftObjectPath()
			&& ClusterState.DownClip == Case.Config.StaggerProfile.DownClip.ToSoftObjectPath()
			&& ClusterState.RipostePlayerClip == Case.Config.StaggerProfile.RipostePlayerClip.ToSoftObjectPath()
			&& ClusterState.RiposteBossClip == Case.Config.StaggerProfile.RiposteBossClip.ToSoftObjectPath()
			&& ClusterState.ImmunityEffect == Case.Config.StaggerProfile.ImmunityEffect.ToSoftObjectPath());

		TestTrue(FString::Printf(TEXT("%s: runtime state equal and unchanged"), Case.Name), ClusterState.RuntimeEquals(OracleState) && ClusterState.RuntimeEquals(Start));
	}

	// No object or package loaded when assigning real default asset paths
	{
		AActor* Owner = Scope.SpawnOwner();
		if (!TestNotNull(TEXT("owner actor"), Owner))
		{
			return false;
		}
		TStrongObjectPtr<URPGBossStagger> Stagger = NewStagger(Owner, TEXT("NoLoadStagger"));
		if (!TestTrue(TEXT("component created"), Stagger.IsValid()))
		{
			return false;
		}
		ArmDistinctStart(*Stagger);

		const FRPGStaggerProfileConfig RealDefaults;
		const FSoftObjectPath RealPaths[] = {
			RealDefaults.FallMontage.ToSoftObjectPath(),
			RealDefaults.GetUpMontage.ToSoftObjectPath(),
			RealDefaults.FallClip.ToSoftObjectPath(),
			RealDefaults.DownClip.ToSoftObjectPath(),
			RealDefaults.RipostePlayerClip.ToSoftObjectPath(),
			RealDefaults.RiposteBossClip.ToSoftObjectPath(),
			RealDefaults.ImmunityEffect.ToSoftObjectPath()
		};

		bool bLoadedBefore[7];
		bool bPackageBefore[7];
		for (int32 Index = 0; Index < 7; ++Index)
		{
			bLoadedBefore[Index] = RealPaths[Index].ResolveObject() != nullptr;
			bPackageBefore[Index] = FindPackage(nullptr, *RealPaths[Index].GetLongPackageName()) != nullptr;
		}

		FRPGParticipantConfig Config = ConfigA();
		Config.StaggerProfile = RealDefaults;
		FString Error;
		TestTrue(TEXT("real defaults assign successfully"), RPGBossStaggerClusterAdapters::ConfigureStaggerCluster(*Stagger, Config, Error));

		for (int32 Index = 0; Index < 7; ++Index)
		{
			const bool bLoadedAfter = RealPaths[Index].ResolveObject() != nullptr;
			const bool bPackageAfter = FindPackage(nullptr, *RealPaths[Index].GetLongPackageName()) != nullptr;
			TestTrue(FString::Printf(TEXT("asset %d was not loaded by assignment"), Index), bLoadedAfter == bLoadedBefore[Index]);
			TestTrue(FString::Printf(TEXT("package %d was not created by assignment"), Index), bPackageAfter == bPackageBefore[Index]);
		}
	}

	return true;
}
