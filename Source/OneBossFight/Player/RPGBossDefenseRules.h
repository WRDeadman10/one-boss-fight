// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "Player/RPGBossPunishRules.h"

/**
 * BOSS-DEF-005 (fair boss defense): pure rules, header only so an automation test can check them. A DEFENSIVE card (a backstep: no hit window, no damage, the boss moves AWAY from the target) is fair when
 * (1) the player can SEE it coming: the move starts at least MinTelegraphSeconds after the card starts (real seconds),
 * (2) it does not leave the player's reach for good: the backstep is at most MaxBackstepCm,
 * (3) it cannot be spammed: the card's cooldown is at least MinCooldownSeconds,
 * (4) the player can still PUNISH after it: the recovery that remains after the move ends is at least the player's attack startup plus the walk from (the card's max range + the backstep) into reach (the PAC-003/005 rule, margin 0).
 */
namespace RPGBossDefense
{
    constexpr double MinTelegraphSeconds=.25, MaxBackstepCm=250., MinCooldownSeconds=3.;
    inline bool TelegraphOk(double MoveStartCardSeconds,double PlayRate)
    {
        return FMath::IsFinite(MoveStartCardSeconds)&&FMath::IsFinite(PlayRate)&&PlayRate>0.&&MoveStartCardSeconds/PlayRate>=MinTelegraphSeconds;
    }
    inline bool BackstepDistanceOk(double BackstepCm){return FMath::IsFinite(BackstepCm)&&BackstepCm>0.&&BackstepCm<=MaxBackstepCm;}
    inline bool CooldownOk(double CooldownSeconds){return FMath::IsFinite(CooldownSeconds)&&CooldownSeconds>=MinCooldownSeconds;}
    /** Seconds the player has left over after it has walked to the boss and swung: positive = a real counterplay window. */
    inline double CounterplayMarginSeconds(double CardMaxRangeCm,double BackstepCm,double RecoveryAfterMoveSeconds,const RPGBossPunish::FPlayerMoves& Moves)
    {
        const double Travel=RPGBossPunish::TravelSeconds(CardMaxRangeCm+BackstepCm,Moves.ReachCm,Moves.RunSpeedCmPerSecond);
        return RPGBossPunish::MarginSeconds(RecoveryAfterMoveSeconds,Moves.LightStartupSeconds,Travel);
    }
}
