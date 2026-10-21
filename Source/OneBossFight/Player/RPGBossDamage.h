// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "CollisionQueryParams.h"
#include "Components/CapsuleComponent.h"
#include "GameFramework/Character.h"
#include "GameplayTagContainer.h"
#include "Pack/RPGBlueprintCall.h"

/**
 * Damage the boss's own moves (A4 low sweep, A5 javelin, A6 wave) deal to the player. The pack has no entry point for damage without a weapon trace, so the health attribute is written directly (as URPGBossShockwave does).
 * Invulnerability is read where the damage resolves (Freeze 32.1): the pack's Status.Invulnerable tag, set during the dodge i-frames.
 */
namespace RPGBossDamage
{
	inline bool IsInvulnerable(AActor* Player)
	{
		bool bInvulnerable = false;
		RPGPack::CallBlueprintFunction(Player, TEXT("HasMatchingGameplayTag"),
			[](UFunction& F, uint8* P) { RPGPack::SetTag(F, P, TEXT("TagToCheck"), FGameplayTag::RequestGameplayTag(TEXT("Status.Invulnerable"), false)); },
			[&bInvulnerable](UFunction& F, uint8* P)
			{
				if (const FBoolProperty* Result = CastField<FBoolProperty>(F.FindPropertyByName(TEXT("ReturnValue"))))
				{
					bInvulnerable = Result->GetPropertyValue_InContainer(P);
				}
			});
		return bInvulnerable;
	}

	inline bool IsAlive(const AActor* Actor)
	{
		double Health = 0.0;
		return Actor && RPGPack::ReadAttribute(Actor, TEXT("Attribute.Health"), false, Health) && Health > 0.0;
	}

	/** Takes Damage from the player's health (never below zero). Returns the health before and after. */
	inline bool HurtPlayer(const AActor* Player, double Damage, double& Before, double& After)
	{
		Before = 0.0;
		After = 0.0;
		if (!RPGPack::ReadAttribute(Player, TEXT("Attribute.Health"), false, Before))
		{
			return false;
		}
		After = FMath::Max(0.0, Before - Damage);
		return RPGPack::WriteAttribute(Player, TEXT("Attribute.Health"), After);
	}

	/** What blocks a boss move on its way to the player: the arena's static and dynamic world objects (pawns do not). */
	inline FCollisionObjectQueryParams WorldBlockers()
	{
		FCollisionObjectQueryParams Query;
		Query.AddObjectTypesToQuery(ECC_WorldStatic);
		Query.AddObjectTypesToQuery(ECC_WorldDynamic);
		return Query;
	}

	/** Feet height above the floor under a character (capsule bottom minus the floor height the move recorded). */
	inline float FeetZ(const ACharacter* Character)
	{
		return Character->GetActorLocation().Z - (Character->GetCapsuleComponent() ? Character->GetCapsuleComponent()->GetScaledCapsuleHalfHeight() : 0.f);
	}
}
