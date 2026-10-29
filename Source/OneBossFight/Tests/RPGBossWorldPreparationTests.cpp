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
#include "Player/RPGBossHydrationPreparation.h"
#include "Player/RPGBossPhases.h"
#include "Player/RPGBossPosture.h"
#include "Player/RPGBossStagger.h"
#include "Player/RPGBossWorldInputCompiler.h"
#include "Player/RPGBossWorldPreparation.h"
#include "Player/RPGCombatCatalog.h"
#include "Player/RPGEncounterBinding.h"
#include "UObject/Package.h"
#include "UObject/StrongObjectPtr.h"
#include "UObject/UObjectHash.h"

// DD18 part C (world preparation): RPGBossWorldPreparation::PrepareWorldBatch driven in a REAL game-instance world (the engine's own standalone lifecycle: NewObject<UGameInstance>(GEngine), InitializeStandalone, which creates the
// world context and a world and initializes every game-instance subsystem, the project's catalog subsystem included, with its actual default latch; cleanup Shutdown, DestroyWorldContext, DestroyWorld), real pack assets (the two
// pack classes are loaded only to READ the mesh their default object holds), three isolated native ACharacter actors finished before any call (two boss-core, one target), transient production-compatible definitions, one real
// ARPGEncounterBinding. No Legacy() epoch is injected, no cvar or asset is changed, nothing is mocked. The setup is copied from DD14, DD16 and DD17 into this file (no helper promoted, no earlier file edited).
// What it can establish, for these exact assets in this editor binary: the facade composes the accepted stages (the epoch is the very lease the game instance published), twenty-four owned unregistered components with each owner's own
// values, abort and scope-exit abort restore the prior component sets, the context and the mesh, an invalid later member allocates nothing, a REAL name collision under a later owner is refused by the allocation guard and
// cleans the earlier allocations, only the fixture-owned blocker is removed before the retry, and a second independent preparation of the same actors is refused without damaging the first.
// What it does NOT establish: epoch, game-instance or binding drift DURING a stage (not provokable without a callback, cvar or injection framework: source-checked only), re-entry, an organic native configure failure,
// garbage-collected name reuse (the retries reuse destroyed uncollected objects and are only observed), which source the game instance latched (logged only), a cold load, the real boss definition or authoritative manifest
// provenance (fixture values and hand rows), registration, BeginPlay, binding, reservation (that is the registry's), Ready, activation or any wiring.

namespace
{
namespace WorldPreparationTests
{
	using FSelection = RPGBossWorldInputCompiler::FSelection;
	using FEpochPtr = TSharedPtr<const RPGCombatRegistry::FEpoch>;

	const TCHAR* const PlayerClassPath = TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter.BP_CombatPlayerCharacter_C");
	const TCHAR* const BossClassPath = TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss.BP_ExampleGreatSwordBoss_C");

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

	FMemberValues BossOneValues() { return FMemberValues{TEXT("WorldPrepBossOne"), TEXT("WorldPrepBossOneLook"), TEXT("PhaseTwo"), 0.35f, 3500.f, 73.5f, 3.25f}; }
	FMemberValues BossTwoValues() { return FMemberValues{TEXT("WorldPrepBossTwo"), TEXT("WorldPrepBossTwoLook"), TEXT("PhaseAlt"), 0.5f, 4100.f, 88.f, 4.5f}; }
	FMemberValues TargetValues() { return FMemberValues{TEXT("WorldPrepTarget"), TEXT("WorldPrepTargetLook"), TEXT("PhaseTwo"), 0.35f, 3500.f, 73.5f, 3.25f}; }

	FString ManifestHash() { return FString::ChrN(64, TEXT('b')); } // a fixture hash, not a real manifest hash

	/** A real game-instance world started the engine's way, with game-thread cleanup. */
	struct FGameWorld
	{
		UWorld* World = nullptr;
		TStrongObjectPtr<UGameInstance> GameInstance;

		FGameWorld()
		{
			if (!GEngine)
			{
				return;
			}
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
		}

		~FGameWorld()
		{
			if (GameInstance.IsValid())
			{
				GameInstance->Shutdown();
			}
			if (World)
			{
				GEngine->DestroyWorldContext(World);
				World->DestroyWorld(/*bInformEngineOfWorld=*/false);
			}
		}

		FGameWorld(const FGameWorld&) = delete;
		FGameWorld& operator=(const FGameWorld&) = delete;

		/** A native ACharacter (never a Blueprint actor); the mesh is set BEFORE the actor is finished, so it never begins play. */
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
			// Independent world-preparation membership expectations.
			TEXT("Bleed.InitialThreshold"), TEXT("Bleed.ThresholdIncrease"), TEXT("Bleed.ThresholdMax"), TEXT("Bleed.HpFraction"), TEXT("Bleed.EffectHeight"), TEXT("Bleed.ProcEffect"), TEXT("Bleed.ProcSound"),
			TEXT("LowSweep.bEnabled"), TEXT("LowSweep.MoveId"), TEXT("LowSweep.Damage"), TEXT("LowSweep.Reach"), TEXT("LowSweep.InnerRadius"), TEXT("LowSweep.BladeHeight"), TEXT("LowSweep.SweepFromDegrees"), TEXT("LowSweep.SweepToDegrees"),
			TEXT("Shockwave.bEnabled"), TEXT("Shockwave.MoveId"), TEXT("Shockwave.Damage"), TEXT("Shockwave.StartRadius"), TEXT("Shockwave.MaxRadius"), TEXT("Shockwave.Speed"), TEXT("Shockwave.Thickness"), TEXT("Shockwave.JumpClearance"),
			TEXT("HealPunish.bEnabled"), TEXT("HealPunish.MinRange"), TEXT("HealPunish.MaxRange"), TEXT("HealPunish.Cooldown"), TEXT("HealPunish.Damage"), TEXT("HealPunish.FlightTime"), TEXT("HealPunish.MinSpeed"), TEXT("HealPunish.MaxSpeed"), TEXT("HealPunish.JavelinRadius"), TEXT("HealPunish.JavelinMaxRange"), TEXT("HealPunish.SpawnSockets"), TEXT("HealPunish.AimHeight"), TEXT("HealPunish.bRespondToHeal"), TEXT("HealPunish.bCancelJavelinsOnInterrupt"),
			TEXT("Look.bEnabled"), TEXT("Look.Body"), TEXT("Look.Pieces"), TEXT("Look.Sword"), TEXT("Look.SwordSocket"),
			TEXT("CloseClipSwap.CloseAbilityClassName"), TEXT("CloseClipSwap.AttackMontagesName"), TEXT("CloseClipSwap.A1Montage"), TEXT("CloseClipSwap.A3aMontage"), TEXT("CloseClipSwap.A3bMontage"),
			TEXT("Death.DeathMode"), TEXT("Death.DeathClip"), TEXT("Death.DeathMontage"), TEXT("Death.PackDeathAbilityClassName"), TEXT("Death.PackDeathMontagesName"), TEXT("Death.PackPollSeconds"), TEXT("Death.PackEndTimeMultiplier"), TEXT("Death.HoldAtSeconds"), TEXT("Death.DyingSeconds"), TEXT("Death.BlendInSeconds"), TEXT("Death.MaxClipRestarts"), TEXT("Death.bGuardPackDeath")};
	}

	FRPGParityField MakeProductionField(const FString& Path)
	{
		FRPGParityField Field;
		Field.FieldPath = Path;
		Field.Type = TEXT("fixture");
		Field.Value = TEXT("production fixture row: membership only, not derived from an asset");
		Field.SourcePath = TEXT("DD18 world preparation fixture, not live provenance");
		Field.SourceSHA256 = FString::ChrN(64, TEXT('c'));
		Field.SourceSite = TEXT("fixture");
		Field.Origin = TEXT("harness");
		Field.Precedence = TEXT("fixture");
		Field.Destination = TEXT("fixture");
		Field.FirstRead = TEXT("not read");
		Field.Witness = TEXT("none: structural membership only");
		return Field;
	}

	TArray<FSoftObjectPath> BossAnimationPaths()
	{
		FRPGDormantWakeConfig Wake;
		FRPGPhaseDependencyConfig Dependencies;
		FRPGStaggerProfileConfig Profile;
		return TArray<FSoftObjectPath>{Wake.DormantClip.ToSoftObjectPath(), Wake.WakeClip.ToSoftObjectPath(), Dependencies.RoarClip.ToSoftObjectPath(), Dependencies.TransitionMontage.ToSoftObjectPath(),
			Profile.FallMontage.ToSoftObjectPath(), Profile.GetUpMontage.ToSoftObjectPath(), Profile.FallClip.ToSoftObjectPath(), Profile.DownClip.ToSoftObjectPath(), Profile.RiposteBossClip.ToSoftObjectPath()};
	}

	TArray<FSoftObjectPath> TargetAnimationPaths()
	{
		FRPGStaggerProfileConfig Profile;
		return TArray<FSoftObjectPath>{Profile.RipostePlayerClip.ToSoftObjectPath()};
	}

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

	FString JoinErrors(const TArray<FString>& Errors) { return FString::Join(Errors, TEXT(" | ")); }

	bool AnyErrorHasAll(const TArray<FString>& Errors, const TCHAR* Token, const TCHAR* WhereText, const TCHAR* FurtherText)
	{
		return Errors.ContainsByPredicate([Token, WhereText, FurtherText](const FString& E) { return E.Contains(Token) && E.Contains(WhereText) && E.Contains(FurtherText); });
	}

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

	struct FActorState
	{
		TArray<const UActorComponent*> Components;
		TArray<int32> Flags;
		bool bBegun = false;
		const USkeletalMesh* MeshAsset = nullptr;
	};

	struct FWorldState
	{
		TArray<FActorState> Actors; // BossOne, BossTwo, Target
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

	bool SameActorState(const FActorState& X, const FActorState& Y)
	{
		return X.bBegun == Y.bBegun && X.MeshAsset == Y.MeshAsset && X.Components == Y.Components && X.Flags == Y.Flags;
	}

	bool SameWorld(const FWorldState& A, const FWorldState& B)
	{
		if (A.Actors.Num() != B.Actors.Num() || A.Bound != B.Bound || A.Ready != B.Ready)
		{
			return false;
		}
		for (int32 Index = 0; Index < A.Actors.Num(); ++Index)
		{
			if (!SameActorState(A.Actors[Index], B.Actors[Index]))
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

	/** The twelve accepted native consumers with the reviewed instance names, written out independently, in plan order. */
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

	/** The real pack mesh and skeleton, three isolated native actors, a marker on each, three transient definitions and the real binding. */
	struct FFixture
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
		ACharacter* TargetActor = nullptr;
		USceneComponent* Markers[3] = {nullptr, nullptr, nullptr};
		TStrongObjectPtr<URPGBossDefinition> BossOneDefinition;
		TStrongObjectPtr<URPGBossDefinition> BossTwoDefinition;
		TStrongObjectPtr<URPGBossDefinition> TargetDefinition;
		ARPGEncounterBinding* Binding = nullptr;
		FGuid Encounter;

		bool Prepare(FAutomationTestBase& Test)
		{
			if (!Scope.World)
			{
				Test.AddError(TEXT("unsupported precondition: the game-instance world could not be created"));
				return false;
			}
			// The startup cvars the game instance latched are only READ and logged; a non-default startup fixture is not the default latch this file is about.
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
			TargetActor = Scope.SpawnCharacter(PlayerMesh, FVector(1000.f, 0.f, 0.f));
			if (!BossOneActor || !BossTwoActor || !TargetActor)
			{
				Test.AddError(TEXT("unsupported precondition: the three isolated native character actors could not be spawned"));
				return false;
			}
			ACharacter* const Actors[3] = {BossOneActor, BossTwoActor, TargetActor};
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
			TargetDefinition.Reset(NewObject<URPGBossDefinition>());
			if (!BossOneDefinition.IsValid() || !BossTwoDefinition.IsValid() || !TargetDefinition.IsValid())
			{
				Test.AddError(TEXT("unsupported precondition: the transient definitions could not be created"));
				return false;
			}
			FillDefinition(*BossOneDefinition, BossOneValues(), BossSkeleton, BossAnimationPaths());
			FillDefinition(*BossTwoDefinition, BossTwoValues(), BossSkeleton, BossAnimationPaths());
			FillDefinition(*TargetDefinition, TargetValues(), PlayerSkeleton, TargetAnimationPaths());
			Encounter = FGuid::NewGuid();
			Binding = SpawnBinding(MakeParticipants(), Encounter);
			if (!Binding)
			{
				Test.AddError(TEXT("unsupported precondition: the encounter binding actor could not be spawned"));
				return false;
			}
			return true;
		}

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
			Target.Actor = TargetActor;
			Target.Definition = TargetDefinition.Get();
			Participants.Add(Target);
			return Participants;
		}

		ARPGEncounterBinding* SpawnBinding(const TArray<FRPGPlacedParticipantBinding>& Participants, const FGuid& Guid) const
		{
			ARPGEncounterBinding* Created = Scope.World ? Scope.World->SpawnActor<ARPGEncounterBinding>() : nullptr;
			if (Created)
			{
				Created->EncounterInstance = Guid;
				Created->Participants = Participants;
			}
			return Created;
		}

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
			for (const AActor* Actor : {static_cast<const AActor*>(BossOneActor), static_cast<const AActor*>(BossTwoActor), static_cast<const AActor*>(TargetActor)})
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

		FEpochPtr PublishedEpoch() const
		{
			const UGameInstance* GameInstance = Scope.World ? Scope.World->GetGameInstance() : nullptr;
			const URPGCombatCatalogSubsystem* Subsystem = GameInstance ? GameInstance->GetSubsystem<URPGCombatCatalogSubsystem>() : nullptr;
			return Subsystem ? Subsystem->GetEpoch() : FEpochPtr();
		}

		/** No object, not even a destroyed one, carries a planned managed-consumer name under any of the three actors. */
		bool NothingAllocated() const
		{
			for (const AActor* Actor : {static_cast<const AActor*>(BossOneActor), static_cast<const AActor*>(BossTwoActor), static_cast<const AActor*>(TargetActor)})
			{
				for (const FExpectedComponent& Wanted : ExpectedComponents())
				{
					if (StaticFindObjectFast(UObject::StaticClass(), const_cast<AActor*>(Actor), FName(Wanted.Name)) != nullptr)
					{
						return false;
					}
				}
			}
			return true;
		}

		bool NoConsumers() const { return NoManagedConsumer(BossOneActor) && NoManagedConsumer(BossTwoActor) && NoManagedConsumer(TargetActor); }
	};

	TArray<TWeakObjectPtr<UActorComponent>> WeakOwned(const FRPGPreparedBatch& Batch)
	{
		TArray<TWeakObjectPtr<UActorComponent>> Weak;
		for (const UActorComponent* Component : Batch.OwnedComponentsForTest())
		{
			Weak.Add(const_cast<UActorComponent*>(Component));
		}
		return Weak;
	}

	/** Every owned component is destroyed: no longer valid; any destroyed object awaiting collection is unregistered, not begun and marked destroyed. */
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

	bool ExpectRestored(FAutomationTestBase& Test, const FFixture& F, const FWorldState& Before, const TCHAR* Label)
	{
		bool bOk = Test.TestTrue(FString::Printf(TEXT("%s: every actor's component set, registered and begun flags, mesh asset and the combat context are exactly as before"), Label), SameWorld(Before, F.Capture()));
		bOk &= Test.TestTrue(FString::Printf(TEXT("%s: no managed consumer remains and the unrelated markers are the same live unregistered objects"), Label),
			F.NoConsumers() && IsValid(F.Markers[0]) && IsValid(F.Markers[1]) && IsValid(F.Markers[2]) && !F.Markers[0]->IsRegistered() && !F.Markers[1]->IsRegistered() && !F.Markers[2]->IsRegistered());
		return bOk;
	}

	/** The exact success shape of a world preparation: twenty-four owned components, the very GI epoch, per-owner values, unregistered/uninitialized/not begun/unticked, the target and the context untouched, summaries. */
	bool ExpectPrepared(FAutomationTestBase& Test, const FFixture& F, const FRPGPreparedBatch& Batch, const FWorldState& Before, const FEpochPtr& Epoch)
	{
		bool bOk = Test.TestTrue(TEXT("the artifact reports prepared and leases twenty-four components"), Batch.IsPrepared() && Batch.GetOwnedComponentCount() == 24);
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
		for (const FBossCase& Case : Bosses)
		{
			const FString Label = Case.Actor->GetName();
			for (const FExpectedComponent& Wanted : ExpectedComponents())
			{
				UActorComponent* Component = Case.Actor->FindComponentByClass(Wanted.Class);
				if (!Test.TestNotNull(FString::Printf(TEXT("%s has a %s"), *Label, *Wanted.Class->GetName()), Component))
				{
					bOk = false;
					continue;
				}
				bOk &= Test.TestTrue(FString::Printf(TEXT("%s: %s has the exact class, the reviewed name and the actor as owner and outer, is leased by the artifact, is unregistered, uninitialized, not begun and unticked"), *Label, Wanted.Name),
					Component->GetClass() == Wanted.Class && Component->GetFName() == FName(Wanted.Name) && Component->GetOwner() == Case.Actor && Component->GetOuter() == Case.Actor && OwnedSet.Contains(Component)
					&& !Component->IsRegistered() && !Component->HasBegunPlay() && !Component->HasBeenInitialized() && !Component->PrimaryComponentTick.IsTickFunctionRegistered());
			}
			const FActorState Now = CaptureActor(Case.Actor);
			const FActorState& Prior = Before.Actors[Case.Index];
			bool bPriorKept = Now.Components.Num() == Prior.Components.Num() + 12 && !Now.bBegun && Now.MeshAsset == Prior.MeshAsset;
			for (const UActorComponent* PriorComponent : Prior.Components)
			{
				bPriorKept = bPriorKept && Now.Components.Contains(PriorComponent) && !OwnedSet.Contains(PriorComponent);
			}
			bOk &= Test.TestTrue(FString::Printf(TEXT("%s: exactly twelve components were added, every unrelated component is still there, the mesh asset is unchanged and no participant component exists"), *Label), bPriorKept && !Case.Actor->FindComponentByClass<URPGCombatParticipant>());
			const URPGBossStagger* Stagger = Case.Actor->FindComponentByClass<URPGBossStagger>();
			const URPGBossPhases* Phases = Case.Actor->FindComponentByClass<URPGBossPhases>();
			const URPGBossEncounter* Encounter = Case.Actor->FindComponentByClass<URPGBossEncounter>();
			const URPGBossPosture* Posture = Case.Actor->FindComponentByClass<URPGBossPosture>();
			bOk &= Test.TestTrue(FString::Printf(TEXT("%s: stagger seconds, the selected phase threshold, boss health and posture maximum are this owner's own values"), *Label),
				Stagger && Phases && Encounter && Posture && Stagger->StaggerSeconds == Case.StaggerSeconds && Phases->PhaseTwoHealthFraction == Case.PhaseThreshold && Encounter->BossMaxHealth == Case.Health && Posture->PostureMax == Case.Posture);
		}
		bOk &= Test.TestTrue(TEXT("the target actor is exactly as before and holds no consumer"), SameActorState(CaptureActor(F.TargetActor), Before.Actors[2]) && NoManagedConsumer(F.TargetActor));
		const FWorldState Now = F.Capture();
		bOk &= Test.TestTrue(TEXT("the combat context has no bound or ready participant change"), Now.Bound == Before.Bound && Now.Ready == Before.Ready);
		const TSharedPtr<const FRPGHydrationPreflightPlan> Plan = Batch.GetPreflightPlan();
		if (Test.TestTrue(TEXT("the retained plan has three participants"), Plan.IsValid() && Plan->Participants.Num() == 3))
		{
			bOk &= Test.TestTrue(TEXT("the plan retains the world, the binding's encounter GUID and the VERY epoch lease the game instance published"), Plan->World.Get() == F.Scope.World && Plan->EncounterInstance == F.Encounter
				&& Epoch.IsValid() && Plan->Content.Get() == Epoch.Get() && Batch.GetEncounterInstance() == F.Encounter);
			bOk &= Test.TestTrue(TEXT("every config is a production config holding that very epoch lease, with the definition's id and the explicit manifest hash"),
				Plan->Participants[0].Config.IsValid() && Plan->Participants[1].Config.IsValid() && Plan->Participants[2].Config.IsValid()
				&& !Plan->Participants[0].Config->bSyntheticFixture && !Plan->Participants[1].Config->bSyntheticFixture && !Plan->Participants[2].Config->bSyntheticFixture
				&& Plan->Participants[0].Config->Content.Get() == Epoch.Get() && Plan->Participants[1].Config->Content.Get() == Epoch.Get() && Plan->Participants[2].Config->Content.Get() == Epoch.Get()
				&& Plan->Participants[0].Config->BossId == FName(One.Id) && Plan->Participants[1].Config->BossId == FName(Two.Id) && Plan->Participants[2].Config->BossId == FName(TargetValues().Id)
				&& Plan->Participants[0].Config->StableManifestHash == ManifestHash());
			bOk &= Test.TestTrue(TEXT("the plan is an incomplete subset: not a complete playable bundle, not a reservation, not ready"), !Plan->IsCompletePlayableBundle() && !Plan->IsReservation() && !Plan->IsReady());
		}
		const TArray<FRPGPreparedParticipantInfo> Infos = Batch.GetParticipants();
		bOk &= Test.TestTrue(TEXT("summaries: three participants, twenty-four components, the explicit phase ids"), Infos.Num() == 3 && Infos[0].OwnedComponentCount == 12 && Infos[1].OwnedComponentCount == 12 && Infos[2].OwnedComponentCount == 0
			&& Infos[0].SelectedPhaseId == FName(One.Phase) && Infos[1].SelectedPhaseId == FName(Two.Phase) && Infos[2].SelectedPhaseId.IsNone());
		return bOk;
	}
}
}

using namespace WorldPreparationTests;

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGWorldPreparationPositiveTest, "OneBossFight.Binding.WorldPreparation.PositiveAndAbort",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGWorldPreparationPositiveTest::RunTest(const FString& Parameters)
{
	FFixture F;
	if (!F.Prepare(*this))
	{
		return false;
	}
	const FEpochPtr Epoch = F.PublishedEpoch();
	if (!TestTrue(TEXT("precondition: the world's game instance published a valid epoch"), Epoch.IsValid() && Epoch->Id.IsValid() && RPGCombatRegistry::ForWorld(F.Scope.World).Get() == Epoch.Get()))
	{
		return false;
	}
	AddInfo(FString::Printf(TEXT("the game instance published epoch %s source '%s' (reason '%s'); the source is logged, never required"), *Epoch->Id.ToString(), *Epoch->Source, *Epoch->Reason));
	const TArray<FSelection> Selections = F.MakeSelections();

	// A first preparation, aborted at once: it performs the legitimate loads (skeletons, animations) so that the dirty comparison below starts after them.
	{
		FRPGWorldPreparationResult Loading = RPGBossWorldPreparation::PrepareWorldBatch(F.Scope.World, F.Binding, Selections, ManifestHash());
		if (!TestTrue(FString::Printf(TEXT("the first world preparation succeeds (errors: %s)"), *JoinErrors(Loading.Errors)), Loading.Succeeded()))
		{
			return false;
		}
		const FRPGPreparationAbortReport Report = Loading.Batch->Abort();
		TestTrue(TEXT("and its abort is clean, twenty-four destroyed"), Report.IsClean() && Report.Destroyed == 24 && Report.ContractViolations == 0);
	}
	TArray<const UObject*> Touched{F.PlayerClass, F.BossClass, F.PlayerMesh, F.BossMesh, F.PlayerSkeleton, F.BossSkeleton};
	const FWorldState Before = F.Capture();
	const TArray<int32> DirtyBefore = CaptureDirty(Touched);

	// Generation one: prepared, checked in full, aborted explicitly.
	{
		FRPGWorldPreparationResult First = RPGBossWorldPreparation::PrepareWorldBatch(F.Scope.World, F.Binding, Selections, ManifestHash());
		if (!TestTrue(FString::Printf(TEXT("the world batch prepares on the real game-instance world (errors: %s)"), *JoinErrors(First.Errors)), First.Succeeded()))
		{
			return false;
		}
		ExpectPrepared(*this, F, *First.Batch, Before, Epoch);
		TArray<TWeakObjectPtr<UActorComponent>> FirstWeak = WeakOwned(*First.Batch);
		const FRPGPreparationAbortReport Report = First.Batch->Abort();
		TestTrue(FString::Printf(TEXT("explicit abort: clean report and twenty-four destroyed (errors: %s)"), *JoinErrors(Report.Errors)), Report.IsClean() && Report.Destroyed == 24 && Report.AlreadyGone == 0 && Report.ContractViolations == 0 && !Report.bRefused);
		ExpectAllDestroyed(*this, FirstWeak, TEXT("explicit abort")); // read BEFORE the names are created again (the engine replaces a destroyed object of the same name in place)
		FirstWeak.Reset();
		ExpectRestored(*this, F, Before, TEXT("explicit abort"));
	}
	// Generation two: released by leaving the scope.
	TArray<TWeakObjectPtr<UActorComponent>> SecondWeak;
	{
		FRPGWorldPreparationResult Second = RPGBossWorldPreparation::PrepareWorldBatch(F.Scope.World, F.Binding, Selections, ManifestHash());
		if (!TestTrue(FString::Printf(TEXT("the same binding prepares again after the abort (errors: %s)"), *JoinErrors(Second.Errors)), Second.Succeeded()))
		{
			return false;
		}
		ExpectPrepared(*this, F, *Second.Batch, Before, Epoch);
		SecondWeak = WeakOwned(*Second.Batch);
	}
	ExpectAllDestroyed(*this, SecondWeak, TEXT("scope-exit abort"));
	ExpectRestored(*this, F, Before, TEXT("scope-exit abort"));
	TestTrue(TEXT("no touched package became dirty around the preparations and aborts (after the legitimate loads)"), CaptureDirty(Touched) == DirtyBefore);
	TestTrue(TEXT("the game instance and its published epoch are still the very ones used"), F.Scope.World->GetGameInstance() == F.Scope.GameInstance.Get() && F.PublishedEpoch().Get() == Epoch.Get());

	AddInfo(TEXT("World preparation on a real game-instance world: twenty-four owned unregistered components with each owner's own values and the very GI epoch lease; abort and scope-exit abort restore the sets. NOT established: drift during a stage (source-checked only), "
		"the latched source (logged), a cold load, authoritative manifest provenance, registration, BeginPlay, binding, reservation, Ready, activation or wiring."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGWorldPreparationLateFailureTest, "OneBossFight.Binding.WorldPreparation.LateInvalidAndCollision",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGWorldPreparationLateFailureTest::RunTest(const FString& Parameters)
{
	FFixture F;
	if (!F.Prepare(*this))
	{
		return false;
	}
	const FEpochPtr Epoch = F.PublishedEpoch();
	const TArray<FSelection> Selections = F.MakeSelections();
	const TArray<FRPGPlacedParticipantBinding> Valid = F.MakeParticipants();
	const TArray<FExpectedComponent> Expected = ExpectedComponents();

	// A late invalid member: the later boss actor holds no mesh, so the preflight inside the input stage refuses the whole batch; nothing is allocated for the valid first boss.
	{
		ACharacter* Bare = F.Scope.SpawnCharacter(nullptr, FVector(2000.f, 0.f, 0.f));
		if (!TestNotNull(TEXT("a mesh-less native character was spawned"), Bare))
		{
			return false;
		}
		TArray<FRPGPlacedParticipantBinding> Mutated = Valid;
		Mutated[1].Actor = Bare;
		ARPGEncounterBinding* Case = F.SpawnBinding(Mutated, FGuid::NewGuid());
		if (!TestNotNull(TEXT("a binding with the mesh-less later boss was spawned"), Case))
		{
			return false;
		}
		const FWorldState Before = F.Capture();
		const FRPGWorldPreparationResult Refused = RPGBossWorldPreparation::PrepareWorldBatch(F.Scope.World, Case, Selections, ManifestHash());
		TestFalse(TEXT("late invalid member: refused, no artifact"), Refused.Succeeded() || Refused.Batch.IsValid());
		TestTrue(FString::Printf(TEXT("late invalid member: the input-stage preflight layer is named with the nested token (got: %s)"), *JoinErrors(Refused.Errors)),
			AnyErrorHasAll(Refused.Errors, TEXT("WorldInput.PreflightRejected"), TEXT("Preflight.ProductionPrerequisite[slot=BossTwo]"), TEXT("mesh is compatible with the compiled skeleton")));
		TestTrue(TEXT("late invalid member: no Preparation.* token (the preparation stage never ran)"), !Refused.Errors.ContainsByPredicate([](const FString& E) { return E.StartsWith(TEXT("Preparation.")); }));
		ExpectRestored(*this, F, Before, TEXT("late invalid member"));
		TestTrue(TEXT("late invalid member: no object, not even a destroyed one, carries a planned name: nothing was allocated"), F.NothingAllocated());
	}

	// A REAL name collision: a live unrelated scene component under the third planned name of the LATER owner. The preflight's class guard does not see it; only the allocation guard can refuse.
	USceneComponent* Blocker = NewObject<USceneComponent>(F.BossTwoActor, USceneComponent::StaticClass(), FName(Expected[2].Name));
	if (!TestNotNull(TEXT("the blocker was created under the later owner"), Blocker))
	{
		return false;
	}
	TStrongObjectPtr<USceneComponent> BlockerLease(Blocker);
	const FVector BlockerLocation(11.f, 22.f, 33.f);
	Blocker->SetRelativeLocation(BlockerLocation);
	TSet<const UObject*> Preexisting;
	for (const AActor* Actor : {static_cast<const AActor*>(F.BossOneActor), static_cast<const AActor*>(F.BossTwoActor), static_cast<const AActor*>(F.TargetActor)})
	{
		TArray<UObject*> Inner;
		GetObjectsWithOuter(Actor, Inner, /*bIncludeNestedObjects=*/false);
		for (const UObject* Object : Inner)
		{
			if (IsValid(Object))
			{
				Preexisting.Add(Object);
			}
		}
	}
	const FWorldState BeforeCollision = F.Capture();
	{
		FRPGWorldPreparationResult Refused = RPGBossWorldPreparation::PrepareWorldBatch(F.Scope.World, F.Binding, Selections, ManifestHash());
		TestFalse(TEXT("name collision: refused, no artifact"), Refused.Succeeded() || Refused.Batch.IsValid());
		TestTrue(FString::Printf(TEXT("name collision: ONE error carries Preparation.AllocationFailed, [slot=BossTwo] and [component=RPGBossEncounter], and nothing else (got: %s)"), *JoinErrors(Refused.Errors)),
			Refused.Errors.Num() == 1 && AnyErrorHasAll(Refused.Errors, TEXT("Preparation.AllocationFailed"), TEXT("[slot=BossTwo]"), TEXT("[component=RPGBossEncounter]")));
	}
	// Seven earlier allocations (boss one's twelve, boss two's stagger and phases) must now be destroyed objects; the later names were never allocated; the blocker is the very live object.
	bool bBossOneDestroyed = true;
	for (const FExpectedComponent& Wanted : Expected)
	{
		const UObject* Found = StaticFindObjectFast(UObject::StaticClass(), F.BossOneActor, FName(Wanted.Name));
		bBossOneDestroyed = bBossOneDestroyed && Found && !IsValid(Found) && Found->GetClass() == Wanted.Class;
	}
	bool bBossTwoEarlierDestroyed = true;
	for (int32 Index = 0; Index < 2; ++Index)
	{
		const UObject* Found = StaticFindObjectFast(UObject::StaticClass(), F.BossTwoActor, FName(Expected[Index].Name));
		bBossTwoEarlierDestroyed = bBossTwoEarlierDestroyed && Found && !IsValid(Found) && Found->GetClass() == Expected[Index].Class;
	}
	TestTrue(TEXT("name collision: boss one's twelve and boss two's two earlier components were allocated and are now destroyed"), bBossOneDestroyed && bBossTwoEarlierDestroyed);
	bool bAllLaterNamesAbsent = true;
	for (int32 Index = 3; Index < Expected.Num(); ++Index)
	{
		bAllLaterNamesAbsent = bAllLaterNamesAbsent && StaticFindObjectFast(UObject::StaticClass(), F.BossTwoActor, FName(Expected[Index].Name)) == nullptr;
	}
	TestTrue(TEXT("name collision: blocked name keeps identity; all nine later names absent; target gets none"),
		StaticFindObjectFast(UObject::StaticClass(), F.BossTwoActor, FName(Expected[2].Name)) == Blocker && IsValid(Blocker) && bAllLaterNamesAbsent
		&& StaticFindObjectFast(UObject::StaticClass(), F.TargetActor, FName(Expected[0].Name)) == nullptr);
	ExpectRestored(*this, F, BeforeCollision, TEXT("name collision"));
	bool bPreexistingKept = true;
	for (const UObject* Object : Preexisting)
	{
		bPreexistingKept = bPreexistingKept && IsValid(Object);
	}
	TestTrue(TEXT("name collision: the blocker kept its identity and state and every preexisting object is still live"), bPreexistingKept && Blocker->GetOwner() == F.BossTwoActor && !Blocker->IsRegistered() && !Blocker->HasBegunPlay()
		&& Blocker->GetRelativeLocation() == BlockerLocation && F.BossTwoActor->GetComponents().Contains(Blocker));

	// Remove ONLY the fixture-owned blocker (renamed away first: a destroyed scene component would still hold the name and the allocation guard would refuse again), then retry the same binding.
	const FName RemovedName = MakeUniqueObjectName(F.BossTwoActor, USceneComponent::StaticClass(), TEXT("DD18RemovedBlocker"));
	Blocker->Rename(*RemovedName.ToString(), F.BossTwoActor, REN_DontCreateRedirectors | REN_NonTransactional);
	Blocker->DestroyComponent();
	BlockerLease.Reset();
	Blocker = nullptr;
	const FWorldState AfterRemoval = F.Capture();
	TestTrue(TEXT("only the blocker was removed: boss two lost exactly it, boss one and the target are as before"), AfterRemoval.Actors[1].Components.Num() == BeforeCollision.Actors[1].Components.Num() - 1 && SameActorState(AfterRemoval.Actors[0], BeforeCollision.Actors[0])
		&& SameActorState(AfterRemoval.Actors[2], BeforeCollision.Actors[2]));
	// NOTE: the failed attempt left destroyed, uncollected objects of the exact planned classes under seven names; the engine replaces them in place. This reuse is observed, it is not a claim about collected names.
	{
		FRPGWorldPreparationResult Retry = RPGBossWorldPreparation::PrepareWorldBatch(F.Scope.World, F.Binding, Selections, ManifestHash());
		if (!TestTrue(FString::Printf(TEXT("the same binding prepares after only the blocker was removed (errors: %s)"), *JoinErrors(Retry.Errors)), Retry.Succeeded()))
		{
			return false;
		}
		ExpectPrepared(*this, F, *Retry.Batch, AfterRemoval, Epoch);
		TArray<TWeakObjectPtr<UActorComponent>> RetryWeak = WeakOwned(*Retry.Batch);
		const FRPGPreparationAbortReport Report = Retry.Batch->Abort();
		TestTrue(TEXT("the retry's abort is clean and destroyed twenty-four"), Report.IsClean() && Report.Destroyed == 24 && Report.ContractViolations == 0);
		ExpectAllDestroyed(*this, RetryWeak, TEXT("retry abort"));
	}
	ExpectRestored(*this, F, AfterRemoval, TEXT("retry abort"));

	AddInfo(TEXT("Late invalid member (preflight layer, nothing allocated) and a real name collision under the later owner (allocation guard, seven earlier components cleaned, blocker and preexisting objects untouched, only the fixture-owned blocker removed). NOT covered: "
		"garbage-collected name reuse, an organic native configure failure, drift during a stage."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGWorldPreparationSecondTest, "OneBossFight.Binding.WorldPreparation.SecondPreparation",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGWorldPreparationSecondTest::RunTest(const FString& Parameters)
{
	FFixture F;
	if (!F.Prepare(*this))
	{
		return false;
	}
	const FEpochPtr Epoch = F.PublishedEpoch();
	const TArray<FSelection> Selections = F.MakeSelections();
	const FWorldState Before = F.Capture();

	FRPGWorldPreparationResult First = RPGBossWorldPreparation::PrepareWorldBatch(F.Scope.World, F.Binding, Selections, ManifestHash());
	if (!TestTrue(FString::Printf(TEXT("the first world preparation succeeds (errors: %s)"), *JoinErrors(First.Errors)), First.Succeeded()))
	{
		return false;
	}
	const FWorldState WithFirst = F.Capture();
	TArray<TWeakObjectPtr<UActorComponent>> FirstWeak = WeakOwned(*First.Batch);

	// A second, independent preparation of the SAME actors (another real binding, a new GUID): the accepted preflight refuses the already-attached consumers and nothing of the first is touched.
	{
		ARPGEncounterBinding* Second = F.SpawnBinding(F.MakeParticipants(), FGuid::NewGuid());
		if (!TestNotNull(TEXT("a second binding over the same actors was spawned"), Second))
		{
			return false;
		}
		const FRPGWorldPreparationResult Refused = RPGBossWorldPreparation::PrepareWorldBatch(F.Scope.World, Second, Selections, ManifestHash());
		TestFalse(TEXT("second preparation: refused, no artifact"), Refused.Succeeded() || Refused.Batch.IsValid());
		TestTrue(FString::Printf(TEXT("second preparation: the preflight layer names the preexisting consumer of the first boss (got: %s)"), *JoinErrors(Refused.Errors)),
			AnyErrorHasAll(Refused.Errors, TEXT("WorldInput.PreflightRejected"), TEXT("Preflight.PreexistingConsumer[slot=BossOne]"), TEXT("already has a")));
		TestTrue(TEXT("second preparation: the first artifact is undamaged: still prepared, twenty-four components, the very same objects, unregistered, and every actor is exactly as with the first"),
			First.Batch->IsPrepared() && First.Batch->GetOwnedComponentCount() == 24 && SameWorld(WithFirst, F.Capture()));
		bool bAllLive = true;
		for (const TWeakObjectPtr<UActorComponent>& Pointer : FirstWeak)
		{
			bAllLive = bAllLive && Pointer.IsValid() && !Pointer->IsRegistered();
		}
		TestTrue(TEXT("second preparation: every component of the first artifact is still the same live unregistered object"), FirstWeak.Num() == 24 && bAllLive);
	}
	// The SAME binding again (the first artifact is still held): refused the same way.
	{
		const FRPGWorldPreparationResult Refused = RPGBossWorldPreparation::PrepareWorldBatch(F.Scope.World, F.Binding, Selections, ManifestHash());
		TestFalse(TEXT("the same binding again: refused, no artifact"), Refused.Succeeded() || Refused.Batch.IsValid());
		TestTrue(TEXT("the same binding again: the first artifact is still undamaged"), First.Batch->IsPrepared() && First.Batch->GetOwnedComponentCount() == 24 && SameWorld(WithFirst, F.Capture()));
	}
	// After the first artifact is aborted the same actors prepare again (a new artifact).
	const FRPGPreparationAbortReport Report = First.Batch->Abort();
	TestTrue(TEXT("the first artifact's abort is clean and destroyed twenty-four"), Report.IsClean() && Report.Destroyed == 24 && Report.ContractViolations == 0);
	FirstWeak.Reset();
	TestTrue(TEXT("after the abort the world is as before"), SameWorld(Before, F.Capture()) && F.NoConsumers());
	{
		FRPGWorldPreparationResult Third = RPGBossWorldPreparation::PrepareWorldBatch(F.Scope.World, F.Binding, Selections, ManifestHash());
		if (!TestTrue(FString::Printf(TEXT("the same actors prepare again after the first artifact was aborted (errors: %s)"), *JoinErrors(Third.Errors)), Third.Succeeded()))
		{
			return false;
		}
		ExpectPrepared(*this, F, *Third.Batch, Before, Epoch);
	}
	TestTrue(TEXT("the third artifact was released by scope exit: the world is as before"), SameWorld(Before, F.Capture()) && F.NoConsumers());

	AddInfo(TEXT("A second independent preparation of the same actors is refused by the accepted preflight (nothing is reserved by the facade itself: the registry does that) without damaging the first artifact; after the first abort the actors prepare again. NOT covered: "
		"drift, re-entry, collected-name reuse."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGWorldPreparationRefusalsTest, "OneBossFight.Binding.WorldPreparation.Refusals",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGWorldPreparationRefusalsTest::RunTest(const FString& Parameters)
{
	FFixture F;
	if (!F.Prepare(*this))
	{
		return false;
	}
	const TArray<FSelection> Valid = F.MakeSelections();
	const FWorldState Before = F.Capture();
	auto ExpectRefusal = [this, &F, &Before](const TCHAR* Label, const FRPGWorldPreparationResult& Result, const TCHAR* Token, const TCHAR* Where)
	{
		TestFalse(FString::Printf(TEXT("%s: refused, no artifact"), Label), Result.Succeeded() || Result.Batch.IsValid());
		TestTrue(FString::Printf(TEXT("%s: the nested input-stage diagnostic %s %s is carried unchanged (got: %s)"), Label, Token, Where, *JoinErrors(Result.Errors)), AnyErrorHasAll(Result.Errors, Token, Where, TEXT("")));
		TestTrue(FString::Printf(TEXT("%s: no Preparation.* token (the preparation stage never ran) and nothing was allocated or changed"), Label),
			!Result.Errors.ContainsByPredicate([](const FString& E) { return E.StartsWith(TEXT("Preparation.")); }) && F.NothingAllocated() && SameWorld(Before, F.Capture()) && F.NoConsumers());
	};
	// The input stage refuses these; the facade carries its diagnostics and creates nothing.
	ExpectRefusal(TEXT("no world"), RPGBossWorldPreparation::PrepareWorldBatch(nullptr, F.Binding, Valid, ManifestHash()), TEXT("WorldInput.InvalidWorld"), TEXT(""));
	ExpectRefusal(TEXT("no binding"), RPGBossWorldPreparation::PrepareWorldBatch(F.Scope.World, nullptr, Valid, ManifestHash()), TEXT("WorldInput.InvalidBinding"), TEXT(""));
	ExpectRefusal(TEXT("a bad manifest hash"), RPGBossWorldPreparation::PrepareWorldBatch(F.Scope.World, F.Binding, Valid, FString::ChrN(63, TEXT('b'))), TEXT("WorldInput.InvalidManifestHash"), TEXT(""));
	{
		TArray<FSelection> Missing = Valid;
		Missing.RemoveAt(2);
		ExpectRefusal(TEXT("a missing selection"), RPGBossWorldPreparation::PrepareWorldBatch(F.Scope.World, F.Binding, Missing, ManifestHash()), TEXT("WorldInput.SelectionMissing"), TEXT("[slot=Player]"));
	}
	// Off the game thread: refused before any UObject is touched.
	{
		UWorld* PoolWorld = F.Scope.World;
		const ARPGEncounterBinding* PoolBinding = F.Binding;
		TFuture<TArray<FString>> Future = Async(EAsyncExecution::ThreadPool, [PoolWorld, PoolBinding, &Valid]()
			{
				const FRPGWorldPreparationResult Result = RPGBossWorldPreparation::PrepareWorldBatch(PoolWorld, PoolBinding, Valid, ManifestHash());
				return Result.Errors;
			});
		const TArray<FString> PoolErrors = Future.Get();
		TestTrue(FString::Printf(TEXT("off the game thread: WorldPrep.NotGameThread, nothing touched (got: %s)"), *JoinErrors(PoolErrors)), AnyErrorHasAll(PoolErrors, TEXT("WorldPrep.NotGameThread"), TEXT(""), TEXT("nothing was touched")));
		TestTrue(TEXT("off the game thread: nothing was allocated or changed"), F.NothingAllocated() && SameWorld(Before, F.Capture()));
	}
	// The control: the unmodified call succeeds after all the refusals.
	{
		FRPGWorldPreparationResult Control = RPGBossWorldPreparation::PrepareWorldBatch(F.Scope.World, F.Binding, Valid, ManifestHash());
		TestTrue(FString::Printf(TEXT("control: the unmodified call succeeds after the refusals (errors: %s)"), *JoinErrors(Control.Errors)), Control.Succeeded() && Control.Batch->GetOwnedComponentCount() == 24);
	}
	TestTrue(TEXT("the control artifact was released by scope exit: the world is as before"), SameWorld(Before, F.Capture()) && F.NoConsumers());

	AddInfo(TEXT("Facade refusal paths on a real game-instance world: the input stage's named diagnostics are carried unchanged and nothing is allocated; off the game thread the call is refused before any UObject is touched. NOT covered: drift between the stages "
		"(source-checked only)."));
	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
