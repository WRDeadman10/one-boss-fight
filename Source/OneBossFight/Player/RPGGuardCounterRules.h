// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include <cmath>
#include "CoreMinimal.h"

/** Pure guard-counter timing and posture rules. No engine or actor state is owned here. */
namespace RPGGuardCounterRules
{
	/** Match every weapon-style-specific pack reaction (for example GA_Sword_BlockReaction_C). */
	inline bool IsBlockReactionAbilityClass(const FString& ClassName)
	{
		return ClassName.EndsWith(TEXT("BlockReaction_C"), ESearchCase::CaseSensitive);
	}

	/** A new guarded-contact signal is the pack's block-reaction ability becoming active while the player's block state is up. */
	inline bool IsNewBlockedContact(bool bBlocking, bool bBlockReactionActive, bool bWasBlockReactionActive) noexcept
	{
		return bBlocking && bBlockReactionActive && !bWasBlockReactionActive;
	}

	// PROPOSAL defaults only; the owner has not approved or live-tested these timings/scales.
	inline constexpr double ProposedCounterWindowSeconds = 0.60;
	inline constexpr double ProposedArmedDurationSeconds = 1.20;
	inline constexpr double ProposedStrongPostureMultiplier = 2.0;

	/** A counter input is valid only for a finite, positive window and a press in its closed interval. */
	inline bool IsCounterPress(double BlockTimeSeconds, double PressTimeSeconds, double WindowSeconds) noexcept
	{
		if (!std::isfinite(BlockTimeSeconds) || !std::isfinite(PressTimeSeconds) ||
			!std::isfinite(WindowSeconds) || WindowSeconds <= 0.0)
		{
			return false;
		}

		const double SinceBlock = PressTimeSeconds - BlockTimeSeconds;
		return SinceBlock >= 0.0 && SinceBlock <= WindowSeconds;
	}

	/** Strong-kind hits receive the proposed multiplier only while armed; invalid tuning fails closed to 1x. */
	inline double PostureScale(bool bArmed, bool bStrongKind, double Multiplier) noexcept
	{
		if (!bArmed || !bStrongKind || !std::isfinite(Multiplier) || Multiplier < 1.0)
		{
			return 1.0;
		}
		return Multiplier;
	}

	/** An arm remains valid from its timestamp through the inclusive duration boundary. */
	inline bool IsArmed(double ArmedAtSeconds, double NowSeconds, double ArmedDurationSeconds) noexcept
	{
		if (!std::isfinite(ArmedAtSeconds) || !std::isfinite(NowSeconds) ||
			!std::isfinite(ArmedDurationSeconds) || ArmedDurationSeconds <= 0.0)
		{
			return false;
		}

		const double SinceArmed = NowSeconds - ArmedAtSeconds;
		return SinceArmed >= 0.0 && SinceArmed <= ArmedDurationSeconds;
	}
}
