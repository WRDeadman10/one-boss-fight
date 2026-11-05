// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"

/** Pure, deterministic rules for neutral circular strafe movement. */
namespace RPGBossStrafe
{
    /** Move along the circle centred on Target by arc length Speed * DeltaSeconds. Invalid input leaves Boss unchanged. */
    inline FVector2D NextPosition(FVector2D Boss, FVector2D Target, double SpeedCmPerSecond, double DeltaSeconds, int32 Dir)
    {
        if (!FMath::IsFinite(Boss.X) || !FMath::IsFinite(Boss.Y) ||
            !FMath::IsFinite(Target.X) || !FMath::IsFinite(Target.Y) ||
            !FMath::IsFinite(SpeedCmPerSecond) || !FMath::IsFinite(DeltaSeconds) ||
            SpeedCmPerSecond <= 0. || DeltaSeconds <= 0. || (Dir != 1 && Dir != -1))
            return Boss;

        const FVector2D Offset = Boss - Target;
        const double Radius = Offset.Size();
        if (!FMath::IsFinite(Radius) || Radius < 1.)
            return Boss;

        const double ArcLength = SpeedCmPerSecond * DeltaSeconds;
        if (!FMath::IsFinite(ArcLength))
            return Boss;
        const double Angle = double(Dir) * (ArcLength / Radius);
        if (!FMath::IsFinite(Angle))
            return Boss;

        const double CosAngle = FMath::Cos(Angle);
        const double SinAngle = FMath::Sin(Angle);
        return Target + FVector2D(Offset.X * CosAngle - Offset.Y * SinAngle,
                                  Offset.X * SinAngle + Offset.Y * CosAngle);
    }

    /** A repeatable hold in [MinSeconds, MaxSeconds]; a reversed range collapses to MinSeconds. */
    inline double HoldSeconds(int32 Seed, int32 Index, double MinSeconds, double MaxSeconds)
    {
        if (!FMath::IsFinite(MinSeconds) || !FMath::IsFinite(MaxSeconds))
            return FMath::IsFinite(MinSeconds) ? MinSeconds : 0.;
        if (MaxSeconds < MinSeconds)
            return MinSeconds;
        const double Range = MaxSeconds - MinSeconds;
        if (!FMath::IsFinite(Range))
            return MinSeconds;
        const int32 Hash = int32(HashCombine(GetTypeHash(Seed), GetTypeHash(Index)));
        FRandomStream Stream(Hash);
        Stream.FRand(); // decorrelate the first value from adjacent seed/index hashes
        const double Result = MinSeconds + Range * double(Stream.FRand());
        return FMath::IsFinite(Result) ? Result : MinSeconds;
    }

    /** Direction is stable for each seeded hold segment and flips exactly at each segment boundary. */
    inline int32 DirectionAt(int32 Seed, double ElapsedSeconds, double MinHold, double MaxHold)
    {
        if (!FMath::IsFinite(ElapsedSeconds) || ElapsedSeconds < 0. ||
            !FMath::IsFinite(MinHold) || !FMath::IsFinite(MaxHold) || MinHold <= 0. || MaxHold <= 0.)
            return 1;

        const int32 DirectionHash = int32(HashCombine(GetTypeHash(Seed), GetTypeHash(int32(0x5A17))));
        int32 Direction = (DirectionHash & 1) ? 1 : -1;
        double Remaining = ElapsedSeconds;
        for (int32 Index = 0; Index < MAX_int32; ++Index)
        {
            const double Hold = HoldSeconds(Seed, Index, MinHold, MaxHold);
            if (!FMath::IsFinite(Hold) || Hold <= 0.)
                return Direction;
            if (Remaining < Hold)
                return Direction;
            Remaining -= Hold;
            Direction = -Direction;
        }
        return Direction;
    }
}
