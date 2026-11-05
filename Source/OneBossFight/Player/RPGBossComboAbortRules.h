// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"

/** Decide whether a parry cancels the active combo. Only the first combo hit can abort it. */
namespace RPGBossComboAbort
{
    inline bool ShouldAbort(bool bComboActive,int32 AcceptedHits,bool bFirstHitParried)
    {
        return bComboActive&&AcceptedHits==0&&bFirstHitParried;
    }
}
