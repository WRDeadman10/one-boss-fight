// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"

/** Opt-in normalized music intensity from health and phase. Unwired by design. */
namespace RPGBossMusicIntensity
{
    inline double Evaluate(double HealthFraction,int32 Phase,double PhaseTwoBoost=.25)
    {
        if(!FMath::IsFinite(HealthFraction)||HealthFraction<0.||HealthFraction>1.||(Phase!=1&&Phase!=2)||!FMath::IsFinite(PhaseTwoBoost)||PhaseTwoBoost<0.||PhaseTwoBoost>1.)return 0.;
        return FMath::Clamp(1.-HealthFraction+(Phase==2?PhaseTwoBoost:0.),0.,1.);
    }
}
