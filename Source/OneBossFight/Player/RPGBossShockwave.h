// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "RPGBossShockwave.generated.h"

class URPGAttackTracker;

/**
 * The radial ground wave of A6, the phase two leap (Master Design Freeze 16 A6).
 * The pack's leap ends in a central hit (its own trace, 0.75 to 1.17 s of GS_LeapAttack). This component adds what the pack lacks: a wave that leaves the landing point and travels outwards along the floor.
 *   - It starts when the attack tracker's move A6 opens its active window (once per attack instance), at the boss's feet, with StartRadius and grows at Speed up to MaxRadius.
 *   - A player is hit when the wave front (a band Thickness wide) passes over them, unless their feet are at least JumpClearance above the floor (jumpable), or they are invulnerable (the pack's
 *     Status.Invulnerable tag during dodge i-frames), or the move already hurt them (the central hit takes priority: one damage event per move per target).
 *   - The damage is written to the health attribute (the pack has no entry point for damage without a weapon trace). It does not play a hit reaction yet (TASKS G2-4).
 *   - It ends at MaxRadius, when the boss dies, or when the encounter generation changes.
 * Placeholder visual: a debug ring (not in shipping); the real wave effect is an art request. Attached by RPGPlayerMovesSubsystem.
 */
UCLASS(ClassGroup = (Boss))
class ONEBOSSFIGHT_API URPGBossShockwave : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGBossShockwave();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Wave")
	bool bEnabled = true;

	/** The tracker move that launches the wave. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Wave")
	FName MoveId = TEXT("A6");

	/** Health points taken from a player caught by the wave. The Freeze table says 120 for A6, written for a larger health pool: the pack player has 120 health, and the pack's own slam hits for 36 where the
	 *  Freeze says 90 (a factor of 0.4), so the same factor gives 48. Registered in DELTA_AUDIT as a deviation. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Wave", meta = (ClampMin = "0.0"))
	float Damage = 48.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Wave", meta = (ClampMin = "0.0"))
	float StartRadius = 200.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Wave", meta = (ClampMin = "1.0"))
	float MaxRadius = 1100.f;

	/** cm per second. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Wave", meta = (ClampMin = "1.0"))
	float Speed = 1000.f;

	/** Width of the wave front (cm), so the band passes a point for Thickness / Speed seconds. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Wave", meta = (ClampMin = "1.0"))
	float Thickness = 180.f;

	/** Feet height above the floor (cm) that clears the wave. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Wave", meta = (ClampMin = "0.0"))
	float JumpClearance = 50.f;

	/** Tests and scripted fights: launches a wave at the boss's feet now, as the leap's landing would. */
	UFUNCTION(BlueprintCallable, Category = "Wave")
	void LaunchForTest();

	/** Ends the wave at once (a stance break or a phase transition). */
	void Cancel(const TCHAR* Reason) { Stop(Reason); }

	UFUNCTION(BlueprintPure, Category = "Wave")
	bool IsWaveActive() const { return bActive; }

	UFUNCTION(BlueprintPure, Category = "Wave")
	float GetRadius() const { return Radius; }

	/** Counters (tests): waves launched, players hurt, players that cleared it by jumping, by invulnerability, or that the central hit already hurt. */
	UFUNCTION(BlueprintPure, Category = "Wave")
	int32 GetLaunchCount() const { return LaunchCount; }

	UFUNCTION(BlueprintPure, Category = "Wave")
	int32 GetHitCount() const { return HitCount; }

	UFUNCTION(BlueprintPure, Category = "Wave")
	int32 GetJumpedCount() const { return JumpedCount; }

	UFUNCTION(BlueprintPure, Category = "Wave")
	int32 GetInvulnerableCount() const { return InvulnerableCount; }

	UFUNCTION(BlueprintPure, Category = "Wave")
	int32 GetCentralPriorityCount() const { return CentralPriorityCount; }

protected:
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	void Launch();
	void Stop(const TCHAR* Reason);
	void Resolve();

	bool bActive = false;
	bool bClearedBand = false;
	bool bResolved = false; // this wave has already decided about the player (one damage event per move)
	float Radius = 0.f;
	FVector Origin = FVector::ZeroVector;
	float GroundZ = 0.f;
	double HealthAtLaunch = -1.0;
	int32 LastInstance = -1;
	int32 LaunchGeneration = 0;
	int32 LaunchCount = 0;
	int32 HitCount = 0;
	int32 JumpedCount = 0;
	int32 InvulnerableCount = 0;
	int32 CentralPriorityCount = 0;
	bool bDead = false;
	float DeathCheck = 0.f;
};
