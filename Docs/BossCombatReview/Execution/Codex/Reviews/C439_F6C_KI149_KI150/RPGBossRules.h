// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"

/**
 * The Freeze 21 priority order for the boss's big state changes, in one place so the components and an automation test share it (SPEC_M4, Freeze lines 889 to 905):
 * 1 Dead, 2 Reset, 3 phase transition (except one queued behind a stance break), 4 accepted riposte, 5 stance break, 6 committed attack, 7 selection.
 * Header only, no Unreal object is touched, so it can be tested without a world.
 */
namespace RPGBossRules
{
	struct FFlags
	{
		bool bDead = false;
		bool bDormant = false;
		bool bTransition = false;
		bool bStaggered = false;
		bool bPhaseTwo = false;
		bool bCooldown = false;
	};

	/** What a request for a stance break turns into. */
	enum class EBreakResult : uint8 { Started, Dead, Dormant, Transition, AlreadyStaggered, Cooldown };

	/** What the phase two threshold check turns into. */
	enum class ETransitionResult : uint8 { Start, NotReady, Dead, Dormant, AlreadyDone, AboveThreshold, QueuedBehindStagger };

	inline const TCHAR* Name(EBreakResult Result)
	{
		switch (Result)
		{
		case EBreakResult::Started: return TEXT("started");
		case EBreakResult::Dead: return TEXT("dead");
		case EBreakResult::Dormant: return TEXT("dormant");
		case EBreakResult::Transition: return TEXT("transition");
		case EBreakResult::AlreadyStaggered: return TEXT("staggered");
		case EBreakResult::Cooldown: return TEXT("cooldown");
		}
		return TEXT("?");
	}

	inline const TCHAR* Name(ETransitionResult Result)
	{
		switch (Result)
		{
		case ETransitionResult::Start: return TEXT("start");
		case ETransitionResult::NotReady: return TEXT("not ready");
		case ETransitionResult::Dead: return TEXT("dead");
		case ETransitionResult::Dormant: return TEXT("dormant");
		case ETransitionResult::AlreadyDone: return TEXT("already done");
		case ETransitionResult::AboveThreshold: return TEXT("above threshold");
		case ETransitionResult::QueuedBehindStagger: return TEXT("queued behind the stance break");
		}
		return TEXT("?");
	}

	/** Order: dead, dormant, phase transition (it is not interrupted by a normal break, Freeze 729), a break already running (exactly one break, 713 and 754), the cooldown (skipped when bIgnoreCooldown), else the break starts. */
	inline EBreakResult ResolveBreak(const FFlags& F, bool bIgnoreCooldown)
	{
		if (F.bDead) { return EBreakResult::Dead; }
		if (F.bDormant) { return EBreakResult::Dormant; }
		if (F.bTransition) { return EBreakResult::Transition; }
		if (F.bStaggered) { return EBreakResult::AlreadyStaggered; }
		if (F.bCooldown && !bIgnoreCooldown) { return EBreakResult::Cooldown; }
		return EBreakResult::Started;
	}

	/** Order: no maximum, dead (the lethal crossing wins, Freeze 765 and 1269), dormant, phase two already begun (bPhaseTwo is set together with bTransition, so it covers a running transition too: idempotent, 764),
	 *  above the threshold, a stance break running (queued: the transition starts when the break ends, 770 and 1201), else it starts. Equality starts (the Freeze says at or below). */
	inline ETransitionResult ResolveTransition(const FFlags& F, double Health, double Max, float Fraction)
	{
		if (Max <= 0.0) { return ETransitionResult::NotReady; }
		if (Health <= 0.0 || F.bDead) { return ETransitionResult::Dead; }
		if (F.bDormant) { return ETransitionResult::Dormant; }
		if (F.bPhaseTwo) { return ETransitionResult::AlreadyDone; }
		if (Health / Max > Fraction) { return ETransitionResult::AboveThreshold; }
		if (F.bStaggered) { return ETransitionResult::QueuedBehindStagger; }
		return ETransitionResult::Start;
	}
}
