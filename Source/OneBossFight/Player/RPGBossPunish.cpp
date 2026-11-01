// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossPunish.h"
#include "Animation/AnimMontage.h"
#include "Animation/AnimNotifies/AnimNotifyState.h"

double RPGBossPunish::MeasureStartupSeconds(const UAnimMontage* Montage)
{
    if (!Montage) return -1.;
    double First=-1.;
    for (const FAnimNotifyEvent& Event:Montage->Notifies)
    {
        if (!Event.NotifyStateClass||!Event.NotifyStateClass->GetClass()->GetName().Contains(TEXT("CollisionTrace"))) continue;
        const double Time=double(Event.GetTriggerTime());
        if (First<0.||Time<First) First=Time;
    }
    if (First<0.) return -1.;
    const double Rate=Montage->RateScale>0.f?double(Montage->RateScale):1.;
    return First/Rate;
}
