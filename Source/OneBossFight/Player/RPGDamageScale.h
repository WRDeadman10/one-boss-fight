// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"

/**
 * Per-weapon health damage multiplier (KI-097): the pack deals the health damage of a hit from its own attack data and weapon (the starter sword 41 per light hit, the builds 16), the project's weapon table only
 * decides posture, stamina, bleed and hyperarmor. The multiplier of a table row scales the health a hit took: the pack's loss is matched with the hit record (in either order, within Window seconds) and the difference
 * is given back (multiplier < 1) or taken away (multiplier > 1). Pure logic with no Unreal object so an automation test can check it; the hit intake owns one instance per boss.
 */
struct FRPGDamageScaler
{
	/** A loss and a record that belong together arrive in the same frame or one frame apart (the intake finalizes a hit one frame after the pack's event). */
	static constexpr double Window = 0.35;

	struct FLoss
	{
		double Time = 0.0;
		double Amount = 0.0;
	};

	struct FHit
	{
		double Time = 0.0;
		float Multiplier = 1.f;
	};

	TArray<FLoss> Losses;
	TArray<FHit> Hits;

	void Reset()
	{
		Losses.Reset();
		Hits.Reset();
	}

	/** The boss lost health that nobody has claimed. Returns the health to give back now (positive) or take away (negative), 0 when no scaled hit is waiting for it. */
	double OnLoss(double Time, double Amount)
	{
		Prune(Time);
		if (Amount <= 0.0)
		{
			return 0.0;
		}
		for (int32 Index = 0; Index < Hits.Num(); ++Index)
		{
			if (FMath::Abs(Time - Hits[Index].Time) <= Window)
			{
				const double Adjust = Amount * (1.0 - Hits[Index].Multiplier);
				Hits.RemoveAt(Index);
				return Adjust;
			}
		}
		FLoss Loss;
		Loss.Time = Time;
		Loss.Amount = Amount;
		Losses.Add(Loss);
		return 0.0;
	}

	/** A weapon hit record was finalized with this multiplier. A hit with multiplier 1 still claims the loss it caused (so no later scaled hit takes it). Returns the adjustment as OnLoss does. */
	double OnHit(double Time, float Multiplier)
	{
		Prune(Time);
		for (int32 Index = 0; Index < Losses.Num(); ++Index)
		{
			if (FMath::Abs(Time - Losses[Index].Time) <= Window)
			{
				const double Adjust = Losses[Index].Amount * (1.0 - Multiplier);
				Losses.RemoveAt(Index);
				return Adjust;
			}
		}
		if (!FMath::IsNearlyEqual(Multiplier, 1.f))
		{
			FHit Hit;
			Hit.Time = Time;
			Hit.Multiplier = Multiplier;
			Hits.Add(Hit);
		}
		return 0.0;
	}

	/** Health after an adjustment: never above the maximum, never below 1 (the scaler never kills and never revives). */
	static double Apply(double Health, double Adjust, double MaxHealth)
	{
		if (Health <= 0.0)
		{
			return Health;
		}
		return FMath::Clamp(Health + Adjust, 1.0, FMath::Max(1.0, MaxHealth));
	}

private:
	void Prune(double Time)
	{
		Losses.RemoveAll([Time](const FLoss& Loss) { return Time - Loss.Time > Window; });
		Hits.RemoveAll([Time](const FHit& Hit) { return Time - Hit.Time > Window; });
	}
};
