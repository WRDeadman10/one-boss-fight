// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"

/** Deterministic yaw signal for exercising facing-cone boundary behavior. */
namespace RPGBossYawProbe
{
    inline double YawAt(int32 SampleIndex, double CenterDeg, double AmplitudeDeg, int32 Period)
    {
        if (!FMath::IsFinite(CenterDeg) || !FMath::IsFinite(AmplitudeDeg) || Period <= 0) return 0.;
        constexpr double Pi=3.14159265358979323846;
        const double Phase=2. * Pi * double(SampleIndex) / double(Period);
        const double Result=CenterDeg + AmplitudeDeg * FMath::Sin(Phase);
        return FMath::IsFinite(Result) ? Result : 0.;
    }
}
