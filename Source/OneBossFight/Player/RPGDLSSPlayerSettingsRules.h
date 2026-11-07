// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include <cstdint>

namespace RPGDLSSPlayerSettingsRules
{
	enum class EPlayerMode : uint8_t { Off, DLAA, Quality, Balanced, Performance };
	enum class ERuntimeMode : uint8_t { TSR, DLAA, Quality, Balanced, Performance };

	constexpr ERuntimeMode Resolve(EPlayerMode Requested, bool bSupported) noexcept
	{
		if (!bSupported || Requested == EPlayerMode::Off)
		{
			return ERuntimeMode::TSR;
		}
		switch (Requested)
		{
		case EPlayerMode::DLAA: return ERuntimeMode::DLAA;
		case EPlayerMode::Quality: return ERuntimeMode::Quality;
		case EPlayerMode::Balanced: return ERuntimeMode::Balanced;
		case EPlayerMode::Performance: return ERuntimeMode::Performance;
		default: return ERuntimeMode::TSR;
		}
	}
}
