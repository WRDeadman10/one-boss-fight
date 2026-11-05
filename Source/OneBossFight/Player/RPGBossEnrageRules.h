// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"

/** Opt-in bounded linear enrage scales over elapsed fight time. Unwired by design. */
namespace RPGBossEnrage
{
    struct FConfig
    {
        double RampSeconds=120.;
        double MaxDamageScale=1.5;
        double MaxSpeedScale=1.25;
        bool IsValid() const
        {
            return FMath::IsFinite(RampSeconds)&&FMath::IsFinite(MaxDamageScale)&&FMath::IsFinite(MaxSpeedScale)&&
                RampSeconds>0.&&MaxDamageScale>=1.&&MaxDamageScale<=3.&&MaxSpeedScale>=1.&&MaxSpeedScale<=2.;
        }
    };
    inline double Progress(double ElapsedSeconds,const FConfig& C=FConfig())
    {
        if(!C.IsValid()||!FMath::IsFinite(ElapsedSeconds)||ElapsedSeconds<=0.)return 0.;
        return FMath::Clamp(ElapsedSeconds/C.RampSeconds,0.,1.);
    }
    inline double DamageScale(double ElapsedSeconds,const FConfig& C=FConfig())
    {
        return C.IsValid()?1.+(C.MaxDamageScale-1.)*Progress(ElapsedSeconds,C):1.;
    }
    inline double SpeedScale(double ElapsedSeconds,const FConfig& C=FConfig())
    {
        return C.IsValid()?1.+(C.MaxSpeedScale-1.)*Progress(ElapsedSeconds,C):1.;
    }
}
