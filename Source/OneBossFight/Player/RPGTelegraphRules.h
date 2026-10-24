// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"

namespace RPGTelegraphRules
{
/** The play rate that makes the montage reach ActiveStart (montage seconds) Target real seconds after it began. Position is where the montage is when the rate is applied (the tracker sees a stage a frame or two after it began, at rate 1): the rest of the way, ActiveStart - Position, must take Target - Position real seconds. Position 0 gives ActiveStart / Target. */
inline float RateFor(float ActiveStart, float Target, float Position = 0.f)
{
	if (Target <= 0.f || Target <= ActiveStart || ActiveStart <= 0.f || Position < 0.f || Position >= ActiveStart || Position >= Target)
	{
		return 1.f;
	}
	return FMath::Clamp((ActiveStart - Position) / (Target - Position), 0.1f, 1.f); // 0.1: a stage seen late (a hitch) still gets most of its tell; 0.25 cut the tell of A1 short already at a normal frame lag
}

inline float TargetFor(FName MoveId, float CvarValue)
{
	if (CvarValue <= 0.f)
	{
		return 0.f;
	}
	if (MoveId == TEXT("A1") || MoveId == TEXT("A1b"))
	{
		return FMath::Min(CvarValue, 0.35f);
	}
	return (MoveId == TEXT("A3a") || MoveId == TEXT("A3b")) ? CvarValue : 0.f;
}
}
