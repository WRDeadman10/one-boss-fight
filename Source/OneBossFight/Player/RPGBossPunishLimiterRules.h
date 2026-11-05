// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"

/** Small per-fight budget for punish-window uses. Unwired by design. */
namespace RPGBossPunishLimiter
{
    struct FState { int32 Uses=0; };
    inline bool CanUse(const FState& State,int32 MaxUses)
    {
        return MaxUses>0&&MaxUses<=100&&State.Uses>=0&&State.Uses<MaxUses;
    }
    inline bool RecordUse(FState& State,int32 MaxUses)
    {
        if(!CanUse(State,MaxUses))return false;
        ++State.Uses;return true;
    }
    inline void Reset(FState& State){State.Uses=0;}
}
