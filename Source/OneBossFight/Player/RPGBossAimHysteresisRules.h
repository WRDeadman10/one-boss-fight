// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"

/** Opt-in facing-cone state rule. Callers own bWasInside; this helper stores no selector or encounter state. */
namespace RPGBossAimHysteresis
{
    /** Enter at |SignedYawDegrees| <= EnterDeg; leave an existing cone only above ExitDeg. X < E collapses the band to E. Invalid numbers fail closed. */
    inline bool Step(bool bWasInside,double SignedYawDegrees,double EnterDeg,double ExitDeg)
    {
        if (!FMath::IsFinite(SignedYawDegrees)||!FMath::IsFinite(EnterDeg)||!FMath::IsFinite(ExitDeg)) return false;
        const double EffectiveExit=FMath::Max(EnterDeg,ExitDeg);
        const double AbsYaw=FMath::Abs(SignedYawDegrees);
        return bWasInside ? AbsYaw<=EffectiveExit : AbsYaw<=EnterDeg;
    }
}
