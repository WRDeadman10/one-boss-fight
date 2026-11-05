// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"

/** Opt-in consecutive repeated-pattern detector. Unwired by design. */
namespace RPGBossPatternDetect
{
    struct FState { FName LastPattern=NAME_None; int32 Consecutive=0; };
    inline bool Observe(FState& State,FName Pattern,int32 RequiredRepeats)
    {
        if(Pattern.IsNone()||RequiredRepeats<2||RequiredRepeats>100){State=FState();return false;}
        State.Consecutive=FMath::Clamp(State.Consecutive,0,100);
        if(State.LastPattern==Pattern)State.Consecutive=FMath::Min(State.Consecutive+1,100);
        else{State.LastPattern=Pattern;State.Consecutive=1;}
        return State.Consecutive>=RequiredRepeats;
    }
}
