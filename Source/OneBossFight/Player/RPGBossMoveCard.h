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

USTRUCT(BlueprintType)
struct FRPGBossMoveWindow
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere) FName WindowId;
    UPROPERTY(EditAnywhere) FName HitGroup;
    UPROPERTY(EditAnywhere) float StartSeconds = 0.f;
    UPROPERTY(EditAnywhere) float EndSeconds = 0.f;
    /** A swept capsule segment defined by TWO distinct authored socket or bone names; no proximity fallback. */
    UPROPERTY(EditAnywhere) FName SocketA;
    UPROPERTY(EditAnywhere) FName SocketB;
    UPROPERTY(EditAnywhere) float RadiusCm = 0.f;
    /** BOSS-HIT-010: a SECONDARY window (shockwave / ground splash). It may overlap the direct windows in time, must share a HitGroup with a direct window, and is always processed AFTER the direct windows of the same tick, so the shared hit key makes a simultaneous contact apply the direct hit only. */
    UPROPERTY(EditAnywhere) bool bSecondary = false;
    /** BOSS-HIT-011: a RING window (ground shockwave around the boss, no sockets, no baked samples). Its front starts at RingStartRadiusCm when the window opens and moves outward at RingSpeedCmPerSecond; the band behind the front is RingThicknessCm wide; the wave reaches RingHeightCm above the ground (a target above that is missed). The ring ends with the window. */
    UPROPERTY(EditAnywhere) bool bRing = false;
    UPROPERTY(EditAnywhere) float RingStartRadiusCm = 0.f;
    UPROPERTY(EditAnywhere) float RingSpeedCmPerSecond = 0.f;
    UPROPERTY(EditAnywhere) float RingThicknessCm = 0.f;
    UPROPERTY(EditAnywhere) float RingHeightCm = 0.f;
    /** BOSS-HIT-012: a GRAB window. It is a blade window (sockets, radius) whose contact catches the target instead of damaging it: the victim is attached to GrabAttachSocket (a boss socket or bone) with movement off until GrabReleaseSeconds (card time, after the window, within the recovery), then released to the floor and the card's HPDamage is applied. Any abort of the attack releases the victim at once, without damage. At most one grab window per card. */
    UPROPERTY(EditAnywhere) bool bGrab = false;
    UPROPERTY(EditAnywhere) FName GrabAttachSocket;
    UPROPERTY(EditAnywhere) float GrabReleaseSeconds = 0.f;
    /** Optional (empty = live sockets): the baked blade path of this window, strictly ordered, covering [StartSeconds, EndSeconds], inside the clip. */
    UPROPERTY(EditAnywhere) TArray<FRPGBakedBladeSample> BakedSamples;
};

USTRUCT(BlueprintType)
struct FRPGBossMoveCardSpec
{
    GENERATED_BODY()
    /** Zero-valued draft is deliberately invalid, never a runnable default. */
    UPROPERTY(EditAnywhere) int32 Schema = 0;
    UPROPERTY(EditAnywhere) FName MoveId;
    UPROPERTY(EditAnywhere) FName FamilyId;
    UPROPERTY(EditAnywhere) FName PhaseId;
    UPROPERTY(EditAnywhere) TSoftObjectPtr<USkeleton> Skeleton;
    /** Exactly ONE source. No load or fallback inside pure validation. */
    UPROPERTY(EditAnywhere) TSoftObjectPtr<UAnimSequence> Sequence;
    UPROPERTY(EditAnywhere) TSoftObjectPtr<UAnimMontage> Montage;
    UPROPERTY(EditAnywhere) FName SlotName;
    /** None explicitly means the full source, otherwise a montage section is required. */
    UPROPERTY(EditAnywhere) FName SectionName;
    UPROPERTY(EditAnywhere) float PlayRate = 0.f;
    UPROPERTY(EditAnywhere) float CommitSeconds = 0.f;
    UPROPERTY(EditAnywhere) float ActiveStartSeconds = 0.f;
    UPROPERTY(EditAnywhere) float ActiveEndSeconds = 0.f;
    UPROPERTY(EditAnywhere) float RecoveryEndSeconds = 0.f;
    UPROPERTY(EditAnywhere) float TrackDegreesPerSecond = 0.f;
    /** BOSS-ANM-006 (0 = off): bounded warp. Between WarpStartSeconds and WarpEndSeconds (card time, after the commit, inside the active end) the boss closes on the target down to WarpStandoffCm and turns toward it, by at most WarpMaxDistanceCm and WarpMaxAngleDegrees in total. The clip stays in place (no root motion); the boss actor moves. */
    UPROPERTY(EditAnywhere) float WarpStartSeconds = 0.f;
    UPROPERTY(EditAnywhere) float WarpEndSeconds = 0.f;
    UPROPERTY(EditAnywhere) float WarpMaxDistanceCm = 0.f;
    UPROPERTY(EditAnywhere) float WarpMaxAngleDegrees = 0.f;
    UPROPERTY(EditAnywhere) float WarpStandoffCm = 0.f;
    UPROPERTY(EditAnywhere) float MinRangeCm = 0.f;
    UPROPERTY(EditAnywhere) float MaxRangeCm = 0.f;
    UPROPERTY(EditAnywhere) float FrontConeDegrees = 0.f;
    /** BOSS-AWR-005: the card is refused when the vertical separation to the target is above this many cm (floor-plane cards: a target on a ledge or in the air). 0 = no vertical limit (every card authored before this field). */
    UPROPERTY(EditAnywhere) float MaxVerticalDeltaCm = 0.f;
    UPROPERTY(EditAnywhere) float HPDamage = 0.f;
    /** First backend is in-place only. True is a named unsupported capability, not silently ignored. */
    UPROPERTY(EditAnywhere) bool bUsesRootMotion = false;
    UPROPERTY(EditAnywhere) TArray<FRPGBossMoveWindow> Windows;
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
