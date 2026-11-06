// Copyright One Boss Fight. All Rights Reserved.

#pragma once

/** The tap-level choice between the pack's dodge roll and the optional backstep clip. */
namespace RPGDodgeInputRules
{
	enum class EDodgeTapDecision : unsigned char
	{
		Roll,
		Backstep,
	};

	/**
	 * Classify one dodge tap. The caller supplies direction intent using its established input threshold.
	 * Without a backstep clip, keep the current roll behavior. This rule is deliberately stateless, so
	 * repeated standing taps may each choose another backstep. The pack's dodge ability remains the sole
	 * owner of stamina cost for either choice.
	 */
	constexpr EDodgeTapDecision DecideTap(bool bHasDirectionInput, bool bBackstepClipAvailable) noexcept
	{
		return !bHasDirectionInput && bBackstepClipAvailable
			? EDodgeTapDecision::Backstep
			: EDodgeTapDecision::Roll;
	}
}
