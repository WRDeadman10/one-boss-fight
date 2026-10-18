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

	/** Target for pass/fail in the summary. */
	UPROPERTY(EditAnywhere, Category = "Benchmark", meta = (ClampMin = "1"))
	float TargetFPS = 120.f;

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
	virtual void Tick(float DeltaSeconds) override;

private:
	void FinishBenchmark();
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

	// Saved cvar/engine state restored when the run ends.
	bool bFrameRateOverridden = false;
	float SavedMaxFPS = 0.f;
	int32 SavedVSync = 1;
	bool bSavedSmoothFrameRate = false;
	bool bSavedFixedFrameRate = false;
};
