// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"

/** One-shot player feedback gate for a resolved parry. NEXT_IDEAS #1; unwired. */
namespace RPGBossParryFeedback
{
    inline bool ShouldEmit(bool bOutcomeParried,bool bAlreadyEmitted)
    {
        return bOutcomeParried&&!bAlreadyEmitted;
    }
}
