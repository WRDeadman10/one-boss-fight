// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"
#include "Player/RPGEncounterBinding.h"

/** C275 UNWIRED authored record contracts, not native guards. Five fields, no
 * numeric field: no NotFinite, magnitude ceiling or numeric arithmetic audit.
 * Class/property FNames are syntactic identities only, no suffix/existence rule.
 * Three montage paths required and well-formed, no registry/mount/class/load check.
 * No duplicate rule: identical replacement assets do not create extra components;
 * the three existing pack slots may independently point at the same montage.
 * Live ability reflection, permanent-failure guard, four-entry/three-candidate
 * pack montage rules, playback/timing and successful swap remain UNRESOLVED.
 * Whole record validates after lifecycle checks before five assignments.
 * No transient state, ability, loaded montage or test-enable knob is touched.
 * No BeginPlay, Tick, load, preload, ApplyNowForTest or gameplay operation.
 */
namespace RPGBossCloseClipSwapAdapters
{
	inline constexpr const TCHAR* FieldCloseAbilityClassName = TEXT("CloseClipSwap.CloseAbilityClassName");
	inline constexpr const TCHAR* FieldAttackMontagesName = TEXT("CloseClipSwap.AttackMontagesName");
	inline constexpr const TCHAR* FieldA1Montage = TEXT("CloseClipSwap.A1Montage");
	inline constexpr const TCHAR* FieldA3aMontage = TEXT("CloseClipSwap.A3aMontage");
	inline constexpr const TCHAR* FieldA3bMontage = TEXT("CloseClipSwap.A3bMontage");
	ONEBOSSFIGHT_API bool ValidateCloseClipSwap(const FRPGCloseClipSwapConfig& Record, FString& OutError);
	ONEBOSSFIGHT_API bool ConfigureCloseClipSwap(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError);
	ONEBOSSFIGHT_API FRPGComponentPlan MakeCloseClipSwapPlan();
}
