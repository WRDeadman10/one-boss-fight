// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"
#include "Player/RPGEncounterBinding.h"

/** C269 UNWIRED authored record contracts, not native guards. No numeric field:
 * no magnitude ceiling or numeric arithmetic audit applies. Body and Sword are
 * required structural paths; Pieces may be empty but no entry may be null,
 * malformed or a duplicate FSoftObjectPath. Every record, even disabled, validates.
 * Socket is syntactic identity only; mesh/socket existence and hand_r fallback
 * remain UNRESOLVED. No class, mount, registry, existence check or load.
 * Native Apply body-load failure warns and leaves the pack mesh visible; a failed
 * piece warns and is omitted; a failed sword warns and leaves no new sword.
 * Those runtime outcomes are UNRESOLVED here, not prevented by typed structure.
 * Lifecycle guard: exact live class, unregistered/not begun, live not-begun owner.
 * Whole record validates before all five writes; no runtime/transient state write,
 * allocation, BeginPlay/Apply/enable-for-test call or load. No Ready or suppression.
 */
namespace RPGBossLookAdapters
{
	inline constexpr const TCHAR* FieldbEnabled = TEXT("Look.bEnabled");
	inline constexpr const TCHAR* FieldBody = TEXT("Look.Body");
	inline constexpr const TCHAR* FieldPieces = TEXT("Look.Pieces");
	inline constexpr const TCHAR* FieldSword = TEXT("Look.Sword");
	inline constexpr const TCHAR* FieldSwordSocket = TEXT("Look.SwordSocket");
	ONEBOSSFIGHT_API bool ValidateLook(const FRPGLookConfig& Record, FString& OutError);
	ONEBOSSFIGHT_API bool ConfigureLook(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError);
	ONEBOSSFIGHT_API FRPGComponentPlan MakeLookPlan();
}
