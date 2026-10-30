// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "Player/RPGBossMoveCard.h"
#include "RPGBossFrameworkProfile.generated.h"
class USkeletalMesh;
class UAnimInstance;
class APawn;
/** F5: one selectable card with its cooldown and authored weight (proof values, design values, proposed). */
USTRUCT()
struct FRPGBossProfileCard
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere) TSoftObjectPtr<URPGBossMoveCard> Card;
    UPROPERTY(EditAnywhere) float CooldownSeconds=0.f;
    UPROPERTY(EditAnywhere) float Weight=1.f;
};
UCLASS(BlueprintType)
class ONEBOSSFIGHT_API URPGBossFrameworkProfile : public UPrimaryDataAsset
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere) FString FixtureLabel;
    UPROPERTY(EditAnywhere) TSoftObjectPtr<USkeletalMesh> Mesh;
    UPROPERTY(EditAnywhere) TSoftClassPtr<UAnimInstance> AnimClass;
    UPROPERTY(EditAnywhere) TSoftClassPtr<APawn> TargetPawnClass;
    UPROPERTY(EditAnywhere) TSoftObjectPtr<URPGBossMoveCard> Card;
    UPROPERTY(EditAnywhere) float BandMinCm=0.f;
    UPROPERTY(EditAnywhere) float BandMaxCm=0.f;
    UPROPERTY(EditAnywhere) float WalkSpeedCmPerSecond=0.f;
    UPROPERTY(EditAnywhere) float AcceptanceCm=0.f;
    UPROPERTY(EditAnywhere) float WalkTimeoutSeconds=0.f;
    UPROPERTY(EditAnywhere) float BlendInSeconds=0.f;
    UPROPERTY(EditAnywhere) float BlendOutSeconds=0.f;
    UPROPERTY(EditAnywhere) float CapsuleRadiusCm=0.f;
    UPROPERTY(EditAnywhere) float CapsuleHalfHeightCm=0.f;
    /** Pack player health the proof fixture writes explicitly (a bare proof map has none: measured 0 / 1000000). Fixture value, not tuning. */
    UPROPERTY(EditAnywhere) float TargetHealth=0.f;
    /** F4: the card may damage (HPDamage > 0) and the sweep values below apply; the label must then be "F4 fixture". F3: false. */
    UPROPERTY(EditAnywhere) bool bDamageEnabled=false;
    /** Largest distance in cm one swept substep may cover, and the substep cap per tick (design values, proposed; F4 only). */
    UPROPERTY(EditAnywhere) float HitStepCm=0.f;
    UPROPERTY(EditAnywhere) int32 HitMaxSubsteps=0;
    /** F5 ("F5 fixture"): the selector chooses among Cards for each of AttackCount attacks; Card must then stay empty. F3/F4: Cards empty. */
    UPROPERTY(EditAnywhere) TArray<FRPGBossProfileCard> Cards;
    UPROPERTY(EditAnywhere) float RepeatPenalty=0.f;
    UPROPERTY(EditAnywhere) int32 RepeatMemory=0;
    UPROPERTY(EditAnywhere) int32 AttackCount=0;
    /** Optional (both > 0 or both 0): the boss's own health and what one player hit takes off it (design values, proposed). 0 = not hittable. */
    UPROPERTY(EditAnywhere) float BossMaxHealth=0.f;
    UPROPERTY(EditAnywhere) float PlayerHitDamage=0.f;
    /** F6c (F5 fixture with a hittable boss): at or below this health fraction (0 < f < 1) the boss moves to PhaseTwoId at the next neutral decision. 0 = no phases (PhaseTwoId must then be empty). Design value, proposed. */
    UPROPERTY(EditAnywhere) float PhaseTwoFraction=0.f;
    UPROPERTY(EditAnywhere) FName PhaseTwoId;
    /** F8 posture / stance break (F5 fixture with a hittable boss; all zero = off): each player hit drains PlayerPostureHitAmount of PostureMax; at zero the boss is staggered for StaggerSeconds
     *  (a running attack is aborted), then posture refills. Regeneration waits PostureRegenDelaySeconds after the last drain, then adds PostureRegenPerSecond. Design values, proposed. */
    UPROPERTY(EditAnywhere) float PostureMax=0.f;
    UPROPERTY(EditAnywhere) float PlayerPostureHitAmount=0.f;
    UPROPERTY(EditAnywhere) float StaggerSeconds=0.f;
    UPROPERTY(EditAnywhere) float PostureRegenDelaySeconds=0.f;
    UPROPERTY(EditAnywhere) float PostureRegenPerSecond=0.f;
    /** F9 bleed (F5 fixture with a hittable boss; BleedBuildupPerHit 0 = off, the other four must then be 0 too): each player hit adds BleedBuildupPerHit; at the threshold (first BleedInitialThreshold,
     *  raised by BleedThresholdIncrease after each proc up to BleedThresholdMax) the boss loses BleedHpFraction of its maximum health at once, never its last point (RPGBleedRules, unchanged). Design values, proposed. */
    UPROPERTY(EditAnywhere) float BleedBuildupPerHit=0.f;
    UPROPERTY(EditAnywhere) float BleedInitialThreshold=0.f;
    UPROPERTY(EditAnywhere) float BleedThresholdIncrease=0.f;
    UPROPERTY(EditAnywhere) float BleedThresholdMax=0.f;
    UPROPERTY(EditAnywhere) float BleedHpFraction=0.f;
    UPROPERTY(EditAnywhere) FTransform MeshRelativeTransform;
    UPROPERTY(EditAnywhere) bool bAlignmentAuthored=false;
};
/** Owned, loaded dependencies. Resolver is the explicit load boundary; consumers never load. */
struct ONEBOSSFIGHT_API FRPGFrameworkDependencies
{
    TStrongObjectPtr<URPGBossFrameworkProfile> Profile;
    TStrongObjectPtr<USkeletalMesh> Mesh;
    TStrongObjectPtr<UClass> AnimClass, TargetClass;
    TSharedPtr<const FRPGCompiledBossMoveCard> Card;
    struct FCandidate { TSharedPtr<const FRPGCompiledBossMoveCard> Card; float CooldownSeconds=0.f,Weight=1.f; };
    TArray<FCandidate> Candidates;   // F5 only
    const TSharedPtr<const FRPGCompiledBossMoveCard>& FirstCard() const { return Candidates.Num()>0 ? Candidates[0].Card : Card; }
};
namespace RPGFramework
{
    /** Pure (KI-149 Tier 1, spec in Antigravity validate_ki149_tier1.py): can a pool of cards with these cooldowns always offer a card on each of AttackCount consecutive attacks?
     *  Yes when one card has no cooldown, or when there are at least AttackCount cards (k-1 earlier attacks put at most k-1 cards on cooldown). Refuses AttackCount < 1. */
    ONEBOSSFIGHT_API bool PhasePoolCannotStarve(const TArray<float>& CooldownSeconds,int32 AttackCount);
    ONEBOSSFIGHT_API bool ValidateProfile(const URPGBossFrameworkProfile& Profile,FString& Error);
    ONEBOSSFIGHT_API bool ResolveProfile(URPGBossFrameworkProfile* Profile,TUniquePtr<FRPGFrameworkDependencies>& Out,FString& Error);
    ONEBOSSFIGHT_API bool HasSlotNode(UAnimInstance* Instance,FName Slot);
}
