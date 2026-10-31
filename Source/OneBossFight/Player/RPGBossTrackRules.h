// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"
/**
 * BOSS-ANM-004 (staged rotation cap): the boss turns toward its target at most TrackDegreesPerSecond of the move card, only until the heading is committed; after the commit the yaw is locked.
 * Header only, no UObject: the executor and an automation test share this one rule.
 */
namespace RPGBossTrack
{
    /** Yaw after one tick: the shortest way toward Target, at most DegPerSecond * Dt (wrap safe); unchanged when committed, when the rate is not positive or Dt is not positive. */
    inline float StepYaw(float Current,float Target,float DegPerSecond,float Dt,bool bCommitted)
    {
        if (bCommitted||!FMath::IsFinite(DegPerSecond)||!FMath::IsFinite(Dt)||!(DegPerSecond>0.f)||!(Dt>0.f)) return Current;
        return FMath::FixedTurn(Current,Target,DegPerSecond*Dt);
    }
}
