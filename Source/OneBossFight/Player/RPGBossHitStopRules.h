// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"
#include "Player/RPGParryGradeRules.h"

/** Opt-in bounded hit-stop duration by parry grade. Unwired by design. */
namespace RPGBossHitStop
{
    struct FConfig { double PerfectSeconds=.12,GoodSeconds=.08,LateSeconds=.04,MaxSeconds=.2; };
    inline bool IsValid(const FConfig& C)
    {
        return FMath::IsFinite(C.PerfectSeconds)&&FMath::IsFinite(C.GoodSeconds)&&FMath::IsFinite(C.LateSeconds)&&FMath::IsFinite(C.MaxSeconds)&&
            C.PerfectSeconds>=C.GoodSeconds&&C.GoodSeconds>=C.LateSeconds&&C.LateSeconds>=0.&&C.MaxSeconds>=0.&&C.PerfectSeconds<=C.MaxSeconds;
    }
    inline double Seconds(RPGParryGrade::EGrade Grade,const FConfig& C=FConfig())
    {
        if(!IsValid(C))return 0.;
        switch(Grade)
        {
        case RPGParryGrade::EGrade::Perfect:return C.PerfectSeconds;
        case RPGParryGrade::EGrade::Good:return C.GoodSeconds;
        case RPGParryGrade::EGrade::Late:return C.LateSeconds;
        default:return 0.;
        }
    }
}
