// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"

/** Bounded posture/stagger resistance scale by phase. Unwired by design. */
namespace RPGBossStaggerResist
{
    inline double Scale(int32 Phase,double PhaseOneScale=1.,double PhaseTwoScale=1.25)
    {
        if(!FMath::IsFinite(PhaseOneScale)||!FMath::IsFinite(PhaseTwoScale)||PhaseOneScale<0.||PhaseOneScale>3.||PhaseTwoScale<0.||PhaseTwoScale>3.)return 1.;
        if(Phase==1)return PhaseOneScale;if(Phase==2)return PhaseTwoScale;return 1.;
    }
}
