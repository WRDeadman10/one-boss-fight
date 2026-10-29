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
#include "Components/ActorComponent.h"
#include "Components/SceneComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/Engine.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "Player/RPGBossDormantWake.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossHydrationPreflight.h"
#include "Player/RPGBossHydrationPreparation.h"
#include "Player/RPGBossPhases.h"
#include "Player/RPGBossPosture.h"
#include "Player/RPGBossStagger.h"
#include "UObject/Package.h"
#include "UObject/StrongObjectPtr.h"
#include "UObject/UObjectHash.h"

// DD16: the DD15 unregistered batch preparation (RPGBossHydrationPreparation::PrepareBatch) driven by REAL pack assets and the REAL production compiler (RPGCombatHydration::CompileParticipant, bSyntheticFixture false), the way DD14
// drove the preflight. Nothing synthetic is substituted for a positive result.
// What it uses: the two pack character Blueprint classes are loaded only to READ the mesh asset their default object holds (no Blueprint actor is spawned, no default object is changed, no asset is saved); the observed
// mesh and its skeleton are placed on THREE isolated native ACharacter actors (two boss-core owners, one target) in a test-local headless game world that never begins play, every actor fully finished before any preparation;
// the animation dependencies are the authoring-default cooked-directory candidates of the typed records; the definitions are transient; the content epoch is the existing legacy registry epoch; the manifest rows are
// hand-authored membership rows. The setup is copied from DD14 into this file (no shared helper, no edit of the DD14 file).
// What it can establish, for these exact assets in this editor binary: PositiveBatch: twenty-four real owned components (twelve exact native consumers per boss-core actor), unregistered, uninitialized, not begun, not ticking, each
// holding its own member's configured values, the exact production config, content, skeleton and animation leases retained by the plan, the unrelated component sets and mesh assets unchanged, explicit and scope-exit abort
// restoring the prior sets. LateRejection: which LAYER refused a batch whose later member is invalid (the preflight inside PrepareBatch for a dependency or a selected phase; CompileParticipant before PrepareBatch can be
// called for a bad definition, after which the missing config is refused by the preflight), with no allocation of any planned name on any actor, and an unmodified positive control. NameCollisionCleanup: a real live
// unrelated component under a planned instance name of the LATER owner makes the real allocation guard refuse, earlier allocations on both owners are cleaned, the blocker and every other preexisting object keep identity and
// state, and the same input succeeds after only the blocker is removed.
// What it does NOT establish: a cold load (the pack classes are loaded first and the assets may already be in memory; the state before the fixture is only logged), the packaged or cooked build, the arena level, the placed
// Blueprint boss, abilities or effects (class paths are structural only), animation playback, the real boss definition asset (typed values, phase lists and manifest rows are fixture values, not authority), serialized
// authoring or a game-instance content epoch, an organic native configure failure, garbage-name reuse after a real collection (no collection is forced; the retry after the collision reuses the names the failed attempt left as
// destroyed objects and its outcome is only observed), a registration, BeginPlay, context binding, reservation, readiness, legacy suppression or any wiring. The prepared subset is twelve components per boss-core member, not a
// complete playable boss.

namespace
{
namespace ProductionPreparationTests
{
	using FEpochPtr = TSharedPtr<const RPGCombatRegistry::FEpoch>;
	using FConfigPtr = TSharedPtr<const FRPGParticipantConfig>;
	using FPlanPtr = TSharedPtr<const FRPGHydrationPreflightPlan>;

	// The two pack character classes, under always-cooked directories. Only their default object's mesh is read.
	const TCHAR* const PlayerClassPath = TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter.BP_CombatPlayerCharacter_C");
	const TCHAR* const BossClassPath = TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss.BP_ExampleGreatSwordBoss_C");

	/** The explicit per-member values of a transient definition: the two bosses differ in id, selected phase id, threshold, stats and stagger seconds, so a component can be told to hold its OWN member's values. */
	struct FMemberValues
	{
		const TCHAR* Id;
		const TCHAR* Look;
		const TCHAR* Phase;
		float Threshold;
		float Health;
		float Posture;
		float StaggerSeconds;
	};

	FMemberValues BossOneValues()
	{
		return FMemberValues{TEXT("ProductionPrepBossOne"), TEXT("ProductionPrepBossOneLook"), TEXT("PhaseTwo"), 0.35f, 3500.f, 73.5f, 3.25f};
	}

	FMemberValues BossTwoValues()
	{
		return FMemberValues{TEXT("ProductionPrepBossTwo"), TEXT("ProductionPrepBossTwoLook"), TEXT("PhaseAlt"), 0.5f, 4100.f, 88.f, 4.5f};
	}

	FMemberValues PlayerValues()
	{
		return FMemberValues{TEXT("ProductionPrepPlayer"), TEXT("ProductionPrepPlayerLook"), TEXT("PhaseTwo"), 0.35f, 3500.f, 73.5f, 3.25f};
	}

	/** Test-local headless game world (same set-up as DD14), destroyed with the scope. */
	struct FPreparationWorld
	{
		UWorld* World = nullptr;

		FPreparationWorld()
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

		~FPreparationWorld()
		{
			if (World)
			{
				GEngine->DestroyWorldContext(World);
				World->DestroyWorld(/*bInformEngineOfWorld=*/false);
			}
		}

		FPreparationWorld(const FPreparationWorld&) = delete;
		FPreparationWorld& operator=(const FPreparationWorld&) = delete;

		/** A native ACharacter (never a Blueprint actor). The mesh asset is set BEFORE the actor is finished, so it is never begun play. */
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

	/** The unique manifest paths the twelve combined boss-core plans read for a selected phase id, written out as independent literals (copied from DD14). Membership only. */
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
			// Independent preparation fixture manifest literals.
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
		Field.SourcePath = TEXT("DD16 production preparation fixture, not live provenance");
		Field.SourceSHA256 = FString::ChrN(64, TEXT('c'));
		Field.SourceSite = TEXT("fixture");
		Field.Origin = TEXT("harness");
		Field.Precedence = TEXT("fixture");
		Field.Destination = TEXT("fixture");
		Field.FirstRead = TEXT("not read");
		Field.Witness = TEXT("none: structural membership only");
		return Field;
	}

	/** The boss animation dependencies: the cooked-directory authoring-default candidates of the dormant wake, phase dependency and stagger profile records (twenty-three paths). */
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

	/** Valid typed fixture values for the whole record: the typed records are the authoring defaults (the cooked-directory candidates) except the explicit per-member values; valid structurally, not the authored boss values. */
	void FillDefinition(URPGBossDefinition& Definition, const FMemberValues& Values, USkeleton* Skeleton, const TArray<FSoftObjectPath>& AnimationPaths)
	{
		Definition.Schema = 1;
		Definition.DefinitionId = FName(Values.Id);
		Definition.PresentationId = FName(Values.Look);
		Definition.Stats.MaxHealth = Values.Health;
		Definition.Stats.MaxPosture = Values.Posture;
		Definition.Stats.PostureRegenDelay = 4.25f;
		Definition.Stats.PostureRegenRate = 9.75f;
		Definition.EncounterPolicy = FRPGEncounterPolicyConfig();
		Definition.StaggerPolicy = FRPGStaggerPolicyConfig();
		Definition.StaggerPolicy.StaggerSeconds = Values.StaggerSeconds;
		Definition.PhaseFlow = FRPGPhaseFlowConfig();
		Definition.Fireball = FRPGFireballConfig();
		Definition.PhaseDependencies = FRPGPhaseDependencyConfig();
		Definition.StaggerProfile = FRPGStaggerProfileConfig();
		Definition.DormantWake = FRPGDormantWakeConfig();
		FRPGPhaseConfig Phase;
		Phase.PhaseId = FName(Values.Phase);
		Phase.EntryHealthFraction = Values.Threshold;
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
		for (const FString& Path : AllRequiredPaths(FName(Values.Phase)))
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

	FString JoinErrors(const TArray<FString>& Errors)
	{
		return FString::Join(Errors, TEXT(" | "));
	}

	bool AnyErrorContains(const TArray<FString>& Errors, const FString& Text)
	{
		return Errors.ContainsByPredicate([&Text](const FString& E) { return E.Contains(Text); });
	}

	/** One single error that carries the token at its start, the slot text and a further text (a component name or the detail). */
	bool AnyErrorHasAll(const TArray<FString>& Errors, const TCHAR* Token, const TCHAR* SlotText, const TCHAR* FurtherText)
	{
		return Errors.ContainsByPredicate([Token, SlotText, FurtherText](const FString& E) { return E.StartsWith(Token) && E.Contains(SlotText) && E.Contains(FurtherText); });
	}

	bool NoErrorStartsWith(const TArray<FString>& Errors, const TCHAR* Prefix)
	{
		return !Errors.ContainsByPredicate([Prefix](const FString& E) { return E.StartsWith(Prefix); });
	}

	/** The dirty flag of the package of each object, compared around the preparation and abort cases only (the class load, the spawn and the production compile happen before the first snapshot and are not covered). */
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

	/** The clone of a production config for a negative case: every record and lease is re-supplied by hand (no whole-config copy), bSyntheticFixture stays false, then the case changes one thing (copied from DD14). */
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

	/** What a preparation or an abort must leave alone, per actor: the sorted component set, the registered and begun flags of each, the begun flag of the actor and the mesh asset its character holds. */
	struct FActorState
	{
		TArray<const UActorComponent*> Components;
		TArray<int32> Flags;
		bool bBegun = false;
		const USkeletalMesh* MeshAsset = nullptr;
	};

	struct FWorldState
	{
		TArray<FActorState> Actors; // BossOne, BossTwo, Player
		int32 Bound = -1;
		int32 Ready = -1;
	};

	FActorState CaptureActor(const AActor* Actor)
	{
		FActorState State;
		State.bBegun = Actor->HasActorBegunPlay();
		if (const ACharacter* Character = Cast<ACharacter>(Actor))
		{
			State.MeshAsset = Character->GetMesh() ? Character->GetMesh()->GetSkeletalMeshAsset() : nullptr;
		}
		for (const UActorComponent* Component : Actor->GetComponents())
		{
			State.Components.Add(Component);
		}
		State.Components.Sort([](const UActorComponent& A, const UActorComponent& B) { return &A < &B; }); // a pointer array is sorted through dereferenced references
		for (const UActorComponent* Component : State.Components)
		{
			State.Flags.Add(Component->IsRegistered() ? 1 : 0);
			State.Flags.Add(Component->HasBegunPlay() ? 1 : 0);
		}
		return State;
	}

	bool SameActor(const FActorState& A, const FActorState& B)
	{
		return A.bBegun == B.bBegun && A.MeshAsset == B.MeshAsset && A.Components == B.Components && A.Flags == B.Flags;
	}

	bool SameWorld(const FWorldState& A, const FWorldState& B)
	{
		if (A.Actors.Num() != B.Actors.Num() || A.Bound != B.Bound || A.Ready != B.Ready)
		{
			return false;
		}
		for (int32 Index = 0; Index < A.Actors.Num(); ++Index)
		{
			if (!SameActor(A.Actors[Index], B.Actors[Index]))
			{
				return false;
			}
		}
		return true;
	}

	struct FExpectedComponent
	{
		UClass* Class;
		const TCHAR* Name;
	};

	/** The twelve accepted native consumers with the reviewed instance names, written out independently of the preflight, in the relative plan order. */
	TArray<FExpectedComponent> ExpectedComponents()
	{
		return TArray<FExpectedComponent>{{URPGBossStagger::StaticClass(), TEXT("RPGBossStagger")}, {URPGBossPhases::StaticClass(), TEXT("RPGBossPhases")}, {URPGBossEncounter::StaticClass(), TEXT("RPGBossEncounter")},
			{URPGBossDormantWake::StaticClass(), TEXT("RPGBossDormantWake")}, {URPGBossPosture::StaticClass(), TEXT("RPGBossPosture")},
			{URPGBossBleed::StaticClass(), TEXT("RPGBossBleed")} , {URPGBossLowSweep::StaticClass(), TEXT("RPGBossLowSweep")} , {URPGBossShockwave::StaticClass(), TEXT("RPGBossShockwave")} , {URPGBossHealPunish::StaticClass(), TEXT("RPGBossHealPunish")} , {URPGBossLook::StaticClass(), TEXT("RPGBossLook")} , {URPGBossCloseClipSwap::StaticClass(), TEXT("RPGBossCloseClipSwap")} , {URPGBossDeath::StaticClass(), TEXT("RPGBossDeath")}};
	}

	bool NoManagedConsumer(const AActor* Actor)
	{
		for (UClass* Class : RPGBossHydrationPreflight::ManagedCoreConsumerClasses())
		{
			if (Actor->FindComponentByClass(Class))
			{
				return false;
			}
		}
		return true;
	}

	/** The real pack mesh and skeleton, three isolated native actors (every one finished before any preparation), an unrelated unregistered marker component on each, three transient definitions and (on request) the three
	 *  production configs. Everything observed is logged; a missing precondition is reported as such. */
	struct FProductionFixture
	{
		FPreparationWorld Scope;
		UClass* PlayerClass = nullptr;
		UClass* BossClass = nullptr;
		USkeletalMesh* PlayerMesh = nullptr;
		USkeletalMesh* BossMesh = nullptr;
		USkeleton* PlayerSkeleton = nullptr;
		USkeleton* BossSkeleton = nullptr;
		ACharacter* BossOneActor = nullptr;
		ACharacter* BossTwoActor = nullptr;
		ACharacter* PlayerActor = nullptr;
		USceneComponent* Markers[3] = {nullptr, nullptr, nullptr};
		FEpochPtr Content;
		FGuid Encounter;
		TStrongObjectPtr<URPGBossDefinition> BossOneDefinition;
		TStrongObjectPtr<URPGBossDefinition> BossTwoDefinition;
		TStrongObjectPtr<URPGBossDefinition> PlayerDefinition;
		FConfigPtr BossOneConfig;
		FConfigPtr BossTwoConfig;
		FConfigPtr PlayerConfig;
		FRPGHydrationResult BossOneCompile;
		FRPGHydrationResult BossTwoCompile;
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
			BossOneActor = Scope.SpawnCharacter(BossMesh, FVector(0.f, 0.f, 0.f));
			BossTwoActor = Scope.SpawnCharacter(BossMesh, FVector(500.f, 0.f, 0.f));
			PlayerActor = Scope.SpawnCharacter(PlayerMesh, FVector(1000.f, 0.f, 0.f));
			if (!BossOneActor || !BossTwoActor || !PlayerActor)
			{
				Test.AddError(TEXT("unsupported precondition: the three isolated native character actors could not be spawned"));
				return false;
			}
			// An unrelated, preexisting, unregistered component on every actor: a preparation and an abort must leave it alone.
			ACharacter* const Actors[3] = {BossOneActor, BossTwoActor, PlayerActor};
			for (int32 Index = 0; Index < 3; ++Index)
			{
				Markers[Index] = NewObject<USceneComponent>(Actors[Index], TEXT("UnrelatedMarker"));
				if (!Markers[Index])
				{
					Test.AddError(TEXT("unsupported precondition: an unrelated marker component could not be created"));
					return false;
				}
			}
			Content = RPGCombatRegistry::Legacy();
			if (!Content.IsValid())
			{
				Test.AddError(TEXT("unsupported precondition: the legacy content epoch is not available"));
				return false;
			}
			BossOneDefinition.Reset(NewObject<URPGBossDefinition>());
			BossTwoDefinition.Reset(NewObject<URPGBossDefinition>());
			PlayerDefinition.Reset(NewObject<URPGBossDefinition>());
			if (!BossOneDefinition.IsValid() || !BossTwoDefinition.IsValid() || !PlayerDefinition.IsValid())
			{
				Test.AddError(TEXT("unsupported precondition: the transient definitions could not be created"));
				return false;
			}
			FillDefinition(*BossOneDefinition, BossOneValues(), BossSkeleton, BossAnimationPaths());
			FillDefinition(*BossTwoDefinition, BossTwoValues(), BossSkeleton, BossAnimationPaths());
			FillDefinition(*PlayerDefinition, PlayerValues(), PlayerSkeleton, PlayerAnimationPaths());
			Encounter = FGuid::NewGuid();
			return true;
		}

		/** The genuine production compiler for all three participants. */
		void CompileProduction()
		{
			BossOneCompile = RPGCombatHydration::CompileParticipant(*BossOneDefinition, Content, ManifestHash(), BossOneConfig);
			BossTwoCompile = RPGCombatHydration::CompileParticipant(*BossTwoDefinition, Content, ManifestHash(), BossTwoConfig);
			PlayerCompile = RPGCombatHydration::CompileParticipant(*PlayerDefinition, Content, ManifestHash(), PlayerConfig);
		}

		/** The valid batch: two boss-core members with their own explicit selected phase ids, both targeting the player slot, and the target-only player targeting the first boss. */
		FRPGHydrationPreflightInput MakeInput() const
		{
			FRPGHydrationPreflightInput Input;
			Input.ExpectedWorld = Scope.World;
			Input.EncounterInstance = Encounter;
			Input.ExpectedContent = Content;
			Input.Requests.Add(MakeRequest(BossOneActor, TEXT("BossOne"), TEXT("Player"), ERPGPreflightRole::BossCore, BossOneConfig, FName(BossOneValues().Phase)));
			Input.Requests.Add(MakeRequest(BossTwoActor, TEXT("BossTwo"), TEXT("Player"), ERPGPreflightRole::BossCore, BossTwoConfig, FName(BossTwoValues().Phase)));
			Input.Requests.Add(MakeRequest(PlayerActor, TEXT("Player"), TEXT("BossOne"), ERPGPreflightRole::TargetOnly, PlayerConfig));
			return Input;
		}

		FWorldState Capture() const
		{
			FWorldState State;
			for (const AActor* Actor : {static_cast<const AActor*>(BossOneActor), static_cast<const AActor*>(BossTwoActor), static_cast<const AActor*>(PlayerActor)})
			{
				State.Actors.Add(CaptureActor(Actor));
			}
			if (const URPGCombatContextSubsystem* Context = Scope.World->GetSubsystem<URPGCombatContextSubsystem>())
			{
				State.Bound = Context->GetBoundCount();
				State.Ready = Context->GetReadyCount();
			}
			return State;
		}

		TArray<const UObject*> TouchedObjects() const
		{
			TArray<const UObject*> Objects{PlayerClass, BossClass, PlayerMesh, BossMesh, PlayerSkeleton, BossSkeleton};
			for (const FConfigPtr& Config : {BossOneConfig, BossTwoConfig, PlayerConfig})
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

	/** The compile of the three production participants, reported as real evidence: a failure lists the compiler's exact errors. */
	bool ExpectProductionCompiled(FAutomationTestBase& Test, const FProductionFixture& F)
	{
		bool bOk = true;
		bOk &= Test.TestTrue(FString::Printf(TEXT("production CompileParticipant of boss one succeeded (errors: %s)"), *JoinErrors(F.BossOneCompile.Errors)), F.BossOneCompile.IsReady() && F.BossOneConfig.IsValid());
		bOk &= Test.TestTrue(FString::Printf(TEXT("production CompileParticipant of boss two succeeded (errors: %s)"), *JoinErrors(F.BossTwoCompile.Errors)), F.BossTwoCompile.IsReady() && F.BossTwoConfig.IsValid());
		bOk &= Test.TestTrue(FString::Printf(TEXT("production CompileParticipant of the player succeeded (errors: %s)"), *JoinErrors(F.PlayerCompile.Errors)), F.PlayerCompile.IsReady() && F.PlayerConfig.IsValid());
		return bOk;
	}

	/** Identity and lease evidence of the three production configs, before any preparation (reported with the observed names). */
	void ExpectProductionLeases(FAutomationTestBase& Test, const FProductionFixture& F)
	{
		Test.TestTrue(TEXT("all three configs are production configs, not synthetic fixtures"), !F.BossOneConfig->bSyntheticFixture && !F.BossTwoConfig->bSyntheticFixture && !F.PlayerConfig->bSyntheticFixture);
		Test.TestTrue(TEXT("three distinct config objects with distinct boss ids"), F.BossOneConfig.Get() != F.BossTwoConfig.Get() && F.BossOneConfig.Get() != F.PlayerConfig.Get() && F.BossTwoConfig.Get() != F.PlayerConfig.Get()
			&& F.BossOneConfig->BossId == FName(BossOneValues().Id) && F.BossTwoConfig->BossId == FName(BossTwoValues().Id) && F.PlayerConfig->BossId == FName(PlayerValues().Id));
		Test.TestTrue(TEXT("all three configs lease the very content epoch"), F.BossOneConfig->Content.Get() == F.Content.Get() && F.BossTwoConfig->Content.Get() == F.Content.Get() && F.PlayerConfig->Content.Get() == F.Content.Get());
		Test.TestTrue(TEXT("both boss configs retained the loaded boss skeleton and the player config the loaded player skeleton"), F.BossOneConfig->Skeleton.Get() == F.BossSkeleton && F.BossTwoConfig->Skeleton.Get() == F.BossSkeleton
			&& F.PlayerConfig->Skeleton.Get() == F.PlayerSkeleton);
		Test.TestEqual(TEXT("boss one retained every listed animation"), F.BossOneConfig->Animations.Num(), BossAnimationPaths().Num());
		Test.TestEqual(TEXT("boss two retained every listed animation"), F.BossTwoConfig->Animations.Num(), BossAnimationPaths().Num());
		Test.TestEqual(TEXT("the player retained every listed animation"), F.PlayerConfig->Animations.Num(), PlayerAnimationPaths().Num());
		for (const FConfigPtr& Config : {F.BossOneConfig, F.BossTwoConfig, F.PlayerConfig})
		{
			for (int32 Index = 0; Index < Config->Animations.Num(); ++Index)
			{
				const UAnimSequenceBase* Animation = Config->Animations[Index].Get();
				Test.AddInfo(FString::Printf(TEXT("%s animation #%d: %s | skeleton %s"), *Config->BossId.ToString(), Index, *Describe(Animation), *Describe(Animation ? Animation->GetSkeleton() : nullptr)));
				Test.TestTrue(FString::Printf(TEXT("%s animation #%d is a valid lease on the compiled skeleton"), *Config->BossId.ToString(), Index), Animation && IsValid(Animation) && Animation->GetSkeleton() == Config->Skeleton.Get());
			}
		}
	}

	/** Weak identities of every owned component, to prove they were destroyed. */
	TArray<TWeakObjectPtr<UActorComponent>> WeakOwned(const FRPGPreparedBatch& Batch)
	{
		TArray<TWeakObjectPtr<UActorComponent>> Weak;
		for (const UActorComponent* Component : Batch.OwnedComponentsForTest())
		{
			Weak.Add(const_cast<UActorComponent*>(Component));
		}
		return Weak;
	}

	/** Every owned component is destroyed: no longer valid, and (the garbage object may still exist until collection) unregistered, not begun and flagged as destroyed. */
	bool ExpectAllDestroyed(FAutomationTestBase& Test, const TArray<TWeakObjectPtr<UActorComponent>>& Weak, const TCHAR* Label)
	{
		bool bGone = true;
		bool bCleanState = true;
		for (const TWeakObjectPtr<UActorComponent>& Pointer : Weak)
		{
			bGone = bGone && !Pointer.IsValid();
			if (const UActorComponent* Garbage = Pointer.Get(/*bEvenIfPendingKill=*/true))
			{
				bCleanState = bCleanState && !Garbage->IsRegistered() && !Garbage->HasBegunPlay() && Garbage->IsBeingDestroyed();
			}
		}
		bool bOk = Test.TestTrue(FString::Printf(TEXT("%s: every owned component is destroyed (none resolves any more)"), Label), Weak.Num() == 24 && bGone);
		bOk &= Test.TestTrue(FString::Printf(TEXT("%s: any destroyed object still awaiting collection is unregistered, not begun and marked destroyed"), Label), bCleanState);
		return bOk;
	}

	/** After an abort or a refusal: the world, the three actors and every component set are exactly as before, and no managed consumer is on any actor. */
	bool ExpectRestored(FAutomationTestBase& Test, const FProductionFixture& F, const FWorldState& Before, const TCHAR* Label)
	{
		bool bOk = Test.TestTrue(FString::Printf(TEXT("%s: every actor's component set, registered and begun flags, mesh asset and the combat context are exactly as before"), Label), SameWorld(Before, F.Capture()));
		bOk &= Test.TestTrue(FString::Printf(TEXT("%s: no managed consumer remains on any actor"), Label), NoManagedConsumer(F.BossOneActor) && NoManagedConsumer(F.BossTwoActor) && NoManagedConsumer(F.PlayerActor));
		bOk &= Test.TestTrue(FString::Printf(TEXT("%s: the unrelated marker components are the same objects, still valid and unregistered"), Label),
			F.Markers[0] && F.Markers[1] && F.Markers[2] && IsValid(F.Markers[0]) && IsValid(F.Markers[1]) && IsValid(F.Markers[2]) && !F.Markers[0]->IsRegistered() && !F.Markers[1]->IsRegistered() && !F.Markers[2]->IsRegistered());
		return bOk;
	}

	/** No object at all (live or destroyed) carries any planned instance name under any of the three actors: nothing was allocated. */
	bool ExpectNoPlannedNameAllocated(FAutomationTestBase& Test, const FProductionFixture& F, const TCHAR* Label)
	{
		bool bNone = true;
		for (const AActor* Actor : {static_cast<const AActor*>(F.BossOneActor), static_cast<const AActor*>(F.BossTwoActor), static_cast<const AActor*>(F.PlayerActor)})
		{
			for (const FExpectedComponent& Wanted : ExpectedComponents())
			{
				bNone = bNone && StaticFindObjectFast(UObject::StaticClass(), const_cast<AActor*>(Actor), FName(Wanted.Name)) == nullptr;
			}
		}
		return Test.TestTrue(FString::Printf(TEXT("%s: no object, not even a destroyed one, carries a planned instance name under any actor (nothing was allocated)"), Label), bNone);
	}

	/** The exact success shape on real assets: twenty-four owned real components (twelve per boss-core actor, exact classes, reviewed names, owners, each holding its OWN member's configured values), unregistered, uninitialized, not
	 *  begun, not ticking, nothing for the target, no participant, no bound or ready context, the unrelated components and mesh assets untouched, the artifact's read-only summary and the retained plan and lease identities. */
	bool ExpectPrepared(FAutomationTestBase& Test, const FProductionFixture& F, const FRPGPreparedBatch& Batch, const FWorldState& Before)
	{
		bool bOk = true;
		bOk &= Test.TestTrue(TEXT("the artifact reports prepared"), Batch.IsPrepared());
		bOk &= Test.TestEqual(TEXT("twenty-four components are leased"), Batch.GetOwnedComponentCount(), 24);
		const TArray<const UActorComponent*> OwnedList = Batch.OwnedComponentsForTest();
		const TSet<const UActorComponent*> OwnedSet(OwnedList);
		bOk &= Test.TestTrue(TEXT("twenty-four distinct owned component pointers"), OwnedList.Num() == 24 && OwnedSet.Num() == 24);

		struct FBossCase
		{
			AActor* Actor;
			int32 Index;
			float StaggerSeconds, PhaseThreshold, Health, Posture;
		};
		const FMemberValues One = BossOneValues();
		const FMemberValues Two = BossTwoValues();
		const FBossCase Bosses[] = {{F.BossOneActor, 0, One.StaggerSeconds, One.Threshold, One.Health, One.Posture}, {F.BossTwoActor, 1, Two.StaggerSeconds, Two.Threshold, Two.Health, Two.Posture}};
		const TArray<FExpectedComponent> Expected = ExpectedComponents();
		for (const FBossCase& Case : Bosses)
		{
			const FString Label = Case.Actor->GetName();
			for (const FExpectedComponent& Wanted : Expected)
			{
				UActorComponent* Component = Case.Actor->FindComponentByClass(Wanted.Class);
				if (!Test.TestNotNull(FString::Printf(TEXT("%s has a %s"), *Label, *Wanted.Class->GetName()), Component))
				{
					bOk = false;
					continue;
				}
				bOk &= Test.TestTrue(FString::Printf(TEXT("%s: %s has the exact class, the reviewed name and the actor as owner and outer"), *Label, Wanted.Name),
					Component->GetClass() == Wanted.Class && Component->GetFName() == FName(Wanted.Name) && Component->GetOwner() == Case.Actor && Component->GetOuter() == Case.Actor);
				bOk &= Test.TestTrue(FString::Printf(TEXT("%s: %s is unregistered, not begun, not initialized and its tick function is not registered"), *Label, Wanted.Name),
					!Component->IsRegistered() && !Component->HasBegunPlay() && !Component->HasBeenInitialized() && !Component->PrimaryComponentTick.IsTickFunctionRegistered());
				bOk &= Test.TestTrue(FString::Printf(TEXT("%s: %s is one of the artifact's owned components"), *Label, Wanted.Name), OwnedSet.Contains(Component));
			}
			const FActorState Now = CaptureActor(Case.Actor);
			const FActorState& Prior = Before.Actors[Case.Index];
			bool bPriorKept = Now.Components.Num() == Prior.Components.Num() + 12 && !Now.bBegun && Now.MeshAsset == Prior.MeshAsset;
			for (const UActorComponent* PriorComponent : Prior.Components)
			{
				bPriorKept = bPriorKept && Now.Components.Contains(PriorComponent) && !OwnedSet.Contains(PriorComponent);
			}
			bOk &= Test.TestTrue(FString::Printf(TEXT("%s: exactly twelve components were added, every unrelated component is still there and the mesh asset is unchanged"), *Label), bPriorKept);
			bOk &= Test.TestFalse(FString::Printf(TEXT("%s has no participant component"), *Label), Case.Actor->FindComponentByClass<URPGCombatParticipant>() != nullptr);

			// Representative configured fields: the typed records of this member's own config, never the other boss's.
			const URPGBossStagger* Stagger = Case.Actor->FindComponentByClass<URPGBossStagger>();
			const URPGBossPhases* Phases = Case.Actor->FindComponentByClass<URPGBossPhases>();
			const URPGBossEncounter* Encounter = Case.Actor->FindComponentByClass<URPGBossEncounter>();
			const URPGBossPosture* Posture = Case.Actor->FindComponentByClass<URPGBossPosture>();
			bOk &= Test.TestTrue(FString::Printf(TEXT("%s: stagger seconds, the selected phase threshold, boss health and posture maximum are this member's configured values"), *Label),
				Stagger && Phases && Encounter && Posture && Stagger->StaggerSeconds == Case.StaggerSeconds && Phases->PhaseTwoHealthFraction == Case.PhaseThreshold
				&& Encounter->BossMaxHealth == Case.Health && Posture->PostureMax == Case.Posture);
		}
		bOk &= Test.TestTrue(TEXT("the target actor is exactly as before: no consumer, no participant, no component added"), SameActor(CaptureActor(F.PlayerActor), Before.Actors[2]) && NoManagedConsumer(F.PlayerActor));
		const FWorldState Now = F.Capture();
		bOk &= Test.TestTrue(TEXT("the combat context has no bound or ready participant change"), Now.Bound == Before.Bound && Now.Ready == Before.Ready);

		const TArray<FRPGPreparedParticipantInfo> Infos = Batch.GetParticipants();
		if (Test.TestEqual(TEXT("three participant summaries in the request order"), Infos.Num(), 3))
		{
			bOk &= Test.TestTrue(TEXT("summary: slots, targets, roles, explicit phase ids and owned counts"),
				Infos[0].Slot == FName(TEXT("BossOne")) && Infos[0].TargetSlot == FName(TEXT("Player")) && Infos[0].Role == ERPGPreflightRole::BossCore && Infos[0].SelectedPhaseId == FName(One.Phase) && Infos[0].OwnedComponentCount == 12
				&& Infos[1].Slot == FName(TEXT("BossTwo")) && Infos[1].TargetSlot == FName(TEXT("Player")) && Infos[1].Role == ERPGPreflightRole::BossCore && Infos[1].SelectedPhaseId == FName(Two.Phase) && Infos[1].OwnedComponentCount == 12
				&& Infos[2].Slot == FName(TEXT("Player")) && Infos[2].TargetSlot == FName(TEXT("BossOne")) && Infos[2].Role == ERPGPreflightRole::TargetOnly && Infos[2].SelectedPhaseId.IsNone() && Infos[2].OwnedComponentCount == 0);
		}
		const TSharedPtr<const FRPGHydrationPreflightPlan> Plan = Batch.GetPreflightPlan();
		if (Test.TestTrue(TEXT("the validated preflight plan is retained"), Plan.IsValid() && Plan->Participants.Num() == 3))
		{
			bOk &= Test.TestTrue(TEXT("the plan keeps the world, the encounter, the very content lease and the very production config leases"), Plan->World.Get() == F.Scope.World && Plan->EncounterInstance == F.Encounter && Batch.GetEncounterInstance() == F.Encounter
				&& Plan->Content.Get() == F.Content.Get() && Plan->Participants[0].Config.Get() == F.BossOneConfig.Get() && Plan->Participants[1].Config.Get() == F.BossTwoConfig.Get() && Plan->Participants[2].Config.Get() == F.PlayerConfig.Get());
			bOk &= Test.TestTrue(TEXT("through the retained plan: the same skeleton and animation leases the production compiler loaded"), Plan->Participants[0].Config->Skeleton.Get() == F.BossSkeleton && Plan->Participants[1].Config->Skeleton.Get() == F.BossSkeleton
				&& Plan->Participants[2].Config->Skeleton.Get() == F.PlayerSkeleton && Plan->Participants[0].Config->Animations.Num() == BossAnimationPaths().Num() && Plan->Participants[1].Config->Animations.Num() == BossAnimationPaths().Num()
				&& Plan->Participants[2].Config->Animations.Num() == PlayerAnimationPaths().Num());
			bOk &= Test.TestTrue(TEXT("the plan is still an incomplete subset: not a complete playable bundle, not a reservation, not ready"), !Plan->IsCompletePlayableBundle() && !Plan->IsReservation() && !Plan->IsReady());
		}
		return bOk;
	}

	/** A refused batch: no artifact, the named token and slot in ONE error, the detail text, the layer (only Preflight.* tokens, nothing from the allocation layer), nothing changed and nothing allocated. */
	bool ExpectPrepareRefused(FAutomationTestBase& Test, const FProductionFixture& F, const TCHAR* Label, const FRPGHydrationPreflightInput& Input, const TCHAR* Token, const TCHAR* SlotText, const TCHAR* Detail)
	{
		const FWorldState Before = F.Capture();
		FRPGPreparationResult Result = RPGBossHydrationPreparation::PrepareBatch(Input);
		bool bOk = true;
		bOk &= Test.TestFalse(FString::Printf(TEXT("%s: the preparation is refused"), Label), Result.Succeeded());
		bOk &= Test.TestFalse(FString::Printf(TEXT("%s: no artifact was returned"), Label), Result.Batch.IsValid());
		bOk &= Test.TestTrue(FString::Printf(TEXT("%s: ONE error names %s, %s and carries '%s' (got: %s)"), Label, Token, SlotText, Detail, *JoinErrors(Result.Errors)), AnyErrorHasAll(Result.Errors, Token, SlotText, Detail));
		bOk &= Test.TestTrue(FString::Printf(TEXT("%s: layer reached is the preflight inside PrepareBatch: no Preparation.* token (got: %s)"), Label, *JoinErrors(Result.Errors)), NoErrorStartsWith(Result.Errors, TEXT("Preparation.")));
		bOk &= ExpectRestored(Test, F, Before, Label);
		bOk &= ExpectNoPlannedNameAllocated(Test, F, Label);
		return bOk;
	}
}
}

using namespace ProductionPreparationTests;

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGProductionPreparationPositiveTest, "OneBossFight.Binding.ProductionPreparation.PositiveBatch",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGProductionPreparationPositiveTest::RunTest(const FString& Parameters)
{
	FProductionFixture F;
	if (!F.Prepare(*this))
	{
		return false;
	}

	// The isolated actors: native characters, holding the observed pack meshes, never begun play, no managed consumer.
	TestTrue(TEXT("both boss actors hold the observed boss mesh and the player actor the observed player mesh"), F.BossOneActor->GetMesh() && F.BossOneActor->GetMesh()->GetSkeletalMeshAsset() == F.BossMesh
		&& F.BossTwoActor->GetMesh() && F.BossTwoActor->GetMesh()->GetSkeletalMeshAsset() == F.BossMesh && F.PlayerActor->GetMesh() && F.PlayerActor->GetMesh()->GetSkeletalMeshAsset() == F.PlayerMesh);
	TestTrue(TEXT("the actors are native ACharacter objects, not Blueprint actors"), F.BossOneActor->GetClass() == ACharacter::StaticClass() && F.BossTwoActor->GetClass() == ACharacter::StaticClass() && F.PlayerActor->GetClass() == ACharacter::StaticClass());
	TestTrue(TEXT("no actor has begun play"), !F.BossOneActor->HasActorBegunPlay() && !F.BossTwoActor->HasActorBegunPlay() && !F.PlayerActor->HasActorBegunPlay());
	TestTrue(TEXT("no actor holds a managed consumer before the compile"), NoManagedConsumer(F.BossOneActor) && NoManagedConsumer(F.BossTwoActor) && NoManagedConsumer(F.PlayerActor));
	// The pairing of the observed meshes with their skeletons is real evidence, not assumed: a mismatch fails here with the observed names.
	TestTrue(FString::Printf(TEXT("the boss skeleton %s is compatible with the boss mesh %s"), *Describe(F.BossSkeleton), *Describe(F.BossMesh)), F.BossSkeleton->IsCompatibleMesh(F.BossMesh));
	TestTrue(FString::Printf(TEXT("the player skeleton %s is compatible with the player mesh %s"), *Describe(F.PlayerSkeleton), *Describe(F.PlayerMesh)), F.PlayerSkeleton->IsCompatibleMesh(F.PlayerMesh));

	// The genuine production compiler (bSyntheticFixture false): it loads the skeleton and every animation listed.
	F.CompileProduction();
	if (!ExpectProductionCompiled(*this, F))
	{
		return false;
	}
	ExpectProductionLeases(*this, F);

	// The state after the legitimate loads and the compile: everything below is compared against it.
	const FRPGHydrationPreflightInput Input = F.MakeInput();
	const FWorldState Before = F.Capture();
	const TArray<const UObject*> Touched = F.TouchedObjects();
	const TArray<int32> DirtyBefore = CaptureDirty(Touched);

	// Generation one: prepared, checked, then aborted explicitly.
	{
		FRPGPreparationResult First = RPGBossHydrationPreparation::PrepareBatch(Input);
		if (!TestTrue(FString::Printf(TEXT("the production batch prepares (errors: %s)"), *JoinErrors(First.Errors)), First.Succeeded()))
		{
			return false;
		}
		ExpectPrepared(*this, F, *First.Batch, Before);
		TArray<TWeakObjectPtr<UActorComponent>> FirstWeak = WeakOwned(*First.Batch);
		const FRPGPreparationAbortReport Report = First.Batch->Abort();
		TestTrue(FString::Printf(TEXT("explicit abort: clean report (errors: %s)"), *JoinErrors(Report.Errors)), Report.IsClean());
		TestTrue(TEXT("explicit abort destroyed twenty-four components, found none already gone and no contract violation"), Report.Destroyed == 24 && Report.AlreadyGone == 0 && Report.ContractViolations == 0 && !Report.bRefused);
		TestFalse(TEXT("the artifact is no longer prepared after the abort"), First.Batch->IsPrepared());
		TestEqual(TEXT("the artifact owns nothing after the abort"), First.Batch->GetOwnedComponentCount(), 0);
		// The weak identities of this generation are inspected NOW, before the names are created again (the engine replaces a destroyed object of the same name in place, so a stale pointer would alias the new one).
		ExpectAllDestroyed(*this, FirstWeak, TEXT("explicit abort"));
		FirstWeak.Reset();
		ExpectRestored(*this, F, Before, TEXT("explicit abort"));
		const FRPGPreparationAbortReport Again = First.Batch->Abort();
		TestTrue(TEXT("a second abort is idempotent: clean and nothing more destroyed"), Again.IsClean() && Again.Destroyed == 0 && Again.AlreadyGone == 0 && Again.ContractViolations == 0);
	}

	// Generation two: prepared again from the very same input and released by leaving the scope (the destructor runs the same cleanup).
	TArray<TWeakObjectPtr<UActorComponent>> SecondWeak;
	{
		FRPGPreparationResult Second = RPGBossHydrationPreparation::PrepareBatch(Input);
		if (!TestTrue(FString::Printf(TEXT("the same input prepares again after the abort (errors: %s)"), *JoinErrors(Second.Errors)), Second.Succeeded()))
		{
			return false;
		}
		ExpectPrepared(*this, F, *Second.Batch, Before);
		SecondWeak = WeakOwned(*Second.Batch);
	}
	ExpectAllDestroyed(*this, SecondWeak, TEXT("scope-exit abort"));
	ExpectRestored(*this, F, Before, TEXT("scope-exit abort"));

	TestTrue(TEXT("no touched package became dirty around the preparations and aborts (the class load, the spawn and the production compile are before the first snapshot)"), CaptureDirty(Touched) == DirtyBefore);
	TestTrue(TEXT("the pack character classes and meshes are still the observed objects (no default object was replaced)"), F.BossClass->GetDefaultObject<ACharacter>()->GetMesh()->GetSkeletalMeshAsset() == F.BossMesh
		&& F.PlayerClass->GetDefaultObject<ACharacter>()->GetMesh()->GetSkeletalMeshAsset() == F.PlayerMesh);
	TestTrue(TEXT("the production configs still hold the very skeletons and the full animation sets after the aborts"), F.BossOneConfig->Skeleton.Get() == F.BossSkeleton && F.BossTwoConfig->Skeleton.Get() == F.BossSkeleton
		&& F.PlayerConfig->Skeleton.Get() == F.PlayerSkeleton && F.BossOneConfig->Animations.Num() == BossAnimationPaths().Num() && F.BossTwoConfig->Animations.Num() == BossAnimationPaths().Num());

	AddInfo(TEXT("Real pack assets and the real production compiler; the preparation is an unregistered native subset: not registered, not a reservation, not Ready, not a complete playable boss. NOT established: a cold load, the cooked or packaged build, "
		"the arena level, the placed Blueprint boss, abilities or effects (class paths are structural only), animation playback, the authored boss definition (values and manifest rows are fixture values, the legacy epoch is not a game-instance epoch), "
		"serialized authoring proof, an organic native configure failure, BeginPlay, registration, context binding, activation or wiring."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGProductionPreparationLateRejectionTest, "OneBossFight.Binding.ProductionPreparation.LateRejection",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGProductionPreparationLateRejectionTest::RunTest(const FString& Parameters)
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
	const FRPGHydrationPreflightInput Valid = F.MakeInput();
	const TArray<const UObject*> Touched = F.TouchedObjects();
	const TArray<int32> DirtyBefore = CaptureDirty(Touched);
	const FWorldState Before = F.Capture();

	// The unmodified batch passes the preflight (which allocates nothing): every negative case below changes exactly one thing of it. The positive control through PrepareBatch itself runs at the END, after the
	// negative cases have shown that no planned name was ever allocated.
	{
		FPlanPtr Plan;
		const FRPGHydrationResult Preflight = RPGBossHydrationPreflight::CompilePreflight(Valid, Plan);
		TestTrue(FString::Printf(TEXT("control: the unmodified production batch passes the preflight (errors: %s)"), *JoinErrors(Preflight.Errors)), Preflight.IsReady() && Plan.IsValid() && Plan->Participants.Num() == 3);
		ExpectNoPlannedNameAllocated(*this, F, TEXT("control preflight"));
	}

	// Case 1, layer PREFLIGHT inside PrepareBatch: the later production member (boss two, after a valid first boss-core member) holds a compiled config whose first animation lease is null.
	{
		FRPGHydrationPreflightInput Input = F.MakeInput();
		Input.Requests[1].Config = CloneProduction(*F.BossTwoConfig, [](FRPGParticipantConfig& C) { C.Animations[0].Reset(); });
		ExpectPrepareRefused(*this, F, TEXT("a later member with a null animation lease"), Input, TEXT("Preflight.ProductionPrerequisite"), TEXT("[slot=BossTwo]"), TEXT("animation lease #0 is not valid"));
	}

	// Case 2, layer PREFLIGHT inside PrepareBatch: the later boss-core member selects a phase id its config does not hold.
	{
		FRPGHydrationPreflightInput Input = F.MakeInput();
		Input.Requests[1].SelectedPhaseId = FName(TEXT("PhaseMissing"));
		ExpectPrepareRefused(*this, F, TEXT("a later member selecting a phase its config does not have"), Input, TEXT("Preflight.PhaseRejected"), TEXT("[slot=BossTwo]"), TEXT("InvalidPhase.NotFound"));
	}

	// Case 3, TWO layers, each named: the production COMPILER refuses a later member's definition (a skeleton that is not the animations' skeleton; a transient negative control, nothing is retargeted) so no config exists
	// for it; that refusal is CompileParticipant's, not PrepareBatch's. The batch is then offered with the missing config, and the layer reached is the preflight's (Preflight.NoConfig).
	{
		TStrongObjectPtr<USkeleton> OtherSkeleton(NewObject<USkeleton>(GetTransientPackage()));
		TStrongObjectPtr<URPGBossDefinition> Bad(NewObject<URPGBossDefinition>());
		if (!TestTrue(TEXT("the transient negative control skeleton and definition were created"), OtherSkeleton.IsValid() && Bad.IsValid()))
		{
			return false;
		}
		FillDefinition(*Bad, BossTwoValues(), OtherSkeleton.Get(), BossAnimationPaths());
		FConfigPtr Out = F.BossTwoConfig; // a valid earlier config: a failing compile must clear it and publish nothing
		const FRPGHydrationResult CompileResult = RPGCombatHydration::CompileParticipant(*Bad, F.Content, ManifestHash(), Out);
		TestFalse(TEXT("layer CompileParticipant: the production compile of the later member's definition is refused"), CompileResult.IsReady());
		TestFalse(TEXT("layer CompileParticipant: the earlier output was cleared and no config was published"), Out.IsValid());
		TestTrue(FString::Printf(TEXT("layer CompileParticipant: the failure carries 'animation/skeleton identity mismatch' (got: %s)"), *JoinErrors(CompileResult.Errors)), AnyErrorContains(CompileResult.Errors, TEXT("animation/skeleton identity mismatch")));
		FRPGHydrationPreflightInput Input = F.MakeInput();
		Input.Requests[1].Config = Out;
		ExpectPrepareRefused(*this, F, TEXT("a later member without a config (its production compile was refused first)"), Input, TEXT("Preflight.NoConfig"), TEXT("[slot=BossTwo]"), TEXT("no compiled config lease was given"));
		AddInfo(TEXT("Case 3 layers: CompileParticipant refused the later definition (no config); PrepareBatch was then called with the missing config and its preflight refused it as Preflight.NoConfig. The first refusal is not a PrepareBatch refusal."));
	}

	TestTrue(TEXT("the negative cases left the world, every component set and the combat context as before"), SameWorld(Before, F.Capture()));

	// The unmodified positive control through PrepareBatch, then an abort.
	{
		FRPGPreparationResult Control = RPGBossHydrationPreparation::PrepareBatch(Valid);
		if (!TestTrue(FString::Printf(TEXT("control: the unmodified batch prepares (errors: %s)"), *JoinErrors(Control.Errors)), Control.Succeeded()))
		{
			return false;
		}
		ExpectPrepared(*this, F, *Control.Batch, Before);
		const FRPGPreparationAbortReport Report = Control.Batch->Abort();
		TestTrue(FString::Printf(TEXT("control: abort is clean and destroyed twenty-four components (errors: %s)"), *JoinErrors(Report.Errors)), Report.IsClean() && Report.Destroyed == 24 && Report.AlreadyGone == 0 && Report.ContractViolations == 0);
	}
	ExpectRestored(*this, F, Before, TEXT("control abort"));
	TestTrue(TEXT("no touched package became dirty around the cases"), CaptureDirty(Touched) == DirtyBefore);

	AddInfo(TEXT("Late rejection on real assets: the refusals come from the preflight inside PrepareBatch (a dependency, a selected phase, a missing config) and, separately, from CompileParticipant (a bad definition), each named. NOT covered: a "
		"mesh of another skeleton on a real character, a missing asset reference (it would log load warnings), an organic native configure failure, any wiring."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGProductionPreparationNameCollisionTest, "OneBossFight.Binding.ProductionPreparation.NameCollisionCleanup",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGProductionPreparationNameCollisionTest::RunTest(const FString& Parameters)
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
	const FRPGHydrationPreflightInput Input = F.MakeInput();
	const TArray<FExpectedComponent> Expected = ExpectedComponents();

	// The blocker: a REAL live unrelated scene component carrying the planned instance name of the THIRD managed component (the encounter) of the LATER owner (boss two). Its class is not a managed consumer class, so the
	// preflight's class guard (FindComponentByClass) does not see it: only the allocation guard can refuse. It is never registered and never begun.
	USceneComponent* Blocker = NewObject<USceneComponent>(F.BossTwoActor, USceneComponent::StaticClass(), FName(Expected[2].Name));
	if (!TestNotNull(TEXT("the blocker component was created under the later owner"), Blocker))
	{
		return false;
	}
	TStrongObjectPtr<USceneComponent> BlockerLease(Blocker);
	const FVector BlockerLocation(11.f, 22.f, 33.f);
	Blocker->SetRelativeLocation(BlockerLocation);
	for (const FExpectedComponent& Wanted : Expected)
	{
		TestTrue(FString::Printf(TEXT("the blocker's class is not the %s consumer class"), Wanted.Name), Blocker->GetClass() != Wanted.Class);
	}
	TestTrue(TEXT("the blocker is live, owned by boss two, named like the planned encounter component and not registered"), IsValid(Blocker) && Blocker->GetOwner() == F.BossTwoActor && Blocker->GetOuter() == F.BossTwoActor
		&& Blocker->GetFName() == FName(Expected[2].Name) && !Blocker->IsRegistered());

	// Every preexisting object under the actors (the actors' own components, the markers and the blocker) and the state around the batch.
	const AActor* const Actors[3] = {F.BossOneActor, F.BossTwoActor, F.PlayerActor};
	TSet<const UObject*> Preexisting;
	int32 LiveBefore[3] = {0, 0, 0};
	for (int32 ActorIndex = 0; ActorIndex < 3; ++ActorIndex)
	{
		TArray<UObject*> Inner;
		GetObjectsWithOuter(Actors[ActorIndex], Inner, /*bIncludeNestedObjects=*/false);
		for (const UObject* Object : Inner)
		{
			if (IsValid(Object))
			{
				Preexisting.Add(Object);
				++LiveBefore[ActorIndex];
			}
		}
	}
	TestTrue(TEXT("the blocker and the markers are among the preexisting objects"), Preexisting.Contains(Blocker) && Preexisting.Contains(F.Markers[0]) && Preexisting.Contains(F.Markers[1]) && Preexisting.Contains(F.Markers[2]));
	const FWorldState Before = F.Capture();
	const TArray<const UObject*> Touched = F.TouchedObjects();
	const TArray<int32> DirtyBefore = CaptureDirty(Touched);

	// The refused preparation.
	{
		FRPGPreparationResult Refused = RPGBossHydrationPreparation::PrepareBatch(Input);
		TestFalse(TEXT("the preparation is refused"), Refused.Succeeded());
		TestFalse(TEXT("no artifact was returned"), Refused.Batch.IsValid());
		TestTrue(FString::Printf(TEXT("ONE error carries Preparation.AllocationFailed, [slot=BossTwo] and [component=%s] (got: %s)"), Expected[2].Name, *JoinErrors(Refused.Errors)),
			AnyErrorHasAll(Refused.Errors, TEXT("Preparation.AllocationFailed"), TEXT("[slot=BossTwo]"), *FString::Printf(TEXT("[component=%s]"), Expected[2].Name)));
		TestTrue(FString::Printf(TEXT("exactly one error: the refusal itself, and the cleanup reported nothing (got: %s)"), *JoinErrors(Refused.Errors)), Refused.Errors.Num() == 1);
		TestTrue(TEXT("layer reached is the real allocation guard: only Preparation.* tokens, no Preflight.* token (the preflight passed)"), NoErrorStartsWith(Refused.Errors, TEXT("Preflight.")));
	}

	// The cleanup. The allocation order is boss one's twelve, then boss two's first two, then the blocked third: seven earlier components were allocated and must now be destroyed (a destroyed object stays findable under its
	// name until collection; no collection is forced). The later names were never allocated, the target never gets any, and the blocker is the very live object.
	bool bBossOneAllocatedAndDestroyed = true;
	for (const FExpectedComponent& Wanted : Expected)
	{
		const UObject* Found = StaticFindObjectFast(UObject::StaticClass(), const_cast<AActor*>(Actors[0]), FName(Wanted.Name));
		bBossOneAllocatedAndDestroyed = bBossOneAllocatedAndDestroyed && Found && !IsValid(Found) && Found->GetClass() == Wanted.Class;
	}
	TestTrue(TEXT("all twelve of boss one's components (earlier owner) were allocated and are now destroyed"), bBossOneAllocatedAndDestroyed);
	bool bBossTwoEarlierDestroyed = true;
	for (int32 Index = 0; Index < 2; ++Index)
	{
		const UObject* Found = StaticFindObjectFast(UObject::StaticClass(), const_cast<AActor*>(Actors[1]), FName(Expected[Index].Name));
		bBossTwoEarlierDestroyed = bBossTwoEarlierDestroyed && Found && !IsValid(Found) && Found->GetClass() == Expected[Index].Class;
	}
	TestTrue(TEXT("boss two's two components allocated before the blocked name (stagger, phases) were allocated and are now destroyed"), bBossTwoEarlierDestroyed);
	TestTrue(TEXT("the blocked name still resolves to the very blocker object, live and unchanged"), StaticFindObjectFast(UObject::StaticClass(), const_cast<AActor*>(Actors[1]), FName(Expected[2].Name)) == Blocker && IsValid(Blocker));
	bool bAllLaterNamesAbsent = true;
	for (int32 Index = 3; Index < Expected.Num(); ++Index)
	{
		bAllLaterNamesAbsent = bAllLaterNamesAbsent && StaticFindObjectFast(UObject::StaticClass(), const_cast<AActor*>(Actors[1]), FName(Expected[Index].Name)) == nullptr;
	}
	TestTrue(TEXT("all nine names after the blocked third component were never allocated"), bAllLaterNamesAbsent);
	bool bTargetNone = true;
	for (const FExpectedComponent& Wanted : Expected)
	{
		bTargetNone = bTargetNone && StaticFindObjectFast(UObject::StaticClass(), const_cast<AActor*>(Actors[2]), FName(Wanted.Name)) == nullptr;
	}
	TestTrue(TEXT("the target actor never received an allocation"), bTargetNone);
	ExpectRestored(*this, F, Before, TEXT("after the refused preparation"));
	TestTrue(TEXT("the blocker kept its identity and state: same object, class, owner, name, unregistered, not begun, relative location unchanged"), IsValid(Blocker) && Blocker->GetClass() == USceneComponent::StaticClass() && Blocker->GetOwner() == F.BossTwoActor
		&& Blocker->GetFName() == FName(Expected[2].Name) && !Blocker->IsRegistered() && !Blocker->HasBegunPlay() && Blocker->GetRelativeLocation() == BlockerLocation && F.BossTwoActor->GetComponents().Contains(Blocker));
	bool bPreexistingKept = true;
	for (const UObject* Object : Preexisting)
	{
		bPreexistingKept = bPreexistingKept && IsValid(Object);
	}
	TestTrue(TEXT("every preexisting object under the actors is still the same live object"), bPreexistingKept);
	int32 LiveAfter[3] = {0, 0, 0};
	for (int32 ActorIndex = 0; ActorIndex < 3; ++ActorIndex)
	{
		TArray<UObject*> Inner;
		GetObjectsWithOuter(Actors[ActorIndex], Inner, /*bIncludeNestedObjects=*/false);
		for (const UObject* Object : Inner)
		{
			if (IsValid(Object))
			{
				++LiveAfter[ActorIndex];
			}
		}
	}
	TestTrue(TEXT("no new live object remains under any actor"), LiveAfter[0] == LiveBefore[0] && LiveAfter[1] == LiveBefore[1] && LiveAfter[2] == LiveBefore[2]);

	// Remove ONLY the fixture-owned blocker. It is renamed away first (a destroyed object of another class would still hold the planned name and keep the allocation guard, and the engine, refusing), then destroyed.
	const FName RemovedName = MakeUniqueObjectName(F.BossTwoActor, USceneComponent::StaticClass(), TEXT("DD16RemovedBlocker"));
	Blocker->Rename(*RemovedName.ToString(), F.BossTwoActor, REN_DontCreateRedirectors | REN_NonTransactional);
	Blocker->DestroyComponent();
	BlockerLease.Reset();
	Blocker = nullptr;
	TestTrue(TEXT("the planned name is free of the blocker now (nothing live carries it)"), [&Actors, &Expected]()
		{
			const UObject* Found = StaticFindObjectFast(UObject::StaticClass(), const_cast<AActor*>(Actors[1]), FName(Expected[2].Name));
			return !Found || !IsValid(Found);
		}());
	const FWorldState AfterRemoval = F.Capture();
	TestTrue(TEXT("boss two lost exactly the blocker; boss one and the target are as before"), AfterRemoval.Actors[1].Components.Num() == Before.Actors[1].Components.Num() - 1 && SameActor(AfterRemoval.Actors[0], Before.Actors[0])
		&& SameActor(AfterRemoval.Actors[2], Before.Actors[2]));
	TestTrue(TEXT("the markers are still the same live objects"), IsValid(F.Markers[0]) && IsValid(F.Markers[1]) && IsValid(F.Markers[2]));

	// The same input again. NOTE: the failed attempt left destroyed (not collected) objects of the exact planned classes under seven of the names; the engine replaces those in place. That reuse is observed here, it is
	// not a claim about garbage-collected names, and no reference to a destroyed object is held across it.
	{
		FRPGPreparationResult Retry = RPGBossHydrationPreparation::PrepareBatch(Input);
		if (!TestTrue(FString::Printf(TEXT("the same input prepares after only the blocker was removed (errors: %s)"), *JoinErrors(Retry.Errors)), Retry.Succeeded()))
		{
			return false;
		}
		ExpectPrepared(*this, F, *Retry.Batch, AfterRemoval);
		TArray<TWeakObjectPtr<UActorComponent>> RetryWeak = WeakOwned(*Retry.Batch);
		const FRPGPreparationAbortReport Report = Retry.Batch->Abort();
		TestTrue(FString::Printf(TEXT("the retry's abort is clean and destroyed twenty-four components (errors: %s)"), *JoinErrors(Report.Errors)), Report.IsClean() && Report.Destroyed == 24 && Report.AlreadyGone == 0 && Report.ContractViolations == 0);
		ExpectAllDestroyed(*this, RetryWeak, TEXT("retry abort"));
	}
	ExpectRestored(*this, F, AfterRemoval, TEXT("retry abort"));
	TestTrue(TEXT("no touched package became dirty around the cases"), CaptureDirty(Touched) == DirtyBefore);

	AddInfo(TEXT("Name collision on real assets: a real live unrelated component under a planned instance name of the later owner is refused by the allocation guard (Preparation.AllocationFailed with the slot and the component name), the earlier allocations "
		"on both owners are cleaned, the blocker and every other preexisting object keep identity and state. NOT covered: garbage-collected name reuse (no collection is forced), a destroyed blocker of another class still holding the name "
		"(the blocker is renamed away before it is destroyed), an organic native configure failure, registration, any wiring."));
	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
