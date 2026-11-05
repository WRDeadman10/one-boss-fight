// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"

/** Opt-in attack-rate multiplier that decreases after repeated whiffs and remains bounded. */
namespace RPGBossFatigue
{
    struct FConfig { int32 GraceWhiffs=2; double ReductionPerWhiff=.05, MinRateScale=.7; };
    inline double RateScale(int32 ConsecutiveWhiffs,const FConfig& C=FConfig())
    {
        if (ConsecutiveWhiffs<0||C.GraceWhiffs<0||!FMath::IsFinite(C.ReductionPerWhiff)||!FMath::IsFinite(C.MinRateScale)||
            C.ReductionPerWhiff<0.||C.ReductionPerWhiff>1.||C.MinRateScale<=0.||C.MinRateScale>1.) return -1.;
        const int32 FatigueWhiffs=FMath::Max(0,ConsecutiveWhiffs-C.GraceWhiffs);
        return FMath::Max(C.MinRateScale,1.-double(FatigueWhiffs)*C.ReductionPerWhiff);
    }
}
