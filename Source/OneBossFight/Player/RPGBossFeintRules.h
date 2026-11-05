// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"

/** Feint probability rises as the player's measured reaction gets faster. Unwired by design. */
namespace RPGBossFeint
{
    inline double Chance(double PlayerReactionSeconds,double FastReactionSeconds=.15,double SlowReactionSeconds=.6,double MinChance=.05,double MaxChance=.45)
    {
        if(!FMath::IsFinite(PlayerReactionSeconds)||!FMath::IsFinite(FastReactionSeconds)||!FMath::IsFinite(SlowReactionSeconds)||!FMath::IsFinite(MinChance)||!FMath::IsFinite(MaxChance)||
            PlayerReactionSeconds<0.||FastReactionSeconds<0.||SlowReactionSeconds<=FastReactionSeconds||MinChance<0.||MaxChance<MinChance||MaxChance>1.)return 0.;
        const double T=FMath::Clamp((SlowReactionSeconds-PlayerReactionSeconds)/(SlowReactionSeconds-FastReactionSeconds),0.,1.);
        return FMath::Lerp(MinChance,MaxChance,T);
    }
}
