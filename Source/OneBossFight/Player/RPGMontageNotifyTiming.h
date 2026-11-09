// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimNotifies/AnimNotifyState.h"
#include "Player/RPGAttackTracker.h"
#include "RPGMontageNotifyTiming.generated.h"

/** Per-montage authored timing annotation. Runtime use is opt-in on URPGAttackTracker. */
UCLASS(BlueprintType, EditInlineNew, DefaultToInstanced)
class ONEBOSSFIGHT_API URPGANS_BossMoveTiming : public UAnimNotifyState
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Boss Move Timing") FName MoveId = NAME_None;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Boss Move Timing") float CommitTime = -1.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Boss Move Timing") float WindowStartTime = -1.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Boss Move Timing") float WindowEndTime = -1.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Boss Move Timing") float RecoveryEndTime = -1.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Boss Move Timing") float TrackTurnRate = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Boss Move Timing") bool bBranchStage = false;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Boss Move Timing") float BranchRange = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Boss Move Timing", meta = (ClampMin = "10", ClampMax = "360")) float BranchConeDegrees = 120.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Boss Move Timing") bool bAuthoredWindup = false;
};

/** Optional data contract for a reviewed montage-authored boss move annotation.
 *  No rows are authored by default: the existing RPGAttackTracker table remains authoritative. */
namespace RPGMontageNotifyTiming
{
	struct FAnnotation
	{
		FString MontageObjectPath;
		FName MoveId = NAME_None;
		float MontageLength = 0.f;
		float CommitTime = -1.f;
		float WindowStartTime = -1.f;
		float WindowEndTime = -1.f;
		float RecoveryEndTime = -1.f;
		float TrackTurnRate = 0.f;
		bool bBranchStage = false;
		float BranchRange = 0.f;
		float BranchConeDegrees = 120.f;
		bool bAuthoredWindup = false;

		FRPGAttackTiming ToAttackTiming(const FRPGAttackTiming& LegacyTiming) const;
	};

	enum class EPhase : uint8 { Tell, Committed, Active, Recovery, Complete };

	struct FObserver
	{
		bool bEnabled = false;
		bool bInitialized = false;
		FString MontageObjectPath;
		FName MoveId = NAME_None;
		EPhase Phase = EPhase::Tell;
		float LastPosition = -1.f;

		/** Starts/restarts only for a concrete montage object path and move identity. */
		bool Begin(const FString& InMontageObjectPath, FName InMoveId);
		/** Samples montage-local time; backwards seeks and non-finite positions fail closed. */
		bool Sample(float Position, const FAnnotation& Annotation, EPhase& OutPhase);
		void Reset();
	};

	/** Resolves and caches one montage's annotation result per AttackInstance. Invalid optional data falls back safely. */
	struct FCache
	{
		bool Resolve(bool bEnabled, const UAnimMontage* Montage, uint64 AttackInstanceId, FName MoveId, const FRPGAttackTiming& LegacyTiming,
			float LegacyBranchRange, float LegacyBranchConeDegrees, FRPGAttackTiming& OutTiming, float& OutBranchRange,
			float& OutBranchConeDegrees, FString& OutError, bool& bOutWarnOnce);
		void Reset();

	private:
		TWeakObjectPtr<const UAnimMontage> CachedMontage;
		uint64 CachedAttackInstanceId = MAX_uint64;
		bool bHasResult = false;
		bool bCachedValid = true;
		bool bCachedWarned = false;
		FRPGAttackTiming CachedTiming;
		float CachedBranchRange = 0.f;
		float CachedBranchConeDegrees = 120.f;
		FString CachedError;
	};

	ONEBOSSFIGHT_API bool Validate(const FAnnotation& Annotation, FString& OutError);
	/** Reads only this montage's authored timing notify-state instances; an empty result means table fallback. */
	ONEBOSSFIGHT_API bool CollectAnnotations(const UAnimMontage& Montage, TArray<FAnnotation>& OutAnnotations, FString& OutError);
	/** Returns false only for invalid/ambiguous authored data. Empty data or no exact match selects the legacy row. */
	bool SelectTiming(bool bEnabled, const TArray<FAnnotation>& Annotations, const FString& MontageObjectPath, FName MoveId,
		const FRPGAttackTiming& LegacyTiming, float LegacyBranchRange, float LegacyBranchConeDegrees, FRPGAttackTiming& OutTiming,
		float& OutBranchRange, float& OutBranchConeDegrees, FString& OutError);
}
