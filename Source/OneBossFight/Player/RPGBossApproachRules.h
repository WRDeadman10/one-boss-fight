// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"

/** Smooth distance profile for a gap-closer warp, expressed as fractions of total distance. */
namespace RPGBossApproach
{
    inline double StepFraction(double T01)
    {
        if (!FMath::IsFinite(T01)) return 0.;
        const double T = FMath::Clamp(T01, 0., 1.);
        return T * T * (3. - 2. * T);
    }

    /** Distance covered between normalized times T0 and T1; additive across any partition. */
    inline double StepCm(double TotalCm, double T0, double T1)
    {
        if (!FMath::IsFinite(TotalCm) || !FMath::IsFinite(T0) || !FMath::IsFinite(T1) ||
            TotalCm < 0. || T0 < 0. || T1 > 1. || T1 < T0)
        {
            return 0.;
        }
        return FMath::Max(0., TotalCm * (StepFraction(T1) - StepFraction(T0))); // rounding at the ends of smoothstep can give a difference of -1e-13: the rule never reports a negative step (lead, Q91-Q95 sweep)
    }

    /** Peak speed of smoothstep is 1.5 times average speed. */
    inline double PeakSpeedCm(double TotalCm, double DurationSeconds)
    {
        if (!FMath::IsFinite(TotalCm) || !FMath::IsFinite(DurationSeconds) ||
            TotalCm < 0. || DurationSeconds <= 0.)
        {
            return 0.;
        }
        return 1.5 * TotalCm / DurationSeconds;
    }
}
