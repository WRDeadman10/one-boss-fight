// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"

/** Restart a neutral-strafe budget once after a qualifying interruption. NEXT_IDEAS #5; unwired. */
namespace RPGBossStrafeResume
{
    inline bool ShouldRestart(bool bWasInterrupted,bool bRestartAlreadyUsed,double RemainingBudgetSeconds)
    {
        return bWasInterrupted&&!bRestartAlreadyUsed&&FMath::IsFinite(RemainingBudgetSeconds)&&RemainingBudgetSeconds>0.;
    }
}
