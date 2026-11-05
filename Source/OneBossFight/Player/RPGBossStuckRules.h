// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"

/** Pure one-shot stuck detector for an opt-in neutral strafe. */
namespace RPGBossStuck
{
    struct FStuck
    {
        double AccumExpected=0.;
        double AccumMoved=0.;
        double Window=0.;
        bool bDirectionFlipped=false;
    };

    /** Accumulate expected arc, actual movement, and elapsed observation time. Invalid input resets safely. */
    inline void Update(FStuck& State, double ExpectedCm, double MovedCm, double Dt)
    {
        if (!FMath::IsFinite(ExpectedCm) || !FMath::IsFinite(MovedCm) || !FMath::IsFinite(Dt) ||
            ExpectedCm < 0. || MovedCm < 0. || Dt < 0.)
        {
            State.AccumExpected=0.;
            State.AccumMoved=0.;
            State.Window=0.;
            return;
        }
        State.AccumExpected+=ExpectedCm;
        State.AccumMoved+=MovedCm;
        State.Window+=Dt;
        if (!FMath::IsFinite(State.AccumExpected) || !FMath::IsFinite(State.AccumMoved) || !FMath::IsFinite(State.Window))
        {
            State.AccumExpected=0.;
            State.AccumMoved=0.;
            State.Window=0.;
        }
    }

    /** True once when the observation window is complete and movement fell below the expected-arc ratio. */
    inline bool IsStuck(FStuck& State, double MinRatio=.5, double WindowSeconds=.3)
    {
        if (!FMath::IsFinite(MinRatio) || !FMath::IsFinite(WindowSeconds) || MinRatio < 0. || WindowSeconds <= 0. ||
            State.bDirectionFlipped || State.Window < WindowSeconds || State.AccumExpected <= 0.)
        {
            return false;
        }
        const double Ratio=State.AccumMoved/State.AccumExpected;
        if (!FMath::IsFinite(Ratio) || Ratio >= MinRatio) return false;
        State.bDirectionFlipped=true;
        return true;
    }
}
