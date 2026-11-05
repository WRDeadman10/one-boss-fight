// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"

/** Opt-in chance to evade a heavy attack based on recent player hits. Unwired by design. */
namespace RPGBossReactiveDodge
{
    struct FConfig { int32 HitsToStart=2; double BaseChance=.05; double ChancePerHit=.1; double MaxChance=.65; };
    inline bool IsValid(const FConfig& C)
    {
        return C.HitsToStart>=0&&C.HitsToStart<=100&&FMath::IsFinite(C.BaseChance)&&FMath::IsFinite(C.ChancePerHit)&&FMath::IsFinite(C.MaxChance)&&
            C.BaseChance>=0.&&C.ChancePerHit>=0.&&C.MaxChance>=0.&&C.MaxChance<=1.&&C.BaseChance<=C.MaxChance;
    }
    inline double Chance(bool bHeavyAttack,int32 RecentHits,const FConfig& C=FConfig())
    {
        if(!bHeavyAttack||RecentHits<C.HitsToStart||!IsValid(C))return 0.;
        const int64 HitsSinceThreshold=int64(RecentHits)-int64(C.HitsToStart)+1;
        return FMath::Clamp(C.BaseChance+double(HitsSinceThreshold)*C.ChancePerHit,0.,C.MaxChance);
    }
    inline bool ShouldDodge(bool bHeavyAttack,int32 RecentHits,double Roll,const FConfig& C=FConfig())
    {
        return FMath::IsFinite(Roll)&&Roll>=0.&&Roll<1.&&Roll<Chance(bHeavyAttack,RecentHits,C);
    }
}
