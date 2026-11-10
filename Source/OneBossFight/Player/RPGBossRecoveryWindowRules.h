// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"
#include "Player/RPGParryGradeRules.h"

/** Opt-in recovery window after a parried boss hit. Returns -1 for invalid inputs/configuration. */
namespace RPGBossRecoveryWindow
{
    struct FConfig
    {
        double PerfectFraction=.65, GoodFraction=.45, LateFraction=.25;
        double MinSeconds=.05, MaxSeconds=1.5;
        bool IsValid() const
        {
            return FMath::IsFinite(PerfectFraction)&&FMath::IsFinite(GoodFraction)&&FMath::IsFinite(LateFraction)&&
                PerfectFraction>=0.&&PerfectFraction<=1.&&GoodFraction>=0.&&GoodFraction<=1.&&LateFraction>=0.&&LateFraction<=1.&&
                PerfectFraction>=GoodFraction&&GoodFraction>=LateFraction&&
                FMath::IsFinite(MinSeconds)&&FMath::IsFinite(MaxSeconds)&&MinSeconds>0.&&MaxSeconds>=MinSeconds;
        }
    };
    inline double Seconds(RPGParryGrade::EGrade Grade,double CardRecoverySeconds,const FConfig& Config=FConfig())
    {
        if (!Config.IsValid()||!FMath::IsFinite(CardRecoverySeconds)||CardRecoverySeconds<=0.) return -1.;
        double Fraction=0.;
        switch (Grade)
        {
        case RPGParryGrade::EGrade::Perfect: Fraction=Config.PerfectFraction; break;
        case RPGParryGrade::EGrade::Good: Fraction=Config.GoodFraction; break;
        case RPGParryGrade::EGrade::Late: Fraction=Config.LateFraction; break;
        default: return -1.;
        }
        return FMath::Clamp(CardRecoverySeconds*Fraction,Config.MinSeconds,Config.MaxSeconds);
    }
    /** Converts the opt-in profile scale to an extra recovery duration. Zero is explicitly off. */
    inline double ScaledSeconds(RPGParryGrade::EGrade Grade,double CardRecoverySeconds,double Scale,const FConfig& Config=FConfig())
    {
        if (!FMath::IsFinite(Scale)||Scale<0.||Scale>3.) return -1.;
        if (Scale==0.) return 0.;
        if (!FMath::IsFinite(CardRecoverySeconds)||CardRecoverySeconds<=0.) return -1.;
        return Seconds(Grade,CardRecoverySeconds*Scale,Config);
    }
}
