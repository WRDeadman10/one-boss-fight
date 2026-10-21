// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "RPGBossMusic.generated.h"

class UAudioComponent;
class URPGBossEncounter;
class URPGBossPhases;
class USoundBase;

/**
 * Boss fight music (Freeze 247, 311, 783, 801; SPEC_M3). One track per phase, a small state machine on top of the encounter:
 * the Phase 1 battle theme fades in when the boss wakes (player in the gate or boss hurt), crossfades to the Phase 2 choral climax when phase two starts, and fades out when the boss dies
 * (a shorter fade, the pack removes the boss a few seconds after death) or the encounter resets. Every transition is guarded by the state, so a repeated poll cannot repeat it: at most one voice per track.
 * Under -nosound no audio component exists; the state and the counters still follow the fight (the drivers test the logic, never audibility).
 */
UCLASS(ClassGroup = (Audio), meta = (BlueprintSpawnableComponent))
class ONEBOSSFIGHT_API URPGBossMusic : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGBossMusic();

	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	/** The Phase 1 battle theme (the name stays: the subsystem and the editor set it). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Music")
	TObjectPtr<USoundBase> Music;

	/** The Phase 2 climax. Empty = no swap, Phase 1 plays on. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Music")
	TObjectPtr<USoundBase> PhaseTwoMusic;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Music", meta = (ClampMin = "0", ClampMax = "2"))
	float Volume = 0.55f;

	/** Phase 2 measures about 4.7 dB louder than Phase 1 (RMS), so it plays 2.8 dB lower and still lands about 1.9 dB above it. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Music", meta = (ClampMin = "0", ClampMax = "2"))
	float PhaseTwoVolume = 0.40f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Music", meta = (ClampMin = "0"))
	float FadeInSeconds = 2.5f;

	/** The fade out after a reset or when the boss goes back to sleep. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Music", meta = (ClampMin = "0"))
	float FadeOutSeconds = 4.f;

	/** The fade out after the boss died: shorter than the delay after which the pack destroys the boss, so the end of the actor does not cut it. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Music", meta = (ClampMin = "0"))
	float VictoryFadeOutSeconds = 3.f;

	/** Equal power crossfade from Phase 1 to Phase 2: the two tracks have different tempos (73 and 112 BPM), a short overlap hides the beat clash under the roar. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Music", meta = (ClampMin = "0"))
	float CrossfadeSeconds = 2.f;

	/** Where in the Phase 2 file it starts (s). 0 = its quiet intro; about 37 enters on the climax (decided by ear). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Music", meta = (ClampMin = "0"))
	float PhaseTwoStartOffsetSeconds = 0.f;

	/** Swap to Phase 2 at the phase two threshold (also needs rpg.Legend 1). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Music")
	bool bSwapAtPhaseTwo = true;

	/** True while a track is requested (the state is not None). */
	UFUNCTION(BlueprintPure, Category = "Music")
	bool IsPlaying() const { return ActiveTrack != ETrack::None; }

	/** "None", "Phase1" or "Phase2". */
	UFUNCTION(BlueprintPure, Category = "Music")
	FString GetActiveTrackName() const;

	/** How many times a track was started (1 = Phase 1, 2 = Phase 2). */
	UFUNCTION(BlueprintPure, Category = "Music")
	int32 GetStartCount(int32 Track) const { return Track == 1 ? StartCountPhase1 : (Track == 2 ? StartCountPhase2 : 0); }

	UFUNCTION(BlueprintPure, Category = "Music")
	int32 GetSwapCount() const { return SwapCount; }

	UFUNCTION(BlueprintPure, Category = "Music")
	int32 GetStopCount() const { return StopCount; }

	/** True while an audio component really plays (always false under -nosound). */
	UFUNCTION(BlueprintPure, Category = "Music")
	bool IsAnyComponentPlaying() const;

	/** Tests: the start path of the first track, as the poll calls it (a second call must change nothing). */
	UFUNCTION(BlueprintCallable, Category = "Music")
	void StartForTest();

private:
	enum class ETrack : uint8 { None, Phase1, Phase2 };

	UPROPERTY(Transient)
	TObjectPtr<UAudioComponent> PlayerPhase1;

	UPROPERTY(Transient)
	TObjectPtr<UAudioComponent> PlayerPhase2;

	UPROPERTY(Transient)
	TObjectPtr<URPGBossEncounter> Encounter;

	UPROPERTY(Transient)
	TObjectPtr<URPGBossPhases> Phases;

	ETrack ActiveTrack = ETrack::None;
	int32 StartCountPhase1 = 0;
	int32 StartCountPhase2 = 0;
	int32 SwapCount = 0;
	int32 StopCount = 0;

	UAudioComponent* EnsurePlayer(ETrack Track);
	void StartTrack(ETrack Track);
	void SwapToPhaseTwo();
	void StopAll(bool bBossDead);
};
