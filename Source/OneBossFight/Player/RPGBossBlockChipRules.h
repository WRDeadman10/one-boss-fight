// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"

/** Opt-in damage scale for a hit that is guarded. Invalid inputs fail closed to zero damage. */
namespace RPGBossBlockChip
{
    inline double GuardedDamage(double IncomingDamage,double ChipFraction)
    {
        if (!FMath::IsFinite(IncomingDamage)||!FMath::IsFinite(ChipFraction)||IncomingDamage<0.||ChipFraction<0.||ChipFraction>1.) return 0.;
        return IncomingDamage*ChipFraction;
    }
}
