// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "RPGBossLowSweep.generated.h"

/**
 * The hit of A4, the low sweep (Master Design Freeze 16 A4).
 * The pack has no low attack, so the damage is not a pack weapon trace: a blade of fixed height lies on the floor and turns about the boss from SweepFromDegrees to SweepToDegrees (positive = the boss's right)
 * while the attack tracker's move A4 is in its active window (the angle follows the montage position, so a changed play rate moves it with the clip).
 *   - Each tick the blade covers the angles it crossed since the last tick (a swept test, so a fast blade cannot skip a player), between InnerRadius and Reach cm from the boss, only up to BladeHeight above the floor.
 *   - A player whose feet are at or above BladeHeight is not hit (jumpable, B09); one that is invulnerable (the pack's Status.Invulnerable during the dodge i-frames) is not hit while it is; the world blocks the
 *     blade (a line from the boss to the player at floor height that meets arena geometry means no hit).
 *   - One damage event per attack instance. The attack's heading is locked by the tracker, so the arc does not follow the player.
 *   - Not done: the knockdown reaction (the pack has no entry point for it); the player takes damage only.
 * Attached by RPGPlayerMovesSubsystem. Debug: a line along the blade while it is active (not in shipping).
 */
UCLASS(ClassGroup = (Boss))
class ONEBOSSFIGHT_API URPGBossLowSweep : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGBossLowSweep();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sweep")
	bool bEnabled = true;

	/** The tracker move that drives the blade. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sweep")
	FName MoveId = TEXT("A4");

	/** Health taken from a player the blade hits. The Freeze table says 50 for A4, written for a larger health pool: the pack player has 120 health, the factor 0.4 used for A2 and A6 gives 20. Deviation, see DELTA_AUDIT. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sweep", meta = (ClampMin = "0.0"))
	float Damage = 20.f;

	/** The blade's reach from the boss's centre (cm, horizontal) and the dead zone next to the body. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sweep", meta = (ClampMin = "1.0"))
	float Reach = 380.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sweep", meta = (ClampMin = "0.0"))
	float InnerRadius = 60.f;

	/** Blade top above the floor (cm). Antigravity's request A-04: the whole blade below 40 cm. A player whose feet are at or above this height is not touched. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sweep", meta = (ClampMin = "1.0"))
	float BladeHeight = 40.f;

	/** The blade starts at SweepFromDegrees from the boss's forward (committed) direction and ends at SweepToDegrees; positive is to the boss's right. 180 degrees in front, right to left (Freeze: no more arc than the clip can reach). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sweep")
	float SweepFromDegrees = 90.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sweep")
	float SweepToDegrees = -90.f;

	/** Tests and scripted fights: starts A4 on the boss now (the clip plays through the tracker). Returns false if the boss may not start it. */
	UFUNCTION(BlueprintCallable, Category = "Sweep")
	bool StartForTest(bool bForce = true);

	/** Ends the sweep at once (a stance break or a phase transition: Freeze 17.3 item 2 and 18.1). No damage after this call. */
	void Cancel(const TCHAR* Reason) { End(Reason); }

	UFUNCTION(BlueprintPure, Category = "Sweep")
	bool IsBladeActive() const { return bActive; }

	/** Blade angle now in degrees from the committed forward direction (valid while active). */
	UFUNCTION(BlueprintPure, Category = "Sweep")
	float GetBladeAngle() const { return BladeAngle; }

	/** Counters (tests): sweeps run, players hurt, players that stood above the blade, that were invulnerable, or that the arena's geometry shielded. */
	UFUNCTION(BlueprintPure, Category = "Sweep")
	int32 GetSweepCount() const { return SweepCount; }

	UFUNCTION(BlueprintPure, Category = "Sweep")
	int32 GetHitCount() const { return HitCount; }

	UFUNCTION(BlueprintPure, Category = "Sweep")
	int32 GetJumpedCount() const { return JumpedCount; }

	UFUNCTION(BlueprintPure, Category = "Sweep")
	int32 GetInvulnerableCount() const { return InvulnerableCount; }

	UFUNCTION(BlueprintPure, Category = "Sweep")
	int32 GetBlockedCount() const { return BlockedCount; }

protected:
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	void Begin(float ForwardYaw);
	void End(const TCHAR* Reason);
	void Test(float FromAngle, float ToAngle);

	bool bActive = false;
	bool bDamaged = false; // this attack instance has hurt the player
	bool bJumpCounted = false;
	bool bInvulnerableCounted = false;
	bool bBlockedCounted = false;
	float BladeAngle = 0.f;
	float PreviousAngle = 0.f;
	float ForwardYaw = 0.f;
	float GroundZ = 0.f;
	int32 LastInstance = -1;
	int32 SweepGeneration = 0;
	int32 SweepCount = 0;
	int32 HitCount = 0;
	int32 JumpedCount = 0;
	int32 InvulnerableCount = 0;
	int32 BlockedCount = 0;
	bool bDead = false;
	float DeathCheck = 0.f;
};
