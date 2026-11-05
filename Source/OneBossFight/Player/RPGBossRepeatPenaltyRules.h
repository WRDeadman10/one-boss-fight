// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"

/** Exponential, bounded score reduction for recent repeats. Unwired by design. */
namespace RPGBossRepeatPenalty
{
    inline double Weight(double BaseWeight,int32 RepeatCount,double PerRepeatScale=.7)
    {
        if(!FMath::IsFinite(BaseWeight)||!FMath::IsFinite(PerRepeatScale)||BaseWeight<0.||PerRepeatScale<0.||PerRepeatScale>1.||RepeatCount<0||RepeatCount>100)return 0.;
        double Result=BaseWeight;for(int32 I=0;I<RepeatCount;++I)Result*=PerRepeatScale;
        return FMath::Clamp(Result,0.,BaseWeight);
    }
}
