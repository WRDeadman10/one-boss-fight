// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"

/**
 * BOSS-PAC-003 / BOSS-PAC-005 (guaranteed openings, punish margin): pure rules, header only so an automation test can check them.
 * The boss's recovery (the time from the end of its active state to the end of the card, in real seconds) must exceed what the player needs to punish: the startup of the player's attack (the montage time of its
 * attack-trace window) plus the time to walk from the card's maximum range into the attack's reach, plus a margin (0.3 s for the light punish; 0 for the heavy punish of a heavy finisher).
 */
namespace RPGBossPunish
{
    /** What the boss data needs to know about the player's moves, measured from the pack's own assets (see RPGBossPunish.h). */
    struct FPlayerMoves
    {
        double LightStartupSeconds=0., HeavyStartupSeconds=0., RunSpeedCmPerSecond=0., ReachCm=0.;
        bool IsValid() const { return FMath::IsFinite(LightStartupSeconds)&&FMath::IsFinite(HeavyStartupSeconds)&&FMath::IsFinite(RunSpeedCmPerSecond)&&FMath::IsFinite(ReachCm)
            &&LightStartupSeconds>0.&&HeavyStartupSeconds>0.&&RunSpeedCmPerSecond>0.&&ReachCm>=0.; }
    };
    /** Seconds the player needs to walk from RangeCm to the reach of its attack (0 when already in reach). */
    inline double TravelSeconds(double RangeCm,double ReachCm,double RunSpeedCmPerSecond)
    {
        if (!FMath::IsFinite(RangeCm)||!FMath::IsFinite(ReachCm)||!FMath::IsFinite(RunSpeedCmPerSecond)||RunSpeedCmPerSecond<=0.) return TNumericLimits<double>::Max();
        return FMath::Max(0.,RangeCm-ReachCm)/RunSpeedCmPerSecond;
    }
    /** The recovery of a card in real seconds: card time runs at PlayRate. Non-finite or non-positive input gives -1 (never enough). */
    inline double RecoverySeconds(double ActiveEndSeconds,double RecoveryEndSeconds,double PlayRate)
    {
        if (!FMath::IsFinite(ActiveEndSeconds)||!FMath::IsFinite(RecoveryEndSeconds)||!FMath::IsFinite(PlayRate)||PlayRate<=0.||RecoveryEndSeconds<ActiveEndSeconds) return -1.;
        return (RecoveryEndSeconds-ActiveEndSeconds)/PlayRate;
    }
    /** Recovery minus what the punish needs: positive = the player has time left over. */
    inline double MarginSeconds(double RecoverySecondsReal,double StartupSeconds,double TravelSecondsReal)
    {
        if (!FMath::IsFinite(RecoverySecondsReal)||!FMath::IsFinite(StartupSeconds)||!FMath::IsFinite(TravelSecondsReal)) return -TNumericLimits<double>::Max();
        return RecoverySecondsReal-(StartupSeconds+TravelSecondsReal);
    }
    /** True when the margin is at least Required (and Required is a sane non-negative number). */
    inline bool PunishOk(double Margin,double RequiredSeconds)
    {
        return FMath::IsFinite(Margin)&&FMath::IsFinite(RequiredSeconds)&&RequiredSeconds>=0.&&Margin>=RequiredSeconds;
    }
}
