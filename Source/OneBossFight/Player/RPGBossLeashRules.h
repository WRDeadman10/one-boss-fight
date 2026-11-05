// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"

/** Strict arena-radius boundary used by the framework boss target-fault gate. Equality is inside. */
namespace RPGBossLeashRules
{
	inline bool IsOutsideArena(const FVector& Position, const FVector& Center, double RadiusCm)
	{
		if (!FMath::IsFinite(Position.X) || !FMath::IsFinite(Position.Y) || !FMath::IsFinite(Position.Z)
			|| !FMath::IsFinite(Center.X) || !FMath::IsFinite(Center.Y) || !FMath::IsFinite(Center.Z)
			|| !FMath::IsFinite(RadiusCm))
		{
			return true;
		}
		return RadiusCm > 0. && FVector::Dist2D(Position, Center) > RadiusCm;
	}
}
