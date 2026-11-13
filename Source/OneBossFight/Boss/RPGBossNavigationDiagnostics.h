// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "Navigation/PathFollowingComponent.h"

namespace RPGBossNavigationDiagnostics
{
	inline const TCHAR* CodeName(EPathFollowingResult::Type Code)
	{
		switch (Code)
		{
		case EPathFollowingResult::Success: return TEXT("Success");
		case EPathFollowingResult::Blocked: return TEXT("Blocked");
		case EPathFollowingResult::OffPath: return TEXT("OffPath");
		case EPathFollowingResult::Aborted: return TEXT("Aborted");
		case EPathFollowingResult::Invalid: return TEXT("Invalid");
		default: return TEXT("Unknown");
		}
	}

	inline FString Format(FName Route, uint64 Generation, uint32 RequestId, EPathFollowingResult::Type Code,
		uint16 Flags, const FVector& ActorLocation, const FVector& GoalLocation)
	{
		return FString::Printf(TEXT("route=%s generation=%llu request=%u code=%s codeValue=%d flags=0x%04x actor=%s goal=%s remainingCm=%.1f"),
			*Route.ToString(), static_cast<unsigned long long>(Generation), RequestId, CodeName(Code), int32(Code),
			uint32(Flags), *ActorLocation.ToCompactString(), *GoalLocation.ToCompactString(), FVector::Dist2D(ActorLocation, GoalLocation));
	}
}
