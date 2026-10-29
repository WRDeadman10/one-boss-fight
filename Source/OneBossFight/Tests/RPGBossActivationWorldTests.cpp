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

#include "Player/RPGBossActivation.h"

// C316 new staged tests; fixture setup copied from accepted WorldPreparation tests, not modified in Source.
namespace
{
namespace ActivationWorldTests
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

		bool NoConsumers() const { return NoManagedConsumer(BossOneActor) && NoManagedConsumer(BossTwoActor) && NoManagedConsumer(TargetActor); }
	};

}
}
using namespace ActivationWorldTests;

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGActivationWorldSuccessTest, "OneBossFight.Binding.ActivationWorld.SuccessAndRelease", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGActivationWorldSuccessTest::RunTest(const FString& Parameters)
{
	FFixture F; if (!F.Prepare(*this)) { return false; }
	const FWorldState Before = F.Capture();
	const FEpochPtr Epoch = F.PublishedEpoch();
	{
		auto Result = RPGBossActivation::ActivateWorld(F.Scope.World, F.Binding, F.MakeSelections(), ManifestHash());
		if (!TestTrue(TEXT("world composition holds registered subset"), Result.Succeeded())) { return false; }
		TestTrue(TEXT("caller owns artifact/content lease, not a registry token"), Result.IsHeld() && Result.Batch->GetOwnedComponentCount() == 24 && Result.Batch->GetPreflightPlan()->Content.Get() == Epoch.Get());
		TestTrue(TEXT("exact ordered registrations"), Result.Registration.bSucceeded && Result.Registration.Registered.Num() == 24);
		for (const UActorComponent* Component : Result.Batch->OwnedComponentsForTest())
		{ TestTrue(TEXT("owned registered components never begun"), Component && Component->IsRegistered() && !Component->HasBegunPlay()); }
		TestTrue(TEXT("target/context unchanged"), SameActorState(CaptureActor(F.TargetActor), Before.Actors[2]) && F.Capture().Bound == Before.Bound && F.Capture().Ready == Before.Ready);
		const auto Release = Result.Release();
		TestTrue(TEXT("explicit release clean, all24 destroyed, lease gone, world restored"), Release.IsClean() && Release.Destroyed == 24 && !Result.IsHeld() && !Result.Batch.IsValid() && SameWorld(F.Capture(), Before) && F.NoConsumers());
		const auto Again = Result.Release();
		TestTrue(TEXT("repeat release empty"), Again.IsClean() && Again.Destroyed == 0);
	}
	{
		auto Result = RPGBossActivation::ActivateWorld(F.Scope.World, F.Binding, F.MakeSelections(), ManifestHash());
		if (!TestTrue(TEXT("scope-release control succeeds"), Result.Succeeded())) { return false; }
		FRPGWorldActivationResult Moved = MoveTemp(Result);
		TestTrue(TEXT("move transfers the sole artifact lease"), Moved.IsHeld() && !Result.IsHeld());
	}
	TestTrue(TEXT("result destruction invokes accepted batch cleanup"), SameWorld(F.Capture(), Before) && F.NoConsumers());
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGActivationWorldInvalidTest, "OneBossFight.Binding.ActivationWorld.InvalidInputAndMisuse", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGActivationWorldInvalidTest::RunTest(const FString& Parameters)
{
	FFixture F; if (!F.Prepare(*this)) { return false; }
	const FWorldState Before = F.Capture();
	const auto Selections = F.MakeSelections();
	{
		auto Result = RPGBossActivation::ActivateWorld(F.Scope.World, F.Binding, Selections, FString::ChrN(63, TEXT('b')));
		TestTrue(TEXT("invalid manifest falls back with original diagnostic"), Result.Outcome == ERPGWorldActivationOutcome::FallBackToLegacy && Result.Reason == FName(TEXT("ActivationWorld.PrepareRejected")) && Result.Errors.ContainsByPredicate([](const FString& S) { return S.StartsWith(TEXT("WorldInput.InvalidManifestHash")); }));
		TestTrue(TEXT("no lease, registrations or state drift"), !Result.Batch.IsValid() && Result.Registration.Registered.IsEmpty() && SameWorld(F.Capture(), Before) && F.NoConsumers());
	}
	{
		const auto Errors = Async(EAsyncExecution::ThreadPool, [&]()
		{
			auto Result = RPGBossActivation::ActivateWorld(F.Scope.World, F.Binding, Selections, ManifestHash());
			return Result.Outcome == ERPGWorldActivationOutcome::HardError && Result.Reason == FName(TEXT("ActivationWorld.NotGameThread")) && !Result.Batch.IsValid();
		}).Get();
		TestTrue(TEXT("programmer thread misuse hard-errors without UObject work"), Errors && SameWorld(F.Capture(), Before));
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGActivationWorldEpochTest, "OneBossFight.Binding.ActivationWorld.ContentEpochRejection", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGActivationWorldEpochTest::RunTest(const FString& Parameters)
{
	FFixture F; if (!F.Prepare(*this)) { return false; }
	const FWorldState Before = F.Capture();
	// Test-local missing world-GI content authority, not an injected/mismatched epoch parameter.
	UGameInstance* const OriginalGI = F.Scope.World->GetGameInstance();
	F.Scope.World->SetGameInstance(nullptr);
	auto Result = RPGBossActivation::ActivateWorld(F.Scope.World, F.Binding, F.MakeSelections(), ManifestHash());
	const bool bNoManufacturedGI = F.Scope.World->GetGameInstance() == nullptr;
	F.Scope.World->SetGameInstance(OriginalGI);
	TestTrue(TEXT("no authoritative content epoch means named fallback"), Result.Outcome == ERPGWorldActivationOutcome::FallBackToLegacy && Result.Errors.ContainsByPredicate([](const FString& S) { return S.StartsWith(TEXT("WorldInput.NoContent")); }));
	TestTrue(TEXT("no artifact/component left; fixture restored its own GI control"), bNoManufacturedGI && !Result.Batch.IsValid() && Result.Registration.Registered.IsEmpty() && F.NoConsumers() && SameWorld(F.Capture(), Before) && F.PublishedEpoch().Get() == RPGCombatRegistry::ForWorld(F.Scope.World).Get());
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGActivationWorldPreparationFailureTest, "OneBossFight.Binding.ActivationWorld.PreparationFailure", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGActivationWorldPreparationFailureTest::RunTest(const FString& Parameters)
{
	FFixture F; if (!F.Prepare(*this)) { return false; }
	const FWorldState Before = F.Capture();
	RPGBossHydrationPreparation::FFaultInjectionScope Fault(1);
	auto Result = RPGBossActivation::ActivateWorld(F.Scope.World, F.Binding, F.MakeSelections(), ManifestHash());
	TestTrue(TEXT("real allocation then injected preparation failure falls back"), Fault.Fired() && Result.Outcome == ERPGWorldActivationOutcome::FallBackToLegacy && Result.Reason == FName(TEXT("ActivationWorld.PrepareRejected")) && Result.Errors.ContainsByPredicate([](const FString& S) { return S.StartsWith(TEXT("Preparation.InjectedFault")); }));
	TestTrue(TEXT("whole world restored, nothing registered/held"), !Result.Batch.IsValid() && Result.Registration.Registered.IsEmpty() && F.NoConsumers() && SameWorld(F.Capture(), Before));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGActivationWorldRegistrationFailureTest, "OneBossFight.Binding.ActivationWorld.RegistrationFailure", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGActivationWorldRegistrationFailureTest::RunTest(const FString& Parameters)
{
	FFixture F; if (!F.Prepare(*this)) { return false; }
	const FWorldState Before = F.Capture();
	for (int32 Ordinal : {1, 12, 13, 24})
	{
		RPGBossActivation::FRegistrationFaultScope Fault(Ordinal);
		auto Result = RPGBossActivation::ActivateWorld(F.Scope.World, F.Binding, F.MakeSelections(), ManifestHash());
		TestTrue(TEXT("registration failure reports fallback and nested reason"), Fault.Fired() && Result.Outcome == ERPGWorldActivationOutcome::FallBackToLegacy && Result.Reason == FName(TEXT("ActivationWorld.RegistrationRejected")) && Result.Errors.ContainsByPredicate([](const FString& S) { return S.StartsWith(TEXT("Activation.InjectedFault")); }));
		TestTrue(TEXT("actual ordinal and clean rollback result retained"), Result.Registration.Registered.Num() == Ordinal && Result.Registration.Cleanup.Destroyed == 24 && Result.Registration.Cleanup.IsClean());
		TestTrue(TEXT("no partial registered subset or artifact lease"), !Result.Batch.IsValid() && F.NoConsumers() && SameWorld(F.Capture(), Before));
	}
	return true;
}

#endif
