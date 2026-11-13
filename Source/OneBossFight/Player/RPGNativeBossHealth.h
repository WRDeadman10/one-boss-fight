// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"
#include "UObject/Interface.h"
#include "Player/RPGWeaponAttackTable.h"
#include "RPGNativeBossHealth.generated.h"

DECLARE_MULTICAST_DELEGATE_TwoParams(FRPGNativeBossTerminalDelegate, AActor*, uint64);

namespace RPGBossHealthPresentation
{
inline bool IsSnapshotValid(double Health, double MaxHealth)
{
    return FMath::IsFinite(Health) && FMath::IsFinite(MaxHealth) && MaxHealth > 0.0;
}

inline float Fraction(double Health, double MaxHealth)
{
    return IsSnapshotValid(Health, MaxHealth) ? FMath::Clamp(static_cast<float>(Health / MaxHealth), 0.f, 1.f) : 1.f;
}

inline bool IsVictory(bool bHaveHealth, double Health, bool bSeenAlive)
{
    return bHaveHealth && bSeenAlive && FMath::IsFinite(Health) && Health <= 0.0;
}
}

namespace RPGBossTerminalRules
{
inline bool ShouldAccept(uint64 CurrentGeneration, uint64 EventGeneration, uint64 CompletedGeneration, bool bHaveHealth, double Health)
{
    return CurrentGeneration > 0 && EventGeneration == CurrentGeneration && CompletedGeneration < CurrentGeneration
        && bHaveHealth && FMath::IsFinite(Health) && Health <= 0.0;
}
}

UINTERFACE(MinimalAPI)
class URPGNativeBossHealth : public UInterface
{
    GENERATED_BODY()
};
/**
 * A boss that owns its health natively (the framework Sevarog has no pack attribute component). Health consumers must query this interface explicitly;
 * RPGPack::ReadAttribute remains the path for pack actors. Native encounter presentation also reads its generation and active state here.
 */
class ONEBOSSFIGHT_API IRPGNativeBossHealth
{
    GENERATED_BODY()
public:
    /** Current or maximum health; false when this boss is not hittable (no authored health). */
    virtual bool ReadNativeHealth(bool bMax, double& Out) const = 0;
    /** Generation owned by the native encounter. HUD completion/retry latches are scoped to this value. */
    virtual uint64 NativeEncounterGeneration() const = 0;
    /** True once the native encounter has reached its active/fighting state. */
    virtual bool IsNativeEncounterActive() const = 0;
    /** True after the actor has crossed its authored phase-two transition. */
    virtual bool IsNativePhaseTwo() const = 0;
    /** Terminal notification is generation tagged; consumers must reject stale or duplicate generations. */
    virtual FRPGNativeBossTerminalDelegate& NativeTerminalDelegate() = 0;
    /** One player hit: the boss turns its authored player-hit damage (design value) times the multiplier into a health loss. Returns the loss. */
    virtual double ApplyPlayerHit(double Multiplier) = 0;
    /** F10: the same hit with the weapon attack ROW that caused it (DA_WeaponAttacks: PostureDamage, BleedBuildup, HealthDamageMultiplier). Default: the row is ignored (profile constants). */
    virtual double ApplyPlayerAttackHit(const FRPGWeaponAttackRow& Row, double Multiplier) { return ApplyPlayerHit(Multiplier); }
};
