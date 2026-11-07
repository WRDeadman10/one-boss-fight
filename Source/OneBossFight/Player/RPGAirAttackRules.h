// Copyright One Boss Fight. All Rights Reserved.

#pragma once

namespace RPGAirAttackRules
{
	enum class EAirAttackRoute : unsigned char { Pack, AirLight, AirHeavy };

	/** Use the authored air clip only while falling; empty or grounded routes preserve pack behavior. */
	constexpr EAirAttackRoute Select(bool bFalling, bool bStrongInput, bool bOptionalMontageAvailable) noexcept
	{
		if (!bFalling || !bOptionalMontageAvailable)
		{
			return EAirAttackRoute::Pack;
		}
		return bStrongInput ? EAirAttackRoute::AirHeavy : EAirAttackRoute::AirLight;
	}
}
