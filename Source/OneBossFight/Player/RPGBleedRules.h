// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"

/**
 * The bleed status rules of the dexterity build (Freeze 20.2, parameter registry 36), in one place so the component and an automation test share them. Header only, no Unreal object is touched.
 * Buildup per hit comes from the weapon attack table (20 for the dex weapons). At the threshold (100) the status procs ONCE: the buildup is reset, the next threshold is raised (+20 up to 200) and the boss loses
 * 10.5 percent of its maximum health in one burst. Nothing builds up on a dead boss, a sleeping boss or during the phase transition (Freeze 18 and 20.2), and two hits in the frame of a proc do not proc again.
 */
namespace RPGBleedRules
{
	struct FConfig
	{
		float InitialThreshold = 100.f;
		float ThresholdIncrease = 20.f;
		float ThresholdMax = 200.f;
		/** Fraction of the boss's maximum health taken by a proc. */
		float HpFraction = 0.03f; // 0.105 at 500 health (Freeze 20.2, a tunable custom rule); 0.03 of the 2000 maximum health of the 2 to 4 minute duel is 60 per proc
	};

	struct FState
	{
		float Buildup = 0.f;
		float Threshold = 100.f;
		int32 Procs = 0;
	};

	enum class EResult : uint8 { Added, Proc, IgnoredAmount, IgnoredDead, IgnoredDormant, IgnoredTransition, IgnoredSameFrame };

	inline const TCHAR* Name(EResult Result)
	{
		switch (Result)
		{
		case EResult::Added: return TEXT("added");
		case EResult::Proc: return TEXT("proc");
		case EResult::IgnoredAmount: return TEXT("no buildup");
		case EResult::IgnoredDead: return TEXT("dead");
		case EResult::IgnoredDormant: return TEXT("dormant");
		case EResult::IgnoredTransition: return TEXT("transition");
		case EResult::IgnoredSameFrame: return TEXT("same frame as a proc");
		}
		return TEXT("?");
	}

	/** One hit's buildup. Order of the checks: no amount, dead, dormant, phase transition, a proc already happened this frame, else it is added and a threshold crossing procs once. */
	inline EResult Apply(FState& State, const FConfig& Config, float Amount, bool bDead, bool bDormant, bool bTransition, bool bProcThisFrame)
	{
		if (Amount <= 0.f) { return EResult::IgnoredAmount; }
		if (bDead) { return EResult::IgnoredDead; }
		if (bDormant) { return EResult::IgnoredDormant; }
		if (bTransition) { return EResult::IgnoredTransition; }
		if (bProcThisFrame) { return EResult::IgnoredSameFrame; }
		State.Buildup += Amount;
		if (State.Buildup >= State.Threshold)
		{
			State.Buildup = 0.f;
			++State.Procs;
			State.Threshold = FMath::Min(State.Threshold + Config.ThresholdIncrease, Config.ThresholdMax);
			return EResult::Proc;
		}
		return EResult::Added;
	}

	/** The health a proc takes: the fraction of the maximum, but never the last point (a proc is a burst of damage, the kill stays with the weapon). */
	inline float ProcDamage(float MaxHealth, float Health, const FConfig& Config)
	{
		return FMath::Clamp(MaxHealth * Config.HpFraction, 0.f, FMath::Max(0.f, Health - 1.f));
	}
}
