// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include <limits>

/**
 * BOSS-COM-004 / BOSS-HIT-008 (guard and parry telemetry): pure rules, header only so an automation test can check them.
 * The boss only OBSERVES the player's guard (read-only): at the moment a boss hit is accepted, the executor reads the player's guard tags and the result is one of None / Guarded / Parried.
 * It changes no damage; it only feeds the combo gate (guarded and parried edges) and the log. The tags are the pack's own: the player's guard ability holds Status.Blocking, the parry window Status.ParryActive.
 */
namespace RPGBossGuard
{
    enum class EGuardState : uint8 { None, Guarded, Parried };
    /** A parry beats a block when both are set (the pack's parry window sits inside the guard). */
    inline EGuardState Classify(bool bBlocking,bool bParrying)
    {
        return bParrying?EGuardState::Parried:(bBlocking?EGuardState::Guarded:EGuardState::None);
    }
    inline const TCHAR* Name(EGuardState State){return State==EGuardState::Parried?TEXT("Parried"):State==EGuardState::Guarded?TEXT("Guarded"):TEXT("None");}
    /** The hit outcome of one card for the combo gate: parried beats guarded beats hit beats whiff (the strongest thing the player did to the card). */
    enum class ECardOutcome : uint8 { Whiff, Hit, Guarded, Parried };
    inline ECardOutcome CardOutcome(int32 Accepted,int32 Guarded,int32 Parried)
    {
        return Parried>0?ECardOutcome::Parried:Guarded>0?ECardOutcome::Guarded:Accepted>0?ECardOutcome::Hit:ECardOutcome::Whiff;
    }
    /** The non-shipping proof hook's 100 ms parry-input pulse every 500 ms, shifted by PhaseSeconds. */
    inline bool IsProofParryPulse(double SinceFirstAttack,double PhaseSeconds)
    {
        if (!FMath::IsFinite(SinceFirstAttack)||SinceFirstAttack<0.||!FMath::IsFinite(PhaseSeconds)) return false;
        const double MaxPhase=double(std::numeric_limits<float>::max());
        const double Clock=SinceFirstAttack+FMath::Clamp(PhaseSeconds,-MaxPhase,MaxPhase);
        if (!FMath::IsFinite(Clock)||Clock<0.) return false;
        const double PulsePosition=FMath::Fmod(Clock,.5);
        return PulsePosition>=0.&&PulsePosition<.1;
    }
}
