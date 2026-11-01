// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "Player/RPGBossMoveCard.h"
#include "Player/RPGBossComboRules.h"
#include "RPGBossFrameworkProfile.generated.h"
class USkeletalMesh;
class UAnimInstance;
class UAnimSequence;
class APawn;
/** Combo graph data (BOSS-COM rows): the hit outcome an edge may require. Guarded and Parried are part of the data contract; the boss reports Hit or Whiff today (no guard telemetry yet). */
UENUM()
enum class ERPGBossComboOutcome : uint8 { Hit, Whiff, Guarded, Parried };
USTRUCT()
struct FRPGBossComboEdgeData
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere) FName ToNode;
    UPROPERTY(EditAnywhere) float MinRangeCm=0.f;
    UPROPERTY(EditAnywhere) float MaxRangeCm=1.e6f;
    UPROPERTY(EditAnywhere) float MaxAbsYawDegrees=180.f;
    UPROPERTY(EditAnywhere) bool bAnyOutcome=true;
    UPROPERTY(EditAnywhere) ERPGBossComboOutcome Outcome=ERPGBossComboOutcome::Hit;
    /** BOSS-PAC-002: seconds the boss waits in neutral before the next card of the combo (0..5), a deliberate tempo pause. Design value, proposed. */
    UPROPERTY(EditAnywhere) float TempoPauseSeconds=0.f;
};
USTRUCT()
struct FRPGBossComboNodeData
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere) FName NodeId;
    UPROPERTY(EditAnywhere) FName MoveId;   // MoveId of one of the profile's cards
    UPROPERTY(EditAnywhere) TArray<FRPGBossComboEdgeData> Edges;
};
/** F5: one selectable card with its cooldown and authored weight (proof values, design values, proposed). */
USTRUCT()
struct FRPGBossProfileCard
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere) TSoftObjectPtr<URPGBossMoveCard> Card;
    UPROPERTY(EditAnywhere) float CooldownSeconds=0.f;
    UPROPERTY(EditAnywhere) float Weight=1.f;
    /** BOSS-DEF-004: during the ACTIVE state of this card a player hit costs health but no posture, so it cannot start a stance break. Design choice, proposed. */
    UPROPERTY(EditAnywhere) bool bHyperArmor=false;
    /** BOSS-PHS-005: score factor of this card while the boss has detected kiting / hugging (profile AntiCheese fields); 1 = no preference, (0,100]. Design values, proposed. */
    UPROPERTY(EditAnywhere) float KiteWeightMultiplier=1.f;
    UPROPERTY(EditAnywhere) float HugWeightMultiplier=1.f;
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
    /** BOSS-SEL-005 (opt-in, F5 fixture only, 0 = off): bounded random tie break inside the top score tier of the selector, [0,0.5], with its seed. Design values, proposed. */
    UPROPERTY(EditAnywhere) float SelectorTieBand=0.f;
    UPROPERTY(EditAnywhere) int32 SelectorTieSeed=0;
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
    /** F11 (owner decision 3, spec Antigravity/Reviews/F11_STAGGER_PHASE_ANIM_SPEC.md): optional animation sequences of the boss skeleton. The three stagger clips are all set or all empty (empty = the F8 freeze in place);
     *  Start plays at the break, Loop fills the middle, End starts at StaggerSeconds - its length and finishes with the stagger. PhaseTransitionAnim plays at the phase latch and holds the selector for its length.
     *  AnimSlotName is the slot node of the boss AnimBP the clips play in (the cards use FullBody). */
    UPROPERTY(EditAnywhere) TSoftObjectPtr<UAnimSequence> StaggerStartAnim;
    UPROPERTY(EditAnywhere) TSoftObjectPtr<UAnimSequence> StaggerLoopAnim;
    UPROPERTY(EditAnywhere) TSoftObjectPtr<UAnimSequence> StaggerEndAnim;
    UPROPERTY(EditAnywhere) TSoftObjectPtr<UAnimSequence> PhaseTransitionAnim;
    UPROPERTY(EditAnywhere) FName AnimSlotName=TEXT("FullBody");
    /** Combo graph (F5 fixture only, empty = no combos): when the selector starts the card of ComboRoot's node the boss follows the graph at every branch gate (RPGBossComboRules.h). Design values, proposed. */
    UPROPERTY(EditAnywhere) TArray<FRPGBossComboNodeData> ComboNodes;
    UPROPERTY(EditAnywhere) FName ComboRoot;
    UPROPERTY(EditAnywhere) int32 ComboMaxDepth=3;
    /** Repositioning (F5 fixture only, 0 = off = fail closed with Framework.Selector.NoCandidate as before): when no card is eligible at a decision the boss walks back to its band and decides again, at most this many times in a row (1..8). Design value, proposed. */
    UPROPERTY(EditAnywhere) int32 RepositionMax=0;
    /** Turn rate (deg/s, (0,720], required when RepositionMax > 0, else 0) of the turn in place the boss does when it is inside its band but no card is eligible because it does not face the target (cone). Design value, proposed. */
    UPROPERTY(EditAnywhere) float RepositionTurnDegPerSecond=0.f;
    /** BOSS-AWR-001 (F5 fixture only, 0 = off): the encounter fails with reason OffArena when the target is farther than this many cm (2D) from where it stood when the encounter began. Design value, proposed. */
    UPROPERTY(EditAnywhere) float ArenaRadiusCm=0.f;
    /** BOSS-MOV-005 (needs ArenaRadiusCm > 0): instead of failing the encounter when the target leaves the arena, the boss aborts its card, walks back to the arena centre (where the target began) and waits in neutral; it resumes when the target is back inside the radius. false = fail with reason OffArena (BOSS-AWR-001). Design choice, proposed. */
    UPROPERTY(EditAnywhere) bool bArenaLeash=false;
    /** BOSS-AWR-007 (F5 lane, 0 = off): while the boss is in neutral and a visibility trace to the target is blocked (a pillar), it does not decide or strike: it searches, walking to where the target was last seen, for up to LosSearchSeconds ((0,30]), and goes back to the band when it sees the target again. Design value, proposed. */
    UPROPERTY(EditAnywhere) float LosSearchSeconds=0.f;
    /** BOSS-SEL-009 (F5 lane, both 0 = off): the boss PERCEIVES the target's flask drink (the edge of the DrinkingPotion montage on the target) and may REACT to it only after a delay drawn per drink, seeded (ReactionSeed + count), inside [ReactionDelayMinSeconds, ReactionDelayMaxSeconds] (0 < min <= max <= 5). Design values, proposed. */
    UPROPERTY(EditAnywhere) float ReactionDelayMinSeconds=0.f;
    UPROPERTY(EditAnywhere) float ReactionDelayMaxSeconds=0.f;
    UPROPERTY(EditAnywhere) int32 ReactionSeed=0;
    /** BOSS-PHS-005 (F5 lane, 0 = off): the target is KITING when its range at the boss's last AntiCheeseStreak decisions (this one included) was >= AntiCheeseKiteRangeCm, and HUGGING when it was <= AntiCheeseHugRangeCm; the cards' Kite/HugWeightMultiplier then apply. Design values, proposed. */
    UPROPERTY(EditAnywhere) float AntiCheeseKiteRangeCm=0.f;
    UPROPERTY(EditAnywhere) float AntiCheeseHugRangeCm=0.f;
    UPROPERTY(EditAnywhere) int32 AntiCheeseStreak=2;
    /** BOSS-MOV-002 (needs ArenaRadiusCm > 0): when the target stands at least CenterBiasStartFraction * ArenaRadiusCm from the arena centre (near a wall), the boss takes its place in the band on the CENTRE side of the target (blend 0..1: 0 = where it stands now, 1 = straight to the centre side) so it does not get pinned between the target and the wall. 0 = off. Design values, proposed. */
    UPROPERTY(EditAnywhere) float ArenaCenterBias=0.f;
    UPROPERTY(EditAnywhere) float CenterBiasStartFraction=0.5f;
    /** The arena centre when it is authored; otherwise the point where the target began (BOSS-AWR-001 / MOV-005). */
    UPROPERTY(EditAnywhere) bool bArenaCenterAuthored=false;
    UPROPERTY(EditAnywhere) FVector ArenaCenter=FVector::ZeroVector;
    /** BOSS-EXE-005 (needs posture and a phase two threshold, F5 lane): when the phase threshold is crossed while the boss is staggered, the stagger ends at once and the phase transition starts in the same tick. false = the stagger runs to its end first (BOSS-DEF-001 / F8 behaviour). Design choice, proposed. */
    UPROPERTY(EditAnywhere) bool bPhaseSupersedesStagger=false;
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
    TStrongObjectPtr<UAnimSequence> StaggerStart, StaggerLoop, StaggerEnd, PhaseTransition;   // F11, each null when its profile field is empty
    TSharedPtr<const FRPGCompiledBossMoveCard> Card;
    struct FCandidate { TSharedPtr<const FRPGCompiledBossMoveCard> Card; float CooldownSeconds=0.f,Weight=1.f; bool bHyperArmor=false; float KiteMultiplier=1.f,HugMultiplier=1.f; };
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
    /** The pure combo graph of a profile (empty graph when the profile has no ComboNodes). */
    ONEBOSSFIGHT_API RPGBossCombo::FComboGraph BuildComboGraph(const URPGBossFrameworkProfile& Profile);
}
