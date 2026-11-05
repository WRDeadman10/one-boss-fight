// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"

/** Smooth bounded turn-rate interpolation across card-local start time. Unwired by design. */
namespace RPGBossTurnRateRamp
{
    inline double Rate(double ElapsedSeconds,double RampSeconds,double StartDegPerSecond,double EndDegPerSecond)
    {
        if(!FMath::IsFinite(ElapsedSeconds)||!FMath::IsFinite(RampSeconds)||!FMath::IsFinite(StartDegPerSecond)||!FMath::IsFinite(EndDegPerSecond)||
            ElapsedSeconds<0.||RampSeconds<=0.||StartDegPerSecond<0.||EndDegPerSecond<0.||StartDegPerSecond>720.||EndDegPerSecond>720.)return 0.;
        const double T=FMath::Clamp(ElapsedSeconds/RampSeconds,0.,1.);const double Smooth=T*T*(3.-2.*T);
        return FMath::Lerp(StartDegPerSecond,EndDegPerSecond,Smooth);
    }
}
