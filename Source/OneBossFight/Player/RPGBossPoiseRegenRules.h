// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"

/** Bounded poise regeneration ramp after a post-hit delay. Unwired by design. */
namespace RPGBossPoiseRegen
{
    inline double Rate(double BasePerSecond,double SecondsSinceHit,double DelaySeconds,double RampSeconds,double MaxScale=1.)
    {
        if(!FMath::IsFinite(BasePerSecond)||!FMath::IsFinite(SecondsSinceHit)||!FMath::IsFinite(DelaySeconds)||!FMath::IsFinite(RampSeconds)||!FMath::IsFinite(MaxScale)||
            BasePerSecond<0.||BasePerSecond>1.e6||SecondsSinceHit<0.||DelaySeconds<0.||DelaySeconds>1.e6||RampSeconds<=0.||RampSeconds>1.e6||MaxScale<1.||MaxScale>3.)return 0.;
        if(SecondsSinceHit<DelaySeconds)return 0.;
        const double T=FMath::Clamp((SecondsSinceHit-DelaySeconds)/RampSeconds,0.,1.);
        return BasePerSecond*(1.+(MaxScale-1.)*T);
    }
}
