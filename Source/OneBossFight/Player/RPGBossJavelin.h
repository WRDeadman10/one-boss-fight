// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RPGBossJavelin.generated.h"

class URPGBossHealPunish;
class UStaticMeshComponent;
class UPointLightComponent;

/** How a javelin ended (tests and logs). */
UENUM()
enum class ERPGJavelinResult : uint8
{
	Hit,        // damaged the player
	Dodged,     // passed through the player while invulnerable (dodge i-frames) and flew on
	HitWorld,   // stopped by arena geometry
	Expired,    // flew its full range
	Cancelled   // the boss died, the encounter was reset or the player died
};

/**
 * The thrown javelin of A5 (Master Design Freeze 16 A5). It is a real projectile: it leaves the boss's hand, flies in a straight line at Speed and is moved by a swept sphere each tick, so it cannot skip a thin target
 * and it never appears at the player. It is not a physics actor and not a pack projectile (the pack has none for this).
 *   - The player is hurt once if the sphere meets the player's capsule while the player is not invulnerable; i-frames let it pass through (the javelin goes on and may still hit geometry).
 *   - Arena geometry (static and dynamic world objects) stops it. It stops at MaxRange, when the boss dies, or when the encounter generation changed since it was thrown (a reset).
 * Placeholder look: a glowing cylinder with a point light, until Antigravity's NS_Boss01_Javelin (V-08) exists.
 */
UCLASS(NotBlueprintable)
class ONEBOSSFIGHT_API ARPGBossJavelin : public AActor
{
	GENERATED_BODY()

public:
	ARPGBossJavelin();

	/** Sets the flight (called right after spawning). */
	void Launch(URPGBossHealPunish* InOwner, const FVector& InDirection, float InSpeed, float InRadius, float InDamage, float InMaxRange, int32 InGeneration, int32 InAttackInstance);

	virtual void Tick(float DeltaSeconds) override;

	/** Ends the flight now (a stance break or a phase transition). */
	void Cancel(const TCHAR* Reason) { Finish(ERPGJavelinResult::Cancelled, Reason); }

private:
	void Finish(ERPGJavelinResult Result, const TCHAR* Reason);

	UPROPERTY()
	TObjectPtr<UStaticMeshComponent> Mesh;

	UPROPERTY()
	TObjectPtr<UPointLightComponent> Glow;

	TWeakObjectPtr<URPGBossHealPunish> Source;
	FVector Direction = FVector::ForwardVector;
	float Speed = 1800.f;
	float Radius = 25.f;
	float Damage = 12.f;
	float MaxRange = 3000.f;
	float Travelled = 0.f;
	int32 Generation = 0;
	int32 AttackInstance = 0; // the tracker's attack instance of the throw (the damage resolver's duplicate key)
	bool bDodgedCounted = false;
	bool bFinished = false;
};
