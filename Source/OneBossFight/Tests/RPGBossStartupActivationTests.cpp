// Copyright One Boss Fight. All Rights Reserved.
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "CoreGlobals.h"
#include "Async/Async.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "HAL/IConsoleManager.h"
#include "TimerManager.h"
#include "Animation/Skeleton.h"
#include "Animation/AnimSequenceBase.h"
#include "GameFramework/Character.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/WorldSettings.h"
#include "Audio/RPGFootsteps.h"
#include "Player/RPGBossEncounter.h"
#include "Boss/RPGFrameworkBossCharacter.h"
#include "Player/RPGBossEncounterDefinition.h"
#include "Player/RPGBossFrameworkProfile.h"
#include "Player/RPGBossPhases.h"
#include "Player/RPGCombatCatalog.h"
#include "Player/RPGBossStagger.h"
#include "Player/RPGDodgeTiming.h"
#include "Player/RPGEncounterBinding.h"
#include "Player/RPGEncounterSelectionSubsystem.h"
#include "Player/RPGPlayerMovesSubsystem.h"
#include "Player/RPGBossHydrationPreparation.h"
#include "Player/RPGBossDamage.h"
#include "Player/RPGEncounterGenerationRules.h"
#include "Pack/RPGBlueprintCall.h"
#include "UObject/StrongObjectPtr.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "Math/RandomStream.h"

namespace
{
struct FStartupActivationWorld
{
	TStrongObjectPtr<UGameInstance> GameInstance;
	UWorld* World = nullptr;
	mutable TWeakObjectPtr<APlayerController> LocalPlayerController;

	FStartupActivationWorld()
	{
		if (!GEngine) return;
		GameInstance.Reset(NewObject<UGameInstance>(GEngine));
		if (!GameInstance.IsValid()) return;
		GameInstance->InitializeStandalone();
		World = GameInstance->GetWorld();
		if (World) World->InitializeActorsForPlay(FURL());
	}

	~FStartupActivationWorld()
	{
		if (GameInstance.IsValid()) GameInstance->Shutdown();
		if (World)
		{
			GEngine->DestroyWorldContext(World);
			World->DestroyWorld(false);
		}
	}

	FStartupActivationWorld(const FStartupActivationWorld&) = delete;
	FStartupActivationWorld& operator=(const FStartupActivationWorld&) = delete;

	URPGBossEncounterDefinition* MakeSelection() const
	{
		URPGBossEncounterDefinition* Encounter = NewObject<URPGBossEncounterDefinition>(GetTransientPackage());
		URPGBossDefinition* Boss = NewObject<URPGBossDefinition>(GetTransientPackage());
		URPGBossDefinition* Player = NewObject<URPGBossDefinition>(GetTransientPackage());
		if (!Encounter || !Boss || !Player) return nullptr;
		Encounter->EncounterInstance = FGuid::NewGuid();
		Encounter->StableManifestHash = FString::ChrN(64, TEXT('a'));
		Encounter->BossSlot = TEXT("Boss");
		Encounter->PlayerSlot = TEXT("Player");
		Encounter->InitialBossPhase = TEXT("PhaseOne");
		Encounter->BossDefinition = TSoftObjectPtr<URPGBossDefinition>(Boss);
		Encounter->PlayerDefinition = TSoftObjectPtr<URPGBossDefinition>(Player);
		FRPGPhaseConfig Phase;
		Phase.PhaseId = Encounter->InitialBossPhase;
		Boss->Phases.Add(Phase);
		return Encounter;
	}

	APawn* SpawnPackPawn(const TCHAR* Path, FVector Location) const
	{
		UClass* Class = LoadClass<APawn>(nullptr, Path);
		APawn* Pawn = World && Class ? World->SpawnActor<APawn>(Class, Location, FRotator::ZeroRotator) : nullptr;
		if (Pawn && URPGPlayerMovesSubsystem::IsPackPlayer(Pawn)) { PossessPlayer(Pawn); }
		return Pawn;
	}

	bool PossessPlayer(APawn* Pawn) const
	{
		if (!World || !IsValid(Pawn) || !URPGPlayerMovesSubsystem::IsPackPlayer(Pawn)) return false;
		APlayerController* Controller = LocalPlayerController.Get();
		if (!IsValid(Controller))
		{
			for (FConstPlayerControllerIterator It = World->GetPlayerControllerIterator(); It; ++It)
			{
				if (APlayerController* Existing = It->Get(); IsValid(Existing) && Existing->IsLocalController())
				{
					Controller = Existing;
					break;
				}
			}
		}
		if (!IsValid(Controller))
		{
			Controller = World->SpawnActor<APlayerController>(APlayerController::StaticClass(), FVector::ZeroVector, FRotator::ZeroRotator);
		}
		if (!IsValid(Controller) || !Controller->IsLocalController()) return false;
		LocalPlayerController = Controller;
		if (Controller->GetPawn() != Pawn) Controller->Possess(Pawn);
		return Controller->GetPawn() == Pawn;
	}

	APlayerController* SpawnAdditionalLocalPlayerController() const
	{
		return World ? World->SpawnActor<APlayerController>(APlayerController::StaticClass(), FVector::ZeroVector, FRotator::ZeroRotator) : nullptr;
	}

	void BeginSubsystemsOnly() const
	{
		if (!World) return;
		World->BeginPlay(); // dispatches UWorldSubsystem::OnWorldBeginPlay
	}

	void BeginPlay() const
	{
		BeginSubsystemsOnly();
		if (!World->GetBegunPlay())
		{
			if (AWorldSettings* WorldSettings = World->GetWorldSettings()) { WorldSettings->NotifyBeginPlay(); }
		}
	}
};

bool AddDeadStatusTag(APawn* Pawn)
{
	const FGameplayTag DeadTag = FGameplayTag::RequestGameplayTag(FName(TEXT("Status.Dead")), false);
	if (!IsValid(Pawn) || !DeadTag.IsValid()) return false;
	const bool bAdded = RPGPack::CallBlueprintFunction(Pawn, TEXT("AddOwnedGameplayTag"),
		[&DeadTag](UFunction& Function, uint8* Params) { RPGPack::SetTag(Function, Params, TEXT("TagToAdd"), DeadTag); },
		[](UFunction&, uint8*) {});
	return bAdded && RPGBossDamage::HasTag(Pawn, TEXT("Status.Dead"));
}

TArray<FString> StartupDefinitionFields(FName PhaseId)
{
	const FString Id = PhaseId.ToString();
	return {
		TEXT("StaggerPolicy.StaggerSeconds"), TEXT("StaggerPolicy.FreezeAtPosition"), TEXT("StaggerPolicy.CriticalMultiplier"), TEXT("StaggerPolicy.RiposteRange"), TEXT("StaggerPolicy.RiposteConeDegrees"),
		TEXT("StaggerPolicy.RiposteFacingDegrees"), TEXT("StaggerPolicy.RiposteArmSeconds"), TEXT("StaggerPolicy.RipostePlayerStartGap"), TEXT("StaggerPolicy.RiposteAlignSeconds"), TEXT("StaggerPolicy.RiposteImpactSeconds"),
		TEXT("StaggerPolicy.RiposteBaseDamage"), TEXT("StaggerPolicy.CooldownSeconds"), TEXT("StaggerPolicy.GetUpRate"), TEXT("StaggerPolicy.bHoldPostureAtZero"),
		TEXT("StaggerProfile.bUseClips"), TEXT("StaggerProfile.bUseRiposteClips"), TEXT("StaggerProfile.bCriticalOnEveryHit"), TEXT("StaggerProfile.HitStunAbilityClassName"), TEXT("StaggerProfile.FallMontage"),
		TEXT("StaggerProfile.GetUpMontage"), TEXT("StaggerProfile.FallClip"), TEXT("StaggerProfile.DownClip"), TEXT("StaggerProfile.RipostePlayerClip"), TEXT("StaggerProfile.RiposteBossClip"), TEXT("StaggerProfile.ImmunityEffect"),
		FString::Printf(TEXT("Phases[%s].EntryHealthFraction"), *Id), FString::Printf(TEXT("Phases[%s].SpeedMultiplier"), *Id), FString::Printf(TEXT("Phases[%s].RateMultiplier"), *Id), FString::Printf(TEXT("Phases[%s].AttackMultiplier"), *Id),
		TEXT("PhaseFlow.TransitionSeconds"), TEXT("PhaseFlow.bUseRoarClip"), TEXT("PhaseFlow.bPausePostureInTransition"), TEXT("PhaseFlow.bLockLeapUntilPhaseTwo"), TEXT("PhaseFlow.AttackAbilityPrefix"), TEXT("PhaseFlow.LeapAbilityTag"),
		TEXT("Fireball.bFireballEnabled"), TEXT("Fireball.FireballAbility"), TEXT("Fireball.FireballCooldown"), TEXT("Fireball.FireballMinRange"), TEXT("Fireball.FireballMaxRange"),
		TEXT("PhaseDependencies.RoarClip"), TEXT("PhaseDependencies.TransitionMontage"), TEXT("PhaseDependencies.ImmunityEffect"),
		TEXT("Stats.MaxHealth"), TEXT("EncounterPolicy.GateRadius"), TEXT("EncounterPolicy.bResetOnPlayerRespawn"), TEXT("DormantWake.DormantClip"), TEXT("DormantWake.WakeClip"),
		TEXT("Stats.MaxPosture"), TEXT("Stats.PostureRegenDelay"), TEXT("Stats.PostureRegenRate"),
		TEXT("Bleed.InitialThreshold"), TEXT("Bleed.ThresholdIncrease"), TEXT("Bleed.ThresholdMax"), TEXT("Bleed.HpFraction"), TEXT("Bleed.EffectHeight"), TEXT("Bleed.ProcEffect"), TEXT("Bleed.ProcSound"),
		TEXT("LowSweep.bEnabled"), TEXT("LowSweep.MoveId"), TEXT("LowSweep.Damage"), TEXT("LowSweep.Reach"), TEXT("LowSweep.InnerRadius"), TEXT("LowSweep.BladeHeight"), TEXT("LowSweep.SweepFromDegrees"), TEXT("LowSweep.SweepToDegrees"),
		TEXT("Shockwave.bEnabled"), TEXT("Shockwave.MoveId"), TEXT("Shockwave.Damage"), TEXT("Shockwave.StartRadius"), TEXT("Shockwave.MaxRadius"), TEXT("Shockwave.Speed"), TEXT("Shockwave.Thickness"), TEXT("Shockwave.JumpClearance"),
		TEXT("HealPunish.bEnabled"), TEXT("HealPunish.MinRange"), TEXT("HealPunish.MaxRange"), TEXT("HealPunish.Cooldown"), TEXT("HealPunish.Damage"), TEXT("HealPunish.FlightTime"), TEXT("HealPunish.MinSpeed"), TEXT("HealPunish.MaxSpeed"), TEXT("HealPunish.JavelinRadius"), TEXT("HealPunish.JavelinMaxRange"), TEXT("HealPunish.SpawnSockets"), TEXT("HealPunish.AimHeight"), TEXT("HealPunish.bRespondToHeal"), TEXT("HealPunish.bCancelJavelinsOnInterrupt"),
		TEXT("Look.bEnabled"), TEXT("Look.Body"), TEXT("Look.Pieces"), TEXT("Look.Sword"), TEXT("Look.SwordSocket"),
		TEXT("CloseClipSwap.CloseAbilityClassName"), TEXT("CloseClipSwap.AttackMontagesName"), TEXT("CloseClipSwap.A1Montage"), TEXT("CloseClipSwap.A3aMontage"), TEXT("CloseClipSwap.A3bMontage"),
		TEXT("Death.DeathMode"), TEXT("Death.DeathClip"), TEXT("Death.DeathMontage"), TEXT("Death.PackDeathAbilityClassName"), TEXT("Death.PackDeathMontagesName"), TEXT("Death.PackPollSeconds"), TEXT("Death.PackEndTimeMultiplier"), TEXT("Death.HoldAtSeconds"), TEXT("Death.DyingSeconds"), TEXT("Death.BlendInSeconds"), TEXT("Death.MaxClipRestarts"), TEXT("Death.bGuardPackDeath")};
}

FRPGParityField StartupDefinitionField(const FString& Path)
{
	FRPGParityField Field;
	Field.FieldPath = Path; Field.Type = TEXT("fixture"); Field.Value = TEXT("activation automation fixture membership");
	Field.SourcePath = TEXT("test fixture"); Field.SourceSHA256 = FString::ChrN(64, TEXT('c')); Field.SourceSite = TEXT("test");
	Field.Origin = TEXT("harness"); Field.Precedence = TEXT("fixture"); Field.Destination = TEXT("fixture");
	Field.FirstRead = TEXT("not read"); Field.Witness = TEXT("test fixture");
	return Field;
}

void FillStartupDefinition(URPGBossDefinition& Definition, const TCHAR* Id, const TCHAR* Presentation, USkeleton* Skeleton, const TArray<FSoftObjectPath>& Animations)
{
	Definition.Schema = 1; Definition.DefinitionId = FName(Id); Definition.PresentationId = FName(Presentation);
	Definition.Stats.MaxHealth = 3500.f; Definition.Stats.MaxPosture = 73.5f; Definition.Stats.PostureRegenDelay = 4.25f; Definition.Stats.PostureRegenRate = 9.75f;
	Definition.EncounterPolicy = FRPGEncounterPolicyConfig(); Definition.StaggerPolicy = FRPGStaggerPolicyConfig(); Definition.PhaseFlow = FRPGPhaseFlowConfig();
	Definition.Fireball = FRPGFireballConfig(); Definition.PhaseDependencies = FRPGPhaseDependencyConfig(); Definition.StaggerProfile = FRPGStaggerProfileConfig();
	Definition.DormantWake = FRPGDormantWakeConfig();
	FRPGPhaseConfig Phase; Phase.PhaseId = TEXT("PhaseOne"); Phase.EntryHealthFraction = 0.35f; Phase.SpeedMultiplier = 1.5f; Phase.RateMultiplier = 1.75f; Phase.AttackMultiplier = 2.f;
	Definition.Phases = {Phase}; Definition.Skeleton = TSoftObjectPtr<USkeleton>(Skeleton);
	for (const FSoftObjectPath& Path : Animations) Definition.Animations.Add(TSoftObjectPtr<UAnimSequenceBase>(Path));
	for (const FString& Path : StartupDefinitionFields(Phase.PhaseId)) Definition.Fields.Add(StartupDefinitionField(Path));
}

TArray<FSoftObjectPath> StartupBossAnimations()
{
	FRPGDormantWakeConfig Wake; FRPGPhaseDependencyConfig Dependencies; FRPGStaggerProfileConfig Profile;
	return {Wake.DormantClip.ToSoftObjectPath(), Wake.WakeClip.ToSoftObjectPath(), Dependencies.RoarClip.ToSoftObjectPath(), Dependencies.TransitionMontage.ToSoftObjectPath(),
		Profile.FallMontage.ToSoftObjectPath(), Profile.GetUpMontage.ToSoftObjectPath(), Profile.FallClip.ToSoftObjectPath(), Profile.DownClip.ToSoftObjectPath(), Profile.RiposteBossClip.ToSoftObjectPath()};
}

TArray<FSoftObjectPath> StartupPlayerAnimations()
{
	FRPGStaggerProfileConfig Profile;
	return {Profile.RipostePlayerClip.ToSoftObjectPath()};
}

const TCHAR* const PlayerClassPath = TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter.BP_CombatPlayerCharacter_C");
const TCHAR* const BossClassPath = TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss.BP_ExampleGreatSwordBoss_C");

URPGBossEncounterDefinition* MakeValidPackSelection()
{
	UClass* BossClass = LoadClass<ACharacter>(nullptr, BossClassPath);
	UClass* PlayerClass = LoadClass<ACharacter>(nullptr, PlayerClassPath);
	const ACharacter* BossCDO = BossClass ? Cast<ACharacter>(BossClass->GetDefaultObject()) : nullptr;
	const ACharacter* PlayerCDO = PlayerClass ? Cast<ACharacter>(PlayerClass->GetDefaultObject()) : nullptr;
	USkeletalMesh* BossMesh = BossCDO && BossCDO->GetMesh() ? BossCDO->GetMesh()->GetSkeletalMeshAsset() : nullptr;
	USkeletalMesh* PlayerMesh = PlayerCDO && PlayerCDO->GetMesh() ? PlayerCDO->GetMesh()->GetSkeletalMeshAsset() : nullptr;
	if (!BossMesh || !PlayerMesh || !BossMesh->GetSkeleton() || !PlayerMesh->GetSkeleton()) return nullptr;
	URPGBossDefinition* BossDefinition = NewObject<URPGBossDefinition>(GetTransientPackage());
	URPGBossDefinition* PlayerDefinition = NewObject<URPGBossDefinition>(GetTransientPackage());
	if (!BossDefinition || !PlayerDefinition) return nullptr;
	FillStartupDefinition(*BossDefinition, TEXT("StartupBoss"), TEXT("StartupBossLook"), BossMesh->GetSkeleton(), StartupBossAnimations());
	FillStartupDefinition(*PlayerDefinition, TEXT("StartupPlayer"), TEXT("StartupPlayerLook"), PlayerMesh->GetSkeleton(), StartupPlayerAnimations());
	URPGBossEncounterDefinition* Encounter = NewObject<URPGBossEncounterDefinition>(GetTransientPackage());
	if (!Encounter) return nullptr;
	Encounter->EncounterInstance = FGuid::NewGuid();
	Encounter->StableManifestHash = FString::ChrN(64, TEXT('b'));
	Encounter->BossSlot = TEXT("Boss"); Encounter->PlayerSlot = TEXT("Player"); Encounter->InitialBossPhase = TEXT("PhaseOne");
	Encounter->BossDefinition = TSoftObjectPtr<URPGBossDefinition>(BossDefinition);
	Encounter->PlayerDefinition = TSoftObjectPtr<URPGBossDefinition>(PlayerDefinition);
	FString Error;
	return Encounter->ValidateSelectionRecord(Error) ? Encounter : nullptr;
}

bool HasLegacyBossBundle(const AActor* Boss)
{
	return Boss && (Boss->FindComponentByClass<URPGBossEncounter>()
		|| Boss->FindComponentByClass<URPGBossPhases>()
		|| Boss->FindComponentByClass<URPGBossStagger>());
}

bool ReadActivationSnapshot(const URPGPlayerMovesSubsystem& Moves, FString& OutOutcome, FString& OutReason, bool& bOutBindingRetained, FString* OutRoute = nullptr)
{
	TSharedPtr<FJsonObject> Snapshot;
	const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Moves.BuildEncounterParitySnapshot());
	if (!FJsonSerializer::Deserialize(Reader, Snapshot) || !Snapshot.IsValid()) { return false; }
	if (OutRoute && !Snapshot->TryGetStringField(TEXT("route"), *OutRoute)) { return false; }
	const TSharedPtr<FJsonObject>* Activation = nullptr;
	if (!Snapshot->TryGetObjectField(TEXT("activation"), Activation) || !Activation || !Activation->IsValid()) { return false; }
	return (*Activation)->TryGetStringField(TEXT("outcome"), OutOutcome)
		&& (*Activation)->TryGetStringField(TEXT("reason"), OutReason)
		&& (*Activation)->TryGetBoolField(TEXT("binding_retained"), bOutBindingRetained);
}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterSelectionRecordValidation,
	"OneBossFight.Binding.EncounterSelection.RecordValidation",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterSelectionRecordValidation::RunTest(const FString&)
{
	FStartupActivationWorld Scope;
	if (!TestNotNull(TEXT("real game-instance test world"), Scope.World)) return false;
	URPGBossEncounterDefinition* Encounter = Scope.MakeSelection();
	if (!TestNotNull(TEXT("transient selection record"), Encounter)) return false;
	FString Error;
	TestTrue(TEXT("complete typed record is accepted structurally"), Encounter->ValidateSelectionRecord(Error));
	TestTrue(TEXT("success clears diagnostic"), Error.IsEmpty());
	TestTrue(TEXT("pack definition remains allowed while framework selector is off"), RPGEncounterSelectionRules::AllowsFrameworkDefinition(false, 0));
	TestFalse(TEXT("framework definition is refused with opt-in unset"), RPGEncounterSelectionRules::AllowsFrameworkDefinition(true, 0));
	TestTrue(TEXT("framework definition is allowed only with explicit opt-in"), RPGEncounterSelectionRules::AllowsFrameworkDefinition(true, 1));
	Encounter->bUseFrameworkBoss = true;
	TestFalse(TEXT("framework selection requires a framework profile"), Encounter->ValidateSelectionRecord(Error));
	TestEqual(TEXT("missing framework profile refusal is stable"), Error, FString(TEXT("EncounterDefinition.FrameworkProfile")));
	Encounter->FrameworkBossProfile = TSoftObjectPtr<URPGBossFrameworkProfile>(NewObject<URPGBossFrameworkProfile>(GetTransientPackage()));
	TestTrue(TEXT("framework definition with profile is structurally valid"), Encounter->ValidateSelectionRecord(Error));
	Encounter->bUseFrameworkBoss = false;
	Encounter->FrameworkBossProfile.Reset();
	Encounter->EncounterInstance.Invalidate();
	TestFalse(TEXT("invalid encounter GUID is refused"), Encounter->ValidateSelectionRecord(Error));
	TestEqual(TEXT("invalid GUID token is stable"), Error, FString(TEXT("EncounterDefinition.InstanceId")));
	Encounter->EncounterInstance = FGuid::NewGuid();
	Encounter->BossSlot = NAME_None;
	TestFalse(TEXT("empty boss slot is refused"), Encounter->ValidateSelectionRecord(Error));
	TestEqual(TEXT("empty slot token is stable"), Error, FString(TEXT("EncounterDefinition.Slots")));
	Encounter->BossSlot = Encounter->PlayerSlot;
	TestFalse(TEXT("duplicate role slots are refused"), Encounter->ValidateSelectionRecord(Error));
	TestEqual(TEXT("duplicate slot token is stable"), Error, FString(TEXT("EncounterDefinition.Slots")));
	Encounter->BossSlot = TEXT("Boss");
	Encounter->InitialBossPhase = NAME_None;
	TestFalse(TEXT("missing phase is rejected"), Encounter->ValidateSelectionRecord(Error));
	TestEqual(TEXT("missing phase token"), Error, FString(TEXT("EncounterDefinition.Phase")));
	Encounter->InitialBossPhase = TEXT("PhaseOne");
	Encounter->StableManifestHash = TEXT("not-a-hash");
	TestFalse(TEXT("malformed manifest identity is rejected"), Encounter->ValidateSelectionRecord(Error));
	TestEqual(TEXT("manifest shape token"), Error, FString(TEXT("EncounterDefinition.ManifestShape")));
	Encounter->StableManifestHash = FString::ChrN(64, TEXT('a'));
	Encounter->StableManifestHash[17] = TEXT('g');
	TestFalse(TEXT("non-hex manifest identity is rejected"), Encounter->ValidateSelectionRecord(Error));
	TestEqual(TEXT("manifest alphabet token"), Error, FString(TEXT("EncounterDefinition.ManifestShape")));
	Encounter->StableManifestHash = FString::ChrN(64, TEXT('a'));
	Encounter->PlayerDefinition = Encounter->BossDefinition;
	TestFalse(TEXT("same definition cannot fill both encounter roles"), Encounter->ValidateSelectionRecord(Error));
	TestEqual(TEXT("role-definition collision token"), Error, FString(TEXT("EncounterDefinition.DefinitionsNotDistinct")));
	Encounter->PlayerDefinition = TSoftObjectPtr<URPGBossDefinition>();
	TestFalse(TEXT("missing player definition is rejected"), Encounter->ValidateSelectionRecord(Error));
	TestEqual(TEXT("missing definition token"), Error, FString(TEXT("EncounterDefinition.Definitions")));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGFrameworkEncounterOptInBinding,
	"OneBossFight.Binding.EncounterSelection.FrameworkOptInAndExactBinding",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGFrameworkEncounterOptInBinding::RunTest(const FString&)
{
	FStartupActivationWorld Scope;
	if (!TestNotNull(TEXT("real game-instance test world"), Scope.World)) return false;
	IConsoleVariable* Gate = IConsoleManager::Get().FindConsoleVariable(TEXT("rpg.FrameworkEncounterSelection"));
	if (!TestNotNull(TEXT("default-off framework selection CVar"), Gate)) return false;
	const int32 Previous = Gate->GetInt();
	ON_SCOPE_EXIT { Gate->Set(Previous, ECVF_SetByCode); };
	Gate->Set(0, ECVF_SetByCode);
	URPGEncounterSelectionSubsystem* Selection = Scope.GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>();
	if (!TestNotNull(TEXT("selection subsystem"), Selection)) return false;
	URPGBossEncounterDefinition* Definition = Scope.MakeSelection();
	Definition->bUseFrameworkBoss = true;
	Definition->FrameworkBossProfile = TSoftObjectPtr<URPGBossFrameworkProfile>(NewObject<URPGBossFrameworkProfile>(GetTransientPackage()));
	Selection->SetSelectedDefinition(Definition);
	ARPGEncounterBinding* Binding = nullptr;
	TArray<RPGBossWorldInputCompiler::FSelection> Selections;
	FString Error;
	TestFalse(TEXT("default-off gate refuses framework definition before census"), Selection->BuildWorldBinding(*Scope.World, Binding, Selections, Error));
	TestEqual(TEXT("default-off reason is explicit"), Error, FString(TEXT("EncounterSelection.FrameworkOptInRequired")));
	Gate->Set(1, ECVF_SetByCode);
	ARPGFrameworkBossCharacter* FrameworkBoss = Scope.World->SpawnActor<ARPGFrameworkBossCharacter>(FVector::ZeroVector, FRotator::ZeroRotator);
	APawn* Player = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	TestNotNull(TEXT("placed native framework boss"), FrameworkBoss);
	TestTrue(TEXT("one local player is possessed"), Scope.PossessPlayer(Player));
	if (!TestNotNull(TEXT("framework boss"), FrameworkBoss) || !TestNotNull(TEXT("player"), Player)) return false;
	TestTrue(TEXT("explicit opt-in binds the framework boss and player"), Selection->BuildWorldBinding(*Scope.World, Binding, Selections, Error));
	if (!TestNotNull(TEXT("transient framework binding"), Binding)) return false;
	TestEqual(TEXT("selected generation is carried without narrowing"), Binding->ParticipantGeneration, uint64(1));
	TestEqual(TEXT("typed framework profile is carried on the binding"), Binding->FrameworkBossProfile.Get(), Definition->FrameworkBossProfile.Get());
	TestTrue(TEXT("only selected framework boss and player become participants"), Binding->Participants.Num() == 2
		&& Binding->Participants.ContainsByPredicate([FrameworkBoss](const FRPGPlacedParticipantBinding& Item) { return Item.Actor == FrameworkBoss; })
		&& Binding->Participants.ContainsByPredicate([Player](const FRPGPlacedParticipantBinding& Item) { return Item.Actor == Player; }));
	Binding->Destroy();
	FrameworkBoss->Destroy();
	Definition->bUseFrameworkBoss = false;
	Definition->FrameworkBossProfile.Reset();
	Gate->Set(0, ECVF_SetByCode);
	APawn* PackBoss = Scope.SpawnPackPawn(BossClassPath, FVector(0.f, 3000.f, 0.f));
	TestNotNull(TEXT("legacy pack boss candidate"), PackBoss);
	TestTrue(TEXT("pack definition retains selection while framework gate is off"), Selection->BuildWorldBinding(*Scope.World, Binding, Selections, Error));
	if (TestNotNull(TEXT("pack binding"), Binding))
	{
		TestTrue(TEXT("pack binding still selects the pack boss"), Binding->Participants.ContainsByPredicate(
			[PackBoss](const FRPGPlacedParticipantBinding& Item) { return Item.Slot == FName(TEXT("Boss")) && Item.Actor == PackBoss; }));
		Binding->Destroy();
	}
	Definition->bUseFrameworkBoss = true;
	Definition->FrameworkBossProfile = TSoftObjectPtr<URPGBossFrameworkProfile>(NewObject<URPGBossFrameworkProfile>(GetTransientPackage()));
	Gate->Set(1, ECVF_SetByCode);
	FrameworkBoss = Scope.World->SpawnActor<ARPGFrameworkBossCharacter>(FVector::ZeroVector, FRotator::ZeroRotator);
	Scope.SpawnPackPawn(BossClassPath, FVector(0.f, 3000.f, 0.f));
	TestFalse(TEXT("mixed framework and pack boss census is refused before a second binding"), Selection->BuildWorldBinding(*Scope.World, Binding, Selections, Error));
	TestEqual(TEXT("mixed route refusal is stable"), Error, FString(TEXT("EncounterSelection.Census")));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterSelectionAbsentPreservesLegacy,
	"OneBossFight.Binding.EncounterSelection.AbsentPreservesLegacyStartup",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterSelectionAbsentPreservesLegacy::RunTest(const FString&)
{
	FStartupActivationWorld Scope;
	if (!TestNotNull(TEXT("real game-instance test world"), Scope.World)) return false;
	URPGEncounterSelectionSubsystem* Selection = Scope.GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>();
	URPGPlayerMovesSubsystem* Moves = Scope.World->GetSubsystem<URPGPlayerMovesSubsystem>();
	if (!TestNotNull(TEXT("game-instance selection store"), Selection) || !TestNotNull(TEXT("moves subsystem"), Moves)) return false;
	TestTrue(TEXT("absent config key preserves legacy startup default"), Moves->bUseLegacyStartup);
	Selection->ClearSelectedDefinition();
	TestFalse(TEXT("cleared store means selection absent"), Selection->HasSelectionRequest());
	APawn* Boss = Scope.SpawnPackPawn(BossClassPath, FVector::ZeroVector);
	APawn* Player = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("pack boss"), Boss) || !TestNotNull(TEXT("pack player"), Player)) return false;
	Scope.BeginPlay();
	FString Route;
	FString Outcome;
	FString Reason;
	bool bBindingRetained = false;
	TestTrue(TEXT("legacy route snapshot parses"), ReadActivationSnapshot(*Moves, Outcome, Reason, bBindingRetained, &Route));
	TestEqual(TEXT("no selection chooses legacy route"), Route, FString(TEXT("legacy")));
	TestEqual(TEXT("legacy route records no-selection outcome"), Outcome, FString(TEXT("LegacyNoSelection")));
	TestTrue(TEXT("no-selection startup keeps legacy boss bundle"), HasLegacyBossBundle(Boss));
	TestNotNull(TEXT("no-selection startup keeps player-side dodge setup"), Player->FindComponentByClass<URPGDodgeTiming>());
	TestNotNull(TEXT("no-selection startup keeps player footsteps"), Player->FindComponentByClass<URPGFootsteps>());
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterSelectionLegacyStartupDisabled,
	"OneBossFight.Binding.EncounterSelection.LegacyStartupConfigOff",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterSelectionLegacyStartupDisabled::RunTest(const FString&)
{
	FStartupActivationWorld Scope;
	if (!TestNotNull(TEXT("real game-instance test world"), Scope.World)) return false;
	URPGEncounterSelectionSubsystem* Selection = Scope.GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>();
	URPGPlayerMovesSubsystem* Moves = Scope.World->GetSubsystem<URPGPlayerMovesSubsystem>();
	if (!TestNotNull(TEXT("game-instance selection store"), Selection) || !TestNotNull(TEXT("moves subsystem"), Moves)) return false;
	Selection->ClearSelectedDefinition();
	Moves->bUseLegacyStartup = false;
	APawn* Boss = Scope.SpawnPackPawn(BossClassPath, FVector::ZeroVector);
	APawn* Player = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("pack boss"), Boss) || !TestNotNull(TEXT("pack player"), Player)) return false;
	Scope.BeginPlay();
	FString Route;
	FString Outcome;
	FString Reason;
	bool bBindingRetained = false;
	TestTrue(TEXT("disabled route snapshot parses"), ReadActivationSnapshot(*Moves, Outcome, Reason, bBindingRetained, &Route));
	TestEqual(TEXT("config-off startup selects disabled route"), Route, FString(TEXT("disabled")));
	TestEqual(TEXT("disabled route records its selected outcome"), Outcome, FString(TEXT("LegacyStartupDisabled")));
	TestFalse(TEXT("legacy boss bundle stays absent with config off"), HasLegacyBossBundle(Boss));
	TestNull(TEXT("legacy player dodge component stays absent with config off"), Player->FindComponentByClass<URPGDodgeTiming>());
	TestNull(TEXT("legacy player footsteps stay absent with config off"), Player->FindComponentByClass<URPGFootsteps>());
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterSelectionStartupSuccess,
	"OneBossFight.Binding.EncounterSelection.SelectedStartupActivatesExactParticipants",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterSelectionStartupSuccess::RunTest(const FString&)
{
	FStartupActivationWorld Scope;
	if (!TestNotNull(TEXT("real game-instance test world"), Scope.World)) return false;
	URPGEncounterSelectionSubsystem* Selection = Scope.GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>();
	URPGPlayerMovesSubsystem* Moves = Scope.World->GetSubsystem<URPGPlayerMovesSubsystem>();
	if (!TestNotNull(TEXT("game-instance selection store"), Selection) || !TestNotNull(TEXT("world moves subsystem"), Moves)) return false;
	Moves->bUseLegacyStartup = false; // explicit selected route stays independent of the legacy fallback switch
	URPGBossEncounterDefinition* Encounter = MakeValidPackSelection();
	if (!TestNotNull(TEXT("valid transient boss/player definitions"), Encounter)) return false;
	Selection->SetSelectedDefinition(Encounter);
	APawn* Boss = Scope.SpawnPackPawn(BossClassPath, FVector::ZeroVector);
	APawn* Player = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("pack boss"), Boss) || !TestNotNull(TEXT("pack player"), Player)) return false;

	Scope.BeginPlay();
	FString Route;
	FString Outcome;
	FString Reason;
	bool bBindingRetained = false;
	TestTrue(TEXT("selected route snapshot parses"), ReadActivationSnapshot(*Moves, Outcome, Reason, bBindingRetained, &Route));
	TestEqual(TEXT("stored definition selects data route"), Route, FString(TEXT("data")));
	TestEqual(TEXT("data route records successful activation"), Outcome, FString(TEXT("Activated")));
	TestTrue(TEXT("successful startup clears selection diagnostic"), Selection->GetSelectionDiagnostic().IsEmpty());
	TestTrue(TEXT("successful startup leaves boss collision enabled"), Boss->GetActorEnableCollision());
	TestNotNull(TEXT("data activation registers boss encounter component"), Boss->FindComponentByClass<URPGBossEncounter>());
	TestNotNull(TEXT("data activation registers boss stagger component"), Boss->FindComponentByClass<URPGBossStagger>());
	TestNotNull(TEXT("data activation registers boss phase component"), Boss->FindComponentByClass<URPGBossPhases>());
	TestNotNull(TEXT("selected player retains dodge timing"), Player->FindComponentByClass<URPGDodgeTiming>());
	TestNotNull(TEXT("selected player retains footsteps"), Player->FindComponentByClass<URPGFootsteps>());
	TActorIterator<ARPGEncounterBinding> Bindings(Scope.World);
	TestTrue(TEXT("successful startup keeps its transient binding"), static_cast<bool>(Bindings));
	if (Bindings)
	{
		TestEqual(TEXT("binding has the exact boss and player participants"), Bindings->Participants.Num(), 2);
		if (Bindings->Participants.Num() == 2)
		{
			TestTrue(TEXT("boss participant points at censused boss"), Bindings->Participants[0].Actor == Boss);
			TestTrue(TEXT("player participant points at censused player"), Bindings->Participants[1].Actor == Player);
		}
	}
	Selection->ClearSelectedDefinition();
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterSelectionRespawnRebindAndDuplicateBroadcast,
	"OneBossFight.Binding.EncounterSelection.ResetBroadcastRebindsAndDeduplicates",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterSelectionRespawnRebindAndDuplicateBroadcast::RunTest(const FString&)
{
	FStartupActivationWorld Scope;
	if (!TestNotNull(TEXT("real game-instance test world"), Scope.World)) return false;
	URPGEncounterSelectionSubsystem* Selection = Scope.GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>();
	URPGPlayerMovesSubsystem* Moves = Scope.World->GetSubsystem<URPGPlayerMovesSubsystem>();
	if (!TestNotNull(TEXT("selection store"), Selection) || !TestNotNull(TEXT("moves subsystem"), Moves)) return false;
	URPGBossEncounterDefinition* Definition = MakeValidPackSelection();
	if (!TestNotNull(TEXT("selected data definitions"), Definition)) return false;
	Selection->SetSelectedDefinition(Definition);
	APawn* Boss = Scope.SpawnPackPawn(BossClassPath, FVector::ZeroVector);
	APawn* OldPlayer = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("pack boss"), Boss) || !TestNotNull(TEXT("initial pack player"), OldPlayer)) return false;
	Scope.BeginPlay();
	URPGBossEncounter* OldEncounter = Boss->FindComponentByClass<URPGBossEncounter>();
	if (!TestNotNull(TEXT("initial selected activation"), OldEncounter)) return false;

	OldPlayer->Destroy();
	APawn* NewPlayer = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("replacement pack player"), NewPlayer)) return false;
	OldEncounter->ResetForTest(); // the native reset broadcast is the only rebind trigger
	ARPGEncounterBinding* CurrentBinding = nullptr;
	int32 BindingCount = 0;
	for (TActorIterator<ARPGEncounterBinding> It(Scope.World); It; ++It) { CurrentBinding = *It; ++BindingCount; }
	TestEqual(TEXT("one active binding remains after rebind"), BindingCount, 1);
	if (!TestNotNull(TEXT("rebound selected binding"), CurrentBinding)) return false;
	TestEqual(TEXT("binding carries reset generation"), CurrentBinding->ParticipantGeneration, static_cast<uint64>(2));
	TestEqual(TEXT("binding carries reset count"), CurrentBinding->ResetCount, 1);
	TestTrue(TEXT("binding retains the original selection identity"), CurrentBinding->EncounterInstance == Definition->EncounterInstance);
	TestTrue(TEXT("rebind points to replacement player"), CurrentBinding->Participants.Num() == 2 && CurrentBinding->Participants[1].Actor == NewPlayer);
	TestEqual(TEXT("binding retains the selected definition path"), CurrentBinding->SelectionDefinitionPath, Definition->GetPathName());
	TestEqual(TEXT("binding retains the canonical manifest digest"), CurrentBinding->StableManifestHash, Definition->StableManifestHash);
	URPGBossEncounter* ReboundEncounter = Boss->FindComponentByClass<URPGBossEncounter>();
	if (!TestNotNull(TEXT("rebound encounter component"), ReboundEncounter)) return false;
	TestEqual(TEXT("new component adopts broadcast generation"), ReboundEncounter->GetParticipantGeneration(), static_cast<uint64>(2));

	const FString SnapshotText = Moves->BuildEncounterParitySnapshot();
	TSharedPtr<FJsonObject> Snapshot;
	const TSharedRef<TJsonReader<>> SnapshotReader = TJsonReaderFactory<>::Create(SnapshotText);
	TestTrue(TEXT("runtime parity snapshot is valid JSON"), FJsonSerializer::Deserialize(SnapshotReader, Snapshot) && Snapshot.IsValid());
	if (Snapshot.IsValid())
	{
		TestEqual(TEXT("snapshot identifies the selected data route"), Snapshot->GetStringField(TEXT("route")), FString(TEXT("data")));
		TestEqual(TEXT("snapshot reports activation success"), Snapshot->GetObjectField(TEXT("activation"))->GetStringField(TEXT("outcome")), FString(TEXT("Activated")));
		TestEqual(TEXT("snapshot reports the exact uint64 generation"), Snapshot->GetStringField(TEXT("participant_generation")), FString(TEXT("2")));
		TestEqual(TEXT("snapshot reports both ordered participants"), Snapshot->GetArrayField(TEXT("participants")).Num(), 2);
		const TSharedPtr<FJsonObject> SelectionSnapshot = Snapshot->GetObjectField(TEXT("selection"));
		TestEqual(TEXT("snapshot retains the selection asset path"), SelectionSnapshot->GetStringField(TEXT("definition")), Definition->GetPathName());
		TestEqual(TEXT("snapshot retains the canonical manifest"), SelectionSnapshot->GetStringField(TEXT("manifest_sha256")), Definition->StableManifestHash);
	}

	// A successful rebind must have cleared the spawn-to-broadcast timeout.
	Scope.World->GetTimerManager().Tick(5.1f);
	TestTrue(TEXT("successful rebind remains active after the old timeout interval"), IsValid(CurrentBinding) && CurrentBinding->ParticipantGeneration == 2);

	ReboundEncounter->OnResetBroadcast().Broadcast(2, 1);
	TestTrue(TEXT("duplicate broadcast leaves the same binding active"), IsValid(CurrentBinding) && CurrentBinding->ParticipantGeneration == 2);
	AddExpectedError(TEXT("outcome=HardError reason=EncounterActivation.GenerationNotIncreasing"), EAutomationExpectedErrorFlags::Contains, 1);
	ReboundEncounter->OnResetBroadcast().Broadcast(1, 1);
	TestFalse(TEXT("stale broadcast fails closed and releases the active binding"), IsValid(CurrentBinding));
	Selection->ClearSelectedDefinition();
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterSelectionRebindGenerationRefusalFailsClosed,
	"OneBossFight.Binding.EncounterSelection.RebindGenerationRefusalFailsClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterSelectionRebindGenerationRefusalFailsClosed::RunTest(const FString&)
{
	FStartupActivationWorld Scope;
	if (!TestNotNull(TEXT("real game-instance test world"), Scope.World)) return false;
	URPGEncounterSelectionSubsystem* Selection = Scope.GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>();
	APawn* Boss = Scope.SpawnPackPawn(BossClassPath, FVector::ZeroVector);
	APawn* OldPlayer = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	URPGBossEncounterDefinition* Definition = MakeValidPackSelection();
	if (!TestNotNull(TEXT("selection store"), Selection) || !TestNotNull(TEXT("boss"), Boss)
		|| !TestNotNull(TEXT("initial player"), OldPlayer) || !TestNotNull(TEXT("selection definition"), Definition)) return false;
	Selection->SetSelectedDefinition(Definition);
	Scope.BeginPlay();
	URPGBossEncounter* Encounter = Boss->FindComponentByClass<URPGBossEncounter>();
	if (!TestNotNull(TEXT("reset source"), Encounter)) return false;
	AddExpectedError(TEXT("outcome=HardError reason=EncounterActivation.GenerationNotIncreasing"), EAutomationExpectedErrorFlags::Contains, 1);
	Encounter->OnResetBroadcast().Broadcast(0, 0);
	TestFalse(TEXT("stale generation refusal leaves boss disabled"), Boss->GetActorEnableCollision());
	TestFalse(TEXT("stale generation refusal publishes no active binding"), static_cast<bool>(TActorIterator<ARPGEncounterBinding>(Scope.World)));
	TestFalse(TEXT("stale generation refusal does not add the legacy boss bundle"), HasLegacyBossBundle(Boss));
	TestNotNull(TEXT("independent player setup survives refusal"), OldPlayer->FindComponentByClass<URPGDodgeTiming>());
	Selection->ClearSelectedDefinition();
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterSelectionUnsafeReleaseRetainsLeaseAndBinding,
	"OneBossFight.Binding.EncounterSelection.UnsafeReleaseRetainsLeaseAndBinding",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterSelectionUnsafeReleaseRetainsLeaseAndBinding::RunTest(const FString&)
{
	FStartupActivationWorld Scope;
	if (!TestNotNull(TEXT("real game-instance test world"), Scope.World)) return false;
	URPGEncounterSelectionSubsystem* Selection = Scope.GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>();
	URPGPlayerMovesSubsystem* Moves = Scope.World->GetSubsystem<URPGPlayerMovesSubsystem>();
	APawn* Boss = Scope.SpawnPackPawn(BossClassPath, FVector::ZeroVector);
	APawn* OldPlayer = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	URPGBossEncounterDefinition* Definition = MakeValidPackSelection();
	if (!TestNotNull(TEXT("selection store"), Selection) || !TestNotNull(TEXT("moves subsystem"), Moves)
		|| !TestNotNull(TEXT("boss"), Boss) || !TestNotNull(TEXT("initial player"), OldPlayer)
		|| !TestNotNull(TEXT("selection definition"), Definition)) return false;
	Selection->SetSelectedDefinition(Definition);
	Scope.BeginPlay();
	URPGBossEncounter* Encounter = Boss->FindComponentByClass<URPGBossEncounter>();
	if (!TestNotNull(TEXT("reset source"), Encounter)) return false;
	OldPlayer->Destroy();
	APawn* NewPlayer = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("replacement player"), NewPlayer)) return false;
	URPGBossEncounterDefinition* ChangedDefinition = MakeValidPackSelection();
	if (!TestNotNull(TEXT("changed selection definition"), ChangedDefinition)) return false;
	Selection->SetSelectedDefinition(ChangedDefinition);
	RPGBossHydrationPreparation::FRebindReleaseRefusalScope Refusal;
	AddExpectedError(TEXT("Preparation.RebindReleaseInjectedRefusal"), EAutomationExpectedErrorFlags::Contains, 1);
	Encounter->ResetForTest();
	TestTrue(TEXT("release refusal injection fired"), Refusal.Fired());
	TestFalse(TEXT("boss is disabled after unsafe teardown refusal"), Boss->GetActorEnableCollision());
	ARPGEncounterBinding* RetainedBinding = nullptr;
	for (TActorIterator<ARPGEncounterBinding> It(Scope.World); It; ++It) { RetainedBinding = *It; break; }
	TestNotNull(TEXT("unsafe release retains old binding"), RetainedBinding);
	if (RetainedBinding)
	{
		TestEqual(TEXT("retained binding keeps old generation"), RetainedBinding->ParticipantGeneration, static_cast<uint64>(1));
	}
	TSharedPtr<FJsonObject> Snapshot;
	const TSharedRef<TJsonReader<>> SnapshotReader = TJsonReaderFactory<>::Create(Moves->BuildEncounterParitySnapshot());
	TestTrue(TEXT("release refusal snapshot parses"), FJsonSerializer::Deserialize(SnapshotReader, Snapshot) && Snapshot.IsValid());
	if (Snapshot.IsValid())
	{
		const TSharedPtr<FJsonObject> Activation = Snapshot->GetObjectField(TEXT("activation"));
		TestTrue(TEXT("unsafe release retains the registered lease"), Activation->GetBoolField(TEXT("lease_held")));
		TestTrue(TEXT("unsafe release records retained binding"), Activation->GetBoolField(TEXT("binding_retained")));
	}
	TestNotNull(TEXT("independent player setup survives release refusal"), NewPlayer->FindComponentByClass<URPGDodgeTiming>());
	Selection->ClearSelectedDefinition();
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterSelectionManifestChangeWhilePendingFailsClosed,
	"OneBossFight.Binding.EncounterSelection.ManifestChangeWhilePendingFailsClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterSelectionManifestChangeWhilePendingFailsClosed::RunTest(const FString&)
{
	FStartupActivationWorld Scope;
	if (!TestNotNull(TEXT("real game-instance test world"), Scope.World)) return false;
	URPGEncounterSelectionSubsystem* Selection = Scope.GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>();
	APawn* Boss = Scope.SpawnPackPawn(BossClassPath, FVector::ZeroVector);
	APawn* OldPlayer = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	URPGBossEncounterDefinition* Definition = MakeValidPackSelection();
	if (!TestNotNull(TEXT("selection store"), Selection) || !TestNotNull(TEXT("boss"), Boss)
		|| !TestNotNull(TEXT("initial player"), OldPlayer) || !TestNotNull(TEXT("selection definition"), Definition)) return false;
	Selection->SetSelectedDefinition(Definition);
	Scope.BeginPlay();
	URPGBossEncounter* Encounter = Boss->FindComponentByClass<URPGBossEncounter>();
	if (!TestNotNull(TEXT("reset source"), Encounter)) return false;
	OldPlayer->Destroy();
	APawn* NewPlayer = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("replacement player"), NewPlayer)) return false;
	URPGBossEncounterDefinition* ChangedDefinition = MakeValidPackSelection();
	if (!TestNotNull(TEXT("changed selection definition"), ChangedDefinition)) return false;
	ChangedDefinition->EncounterInstance = Definition->EncounterInstance;
	ChangedDefinition->BossSlot = Definition->BossSlot;
	ChangedDefinition->PlayerSlot = Definition->PlayerSlot;
	ChangedDefinition->InitialBossPhase = Definition->InitialBossPhase;
	ChangedDefinition->BossDefinition = Definition->BossDefinition;
	ChangedDefinition->PlayerDefinition = Definition->PlayerDefinition;
	ChangedDefinition->StableManifestHash = FString::ChrN(64, TEXT('c'));
	Selection->SetSelectedDefinition(ChangedDefinition);
	AddExpectedError(TEXT("outcome=HardError reason=EncounterActivation.SelectionChanged"), EAutomationExpectedErrorFlags::Contains, 1);
	Encounter->ResetForTest();
	TestFalse(TEXT("manifest drift leaves boss disabled"), Boss->GetActorEnableCollision());
	TestFalse(TEXT("manifest drift does not publish a binding"), static_cast<bool>(TActorIterator<ARPGEncounterBinding>(Scope.World)));
	TestNotNull(TEXT("independent player setup survives selection drift"), NewPlayer->FindComponentByClass<URPGDodgeTiming>());
	Selection->ClearSelectedDefinition();
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterSelectionSecondRespawnBeforeBroadcastFailsClosed,
	"OneBossFight.Binding.EncounterSelection.SecondRespawnBeforeBroadcastFailsClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterSelectionSecondRespawnBeforeBroadcastFailsClosed::RunTest(const FString&)
{
	FStartupActivationWorld Scope;
	if (!TestNotNull(TEXT("real game-instance test world"), Scope.World)) return false;
	URPGEncounterSelectionSubsystem* Selection = Scope.GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>();
	APawn* Boss = Scope.SpawnPackPawn(BossClassPath, FVector::ZeroVector);
	APawn* OldPlayer = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	URPGBossEncounterDefinition* Definition = MakeValidPackSelection();
	if (!TestNotNull(TEXT("selection store"), Selection) || !TestNotNull(TEXT("boss"), Boss)
		|| !TestNotNull(TEXT("initial player"), OldPlayer) || !TestNotNull(TEXT("selection definition"), Definition)) return false;
	Selection->SetSelectedDefinition(Definition);
	Scope.BeginPlay();
	URPGBossEncounter* Encounter = Boss->FindComponentByClass<URPGBossEncounter>();
	if (!TestNotNull(TEXT("reset source"), Encounter)) return false;
	OldPlayer->Destroy();
	APawn* FirstRespawn = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("first respawn candidate"), FirstRespawn)) return false;
	APlayerController* SecondLocalController = Scope.SpawnAdditionalLocalPlayerController();
	if (!TestNotNull(TEXT("second local player controller"), SecondLocalController)) return false;
	SecondLocalController->Possess(FirstRespawn);
	TestTrue(TEXT("second local controller possesses the first candidate"), SecondLocalController->GetPawn() == FirstRespawn);
	AddExpectedError(TEXT("outcome=HardError reason=EncounterActivation.RebindAmbiguousPlayer"), EAutomationExpectedErrorFlags::Contains, 1);
	APawn* SecondRespawn = Scope.SpawnPackPawn(PlayerClassPath, FVector(1200.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("second respawn candidate"), SecondRespawn)) return false;
	Encounter->ResetForTest();
	TestFalse(TEXT("several locally possessed candidates disable boss collision"), Boss->GetActorEnableCollision());
	TestFalse(TEXT("ambiguous respawns leave no active binding"), static_cast<bool>(TActorIterator<ARPGEncounterBinding>(Scope.World)));
	TestFalse(TEXT("ambiguous respawns do not install the legacy bundle"), HasLegacyBossBundle(Boss));
	TestNotNull(TEXT("first respawn keeps its independent player setup"), FirstRespawn->FindComponentByClass<URPGDodgeTiming>());
	TestNotNull(TEXT("second respawn keeps its independent player setup"), SecondRespawn->FindComponentByClass<URPGDodgeTiming>());
	Selection->ClearSelectedDefinition();
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterGenerationAdvancesBeyondLegacyInt32,
	"OneBossFight.Binding.EncounterLifecycle.GenerationAdvancesBeyondLegacyInt32",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterGenerationAdvancesBeyondLegacyInt32::RunTest(const FString&)
{
	FStartupActivationWorld Scope;
	if (!TestNotNull(TEXT("real game-instance test world"), Scope.World)) return false;
	APawn* Boss = Scope.SpawnPackPawn(BossClassPath, FVector::ZeroVector);
	APawn* Player = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("pack boss"), Boss) || !TestNotNull(TEXT("pack player"), Player)) return false;
	Scope.BeginPlay();
	URPGBossEncounter* Encounter = Boss->FindComponentByClass<URPGBossEncounter>();
	if (!TestNotNull(TEXT("encounter component"), Encounter)) return false;
	Encounter->SeedLifecycleStateForTest(static_cast<uint64>(MAX_int32), 0);
	Encounter->ResetForTest();
	TestEqual(TEXT("native reset advances beyond int32"), Encounter->GetParticipantGeneration(), static_cast<uint64>(MAX_int32) + 1);
	TestEqual(TEXT("legacy Blueprint getter saturates without changing native authority"), Encounter->GetGeneration(), MAX_int32);
	TestTrue(TEXT("full-width native generation remains authoritative"), Encounter->GetParticipantGeneration() > static_cast<uint64>(Encounter->GetGeneration()));
	TestEqual(TEXT("Blueprint diagnostic exposes the exact full-width decimal token"), Encounter->GetParticipantGenerationText(), LexToString(Encounter->GetParticipantGeneration()));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterResetCountOverflowRefusesBeforeMutation,
	"OneBossFight.Binding.EncounterLifecycle.ResetCountOverflowRefusesBeforeMutation",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterResetCountOverflowRefusesBeforeMutation::RunTest(const FString&)
{
	FStartupActivationWorld Scope;
	if (!TestNotNull(TEXT("real game-instance test world"), Scope.World)) return false;
	APawn* Boss = Scope.SpawnPackPawn(BossClassPath, FVector::ZeroVector);
	APawn* Player = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("pack boss"), Boss) || !TestNotNull(TEXT("pack player"), Player)) return false;
	Scope.BeginPlay();
	URPGBossEncounter* Encounter = Boss->FindComponentByClass<URPGBossEncounter>();
	if (!TestNotNull(TEXT("encounter component"), Encounter)) return false;
	const FTransform Before = Boss->GetActorTransform();
	Encounter->SeedLifecycleStateForTest(77, MAX_int32);
	AddExpectedError(TEXT("outcome=HardError reason=EncounterActivation.ResetCountExhausted"), EAutomationExpectedErrorFlags::Contains, 1);
	Encounter->ResetForTest();
	TestEqual(TEXT("reset count remains at maximum"), Encounter->GetResetCount(), MAX_int32);
	TestEqual(TEXT("generation is unchanged on reset-count overflow"), Encounter->GetParticipantGeneration(), static_cast<uint64>(77));
	TestTrue(TEXT("overflow refusal leaves boss transform unchanged"), Boss->GetActorTransform().Equals(Before));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterSelectedRebindGenerationSequenceKeepsOneLease,
	"OneBossFight.Binding.EncounterLifecycle.SelectedRebindGenerationSequenceKeepsOneLease",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterSelectedRebindGenerationSequenceKeepsOneLease::RunTest(const FString&)
{
	FStartupActivationWorld Scope;
	if (!TestNotNull(TEXT("real game-instance test world"), Scope.World)) return false;
	URPGEncounterSelectionSubsystem* Selection = Scope.GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>();
	URPGPlayerMovesSubsystem* Moves = Scope.World->GetSubsystem<URPGPlayerMovesSubsystem>();
	URPGBossEncounterDefinition* Definition = MakeValidPackSelection();
	APawn* Boss = Scope.SpawnPackPawn(BossClassPath, FVector::ZeroVector);
	APawn* Player = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("selection store"), Selection) || !TestNotNull(TEXT("moves subsystem"), Moves)
		|| !TestNotNull(TEXT("definition"), Definition) || !TestNotNull(TEXT("boss"), Boss) || !TestNotNull(TEXT("initial player"), Player)) return false;
	Selection->SetSelectedDefinition(Definition);
	Scope.BeginPlay();
	URPGBossEncounter* Encounter = Boss->FindComponentByClass<URPGBossEncounter>();
	if (!TestNotNull(TEXT("initial encounter"), Encounter)) return false;
	FRandomStream Random(0x4A011);
	uint64 Generation = static_cast<uint64>(MAX_int32) - 4;
	int32 ResetCount = 0;
	bool bCrossedLegacyCeiling = false;
	for (int32 Index = 0; Index < 64; ++Index)
	{
		const uint64 Next = Generation + static_cast<uint64>(Random.RandRange(1, 7));
		FString Error;
		if (!TestTrue(FString::Printf(TEXT("sequence advance %d is valid"), Index), RPGEncounterGenerationRules::CanAdvance(Generation, Next, Error))) return false;
		bCrossedLegacyCeiling |= Next > static_cast<uint64>(MAX_int32);
		Player->Destroy();
		Player = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
		if (!TestNotNull(TEXT("next player candidate"), Player)) return false;
		Encounter->OnResetBroadcast().Broadcast(Next, ++ResetCount);
		ARPGEncounterBinding* Binding = nullptr;
		int32 BindingCount = 0;
		for (TActorIterator<ARPGEncounterBinding> It(Scope.World); It; ++It) { Binding = *It; ++BindingCount; }
		if (!TestEqual(FString::Printf(TEXT("sequence %d has exactly one binding"), Index), BindingCount, 1) || !TestNotNull(TEXT("active sequence binding"), Binding)) return false;
		if (!TestEqual(FString::Printf(TEXT("sequence %d preserves full-width generation"), Index), Binding->ParticipantGeneration, Next)) return false;
		Encounter = Boss->FindComponentByClass<URPGBossEncounter>();
		if (!TestNotNull(TEXT("rebound encounter component"), Encounter)) return false;
		Generation = Next;
	}
	TestTrue(TEXT("seeded runtime sequence crosses the legacy int32 limit"), bCrossedLegacyCeiling);
	TSharedPtr<FJsonObject> Snapshot;
	const TSharedRef<TJsonReader<>> SnapshotReader = TJsonReaderFactory<>::Create(Moves->BuildEncounterParitySnapshot());
	TestTrue(TEXT("last sequence snapshot parses"), FJsonSerializer::Deserialize(SnapshotReader, Snapshot) && Snapshot.IsValid());
	if (Snapshot.IsValid())
	{
		TestTrue(TEXT("runtime transaction retains its active lease"), Snapshot->GetObjectField(TEXT("activation"))->GetBoolField(TEXT("lease_held")));
		TestEqual(TEXT("snapshot emits generation as exact decimal text"), Snapshot->GetStringField(TEXT("participant_generation")), LexToString(Generation));
	}
	Selection->ClearSelectedDefinition();
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterSubsystemShutdownUnbindsPendingRebind,
	"OneBossFight.Binding.EncounterLifecycle.SubsystemShutdownUnbindsPendingRebind",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterSubsystemShutdownUnbindsPendingRebind::RunTest(const FString&)
{
	FStartupActivationWorld Scope;
	if (!TestNotNull(TEXT("real game-instance test world"), Scope.World)) return false;
	URPGEncounterSelectionSubsystem* Selection = Scope.GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>();
	URPGPlayerMovesSubsystem* Moves = Scope.World->GetSubsystem<URPGPlayerMovesSubsystem>();
	APawn* Boss = Scope.SpawnPackPawn(BossClassPath, FVector::ZeroVector);
	APawn* OldPlayer = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	URPGBossEncounterDefinition* Definition = MakeValidPackSelection();
	if (!TestNotNull(TEXT("selection store"), Selection) || !TestNotNull(TEXT("moves subsystem"), Moves)
		|| !TestNotNull(TEXT("boss"), Boss) || !TestNotNull(TEXT("initial player"), OldPlayer)
		|| !TestNotNull(TEXT("selection definition"), Definition)) return false;
	Selection->SetSelectedDefinition(Definition);
	Scope.BeginPlay();
	URPGBossEncounter* Encounter = Boss->FindComponentByClass<URPGBossEncounter>();
	if (!TestNotNull(TEXT("active reset source"), Encounter)) return false;
	OldPlayer->Destroy();
	APawn* NewPlayer = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("pending replacement player"), NewPlayer)) return false;
	TestTrue(TEXT("subsystem is bound to the reset delegate before shutdown"), Encounter->OnResetBroadcast().IsBoundToObject(Moves));
	Moves->Deinitialize();
	TestFalse(TEXT("shutdown removes the reset delegate binding"), IsValid(Encounter) && Encounter->OnResetBroadcast().IsBoundToObject(Moves));
	Scope.World->GetTimerManager().Tick(6.0f);
	TestFalse(TEXT("shutdown releases the selected binding"), static_cast<bool>(TActorIterator<ARPGEncounterBinding>(Scope.World)));
	TestNotNull(TEXT("shutdown preserves independent replacement-player setup"), NewPlayer->FindComponentByClass<URPGDodgeTiming>());
	Selection->ClearSelectedDefinition();
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterRepeatedSubsystemRestartPreservesPlayerSetup,
	"OneBossFight.Binding.EncounterLifecycle.RepeatedSubsystemRestartPreservesPlayerSetup",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterRepeatedSubsystemRestartPreservesPlayerSetup::RunTest(const FString&)
{
	for (int32 Cycle = 0; Cycle < 3; ++Cycle)
	{
		FStartupActivationWorld Scope;
		if (!TestNotNull(FString::Printf(TEXT("cycle %d world"), Cycle), Scope.World)) return false;
		URPGEncounterSelectionSubsystem* Selection = Scope.GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>();
		URPGPlayerMovesSubsystem* Moves = Scope.World->GetSubsystem<URPGPlayerMovesSubsystem>();
		URPGBossEncounterDefinition* Definition = MakeValidPackSelection();
		APawn* Boss = Scope.SpawnPackPawn(BossClassPath, FVector::ZeroVector);
		APawn* Player = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
		if (!TestNotNull(TEXT("selection store"), Selection) || !TestNotNull(TEXT("moves subsystem"), Moves)
			|| !TestNotNull(TEXT("definition"), Definition) || !TestNotNull(TEXT("boss"), Boss) || !TestNotNull(TEXT("player"), Player)) return false;
		Selection->SetSelectedDefinition(Definition);
		Scope.BeginPlay();
		URPGDodgeTiming* IndependentPlayerComponent = Player->FindComponentByClass<URPGDodgeTiming>();
		if (!TestNotNull(TEXT("independent dodge component"), IndependentPlayerComponent)) return false;
		TestTrue(TEXT("cycle owns one live selected binding"), static_cast<bool>(TActorIterator<ARPGEncounterBinding>(Scope.World)));
		Moves->Deinitialize();
		TActorIterator<ARPGEncounterBinding> Bindings(Scope.World);
		TestFalse(TEXT("shutdown releases selected binding"), static_cast<bool>(Bindings));
		TestTrue(TEXT("shutdown leaves independent player component alive and registered"), IsValid(IndependentPlayerComponent) && IndependentPlayerComponent->IsRegistered());
		Selection->ClearSelectedDefinition();
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterSelectionRebindWaitsForDelayedPossession,
	"OneBossFight.Binding.EncounterSelection.RebindWaitsForDelayedPossession",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterSelectionRebindWaitsForDelayedPossession::RunTest(const FString&)
{
	FStartupActivationWorld Scope;
	if (!TestNotNull(TEXT("real game-instance test world"), Scope.World)) return false;
	URPGEncounterSelectionSubsystem* Selection = Scope.GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>();
	APawn* Boss = Scope.SpawnPackPawn(BossClassPath, FVector::ZeroVector);
	APawn* OldPlayer = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("selection store"), Selection) || !TestNotNull(TEXT("pack boss"), Boss) || !TestNotNull(TEXT("initial pack player"), OldPlayer)) return false;
	URPGBossEncounterDefinition* Definition = MakeValidPackSelection();
	if (!TestNotNull(TEXT("selected definition"), Definition)) return false;
	Selection->SetSelectedDefinition(Definition);
	Scope.BeginPlay();
	OldPlayer->Destroy();
	URPGBossEncounter* Encounter = Boss->FindComponentByClass<URPGBossEncounter>();
	URPGPlayerMovesSubsystem* Moves = Scope.World->GetSubsystem<URPGPlayerMovesSubsystem>();
	if (!TestNotNull(TEXT("reset source"), Encounter) || !TestNotNull(TEXT("moves subsystem"), Moves)) return false;
	Encounter->ResetForTest(); // reset broadcast arrives while the controller has no pawn
	FString PendingOutcome, PendingReason;
	bool bPendingBindingRetained = false;
	TestTrue(TEXT("pending snapshot parses"), ReadActivationSnapshot(*Moves, PendingOutcome, PendingReason, bPendingBindingRetained));
	TestTrue(TEXT("pending rebind retains the active binding while no pawn is possessed"), PendingOutcome == TEXT("Activated") && bPendingBindingRetained);
	TestTrue(TEXT("pending rebind keeps boss collision active"), Boss->GetActorEnableCollision());
	for (int32 Tick = 0; Tick < 3; ++Tick)
	{
		Scope.World->Tick(LEVELTICK_All, 1.f / 60.f);
		++GFrameCounter;
	}
	UClass* PlayerClass = LoadClass<APawn>(nullptr, PlayerClassPath);
	if (!TestNotNull(TEXT("pack player class"), PlayerClass)) return false;
	APawn* NewPlayer = Scope.World->SpawnActor<APawn>(PlayerClass, FVector(1000.f, 0.f, 0.f), FRotator::ZeroRotator);
	if (!TestNotNull(TEXT("unpossessed replacement player"), NewPlayer)) return false;
	for (int32 Tick = 0; Tick < 3; ++Tick)
	{
		Scope.World->Tick(LEVELTICK_All, 1.f / 60.f);
		++GFrameCounter;
	}
	if (!TestTrue(TEXT("local controller possesses delayed replacement"), Scope.PossessPlayer(NewPlayer))) return false;
	APlayerController* Controller = nullptr;
	for (FConstPlayerControllerIterator It = Scope.World->GetPlayerControllerIterator(); It; ++It)
	{
		APlayerController* CandidateController = It->Get();
		if (IsValid(CandidateController) && CandidateController->IsLocalController() && CandidateController->GetPawn() == NewPlayer)
		{
			Controller = CandidateController;
			break;
		}
	}
	TestNotNull(TEXT("possessing local controller"), Controller);
	for (int32 Tick = 0; Tick < 3; ++Tick)
	{
		Scope.World->Tick(LEVELTICK_All, 1.f / 60.f);
		++GFrameCounter;
	}
	FString Outcome, Reason;
	bool bBindingRetained = false;
	TestTrue(TEXT("post-possession snapshot parses"), ReadActivationSnapshot(*Moves, Outcome, Reason, bBindingRetained));
	TestTrue(TEXT("delayed possession completes rebind without HardError"), Outcome == TEXT("Activated") && Reason.IsEmpty() && bBindingRetained);
	ARPGEncounterBinding* NewBinding = nullptr;
	for (TActorIterator<ARPGEncounterBinding> It(Scope.World); It; ++It) { NewBinding = *It; break; }
	TestNotNull(TEXT("new selected binding after possession"), NewBinding);
	TestTrue(TEXT("new binding uses the possessed replacement pawn"), NewBinding && NewBinding->Participants.ContainsByPredicate([NewPlayer](const FRPGPlacedParticipantBinding& Participant) { return Participant.Slot == FName(TEXT("Player")) && Participant.Actor.Get() == NewPlayer; }));
	Selection->ClearSelectedDefinition();
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterSelectionRebindDuplicatePlayerFailsClosed,
	"OneBossFight.Binding.EncounterSelection.RebindDuplicatePlayerFailsClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterSelectionRebindDuplicatePlayerFailsClosed::RunTest(const FString&)
{
	FStartupActivationWorld Scope;
	if (!TestNotNull(TEXT("real game-instance test world"), Scope.World)) return false;
	URPGEncounterSelectionSubsystem* Selection = Scope.GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>();
	URPGBossEncounterDefinition* Definition = MakeValidPackSelection();
	APawn* Boss = Scope.SpawnPackPawn(BossClassPath, FVector::ZeroVector);
	APawn* OldPlayer = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("selection store"), Selection) || !TestNotNull(TEXT("definition"), Definition)
		|| !TestNotNull(TEXT("boss"), Boss) || !TestNotNull(TEXT("initial player"), OldPlayer)) return false;
	Selection->SetSelectedDefinition(Definition);
	Scope.BeginPlay();
	URPGBossEncounter* Encounter = Boss->FindComponentByClass<URPGBossEncounter>();
	if (!TestNotNull(TEXT("reset source"), Encounter)) return false;
	OldPlayer->Destroy();
	APawn* Candidate = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("replacement candidate"), Candidate)) return false;
	APlayerController* SecondLocalController = Scope.SpawnAdditionalLocalPlayerController();
	if (!TestNotNull(TEXT("second local player controller"), SecondLocalController)) return false;
	SecondLocalController->Possess(Candidate);
	TestTrue(TEXT("second local controller possesses the candidate"), SecondLocalController->GetPawn() == Candidate);
	APawn* Duplicate = Scope.SpawnPackPawn(PlayerClassPath, FVector(1100.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("duplicate player"), Duplicate)) return false;
	AddExpectedError(TEXT("outcome=HardError reason=EncounterActivation.RebindAmbiguousPlayer"), EAutomationExpectedErrorFlags::Contains, 1);
	Encounter->ResetForTest();
	TestFalse(TEXT("multiple authoritative players disable boss collision"), Boss->GetActorEnableCollision());
	TestFalse(TEXT("multiple authoritative players leave no active binding"), static_cast<bool>(TActorIterator<ARPGEncounterBinding>(Scope.World)));
	TestNotNull(TEXT("candidate player setup survives refusal"), Candidate->FindComponentByClass<URPGDodgeTiming>());
	TestNotNull(TEXT("other player setup survives refusal"), Duplicate->FindComponentByClass<URPGDodgeTiming>());
	Selection->ClearSelectedDefinition();
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterSelectionRebindIgnoresDeadUnpossessedPlayer,
	"OneBossFight.Binding.EncounterSelection.RebindIgnoresDeadUnpossessedPlayer",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterSelectionRebindIgnoresDeadUnpossessedPlayer::RunTest(const FString&)
{
	FStartupActivationWorld Scope;
	if (!TestNotNull(TEXT("real game-instance test world"), Scope.World)) return false;
	URPGEncounterSelectionSubsystem* Selection = Scope.GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>();
	URPGBossEncounterDefinition* Definition = MakeValidPackSelection();
	APawn* Boss = Scope.SpawnPackPawn(BossClassPath, FVector::ZeroVector);
	APawn* DeadPlayer = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("selection store"), Selection) || !TestNotNull(TEXT("definition"), Definition)
		|| !TestNotNull(TEXT("boss"), Boss) || !TestNotNull(TEXT("initial player"), DeadPlayer)) return false;
	Selection->SetSelectedDefinition(Definition);
	Scope.BeginPlay();
	URPGBossEncounter* Encounter = Boss->FindComponentByClass<URPGBossEncounter>();
	if (!TestNotNull(TEXT("active encounter"), Encounter)) return false;
	if (!TestTrue(TEXT("old pawn receives the pack dead status tag"), AddDeadStatusTag(DeadPlayer))) return false;
	TestTrue(TEXT("old dead pawn remains in the world"), IsValid(DeadPlayer) && !DeadPlayer->IsActorBeingDestroyed());
	APawn* NewPlayer = Scope.SpawnPackPawn(PlayerClassPath, FVector(1200.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("possessed replacement player"), NewPlayer)) return false;
	TestTrue(TEXT("local controller possesses the replacement"), Scope.LocalPlayerController.IsValid() && Scope.LocalPlayerController->GetPawn() == NewPlayer);
	Encounter->ResetForTest();
	ARPGEncounterBinding* Binding = nullptr;
	int32 BindingCount = 0;
	for (TActorIterator<ARPGEncounterBinding> It(Scope.World); It; ++It) { Binding = *It; ++BindingCount; }
	TestEqual(TEXT("successful corpse-filtered rebind keeps one binding"), BindingCount, 1);
	if (TestNotNull(TEXT("rebound selection"), Binding))
	{
		const bool bSelectedNewPlayer = Binding->Participants.ContainsByPredicate([&](const FRPGPlacedParticipantBinding& Participant)
		{
			return Participant.Slot == Definition->PlayerSlot && Participant.Actor.Get() == NewPlayer;
		});
		TestTrue(TEXT("binding identifies the locally possessed live pawn"), bSelectedNewPlayer);
	}
	TestTrue(TEXT("boss lease keeps the original encounter component"), Boss->FindComponentByClass<URPGBossEncounter>() == Encounter);
	TestTrue(TEXT("dead corpse remains excluded without being destroyed"), IsValid(DeadPlayer) && !DeadPlayer->IsActorBeingDestroyed());
	Selection->ClearSelectedDefinition();
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterSelectionRebindRefusesDeadBoss,
	"OneBossFight.Binding.EncounterSelection.RebindRefusesDeadBoss",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterSelectionRebindRefusesDeadBoss::RunTest(const FString&)
{
	FStartupActivationWorld Scope;
	if (!TestNotNull(TEXT("real game-instance test world"), Scope.World)) return false;
	URPGEncounterSelectionSubsystem* Selection = Scope.GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>();
	URPGBossEncounterDefinition* Definition = MakeValidPackSelection();
	APawn* Boss = Scope.SpawnPackPawn(BossClassPath, FVector::ZeroVector);
	APawn* OldPlayer = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("selection store"), Selection) || !TestNotNull(TEXT("definition"), Definition)
		|| !TestNotNull(TEXT("boss"), Boss) || !TestNotNull(TEXT("initial player"), OldPlayer)) return false;
	Selection->SetSelectedDefinition(Definition);
	Scope.BeginPlay();
	URPGBossEncounter* Encounter = Boss->FindComponentByClass<URPGBossEncounter>();
	if (!TestNotNull(TEXT("reset source"), Encounter)) return false;
	OldPlayer->Destroy();
	APawn* NewPlayer = Scope.SpawnPackPawn(PlayerClassPath, FVector(1200.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("replacement player"), NewPlayer)) return false;
	if (!TestTrue(TEXT("boss receives the pack dead status tag"), AddDeadStatusTag(Boss))) return false;
	AddExpectedError(TEXT("Preparation.RebindRetagBossDead"), EAutomationExpectedErrorFlags::Contains, 1);   // pattern is a regex: "[slot=Boss]" would be a character class
	Encounter->ResetForTest();
	TestFalse(TEXT("dead boss is disabled after refused rebind"), Boss->GetActorEnableCollision());
	TestFalse(TEXT("dead boss refusal removes the transient binding"), static_cast<bool>(TActorIterator<ARPGEncounterBinding>(Scope.World)));
	TestNotNull(TEXT("replacement player setup survives dead-boss refusal"), NewPlayer->FindComponentByClass<URPGDodgeTiming>());
	Selection->ClearSelectedDefinition();
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterSelectionRebindTimeoutFailsClosed,
	"OneBossFight.Binding.EncounterSelection.RebindTimeoutFailsClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterSelectionRebindTimeoutFailsClosed::RunTest(const FString&)
{
	FStartupActivationWorld Scope;
	if (!TestNotNull(TEXT("real game-instance test world"), Scope.World)) return false;
	URPGEncounterSelectionSubsystem* Selection = Scope.GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>();
	URPGBossEncounterDefinition* Definition = MakeValidPackSelection();
	APawn* Boss = Scope.SpawnPackPawn(BossClassPath, FVector::ZeroVector);
	APawn* OldPlayer = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("selection store"), Selection) || !TestNotNull(TEXT("definition"), Definition)
		|| !TestNotNull(TEXT("boss"), Boss) || !TestNotNull(TEXT("initial player"), OldPlayer)) return false;
	Selection->SetSelectedDefinition(Definition);
	Scope.BeginPlay();
	URPGBossEncounter* Encounter = Boss->FindComponentByClass<URPGBossEncounter>();
	if (!TestNotNull(TEXT("reset source"), Encounter)) return false;
	OldPlayer->Destroy();
	URPGPlayerMovesSubsystem* Moves = Scope.World->GetSubsystem<URPGPlayerMovesSubsystem>();
	if (!TestNotNull(TEXT("moves subsystem"), Moves)) return false;
	Encounter->ResetForTest();
	AddExpectedError(TEXT("outcome=HardError reason=EncounterActivation.RebindTimeout"), EAutomationExpectedErrorFlags::Contains, 1);
	for (int32 Tick = 0; Tick < 19; ++Tick)
	{
		Scope.World->Tick(LEVELTICK_All, 0.25f);
		++GFrameCounter;
	}
	FString PendingOutcome, PendingReason;
	bool bPendingBindingRetained = false;
	TestTrue(TEXT("pre-timeout snapshot parses"), ReadActivationSnapshot(*Moves, PendingOutcome, PendingReason, bPendingBindingRetained));
	TestTrue(TEXT("before five seconds, no pawn means the old binding and boss remain active"), bPendingBindingRetained
		&& Boss->GetActorEnableCollision() && static_cast<bool>(TActorIterator<ARPGEncounterBinding>(Scope.World)));
	for (int32 Tick = 0; Tick < 3; ++Tick)
	{
		Scope.World->Tick(LEVELTICK_All, 0.25f);
		++GFrameCounter;
	}
	FString Outcome, Reason;
	bool bBindingRetained = true;
	TestTrue(TEXT("timeout snapshot parses"), ReadActivationSnapshot(*Moves, Outcome, Reason, bBindingRetained));
	TestTrue(TEXT("a pawn that never arrives times out and releases the selected activation"), Outcome == TEXT("HardError") && Reason == TEXT("EncounterActivation.RebindTimeout")
		&& !bBindingRetained && !Boss->GetActorEnableCollision() && !static_cast<bool>(TActorIterator<ARPGEncounterBinding>(Scope.World)));
	Selection->ClearSelectedDefinition();
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterSelectionRebindCensusFailureFailsClosed,
	"OneBossFight.Binding.EncounterSelection.RebindCensusFailureFailsClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterSelectionRebindCensusFailureFailsClosed::RunTest(const FString&)
{
	FStartupActivationWorld Scope;
	if (!TestNotNull(TEXT("real game-instance test world"), Scope.World)) return false;
	URPGEncounterSelectionSubsystem* Selection = Scope.GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>();
	URPGPlayerMovesSubsystem* Moves = Scope.World->GetSubsystem<URPGPlayerMovesSubsystem>();
	URPGBossEncounterDefinition* Definition = MakeValidPackSelection();
	APawn* Boss = Scope.SpawnPackPawn(BossClassPath, FVector::ZeroVector);
	APawn* OldPlayer = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("selection store"), Selection) || !TestNotNull(TEXT("moves subsystem"), Moves)
		|| !TestNotNull(TEXT("definition"), Definition) || !TestNotNull(TEXT("boss"), Boss)
		|| !TestNotNull(TEXT("initial player"), OldPlayer)) return false;
	Selection->SetSelectedDefinition(Definition);
	Scope.BeginPlay();
	URPGBossEncounter* Encounter = Boss->FindComponentByClass<URPGBossEncounter>();
	if (!TestNotNull(TEXT("reset source"), Encounter)) return false;
	OldPlayer->Destroy();
	APawn* FirstCandidate = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("first replacement candidate"), FirstCandidate)) return false;
	APlayerController* SecondLocalController = Scope.SpawnAdditionalLocalPlayerController();
	if (!TestNotNull(TEXT("second local player controller"), SecondLocalController)) return false;
	SecondLocalController->Possess(FirstCandidate);
	TestTrue(TEXT("second local controller possesses the first candidate"), SecondLocalController->GetPawn() == FirstCandidate);
	APawn* SecondCandidate = Scope.SpawnPackPawn(PlayerClassPath, FVector(1200.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("second replacement candidate"), SecondCandidate)) return false;
	AddExpectedError(TEXT("outcome=HardError reason=EncounterActivation.RebindAmbiguousPlayer"), EAutomationExpectedErrorFlags::Contains, 1);
	Encounter->ResetForTest();
	TestFalse(TEXT("ambiguous census disables boss collision"), Boss->GetActorEnableCollision());
	TestFalse(TEXT("ambiguous census does not retain an active binding"), static_cast<bool>(TActorIterator<ARPGEncounterBinding>(Scope.World)));
	TestFalse(TEXT("ambiguous census does not add the legacy boss bundle"), HasLegacyBossBundle(Boss));
	TestNotNull(TEXT("first candidate player setup remains"), FirstCandidate->FindComponentByClass<URPGDodgeTiming>());
	TestNotNull(TEXT("second candidate player setup remains"), SecondCandidate->FindComponentByClass<URPGDodgeTiming>());
	TSharedPtr<FJsonObject> Snapshot;
	const TSharedRef<TJsonReader<>> SnapshotReader = TJsonReaderFactory<>::Create(Moves->BuildEncounterParitySnapshot());
	TestTrue(TEXT("census refusal produces a parseable runtime snapshot"), FJsonSerializer::Deserialize(SnapshotReader, Snapshot) && Snapshot.IsValid());
	if (Snapshot.IsValid())
	{
		const TSharedPtr<FJsonObject> Activation = Snapshot->GetObjectField(TEXT("activation"));
		TestEqual(TEXT("snapshot captures the census refusal"), Activation->GetStringField(TEXT("outcome")), FString(TEXT("HardError")));
		TestTrue(TEXT("snapshot retains the exact refusal token"), Activation->GetStringField(TEXT("reason")).Contains(TEXT("RebindAmbiguousPlayer")));
		const TSharedPtr<FJsonObject> Census = Snapshot->GetObjectField(TEXT("components"));
		TestTrue(TEXT("refusal census retains independent player setup"),
			Census->GetArrayField(TEXT("player")).ContainsByPredicate([](const TSharedPtr<FJsonValue>& Value)
			{
				return Value.IsValid() && Value->AsString().Contains(TEXT("RPGDodgeTiming"));
			}));
	}
	Selection->ClearSelectedDefinition();
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterSelectionMalformedRecordStartupFailsClosed,
	"OneBossFight.Binding.EncounterSelection.MalformedRecordStartupFailsClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterSelectionMalformedRecordStartupFailsClosed::RunTest(const FString&)
{
	FStartupActivationWorld Scope;
	if (!TestNotNull(TEXT("real game-instance test world"), Scope.World)) return false;
	URPGEncounterSelectionSubsystem* Selection = Scope.GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>();
	if (!TestNotNull(TEXT("selection store"), Selection)) return false;
	URPGBossEncounterDefinition* Encounter = MakeValidPackSelection();
	if (!TestNotNull(TEXT("typed selection fixture"), Encounter)) return false;
	Encounter->StableManifestHash = FString::ChrN(64, TEXT('a'));
	Encounter->StableManifestHash[31] = TEXT('z');
	Selection->SetSelectedDefinition(Encounter);
	APawn* Boss = Scope.SpawnPackPawn(BossClassPath, FVector::ZeroVector);
	APawn* Player = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("pack boss"), Boss) || !TestNotNull(TEXT("pack player"), Player)) return false;

	AddExpectedError(TEXT("outcome=HardError reason=EncounterDefinition.ManifestShape"), EAutomationExpectedErrorFlags::Contains, 1);
	// Check the subsystem's immediate refusal state before actor BeginPlay can independently enable default ticks.
	Scope.BeginSubsystemsOnly();
	TestEqual(TEXT("startup stores the stable manifest refusal"), Selection->GetSelectionDiagnostic(), FString(TEXT("EncounterDefinition.ManifestShape")));
	TestFalse(TEXT("refused selected startup disables the boss"), Boss->IsActorTickEnabled());
	TestFalse(TEXT("refused selected startup disables boss collision"), Boss->GetActorEnableCollision());
	TestFalse(TEXT("refused selected startup does not attach the legacy boss bundle"), HasLegacyBossBundle(Boss));
	TestNotNull(TEXT("player-only setup remains on the selected player"), Player->FindComponentByClass<URPGDodgeTiming>());
	TestNotNull(TEXT("player footsteps survive selected startup refusal"), Player->FindComponentByClass<URPGFootsteps>());
	TActorIterator<ARPGEncounterBinding> Bindings(Scope.World);
	TestFalse(TEXT("malformed record leaves no transient binding"), static_cast<bool>(Bindings));
	Selection->ClearSelectedDefinition();
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterSelectionEmptyCensus,
	"OneBossFight.Binding.EncounterSelection.EmptyCensusFailsClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterSelectionEmptyCensus::RunTest(const FString&)
{
	FStartupActivationWorld Scope;
	if (!TestNotNull(TEXT("real game-instance test world"), Scope.World)) return false;
	URPGEncounterSelectionSubsystem* Selection = Scope.GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>();
	URPGPlayerMovesSubsystem* Moves = Scope.World->GetSubsystem<URPGPlayerMovesSubsystem>();
	if (!TestNotNull(TEXT("game-instance selection store"), Selection) || !TestNotNull(TEXT("world moves subsystem"), Moves)) return false;
	URPGBossEncounterDefinition* Encounter = Scope.MakeSelection();
	if (!TestNotNull(TEXT("transient selection record"), Encounter)) return false;
	Selection->SetSelectedDefinition(Encounter);
	AddExpectedError(TEXT("outcome=HardError reason=EncounterSelection.Census"), EAutomationExpectedErrorFlags::Contains, 1);
	Moves->OnWorldBeginPlay(*Scope.World);
	TestEqual(TEXT("selection store reports census refusal"), Selection->GetSelectionDiagnostic(), FString(TEXT("EncounterSelection.Census")));
	TActorIterator<ARPGEncounterBinding> Bindings(Scope.World);
	TestFalse(TEXT("failed census leaves no transient binding"), static_cast<bool>(Bindings));   // TActorIterator has only an explicit bool conversion
	TestTrue(TEXT("no pack boss exists to receive legacy bundle"), !HasLegacyBossBundle(nullptr));
	Selection->ClearSelectedDefinition();
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterSelectionThreadAndWorldRefusal,
	"OneBossFight.Binding.EncounterSelection.ThreadAndWorldStateRefuseBeforeResolution",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterSelectionThreadAndWorldRefusal::RunTest(const FString&)
{
	FStartupActivationWorld Scope;
	FStartupActivationWorld ForeignScope;
	if (!TestNotNull(TEXT("selection-owner game world"), Scope.World) || !TestNotNull(TEXT("foreign game world"), ForeignScope.World)) return false;
	URPGEncounterSelectionSubsystem* Selection = Scope.GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>();
	if (!TestNotNull(TEXT("game-instance selection store"), Selection)) return false;
	FString SeedDiagnostic;
	Selection->ResolveSelectedDefinition(SeedDiagnostic);
	TestEqual(TEXT("fixture seeds an absent-selection diagnostic"), Selection->GetSelectionDiagnostic(), FString(TEXT("EncounterSelection.Absent")));

	ARPGEncounterBinding* Binding = nullptr;
	TArray<RPGBossWorldInputCompiler::FSelection> Selections;
	FString Error;
	const bool bOffThreadBuilt = Async(EAsyncExecution::ThreadPool, [&Selection, &Scope, &Binding, &Selections, &Error]()
	{
		return Selection->BuildWorldBinding(*Scope.World, Binding, Selections, Error);
	}).Get();
	TestFalse(TEXT("off-thread selection request refuses before world access"), bOffThreadBuilt);
	TestEqual(TEXT("off-thread selection has its exact refusal token"), Error, FString(TEXT("EncounterSelection.NotGameThread")));
	TestEqual(TEXT("off-thread refusal replaces the old diagnostic safely"), Selection->GetSelectionDiagnostic(), FString(TEXT("EncounterSelection.NotGameThread")));
	TestNull(TEXT("off-thread refusal creates no binding"), Binding);

	Error.Reset();
	TestFalse(TEXT("a game world owned by another game instance is refused"), Selection->BuildWorldBinding(*ForeignScope.World, Binding, Selections, Error));
	TestEqual(TEXT("foreign world has its exact refusal token"), Error, FString(TEXT("EncounterSelection.WorldState")));
	TestEqual(TEXT("foreign-world refusal replaces the diagnostic"), Selection->GetSelectionDiagnostic(), FString(TEXT("EncounterSelection.WorldState")));
	TestNull(TEXT("foreign-world refusal creates no binding"), Binding);
	TestTrue(TEXT("foreign-world refusal publishes no participant selections"), Selections.IsEmpty());
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterSelectionRejectsAlreadyBegunParticipants,
	"OneBossFight.Binding.EncounterSelection.AlreadyBegunActorsRefusedBeforeBinding",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterSelectionRejectsAlreadyBegunParticipants::RunTest(const FString&)
{
	FStartupActivationWorld Scope;
	if (!TestNotNull(TEXT("real game-instance test world"), Scope.World)) return false;
	URPGEncounterSelectionSubsystem* Selection = Scope.GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>();
	URPGBossEncounterDefinition* Definition = MakeValidPackSelection();
	APawn* Boss = Scope.SpawnPackPawn(BossClassPath, FVector::ZeroVector);
	APawn* Player = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("selection store"), Selection) || !TestNotNull(TEXT("definition"), Definition)
		|| !TestNotNull(TEXT("boss participant"), Boss) || !TestNotNull(TEXT("player participant"), Player)) return false;
	Selection->SetSelectedDefinition(Definition);
	Boss->DispatchBeginPlay();
	Player->DispatchBeginPlay();
	ARPGEncounterBinding* Binding = nullptr;
	TArray<RPGBossWorldInputCompiler::FSelection> Selections;
	FString Error;
	TestFalse(TEXT("strict initial compiler refuses actors that already began"), Selection->BuildWorldBinding(*Scope.World, Binding, Selections, Error));
	TestEqual(TEXT("begun actor refusal is stable"), Error, FString(TEXT("EncounterSelection.ActorState")));
	TestNull(TEXT("begun actor refusal publishes no binding"), Binding);
	TActorIterator<ARPGEncounterBinding> Bindings(Scope.World);
	TestFalse(TEXT("begun actor refusal leaves no binding actor"), static_cast<bool>(Bindings));
	Selection->ClearSelectedDefinition();
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterSelectionBuildsOnlyMatchingPhase,
	"OneBossFight.Binding.EncounterSelection.BindingRequiresDefinedPhase",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterSelectionBuildsOnlyMatchingPhase::RunTest(const FString&)
{
	FStartupActivationWorld Scope;
	if (!TestNotNull(TEXT("real game-instance test world"), Scope.World)) return false;
	URPGEncounterSelectionSubsystem* Selection = Scope.GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>();
	if (!TestNotNull(TEXT("game-instance selection store"), Selection)) return false;
	URPGBossEncounterDefinition* Encounter = Scope.MakeSelection();
	if (!TestNotNull(TEXT("typed selection record"), Encounter)) return false;
	Selection->SetSelectedDefinition(Encounter);
	APawn* Boss = Scope.SpawnPackPawn(BossClassPath, FVector::ZeroVector);
	APawn* Player = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("pack boss"), Boss) || !TestNotNull(TEXT("pack player"), Player)) return false;
	TestNotNull(TEXT("selected startup retains player footsteps"), Player->FindComponentByClass<URPGFootsteps>());

	ARPGEncounterBinding* Binding = nullptr;
	TArray<RPGBossWorldInputCompiler::FSelection> Selections;
	FString Error;
	TestTrue(TEXT("a phase declared by the selected boss definition builds a transient binding"), Selection->BuildWorldBinding(*Scope.World, Binding, Selections, Error));
	if (!TestNotNull(TEXT("transient encounter binding"), Binding)) return false;
	TestEqual(TEXT("boss phase is explicitly selected"), Selections[0].SelectedPhaseId, FName(TEXT("PhaseOne")));
	Binding->Destroy();

	Encounter->InitialBossPhase = TEXT("MissingPhase");
	Binding = nullptr;
	TestFalse(TEXT("an undefined selected phase is refused before binding spawn"), Selection->BuildWorldBinding(*Scope.World, Binding, Selections, Error));
	TestEqual(TEXT("undefined phase has a stable refusal token"), Error, FString(TEXT("EncounterSelection.Phase")));
	TestNull(TEXT("phase refusal creates no partial binding"), Binding);
	TestFalse(TEXT("selected-mode phase refusal does not attach the legacy boss bundle"), HasLegacyBossBundle(Boss));

	Encounter->InitialBossPhase = TEXT("PhaseOne");
	Encounter->StableManifestHash = FString::ChrN(64, TEXT('a'));
	Encounter->StableManifestHash[31] = TEXT('z');
	Binding = nullptr;
	TestFalse(TEXT("invalid manifest alphabet is refused before binding spawn"), Selection->BuildWorldBinding(*Scope.World, Binding, Selections, Error));
	TestEqual(TEXT("manifest refusal has a stable token"), Error, FString(TEXT("EncounterDefinition.ManifestShape")));
	TestNull(TEXT("manifest refusal creates no partial binding"), Binding);

	Encounter->StableManifestHash = FString::ChrN(64, TEXT('b'));
	Encounter->BossDefinition = TSoftObjectPtr<URPGBossDefinition>(FSoftObjectPath(TEXT("/Game/DoesNotExist/DA_MissingBoss.DA_MissingBoss")));
	Binding = nullptr;
	TestFalse(TEXT("an unresolved boss definition is refused"), Selection->BuildWorldBinding(*Scope.World, Binding, Selections, Error));
	TestEqual(TEXT("unresolved definition has a stable refusal token"), Error, FString(TEXT("EncounterSelection.DefinitionLoad")));
	TestNull(TEXT("unresolved definition creates no partial binding"), Binding);
	Selection->ClearSelectedDefinition();
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterSelectionBindingsAreWorldScoped,
	"OneBossFight.Binding.EncounterSelection.GameInstancesCannotShareBindings",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterSelectionBindingsAreWorldScoped::RunTest(const FString&)
{
	FStartupActivationWorld First;
	FStartupActivationWorld Second;
	if (!TestNotNull(TEXT("first world"), First.World) || !TestNotNull(TEXT("second world"), Second.World)) return false;
	const auto FirstEpoch = RPGCombatRegistry::ForWorld(First.World);
	const auto SecondEpoch = RPGCombatRegistry::ForWorld(Second.World);
	if (!TestTrue(TEXT("both game instances publish their own catalog epochs"), FirstEpoch.IsValid() && SecondEpoch.IsValid())) return false;
	TestTrue(TEXT("game instances publish distinct epoch identities"), FirstEpoch.Get() != SecondEpoch.Get());
	URPGEncounterSelectionSubsystem* FirstStore = First.GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>();
	URPGEncounterSelectionSubsystem* SecondStore = Second.GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>();
	if (!TestNotNull(TEXT("first selection store"), FirstStore) || !TestNotNull(TEXT("second selection store"), SecondStore)) return false;
	URPGBossEncounterDefinition* FirstDefinition = First.MakeSelection();
	URPGBossEncounterDefinition* SecondDefinition = Second.MakeSelection();
	if (!TestNotNull(TEXT("first selection record"), FirstDefinition) || !TestNotNull(TEXT("second selection record"), SecondDefinition)) return false;
	FirstStore->SetSelectedDefinition(FirstDefinition);
	SecondStore->SetSelectedDefinition(SecondDefinition);
	APawn* FirstBoss = First.SpawnPackPawn(BossClassPath, FVector::ZeroVector);
	APawn* FirstPlayer = First.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	APawn* SecondBoss = Second.SpawnPackPawn(BossClassPath, FVector::ZeroVector);
	APawn* SecondPlayer = Second.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("first boss"), FirstBoss) || !TestNotNull(TEXT("first player"), FirstPlayer)
		|| !TestNotNull(TEXT("second boss"), SecondBoss) || !TestNotNull(TEXT("second player"), SecondPlayer)) return false;
	ARPGEncounterBinding* FirstBinding = nullptr;
	ARPGEncounterBinding* SecondBinding = nullptr;
	TArray<RPGBossWorldInputCompiler::FSelection> FirstSelections;
	TArray<RPGBossWorldInputCompiler::FSelection> SecondSelections;
	FString Error;
	TestTrue(TEXT("first world builds its own binding"), FirstStore->BuildWorldBinding(*First.World, FirstBinding, FirstSelections, Error));
	TestTrue(TEXT("second world builds its own binding"), SecondStore->BuildWorldBinding(*Second.World, SecondBinding, SecondSelections, Error));
	if (!TestNotNull(TEXT("first binding"), FirstBinding) || !TestNotNull(TEXT("second binding"), SecondBinding)) return false;
	TestTrue(TEXT("each binding remains in its originating world"), FirstBinding->GetWorld() == First.World && SecondBinding->GetWorld() == Second.World);
	FRPGHydrationPreflightInput Compiled;
	const FRPGHydrationResult CrossWorld = RPGBossWorldInputCompiler::CompileWorldInput(Second.World, FirstBinding, FirstSelections, FirstDefinition->StableManifestHash, Compiled);
	TestFalse(TEXT("world B cannot compile world A's binding"), CrossWorld.IsReady());
	TestTrue(TEXT("cross-world refusal is exact and occurs before publication"), CrossWorld.Errors.Num() == 1 && CrossWorld.Errors[0].StartsWith(TEXT("WorldInput.InvalidBinding")) && !Compiled.ExpectedWorld.IsValid());
	FirstBinding->Destroy();
	SecondBinding->Destroy();
	FirstStore->ClearSelectedDefinition();
	SecondStore->ClearSelectedDefinition();
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterSelectionUnavailableEpochFailsClosed,
	"OneBossFight.Binding.EncounterSelection.UnavailableCatalogEpochFailsClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterSelectionUnavailableEpochFailsClosed::RunTest(const FString&)
{
	FStartupActivationWorld Scope;
	if (!TestNotNull(TEXT("real game-instance test world"), Scope.World)) return false;
	URPGEncounterSelectionSubsystem* Selection = Scope.GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>();
	URPGPlayerMovesSubsystem* Moves = Scope.World->GetSubsystem<URPGPlayerMovesSubsystem>();
	URPGCombatCatalogSubsystem* Catalog = Scope.GameInstance->GetSubsystem<URPGCombatCatalogSubsystem>();
	if (!TestNotNull(TEXT("selection store"), Selection) || !TestNotNull(TEXT("world moves subsystem"), Moves) || !TestNotNull(TEXT("catalog subsystem"), Catalog)) return false;
	URPGBossEncounterDefinition* Encounter = MakeValidPackSelection();
	if (!TestNotNull(TEXT("valid transient encounter fixture"), Encounter)) return false;
	Selection->SetSelectedDefinition(Encounter);
	APawn* Boss = Scope.SpawnPackPawn(BossClassPath, FVector::ZeroVector);
	APawn* Player = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("pack boss"), Boss) || !TestNotNull(TEXT("pack player"), Player)) return false;
	Catalog->Deinitialize();
	TestFalse(TEXT("fixture removes only this instance's catalog epoch"), static_cast<bool>(Catalog->GetEpoch()));
	AddExpectedError(TEXT("reason=WorldInput.NoContent"), EAutomationExpectedErrorFlags::Contains, 1);
	Scope.BeginPlay();
	TestFalse(TEXT("missing epoch leaves no framework boss collision"), Boss->GetActorEnableCollision());
	TestFalse(TEXT("missing epoch leaves no framework encounter component"), Boss->FindComponentByClass<URPGBossEncounter>() != nullptr);
	TestNotNull(TEXT("player-only setup survives catalog refusal"), Player->FindComponentByClass<URPGDodgeTiming>());
	TActorIterator<ARPGEncounterBinding> Bindings(Scope.World);
	TestFalse(TEXT("missing epoch destroys the transient binding"), static_cast<bool>(Bindings));
	Selection->ClearSelectedDefinition();
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterSelectionSubsystemTeardownReleasesOwnedActivation,
	"OneBossFight.Binding.EncounterSelection.SubsystemTeardownReleasesOwnedActivation",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterSelectionSubsystemTeardownReleasesOwnedActivation::RunTest(const FString&)
{
	FStartupActivationWorld Scope;
	if (!TestNotNull(TEXT("real game-instance test world"), Scope.World)) return false;
	URPGEncounterSelectionSubsystem* Selection = Scope.GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>();
	URPGPlayerMovesSubsystem* Moves = Scope.World->GetSubsystem<URPGPlayerMovesSubsystem>();
	if (!TestNotNull(TEXT("selection store"), Selection) || !TestNotNull(TEXT("world moves subsystem"), Moves)) return false;
	URPGBossEncounterDefinition* Encounter = MakeValidPackSelection();
	if (!TestNotNull(TEXT("valid transient encounter fixture"), Encounter)) return false;
	Selection->SetSelectedDefinition(Encounter);
	APawn* Boss = Scope.SpawnPackPawn(BossClassPath, FVector::ZeroVector);
	APawn* Player = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("pack boss"), Boss) || !TestNotNull(TEXT("pack player"), Player)) return false;
	Moves->OnWorldBeginPlay(*Scope.World);
	if (!TestNotNull(TEXT("activation was registered before teardown"), Boss->FindComponentByClass<URPGBossEncounter>())) return false;
	TActorIterator<ARPGEncounterBinding> Before(Scope.World);
	if (!TestTrue(TEXT("binding exists before teardown"), static_cast<bool>(Before))) return false;

	Moves->Deinitialize();
	TestNull(TEXT("owned encounter component is removed by subsystem teardown"), Boss->FindComponentByClass<URPGBossEncounter>());
	TestNull(TEXT("owned stagger component is removed by subsystem teardown"), Boss->FindComponentByClass<URPGBossStagger>());
	TestNotNull(TEXT("unrelated player dodge setup survives boss activation release"), Player->FindComponentByClass<URPGDodgeTiming>());
	TActorIterator<ARPGEncounterBinding> After(Scope.World);
	TestFalse(TEXT("transient binding is destroyed by subsystem teardown"), static_cast<bool>(After));
	Moves->Deinitialize();
	TestNull(TEXT("repeated subsystem teardown remains harmless"), Boss->FindComponentByClass<URPGBossEncounter>());
	Selection->ClearSelectedDefinition();
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterSelectionDuplicateCensus,
	"OneBossFight.Binding.EncounterSelection.DuplicateBossAndPlayerCensusFailsClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterSelectionDuplicateCensus::RunTest(const FString&)
{
	FStartupActivationWorld Scope;
	if (!TestNotNull(TEXT("real game-instance test world"), Scope.World)) return false;
	URPGEncounterSelectionSubsystem* Selection = Scope.GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>();
	URPGPlayerMovesSubsystem* Moves = Scope.World->GetSubsystem<URPGPlayerMovesSubsystem>();
	if (!TestNotNull(TEXT("game-instance selection store"), Selection) || !TestNotNull(TEXT("world moves subsystem"), Moves)) return false;
	Selection->SetSelectedDefinition(Scope.MakeSelection());
	APawn* BossA = Scope.SpawnPackPawn(BossClassPath, FVector(0.f, 0.f, 0.f));
	APawn* BossB = Scope.SpawnPackPawn(BossClassPath, FVector(500.f, 0.f, 0.f));
	APawn* PlayerA = Scope.SpawnPackPawn(PlayerClassPath, FVector(1000.f, 0.f, 0.f));
	APawn* PlayerB = Scope.SpawnPackPawn(PlayerClassPath, FVector(1500.f, 0.f, 0.f));
	if (!TestNotNull(TEXT("first pack boss"), BossA) || !TestNotNull(TEXT("duplicate pack boss"), BossB)
		|| !TestNotNull(TEXT("first pack player"), PlayerA) || !TestNotNull(TEXT("duplicate pack player"), PlayerB)) return false;
	AddExpectedError(TEXT("outcome=HardError reason=EncounterSelection.Census"), EAutomationExpectedErrorFlags::Contains, 1);
	Moves->OnWorldBeginPlay(*Scope.World);
	TestFalse(TEXT("first boss receives no legacy bundle"), HasLegacyBossBundle(BossA));
	TestFalse(TEXT("duplicate boss receives no legacy bundle"), HasLegacyBossBundle(BossB));
	TestFalse(TEXT("census refusal disables the first framework boss actor"), BossA->IsActorTickEnabled());
	TestFalse(TEXT("census refusal disables the duplicate framework boss actor"), BossB->IsActorTickEnabled());
	TestFalse(TEXT("census refusal disables boss collision"), BossA->GetActorEnableCollision());
	TestEqual(TEXT("selection store reports ambiguous census"), Selection->GetSelectionDiagnostic(), FString(TEXT("EncounterSelection.Census")));
	TActorIterator<ARPGEncounterBinding> Bindings(Scope.World);
	TestFalse(TEXT("duplicate census leaves no transient binding"), static_cast<bool>(Bindings));   // TActorIterator has only an explicit bool conversion
	Selection->ClearSelectedDefinition();
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterSelectionStoreIsGameInstanceScoped,
	"OneBossFight.Binding.EncounterSelection.StoreIsGameInstanceScoped",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterSelectionStoreIsGameInstanceScoped::RunTest(const FString&)
{
	FStartupActivationWorld First;
	FStartupActivationWorld Second;
	if (!TestNotNull(TEXT("first game-instance world"), First.World) || !TestNotNull(TEXT("second game-instance world"), Second.World)) return false;
	URPGEncounterSelectionSubsystem* FirstStore = First.GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>();
	URPGEncounterSelectionSubsystem* SecondStore = Second.GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>();
	if (!TestNotNull(TEXT("first selection store"), FirstStore) || !TestNotNull(TEXT("second selection store"), SecondStore)) return false;
	URPGBossEncounterDefinition* FirstDefinition = First.MakeSelection();
	URPGBossEncounterDefinition* SecondDefinition = Second.MakeSelection();
	if (!TestNotNull(TEXT("first transient definition"), FirstDefinition) || !TestNotNull(TEXT("second transient definition"), SecondDefinition)) return false;
	FirstStore->SetSelectedDefinition(FirstDefinition);
	TestTrue(TEXT("the first instance retains its selected definition"), FirstStore->HasSelectionRequest());
	FirstStore->SetSelectedDefinition(SecondDefinition);
	FString ResolveError;
	TestTrue(TEXT("replacement definition becomes the active selection"), FirstStore->ResolveSelectedDefinition(ResolveError) == SecondDefinition);
	TestTrue(TEXT("replacement resolution clears diagnostic"), ResolveError.IsEmpty());
	TestFalse(TEXT("selection does not leak into a second game instance"), SecondStore->HasSelectionRequest());
	SecondStore->SetSelectedDefinition(SecondDefinition);
	FirstStore->ClearSelectedDefinition();
	TestFalse(TEXT("clearing the first instance clears only its selection"), FirstStore->HasSelectionRequest());
	TestTrue(TEXT("second instance retains its independent selection"), SecondStore->HasSelectionRequest());
	SecondStore->ClearSelectedDefinition();
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGBossEncounterResetBroadcastsAfterStateUpdate,
	"OneBossFight.Binding.EncounterLifecycle.ResetBroadcastAfterStateUpdate",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGBossEncounterResetBroadcastsAfterStateUpdate::RunTest(const FString&)
{
	FStartupActivationWorld Scope;
	if (!TestNotNull(TEXT("real game-instance test world"), Scope.World)) return false;
	AActor* Owner = Scope.World->SpawnActor<AActor>();
	if (!TestNotNull(TEXT("transient encounter owner"), Owner)) return false;
	URPGBossEncounter* Encounter = NewObject<URPGBossEncounter>(Owner, TEXT("LifecycleEncounter"));
	if (!TestNotNull(TEXT("encounter lifecycle component"), Encounter)) return false;
	Owner->AddInstanceComponent(Encounter);
	Encounter->RegisterComponent();
	Scope.BeginPlay();

	int32 Broadcasts = 0;
	uint64 BroadcastGeneration = 0;
	int32 BroadcastResetCount = 0;
	bool bBroadcastSawUpdatedState = false;
	Encounter->OnResetBroadcast().AddLambda([&](uint64 NewGeneration, int32 ResetCount)
	{
		++Broadcasts;
		BroadcastGeneration = NewGeneration;
		BroadcastResetCount = ResetCount;
		bBroadcastSawUpdatedState = NewGeneration == static_cast<uint64>(Encounter->GetParticipantGeneration())
			&& ResetCount == Encounter->GetResetCount();
	});

	Encounter->ResetForTest();
	TestEqual(TEXT("one successful reset emits exactly one lifecycle notification"), Broadcasts, 1);
	TestEqual(TEXT("notification generation increments once"), BroadcastGeneration, static_cast<uint64>(2));
	TestEqual(TEXT("notification reset count increments once"), BroadcastResetCount, 1);
	TestTrue(TEXT("notification is broadcast after both generation fields update"), bBroadcastSawUpdatedState);
	Encounter->OnResetBroadcast().Clear();
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterDefaultDataStartup,
	"OneBossFight.Binding.EncounterSelection.DefaultDataStartup",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterDefaultDataStartup::RunTest(const FString&)
{
	// Owner decision 2026-11-06 (retire legacy): with no explicit selection the arena stores the default definition; every other case leaves the selection absent.
	FStartupActivationWorld Scope;
	if (!TestNotNull(TEXT("real game-instance test world"), Scope.World)) return false;
	URPGEncounterSelectionSubsystem* Selection = Scope.GameInstance->GetSubsystem<URPGEncounterSelectionSubsystem>();
	URPGPlayerMovesSubsystem* Moves = Scope.World->GetSubsystem<URPGPlayerMovesSubsystem>();
	if (!TestNotNull(TEXT("game-instance selection store"), Selection) || !TestNotNull(TEXT("moves subsystem"), Moves)) return false;
	const FString DefaultPath = Moves->DefaultEncounterDefinition;
	const FString MapName = UWorld::RemovePIEPrefix(Scope.World->GetMapName());
	TestTrue(TEXT("the shipped default path is set"), !DefaultPath.IsEmpty());
	Selection->ClearSelectedDefinition();

	Moves->bDefaultToDataStartup = false;
	Moves->DefaultEncounterMap = MapName;
	Moves->ApplyDefaultDataSelection();
	TestFalse(TEXT("switch off: no selection"), Selection->HasSelectionRequest());

	Moves->bDefaultToDataStartup = true;
	Moves->DefaultEncounterMap = TEXT("L_SomeOtherMap");
	Moves->ApplyDefaultDataSelection();
	TestFalse(TEXT("other map: no selection"), Selection->HasSelectionRequest());

	Moves->DefaultEncounterMap = MapName;
	Moves->DefaultEncounterDefinition.Reset();
	Moves->ApplyDefaultDataSelection();
	TestFalse(TEXT("empty definition path: no selection"), Selection->HasSelectionRequest());

	AddExpectedError(TEXT("DoesNotExist_ER"), EAutomationExpectedErrorFlags::Contains, 0);
	Moves->DefaultEncounterDefinition = TEXT("/Game/OneBossFight/Data/DoesNotExist_ER.DoesNotExist_ER");
	Moves->ApplyDefaultDataSelection();
	TestFalse(TEXT("definition that does not load: legacy stays, no selection"), Selection->HasSelectionRequest());

	Moves->DefaultEncounterDefinition = DefaultPath;
	Moves->ApplyDefaultDataSelection();
	TestTrue(TEXT("default on the arena map stores the definition"), Selection->HasSelectionRequest());
	TestTrue(TEXT("the stored definition is the G044 encounter"), Selection->GetRequestedDefinitionPathForDiagnostics().Contains(TEXT("DA_Sevarog_G044_Encounter")));

	Selection->ClearSelectedDefinition();
	URPGBossEncounterDefinition* Explicit = Scope.MakeSelection();
	if (!TestNotNull(TEXT("explicit selection"), Explicit)) return false;
	Selection->SetSelectedDefinition(Explicit);
	const FString Before = Selection->GetRequestedDefinitionPathForDiagnostics();
	Moves->ApplyDefaultDataSelection();
	TestEqual(TEXT("an explicit selection always wins"), Selection->GetRequestedDefinitionPathForDiagnostics(), Before);
	Selection->ClearSelectedDefinition();
	return true;
}

#endif
