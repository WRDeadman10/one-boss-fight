// Copyright One Boss Fight. All Rights Reserved.

#include "Benchmark/RPGFrameStats.h"

double FRPGFrameStats::PercentileSorted(const TArray<double>& SortedMs, double P)
{
	if (SortedMs.IsEmpty())
	{
		return 0.0;
	}

	// Nearest-rank: smallest value such that at least P percent of samples are <= it.
	const double Clamped = FMath::Clamp(P, 0.0, 100.0);
	const int32 Rank = FMath::CeilToInt(Clamped / 100.0 * SortedMs.Num());
	const int32 Index = FMath::Clamp(Rank - 1, 0, SortedMs.Num() - 1);
	return SortedMs[Index];
}

FRPGFrameStats FRPGFrameStats::Compute(const TArray<double>& FrameTimesMs, double InBudgetMs)
{
	FRPGFrameStats Stats;
	Stats.BudgetMs = InBudgetMs;
	Stats.FrameCount = FrameTimesMs.Num();
	if (Stats.FrameCount == 0)
	{
		return Stats;
	}

	double SumMs = 0.0;
	for (const double Ms : FrameTimesMs)
	{
		SumMs += Ms;
		if (Ms > InBudgetMs)
		{
			++Stats.FramesOverBudget;
		}
	}

	TArray<double> Sorted = FrameTimesMs;
	Sorted.Sort();

	Stats.TotalSeconds = SumMs / 1000.0;
	Stats.AverageMs = SumMs / Stats.FrameCount;
	Stats.AverageFPS = Stats.TotalSeconds > 0.0 ? Stats.FrameCount / Stats.TotalSeconds : 0.0;
	Stats.MinMs = Sorted[0];
	Stats.MaxMs = Sorted.Last();
	Stats.MedianMs = PercentileSorted(Sorted, 50.0);
	Stats.P95Ms = PercentileSorted(Sorted, 95.0);
	Stats.P99Ms = PercentileSorted(Sorted, 99.0);
	return Stats;
}

bool FRPGFrameStats::MeetsTarget(double TargetFPS) const
{
	return FrameCount > 0 && AverageFPS >= TargetFPS && P99Ms <= BudgetForFPS(TargetFPS);
}

FString FRPGFrameStats::ToLogString() const
{
	return FString::Printf(
		TEXT("frames=%d avgFPS=%.1f avg=%.2fms median=%.2fms p95=%.2fms p99=%.2fms max=%.2fms over%.2fms=%d (%.1f%%)"),
		FrameCount, AverageFPS, AverageMs, MedianMs, P95Ms, P99Ms, MaxMs, BudgetMs, FramesOverBudget,
		FrameCount > 0 ? 100.0 * FramesOverBudget / FrameCount : 0.0);
}
