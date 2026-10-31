// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"
/**
 * BOSS-QA-001 (runtime overlay): the one text line the framework boss shows on screen (console variable rpg.BossOverlay 1) and logs once per second (2): active move card, move state, phase, range, cone,
 * hit window state, posture, health and the stagger / phase hold flags. Header only, no UObject: the boss and an automation test share the exact format.
 */
namespace RPGBossOverlay
{
    struct FInput
    {
        FString CardId, State, Phase;        // CardId empty = no card running
        double Range=0., Cone=0.;            // cm to the target (floor plane), the running card's front cone in degrees
        bool bWindowOpen=false;              // the move model is in its Active state (a hit window is open)
        double Posture=0., PostureMax=0., Health=0., MaxHealth=0.;
        bool bStaggered=false, bPhaseHold=false;
    };
    /** A finite number with the given digits, "n/a" otherwise (the overlay must never show NaN or inf as a value). */
    inline FString Num(double V,int32 Digits=0)
    {
        if (!FMath::IsFinite(V)) return TEXT("n/a");
        return Digits<=0 ? FString::Printf(TEXT("%.0f"),V) : Digits==1 ? FString::Printf(TEXT("%.1f"),V) : FString::Printf(TEXT("%.2f"),V);
    }
    inline FString Format(const FInput& I)
    {
        return FString::Printf(TEXT("Card=%s State=%s Phase=%s Range=%scm Cone=%sdeg Window=%s Posture=%s/%s Health=%s/%s Stagger=%d PhaseHold=%d"),
            I.CardId.IsEmpty()?TEXT("None"):*I.CardId,*I.State,*I.Phase,*Num(I.Range),*Num(I.Cone),I.bWindowOpen?TEXT("Open"):TEXT("Closed"),
            *Num(I.Posture),*Num(I.PostureMax),*Num(I.Health),*Num(I.MaxHealth),I.bStaggered?1:0,I.bPhaseHold?1:0);
    }
}
