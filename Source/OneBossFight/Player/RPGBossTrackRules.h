// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"
#include "Player/RPGAttackKind.h"
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
    /**
     * BOSS-AWR-008 (soft adaptation memory): the direction of the target's dodges seen from the boss. Classify takes the target's velocity and the direction from the boss to the target (flat):
     * Back = moving away (dot >= 0.5), Forward = toward the boss (dot <= -0.5), Side otherwise; None when the velocity is not finite or not above SpeedCm. FDodgeHistory keeps the last Depth directions
     * (a ring) and BackCount() says how many of them were Back.
     */
    enum class EDodgeDir : uint8 { None, Back, Forward, Side };
    inline EDodgeDir ClassifyDodge(const FVector& Velocity,const FVector& BossToTarget,float SpeedCm)
    {
        FVector V(Velocity.X,Velocity.Y,0.), A(BossToTarget.X,BossToTarget.Y,0.);
        if (!FMath::IsFinite(SpeedCm)||!(SpeedCm>0.f)||V.ContainsNaN()||A.ContainsNaN()||!(V.Size()>=double(SpeedCm))||!A.Normalize()) return EDodgeDir::None;
        V.Normalize(); const double Dot=FVector::DotProduct(V,A);
        return Dot>=.5 ? EDodgeDir::Back : Dot<=-.5 ? EDodgeDir::Forward : EDodgeDir::Side;
    }
    struct FDodgeHistory
    {
        TArray<EDodgeDir> Dirs;
        void Push(EDodgeDir D,int32 Depth) { if (D==EDodgeDir::None||Depth<1) return; Dirs.Add(D); while (Dirs.Num()>Depth) Dirs.RemoveAt(0); }
        int32 BackCount() const { int32 N=0; for (EDodgeDir D:Dirs) if (D==EDodgeDir::Back) ++N; return N; }
    };
    /**
     * BOSS-HIT-011 (swept annulus): a ground shockwave around the boss. At time t after the window opens its front is at Start+Speed*t and the band is [front-Thickness, front].
     * RingTouches takes the front radius at both ends of ONE tick: the band covered during the tick is [FrontLo-Thickness, FrontHi], a continuous span, so consecutive ticks leave no gap (FrontHi of one tick is FrontLo of the next).
     * Dist = horizontal distance boss to target, TargetRadius = the target capsule radius, DzAbs = vertical feet-to-feet distance, Height = how high the wave reaches (a target that jumped above it is missed).
     */
    inline double RingFront(double StartCm,double SpeedCmPerSecond,double SecondsIntoWindow)
    {
        if (!FMath::IsFinite(StartCm)||!FMath::IsFinite(SpeedCmPerSecond)||!FMath::IsFinite(SecondsIntoWindow)) return -1.;
        const double Front=StartCm+SpeedCmPerSecond*SecondsIntoWindow;
        return FMath::IsFinite(Front) && Front>=0. ? Front : -1.;
    }
    inline bool RingTouches(double FrontLo,double FrontHi,double Thickness,double Dist,double TargetRadius,double DzAbs,double Height)
    {
        if (!FMath::IsFinite(FrontLo)||!FMath::IsFinite(FrontHi)||!FMath::IsFinite(Thickness)||!FMath::IsFinite(Dist)||!FMath::IsFinite(TargetRadius)||!FMath::IsFinite(DzAbs)||!FMath::IsFinite(Height)) return false;
        if (FrontLo<0.||FrontHi<0.||FrontHi<FrontLo||DzAbs>Height) return false;
        return Dist+TargetRadius>=FrontLo-Thickness && Dist-TargetRadius<=FrontHi;
    }
    /**
     * BOSS-HIT-012 (grab fail-safe): the hold of a grabbed victim. A contact of the grab window catches (once per card); the hold ends at ReleaseAtSeconds (card time) with Released, or AT ONCE with Interrupted when anything
     * aborts the attack (stagger, death, leash, watchdog, the card ending early, a lost victim). GroundedZ is where the victim's capsule centre goes on release: on the floor, never below it.
     */
    enum class EGrabEvent : uint8 { None, Caught, Released, Interrupted };
    struct FGrabState { bool bHeld=false; double ReleaseAt=0.; };
    inline EGrabEvent GrabStep(FGrabState& S,bool bContact,double Position,double ReleaseAtSeconds,bool bInterrupt)
    {
        if (S.bHeld)
        {
            if (bInterrupt) { S=FGrabState(); return EGrabEvent::Interrupted; }
            if (Position>=S.ReleaseAt) { S=FGrabState(); return EGrabEvent::Released; }
            return EGrabEvent::None;
        }
        if (bContact&&!bInterrupt&&FMath::IsFinite(ReleaseAtSeconds)) { S.bHeld=true; S.ReleaseAt=ReleaseAtSeconds; return EGrabEvent::Caught; }
        return EGrabEvent::None;
    }
    inline double GroundedZ(double FloorZ,double CapsuleHalfHeight,double SkinCm)
    {
        if (!FMath::IsFinite(FloorZ)||!FMath::IsFinite(CapsuleHalfHeight)||!FMath::IsFinite(SkinCm)) return FMath::IsFinite(FloorZ) ? FloorZ : 0.;
        const double Result=FloorZ+CapsuleHalfHeight+SkinCm;
        return FMath::IsFinite(Result) ? Result : FloorZ;
    }
    /**
     * BOSS-ANM-006 (bounded warp): the boss closes on the target during a warp window of the card, but never by more than WarpMaxDistanceCm / WarpMaxAngleDegrees IN TOTAL. Each tick covers the share of what is still needed
     * that this tick is of the time left in the window (so the warp ends exactly at the standoff when the budget allows), and never more than the budget still unspent: the sum of the steps cannot exceed the budget.
     */
    inline double WarpStepCm(double NeededCm,double RemainingBudgetCm,double DeltaSeconds,double SecondsLeft)
    {
        if (!FMath::IsFinite(NeededCm)||!FMath::IsFinite(RemainingBudgetCm)||!FMath::IsFinite(DeltaSeconds)||!FMath::IsFinite(SecondsLeft)) return 0.;
        if (NeededCm<=0.||RemainingBudgetCm<=0.||DeltaSeconds<=0.||SecondsLeft<=0.) return 0.;
        return FMath::Min(NeededCm*FMath::Min(1.,DeltaSeconds/SecondsLeft),RemainingBudgetCm);
    }
    inline double WarpStepDegrees(double NeededSignedDegrees,double RemainingBudgetDegrees,double DeltaSeconds,double SecondsLeft)
    {
        if (!FMath::IsFinite(NeededSignedDegrees)) return 0.;
        return (NeededSignedDegrees<0.?-1.:1.)*WarpStepCm(FMath::Abs(NeededSignedDegrees),RemainingBudgetDegrees,DeltaSeconds,SecondsLeft);
    }
    /**
     * BOSS-AWR-006 (observable player activity): what the boss reads from the player at a decision. A flask drink (already past the boss's reaction delay) or a HEAVY attack in progress (Strong, Charged or the
     * jumping heavy: the player is committed to a long swing) makes the target greedy; the flask wins when both are true. Light attacks are not a commitment.
     */
    enum class EPlayerActivity : uint8 { None, Flask, HeavyCommit };
    inline bool IsHeavyAttackKind(ERPGAttackKind Kind){return Kind==ERPGAttackKind::Strong||Kind==ERPGAttackKind::Charged||Kind==ERPGAttackKind::JumpHeavy;}
    inline EPlayerActivity ClassifyPlayerActivity(bool bFlaskKnown,bool bHeavyInProgress){return bFlaskKnown?EPlayerActivity::Flask:(bHeavyInProgress?EPlayerActivity::HeavyCommit:EPlayerActivity::None);}
    inline const TCHAR* PlayerActivityName(EPlayerActivity A){return A==EPlayerActivity::Flask?TEXT("Flask"):(A==EPlayerActivity::HeavyCommit?TEXT("HeavyCommit"):TEXT("None"));}
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
