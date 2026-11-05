// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"

/** Urgency weight for pressing when the player's stamina is low. Unwired by design. */
namespace RPGBossStaminaPressure
{
    inline double Pressure(double StaminaFraction,double LowThreshold=.4,double MaxPressure=1.)
    {
        if(!FMath::IsFinite(StaminaFraction)||!FMath::IsFinite(LowThreshold)||!FMath::IsFinite(MaxPressure)||StaminaFraction<0.||StaminaFraction>1.||LowThreshold<=0.||LowThreshold>1.||MaxPressure<0.||MaxPressure>3.)return 0.;
        return FMath::Clamp((LowThreshold-StaminaFraction)/LowThreshold,0.,1.)*MaxPressure;
    }
}
