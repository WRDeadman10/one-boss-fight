// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"

/** Pure guards for the generation supplied by the encounter reset broadcast. */
namespace RPGEncounterGenerationRules
{
	/**
	 * Accept only a strictly newer, usable participant generation. Generation zero is reserved for
	 * "not initialized" and MAX_uint64 is refused so the lifecycle never enters an exhausted state.
	 */
	inline bool CanAdvance(uint64 CurrentGeneration, uint64 BroadcastGeneration, FString& OutError)
	{
		OutError.Reset();
		if (CurrentGeneration == MAX_uint64 || BroadcastGeneration == MAX_uint64)
		{
			OutError = TEXT("EncounterActivation.GenerationExhausted");
			return false;
		}
		if (BroadcastGeneration == 0 || BroadcastGeneration <= CurrentGeneration)
		{
			OutError = TEXT("EncounterActivation.GenerationNotIncreasing");
			return false;
		}
		return true;
	}
}
