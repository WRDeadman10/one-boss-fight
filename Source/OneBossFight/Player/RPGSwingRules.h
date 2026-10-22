// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Player/RPGWeaponAttackTable.h"

/**
 * The rules of the swing tracker (Gate 3, M10 and M11) with no Unreal object in them, so the automation tests can check each one without a world: which hyperarmor window a swing gets, when the window wants the effect,
 * how much stamina the swing takes on top of the pack's own cost, and when the pack's timed immunity effect has to be applied again.
 */
namespace RPGSwingRules
{
	/** The hyperarmor window of a swing in montage seconds: the weapon attack table row's window, replaced by a test override when there is one. Both outputs are -1 when the swing has none. */
	inline void ResolveWindow(const FRPGWeaponAttackRow& Row, const FVector2D* Override, float& OutStart, float& OutEnd)
	{
		OutStart = -1.f;
		OutEnd = -1.f;
		if (Row.HasHyperArmor())
		{
			OutStart = Row.HyperArmorStart;
			OutEnd = Row.HyperArmorEnd;
		}
		if (Override)
		{
			OutStart = Override->X;
			OutEnd = Override->Y;
		}
	}

	/** True when a window [Start, End] wants the effect at this montage position (both ends inclusive; a window without a start or with End not after Start never opens). */
	inline bool WindowOpen(float Start, float End, float Position)
	{
		return Start >= 0.f && End > Start && Position >= Start && Position <= End;
	}

	/** Stamina taken (positive) or given back (negative) on top of the pack's own cost so that the swing costs Wanted in total. Wanted below zero: the row leaves the pack's cost (0). A positive extra never takes
	 *  more than the stamina left (the value never goes below zero). */
	inline float StaminaExtra(float Wanted, float PackCost, double StaminaNow)
	{
		if (Wanted < 0.f)
		{
			return 0.f;
		}
		float Extra = Wanted - PackCost;
		if (Extra > 0.f)
		{
			Extra = FMath::Min(Extra, static_cast<float>(FMath::Max(StaminaNow, 0.0)));
		}
		return Extra;
	}

	/** The pack's immunity effect (GE_HitStunImmune) lasts 4 s and is not applied again while it is active: a window that is still wanted when the effect is RefreshAfter seconds old needs it applied again. */
	inline bool NeedsRefresh(double Now, double AppliedAt, float RefreshAfter)
	{
		return RefreshAfter > 0.f && Now - AppliedAt >= RefreshAfter;
	}
}
