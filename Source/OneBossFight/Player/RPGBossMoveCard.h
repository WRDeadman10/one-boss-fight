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
    UPROPERTY(EditAnywhere) float MinRangeCm = 0.f;
    UPROPERTY(EditAnywhere) float MaxRangeCm = 0.f;
    UPROPERTY(EditAnywhere) float FrontConeDegrees = 0.f;
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
