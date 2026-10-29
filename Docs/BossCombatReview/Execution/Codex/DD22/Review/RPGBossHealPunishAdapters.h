// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"
#include "Player/RPGEncounterBinding.h"

/**
 * C265 UNWIRED authored HealPunish record:14 public fields only, no runtime state.
 * All TEN floats finite first in native header order. Domain order:
 * MinRange>=0/cap; MaxRange>0/cap/>MinRange; Cooldown>=0/cap; Damage>=0(no cap);
 * FlightTime>=0.05/cap; MinSpeed>0/cap; MaxSpeed>0/cap then MinSpeed<=MaxSpeed;
 * JavelinRadius>0/cap; JavelinMaxRange>0/cap; nonempty SpawnSockets with each name
 * not None/no whitespace/control; finally AimHeight in[-cap,cap]. Bool values any.
 * These are AUTHORED RECORD CONTRACTS, not native guards or balance approval.
 * Editor minimum1 is not imposed;0.05 flight floor is an explicit authored choice.
 * Empty socket list is refused instead of silently invoking native fallback.
 * No ASCII regex, uniqueness rule, bone/socket existence or class check is invented.
 *
 * MaxAuthoredMagnitude=1e6 screens float-extreme values, not actual arena tuning.
 * Signed AimHeight is legal. Damage is a finite nonnegative health payload, not
 * trajectory geometry; it has no ceiling. Native world/time/trajectory inputs
 * remain separate: no unrestricted runtime arithmetic or gameplay proof.
 *
 * Move A5 and the player potion montage are HARDCODED in native cpp and UNRESOLVED
 * by this record. No move/ability/timing/socket resolution is claimed.
 * Exact class/live/not registered/not begun and valid not-begun owner precede
 * whole-record validation, then all14 fields are copied (array by value).
 * No pending/cooldown/counter/generation, DrinkMontage/Flying or tick flag is
 * assigned. No load, create, register, BeginPlay, Tick, heal notification, release,
 * launch, report or CancelAll operation. ComponentBegunPlay stays source-only.
 * Plan stays outside preflight/preparation/reservations: no Ready/legacy suppression.
 */
namespace RPGBossHealPunishAdapters
{
	inline constexpr float MaxAuthoredMagnitude = 1.0e6f;
	inline constexpr float MinAuthoredFlightTime = 0.05f;
	inline constexpr const TCHAR* FieldbEnabled = TEXT("HealPunish.bEnabled");
	inline constexpr const TCHAR* FieldMinRange = TEXT("HealPunish.MinRange");
	inline constexpr const TCHAR* FieldMaxRange = TEXT("HealPunish.MaxRange");
	inline constexpr const TCHAR* FieldCooldown = TEXT("HealPunish.Cooldown");
	inline constexpr const TCHAR* FieldDamage = TEXT("HealPunish.Damage");
	inline constexpr const TCHAR* FieldFlightTime = TEXT("HealPunish.FlightTime");
	inline constexpr const TCHAR* FieldMinSpeed = TEXT("HealPunish.MinSpeed");
	inline constexpr const TCHAR* FieldMaxSpeed = TEXT("HealPunish.MaxSpeed");
	inline constexpr const TCHAR* FieldJavelinRadius = TEXT("HealPunish.JavelinRadius");
	inline constexpr const TCHAR* FieldJavelinMaxRange = TEXT("HealPunish.JavelinMaxRange");
	inline constexpr const TCHAR* FieldSpawnSockets = TEXT("HealPunish.SpawnSockets");
	inline constexpr const TCHAR* FieldAimHeight = TEXT("HealPunish.AimHeight");
	inline constexpr const TCHAR* FieldbRespondToHeal = TEXT("HealPunish.bRespondToHeal");
	inline constexpr const TCHAR* FieldbCancelJavelinsOnInterrupt = TEXT("HealPunish.bCancelJavelinsOnInterrupt");
	ONEBOSSFIGHT_API bool ValidateHealPunish(const FRPGHealPunishConfig& Record, FString& OutError);
	ONEBOSSFIGHT_API bool ConfigureHealPunish(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError);
	ONEBOSSFIGHT_API FRPGComponentPlan MakeHealPunishPlan();
}
