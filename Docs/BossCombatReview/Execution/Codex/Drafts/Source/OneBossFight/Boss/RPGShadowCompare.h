#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Boss/RPGTimelineCompiler.h"
#include "RPGShadowCompare.generated.h"

class URPGAttackTracker;
class FJsonObject;

namespace RPGTimeline
{
/** One copied sample at the tracker hook, including otherwise untracked active playback. */
struct FPassiveSnapshot
{
	FLegacySample Legacy;
	FString SourceAsset, CurrentSegmentAsset;
	FName Section;
	FName Slot;
	TOptional<int32> EngineInstance;
	TOptional<double> Position;
	TOptional<float> Rate;
	double GameTime = 0.;
};
ONEBOSSFIGHT_API FPassiveSnapshot CaptureAfterTracker(const URPGAttackTracker& Tracker);
DECLARE_MULTICAST_DELEGATE_OneParam(FAfterTracker, const FPassiveSnapshot&);

/** Passive identity adapter. Source artifacts are precompiled/preloaded, never loaded on a hit tick. */
class ONEBOSSFIGHT_API FPlaybackAdapter
{
public:
	TOptional<FObservation> Observe(const FPassiveSnapshot& Sample, const FRPGParticipantKey& Key,
		const TArray<TSharedPtr<const FCompiled>>& Artifacts);
private:
	uint64 Sequence = 0, Ordinal = 0;
	TOptional<FObservation> Last;
};
}

UCLASS()
class ONEBOSSFIGHT_API URPGCombatTimelineShadow : public UActorComponent
{
	GENERATED_BODY()
public:
	URPGCombatTimelineShadow();
	bool Configure(const TArray<TSharedPtr<const RPGTimeline::FCompiled>>& InTimelines, const FRPGParticipantKey& Key,
		TSharedPtr<const RPGCombatRegistry::FEpoch> InLease);
	bool BindTracker(URPGAttackTracker& Tracker, URPGCombatContextSubsystem& InContext);
	/** Lifecycle/variant adapter supplies identity. No gameplay calls or animation writes. */
	void ObserveAfterTracker(const RPGTimeline::FObservation& Observation);
	bool FlushReport(const TSharedRef<FJsonObject>& RunHeader, FString& OutPath);
	UFUNCTION(BlueprintPure) int32 GetRecordCount() const { return Records.Num(); }
	UFUNCTION(BlueprintPure) int32 GetDroppedRecords() const { return Dropped; }
protected:
	virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
	void OnSnapshot(const RPGTimeline::FPassiveSnapshot& Sample);
	TArray<TSharedPtr<const RPGTimeline::FCompiled>> Timelines;
	TSharedPtr<const RPGCombatRegistry::FEpoch> ContentLease;
	FRPGParticipantKey Participant;
	RPGTimeline::FCursor Cursor;
	RPGTimeline::FPlaybackAdapter Playback;
	TWeakObjectPtr<URPGAttackTracker> BoundTracker;
	TWeakObjectPtr<URPGCombatContextSubsystem> Context;
	FDelegateHandle ObservationHandle;
	TArray<TSharedPtr<FJsonObject>> Records;
	int32 Dropped = 0;
	static constexpr int32 MaxRecords = 4096;
};
