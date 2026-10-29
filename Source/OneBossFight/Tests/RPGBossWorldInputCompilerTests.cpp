// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Animation/AnimSequence.h"
#include "Animation/AnimSequenceBase.h"
#include "Animation/Skeleton.h"
#include "Async/Async.h"
#include "Components/ActorComponent.h"
#include "Components/SceneComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"
#include "GameFramework/Character.h"
#include "HAL/IConsoleManager.h"
#include "Player/RPGBossDormantWake.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossHydrationPreflight.h"
#include "Player/RPGBossPhases.h"
#include "Player/RPGBossPosture.h"
#include "Player/RPGBossStagger.h"
#include "Player/RPGBossWorldInputCompiler.h"
#include "Player/RPGCombatCatalog.h"
#include "Player/RPGEncounterBinding.h"
#include "UObject/Package.h"
#include "UObject/StrongObjectPtr.h"
#include "UObject/UObjectHash.h"

// DD17: the world-bound encounter input compiler (RPGBossWorldInputCompiler::CompileWorldInput) driven in a REAL game-instance world: the content epoch comes from the game instance's own catalog subsystem, started by the
// engine's own lifecycle (UGameInstance::InitializeStandalone, which creates the world context, a world and runs Init, which initializes every game-instance subsystem, the project's UGameInstanceSubsystem
// URPGCombatCatalogSubsystem included, with its actual default latch), and is read back through RPGCombatRegistry::ForWorld. No Legacy() epoch is injected, nothing is mocked and no cvar or asset is changed.
// What it uses: the two pack character Blueprint classes are loaded only to READ the mesh asset their default object holds (no Blueprint actor is spawned, no default object changes, no asset is saved); the observed mesh
// and skeleton go on three isolated native ACharacter actors (two boss-core, one target) finished before any call; one real ARPGEncounterBinding actor carries the explicit participants, their targets and their three
// transient production-compatible definitions (the authoring-default animation dependencies, hand-authored manifest rows, fixture values). The setup is copied from DD14 and DD16 into this file.
// What it can establish, for these exact assets in this editor binary: PositiveGameInstance: the output identities (world, encounter GUID, the very epoch lease the game instance published, per-slot actors, targets,
// roles, selected phases, production configs holding that lease, skeleton and animation leases), the output feeds the accepted preflight, and the call changes no actor, component, combat context or touched package.
// ContentRejections: no game instance and a game instance without the catalog subsystem fail with the named content error. InputRejections: every named input failure (world, binding, GUID, manifest hash, selections,
// actors, targets, definitions, the production compile layer, the preflight layer, off-thread) clears a populated output, allocates and binds nothing, names its layer, and an unmodified positive control follows.
// What it does NOT establish: which source the game instance latched is only logged (the default latch is whatever it is: this file does not require data), epoch drift DURING a call (it cannot be provoked without a
// callback, a cvar or an injection framework, so that branch is not exercised: the identity rechecks are source claims only), a cold load (the assets may already be in memory), the packaged build, the arena level, the
// placed Blueprint boss, the real boss definition asset (values, phases and manifest rows are fixture values), serialized authoring, a registration, preparation, BeginPlay, context binding, reservation, readiness,
// legacy suppression or any wiring. The compiled input is only an input.

namespace
{
namespace WorldInputTests
{
	using FSelection = RPGBossWorldInputCompiler::FSelection;
	using FEpochPtr = TSharedPtr<const RPGCombatRegistry::FEpoch>;
	using FConfigPtr = TSharedPtr<const FRPGParticipantConfig>;

	// The two pack character classes, under always-cooked directories. Only their default object's mesh is read.
	const TCHAR* const PlayerClassPath = TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter.BP_CombatPlayerCharacter_C");
	const TCHAR* const BossClassPath = TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss.BP_ExampleGreatSwordBoss_C");

	/** The explicit per-member values of a transient definition (the bosses differ in id, selected phase id and values). */
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
		return FMemberValues{TEXT("WorldInputBossOne"), TEXT("WorldInputBossOneLook"), TEXT("PhaseTwo"), 0.35f, 3500.f, 73.5f, 3.25f};
	}

	FMemberValues BossTwoValues()
	{
		return FMemberValues{TEXT("WorldInputBossTwo"), TEXT("WorldInputBossTwoLook"), TEXT("PhaseAlt"), 0.5f, 4100.f, 88.f, 4.5f};
	}

	FMemberValues PlayerValues()
	{
		return FMemberValues{TEXT("WorldInputPlayer"), TEXT("WorldInputPlayerLook"), TEXT("PhaseTwo"), 0.35f, 3500.f, 73.5f, 3.25f};
	}

	FString ManifestHash()
	{
		return FString::ChrN(64, TEXT('b')); // a fixture hash, not a real manifest hash
	}

	/** Which kind of world a fixture builds. RealGameInstance is the engine's own standalone lifecycle; the other two exist only for the content rejections. */
	enum class EWorldKind : uint8
	{
		RealGameInstance,
		NoGameInstance,
		UninitializedGameInstance,
	};

	/** A test-local world with game-thread cleanup. In the real kind the game instance is created and started exactly as UGameEngine does (outer the engine, InitializeStandalone) and shut down with Shutdown. */
	struct FGameWorld
	{
		UWorld* World = nullptr;
		TStrongObjectPtr<UGameInstance> GameInstance;
		EWorldKind Kind;

		explicit FGameWorld(EWorldKind InKind)
			: Kind(InKind)
		{
			if (!GEngine)
			{
				return;
			}
			if (Kind == EWorldKind::RealGameInstance)
			{
				GameInstance.Reset(NewObject<UGameInstance>(GEngine));
				if (!GameInstance.IsValid())
				{
					return;
				}
				GameInstance->InitializeStandalone();
				World = GameInstance->GetWorld();
				if (World)
				{
					World->InitializeActorsForPlay(FURL());
				}
				return;
			}
			World = UWorld::CreateWorld(EWorldType::Game, /*bInformEngineOfWorld=*/false);
			if (World)
			{
				FWorldContext& Context = GEngine->CreateNewWorldContext(EWorldType::Game);
				Context.SetCurrentWorld(World);
				World->InitializeActorsForPlay(FURL());
				if (Kind == EWorldKind::UninitializedGameInstance)
				{
					// A game instance object that never ran Init: its subsystem collection is empty.
					GameInstance.Reset(NewObject<UGameInstance>(GEngine));
					if (GameInstance.IsValid())
					{
						World->SetGameInstance(GameInstance.Get());
					}
				}
			}
		}

		~FGameWorld()
		{
			if (Kind == EWorldKind::RealGameInstance)
			{
				if (GameInstance.IsValid())
				{
					GameInstance->Shutdown();
				}
			}
			else if (Kind == EWorldKind::UninitializedGameInstance && World)
			{
				World->SetGameInstance(nullptr);
			}
			if (World)
			{
				GEngine->DestroyWorldContext(World);
				World->DestroyWorld(/*bInformEngineOfWorld=*/false);
			}
		}

		FGameWorld(const FGameWorld&) = delete;
		FGameWorld& operator=(const FGameWorld&) = delete;

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

		AActor* SpawnPlainActor() const { return World ? World->SpawnActor<AActor>() : nullptr; }
		ARPGEncounterBinding* SpawnBindingActor() const { return World ? World->SpawnActor<ARPGEncounterBinding>() : nullptr; }
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
			// Independent world-input compiler fixture manifest, no factory extraction.
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
		Field.SourcePath = TEXT("DD17 world input fixture, not live provenance");
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

	/** Valid typed fixture values for the whole record (authoring defaults except the explicit per-member values). */
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

	FString Describe(const UObject* Object)
	{
		return Object ? FString::Printf(TEXT("%s (%s)"), *Object->GetPathName(), *Object->GetClass()->GetName()) : FString(TEXT("none"));
	}

	FString JoinErrors(const TArray<FString>& Errors)
	{
		return FString::Join(Errors, TEXT(" | "));
	}

	/** One single error that carries the token at its start, the where text and a further text (an empty text always matches). */
	bool AnyErrorHasAll(const TArray<FString>& Errors, const TCHAR* Token, const TCHAR* WhereText, const TCHAR* FurtherText)
	{
		return Errors.ContainsByPredicate([Token, WhereText, FurtherText](const FString& E) { return E.StartsWith(Token) && E.Contains(WhereText) && E.Contains(FurtherText); });
	}

	/** The dirty flag of the package of each object, compared around a call after the legitimate loads and the setup. */
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

	/** What a call must leave alone, per actor: the sorted component set, the registered and begun flags of each, the begun flag of the actor and the mesh asset its character holds; and the combat context counts. */
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

	bool SameWorld(const FWorldState& A, const FWorldState& B)
	{
		if (A.Actors.Num() != B.Actors.Num() || A.Bound != B.Bound || A.Ready != B.Ready)
		{
			return false;
		}
		for (int32 Index = 0; Index < A.Actors.Num(); ++Index)
		{
			const FActorState& X = A.Actors[Index];
			const FActorState& Y = B.Actors[Index];
			if (X.bBegun != Y.bBegun || X.MeshAsset != Y.MeshAsset || X.Components != Y.Components || X.Flags != Y.Flags)
			{
				return false;
			}
		}
		return true;
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

	/** The reviewed instance names of the twelve managed consumers, written out independently. */
	const TCHAR* const PlannedNames[12] = {TEXT("RPGBossStagger"), TEXT("RPGBossPhases"), TEXT("RPGBossEncounter"), TEXT("RPGBossDormantWake"), TEXT("RPGBossPosture"), TEXT("RPGBossBleed"), TEXT("RPGBossLowSweep"), TEXT("RPGBossShockwave"), TEXT("RPGBossHealPunish"), TEXT("RPGBossLook"), TEXT("RPGBossCloseClipSwap"), TEXT("RPGBossDeath")};

	/** A populated output whose every part must be gone after a failure: the leases of a good output, a new encounter GUID and the LIVE world of the case (the good output may come from a world that no longer exists). */
	FRPGHydrationPreflightInput MakeSentinel(const FRPGHydrationPreflightInput& Good, UWorld* LiveWorld)
	{
		FRPGHydrationPreflightInput Sentinel = Good;
		Sentinel.EncounterInstance = FGuid::NewGuid();
		Sentinel.ExpectedWorld = LiveWorld;
		return Sentinel;
	}

	bool IsPopulated(const FRPGHydrationPreflightInput& Input)
	{
		return Input.Requests.Num() == 3 && Input.EncounterInstance.IsValid() && Input.ExpectedWorld.IsValid() && Input.ExpectedContent.IsValid();
	}

	bool IsCleared(const FRPGHydrationPreflightInput& Input)
	{
		return Input.Requests.IsEmpty() && !Input.EncounterInstance.IsValid() && !Input.ExpectedWorld.IsValid() && !Input.ExpectedContent.IsValid();
	}

	/** The real pack mesh and skeleton, three isolated native actors, an unrelated marker on each, three transient definitions and the real binding actor with its explicit participants. */
	struct FWorldInputFixture
	{
		FGameWorld Scope;
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
		TStrongObjectPtr<URPGBossDefinition> BossOneDefinition;
		TStrongObjectPtr<URPGBossDefinition> BossTwoDefinition;
		TStrongObjectPtr<URPGBossDefinition> PlayerDefinition;
		ARPGEncounterBinding* Binding = nullptr;
		FGuid Encounter;

		explicit FWorldInputFixture(EWorldKind Kind)
			: Scope(Kind)
		{
		}

		/** False (with an error naming the unsupported precondition) when a precondition cannot be built. */
		bool Prepare(FAutomationTestBase& Test)
		{
			if (!Scope.World)
			{
				Test.AddError(TEXT("unsupported precondition: the world could not be created"));
				return false;
			}
			if (Scope.Kind == EWorldKind::RealGameInstance)
			{
				// The real game instance latched these startup cvars when it initialized. They are only READ and logged here, never changed; a non-default startup fixture is not the default latch this file is about.
				FString Latched;
				bool bDefaultLatch = true;
				const TCHAR* const CvarNames[4] = {TEXT("rpg.CatalogSource"), TEXT("rpg.CatalogPath"), TEXT("rpg.CatalogTestFourth"), TEXT("rpg.CatalogTestInvalid")};
				const TCHAR* const CvarDefaults[4] = {TEXT("auto"), TEXT(""), TEXT("0"), TEXT("0")};
				for (int32 CvarIndex = 0; CvarIndex < 4; ++CvarIndex)
				{
					const IConsoleVariable* Variable = IConsoleManager::Get().FindConsoleVariable(CvarNames[CvarIndex]);
					const FString Value = Variable ? Variable->GetString() : FString(TEXT("(not registered)"));
					Latched += FString::Printf(TEXT("%s='%s' "), CvarNames[CvarIndex], *Value);
					bDefaultLatch = bDefaultLatch && (!Variable || Value.Equals(CvarDefaults[CvarIndex], ESearchCase::IgnoreCase));
				}
				Test.AddInfo(FString::Printf(TEXT("startup cvars at the real game instance: %s"), *Latched));
				if (!bDefaultLatch)
				{
					Test.AddError(FString::Printf(TEXT("unsupported precondition: a catalog startup cvar is not at its default (%s); this fixture needs the default latch and never changes a cvar"), *Latched));
					return false;
				}
			}
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
			Binding = SpawnBinding(MakeParticipants(), Encounter);
			if (!Binding)
			{
				Test.AddError(TEXT("unsupported precondition: the encounter binding actor could not be spawned"));
				return false;
			}
			return true;
		}

		/** The valid explicit participants: both bosses target the player slot, the target-only player targets the first boss; every member has its own production definition. */
		TArray<FRPGPlacedParticipantBinding> MakeParticipants() const
		{
			TArray<FRPGPlacedParticipantBinding> Participants;
			FRPGPlacedParticipantBinding One;
			One.Slot = TEXT("BossOne");
			One.TargetSlot = TEXT("Player");
			One.Actor = BossOneActor;
			One.Definition = BossOneDefinition.Get();
			Participants.Add(One);
			FRPGPlacedParticipantBinding Two;
			Two.Slot = TEXT("BossTwo");
			Two.TargetSlot = TEXT("Player");
			Two.Actor = BossTwoActor;
			Two.Definition = BossTwoDefinition.Get();
			Participants.Add(Two);
			FRPGPlacedParticipantBinding Target;
			Target.Slot = TEXT("Player");
			Target.TargetSlot = TEXT("BossOne");
			Target.Actor = PlayerActor;
			Target.Definition = PlayerDefinition.Get();
			Participants.Add(Target);
			return Participants;
		}

		/** A real placed binding actor of this world (or of a given world), carrying the participants and the explicit encounter GUID. */
		ARPGEncounterBinding* SpawnBinding(const TArray<FRPGPlacedParticipantBinding>& Participants, const FGuid& Guid) const
		{
			ARPGEncounterBinding* Created = Scope.SpawnBindingActor();
			if (Created)
			{
				Created->EncounterInstance = Guid;
				Created->Participants = Participants;
			}
			return Created;
		}

		/** The valid explicit selections, written as literals. */
		TArray<FSelection> MakeSelections() const
		{
			TArray<FSelection> Selections;
			Selections.Add(FSelection{TEXT("BossOne"), ERPGPreflightRole::BossCore, TEXT("PhaseTwo")});
			Selections.Add(FSelection{TEXT("BossTwo"), ERPGPreflightRole::BossCore, TEXT("PhaseAlt")});
			Selections.Add(FSelection{TEXT("Player"), ERPGPreflightRole::TargetOnly, NAME_None});
			return Selections;
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

		/** The epoch the world's own game instance catalog subsystem published (null when there is none). */
		FEpochPtr PublishedEpoch() const
		{
			const UGameInstance* GameInstance = Scope.World ? Scope.World->GetGameInstance() : nullptr;
			const URPGCombatCatalogSubsystem* Subsystem = GameInstance ? GameInstance->GetSubsystem<URPGCombatCatalogSubsystem>() : nullptr;
			return Subsystem ? Subsystem->GetEpoch() : FEpochPtr();
		}

		/** No object, not even a destroyed one, carries a planned managed-consumer instance name under any of the three actors: nothing was allocated. */
		bool NothingAllocated() const
		{
			for (const AActor* Actor : {static_cast<const AActor*>(BossOneActor), static_cast<const AActor*>(BossTwoActor), static_cast<const AActor*>(PlayerActor)})
			{
				for (const TCHAR* Name : PlannedNames)
				{
					if (StaticFindObjectFast(UObject::StaticClass(), const_cast<AActor*>(Actor), FName(Name)) != nullptr)
					{
						return false;
					}
				}
			}
			return true;
		}
	};

	/** The exact success shape of an output, written as literal expectations: identities, per-slot actors, targets, roles, selected phases, production configs holding the very epoch lease. */
	bool ExpectOutput(FAutomationTestBase& Test, const FWorldInputFixture& F, const FRPGHydrationPreflightInput& Output, const FEpochPtr& Epoch, const TCHAR* Label)
	{
		bool bOk = true;
		bOk &= Test.TestTrue(FString::Printf(TEXT("%s: the output holds the expected world, the binding's explicit encounter GUID and the very epoch lease the game instance published"), Label),
			Output.ExpectedWorld.Get() == F.Scope.World && Output.EncounterInstance == F.Encounter && Output.EncounterInstance == F.Binding->EncounterInstance && Epoch.IsValid() && Output.ExpectedContent.Get() == Epoch.Get());
		if (!Test.TestEqual(FString::Printf(TEXT("%s: three requests"), Label), Output.Requests.Num(), 3))
		{
			return false;
		}
		struct FWanted
		{
			AActor* Actor;
			const TCHAR* Slot;
			const TCHAR* Target;
			ERPGPreflightRole Role;
			const TCHAR* Phase;
			const TCHAR* BossId;
			int32 Animations;
			USkeleton* Skeleton;
		};
		const FWanted Wanted[3] = {
			{F.BossOneActor, TEXT("BossOne"), TEXT("Player"), ERPGPreflightRole::BossCore, TEXT("PhaseTwo"), TEXT("WorldInputBossOne"), 9, F.BossSkeleton},
			{F.BossTwoActor, TEXT("BossTwo"), TEXT("Player"), ERPGPreflightRole::BossCore, TEXT("PhaseAlt"), TEXT("WorldInputBossTwo"), 9, F.BossSkeleton},
			{F.PlayerActor, TEXT("Player"), TEXT("BossOne"), ERPGPreflightRole::TargetOnly, TEXT(""), TEXT("WorldInputPlayer"), 1, F.PlayerSkeleton}};
		for (int32 Index = 0; Index < 3; ++Index)
		{
			const FRPGHydrationPreflightRequest& Request = Output.Requests[Index];
			const FWanted& Want = Wanted[Index];
			const FString Which = FString::Printf(TEXT("%s request #%d (%s)"), Label, Index, Want.Slot);
			bOk &= Test.TestTrue(FString::Printf(TEXT("%s: the actor, slot, explicit target, role and explicit selected phase are as given"), *Which),
				Request.Actor.Get() == Want.Actor && Request.Slot == FName(Want.Slot) && Request.TargetSlot == FName(Want.Target) && Request.Role == Want.Role && Request.SelectedPhaseId == FName(Want.Phase));
			if (!Test.TestTrue(FString::Printf(TEXT("%s: a production config was compiled"), *Which), Request.Config.IsValid()))
			{
				bOk = false;
				continue;
			}
			const FRPGParticipantConfig& Config = *Request.Config;
			bOk &= Test.TestTrue(FString::Printf(TEXT("%s: not a synthetic fixture, the definition's boss id, the explicit manifest hash and the very epoch lease"), *Which),
				!Config.bSyntheticFixture && Config.BossId == FName(Want.BossId) && Config.StableManifestHash == ManifestHash() && Config.Content.Get() == Epoch.Get());
			bOk &= Test.TestTrue(FString::Printf(TEXT("%s: the retained skeleton and %d animation leases"), *Which, Want.Animations), Config.Skeleton.Get() == Want.Skeleton && Config.Animations.Num() == Want.Animations);
			for (int32 AnimationIndex = 0; AnimationIndex < Config.Animations.Num(); ++AnimationIndex)
			{
				const UAnimSequenceBase* Animation = Config.Animations[AnimationIndex].Get();
				bOk &= Test.TestTrue(FString::Printf(TEXT("%s animation #%d is a valid lease on the compiled skeleton"), *Which, AnimationIndex), Animation && IsValid(Animation) && Animation->GetSkeleton() == Config.Skeleton.Get());
			}
			if (Request.Role == ERPGPreflightRole::BossCore)
			{
				bOk &= Test.TestTrue(FString::Printf(TEXT("%s: the config holds the selected phase"), *Which), Config.Phases.ContainsByPredicate([&Request](const FRPGPhaseConfig& Phase) { return Phase.PhaseId == Request.SelectedPhaseId; }));
			}
		}
		return bOk;
	}

	/** A refused call: not ready, ONE error carrying the token, the where text and the detail, a populated output cleared, nothing changed, allocated or bound. */
	bool ExpectRejected(FAutomationTestBase& Test, const FWorldInputFixture& F, const FRPGHydrationPreflightInput& Good, const TCHAR* Label, UWorld* World, const ARPGEncounterBinding* Binding, const TArray<FSelection>& Selections,
		const FString& Hash, const TCHAR* Token, const TCHAR* Where, const TCHAR* Detail)
	{
		FRPGHydrationPreflightInput Output = MakeSentinel(Good, F.Scope.World);
		bool bOk = Test.TestTrue(FString::Printf(TEXT("%s: the output starts populated (the sentinel)"), Label), IsPopulated(Output));
		const FWorldState Before = F.Capture();
		const FRPGHydrationResult Result = RPGBossWorldInputCompiler::CompileWorldInput(World, Binding, Selections, Hash, Output);
		bOk &= Test.TestFalse(FString::Printf(TEXT("%s: refused"), Label), Result.IsReady());
		bOk &= Test.TestTrue(FString::Printf(TEXT("%s: ONE error names %s, %s and '%s' (got: %s)"), Label, Token, Where, Detail, *JoinErrors(Result.Errors)), AnyErrorHasAll(Result.Errors, Token, Where, Detail));
		bOk &= Test.TestTrue(FString::Printf(TEXT("%s: the populated output was cleared completely"), Label), IsCleared(Output));
		bOk &= Test.TestTrue(FString::Printf(TEXT("%s: no actor, component, mesh, begun flag or combat context changed"), Label), SameWorld(Before, F.Capture()));
		bOk &= Test.TestTrue(FString::Printf(TEXT("%s: nothing was allocated or bound: no managed consumer, no object under a planned name"), Label), NoManagedConsumer(F.BossOneActor) && NoManagedConsumer(F.BossTwoActor) && NoManagedConsumer(F.PlayerActor) && F.NothingAllocated());
		return bOk;
	}
}
}

using namespace WorldInputTests;

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGWorldInputPositiveTest, "OneBossFight.Binding.WorldInput.PositiveGameInstance",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGWorldInputPositiveTest::RunTest(const FString& Parameters)
{
	FWorldInputFixture F(EWorldKind::RealGameInstance);
	if (!F.Prepare(*this))
	{
		return false;
	}
	// The real game-instance lifecycle: the world's game instance is the one the engine lifecycle started, and its catalog subsystem published an epoch with its actual default latch.
	UGameInstance* GameInstance = F.Scope.World->GetGameInstance();
	const URPGCombatCatalogSubsystem* Subsystem = GameInstance ? GameInstance->GetSubsystem<URPGCombatCatalogSubsystem>() : nullptr;
	if (!TestTrue(TEXT("precondition: the world's game instance is the standalone one and holds the project's catalog subsystem"), GameInstance && GameInstance == F.Scope.GameInstance.Get() && Subsystem))
	{
		return false;
	}
	const FEpochPtr Epoch = F.PublishedEpoch();
	if (!TestTrue(TEXT("precondition: the catalog subsystem published a valid epoch"), Epoch.IsValid() && Epoch->Id.IsValid() && RPGCombatRegistry::ForWorld(F.Scope.World).Get() == Epoch.Get()))
	{
		return false;
	}
	AddInfo(FString::Printf(TEXT("the game instance %s latched source '%s' path '%s'; its published epoch id %s source '%s' (reason '%s'); the source is logged, never required"), *Describe(GameInstance), *Subsystem->GetLatchedSource(),
		*Subsystem->GetLatchedPath(), *Epoch->Id.ToString(), *Epoch->Source, *Epoch->Reason));
	TestTrue(TEXT("the actors are native ACharacter objects, not Blueprint actors, none begun, none holding a managed consumer"), F.BossOneActor->GetClass() == ACharacter::StaticClass() && F.BossTwoActor->GetClass() == ACharacter::StaticClass()
		&& F.PlayerActor->GetClass() == ACharacter::StaticClass() && !F.BossOneActor->HasActorBegunPlay() && !F.BossTwoActor->HasActorBegunPlay() && !F.PlayerActor->HasActorBegunPlay()
		&& NoManagedConsumer(F.BossOneActor) && NoManagedConsumer(F.BossTwoActor) && NoManagedConsumer(F.PlayerActor));
	TestTrue(FString::Printf(TEXT("the boss skeleton %s is compatible with the boss mesh %s and the player skeleton %s with the player mesh %s"), *Describe(F.BossSkeleton), *Describe(F.BossMesh), *Describe(F.PlayerSkeleton), *Describe(F.PlayerMesh)),
		F.BossSkeleton->IsCompatibleMesh(F.BossMesh) && F.PlayerSkeleton->IsCompatibleMesh(F.PlayerMesh));

	const TArray<FSelection> Selections = F.MakeSelections();
	const FWorldState StateBeforeFirst = F.Capture();
	// A populated sentinel output: a success replaces it completely.
	FRPGHydrationPreflightInput First;
	First.EncounterInstance = FGuid::NewGuid();
	First.Requests.AddDefaulted(2);
	const FRPGHydrationResult FirstResult = RPGBossWorldInputCompiler::CompileWorldInput(F.Scope.World, F.Binding, Selections, ManifestHash(), First);
	if (!TestTrue(FString::Printf(TEXT("the world input compiles on the real game-instance world (errors: %s)"), *JoinErrors(FirstResult.Errors)), FirstResult.IsReady() && FirstResult.Errors.IsEmpty()))
	{
		return false;
	}
	ExpectOutput(*this, F, First, Epoch, TEXT("first call"));
	TestTrue(TEXT("the first call changed no actor, component, mesh, begun flag or combat context"), SameWorld(StateBeforeFirst, F.Capture()));

	// The output is a valid input of the accepted preflight (load-free): the whole batch passes and a plan exists.
	TSharedPtr<const FRPGHydrationPreflightPlan> Plan;
	const FRPGHydrationResult Preflight = RPGBossHydrationPreflight::CompilePreflight(First, Plan);
	TestTrue(FString::Printf(TEXT("the output passes the accepted preflight as published (errors: %s)"), *JoinErrors(Preflight.Errors)), Preflight.IsReady() && Plan.IsValid() && Plan->Participants.Num() == 3);

	// A second call, after the first call's legitimate loads: the actors, components, context and touched packages are unchanged around it, and it publishes the same epoch lease.
	TArray<const UObject*> Touched{F.PlayerClass, F.BossClass, F.PlayerMesh, F.BossMesh, F.PlayerSkeleton, F.BossSkeleton};
	for (const FRPGHydrationPreflightRequest& Request : First.Requests)
	{
		for (const TStrongObjectPtr<UAnimSequenceBase>& Animation : Request.Config->Animations)
		{
			Touched.Add(Animation.Get());
		}
	}
	const FWorldState StateBefore = F.Capture();
	const TArray<int32> DirtyBefore = CaptureDirty(Touched);
	FRPGHydrationPreflightInput Second;
	const FRPGHydrationResult SecondResult = RPGBossWorldInputCompiler::CompileWorldInput(F.Scope.World, F.Binding, Selections, ManifestHash(), Second);
	if (!TestTrue(FString::Printf(TEXT("a second call also compiles (errors: %s)"), *JoinErrors(SecondResult.Errors)), SecondResult.IsReady()))
	{
		return false;
	}
	ExpectOutput(*this, F, Second, Epoch, TEXT("second call"));
	TestTrue(TEXT("the second call is a different output with different config objects but the same epoch lease"), Second.Requests[0].Config.Get() != First.Requests[0].Config.Get() && Second.ExpectedContent.Get() == First.ExpectedContent.Get());
	TestTrue(TEXT("the second call changed no actor, component, mesh, begun flag or combat context"), SameWorld(StateBefore, F.Capture()));
	TestTrue(TEXT("no touched package became dirty around the second call"), CaptureDirty(Touched) == DirtyBefore);
	TestTrue(TEXT("no managed consumer exists and nothing was allocated under any planned name"), NoManagedConsumer(F.BossOneActor) && NoManagedConsumer(F.BossTwoActor) && NoManagedConsumer(F.PlayerActor) && F.NothingAllocated());
	TestTrue(TEXT("the binding and its participants are unchanged by the calls"), F.Binding->EncounterInstance == F.Encounter && F.Binding->Participants.Num() == 3 && F.Binding->Participants[0].Actor.Get() == F.BossOneActor
		&& F.Binding->Participants[1].Definition.Get() == F.BossTwoDefinition.Get() && F.Binding->Participants[2].Slot == FName(TEXT("Player")));
	TestTrue(TEXT("the game instance and the published epoch are still the same ones"), F.Scope.World->GetGameInstance() == GameInstance && F.PublishedEpoch().Get() == Epoch.Get());
	TestTrue(TEXT("the pack character classes and meshes are still the observed objects (no default object was replaced)"), F.BossClass->GetDefaultObject<ACharacter>()->GetMesh()->GetSkeletalMeshAsset() == F.BossMesh
		&& F.PlayerClass->GetDefaultObject<ACharacter>()->GetMesh()->GetSkeletalMeshAsset() == F.PlayerMesh);

	AddInfo(TEXT("Real game-instance lifecycle, real pack assets and the real production compiler; the output is only a preflight INPUT: no callback ran, no component was created, nothing was registered, bound, prepared, reserved or made Ready. NOT established: epoch drift during a call "
		"(not provokable without a callback, cvar or injection framework), the latched source (logged only), a cold load, the cooked or packaged build, the arena level, the placed Blueprint boss, the authored boss definition (values and manifest rows are fixture "
		"values), serialized authoring proof, BeginPlay, registration, context binding, activation or wiring."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGWorldInputContentTest, "OneBossFight.Binding.WorldInput.ContentRejections",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGWorldInputContentTest::RunTest(const FString& Parameters)
{
	// The valid sentinel output comes from a real game-instance world, in this scope, and is released with it.
	FRPGHydrationPreflightInput Good;
	{
		FWorldInputFixture Real(EWorldKind::RealGameInstance);
		if (!Real.Prepare(*this))
		{
			return false;
		}
		const FRPGHydrationResult RealResult = RPGBossWorldInputCompiler::CompileWorldInput(Real.Scope.World, Real.Binding, Real.MakeSelections(), ManifestHash(), Good);
		if (!TestTrue(FString::Printf(TEXT("the real game-instance world compiles first, giving a populated sentinel for the failures (errors: %s)"), *JoinErrors(RealResult.Errors)), RealResult.IsReady() && IsPopulated(Good)))
		{
			return false;
		}
	}

	// A world without any game instance: the epoch cannot be acquired and there is no legacy fallback.
	{
		FWorldInputFixture NoGi(EWorldKind::NoGameInstance);
		if (!NoGi.Prepare(*this))
		{
			return false;
		}
		TestTrue(TEXT("precondition: this world has no game instance"), NoGi.Scope.World->GetGameInstance() == nullptr && !NoGi.PublishedEpoch().IsValid());
		ExpectRejected(*this, NoGi, Good, TEXT("a world without a game instance"), NoGi.Scope.World, NoGi.Binding, NoGi.MakeSelections(), ManifestHash(), TEXT("WorldInput.NoContent"), TEXT(""), TEXT("the world has no game instance"));
	}

	// A world whose game instance never ran Init: it has no catalog subsystem, so no epoch (not a fallback to the process Legacy() epoch).
	{
		FWorldInputFixture Cold(EWorldKind::UninitializedGameInstance);
		if (!Cold.Prepare(*this))
		{
			return false;
		}
		TestTrue(TEXT("precondition: this world has a game instance object without a catalog subsystem"), Cold.Scope.World->GetGameInstance() == Cold.Scope.GameInstance.Get() && Cold.Scope.World->GetGameInstance()
			&& !Cold.Scope.World->GetGameInstance()->GetSubsystem<URPGCombatCatalogSubsystem>() && !Cold.PublishedEpoch().IsValid());
		ExpectRejected(*this, Cold, Good, TEXT("a game instance without the catalog subsystem"), Cold.Scope.World, Cold.Binding, Cold.MakeSelections(), ManifestHash(), TEXT("WorldInput.NoContent"), TEXT(""),
			TEXT("the world's game instance has no catalog subsystem"));
	}

	AddInfo(TEXT("Content rejections: the epoch is acquired only through RPGCombatRegistry::ForWorld; a world without a game instance and a game instance without the catalog subsystem both fail with WorldInput.NoContent and no Legacy() fallback. NOT covered here: "
		"a game instance whose subsystem published no epoch (the shipped startup latch cannot be changed without a cvar, which this package does not touch)."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGWorldInputRejectionTest, "OneBossFight.Binding.WorldInput.InputRejections",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGWorldInputRejectionTest::RunTest(const FString& Parameters)
{
	FWorldInputFixture F(EWorldKind::RealGameInstance);
	if (!F.Prepare(*this))
	{
		return false;
	}
	const TArray<FSelection> Valid = F.MakeSelections();
	const FString Hash = ManifestHash();
	// The unmodified positive input first: it is the sentinel source and proves every later failure is caused by its one change.
	FRPGHydrationPreflightInput Good;
	const FRPGHydrationResult GoodResult = RPGBossWorldInputCompiler::CompileWorldInput(F.Scope.World, F.Binding, Valid, Hash, Good);
	if (!TestTrue(FString::Printf(TEXT("the unmodified input compiles first (errors: %s)"), *JoinErrors(GoodResult.Errors)), GoodResult.IsReady() && IsPopulated(Good)))
	{
		return false;
	}
	const FEpochPtr Epoch = F.PublishedEpoch();
	const FWorldState Before = F.Capture();
	const TArray<FRPGPlacedParticipantBinding> ValidParticipants = F.MakeParticipants();

	// A second world (a plain world without a game instance) for the foreign binding and the foreign actor.
	FGameWorld Other(EWorldKind::NoGameInstance);
	if (!TestNotNull(TEXT("a second world exists for the foreign cases"), Other.World))
	{
		return false;
	}
	AActor* ForeignActor = Other.SpawnPlainActor();
	ARPGEncounterBinding* ForeignBinding = Other.SpawnBindingActor();
	if (!TestTrue(TEXT("a foreign actor and a foreign binding were spawned in the second world"), ForeignActor && ForeignBinding))
	{
		return false;
	}
	ForeignBinding->EncounterInstance = FGuid::NewGuid();
	ForeignBinding->Participants = ValidParticipants;

	// 1. The explicit world, binding, GUID, participants and manifest hash.
	ExpectRejected(*this, F, Good, TEXT("no expected world"), nullptr, F.Binding, Valid, Hash, TEXT("WorldInput.InvalidWorld"), TEXT(""), TEXT("no expected world"));
	ExpectRejected(*this, F, Good, TEXT("no binding"), F.Scope.World, nullptr, Valid, Hash, TEXT("WorldInput.InvalidBinding"), TEXT(""), TEXT("no encounter binding"));
	ExpectRejected(*this, F, Good, TEXT("a binding of another world"), F.Scope.World, ForeignBinding, Valid, Hash, TEXT("WorldInput.InvalidBinding"), TEXT(""), TEXT("not in the expected world"));
	{
		ARPGEncounterBinding* Stale = F.SpawnBinding(ValidParticipants, FGuid::NewGuid());
		if (TestNotNull(TEXT("a binding to destroy was spawned"), Stale))
		{
			Stale->Destroy();
			ExpectRejected(*this, F, Good, TEXT("a destroyed binding"), F.Scope.World, Stale, Valid, Hash, TEXT("WorldInput.InvalidBinding"), TEXT(""), TEXT("destroyed or collected"));
		}
	}
	{
		ARPGEncounterBinding* Late = F.SpawnBinding(ValidParticipants, FGuid::NewGuid());
		if (TestNotNull(TEXT("a binding to begin play was spawned"), Late))
		{
			Late->DispatchBeginPlay();
			TestTrue(TEXT("precondition: the late binding has begun play"), Late->HasActorBegunPlay());
			ExpectRejected(*this, F, Good, TEXT("a binding that began play"), F.Scope.World, Late, Valid, Hash, TEXT("WorldInput.InvalidBinding"), TEXT(""), TEXT("began or is beginning play"));
		}
	}
	{
		ARPGEncounterBinding* NoGuid = F.SpawnBinding(ValidParticipants, FGuid());
		if (TestNotNull(TEXT("a binding without a GUID was spawned"), NoGuid))
		{
			ExpectRejected(*this, F, Good, TEXT("a binding without an explicit GUID"), F.Scope.World, NoGuid, Valid, Hash, TEXT("WorldInput.InvalidEncounter"), TEXT(""), TEXT("no explicit valid encounter GUID"));
		}
	}
	{
		ARPGEncounterBinding* Empty = F.SpawnBinding(TArray<FRPGPlacedParticipantBinding>(), FGuid::NewGuid());
		if (TestNotNull(TEXT("a binding without participants was spawned"), Empty))
		{
			ExpectRejected(*this, F, Good, TEXT("a binding without participants"), F.Scope.World, Empty, Valid, Hash, TEXT("WorldInput.NoParticipants"), TEXT(""), TEXT("no participant"));
		}
	}
	ExpectRejected(*this, F, Good, TEXT("an empty manifest hash"), F.Scope.World, F.Binding, Valid, FString(), TEXT("WorldInput.InvalidManifestHash"), TEXT(""), TEXT("64 hexadecimal digits"));
	ExpectRejected(*this, F, Good, TEXT("a manifest hash of 63 digits"), F.Scope.World, F.Binding, Valid, FString::ChrN(63, TEXT('b')), TEXT("WorldInput.InvalidManifestHash"), TEXT(""), TEXT("64 hexadecimal digits"));
	ExpectRejected(*this, F, Good, TEXT("a manifest hash with a non-hex digit"), F.Scope.World, F.Binding, Valid, FString::ChrN(63, TEXT('b')) + TEXT("g"), TEXT("WorldInput.InvalidManifestHash"), TEXT(""), TEXT("64 hexadecimal digits"));

	// 2. The selections: exact one-to-one coverage, explicit roles, role/phase semantics (direct literal expectations).
	{
		TArray<FSelection> Duplicate = Valid;
		Duplicate.Add(Valid[0]);
		ExpectRejected(*this, F, Good, TEXT("a duplicate selection"), F.Scope.World, F.Binding, Duplicate, Hash, TEXT("WorldInput.SelectionDuplicate"), TEXT("[slot=BossOne]"), TEXT("more than one selection"));
		TArray<FSelection> Missing = Valid;
		Missing.RemoveAt(2);
		ExpectRejected(*this, F, Good, TEXT("a missing selection for the last participant"), F.Scope.World, F.Binding, Missing, Hash, TEXT("WorldInput.SelectionMissing"), TEXT("[slot=Player]"), TEXT("no selection"));
		TArray<FSelection> Extra = Valid;
		Extra.Add(FSelection{TEXT("Ghost"), ERPGPreflightRole::TargetOnly, NAME_None});
		ExpectRejected(*this, F, Good, TEXT("an extraneous selection"), F.Scope.World, F.Binding, Extra, Hash, TEXT("WorldInput.SelectionExtraneous"), TEXT("[slot=Ghost]"), TEXT("not a participant"));
		TArray<FSelection> Empty = Valid;
		Empty.Add(FSelection{NAME_None, ERPGPreflightRole::TargetOnly, NAME_None});
		ExpectRejected(*this, F, Good, TEXT("a selection with an empty slot"), F.Scope.World, F.Binding, Empty, Hash, TEXT("WorldInput.SelectionInvalid"), TEXT("[selection=#3]"), TEXT("slot name is empty"));
		TArray<FSelection> NoRole = Valid;
		NoRole[1].Role = ERPGPreflightRole::None;
		ExpectRejected(*this, F, Good, TEXT("a selection without a role"), F.Scope.World, F.Binding, NoRole, Hash, TEXT("WorldInput.SelectionRole"), TEXT("[slot=BossTwo]"), TEXT("never inferred from the slot name"));
		TArray<FSelection> TargetPhase = Valid;
		TargetPhase[2].SelectedPhaseId = TEXT("PhaseTwo");
		ExpectRejected(*this, F, Good, TEXT("a target-only member with a phase"), F.Scope.World, F.Binding, TargetPhase, Hash, TEXT("WorldInput.SelectionPhaseUnexpected"), TEXT("[slot=Player]"), TEXT("no phase to select"));
		TArray<FSelection> BadRole = Valid;
		BadRole[1].Role = static_cast<ERPGPreflightRole>(99);
		ExpectRejected(*this, F, Good, TEXT("a selection with an out-of-range role value"), F.Scope.World, F.Binding, BadRole, Hash, TEXT("WorldInput.SelectionRole"), TEXT("[slot=BossTwo]"), TEXT("role is not set"));
		TArray<FSelection> BossNoPhase = Valid;
		BossNoPhase[1].SelectedPhaseId = NAME_None;
		ExpectRejected(*this, F, Good, TEXT("a boss-core member without a phase"), F.Scope.World, F.Binding, BossNoPhase, Hash, TEXT("WorldInput.SelectionPhaseMissing"), TEXT("[slot=BossTwo]"), TEXT("explicit selected phase id"));
	}

	// 3. The members: actors (the invalid one is the LAST member, after valid ones), explicit targets, explicit definitions.
	// NOTE for maintainers: nothing below may yield a frame or run a garbage collection between a Destroy() and the call that passes the destroyed object (a collection would null the participant's pointer and change the
	// expected error from Stale to Missing).
	{
		TArray<FRPGPlacedParticipantBinding> DuplicateSlot = ValidParticipants;
		DuplicateSlot[2].Slot = TEXT("BossOne");
		ARPGEncounterBinding* CaseDuplicate = F.SpawnBinding(DuplicateSlot, FGuid::NewGuid());
		TArray<FRPGPlacedParticipantBinding> EmptySlot = ValidParticipants;
		EmptySlot[2].Slot = NAME_None;
		ARPGEncounterBinding* CaseEmpty = F.SpawnBinding(EmptySlot, FGuid::NewGuid());
		if (TestTrue(TEXT("the two slot cases were spawned"), CaseDuplicate && CaseEmpty))
		{
			ExpectRejected(*this, F, Good, TEXT("two participants with the same slot"), F.Scope.World, CaseDuplicate, Valid, Hash, TEXT("WorldInput.ParticipantDuplicateSlot"), TEXT("[slot=BossOne]"), TEXT("more than one participant"));
			ExpectRejected(*this, F, Good, TEXT("a participant with an empty slot"), F.Scope.World, CaseEmpty, Valid, Hash, TEXT("WorldInput.ParticipantInvalid"), TEXT("[member=#2]"), TEXT("slot name is empty"));
		}
	}
	{
		TArray<FRPGPlacedParticipantBinding> Mutated = ValidParticipants;
		Mutated[2].Actor = ForeignActor;
		ARPGEncounterBinding* Case = F.SpawnBinding(Mutated, FGuid::NewGuid());
		if (TestNotNull(TEXT("a binding with a foreign actor was spawned"), Case))
		{
			ExpectRejected(*this, F, Good, TEXT("a foreign actor as the last member"), F.Scope.World, Case, Valid, Hash, TEXT("WorldInput.ParticipantForeign"), TEXT("[slot=Player]"), TEXT("not in the expected world"));
		}
	}
	{
		AActor* Doomed = F.Scope.SpawnPlainActor();
		TArray<FRPGPlacedParticipantBinding> Mutated = ValidParticipants;
		Mutated[2].Actor = Doomed;
		ARPGEncounterBinding* Case = F.SpawnBinding(Mutated, FGuid::NewGuid());
		if (TestTrue(TEXT("a binding with an actor to destroy was spawned"), Doomed && Case))
		{
			Doomed->Destroy();
			ExpectRejected(*this, F, Good, TEXT("a destroyed actor as the last member"), F.Scope.World, Case, Valid, Hash, TEXT("WorldInput.ParticipantActorStale"), TEXT("[slot=Player]"), TEXT("destroyed or collected"));
		}
	}
	{
		AActor* Begun = F.Scope.SpawnPlainActor();
		TArray<FRPGPlacedParticipantBinding> Mutated = ValidParticipants;
		Mutated[2].Actor = Begun;
		ARPGEncounterBinding* Case = F.SpawnBinding(Mutated, FGuid::NewGuid());
		if (TestTrue(TEXT("a binding with an actor to begin play was spawned"), Begun && Case))
		{
			Begun->DispatchBeginPlay();
			TestTrue(TEXT("precondition: the late actor has begun play"), Begun->HasActorBegunPlay());
			ExpectRejected(*this, F, Good, TEXT("a late (begun) actor as the last member"), F.Scope.World, Case, Valid, Hash, TEXT("WorldInput.ParticipantActorBegun"), TEXT("[slot=Player]"), TEXT("began or is beginning play"));
		}
	}
	{
		TArray<FRPGPlacedParticipantBinding> Mutated = ValidParticipants;
		Mutated[2].Actor = F.BossOneActor;
		ARPGEncounterBinding* Case = F.SpawnBinding(Mutated, FGuid::NewGuid());
		if (TestNotNull(TEXT("a binding with a duplicate actor was spawned"), Case))
		{
			ExpectRejected(*this, F, Good, TEXT("the same actor in two members"), F.Scope.World, Case, Valid, Hash, TEXT("WorldInput.ParticipantDuplicateActor"), TEXT("[slot=Player]"), TEXT("more than one participant"));
		}
	}
	{
		TArray<FRPGPlacedParticipantBinding> NoTarget = ValidParticipants;
		NoTarget[2].TargetSlot = NAME_None;
		ARPGEncounterBinding* CaseNone = F.SpawnBinding(NoTarget, FGuid::NewGuid());
		TArray<FRPGPlacedParticipantBinding> SelfTarget = ValidParticipants;
		SelfTarget[2].TargetSlot = TEXT("Player");
		ARPGEncounterBinding* CaseSelf = F.SpawnBinding(SelfTarget, FGuid::NewGuid());
		TArray<FRPGPlacedParticipantBinding> UnknownTarget = ValidParticipants;
		UnknownTarget[2].TargetSlot = TEXT("Nowhere");
		ARPGEncounterBinding* CaseUnknown = F.SpawnBinding(UnknownTarget, FGuid::NewGuid());
		if (TestTrue(TEXT("the three target cases were spawned"), CaseNone && CaseSelf && CaseUnknown))
		{
			ExpectRejected(*this, F, Good, TEXT("a member without an explicit target"), F.Scope.World, CaseNone, Valid, Hash, TEXT("WorldInput.ParticipantTargetMissing"), TEXT("[slot=Player]"), TEXT("no explicit target slot"));
			ExpectRejected(*this, F, Good, TEXT("a member targeting itself"), F.Scope.World, CaseSelf, Valid, Hash, TEXT("WorldInput.ParticipantTargetSelf"), TEXT("[slot=Player]"), TEXT("member's own slot"));
			ExpectRejected(*this, F, Good, TEXT("a member targeting a slot outside the batch"), F.Scope.World, CaseUnknown, Valid, Hash, TEXT("WorldInput.ParticipantTargetNotInBatch"), TEXT("[slot=Player]"), TEXT("'Nowhere'"));
		}
	}
	{
		TArray<FRPGPlacedParticipantBinding> NullDefinition = ValidParticipants;
		NullDefinition[2].Definition = nullptr;
		ARPGEncounterBinding* CaseNull = F.SpawnBinding(NullDefinition, FGuid::NewGuid());
		TStrongObjectPtr<URPGBossDefinition> WrongSchema(NewObject<URPGBossDefinition>());
		TStrongObjectPtr<URPGBossDefinition> NoId(NewObject<URPGBossDefinition>());
		if (!TestTrue(TEXT("the definition cases were created"), CaseNull && WrongSchema.IsValid() && NoId.IsValid()))
		{
			return false;
		}
		FillDefinition(*WrongSchema, PlayerValues(), F.PlayerSkeleton, PlayerAnimationPaths());
		WrongSchema->Schema = 2;
		FillDefinition(*NoId, PlayerValues(), F.PlayerSkeleton, PlayerAnimationPaths());
		NoId->DefinitionId = NAME_None;
		TArray<FRPGPlacedParticipantBinding> WrongSchemaParticipants = ValidParticipants;
		WrongSchemaParticipants[2].Definition = WrongSchema.Get();
		ARPGEncounterBinding* CaseSchema = F.SpawnBinding(WrongSchemaParticipants, FGuid::NewGuid());
		TArray<FRPGPlacedParticipantBinding> NoIdParticipants = ValidParticipants;
		NoIdParticipants[2].Definition = NoId.Get();
		ARPGEncounterBinding* CaseNoId = F.SpawnBinding(NoIdParticipants, FGuid::NewGuid());
		if (TestTrue(TEXT("the definition bindings were spawned"), CaseSchema && CaseNoId))
		{
			ExpectRejected(*this, F, Good, TEXT("a target-only member without its own definition"), F.Scope.World, CaseNull, Valid, Hash, TEXT("WorldInput.DefinitionMissing"), TEXT("[slot=Player]"), TEXT("needs its own"));
			ExpectRejected(*this, F, Good, TEXT("a definition of schema 2"), F.Scope.World, CaseSchema, Valid, Hash, TEXT("WorldInput.DefinitionInvalid"), TEXT("[slot=Player]"), TEXT("schema is not 1"));
			ExpectRejected(*this, F, Good, TEXT("a definition without an id"), F.Scope.World, CaseNoId, Valid, Hash, TEXT("WorldInput.DefinitionInvalid"), TEXT("[slot=Player]"), TEXT("definition id or presentation id is empty"));
		}
	}

	// 4. The PRODUCTION DEFINITION layer: the production compiler refuses the later member's definition (a transient negative-control skeleton that is not the animations' skeleton; nothing is retargeted). The nested
	//    diagnostic is carried unchanged under WorldInput.DefinitionRejected.
	{
		TStrongObjectPtr<USkeleton> OtherSkeleton(NewObject<USkeleton>(GetTransientPackage()));
		TStrongObjectPtr<URPGBossDefinition> Bad(NewObject<URPGBossDefinition>());
		if (!TestTrue(TEXT("the transient negative control skeleton and definition were created"), OtherSkeleton.IsValid() && Bad.IsValid()))
		{
			return false;
		}
		FillDefinition(*Bad, BossTwoValues(), OtherSkeleton.Get(), BossAnimationPaths());
		TArray<FRPGPlacedParticipantBinding> Mutated = ValidParticipants;
		Mutated[1].Definition = Bad.Get();
		ARPGEncounterBinding* Case = F.SpawnBinding(Mutated, FGuid::NewGuid());
		if (TestNotNull(TEXT("a binding with a definition the production compiler refuses was spawned"), Case))
		{
			ExpectRejected(*this, F, Good, TEXT("a later definition refused by the production compiler"), F.Scope.World, Case, Valid, Hash, TEXT("WorldInput.DefinitionRejected"), TEXT("[slot=BossTwo]"), TEXT("animation/skeleton identity mismatch"));
		}
	}

	// 4b. The production compiler refuses a definition whose manifest rows are incomplete (an invalid manifest INSIDE the definition, not the hash): the nested diagnostic is carried unchanged.
	{
		TStrongObjectPtr<URPGBossDefinition> BadManifest(NewObject<URPGBossDefinition>());
		if (!TestTrue(TEXT("the definition with an incomplete manifest row was created"), BadManifest.IsValid()))
		{
			return false;
		}
		FillDefinition(*BadManifest, BossTwoValues(), F.BossSkeleton, BossAnimationPaths());
		BadManifest->Fields[0].SourcePath.Empty();
		TArray<FRPGPlacedParticipantBinding> Mutated = ValidParticipants;
		Mutated[1].Definition = BadManifest.Get();
		ARPGEncounterBinding* Case = F.SpawnBinding(Mutated, FGuid::NewGuid());
		if (TestNotNull(TEXT("a binding with the incomplete manifest definition was spawned"), Case))
		{
			ExpectRejected(*this, F, Good, TEXT("a later definition with an incomplete manifest row"), F.Scope.World, Case, Valid, Hash, TEXT("WorldInput.DefinitionRejected"), TEXT("[slot=BossTwo]"), TEXT("incomplete/duplicate field-source manifest"));
		}
	}

	// 5. The PREFLIGHT layer (whole batch, nested diagnostics unchanged): a selected phase the definition does not hold, and a boss-core member whose actor holds no mesh (the later member of the batch).
	{
		TArray<FSelection> MissingPhase = Valid;
		MissingPhase[1].SelectedPhaseId = TEXT("PhaseMissing");
		ExpectRejected(*this, F, Good, TEXT("a selected phase the later definition lacks"), F.Scope.World, F.Binding, MissingPhase, Hash, TEXT("WorldInput.PreflightRejected"), TEXT("Preflight.PhaseRejected[slot=BossTwo]"), TEXT("InvalidPhase.NotFound"));
		ACharacter* Bare = F.Scope.SpawnCharacter(nullptr, FVector(2000.f, 0.f, 0.f));
		if (TestNotNull(TEXT("a native character without a mesh was spawned"), Bare))
		{
			TArray<FRPGPlacedParticipantBinding> Mutated = ValidParticipants;
			Mutated[1].Actor = Bare;
			ARPGEncounterBinding* Case = F.SpawnBinding(Mutated, FGuid::NewGuid());
			if (TestNotNull(TEXT("a binding with the mesh-less character was spawned"), Case))
			{
				ExpectRejected(*this, F, Good, TEXT("a later member whose actor holds no mesh"), F.Scope.World, Case, Valid, Hash, TEXT("WorldInput.PreflightRejected"), TEXT("Preflight.ProductionPrerequisite[slot=BossTwo]"),
					TEXT("mesh is compatible with the compiled skeleton"));
			}
		}
	}

	// 6. Off the game thread: refused before any UObject is touched; this is the one case where the output is NOT touched either (clearing it would release leases off the game thread).
	{
		FRPGHydrationPreflightInput Output = MakeSentinel(Good, F.Scope.World);
		const FGuid SentinelGuid = Output.EncounterInstance;
		UWorld* PoolWorld = F.Scope.World;
		const ARPGEncounterBinding* PoolBinding = F.Binding;
		TFuture<FRPGHydrationResult> Future = Async(EAsyncExecution::ThreadPool, [PoolWorld, PoolBinding, &Valid, &Hash, &Output]() { return RPGBossWorldInputCompiler::CompileWorldInput(PoolWorld, PoolBinding, Valid, Hash, Output); });
		const FRPGHydrationResult PoolResult = Future.Get();
		TestTrue(FString::Printf(TEXT("off the game thread: refused with WorldInput.NotGameThread (got: %s)"), *JoinErrors(PoolResult.Errors)), !PoolResult.IsReady() && AnyErrorHasAll(PoolResult.Errors, TEXT("WorldInput.NotGameThread"), TEXT(""), TEXT("the output was not touched")));
		TestTrue(TEXT("off the game thread: the output was NOT touched (still the populated sentinel)"), IsPopulated(Output) && Output.EncounterInstance == SentinelGuid);
	}

	TestTrue(TEXT("none of the cases changed an actor, a component, a mesh, a begun flag or the combat context"), SameWorld(Before, F.Capture()));
	TestTrue(TEXT("none of the cases allocated an object under a planned name"), F.NothingAllocated());

	// The positive control after the negative cases: the unmodified input still compiles, to a fresh output with the same epoch lease.
	{
		FRPGHydrationPreflightInput Control = MakeSentinel(Good, F.Scope.World);
		const FRPGHydrationResult ControlResult = RPGBossWorldInputCompiler::CompileWorldInput(F.Scope.World, F.Binding, Valid, Hash, Control);
		if (!TestTrue(FString::Printf(TEXT("control: the unmodified input compiles after the negative cases (errors: %s)"), *JoinErrors(ControlResult.Errors)), ControlResult.IsReady()))
		{
			return false;
		}
		ExpectOutput(*this, F, Control, Epoch, TEXT("control"));
	}

	AddInfo(TEXT("Input rejections on the real game-instance world: every named failure clears a populated output, allocates and binds nothing and names its layer: the input (WorldInput.*), the production compiler (WorldInput.DefinitionRejected with the nested diagnostic) or the preflight "
		"(WorldInput.PreflightRejected with each nested diagnostic). NOT covered: epoch or binding drift DURING a call (not provokable without a callback, cvar or injection framework), a destroyed GAME INSTANCE mid-call, a content epoch whose subsystem published nothing, ConfigInvalid (the production compiler cannot return a synthetic config or a foreign lease for a definition it accepted, and no mock is allowed), a definition whose skeleton does not fit its actor's mesh "
		"(the two pack classes observed share one skeleton; only the mesh-less actor case is exercised)."));
	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
