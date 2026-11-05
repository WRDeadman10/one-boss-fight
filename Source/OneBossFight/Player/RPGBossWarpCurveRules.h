// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"

/** Normalized bounded-distance curves. Every mode starts at 0 and ends at 1. Unwired by design. */
namespace RPGBossWarpCurve
{
    enum class ECurve:uint8 { Linear, Smooth, Overshoot };
    inline double Fraction(double T01,ECurve Curve,double OvershootAmount=.12)
    {
        if(!FMath::IsFinite(T01)||!FMath::IsFinite(OvershootAmount)||OvershootAmount<0.||OvershootAmount>.5)return 0.;
        const double T=FMath::Clamp(T01,0.,1.);
        switch(Curve)
        {
        case ECurve::Linear:return T;
        case ECurve::Smooth:return T*T*(3.-2.*T);
        case ECurve::Overshoot:{const double X=T-1.,Back=OvershootAmount*10.;return 1.+(Back+1.)*X*X*X+Back*X*X;} // ease-out-back: passes 1 before T=1 and returns to it (lead fix: the sine form never exceeded 1, so it was not an overshoot)
        default:return 0.;
        }
    }
}
