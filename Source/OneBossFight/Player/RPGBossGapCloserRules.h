// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"

/** Hysteretic range gate for choosing a gap-closing action. Unwired by design. */
namespace RPGBossGapCloser
{
    inline bool ShouldClose(bool bAlreadyClosing,double RangeCm,double EnterRangeCm,double ExitRangeCm)
    {
        if(!FMath::IsFinite(RangeCm)||!FMath::IsFinite(EnterRangeCm)||!FMath::IsFinite(ExitRangeCm)||RangeCm<0.||EnterRangeCm<0.||ExitRangeCm<EnterRangeCm)return false;
        return bAlreadyClosing?RangeCm>EnterRangeCm:RangeCm>ExitRangeCm;
    }
}
