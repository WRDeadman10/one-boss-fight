// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"
/**
 * BOSS-ANM-004 (staged rotation cap): the boss turns toward its target at most TrackDegreesPerSecond of the move card, only until the heading is committed; after the commit the yaw is locked.
 * Header only, no UObject: the executor and an automation test share this one rule.
 */
namespace RPGBossTrack
{
    /** BOSS-MOV-003 (commitment hysteresis): the way the boss is turning (+1 / -1 / 0), and how often it changed its mind. */
    struct FTurnLatch { int32 Dir=0; int32 LastDir=0; int32 Flips=0; };
    /**
     * Like StepYaw, but a turn that has started keeps its direction while the target is within HysteresisDeg of the boss's back axis: a target flickering across the 180 degree line
     * (one tick +170, the next -170) does not make the boss reverse every frame. A target that really crosses to the other side (more than HysteresisDeg away from the back axis)
     * releases the latch. bUseLatch=false turns with the plain shortest way but still counts the direction changes (test hook control). Unchanged when committed / bad input.
     */
    inline float StepYawLatched(float Current,float Target,float DegPerSecond,float Dt,bool bCommitted,FTurnLatch& L,bool bUseLatch=true,float HysteresisDeg=30.f)
    {
        if (bCommitted||!FMath::IsFinite(DegPerSecond)||!FMath::IsFinite(Dt)||!(DegPerSecond>0.f)||!(Dt>0.f)) return Current;
        const float Delta=FMath::FindDeltaAngleDegrees(Current,Target), Step=DegPerSecond*Dt;
        if (FMath::Abs(Delta)<=Step) { L.Dir=0; return FRotator::NormalizeAxis(Current+Delta); }
        int32 Dir=Delta>0.f?1:-1;
        if (bUseLatch&&L.Dir!=0&&Dir!=L.Dir&&FMath::Abs(Delta)>=180.f-HysteresisDeg) Dir=L.Dir;   // near the back axis: keep the way we were turning
        L.Dir=Dir;
        if (L.LastDir!=0&&Dir!=L.LastDir) ++L.Flips;
        L.LastDir=Dir;
        return FRotator::NormalizeAxis(Current+float(Dir)*Step);
    }
    /**
     * BOSS-MOV-002 (centre bias): the direction, seen from the target, in which the boss takes its place in the band. Away is where the boss stands now (the unbiased way),
     * ToCenter points from the target to the arena centre. Bias 0 = Away, 1 = ToCenter (the boss ends between the target and the middle, not between the target and the wall),
     * in between = the normalised blend. Degenerate input (no centre direction, opposite vectors that cancel, bad bias) falls back to Away. Flat (Z = 0).
     */
    inline FVector CenterBiasedAway(const FVector& Away,const FVector& ToCenter,float Bias)
    {
        if (!FMath::IsFinite(Bias)||!(Bias>0.f)) return Away;
        FVector C(ToCenter.X,ToCenter.Y,0.); if (!C.Normalize()) return Away;
        const double B=FMath::Min(Bias,1.f); FVector R=FVector(Away.X,Away.Y,0.)*(1.-B)+C*B;
        return R.Normalize() ? R : Away;
    }
    /**
     * BOSS-SEL-009 (reaction latency): the delay between the boss PERCEIVING a player action (a flask drink) and the boss being able to REACT to it, drawn once per perceived action
     * from a seeded stream (Seed + Count), uniformly inside the authored window [Min, Max] seconds. Negative = invalid window (the profile is refused): Min > 0, Max >= Min, Max <= 5, all finite.
     */
    inline double ReactionDelaySeconds(float MinSeconds,float MaxSeconds,int32 Seed,int32 Count)
    {
        if (!FMath::IsFinite(MinSeconds)||!FMath::IsFinite(MaxSeconds)||!(MinSeconds>0.f)||MaxSeconds<MinSeconds||MaxSeconds>5.f) return -1.;
        FRandomStream Stream(Seed+Count*7919);
        return double(MinSeconds)+(double(MaxSeconds)-double(MinSeconds))*double(Stream.FRand());
    }
    /**
     * BOSS-AWR-007 (line of sight and memory): what the boss remembers about a target it can no longer see. LastKnown is the target's position at the last tick it was visible.
     * LosStep is called once per tick with the result of the visibility trace: it reports the moment the sight is Lost, Regained, or the search has run SearchSeconds without sight (TimedOut, reported once).
     */
    struct FLosMemory { bool bLost=false, bTimedOut=false; double LostAt=0.; FVector LastKnown=FVector::ZeroVector; };
    enum class ELosEvent : uint8 { None, Lost, Regained, TimedOut };
    inline ELosEvent LosStep(FLosMemory& M,bool bVisible,double Now,double SearchSeconds,const FVector& TargetNow)
    {
        if (bVisible) { M.LastKnown=TargetNow; if (M.bLost) { M.bLost=false; M.bTimedOut=false; return ELosEvent::Regained; } return ELosEvent::None; }
        if (!M.bLost) { M.bLost=true; M.bTimedOut=false; M.LostAt=Now; return ELosEvent::Lost; }
        if (!M.bTimedOut && Now-M.LostAt>=SearchSeconds) { M.bTimedOut=true; return ELosEvent::TimedOut; }
        return ELosEvent::None;
    }
    /** BOSS-EXE-007 (executor watchdog): a card that is still running this many WORLD seconds after its start is aborted: RecoveryEndSeconds / PlayRate + 0.5 s. Negative = invalid input (the card is refused at start). */
    inline double WatchdogTimeoutSeconds(float RecoveryEndSeconds,float PlayRate)
    {
        if (!FMath::IsFinite(RecoveryEndSeconds)||!FMath::IsFinite(PlayRate)||!(RecoveryEndSeconds>0.f)||!(PlayRate>0.f)) return -1.;
        return double(RecoveryEndSeconds)/double(PlayRate)+0.5;
    }
    /** Yaw after one tick: the shortest way toward Target, at most DegPerSecond * Dt (wrap safe); unchanged when committed, when the rate is not positive or Dt is not positive. */
    inline float StepYaw(float Current,float Target,float DegPerSecond,float Dt,bool bCommitted)
    {
        if (bCommitted||!FMath::IsFinite(DegPerSecond)||!FMath::IsFinite(Dt)||!(DegPerSecond>0.f)||!(Dt>0.f)) return Current;
        return FMath::FixedTurn(Current,Target,DegPerSecond*Dt);
    }
}
