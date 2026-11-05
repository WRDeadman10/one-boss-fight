// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"

/** Opt-in arena-edge pressure and inward heading. Unwired by design. */
namespace RPGBossArenaEdge
{
    struct FResult { double Pressure=0.; FVector2D Inward=FVector2D::ZeroVector; };
    inline FResult Evaluate(FVector2D Boss,FVector2D Center,double ArenaRadiusCm,double MarginCm)
    {
        FResult Out;
        if(Boss.ContainsNaN()||Center.ContainsNaN()||!FMath::IsFinite(ArenaRadiusCm)||!FMath::IsFinite(MarginCm)||ArenaRadiusCm<=0.||MarginCm<=0.)return Out;
        const FVector2D ToCenter=Center-Boss;const double Distance=ToCenter.Size();
        if(!FMath::IsFinite(Distance)||Distance<=SMALL_NUMBER)return Out;
        const double EdgeDistance=ArenaRadiusCm-Distance;
        Out.Pressure=FMath::Clamp((MarginCm-EdgeDistance)/MarginCm,0.,1.);
        Out.Inward=ToCenter/Distance;
        return Out;
    }
}
