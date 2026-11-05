// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"

/** Permit one bounded direction-change recovery after blocked strafe movement. NEXT_IDEAS #9; unwired. */
namespace RPGBossStuckRecovery
{
    inline bool CanRecover(bool bBlocked,bool bRecoveryAlreadyUsed,int32 Attempts,int32 MaxAttempts)
    {
        return bBlocked&&!bRecoveryAlreadyUsed&&Attempts>=0&&MaxAttempts>0&&MaxAttempts<=8&&Attempts<MaxAttempts;
    }
}
