// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Benchmark/RPGFrameStats.h"
#include "RPGBenchmarkRunner.generated.h"

class ACameraActor;

/**
 * Repeatable frame-time benchmark. Place one in a map and launch with -RPGBenchmark
 * (add -RPGBenchmarkQuit to exit when done). It orbits a camera around this actor's location,
 * discards the warmup, records raw per-frame times, and writes frames.csv and summary.json to
 * Saved/Benchmark/<label>_<timestamp>/ so runs can be compared across milestones.
 *
 * It temporarily removes the frame-rate cap and VSync so the measurement is not artificially limited.
 */
UCLASS()
class ONEBOSSFIGHT_API ARPGBenchmarkRunner : public AActor
{
	GENERATED_BODY()

public:
	ARPGBenchmarkRunner();

	/** Starts a run. Ignored if one is already running. */
	UFUNCTION(BlueprintCallable, Category = "Benchmark")
	void StartBenchmark();

	/** Ends a run early; results are written only for a completed run. */
	UFUNCTION(BlueprintCallable, Category = "Benchmark")
	void AbortBenchmark();

	bool IsRunning() const { return bRunning; }
	const FRPGFrameStats& GetLastStats() const { return LastStats; }

	/** Seconds ignored at the start (shader compile, streaming, camera settle). */
	UPROPERTY(EditAnywhere, Category = "Benchmark", meta = (ClampMin = "0"))
	float WarmupSeconds = 5.f;

	/** Seconds of recorded frames. */
	UPROPERTY(EditAnywhere, Category = "Benchmark", meta = (ClampMin = "1"))
	float DurationSeconds = 60.f;

	UPROPERTY(EditAnywhere, Category = "Benchmark|Camera", meta = (ClampMin = "100"))
	float OrbitRadius = 1800.f;

	UPROPERTY(EditAnywhere, Category = "Benchmark|Camera")
	float OrbitHeight = 450.f;

	/** Seconds per full revolution. */
	UPROPERTY(EditAnywhere, Category = "Benchmark|Camera", meta = (ClampMin = "1"))
	float OrbitPeriodSeconds = 30.f;

	/** Start automatically on BeginPlay, in addition to the -RPGBenchmark command-line switch. */
	UPROPERTY(EditAnywhere, Category = "Benchmark")
	bool bAutoStart = false;

	/** Label used in the output folder name, e.g. "baseline_defaults". Overridden by -RPGBenchmarkLabel=Name. */
	UPROPERTY(EditAnywhere, Category = "Benchmark")
	FString RunLabel = TEXT("run");

	/**
	 * Fight mode (also -RPGBenchmarkFight): instead of an empty arena, run the real encounter on the pack. A bot drives Greystone through the pack's own abilities
	 * (enter combat, melee, dodge), walks him up to Sevarog and keeps him alive, pushes the boss into phase 2 at Phase2AtSeconds, and heals the boss so the fight
	 * never ends. The view stays the player's camera. Boss animation, spells, hit effects and the HUD all run, so this is the worst case the game has.
	 */
	UPROPERTY(EditAnywhere, Category = "Benchmark|Fight")
	bool bFightMode = false;

	/** Seconds after the benchmark starts when the boss is brought to phase 2. */
	UPROPERTY(EditAnywhere, Category = "Benchmark|Fight", meta = (ClampMin = "0"))
	float Phase2AtSeconds = 30.f;

	/** Target for pass/fail in the summary. */
	UPROPERTY(EditAnywhere, Category = "Benchmark", meta = (ClampMin = "1"))
	float TargetFPS = 60.f; // the final release gate: 60 FPS average and p99 <= 16.67 ms

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
	virtual void Tick(float DeltaSeconds) override;

private:
	void FinishBenchmark();
	void TickFight(double ElapsedSeconds, float DeltaSeconds);
	void WriteResults(const FRPGFrameStats& Stats) const;
	void ApplyUncappedFrameRate();
	void RestoreFrameRate();
	void UpdateCamera(double ElapsedSeconds);

	bool bRunning = false;
	double StartTime = 0.0;
	double LastTickTime = 0.0;
	TArray<double> FrameTimesMs;

	// Engine-reported per-frame thread times (ms), sampled alongside the wall-clock frame time.
	// They overlap in the pipeline, so they identify the bottleneck; they are not summed.
	TArray<double> GameThreadMs;
	TArray<double> RenderThreadMs;
	TArray<double> GpuMs;

	FRPGFrameStats LastStats;
	FString ResolvedLabel;

	UPROPERTY(Transient)
	TObjectPtr<ACameraActor> BenchmarkCamera;

	// Fight mode state.
	TWeakObjectPtr<AActor> FightBoss;
	TWeakObjectPtr<APawn> FightPlayer;
	bool bFightStarted = false;
	bool bPhase2Forced = false;

	/** Console variables applied by -RPGBenchmarkCvars="name=value;name=value" (performance experiments, works in Shipping), as "name=value" with a note when unknown; written to summary.json. */
	FString AppliedCvars;
	/** -RPGBenchmarkProfileGPUAt=<seconds>: runs ProfileGPU once at that benchmark time (Development builds only; the pass table goes to the log). */
	float ProfileGpuAt = -1.f;
	bool bProfileGpuDone = false;
	float BotAttackTimer = 0.f;
	float BotDodgeTimer = 0.f;
	float BotHealTimer = 0.f;
	bool bBotInCombat = false;
	FVector FightCenter = FVector::ZeroVector;

	// Saved cvar/engine state restored when the run ends.
	bool bFrameRateOverridden = false;
	float SavedMaxFPS = 0.f;
	int32 SavedVSync = 1;
	bool bSavedSmoothFrameRate = false;
	bool bSavedFixedFrameRate = false;
};
