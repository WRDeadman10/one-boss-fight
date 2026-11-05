// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"

/** Back-off gate for a threatened boss in close range. Unwired by design. */
namespace RPGBossRetreat
{
    inline bool ShouldRetreat(double RangeCm,double CloseRangeCm,double Threat01,double ThreatThreshold=.5)
    {
        if(!FMath::IsFinite(RangeCm)||!FMath::IsFinite(CloseRangeCm)||!FMath::IsFinite(Threat01)||!FMath::IsFinite(ThreatThreshold)||
            RangeCm<0.||CloseRangeCm<0.||Threat01<0.||Threat01>1.||ThreatThreshold<0.||ThreatThreshold>1.)return false;
        return RangeCm<CloseRangeCm&&Threat01>=ThreatThreshold;
    }
}
