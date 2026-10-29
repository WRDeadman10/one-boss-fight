// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossBleed.h"
#include "Player/RPGBossLowSweep.h"
#include "Player/RPGBossShockwave.h"
#include "Player/RPGBossHealPunish.h"
#include "Player/RPGBossLook.h"
#include "Player/RPGBossCloseClipSwap.h"
#include "Player/RPGBossDeath.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Animation/AnimSequence.h"
#include "Animation/AnimSequenceBase.h"
#include "Animation/Skeleton.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/Engine.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "Player/RPGBossDormantWake.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossHydrationPreflight.h"
#include "Player/RPGBossPhases.h"
#include "Player/RPGBossPosture.h"
#include "Player/RPGBossStagger.h"
#include "UObject/Package.h"
#include "UObject/StrongObjectPtr.h"

// DD14: a production fixture for the expanded native subset preflight, built from REAL pack assets and the REAL production compiler (RPGCombatHydration::CompileParticipant, bSyntheticFixture false), nothing synthetic
// substituted for a positive result.
// What it uses: the two pack character Blueprint classes are loaded only to READ the mesh asset their default object holds (no Blueprint actor is spawned, no default object is changed, no asset is saved); the observed
// mesh and its skeleton are placed on two ISOLATED native ACharacter actors in a test-local headless game world that never begins play; the animation dependencies are the authoring-default cooked-directory candidates
// of the typed records; the definitions are transient; the content epoch is the existing legacy registry epoch.
// What it can establish: that, for these exact assets in this editor binary, the production compiler loads the skeleton and every listed animation, every animation is on the skeleton, the actor meshes are compatible with
// the skeleton, and the preflight then publishes twelve plans for the boss and none for the target. A mismatch is a real finding and fails the test with the observed names; nothing is retargeted, substituted or weakened.
// What it does NOT establish: a cold load (the pack classes are loaded first and the assets may already be in memory; the state before the fixture is only logged), the packaged or cooked build, the arena level, the placed
// Blueprint boss, an ability or gameplay effect (class paths are structural only), animation playback or root motion, the real boss definition asset (the typed values, phase list and manifest rows are fixture values, not
// authority), a game-instance content epoch, BeginPlay, registration, context binding, activation or any wiring. The plans are built and never run.

namespace
{
namespace ProductionPreflightTests
{
	using FEpochPtr = TSharedPtr<const RPGCombatRegistry::FEpoch>;
	using FConfigPtr = TSharedPtr<const FRPGParticipantConfig>;
	using FPlanPtr = TSharedPtr<const FRPGHydrationPreflightPlan>;

	const FName PhaseTwo(TEXT("PhaseTwo"));

	// The two pack character classes, under always-cooked directories. Only their default object's mesh is read.
	const TCHAR* const PlayerClassPath = TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter.BP_CombatPlayerCharacter_C");
	const TCHAR* const BossClassPath = TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss.BP_ExampleGreatSwordBoss_C");

	/** Test-local headless game world (same set-up as the earlier preflight tests), destroyed with the scope. */
	struct FProductionWorld
	{
		UWorld* World = nullptr;

		FProductionWorld()
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

		~FProductionWorld()
		{
			if (World)
			{
				GEngine->DestroyWorldContext(World);
				World->DestroyWorld(/*bInformEngineOfWorld=*/false);
			}
		}

		FProductionWorld(const FProductionWorld&) = delete;
		FProductionWorld& operator=(const FProductionWorld&) = delete;

		/** A native ACharacter (never a Blueprint actor). The mesh asset, when given, is set BEFORE the actor is finished, so it is never begun play. */
		ACharacter* SpawnCharacter(USkeletalMesh* Mesh, const FVector& Location) const
		{
			if (!World)
			{
				return nullptr;
			}
			ACharacter* Character = World->SpawnActorDeferred<ACharacter>(ACharacter::StaticClass(), FTransform(Location));
			if (!Character)
			{
				return nullptr;
			}
			if (Mesh && Character->GetMesh())
			{
				Character->GetMesh()->SetSkeletalMeshAsset(Mesh);
			}
			Character->FinishSpawning(FTransform(Location));
			return Character;
		}
	};

	/** The 110 unique manifest paths the twelve combined boss-core plans read, written out as independent literals. Membership only. */
	TArray<FString> AllRequiredPaths(FName PhaseId)
	{
		const FString Id = PhaseId.ToString();
		return TArray<FString>{
			TEXT("StaggerPolicy.StaggerSeconds"), TEXT("StaggerPolicy.FreezeAtPosition"), TEXT("StaggerPolicy.CriticalMultiplier"), TEXT("StaggerPolicy.RiposteRange"), TEXT("StaggerPolicy.RiposteConeDegrees"),
			TEXT("StaggerPolicy.RiposteFacingDegrees"), TEXT("StaggerPolicy.RiposteArmSeconds"), TEXT("StaggerPolicy.RipostePlayerStartGap"), TEXT("StaggerPolicy.RiposteAlignSeconds"), TEXT("StaggerPolicy.RiposteImpactSeconds"),
			TEXT("StaggerPolicy.RiposteBaseDamage"), TEXT("StaggerPolicy.CooldownSeconds"), TEXT("StaggerPolicy.GetUpRate"), TEXT("StaggerPolicy.bHoldPostureAtZero"),
			TEXT("StaggerProfile.bUseClips"), TEXT("StaggerProfile.bUseRiposteClips"), TEXT("StaggerProfile.bCriticalOnEveryHit"), TEXT("StaggerProfile.HitStunAbilityClassName"), TEXT("StaggerProfile.FallMontage"),
			TEXT("StaggerProfile.GetUpMontage"), TEXT("StaggerProfile.FallClip"), TEXT("StaggerProfile.DownClip"), TEXT("StaggerProfile.RipostePlayerClip"), TEXT("StaggerProfile.RiposteBossClip"), TEXT("StaggerProfile.ImmunityEffect"),
			FString::Printf(TEXT("Phases[%s].EntryHealthFraction"), *Id), FString::Printf(TEXT("Phases[%s].SpeedMultiplier"), *Id), FString::Printf(TEXT("Phases[%s].RateMultiplier"), *Id), FString::Printf(TEXT("Phases[%s].AttackMultiplier"), *Id),
			TEXT("PhaseFlow.TransitionSeconds"), TEXT("PhaseFlow.bUseRoarClip"), TEXT("PhaseFlow.bPausePostureInTransition"), TEXT("PhaseFlow.bLockLeapUntilPhaseTwo"), TEXT("PhaseFlow.AttackAbilityPrefix"), TEXT("PhaseFlow.LeapAbilityTag"),
			TEXT("Fireball.bFireballEnabled"), TEXT("Fireball.FireballAbility"), TEXT("Fireball.FireballCooldown"), TEXT("Fireball.FireballMinRange"), TEXT("Fireball.FireballMaxRange"),
			TEXT("PhaseDependencies.RoarClip"), TEXT("PhaseDependencies.TransitionMontage"), TEXT("PhaseDependencies.ImmunityEffect"),
			TEXT("Stats.MaxHealth"), TEXT("EncounterPolicy.GateRadius"), TEXT("EncounterPolicy.bResetOnPlayerRespawn"),
			TEXT("DormantWake.DormantClip"), TEXT("DormantWake.WakeClip"),
			TEXT("Stats.MaxPosture"), TEXT("Stats.PostureRegenDelay"), TEXT("Stats.PostureRegenRate"),
			// Independent production-preflight fixture membership, not factory-derived.
			TEXT("Bleed.InitialThreshold"), TEXT("Bleed.ThresholdIncrease"), TEXT("Bleed.ThresholdMax"), TEXT("Bleed.HpFraction"), TEXT("Bleed.EffectHeight"), TEXT("Bleed.ProcEffect"), TEXT("Bleed.ProcSound"),
			TEXT("LowSweep.bEnabled"), TEXT("LowSweep.MoveId"), TEXT("LowSweep.Damage"), TEXT("LowSweep.Reach"), TEXT("LowSweep.InnerRadius"), TEXT("LowSweep.BladeHeight"), TEXT("LowSweep.SweepFromDegrees"), TEXT("LowSweep.SweepToDegrees"),
			TEXT("Shockwave.bEnabled"), TEXT("Shockwave.MoveId"), TEXT("Shockwave.Damage"), TEXT("Shockwave.StartRadius"), TEXT("Shockwave.MaxRadius"), TEXT("Shockwave.Speed"), TEXT("Shockwave.Thickness"), TEXT("Shockwave.JumpClearance"),
			TEXT("HealPunish.bEnabled"), TEXT("HealPunish.MinRange"), TEXT("HealPunish.MaxRange"), TEXT("HealPunish.Cooldown"), TEXT("HealPunish.Damage"), TEXT("HealPunish.FlightTime"), TEXT("HealPunish.MinSpeed"), TEXT("HealPunish.MaxSpeed"), TEXT("HealPunish.JavelinRadius"), TEXT("HealPunish.JavelinMaxRange"), TEXT("HealPunish.SpawnSockets"), TEXT("HealPunish.AimHeight"), TEXT("HealPunish.bRespondToHeal"), TEXT("HealPunish.bCancelJavelinsOnInterrupt"),
			TEXT("Look.bEnabled"), TEXT("Look.Body"), TEXT("Look.Pieces"), TEXT("Look.Sword"), TEXT("Look.SwordSocket"),
			TEXT("CloseClipSwap.CloseAbilityClassName"), TEXT("CloseClipSwap.AttackMontagesName"), TEXT("CloseClipSwap.A1Montage"), TEXT("CloseClipSwap.A3aMontage"), TEXT("CloseClipSwap.A3bMontage"),
			TEXT("Death.DeathMode"), TEXT("Death.DeathClip"), TEXT("Death.DeathMontage"), TEXT("Death.PackDeathAbilityClassName"), TEXT("Death.PackDeathMontagesName"), TEXT("Death.PackPollSeconds"), TEXT("Death.PackEndTimeMultiplier"), TEXT("Death.HoldAtSeconds"), TEXT("Death.DyingSeconds"), TEXT("Death.BlendInSeconds"), TEXT("Death.MaxClipRestarts"), TEXT("Death.bGuardPackDeath")};
	}

	/** A manifest row supplied by this fixture: it satisfies the production compiler's row shape and the preflight's membership check; it is not derived from any asset and carries no authority. */
	FRPGParityField MakeProductionField(const FString& Path)
	{
		FRPGParityField Field;
		Field.FieldPath = Path;
		Field.Type = TEXT("fixture");
		Field.Value = TEXT("production fixture row: membership only, not derived from an asset");
		Field.SourcePath = TEXT("DD14 production preflight fixture, not live provenance");
		Field.SourceSHA256 = FString::ChrN(64, TEXT('c'));
		Field.SourceSite = TEXT("fixture");
		Field.Origin = TEXT("harness");
		Field.Precedence = TEXT("fixture");
		Field.Destination = TEXT("fixture");
		Field.FirstRead = TEXT("not read");
		Field.Witness = TEXT("none: structural membership only");
		return Field;
	}

	/** The boss animation dependencies: the cooked-directory authoring-default candidates of the dormant wake, phase dependency and stagger profile records (twenty-three paths: twelve sequences, three montages and the riposte reaction). */
	TArray<FSoftObjectPath> BossAnimationPaths()
	{
		FRPGDormantWakeConfig Wake;
		FRPGPhaseDependencyConfig Dependencies;
		FRPGStaggerProfileConfig Profile;
		return TArray<FSoftObjectPath>{Wake.DormantClip.ToSoftObjectPath(), Wake.WakeClip.ToSoftObjectPath(), Dependencies.RoarClip.ToSoftObjectPath(), Dependencies.TransitionMontage.ToSoftObjectPath(),
			Profile.FallMontage.ToSoftObjectPath(), Profile.GetUpMontage.ToSoftObjectPath(), Profile.FallClip.ToSoftObjectPath(), Profile.DownClip.ToSoftObjectPath(), Profile.RiposteBossClip.ToSoftObjectPath()};
	}

	/** The player animation dependency: the riposte clip of the player. */
	TArray<FSoftObjectPath> PlayerAnimationPaths()
	{
		FRPGStaggerProfileConfig Profile;
		return TArray<FSoftObjectPath>{Profile.RipostePlayerClip.ToSoftObjectPath()};
	}

	/** Valid typed fixture values for the whole record. The typed records are set explicitly to the authoring defaults (the cooked-directory candidates): valid structurally, not claimed to be the authored boss values. */
	void FillDefinition(URPGBossDefinition& Definition, const TCHAR* Id, const TCHAR* Look, USkeleton* Skeleton, const TArray<FSoftObjectPath>& AnimationPaths)
	{
		Definition.Schema = 1;
		Definition.DefinitionId = FName(Id);
		Definition.PresentationId = FName(Look);
		Definition.Stats.MaxHealth = 3500.f;
		Definition.Stats.MaxPosture = 73.5f;
		Definition.Stats.PostureRegenDelay = 4.25f;
		Definition.Stats.PostureRegenRate = 9.75f;
		Definition.EncounterPolicy = FRPGEncounterPolicyConfig();
		Definition.StaggerPolicy = FRPGStaggerPolicyConfig();
		Definition.PhaseFlow = FRPGPhaseFlowConfig();
		Definition.Fireball = FRPGFireballConfig();
		Definition.PhaseDependencies = FRPGPhaseDependencyConfig();
		Definition.StaggerProfile = FRPGStaggerProfileConfig();
		Definition.DormantWake = FRPGDormantWakeConfig();
		FRPGPhaseConfig Phase;
		Phase.PhaseId = PhaseTwo;
		Phase.EntryHealthFraction = 0.35f;
		Phase.SpeedMultiplier = 1.5f;
		Phase.RateMultiplier = 1.75f;
		Phase.AttackMultiplier = 2.f;
		Definition.Phases.Reset();
		Definition.Phases.Add(Phase);
		Definition.Skeleton = TSoftObjectPtr<USkeleton>(Skeleton);
		Definition.Animations.Reset();
		for (const FSoftObjectPath& Path : AnimationPaths)
		{
			Definition.Animations.Add(TSoftObjectPtr<UAnimSequenceBase>(Path));
		}
		Definition.Fields.Reset();
		for (const FString& Path : AllRequiredPaths(PhaseTwo))
		{
			Definition.Fields.Add(MakeProductionField(Path));
		}
	}

	FString ManifestHash()
	{
		return FString::ChrN(64, TEXT('b')); // a fixture hash, not a real manifest hash
	}

	FString Describe(const UObject* Object)
	{
		return Object ? FString::Printf(TEXT("%s (%s)"), *Object->GetPathName(), *Object->GetClass()->GetName()) : FString(TEXT("none"));
	}

	/** Everything a compile must leave alone: per actor the component count, the begun flag and the presence of each managed consumer; and the world's combat context counts. */
	TArray<int32> CaptureState(UWorld* World)
	{
		TArray<int32> State;
		const TArray<UClass*> Managed = RPGBossHydrationPreflight::ManagedCoreConsumerClasses();
		for (TActorIterator<AActor> It(World); It; ++It)
		{
			State.Add(It->GetComponents().Num());
			State.Add(It->HasActorBegunPlay() ? 1 : 0);
			for (UClass* Class : Managed)
			{
				State.Add(It->FindComponentByClass(Class) ? 1 : 0);
			}
		}
		if (const URPGCombatContextSubsystem* Context = World->GetSubsystem<URPGCombatContextSubsystem>())
		{
			State.Add(Context->GetBoundCount());
			State.Add(Context->GetReadyCount());
		}
		return State;
	}

	/** The dirty flag of the package of each object, compared around the preflight and the negative cases only (the class load, the spawn and the production compile happen before the first snapshot and are not covered). */
	TArray<int32> CaptureDirty(const TArray<const UObject*>& Objects)
	{
		TArray<int32> Flags;
		for (const UObject* Object : Objects)
		{
			const UPackage* Package = Object ? Object->GetOutermost() : nullptr;
			Flags.Add(Package ? (Package->IsDirty() ? 1 : 0) : -1);
		}
		return Flags;
	}

	bool AnyErrorStartsWith(const FRPGHydrationResult& Result, const TCHAR* Token)
	{
		return Result.Errors.ContainsByPredicate([Token](const FString& E) { return E.StartsWith(Token); });
	}

	bool AnyErrorContains(const FRPGHydrationResult& Result, const FString& Text)
	{
		return Result.Errors.ContainsByPredicate([&Text](const FString& E) { return E.Contains(Text); });
	}

	FString JoinErrors(const FRPGHydrationResult& Result)
	{
		return FString::Join(Result.Errors, TEXT(" | "));
	}

	FRPGHydrationPreflightRequest MakeRequest(AActor* Actor, const TCHAR* Slot, const TCHAR* Target, ERPGPreflightRole Role, FConfigPtr Config, FName Phase = NAME_None)
	{
		FRPGHydrationPreflightRequest Request;
		Request.Actor = Actor;
		Request.Slot = FName(Slot);
		Request.TargetSlot = FName(Target);
		Request.Role = Role;
		Request.Config = Config;
		Request.SelectedPhaseId = Phase;
		return Request;
	}

	/** The clone of a production config for a negative case: every record and lease is re-supplied by hand (no whole-config copy), bSyntheticFixture stays false, then the case changes one thing. */
	FConfigPtr CloneProduction(const FRPGParticipantConfig& Source, const TFunction<void(FRPGParticipantConfig&)>& Mutate)
	{
		TSharedRef<FRPGParticipantConfig> Copy = MakeShared<FRPGParticipantConfig>();
		Copy->BossId = Source.BossId;
		Copy->PresentationId = Source.PresentationId;
		Copy->StableManifestHash = Source.StableManifestHash;
		Copy->Schema = Source.Schema;
		Copy->Stats = Source.Stats;
		Copy->EncounterPolicy = Source.EncounterPolicy;
		Copy->StaggerPolicy = Source.StaggerPolicy;
		Copy->PhaseFlow = Source.PhaseFlow;
		Copy->Fireball = Source.Fireball;
		Copy->PhaseDependencies = Source.PhaseDependencies;
		Copy->StaggerProfile = Source.StaggerProfile;
		Copy->DormantWake = Source.DormantWake;
		Copy->Phases = Source.Phases;
		Copy->Fields = Source.Fields;
		Copy->Content = Source.Content;
		Copy->bSyntheticFixture = false;
		Copy->Skeleton.Reset(Source.Skeleton.Get());
		for (const TStrongObjectPtr<UAnimSequenceBase>& Animation : Source.Animations)
		{
			Copy->Animations.Emplace(Animation.Get());
		}
		if (Mutate)
		{
			Mutate(*Copy);
		}
		return Copy;
	}

	/** The real pack mesh and skeleton, the two isolated native actors, the two transient definitions and (on request) the two production configs. Everything observed is logged; a missing precondition is reported as such. */
	struct FProductionFixture
	{
		FProductionWorld Scope;
		UClass* PlayerClass = nullptr;
		UClass* BossClass = nullptr;
		USkeletalMesh* PlayerMesh = nullptr;
		USkeletalMesh* BossMesh = nullptr;
		USkeleton* PlayerSkeleton = nullptr;
		USkeleton* BossSkeleton = nullptr;
		ACharacter* BossActor = nullptr;
		ACharacter* PlayerActor = nullptr;
		FEpochPtr Content;
		TStrongObjectPtr<URPGBossDefinition> BossDefinition;
		TStrongObjectPtr<URPGBossDefinition> PlayerDefinition;
		FConfigPtr BossConfig;
		FConfigPtr PlayerConfig;
		FRPGHydrationResult BossCompile;
		FRPGHydrationResult PlayerCompile;

		/** Builds everything up to (and not including) the production compile. False (with an error naming the unsupported precondition) when a precondition cannot be built. */
		bool Prepare(FAutomationTestBase& Test)
		{
			if (!Scope.World)
			{
				Test.AddError(TEXT("unsupported precondition: the headless game world could not be created"));
				return false;
			}
			// What was already in memory before this test touched anything (the pack classes load their own dependencies, so this is not a cold-load claim).
			TArray<FSoftObjectPath> Candidates = BossAnimationPaths();
			Candidates.Append(PlayerAnimationPaths());
			for (const FSoftObjectPath& Path : Candidates)
			{
				Test.AddInfo(FString::Printf(TEXT("before the fixture: %s in memory = %s"), *Path.ToString(), Path.ResolveObject() ? TEXT("yes") : TEXT("no")));
			}
			PlayerClass = LoadClass<ACharacter>(nullptr, PlayerClassPath);
			BossClass = LoadClass<ACharacter>(nullptr, BossClassPath);
			if (!PlayerClass || !BossClass)
			{
				Test.AddError(FString::Printf(TEXT("unsupported precondition: a pack character class did not load (player %s, boss %s)"), *Describe(PlayerClass), *Describe(BossClass)));
				return false;
			}
			const ACharacter* PlayerDefault = Cast<ACharacter>(PlayerClass->GetDefaultObject());
			const ACharacter* BossDefault = Cast<ACharacter>(BossClass->GetDefaultObject());
			PlayerMesh = PlayerDefault && PlayerDefault->GetMesh() ? PlayerDefault->GetMesh()->GetSkeletalMeshAsset() : nullptr;
			BossMesh = BossDefault && BossDefault->GetMesh() ? BossDefault->GetMesh()->GetSkeletalMeshAsset() : nullptr;
			PlayerSkeleton = PlayerMesh ? PlayerMesh->GetSkeleton() : nullptr;
			BossSkeleton = BossMesh ? BossMesh->GetSkeleton() : nullptr;
			Test.AddInfo(FString::Printf(TEXT("player class %s | default object mesh %s | skeleton %s"), *Describe(PlayerClass), *Describe(PlayerMesh), *Describe(PlayerSkeleton)));
			Test.AddInfo(FString::Printf(TEXT("boss class %s | default object mesh %s | skeleton %s"), *Describe(BossClass), *Describe(BossMesh), *Describe(BossSkeleton)));
			if (!PlayerMesh || !BossMesh || !PlayerSkeleton || !BossSkeleton)
			{
				Test.AddError(TEXT("unsupported precondition: a pack character default object holds no skeletal mesh or the mesh has no skeleton"));
				return false;
			}
			BossActor = Scope.SpawnCharacter(BossMesh, FVector(0.f, 0.f, 0.f));
			PlayerActor = Scope.SpawnCharacter(PlayerMesh, FVector(1000.f, 0.f, 0.f));
			if (!BossActor || !PlayerActor)
			{
				Test.AddError(TEXT("unsupported precondition: the two isolated native character actors could not be spawned"));
				return false;
			}
			Content = RPGCombatRegistry::Legacy();
			if (!Content.IsValid())
			{
				Test.AddError(TEXT("unsupported precondition: the legacy content epoch is not available"));
				return false;
			}
			BossDefinition.Reset(NewObject<URPGBossDefinition>());
			PlayerDefinition.Reset(NewObject<URPGBossDefinition>());
			if (!BossDefinition.IsValid() || !PlayerDefinition.IsValid())
			{
				Test.AddError(TEXT("unsupported precondition: the transient definitions could not be created"));
				return false;
			}
			FillDefinition(*BossDefinition, TEXT("ProductionBoss"), TEXT("ProductionBossLook"), BossSkeleton, BossAnimationPaths());
			FillDefinition(*PlayerDefinition, TEXT("ProductionPlayer"), TEXT("ProductionPlayerLook"), PlayerSkeleton, PlayerAnimationPaths());
			return true;
		}

		/** The genuine production compiler for both participants. */
		void CompileProduction()
		{
			BossCompile = RPGCombatHydration::CompileParticipant(*BossDefinition, Content, ManifestHash(), BossConfig);
			PlayerCompile = RPGCombatHydration::CompileParticipant(*PlayerDefinition, Content, ManifestHash(), PlayerConfig);
		}

		FRPGHydrationPreflightInput MakeInput() const
		{
			FRPGHydrationPreflightInput Input;
			Input.ExpectedWorld = Scope.World;
			Input.EncounterInstance = FGuid::NewGuid();
			Input.ExpectedContent = Content;
			Input.Requests.Add(MakeRequest(BossActor, TEXT("Boss"), TEXT("Player"), ERPGPreflightRole::BossCore, BossConfig, PhaseTwo));
			Input.Requests.Add(MakeRequest(PlayerActor, TEXT("Player"), TEXT("Boss"), ERPGPreflightRole::TargetOnly, PlayerConfig));
			return Input;
		}

		TArray<const UObject*> TouchedObjects() const
		{
			TArray<const UObject*> Objects{PlayerClass, BossClass, PlayerMesh, BossMesh, PlayerSkeleton, BossSkeleton};
			for (const FConfigPtr& Config : {BossConfig, PlayerConfig})
			{
				if (Config.IsValid())
				{
					for (const TStrongObjectPtr<UAnimSequenceBase>& Animation : Config->Animations)
					{
						Objects.Add(Animation.Get());
					}
				}
			}
			return Objects;
		}
	};

	/** The compile of both production participants, reported as real evidence: a failure lists the compiler's exact errors. */
	bool ExpectProductionCompiled(FAutomationTestBase& Test, const FProductionFixture& F)
	{
		bool bOk = true;
		bOk &= Test.TestTrue(FString::Printf(TEXT("production CompileParticipant of the boss succeeded (errors: %s)"), *JoinErrors(F.BossCompile)), F.BossCompile.IsReady() && F.BossConfig.IsValid());
		bOk &= Test.TestTrue(FString::Printf(TEXT("production CompileParticipant of the player succeeded (errors: %s)"), *JoinErrors(F.PlayerCompile)), F.PlayerCompile.IsReady() && F.PlayerConfig.IsValid());
		return bOk;
	}

	/** A failing batch: refused with the named token and the detail text, the earlier output cleared, no actor, component or context changed. */
	bool ExpectRejected(FAutomationTestBase& Test, const FProductionFixture& F, const TCHAR* Label, const FRPGHydrationPreflightInput& Input, const TCHAR* Token, const TCHAR* Detail, const FPlanPtr& Prior)
	{
		FPlanPtr Out = Prior; // a valid earlier plan: a failure must not leave it in place
		const TArray<int32> Before = CaptureState(F.Scope.World);
		const FRPGHydrationResult Result = RPGBossHydrationPreflight::CompilePreflight(Input, Out);
		bool bOk = true;
		bOk &= Test.TestFalse(FString::Printf(TEXT("%s: refused"), Label), Result.IsReady());
		bOk &= Test.TestFalse(FString::Printf(TEXT("%s: the earlier output was cleared and no plan was published"), Label), Out.IsValid());
		bOk &= Test.TestTrue(FString::Printf(TEXT("%s: a failure named %s (got: %s)"), Label, Token, *JoinErrors(Result)), AnyErrorStartsWith(Result, Token));
		bOk &= Test.TestTrue(FString::Printf(TEXT("%s: the failure carries '%s' (got: %s)"), Label, Detail, *JoinErrors(Result)), AnyErrorContains(Result, FString(Detail)));
		bOk &= Test.TestTrue(FString::Printf(TEXT("%s: no actor, component or combat context changed"), Label), CaptureState(F.Scope.World) == Before);
		return bOk;
	}
}
}

using namespace ProductionPreflightTests;

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGProductionPreflightPositiveTest, "OneBossFight.Binding.ProductionPreflight.PositiveBatch",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGProductionPreflightPositiveTest::RunTest(const FString& Parameters)
{
	FProductionFixture F;
	if (!F.Prepare(*this))
	{
		return false;
	}

	// The isolated actors: native characters, holding the observed pack meshes, never begun play, no managed consumer.
	TestTrue(TEXT("the boss actor holds the observed boss mesh"), F.BossActor->GetMesh() && F.BossActor->GetMesh()->GetSkeletalMeshAsset() == F.BossMesh);
	TestTrue(TEXT("the player actor holds the observed player mesh"), F.PlayerActor->GetMesh() && F.PlayerActor->GetMesh()->GetSkeletalMeshAsset() == F.PlayerMesh);
	TestTrue(TEXT("the actors are native ACharacter objects, not Blueprint actors"), F.BossActor->GetClass() == ACharacter::StaticClass() && F.PlayerActor->GetClass() == ACharacter::StaticClass());
	TestTrue(TEXT("neither actor has begun play"), !F.BossActor->HasActorBegunPlay() && !F.PlayerActor->HasActorBegunPlay());
	for (UClass* Managed : RPGBossHydrationPreflight::ManagedCoreConsumerClasses())
	{
		TestTrue(FString::Printf(TEXT("neither actor has a %s before the compile"), *Managed->GetName()), !F.BossActor->FindComponentByClass(Managed) && !F.PlayerActor->FindComponentByClass(Managed));
	}
	// The pairing of the observed meshes with their skeletons is real evidence, not assumed: a mismatch fails here with the observed names.
	TestTrue(FString::Printf(TEXT("the boss skeleton %s is compatible with the boss mesh %s"), *Describe(F.BossSkeleton), *Describe(F.BossMesh)), F.BossSkeleton->IsCompatibleMesh(F.BossMesh));
	TestTrue(FString::Printf(TEXT("the player skeleton %s is compatible with the player mesh %s"), *Describe(F.PlayerSkeleton), *Describe(F.PlayerMesh)), F.PlayerSkeleton->IsCompatibleMesh(F.PlayerMesh));

	// The genuine production compiler (bSyntheticFixture false): it loads the skeleton and every animation listed.
	F.CompileProduction();
	if (!ExpectProductionCompiled(*this, F))
	{
		return false;
	}
	const FRPGParticipantConfig& BossConfig = *F.BossConfig;
	const FRPGParticipantConfig& PlayerConfig = *F.PlayerConfig;
	TestTrue(TEXT("both configs are production configs, not synthetic fixtures"), !BossConfig.bSyntheticFixture && !PlayerConfig.bSyntheticFixture);
	TestTrue(TEXT("two distinct config objects with distinct identities"), F.BossConfig.Get() != F.PlayerConfig.Get() && BossConfig.BossId != PlayerConfig.BossId && BossConfig.BossId == FName(TEXT("ProductionBoss")));
	TestTrue(TEXT("both configs lease the very content epoch"), BossConfig.Content.Get() == F.Content.Get() && PlayerConfig.Content.Get() == F.Content.Get());
	TestTrue(TEXT("the boss config retained the loaded skeleton the boss mesh reports"), BossConfig.Skeleton.Get() == F.BossSkeleton);
	TestTrue(TEXT("the player config retained the loaded skeleton the player mesh reports"), PlayerConfig.Skeleton.Get() == F.PlayerSkeleton);
	TestEqual(TEXT("the boss config retained every listed animation"), BossConfig.Animations.Num(), BossAnimationPaths().Num());
	TestEqual(TEXT("the player config retained every listed animation"), PlayerConfig.Animations.Num(), PlayerAnimationPaths().Num());
	for (const FConfigPtr& Config : {F.BossConfig, F.PlayerConfig})
	{
		for (int32 Index = 0; Index < Config->Animations.Num(); ++Index)
		{
			const UAnimSequenceBase* Animation = Config->Animations[Index].Get();
			AddInfo(FString::Printf(TEXT("%s animation #%d: %s | skeleton %s"), *Config->BossId.ToString(), Index, *Describe(Animation), *Describe(Animation ? Animation->GetSkeleton() : nullptr)));
			TestTrue(FString::Printf(TEXT("%s animation #%d is a valid lease on the compiled skeleton"), *Config->BossId.ToString(), Index), Animation && IsValid(Animation) && Animation->GetSkeleton() == Config->Skeleton.Get());
		}
	}
	FString BossDependencyError, PlayerDependencyError;
	const bool bBossDependencies = RPGBossHydrationPreflight::CheckCompiledDependencies(BossConfig, BossDependencyError);
	const bool bPlayerDependencies = RPGBossHydrationPreflight::CheckCompiledDependencies(PlayerConfig, PlayerDependencyError);
	TestTrue(FString::Printf(TEXT("the dependency predicate accepts the boss config (%s)"), *BossDependencyError), bBossDependencies);
	TestTrue(FString::Printf(TEXT("the dependency predicate accepts the player config (%s)"), *PlayerDependencyError), bPlayerDependencies);

	// The batch: the boss is boss-core with the explicit phase id, the player is target-only.
	const FRPGHydrationPreflightInput Input = F.MakeInput();
	const TArray<int32> StateBefore = CaptureState(F.Scope.World);
	const TArray<const UObject*> Touched = F.TouchedObjects();
	const TArray<int32> DirtyBefore = CaptureDirty(Touched);
	FPlanPtr Plan;
	const FRPGHydrationResult Result = RPGBossHydrationPreflight::CompilePreflight(Input, Plan);
	if (!TestTrue(FString::Printf(TEXT("the production batch compiles (errors: %s)"), *JoinErrors(Result)), Result.IsReady() && Result.Errors.IsEmpty() && Plan.IsValid()))
	{
		return false;
	}
	TestTrue(TEXT("scope name"), FString(FRPGHydrationPreflightPlan::ScopeName()) == TEXT("ExpandedNativeSubsetPreflight"));
	TestFalse(TEXT("not a complete playable bundle"), Plan->IsCompletePlayableBundle());
	TestFalse(TEXT("not a reservation"), Plan->IsReservation());
	TestFalse(TEXT("not ready"), Plan->IsReady());
	TestTrue(TEXT("the world, the encounter identity and the very content lease are retained"), Plan->World.Get() == F.Scope.World && Plan->EncounterInstance == Input.EncounterInstance && Plan->Content.Get() == F.Content.Get());
	if (!TestEqual(TEXT("two participants"), Plan->Participants.Num(), 2))
	{
		return false;
	}
	const FRPGPreflightParticipantPlan& BossPlan = Plan->Participants[0];
	const FRPGPreflightParticipantPlan& PlayerPlan = Plan->Participants[1];
	TestTrue(TEXT("slots, targets, roles and actors are as requested"), BossPlan.Slot == FName(TEXT("Boss")) && BossPlan.TargetSlot == FName(TEXT("Player")) && BossPlan.Role == ERPGPreflightRole::BossCore && BossPlan.Actor.Get() == F.BossActor
		&& PlayerPlan.Slot == FName(TEXT("Player")) && PlayerPlan.TargetSlot == FName(TEXT("Boss")) && PlayerPlan.Role == ERPGPreflightRole::TargetOnly && PlayerPlan.Actor.Get() == F.PlayerActor);
	TestTrue(TEXT("the plan holds the very production config leases"), BossPlan.Config.Get() == F.BossConfig.Get() && PlayerPlan.Config.Get() == F.PlayerConfig.Get());
	if (!TestEqual(TEXT("the boss has twelve plans"), BossPlan.Plans.Num(), 12))
	{
		return false;
	}
	TestTrue(TEXT("plan classes in the relative order Stagger, Phases, Encounter, DormantWake, Posture"), BossPlan.Plans[0].Class == URPGBossStagger::StaticClass() && BossPlan.Plans[1].Class == URPGBossPhases::StaticClass()
		&& BossPlan.Plans[2].Class == URPGBossEncounter::StaticClass() && BossPlan.Plans[3].Class == URPGBossDormantWake::StaticClass() && BossPlan.Plans[4].Class == URPGBossPosture::StaticClass() && BossPlan.Plans[5].Class == URPGBossBleed::StaticClass() && BossPlan.Plans[6].Class == URPGBossLowSweep::StaticClass() && BossPlan.Plans[7].Class == URPGBossShockwave::StaticClass() && BossPlan.Plans[8].Class == URPGBossHealPunish::StaticClass() && BossPlan.Plans[9].Class == URPGBossLook::StaticClass() && BossPlan.Plans[10].Class == URPGBossCloseClipSwap::StaticClass() && BossPlan.Plans[11].Class == URPGBossDeath::StaticClass());
	TestTrue(TEXT("plan instance names are the legacy names"), BossPlan.Plans[0].InstanceName == FName(TEXT("RPGBossStagger")) && BossPlan.Plans[1].InstanceName == FName(TEXT("RPGBossPhases")) && BossPlan.Plans[2].InstanceName == FName(TEXT("RPGBossEncounter"))
		&& BossPlan.Plans[3].InstanceName == FName(TEXT("RPGBossDormantWake")) && BossPlan.Plans[4].InstanceName == FName(TEXT("RPGBossPosture")) && BossPlan.Plans[5].InstanceName == FName(TEXT("RPGBossBleed")) && BossPlan.Plans[6].InstanceName == FName(TEXT("RPGBossLowSweep")) && BossPlan.Plans[7].InstanceName == FName(TEXT("RPGBossShockwave")) && BossPlan.Plans[8].InstanceName == FName(TEXT("RPGBossHealPunish")) && BossPlan.Plans[9].InstanceName == FName(TEXT("RPGBossLook")) && BossPlan.Plans[10].InstanceName == FName(TEXT("RPGBossCloseClipSwap")) && BossPlan.Plans[11].InstanceName == FName(TEXT("RPGBossDeath")));
	TestTrue(TEXT("the callbacks exist (built, never run)"), static_cast<bool>(BossPlan.Plans[0].Configure) && static_cast<bool>(BossPlan.Plans[1].Configure) && static_cast<bool>(BossPlan.Plans[2].Configure)
		&& static_cast<bool>(BossPlan.Plans[3].Configure) && static_cast<bool>(BossPlan.Plans[4].Configure) && static_cast<bool>(BossPlan.Plans[5].Configure) && static_cast<bool>(BossPlan.Plans[6].Configure) && static_cast<bool>(BossPlan.Plans[7].Configure) && static_cast<bool>(BossPlan.Plans[8].Configure) && static_cast<bool>(BossPlan.Plans[9].Configure) && static_cast<bool>(BossPlan.Plans[10].Configure) && static_cast<bool>(BossPlan.Plans[11].Configure));
	TSet<FString> Required;
	for (const FRPGComponentPlan& ComponentPlan : BossPlan.Plans)
	{
		Required.Append(ComponentPlan.RequiredFields);
	}
	const TArray<FString> Expected = AllRequiredPaths(PhaseTwo);
	TestEqual(TEXT("the union of required manifest paths is one hundred ten"), Required.Num(), 110);
	for (const FString& Path : Expected)
	{
		TestTrue(FString::Printf(TEXT("required path %s is named by a plan"), *Path), Required.Contains(Path));
	}
	TestEqual(TEXT("one class lease per boss plan"), BossPlan.ClassLeases.Num(), 12);
	TestTrue(TEXT("the target gets no plan and no class lease"), PlayerPlan.Plans.IsEmpty() && PlayerPlan.ClassLeases.IsEmpty());

	// A stable repeat compile, and the world and the assets are exactly as before: nothing created, registered, bound, begun or ticked, and no touched package dirtied by the preflight.
	FPlanPtr Again;
	TestTrue(TEXT("a second compile of the same input succeeds as a different plan object"), RPGBossHydrationPreflight::CompilePreflight(Input, Again).IsReady() && Again.IsValid() && Again.Get() != Plan.Get());
	TestTrue(TEXT("compiling changed no actor, component or combat context"), CaptureState(F.Scope.World) == StateBefore);
	TestTrue(TEXT("neither actor has begun play and neither holds a managed consumer after the compile"), !F.BossActor->HasActorBegunPlay() && !F.PlayerActor->HasActorBegunPlay());
	for (UClass* Managed : RPGBossHydrationPreflight::ManagedCoreConsumerClasses())
	{
		TestTrue(FString::Printf(TEXT("no %s was created by the compile"), *Managed->GetName()), !F.BossActor->FindComponentByClass(Managed) && !F.PlayerActor->FindComponentByClass(Managed));
	}
	TestTrue(TEXT("no touched package became dirty during the preflight"), CaptureDirty(Touched) == DirtyBefore);
	TestTrue(TEXT("the pack character classes and meshes are still the observed objects (no default object was replaced)"), F.BossClass->GetDefaultObject<ACharacter>()->GetMesh()->GetSkeletalMeshAsset() == F.BossMesh
		&& F.PlayerClass->GetDefaultObject<ACharacter>()->GetMesh()->GetSkeletalMeshAsset() == F.PlayerMesh);

	AddInfo(TEXT("Real pack assets and the real production compiler; the preflight output is an expanded native subset: not a complete playable bundle, not a reservation, not Ready. NOT established: a cold load, the cooked or packaged build, "
		"the arena level, the placed Blueprint boss, abilities or effects (class paths are structural only), animation playback or root motion, the authored boss definition (values and manifest rows are fixture values), a game-instance "
		"content epoch, BeginPlay, registration, context binding, activation or wiring."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGProductionPreflightDependencyTest, "OneBossFight.Binding.ProductionPreflight.DependencyRejections",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGProductionPreflightDependencyTest::RunTest(const FString& Parameters)
{
	FProductionFixture F;
	if (!F.Prepare(*this))
	{
		return false;
	}
	F.CompileProduction();
	if (!ExpectProductionCompiled(*this, F))
	{
		return false;
	}
	FPlanPtr Prior;
	const FRPGHydrationPreflightInput Valid = F.MakeInput();
	if (!TestTrue(TEXT("the unmodified production batch compiles first (the control for every case below)"), RPGBossHydrationPreflight::CompilePreflight(Valid, Prior).IsReady() && Prior.IsValid()))
	{
		return false;
	}

	// Negative controls only: a transient skeleton and a transient animation bound to it. They exist to be the "other" skeleton; nothing is loaded, retargeted or substituted.
	TStrongObjectPtr<USkeleton> OtherSkeleton(NewObject<USkeleton>(GetTransientPackage()));
	TStrongObjectPtr<UAnimSequence> OtherAnimation(NewObject<UAnimSequence>(GetTransientPackage()));
	if (!TestTrue(TEXT("the transient negative controls were created"), OtherSkeleton.IsValid() && OtherAnimation.IsValid()))
	{
		AddError(TEXT("unsupported precondition: the transient skeleton and animation could not be created"));
		return false;
	}
	OtherAnimation->SetSkeleton(OtherSkeleton.Get());
	if (!TestTrue(TEXT("precondition: the transient animation holds the transient skeleton, not the pack skeleton"), OtherAnimation->GetSkeleton() == OtherSkeleton.Get() && OtherSkeleton.Get() != F.BossSkeleton))
	{
		return false;
	}

	auto BatchWith = [&F](const TFunction<void(FRPGParticipantConfig&)>& Mutate)
	{
		FRPGHydrationPreflightInput Input = F.MakeInput();
		Input.Requests[0].Config = CloneProduction(*F.BossConfig, Mutate);
		return Input;
	};

	// The unmutated clone is accepted: the clone helper itself changes nothing.
	{
		FPlanPtr Out;
		const FRPGHydrationResult Result = RPGBossHydrationPreflight::CompilePreflight(BatchWith(TFunction<void(FRPGParticipantConfig&)>()), Out);
		TestTrue(FString::Printf(TEXT("control: an unmutated clone of the production config is accepted (errors: %s)"), *JoinErrors(Result)), Result.IsReady() && Out.IsValid());
	}
	// The native character without a mesh (used for the mesh-side case) is spawned BEFORE the state snapshot, so the snapshot covers every actor the cases use.
	ACharacter* Bare = F.Scope.SpawnCharacter(nullptr, FVector(2000.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("a native character without a mesh"), Bare))
	{
		return false;
	}
	const TArray<int32> StateBefore = CaptureState(F.Scope.World);
	const TArray<const UObject*> Touched = F.TouchedObjects();
	const TArray<int32> DirtyBefore = CaptureDirty(Touched);

	// The preflight's production prerequisite on the compiled leases: each case changes exactly one dependency of the successful boss config.
	ExpectRejected(*this, F, TEXT("a null animation lease"), BatchWith([](FRPGParticipantConfig& C) { C.Animations[0].Reset(); }), TEXT("Preflight.ProductionPrerequisite"), TEXT("animation lease #0 is not valid"), Prior);
	ExpectRejected(*this, F, TEXT("no compiled animation"), BatchWith([](FRPGParticipantConfig& C) { C.Animations.Reset(); }), TEXT("Preflight.ProductionPrerequisite"), TEXT("no compiled animation"), Prior);
	ExpectRejected(*this, F, TEXT("no compiled skeleton"), BatchWith([](FRPGParticipantConfig& C) { C.Skeleton.Reset(); }), TEXT("Preflight.ProductionPrerequisite"), TEXT("compiled skeleton is missing"), Prior);
	ExpectRejected(*this, F, TEXT("an animation of another skeleton (transient control) after the real ones"), BatchWith([&OtherAnimation](FRPGParticipantConfig& C) { C.Animations.Emplace(OtherAnimation.Get()); }),
		TEXT("Preflight.ProductionPrerequisite"), TEXT("belongs to skeleton"), Prior);
	ExpectRejected(*this, F, TEXT("a compiled skeleton that is not the animations' skeleton (transient control)"), BatchWith([&OtherSkeleton](FRPGParticipantConfig& C) { C.Skeleton.Reset(OtherSkeleton.Get()); }),
		TEXT("Preflight.ProductionPrerequisite"), TEXT("not the compiled skeleton"), Prior);

	// The mesh side: a native character that holds no mesh at all, with every dependency of the config valid, is refused for the mesh only.
	{
		FRPGHydrationPreflightInput Input = F.MakeInput();
		Input.Requests[0].Actor = Bare;
		ExpectRejected(*this, F, TEXT("a production member whose actor holds no mesh"), Input, TEXT("Preflight.ProductionPrerequisite"), TEXT("character whose mesh is compatible with the compiled skeleton"), Prior);
		FPlanPtr Out;
		const FRPGHydrationResult Result = RPGBossHydrationPreflight::CompilePreflight(Input, Out);
		TestFalse(TEXT("the mesh-only refusal does not name an animation problem"), AnyErrorContains(Result, TEXT("animation")));
	}

	// The production compiler itself, from the same successful definitions, one change at a time. The output is pre-set to a valid config: a failing compile must clear it and publish nothing.
	auto ExpectCompileRefused = [this, &F](const TCHAR* Label, USkeleton* Skeleton, const TArray<FSoftObjectPath>& Paths, const TCHAR* Detail)
	{
		TStrongObjectPtr<URPGBossDefinition> Definition(NewObject<URPGBossDefinition>());
		if (!TestTrue(FString::Printf(TEXT("%s: the transient definition was created"), Label), Definition.IsValid()))
		{
			return;
		}
		FillDefinition(*Definition, TEXT("ProductionBoss"), TEXT("ProductionBossLook"), Skeleton, Paths);
		FConfigPtr Out = F.BossConfig; // a valid earlier config: a failure must not leave it in place
		const FRPGHydrationResult Result = RPGCombatHydration::CompileParticipant(*Definition, F.Content, ManifestHash(), Out);
		TestFalse(FString::Printf(TEXT("%s: the production compile is refused"), Label), Result.IsReady());
		TestFalse(FString::Printf(TEXT("%s: the earlier output was cleared and no config was published"), Label), Out.IsValid());
		TestTrue(FString::Printf(TEXT("%s: the failure carries '%s' (got: %s)"), Label, Detail, *JoinErrors(Result)), AnyErrorContains(Result, FString(Detail)));
	};
	const TArray<FSoftObjectPath> RealPaths = BossAnimationPaths();
	ExpectCompileRefused(TEXT("no skeleton reference"), nullptr, RealPaths, TEXT("required skeleton/animation dependencies missing"));
	ExpectCompileRefused(TEXT("no animation reference"), F.BossSkeleton, TArray<FSoftObjectPath>(), TEXT("required skeleton/animation dependencies missing"));
	{
		TArray<FSoftObjectPath> WithNull = RealPaths;
		WithNull.Add(FSoftObjectPath());
		ExpectCompileRefused(TEXT("a null animation reference after the real ones"), F.BossSkeleton, WithNull, TEXT("animation/skeleton identity mismatch"));
	}
	ExpectCompileRefused(TEXT("a skeleton that is not the animations' skeleton (transient control)"), OtherSkeleton.Get(), RealPaths, TEXT("animation/skeleton identity mismatch"));

	TestTrue(TEXT("none of the cases changed an actor, a component or the combat context"), CaptureState(F.Scope.World) == StateBefore);
	TestTrue(TEXT("none of the cases dirtied a touched package"), CaptureDirty(Touched) == DirtyBefore);
	TestTrue(TEXT("the successful production configs and the earlier plan are untouched by the negative cases"), F.BossConfig.IsValid() && F.BossConfig->Animations.Num() == BossAnimationPaths().Num() && Prior.IsValid() && Prior->Participants.Num() == 2);

	AddInfo(TEXT("Dependency rejections derived from the successful real-asset production result; the transient skeleton and animation are negative controls only. NOT covered: a mesh of another skeleton on a real character (no such pack pairing is built), "
		"a reference to a missing asset (it would log load warnings), a retargeted dependency, the packaged build, any wiring."));
	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
