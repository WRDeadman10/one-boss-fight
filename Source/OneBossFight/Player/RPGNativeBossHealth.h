// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "UObject/Interface.h"
#include "Player/RPGWeaponAttackTable.h"
#include "RPGNativeBossHealth.generated.h"

UINTERFACE(MinimalAPI)
class URPGNativeBossHealth : public UInterface
{
    GENERATED_BODY()
};
/**
 * A boss that owns its health natively (the framework Sevarog has no pack attribute component). Three consumers share these facts:
 * RPGPack::ReadAttribute (the boss-health readers: HUD, music, fog gate, bleed, posture, debug), the hit intake (a player hit on it)
 * and the damage resolver's life provider. Pack bosses do not implement it: every path stays as it was for them.
 */
class ONEBOSSFIGHT_API IRPGNativeBossHealth
{
    GENERATED_BODY()
public:
    /** Current or maximum health; false when this boss is not hittable (no authored health). */
    virtual bool ReadNativeHealth(bool bMax, double& Out) const = 0;
    /** One player hit: the boss turns its authored player-hit damage (design value) times the multiplier into a health loss. Returns the loss. */
    virtual double ApplyPlayerHit(double Multiplier) = 0;
    /** F10: the same hit with the weapon attack ROW that caused it (DA_WeaponAttacks: PostureDamage, BleedBuildup, HealthDamageMultiplier). Default: the row is ignored (profile constants). */
    virtual double ApplyPlayerAttackHit(const FRPGWeaponAttackRow& Row, double Multiplier) { return ApplyPlayerHit(Multiplier); }
};
