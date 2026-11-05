// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"

/** Pure timing grades for a contact inside the player's parry window. */
namespace RPGParryGrade
{
    enum class EGrade : uint8
    {
        None,
        Perfect,
        Good,
        Late
    };

    /**
     * Classify the contact offset from the opening instant. The first 40% is Perfect,
     * the next 40% Good, and the remaining valid window Late. Invalid inputs fail closed.
     */
    inline EGrade Grade(double OffsetSeconds, double WindowSeconds)
    {
        if (!FMath::IsFinite(OffsetSeconds) || !FMath::IsFinite(WindowSeconds) ||
            OffsetSeconds < 0. || WindowSeconds <= 0. || OffsetSeconds >= WindowSeconds)
        {
            return EGrade::None;
        }

        const double ClampedOffset = FMath::Clamp(OffsetSeconds, 0., WindowSeconds);
        const double Fraction = ClampedOffset / WindowSeconds;
        if (Fraction < .4) return EGrade::Perfect;
        if (Fraction < .8) return EGrade::Good;
        return EGrade::Late;
    }

    inline double PostureScale(EGrade TimingGrade)
    {
        switch (TimingGrade)
        {
        case EGrade::Perfect: return 1.;
        case EGrade::Good: return .6;
        case EGrade::Late: return .3;
        case EGrade::None:
        default: return 0.;
        }
    }
}
