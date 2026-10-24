// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"

namespace RPGBossDormantWakeRules
{
	/** A missing/stopped wake montage resumes only after it has had a small start grace period; a healthy running montage owns the gate. */
	inline bool ShouldFinishWake(bool bMontagePlaying, float Elapsed, float ExpectedSeconds)
	{
		return !bMontagePlaying && Elapsed >= FMath::Min(0.15f, ExpectedSeconds);
	}
}
