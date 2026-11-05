// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"

/** Opt-in preferred range band with separate entry/exit thresholds to prevent band flapping. */
namespace RPGBossAggro
{
    enum class EBand : uint8 { Balanced, Close, Far };
    struct FConfig
    {
        double EnterCloseCm=250., ExitCloseCm=300., EnterFarCm=700., ExitFarCm=600.;
        double EnterDodgeRate=.6, ExitDodgeRate=.3, DodgeRateWindowSeconds=5.;
    };
    inline bool IsValid(const FConfig& C)
    {
        return FMath::IsFinite(C.EnterCloseCm)&&FMath::IsFinite(C.ExitCloseCm)&&FMath::IsFinite(C.EnterFarCm)&&FMath::IsFinite(C.ExitFarCm)&&
            FMath::IsFinite(C.EnterDodgeRate)&&FMath::IsFinite(C.ExitDodgeRate)&&FMath::IsFinite(C.DodgeRateWindowSeconds)&&
            C.EnterCloseCm>=0.&&C.ExitCloseCm>C.EnterCloseCm&&C.ExitFarCm>C.ExitCloseCm&&C.EnterFarCm>C.ExitFarCm&&
            C.ExitDodgeRate>=0.&&C.EnterDodgeRate>C.ExitDodgeRate&&C.DodgeRateWindowSeconds>0.;
    }
    inline EBand Step(EBand Current,double RangeCm,bool bPlayerHugging,bool bPlayerKiting,double DodgeRatePerSecond,const FConfig& C=FConfig())
    {
        if (!IsValid(C)||!FMath::IsFinite(RangeCm)||RangeCm<0.||!FMath::IsFinite(DodgeRatePerSecond)||DodgeRatePerSecond<0.|| (bPlayerHugging&&bPlayerKiting)) return Current;
        bPlayerKiting=bPlayerKiting||(Current==EBand::Far?DodgeRatePerSecond>C.ExitDodgeRate:DodgeRatePerSecond>=C.EnterDodgeRate);
        if (Current==EBand::Close && !bPlayerKiting && RangeCm<C.ExitCloseCm) return EBand::Close;
        if (Current==EBand::Far && !bPlayerHugging && RangeCm>C.ExitFarCm) return EBand::Far;
        if (bPlayerHugging||RangeCm<C.EnterCloseCm) return EBand::Close;
        if (bPlayerKiting||RangeCm>C.EnterFarCm) return EBand::Far;
        return EBand::Balanced;
    }
    inline EBand Step(EBand Current,double RangeCm,bool bPlayerHugging,bool bPlayerKiting,const FConfig& C=FConfig())
    {
        return Step(Current,RangeCm,bPlayerHugging,bPlayerKiting,0.,C);
    }
}
