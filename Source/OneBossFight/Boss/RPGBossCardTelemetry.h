// Copyright One Boss Fight. All Rights Reserved.
#pragma once

namespace RPGBossCardTelemetry
{
	struct FDelta
	{
		int32 AcceptedHits = 0;
		double AppliedDamage = 0.;
	};

	/** A CARD_END snapshot is a per-card delta from executor lifetime totals. */
	inline FDelta Since(int32 TotalHits, int32 HitsAtStart, double TotalDamage, double DamageAtStart)
	{
		FDelta Result;
		Result.AcceptedHits = TotalHits >= HitsAtStart ? TotalHits - HitsAtStart : 0;
		Result.AppliedDamage = TotalDamage >= DamageAtStart ? TotalDamage - DamageAtStart : 0.;
		return Result;
	}
}
