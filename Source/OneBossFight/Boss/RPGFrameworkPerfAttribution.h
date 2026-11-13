// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"

/** Pure bounded accumulator for explicitly scoped framework CPU samples. GPU frame data is not component-attributable. */
namespace RPGFrameworkPerfAttribution
{
	struct FWindow
	{
		uint64 Samples = 0;
		uint64 TotalMicroseconds = 0;
		uint64 MaxMicroseconds = 0;

		void Reset() { Samples = TotalMicroseconds = MaxMicroseconds = 0; }

		void RecordMilliseconds(double Milliseconds)
		{
			if (!FMath::IsFinite(Milliseconds) || Milliseconds < 0.0) return;
			const double Bounded = Milliseconds * 1000.0;
			const uint64 Microseconds = Bounded >= double(MAX_uint64) - 4096.0
				? MAX_uint64 : static_cast<uint64>(Bounded + 0.5);
			if (Samples < MAX_uint64) ++Samples;
			TotalMicroseconds = Microseconds > MAX_uint64 - TotalMicroseconds ? MAX_uint64 : TotalMicroseconds + Microseconds;
			MaxMicroseconds = FMath::Max(MaxMicroseconds, Microseconds);
		}
	};
}
