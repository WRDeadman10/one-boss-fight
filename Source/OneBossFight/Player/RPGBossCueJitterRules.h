// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"

/** Deterministic per-cue timing jitter clamped to an authored safe interval. Unwired by design. */
namespace RPGBossCueJitter
{
    inline double Time(int32 Seed,int32 CueIndex,double BaseSeconds,double JitterSeconds,double SafeMin,double SafeMax)
    {
        if(CueIndex<0||!FMath::IsFinite(BaseSeconds)||!FMath::IsFinite(JitterSeconds)||!FMath::IsFinite(SafeMin)||!FMath::IsFinite(SafeMax)||
            JitterSeconds<0.||SafeMin<0.||SafeMax<SafeMin)return 0.;
        const int32 Mixed=int32(HashCombine(GetTypeHash(Seed),GetTypeHash(CueIndex)));
        FRandomStream Stream(Mixed);
        const double Offset=(2.*double(Stream.FRand())-1.)*JitterSeconds;
        return FMath::Clamp(BaseSeconds+Offset,SafeMin,SafeMax);
    }
}
