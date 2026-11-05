// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"

/** One normalized difficulty scalar mapped to bounded damage, speed, and tell-rate scales. Unwired by design. */
namespace RPGBossDifficulty
{
    struct FConfig { double DamageMin=.8,DamageMax=1.25,SpeedMin=.9,SpeedMax=1.2,TelegraphMin=.85,TelegraphMax=1.15; };
    struct FScales { double Damage=1.,Speed=1.,Telegraph=1.; };
    inline bool IsValid(const FConfig& C)
    {
        return FMath::IsFinite(C.DamageMin)&&FMath::IsFinite(C.DamageMax)&&FMath::IsFinite(C.SpeedMin)&&FMath::IsFinite(C.SpeedMax)&&FMath::IsFinite(C.TelegraphMin)&&FMath::IsFinite(C.TelegraphMax)&&
            C.DamageMin>0.&&C.DamageMax>=C.DamageMin&&C.SpeedMin>0.&&C.SpeedMax>=C.SpeedMin&&C.TelegraphMin>0.&&C.TelegraphMax>=C.TelegraphMin&&
            C.DamageMax<=3.&&C.SpeedMax<=2.&&C.TelegraphMax<=2.;
    }
    inline FScales Evaluate(double Difficulty01,const FConfig& C=FConfig())
    {
        if(!FMath::IsFinite(Difficulty01)||Difficulty01<0.||Difficulty01>1.||!IsValid(C))return FScales();
        return {FMath::Lerp(C.DamageMin,C.DamageMax,Difficulty01),FMath::Lerp(C.SpeedMin,C.SpeedMax,Difficulty01),FMath::Lerp(C.TelegraphMin,C.TelegraphMax,Difficulty01)};
    }
}
