// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"
#include "Player/RPGBossParryFairRules.h"

/** Opt-in play-rate adjustment: slow a card only enough for its opening to satisfy the parry reaction window. */
namespace RPGBossTelegraphScale
{
    /** Returns a play rate <= CurrentRate; -1 means invalid data or the requested tell exceeds the slowdown cap. */
    inline double Rate(double ActiveStartSeconds,double CurrentRate,double RequiredRealSeconds,double MinRateScale=.4)
    {
        if (!FMath::IsFinite(ActiveStartSeconds)||!FMath::IsFinite(CurrentRate)||!FMath::IsFinite(RequiredRealSeconds)||!FMath::IsFinite(MinRateScale)||
            ActiveStartSeconds<=0.||CurrentRate<=0.||RequiredRealSeconds<=0.||MinRateScale<=0.||MinRateScale>1.) return -1.;
        const double Needed=FMath::Min(CurrentRate,ActiveStartSeconds/RequiredRealSeconds);
        const double Floor=CurrentRate*MinRateScale;
        if (!FMath::IsFinite(Needed)||Needed<Floor) return -1.;
        return Needed;
    }
}
