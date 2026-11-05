// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"

/** Pure stamina rules for a parry press; a successful parry refunds half its cost. */
namespace RPGParryCost
{
    inline bool CanPress(double Stamina, double Cost)
    {
        return FMath::IsFinite(Stamina) && FMath::IsFinite(Cost) && Stamina >= 0. && Cost >= 0. && Stamina >= Cost;
    }

    /** Apply the cost after an attempted press. Invalid values fail closed to zero stamina. */
    inline double StaminaAfter(double Stamina, double Cost, bool bParried)
    {
        if (!FMath::IsFinite(Stamina) || !FMath::IsFinite(Cost) || Stamina < 0. || Cost < 0.) return 0.;
        const double NetCost = bParried ? Cost * .5 : Cost;
        return FMath::Max(0., Stamina - NetCost);
    }

    /** Refund half a paid parry cost without exceeding the current maximum stamina. Invalid input fails closed. */
    inline double ParryRefund(double Stamina,double MaxStamina,double Cost)
    {
        if (!FMath::IsFinite(Stamina)||!FMath::IsFinite(MaxStamina)||!FMath::IsFinite(Cost)||Stamina<0.||MaxStamina<0.||Cost<0.) return 0.;
        return FMath::Min(MaxStamina,Stamina+Cost*.5);
    }
}
