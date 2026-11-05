// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"

/** Pure timing check for whether a move leaves enough time to react to a parry window. */
namespace RPGBossParryFair
{
    constexpr double DefaultWindowSeconds=.25;
    constexpr double DefaultReactionSeconds=.2;

    inline bool ParryableOk(double TelegraphSeconds, double ActiveStartSeconds, double PlayRate,
        double WindowSeconds=DefaultWindowSeconds, double ReactionSeconds=DefaultReactionSeconds)
    {
        if (!FMath::IsFinite(TelegraphSeconds) || !FMath::IsFinite(ActiveStartSeconds) ||
            !FMath::IsFinite(PlayRate) || !FMath::IsFinite(WindowSeconds) || !FMath::IsFinite(ReactionSeconds) ||
            TelegraphSeconds < 0. || ActiveStartSeconds < TelegraphSeconds || PlayRate <= 0. ||
            WindowSeconds < 0. || ReactionSeconds < 0.)
        {
            return false;
        }
        const double ReactionGap=(ActiveStartSeconds-TelegraphSeconds)/PlayRate;
        return FMath::IsFinite(ReactionGap) && ReactionGap + 1.e-9 >= ReactionSeconds + .5 * WindowSeconds;   // 1e-9 s tolerance: (.425 - .1) is 0.32499999999999996 in doubles, exactly at the boundary
    }
}
