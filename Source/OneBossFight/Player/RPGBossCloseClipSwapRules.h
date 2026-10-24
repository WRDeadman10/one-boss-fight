// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"

/** Pure mapping between the pack's close montages and the project-owned authored replacements. */
namespace RPGBossCloseClipSwapRules
{
	inline FName ReplacementFor(FName PackMontageName)
	{
		if (PackMontageName == TEXT("GS_Attack03_Montage")) return TEXT("AM_Boss01_A1");
		if (PackMontageName == TEXT("GS_Attack01_Montage")) return TEXT("AM_Boss01_A3a");
		if (PackMontageName == TEXT("GS_Attack02_Montage")) return TEXT("AM_Boss01_A3b");
		return NAME_None; // GS_Attack04_Montage (A1b) intentionally remains the pack montage.
	}

	inline bool IsPackCloseMontage(FName Name)
	{
		return Name == TEXT("GS_Attack01_Montage") || Name == TEXT("GS_Attack02_Montage") || Name == TEXT("GS_Attack03_Montage") || Name == TEXT("GS_Attack04_Montage");
	}
}
