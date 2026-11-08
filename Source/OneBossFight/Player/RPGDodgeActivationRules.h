// Copyright One Boss Fight. All Rights Reserved.
#pragma once

/** Guard the one-tick first-press recovery against blocking, repeats and double activation. */
namespace RPGDodgeActivationRules
{
	constexpr bool ShouldRetryFirstPress(bool bFirstPress, bool bCanActivate, bool bAbilityActive, bool bAlreadyAttempted) noexcept
	{
		return bFirstPress && bCanActivate && !bAbilityActive && !bAlreadyAttempted;
	}
}
