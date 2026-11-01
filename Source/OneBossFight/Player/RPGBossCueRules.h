// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "Player/RPGBossTrackRules.h"

/**
 * BOSS-ANM-003 (bounded holds), BOSS-PAC-004 (recovery cues), BOSS-QA-007 (accessible feedback): pure rules, header only so an automation test can check them.
 * A card may HOLD its windup (the montage stops at HoldAtSeconds for a seeded time inside [HoldMin, HoldMax]) and fires CUES (a visual and a sound) at card times, at the end of the hold, or at the start of the recovery.
 * Accessibility: every cue has BOTH channels and the channels are distinct per cue meaning, so the player can read the cue from the picture alone, from the sound alone, or with the effects scaled down.
 */
namespace RPGBossCue
{
    /** The setting rpg.CueMode: 0 both, 1 visual only, 2 audio only, 3 low effects (both channels, the visual at half size). Anything else is 0. */
    struct FChannels { bool bVisual=true, bAudio=true; float VisualScale=1.f; };
    inline FChannels ChannelsFor(int32 Mode)
    {
        FChannels C;
        if (Mode==1) C.bAudio=false;
        else if (Mode==2) C.bVisual=false;
        else if (Mode==3) C.VisualScale=.5f;
        return C;
    }
    /** How long the windup is held this time: uniform in [Min, Max] from the seeded stream (Seed + Index). Negative = invalid window (Min > 0, Max >= Min, Max <= 3, finite). */
    inline double HoldSeconds(float MinSeconds,float MaxSeconds,int32 Seed,int32 Index)
    {
        if (!FMath::IsFinite(MinSeconds)||!FMath::IsFinite(MaxSeconds)||!(MinSeconds>0.f)||MaxSeconds<MinSeconds||MaxSeconds>3.f) return -1.;
        // Seeded and repeatable, but not correlated between neighbouring attacks: the seed and the index are hashed together, the first draw is thrown away.
        FRandomStream Stream(int32(HashCombine(GetTypeHash(Seed),GetTypeHash(Index)))); Stream.FRand();
        return double(MinSeconds)+(double(MaxSeconds)-double(MinSeconds))*double(Stream.FRand());
    }
    /** What identifies a cue to the player: its visual kind and its sound. Two cues with different ids must differ in BOTH (so each channel alone tells them apart). */
    struct FCueKey { FName Id; int32 Visual=0; FString Sound; };
    inline bool DistinctChannels(const TArray<FCueKey>& Cues)
    {
        for (int32 I=0;I<Cues.Num();++I)
            for (int32 J=I+1;J<Cues.Num();++J)
            {
                if (Cues[I].Id==Cues[J].Id) return false;
                if (Cues[I].Visual==Cues[J].Visual||Cues[I].Sound==Cues[J].Sound) return false;
            }
        return true;
    }
}
