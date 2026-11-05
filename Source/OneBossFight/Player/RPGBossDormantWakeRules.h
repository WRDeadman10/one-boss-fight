// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"

namespace RPGBossDormantWakeRules
{
	/** A missing/stopped wake montage resumes only after it has had a small start grace period; a healthy running montage owns the gate. */
	inline bool ShouldFinishWake(bool bMontagePlaying, float Elapsed, float ExpectedSeconds)
	{
		if (bMontagePlaying || !FMath::IsFinite(Elapsed)) return false;
		const float Grace = FMath::IsFinite(ExpectedSeconds) ? FMath::Min(0.15f, FMath::Max(0.f, ExpectedSeconds)) : 0.15f;
		return Elapsed >= Grace;
	}
}
