// DRAFT ONLY. Promote with reviewed integration seams; not part of the live module.
#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Engine/DataAsset.h"
#include "GameFramework/Actor.h"
#include "Subsystems/WorldSubsystem.h"
#include "Player/RPGCombatCatalog.h"
#include "RPGEncounterBinding.generated.h"

class URPGBossEncounter;
class URPGCombatContextSubsystem;
class UAnimSequenceBase;
class USkeleton;

USTRUCT(BlueprintType)
struct FRPGBossStatsConfig
{
	GENERATED_BODY()
	UPROPERTY(EditAnywhere) float MaxHealth = 0.f;
	UPROPERTY(EditAnywhere) float MaxPosture = 0.f;
	UPROPERTY(EditAnywhere) float PostureRegenDelay = 0.f;
	UPROPERTY(EditAnywhere) float PostureRegenRate = 0.f;
};

/** Encounter flow policy of the boss (URPGBossEncounter): the typed authoring record. The defaults below are defaults of this NEW asset field (old schema 1 definitions receive them additively); they match the native
 *  declarations of URPGBossEncounter, are not proof of any serialized or live actor value and are never a fallback for an invalid value. */
USTRUCT(BlueprintType)
struct FRPGEncounterPolicyConfig
{
	GENERATED_BODY()
	/** The boss sleeps until the player is this close (cm, horizontal) or damages it. 0 = no gate (the native meaning). Finite and not negative; fractional values are valid. */
	UPROPERTY(EditAnywhere) float GateRadius = 1200.f;
	/** Move the boss back to its start and make it dormant when the player respawns. */
	UPROPERTY(EditAnywhere) bool bResetOnPlayerRespawn = true;
};

/** Stagger and riposte scalar policy of the boss (URPGBossStagger): the typed authoring record, thirteen floats and one bool with the names of the native component. The defaults are defaults of this NEW asset field
 *  (old schema 1 definitions receive them additively); they match the native declarations, are not proof of any serialized or live actor value and are never a fallback for an invalid value. The domains are in
 *  RPGBossStaggerPolicyAdapters (the native ClampMin and ClampMax metadata is editor metadata and is not copied here as a runtime rule). Clips, classes, effects and mode toggles are NOT part of this record. */
USTRUCT(BlueprintType)
struct FRPGStaggerPolicyConfig
{
	GENERATED_BODY()
	UPROPERTY(EditAnywhere) float StaggerSeconds = 2.5f;
	UPROPERTY(EditAnywhere) float FreezeAtPosition = 1.55f;
	UPROPERTY(EditAnywhere) float CriticalMultiplier = 2.5f;
	UPROPERTY(EditAnywhere) float RiposteRange = 150.f;
	UPROPERTY(EditAnywhere) float RiposteConeDegrees = 120.f;
	UPROPERTY(EditAnywhere) float RiposteFacingDegrees = 120.f;
	UPROPERTY(EditAnywhere) float RiposteArmSeconds = 1.2f;
	UPROPERTY(EditAnywhere) float RipostePlayerStartGap = 150.f;
	UPROPERTY(EditAnywhere) float RiposteAlignSeconds = 0.3f;
	UPROPERTY(EditAnywhere) float RiposteImpactSeconds = 0.8f;
	UPROPERTY(EditAnywhere) float RiposteBaseDamage = 40.f;
	UPROPERTY(EditAnywhere) float CooldownSeconds = 0.f;
	UPROPERTY(EditAnywhere) float GetUpRate = 0.6f;
	UPROPERTY(EditAnywhere) bool bHoldPostureAtZero = true;
};

/** Phase flow policy of the boss (URPGBossPhases): the typed authoring record, six fields with the names of the native component. The defaults are defaults of this NEW asset field (old schema 1 definitions
 *  receive them additively); they match the source declarations of URPGBossPhases, are not proof of any serialized or live actor value and are never a fallback for an invalid value. The selected phase record with its
 *  threshold and multipliers, the fireball fields and every asset reference are NOT part of this record. AttackAbilityPrefix and LeapAbilityTag state an explicit identity only: that a matching ability or a registered
 *  gameplay tag exists is a later integration check, not something a non-empty value proves. */
USTRUCT(BlueprintType)
struct FRPGPhaseFlowConfig
{
	GENERATED_BODY()
	UPROPERTY(EditAnywhere) float TransitionSeconds = 1.8f;
	UPROPERTY(EditAnywhere) bool bUseRoarClip = true;
	UPROPERTY(EditAnywhere) bool bPausePostureInTransition = true;
	UPROPERTY(EditAnywhere) bool bLockLeapUntilPhaseTwo = true;
	UPROPERTY(EditAnywhere) FString AttackAbilityPrefix = TEXT("GA_GS_Boss_");
	UPROPERTY(EditAnywhere) FName LeapAbilityTag = TEXT("Ability.Melee.LeapAttack");
};

USTRUCT(BlueprintType)
struct FRPGPhaseConfig
{
	GENERATED_BODY()
	UPROPERTY(EditAnywhere) FName PhaseId;
	UPROPERTY(EditAnywhere) float EntryHealthFraction = 0.f;
	UPROPERTY(EditAnywhere) float SpeedMultiplier = 1.f;
	UPROPERTY(EditAnywhere) float RateMultiplier = 1.f;
	UPROPERTY(EditAnywhere) float AttackMultiplier = 1.f;
};

/** Transport record, not permission to apply arbitrary reflected properties at runtime. */
USTRUCT(BlueprintType)
struct FRPGParityField
{
	GENERATED_BODY()
	UPROPERTY(EditAnywhere) FString FieldPath;
	UPROPERTY(EditAnywhere) FString Value;
	UPROPERTY(EditAnywhere) FString Type;
	UPROPERTY(EditAnywhere) FString Units;
	UPROPERTY(EditAnywhere) FString SourcePath;
	UPROPERTY(EditAnywhere) FString SourceSHA256;
	UPROPERTY(EditAnywhere) FString SourceSite;
	UPROPERTY(EditAnywhere) FString Origin;
	UPROPERTY(EditAnywhere) FString Precedence;
	UPROPERTY(EditAnywhere) FString Destination;
	UPROPERTY(EditAnywhere) FString FirstRead;
	UPROPERTY(EditAnywhere) FString Witness;
};

UCLASS(BlueprintType)
class ONEBOSSFIGHT_API URPGBossDefinition : public UPrimaryDataAsset
{
	GENERATED_BODY()
public:
	UPROPERTY(EditAnywhere) int32 Schema = 1;
	UPROPERTY(EditAnywhere) FName DefinitionId;
	UPROPERTY(EditAnywhere) FName PresentationId;
	UPROPERTY(EditAnywhere) FRPGBossStatsConfig Stats;
	UPROPERTY(EditAnywhere) FRPGEncounterPolicyConfig EncounterPolicy;
	UPROPERTY(EditAnywhere) FRPGStaggerPolicyConfig StaggerPolicy;
	UPROPERTY(EditAnywhere) FRPGPhaseFlowConfig PhaseFlow;
	UPROPERTY(EditAnywhere) TArray<FRPGPhaseConfig> Phases;
	UPROPERTY(EditAnywhere) TSoftObjectPtr<USkeleton> Skeleton;
	UPROPERTY(EditAnywhere) TArray<TSoftObjectPtr<UAnimSequenceBase>> Animations;
	/** Must cover private/constructor/instance fields too before migration is accepted. */
	UPROPERTY(EditAnywhere) TArray<FRPGParityField> Fields;
};

struct FRPGParticipantKey
{
	FGuid WorldSession, EncounterInstance;
	FName Slot;
	uint32 Generation = 0;
	bool operator==(const FRPGParticipantKey& Other) const
	{
		return WorldSession == Other.WorldSession && EncounterInstance == Other.EncounterInstance
			&& Slot == Other.Slot && Generation == Other.Generation;
	}
};

struct FRPGHydrationResult
{
	TArray<FString> Errors;
	bool IsReady() const { return Errors.IsEmpty(); }
	void Fail(const FString& Message) { Errors.Add(Message); }
};

/** Value metadata plus a lease on the SAME game-instance content epoch, never a global copy. */
struct FRPGParticipantConfig
{
	FName BossId, PresentationId;
	FString StableManifestHash;
	int32 Schema = 1;
	FRPGBossStatsConfig Stats;
	FRPGEncounterPolicyConfig EncounterPolicy;
	FRPGStaggerPolicyConfig StaggerPolicy;
	FRPGPhaseFlowConfig PhaseFlow;
	TArray<FRPGPhaseConfig> Phases;
	TArray<FRPGParityField> Fields;
	TSharedPtr<const RPGCombatRegistry::FEpoch> Content;
	TStrongObjectPtr<USkeleton> Skeleton;
	TArray<TStrongObjectPtr<UAnimSequenceBase>> Animations;
	bool bSyntheticFixture = false; // only the automation factory sets this; never asset-authored
};

USTRUCT(BlueprintType)
struct FRPGPlacedParticipantBinding
{
	GENERATED_BODY()
	UPROPERTY(EditAnywhere) FName Slot;
	UPROPERTY(EditAnywhere) FName TargetSlot;
	UPROPERTY(EditInstanceOnly) TObjectPtr<AActor> Actor = nullptr;
	UPROPERTY(EditAnywhere) TObjectPtr<URPGBossDefinition> Definition = nullptr;
};

UCLASS()
class ONEBOSSFIGHT_API ARPGEncounterBinding : public AActor
{
	GENERATED_BODY()
public:
	/** Explicit identity; invalid/duplicate is rejected, not regenerated silently. */
	UPROPERTY(EditInstanceOnly) FGuid EncounterInstance;
	UPROPERTY(EditInstanceOnly) TArray<FRPGPlacedParticipantBinding> Participants;
};

UCLASS()
class ONEBOSSFIGHT_API URPGCombatParticipant : public UActorComponent
{
	GENERATED_BODY()
public:
	bool ConfigureBeforeRegistration(TSharedPtr<const FRPGParticipantConfig> InConfig,
		const FRPGParticipantKey& InKey, URPGCombatContextSubsystem& InContext);
	UFUNCTION(BlueprintPure) bool IsReady() const;
	UFUNCTION(BlueprintPure) FString GetKeyDiagnostic() const;
	const FRPGParticipantKey& Key() const { return ParticipantKey; }
	TSharedPtr<const FRPGParticipantConfig> Config() const { return Snapshot; }
protected:
	virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
	friend class URPGCombatContextSubsystem;
	FRPGParticipantKey ParticipantKey;
	TSharedPtr<const FRPGParticipantConfig> Snapshot;
	TWeakObjectPtr<URPGCombatContextSubsystem> Context;
};

/** Native adapter is deliberately typed code, not ImportText of author-controlled properties. */
struct FRPGComponentPlan
{
	UClass* Class = nullptr;
	FName InstanceName;
	TArray<FString> RequiredFields;
	TFunction<bool(UActorComponent&, const FRPGParticipantConfig&, FString&)> Configure;
};

UCLASS()
class ONEBOSSFIGHT_API URPGCombatContextSubsystem : public UWorldSubsystem
{
	GENERATED_BODY()
public:
	virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
	virtual void Initialize(FSubsystemCollectionBase& Collection) override;
	virtual void Deinitialize() override;
	FRPGHydrationResult BindEncounter(const ARPGEncounterBinding& Binding,
		const TMap<FName, TSharedPtr<const FRPGParticipantConfig>>& Configs);
	TOptional<FRPGParticipantKey> FindParticipant(const AActor& Actor) const;
	AActor* ResolveTarget(const FRPGParticipantKey& Key, FName TargetSlot) const;
	URPGBossEncounter* ResolveEncounter(const AActor& Requester) const;
	bool IsCurrent(const FRPGParticipantKey& Key) const;
	bool IsHydrated(const FRPGParticipantKey& Key) const;
	bool OnGenerationChanged(AActor& Actor, uint32 NewGeneration);
	void UnbindActor(AActor& Actor);
	FRPGHydrationResult CreateConfigureRegister(AActor& Actor, const TArray<FRPGComponentPlan>& Plans);
	UFUNCTION(BlueprintPure) int32 GetBoundCount() const;
	UFUNCTION(BlueprintPure) int32 GetReadyCount() const;
	UFUNCTION(BlueprintPure) FString GetSessionId() const { return Session.ToString(); }
private:
	struct FRecord
	{
		TWeakObjectPtr<AActor> Actor;
		FRPGParticipantKey Key;
		FName TargetSlot;
		TSharedPtr<const FRPGParticipantConfig> Config;
		bool bHydrated = false;
		bool bPoisoned = false;
	};
	FGuid Session;
	TArray<FRecord> Records;
	bool bHydrationInProgress = false;
};

namespace RPGCombatHydration
{
	ONEBOSSFIGHT_API FRPGHydrationResult CompileParticipant(const URPGBossDefinition& Definition,
		TSharedPtr<const RPGCombatRegistry::FEpoch> Content, const FString& ManifestHash,
		TSharedPtr<const FRPGParticipantConfig>& Out);
#if WITH_DEV_AUTOMATION_TESTS
	ONEBOSSFIGHT_API FRPGHydrationResult CompileSyntheticParticipant(const URPGBossDefinition& Definition,
		TSharedPtr<const RPGCombatRegistry::FEpoch> Content, const FString& ManifestHash,
		TSharedPtr<const FRPGParticipantConfig>& Out);
#endif
}
