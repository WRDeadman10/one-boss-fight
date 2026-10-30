// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "Player/RPGBossMoveCard.h"

/** Base and tip of one blade segment in the space of the caller. */
struct FRPGSweepPose
{
    FVector A = FVector::ZeroVector, B = FVector::ZeroVector;
};
namespace RPGBossSweep
{
    /**
     * Pure: the key poses of one hit window for the part of a tick it was open, in time order (at least two when the window overlaps the tick).
     * With baked samples (opt-in per window) the poses come from the baked blade path in COMPONENT space (bBaked=true): the interpolated pose at the
     * start of the overlap, every sample strictly inside it, the interpolated pose at its end, so a long frame cannot skip the apex of a thrust.
     * Without baked samples the two poses are the linear interpolation of the two tick poses (WORLD space, bBaked=false), as before.
     * Returns false when the window and the tick do not overlap.
     */
    ONEBOSSFIGHT_API bool BuildKeyPoses(const FRPGBossMoveWindow& Window, double PrevPosition, double Position,
        const FRPGSweepPose& PrevTickPose, const FRPGSweepPose& CurrentTickPose, TArray<FRPGSweepPose>& OutKeys, bool& bBaked, double& OutLo, double& OutHi);
}
