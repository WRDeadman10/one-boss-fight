// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"

/** One-shot death and phase-roar presentation gates. NEXT_IDEAS #8; unwired. */
namespace RPGBossPresentation
{
    inline bool ShouldPlayDeath(bool bDead,bool bDeathAlreadyPlayed)
    {
        return bDead&&!bDeathAlreadyPlayed;
    }
    inline bool ShouldPlayPhaseRoar(bool bDead,bool bPhaseChanged,bool bRoarAlreadyPlayed)
    {
        return !bDead&&bPhaseChanged&&!bRoarAlreadyPlayed;
    }
}
