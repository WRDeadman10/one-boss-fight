// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"

namespace RPGBossChannelDrain
{
    /** Counts inclusive card-local ticks robustly when float-authored endpoints have a tiny representation gap. */
    inline int32 TickCount(double StartSeconds,double EndSeconds,double IntervalSeconds)
    {
        if (!FMath::IsFinite(StartSeconds)||!FMath::IsFinite(EndSeconds)||!FMath::IsFinite(IntervalSeconds)||StartSeconds<0.||EndSeconds<=StartSeconds||IntervalSeconds<=0.) return 0;
        const double Ratio=(EndSeconds-StartSeconds+1.e-4)/IntervalSeconds;
        if (!FMath::IsFinite(Ratio)||Ratio>=65.) return 65;
        return FMath::Max(0,FMath::FloorToInt(Ratio));
    }
    /** Pure upper bound for healing: only accepted HP loss contributes and boss health cannot pass its maximum. */
    inline double CappedHeal(double AcceptedHPApplied,double HealFraction,double BossHealth,double BossMaxHealth)
    {
        if (!FMath::IsFinite(AcceptedHPApplied)||!FMath::IsFinite(HealFraction)||!FMath::IsFinite(BossHealth)||!FMath::IsFinite(BossMaxHealth)||
            AcceptedHPApplied<=0.||HealFraction<=0.||HealFraction>1.||BossHealth<0.||BossMaxHealth<=0.||BossHealth>=BossMaxHealth) return 0.;
        return FMath::Min(BossMaxHealth-BossHealth,AcceptedHPApplied*HealFraction);
    }
}
