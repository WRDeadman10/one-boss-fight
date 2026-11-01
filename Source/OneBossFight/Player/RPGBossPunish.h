// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "Player/RPGBossPunishRules.h"

class UAnimMontage;

/** BOSS-PAC-003 / PAC-005: reads the player's punish speed from the pack's own assets. */
namespace RPGBossPunish
{
    /**
     * The startup of an attack montage in real seconds: the time of the first notify state that is the pack's attack trace (a notify state class whose name contains "CollisionTrace": the pack's ANS_CollisionTrace,
     * named AttackTraceNS on the montages), divided by the montage rate scale. Returns -1 when the montage is null or has no such notify state.
     */
    ONEBOSSFIGHT_API double MeasureStartupSeconds(const UAnimMontage* Montage);
}
