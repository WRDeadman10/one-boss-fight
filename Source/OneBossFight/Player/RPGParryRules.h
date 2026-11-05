// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"

/**
 * The player's parry (owner decision 2026-11-02: pressing the button at the right moment while the boss attacks parries the hit): pure rules, header only so an automation test can check them.
 * A press opens a short window (WindowSeconds, the "perfect timing"); a boss contact inside it is parried (no damage). A press during the cooldown (counted from the press) does nothing, so the button cannot be held down.
 * The pack's own parry ability is a stub (no montage, no ParryFramesNS use), so the window lives here; times are game seconds.
 */
namespace RPGParry
{
    constexpr double DefaultWindowSeconds=.25, DefaultCooldownSeconds=.7;   // design values, proposed
    struct FState { double OpenedAt=-1.e9, ReadyAt=-1.e9; };
    /** A press at Now: opens the window when the cooldown is over; the cooldown is never shorter than the window. Returns whether a window was opened. */
    inline bool Press(FState& State,double Now,double WindowSeconds,double CooldownSeconds)
    {
        if (!FMath::IsFinite(Now)||!FMath::IsFinite(WindowSeconds)||!FMath::IsFinite(CooldownSeconds)||WindowSeconds<=0.||Now<State.ReadyAt) return false;
        State.OpenedAt=Now; State.ReadyAt=Now+FMath::Max(WindowSeconds,CooldownSeconds);
        return true;
    }
    /** True while a contact at Now is inside the window that the last accepted press opened (the opening instant is in, the closing instant is out). */
    inline bool IsOpen(const FState& State,double Now,double WindowSeconds)
    {
        return FMath::IsFinite(Now)&&FMath::IsFinite(WindowSeconds)&&WindowSeconds>0.&&Now>=State.OpenedAt&&Now<State.OpenedAt+WindowSeconds;
    }
}
