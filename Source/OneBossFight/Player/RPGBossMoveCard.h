// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "UObject/SoftObjectPtr.h"
#include "UObject/StrongObjectPtr.h"
#include "RPGBossMoveCard.generated.h"
class USkeleton;
class USkeletalMesh;
class UAnimSequence;
class UAnimMontage;
class UAnimSequenceBase;

/** One baked sample of a hit window's blade segment in COMPONENT space. A COPY of animation data: re-bake whenever the animation changes. */
USTRUCT(BlueprintType)
struct FRPGBakedBladeSample
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere) float TimeSeconds = 0.f;
    UPROPERTY(EditAnywhere) FVector BaseCS = FVector::ZeroVector;
    UPROPERTY(EditAnywhere) FVector TipCS = FVector::ZeroVector;
};

class USoundBase;

/** BOSS-PAC-004 / QA-007: the visual of a cue (the project's authored flipbook sheets). None is refused: a cue has both channels. */
UENUM(BlueprintType)
enum class ERPGBossCueVisual : uint8 { None, HitSpark, DodgeDust, BloodBurst };

/** BOSS-ANM-003 / PAC-004 / QA-007: one cue of a card: a visual and a sound at a card time (or at the end of the windup hold), at a boss socket (None = at the boss's feet). */
USTRUCT(BlueprintType)
struct FRPGBossCue
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere) FName CueId;
    UPROPERTY(EditAnywhere) float TimeSeconds = 0.f;
    /** True: fired when the windup hold ends (TimeSeconds is ignored; the card needs a hold). */
    UPROPERTY(EditAnywhere) bool bAtHoldRelease = false;
    UPROPERTY(EditAnywhere) ERPGBossCueVisual Visual = ERPGBossCueVisual::None;
    UPROPERTY(EditAnywhere) TSoftObjectPtr<USoundBase> Sound;
    UPROPERTY(EditAnywhere) FName Socket;
};

USTRUCT(BlueprintType)
struct FRPGBossMoveWindow
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FName WindowId;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FName HitGroup;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float StartSeconds = 0.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float EndSeconds = 0.f;
    /** A swept capsule segment defined by TWO distinct authored socket or bone names; no proximity fallback. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FName SocketA;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FName SocketB;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float RadiusCm = 0.f;
    /** BOSS-HIT-010: a SECONDARY window (shockwave / ground splash). It may overlap the direct windows in time, must share a HitGroup with a direct window, and is always processed AFTER the direct windows of the same tick, so the shared hit key makes a simultaneous contact apply the direct hit only. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite) bool bSecondary = false;
    /** BOSS-HIT-011: a RING window (ground shockwave around the boss, no sockets, no baked samples). Its front starts at RingStartRadiusCm when the window opens and moves outward at RingSpeedCmPerSecond; the band behind the front is RingThicknessCm wide; the wave reaches RingHeightCm above the ground (a target above that is missed). The ring ends with the window. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite) bool bRing = false;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float RingStartRadiusCm = 0.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float RingSpeedCmPerSecond = 0.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float RingThicknessCm = 0.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float RingHeightCm = 0.f;
    /** BOSS-HIT-012: a GRAB window. It is a blade window (sockets, radius) whose contact catches the target instead of damaging it: the victim is attached to GrabAttachSocket (a boss socket or bone) with movement off until GrabReleaseSeconds (card time, after the window, within the recovery), then released to the floor and the card's HPDamage is applied. Any abort of the attack releases the victim at once, without damage. At most one grab window per card. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite) bool bGrab = false;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FName GrabAttachSocket;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float GrabReleaseSeconds = 0.f;
    /** Optional (empty = live sockets): the baked blade path of this window, strictly ordered, covering [StartSeconds, EndSeconds], inside the clip. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite) TArray<FRPGBakedBladeSample> BakedSamples;
};

USTRUCT(BlueprintType)
struct FRPGBossMoveCardSpec
{
    GENERATED_BODY()
    /** Zero-valued draft is deliberately invalid, never a runnable default. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 Schema = 0;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FName MoveId;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FName FamilyId;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FName PhaseId;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) TSoftObjectPtr<USkeleton> Skeleton;
    /** Exactly ONE source. No load or fallback inside pure validation. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite) TSoftObjectPtr<UAnimSequence> Sequence;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) TSoftObjectPtr<UAnimMontage> Montage;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FName SlotName;
    /** None explicitly means the full source, otherwise a montage section is required. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FName SectionName;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float PlayRate = 0.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float CommitSeconds = 0.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float ActiveStartSeconds = 0.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float ActiveEndSeconds = 0.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float RecoveryEndSeconds = 0.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float TrackDegreesPerSecond = 0.f;
    /** BOSS-ANM-006 (0 = off): bounded warp. Between WarpStartSeconds and WarpEndSeconds (card time, after the commit, inside the active end) the boss closes on the target down to WarpStandoffCm and turns toward it, by at most WarpMaxDistanceCm and WarpMaxAngleDegrees in total. The clip stays in place (no root motion); the boss actor moves. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float WarpStartSeconds = 0.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float WarpEndSeconds = 0.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float WarpMaxDistanceCm = 0.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float WarpMaxAngleDegrees = 0.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float WarpStandoffCm = 0.f;
    /** Optional smoothstep distribution of the bounded warp distance over its window; disabled by default. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite) bool WarpEaseInOut = false;
    /** BOSS-DEF-005: a DEFENSIVE reposition: no hit window, no damage. With bWarpAway the warp moves the boss away; otherwise it closes toward WarpStandoffCm. Fair-window rules in RPGBossDefenseRules.h. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite) bool bDefensive = false;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) bool bWarpAway = false;
    /** BOSS-ANM-003 (0/0 = off): the windup HOLD. At HoldAtSeconds (card time, after the commit, before the active start) the montage stops for a seeded time in [HoldMinSeconds, HoldMaxSeconds] ((0,3]), then goes on. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float HoldAtSeconds = 0.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float HoldMinSeconds = 0.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float HoldMaxSeconds = 0.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 HoldSeed = 0;
    /** BOSS-PAC-004 / QA-007: the cues of this card (at most 8), each with both channels, distinct per id. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite) TArray<FRPGBossCue> Cues;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float MinRangeCm = 0.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float MaxRangeCm = 0.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float FrontConeDegrees = 0.f;
    /** BOSS-AWR-005: the card is refused when the vertical separation to the target is above this many cm (floor-plane cards: a target on a ledge or in the air). 0 = no vertical limit (every card authored before this field). */
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float MaxVerticalDeltaCm = 0.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float HPDamage = 0.f;
    /** First backend is in-place only. True is a named unsupported capability, not silently ignored. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite) bool bUsesRootMotion = false;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) TArray<FRPGBossMoveWindow> Windows;
};

UCLASS(BlueprintType)
class ONEBOSSFIGHT_API URPGBossMoveCard : public UPrimaryDataAsset
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, Category="Move Card") FRPGBossMoveCardSpec Spec;
};

/** Read-only resolution descriptor. Pure previews/tests may supply one; that alone is NOT real asset proof. */
struct FRPGBossMoveMetadata
{
    FSoftObjectPath AnimationPath, SkeletonPath, AnimationSkeletonPath, MeshSkeletonPath;
    double ClipLengthSeconds = 0.0;
    bool bRootMotion = false;
    TSet<FName> Slots, Sections, SocketOrBoneNames;
};
struct FRPGBossMoveIssues
{
    TArray<FString> Errors;
    bool IsValid() const { return Errors.IsEmpty(); }
};
namespace RPGBossMoveCards { struct FCompiler; }
/** Value snapshot is immutable through this API. Leases retain assets, not their mutability against external aliases. */
class ONEBOSSFIGHT_API FRPGCompiledBossMoveCard final
{
public:
    const FRPGBossMoveCardSpec& Spec() const { return SpecValue; }
    const FRPGBossMoveMetadata& Metadata() const { return MetadataValue; }
    /** Executor MUST require this; a metadata-only preview is never a playback capability. */
    bool HasResolvedAssets() const { return Leases.Num() == 3; }
private:
    friend struct RPGBossMoveCards::FCompiler;
    FRPGCompiledBossMoveCard(const FRPGBossMoveCardSpec& S, const FRPGBossMoveMetadata& M,
        TArray<TStrongObjectPtr<UObject>>&& InLeases) : SpecValue(S), MetadataValue(M), Leases(MoveTemp(InLeases)) {}
    FRPGBossMoveCardSpec SpecValue;
    FRPGBossMoveMetadata MetadataValue;
    TArray<TStrongObjectPtr<UObject>> Leases;
};
namespace RPGBossMoveCards
{
    /** No object loads, creation, registration, callback, mutation, defaulting or tuning. */
    ONEBOSSFIGHT_API FRPGBossMoveIssues Validate(const FRPGBossMoveCardSpec& Spec, const FRPGBossMoveMetadata& Metadata);
    /** Pure immutable preview; HasResolvedAssets=false. Clears stale output before every attempt. */
    ONEBOSSFIGHT_API FRPGBossMoveIssues CompileMetadata(const FRPGBossMoveCardSpec& Spec, const FRPGBossMoveMetadata& Metadata,
        TSharedPtr<const FRPGCompiledBossMoveCard>& Out);
    /** Real pointer/path/skeleton/type/mesh/slot checks. Supplied assets already loaded by the caller; no LoadSynchronous. Game thread only. */
    ONEBOSSFIGHT_API FRPGBossMoveIssues CompileResolved(const FRPGBossMoveCardSpec& Spec, USkeleton* Skeleton,
        UAnimSequenceBase* Animation, USkeletalMesh* Mesh, TSharedPtr<const FRPGCompiledBossMoveCard>& Out);
}
