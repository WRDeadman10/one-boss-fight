// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "Player/RPGEncounterBinding.h"

namespace RPGBossAttackTrackerAdapters
{
	inline constexpr const TCHAR* FieldAttacks = TEXT("AttackTracker.Attacks");
	inline constexpr const TCHAR* FieldEnabled = TEXT("AttackTracker.bEnabled");
	inline constexpr const TCHAR* FieldVetoIllegalStarts = TEXT("AttackTracker.bVetoIllegalStarts");
	inline constexpr const TCHAR* FieldBranchRange = TEXT("AttackTracker.BranchRange");
	inline constexpr const TCHAR* FieldBranchConeDegrees = TEXT("AttackTracker.BranchConeDegrees");
	inline constexpr const TCHAR* FieldUseMontageNotifyTimings = TEXT("bUseMontageNotifyTimings");

	ONEBOSSFIGHT_API bool ValidateAttackTracker(const FRPGAttackTrackerConfig& Config, FString& OutError);
	ONEBOSSFIGHT_API bool IsNativeDefault(const FRPGAttackTrackerConfig& Config);
	ONEBOSSFIGHT_API bool ConfigureAttackTracker(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError);
	ONEBOSSFIGHT_API FRPGComponentPlan MakeAttackTrackerPlan();
}
