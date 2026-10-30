// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossSweepSampling.h"

namespace
{
    FRPGSweepPose Lerp(const FRPGSweepPose& P, const FRPGSweepPose& Q, double T)
    {
        FRPGSweepPose R; R.A = FMath::Lerp(P.A, Q.A, T); R.B = FMath::Lerp(P.B, Q.B, T); return R;
    }
    FRPGSweepPose PoseAt(const TArray<FRPGBakedBladeSample>& S, double Time)
    {
        FRPGSweepPose R;
        if (Time <= S[0].TimeSeconds) { R.A = S[0].BaseCS; R.B = S[0].TipCS; return R; }
        for (int32 I = 1; I < S.Num(); ++I)
        {
            if (Time <= S[I].TimeSeconds)
            {
                const double Span = S[I].TimeSeconds - S[I - 1].TimeSeconds, T = Span > 0.0 ? (Time - S[I - 1].TimeSeconds) / Span : 1.0;
                R.A = FMath::Lerp(S[I - 1].BaseCS, S[I].BaseCS, T); R.B = FMath::Lerp(S[I - 1].TipCS, S[I].TipCS, T); return R;
            }
        }
        R.A = S.Last().BaseCS; R.B = S.Last().TipCS; return R;
    }
}
bool RPGBossSweep::BuildKeyPoses(const FRPGBossMoveWindow& W, double PrevPosition, double Position,
    const FRPGSweepPose& PrevTickPose, const FRPGSweepPose& CurrentTickPose, TArray<FRPGSweepPose>& OutKeys, bool& bBaked, double& OutLo, double& OutHi)
{
    OutKeys.Reset(); bBaked = false;
    const double Lo = FMath::Max(PrevPosition, double(W.StartSeconds)), Hi = FMath::Min(Position, double(W.EndSeconds));
    OutLo = Lo; OutHi = Hi;
    if (Position <= PrevPosition || Hi <= Lo) return false;
    if (W.BakedSamples.Num() >= 2)
    {
        bBaked = true;
        OutKeys.Add(PoseAt(W.BakedSamples, Lo));
        for (const FRPGBakedBladeSample& S : W.BakedSamples)
            if (S.TimeSeconds > Lo && S.TimeSeconds < Hi) { FRPGSweepPose P; P.A = S.BaseCS; P.B = S.TipCS; OutKeys.Add(P); }
        OutKeys.Add(PoseAt(W.BakedSamples, Hi));
        return true;
    }
    const double Span = Position - PrevPosition;
    OutKeys.Add(Lerp(PrevTickPose, CurrentTickPose, (Lo - PrevPosition) / Span));
    OutKeys.Add(Lerp(PrevTickPose, CurrentTickPose, (Hi - PrevPosition) / Span));
    return true;
}
