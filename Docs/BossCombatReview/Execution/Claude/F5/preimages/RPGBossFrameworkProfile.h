// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "Player/RPGBossMoveCard.h"
#include "RPGBossFrameworkProfile.generated.h"
class USkeletalMesh;
class UAnimInstance;
class APawn;
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
};
namespace RPGFramework
{
    ONEBOSSFIGHT_API bool ValidateProfile(const URPGBossFrameworkProfile& Profile,FString& Error);
    ONEBOSSFIGHT_API bool ResolveProfile(URPGBossFrameworkProfile* Profile,TUniquePtr<FRPGFrameworkDependencies>& Out,FString& Error);
    ONEBOSSFIGHT_API bool HasSlotNode(UAnimInstance* Instance,FName Slot);
}
