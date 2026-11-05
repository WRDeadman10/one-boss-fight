// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"

/** Opt-in low-health weight ramp. A multiplier of 1 means unchanged behavior. Unwired by design. */
namespace RPGBossDesperation
{
    inline double WeightMultiplier(double HealthFraction,double StartFraction=.35,double MaxMultiplier=1.5)
    {
        if(!FMath::IsFinite(HealthFraction)||!FMath::IsFinite(StartFraction)||!FMath::IsFinite(MaxMultiplier)||
            HealthFraction<0.||HealthFraction>1.||StartFraction<=0.||StartFraction>1.||MaxMultiplier<1.||MaxMultiplier>3.)return 1.;
        const double Progress=FMath::Clamp((StartFraction-HealthFraction)/StartFraction,0.,1.);
        return 1.+(MaxMultiplier-1.)*Progress;
    }
}
