// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"

/**
 * Frame-time statistics for the performance gate.
 * Release target: average >= 120 FPS AND 99th-percentile frame time <= 8.33 ms.
 * Average FPS alone hides spikes, so both are always reported.
 */
struct ONEBOSSFIGHT_API FRPGFrameStats
{
	int32 FrameCount = 0;
	double TotalSeconds = 0.0;

	/** FrameCount / TotalSeconds (not the mean of per-frame FPS). */
	double AverageFPS = 0.0;
	double AverageMs = 0.0;
	double MinMs = 0.0;
	double MaxMs = 0.0;
	double MedianMs = 0.0;
	double P95Ms = 0.0;
	double P99Ms = 0.0;

	/** Frames slower than BudgetMs. */
	int32 FramesOverBudget = 0;
	double BudgetMs = 1000.0 / 120.0;

	/** Frame budget in ms for a target frame rate. */
	static double BudgetForFPS(double TargetFPS) { return 1000.0 / TargetFPS; }

	/** Computes statistics from per-frame times in milliseconds. Empty input yields zeros. */
	static FRPGFrameStats Compute(const TArray<double>& FrameTimesMs, double InBudgetMs = 1000.0 / 120.0);

	/** Nearest-rank percentile (P in 0..100) of an ascending-sorted array. Empty input returns 0. */
	static double PercentileSorted(const TArray<double>& SortedMs, double P);

	/** True when both the average-FPS and 99th-percentile gates pass for the given target. */
	bool MeetsTarget(double TargetFPS = 120.0) const;

	FString ToLogString() const;
};
