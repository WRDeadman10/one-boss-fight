// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"

namespace RPGFlaskHudRules
{
	enum class EFill : uint8
	{
		Unavailable,
		Empty,
		Half,
		Full
	};

	/** Full is strictly above two thirds of the recorded starting count; zero is empty; every positive remaining count at or below two thirds is half. */
	inline EFill DecideFill(int32 Count, int32 Maximum)
	{
		if (Count < 0 || Maximum <= 0)
		{
			return EFill::Unavailable;
		}
		if (Count == 0)
		{
			return EFill::Empty;
		}
		return Count * 3 > Maximum * 2 ? EFill::Full : EFill::Half;
	}

	inline FString FillName(EFill Fill)
	{
		switch (Fill)
		{
		case EFill::Empty: return TEXT("Empty");
		case EFill::Half: return TEXT("Half");
		case EFill::Full: return TEXT("Full");
		default: return TEXT("Unavailable");
		}
	}
}
