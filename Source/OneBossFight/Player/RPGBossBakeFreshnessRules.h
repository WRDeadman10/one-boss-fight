// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"

/** Pure identity check for whether baked hit samples match their animation source fingerprint. NEXT_IDEAS #7; unwired. */
namespace RPGBossBakeFreshness
{
    inline bool IsFresh(uint64 CurrentSourceFingerprint,uint64 BakedSourceFingerprint)
    {
        return CurrentSourceFingerprint!=0&&BakedSourceFingerprint!=0&&CurrentSourceFingerprint==BakedSourceFingerprint;
    }
}
