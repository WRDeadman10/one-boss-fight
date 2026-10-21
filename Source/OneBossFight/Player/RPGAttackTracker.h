// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "RPGAttackTracker.generated.h"

/**
 * Timing of one boss attack (Master Design Freeze section 15). All times are montage-local seconds from the montage start (what UAnimInstance::Montage_GetPosition returns),
 * so they do not depend on the play rate. Names ending in Time are timestamps, names ending in Duration are durations.
 */
class UAnimMontage;

USTRUCT(BlueprintType)
struct FRPGAttackTiming
{
	GENERATED_BODY()

	/** The move: "A2" and so on (Freeze section 4). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Attack")
	FName MoveId;

	/** The montage this move plays, by asset name. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Attack")
	FString MontageName;

	/** The boss may turn towards its target until this time; from here its heading is locked until ActiveEndTime (the commitment point). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Attack")
	float CommitTime = 0.f;

	/** The first moment the weapon can hurt (the trace window opens) and the moment the last window closes. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Attack")
	float ActiveStartTime = 0.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Attack")
	float ActiveEndTime = 0.f;

	/** The boss may choose a new action from here (end of the montage for the stand-in). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Attack")
	float RecoveryEndTime = 0.f;

	/** Degrees per second the boss turns towards the player before CommitTime. 0 = it does not turn at all in this attack. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Attack", meta = (ClampMin = "0.0"))
	float TrackTurnRate = 120.f;

	/** The second stage of a chain (Freeze 16 A3: slash 2 only when the player is in the frontal cone and in range). The branch check runs when this stage's montage starts; a failed check stops the montage. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Attack")
	bool bBranchStage = false;

	/** Moves without a pack ability (A4, A5): the animation asset that StartMove plays on the boss as a dynamic montage. MontageName is then the name of that animation. Empty for pack montages. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Attack")
	FString ClipPath;
};

/**
 * Tracking, commitment and window bookkeeping for the pack boss's attacks (Freeze 14, 32.1).
 * It watches the boss's active montage. When the montage belongs to an entry of Attacks it starts an attack instance (a counter that goes up once per attack) and then:
 *   - before CommitTime the boss turns towards the player at TrackTurnRate;
 *   - at CommitTime the heading is captured and held (the actor yaw is set back to it every tick) until ActiveEndTime, so the swing follows the committed direction;
 *   - during ActiveStartTime to ActiveEndTime the attack is "active" (the pack's trace notify opens the real hit window; this class only observes it for tests and logs);
 *   - after ActiveEndTime the heading is not touched (recovery).
 * It keeps nothing alive that the montage does not: when the montage stops for any reason (end, interrupt, stagger, phase change, death, reset) the next tick ends the attack instance and the lock stops, so no
 * rotation lock can outlive its montage. The pack montages stay unchanged; the timing numbers are read off them (DELTA_AUDIT.md).
 */
UCLASS(ClassGroup = (Boss))
class ONEBOSSFIGHT_API URPGAttackTracker : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGAttackTracker();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Attack")
	TArray<FRPGAttackTiming> Attacks;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Attack")
	bool bEnabled = true;

	/** Starts the pack ability that plays this move now (tests and scripted fights). bForce skips the ability's own activation conditions (blocked tags, cooldown). Returns false if the move is unknown or the ability refused.
	 *  A move with a ClipPath (A4, A5) has no pack ability: its clip plays as a dynamic montage in the pack's montage slot; without bForce it starts only when the boss plays no montage and is in no stance break,
	 *  phase transition or sleep. */
	UFUNCTION(BlueprintCallable, Category = "Attack")
	bool StartMove(FName MoveId, bool bForce = true);

	/** True while the boss may start a move of its own (nothing playing, no attack tracked, not staggered, not in a phase transition, not dormant, not dead). */
	UFUNCTION(BlueprintPure, Category = "Attack")
	bool IsNeutral() const;

	/** Montage position (seconds) of the tracked attack, and the timing entry of a move (false if unknown). */
	UFUNCTION(BlueprintPure, Category = "Attack")
	float GetPosition() const { return LastPosition; }

	UFUNCTION(BlueprintPure, Category = "Attack")
	bool GetTiming(FName MoveId, FRPGAttackTiming& OutTiming) const;

	/** Attack priority (Freeze 21): a new attack may not begin while the boss is staggered, in a phase transition or dormant. With this on, such a start is stopped at once and counted (a safety net:
	 *  the pack's behaviour is already held in those states). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Attack")
	bool bVetoIllegalStarts = true;

	/** Counters (tests): starts vetoed by the priority rule, and attacks that replaced another one before its active window ended (a double launch; chained stages are legal). */
	UFUNCTION(BlueprintPure, Category = "Attack")
	int32 GetIllegalStartCount() const { return IllegalStarts; }

	UFUNCTION(BlueprintPure, Category = "Attack")
	int32 GetDoubleLaunchCount() const { return DoubleLaunches; }

	/** Branch check of chained stages (A3 slash 2): the player must be within BranchRange cm (horizontal) and inside a frontal cone of BranchConeDegrees in total (Freeze 16: 120 degrees). Tunable, not a literal in code. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Attack", meta = (ClampMin = "0.0"))
	float BranchRange = 400.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Attack", meta = (ClampMin = "10.0", ClampMax = "360.0"))
	float BranchConeDegrees = 120.f;

	/** Tests: plays the montage of this move now on the boss (the pack ability that normally picks it is not involved). Returns false if the move or the montage is unknown. */
	UFUNCTION(BlueprintCallable, Category = "Attack")
	bool PlayMoveMontageForTest(FName MoveId);

	/** Counters of the branch check (stage 2 allowed / denied). */
	UFUNCTION(BlueprintPure, Category = "Attack")
	int32 GetBranchAllowedCount() const { return BranchAllowed; }

	UFUNCTION(BlueprintPure, Category = "Attack")
	int32 GetBranchDeniedCount() const { return BranchDenied; }

	/** Tests: makes the boss draw its weapon (the pack's EnterCombat ability, forced) so a scripted move can hurt; the frozen boss does not do it by itself. */
	UFUNCTION(BlueprintCallable, Category = "Attack")
	bool EnterCombat();

	/** Counter of attack instances (Freeze 12.2): goes up when a tracked attack begins. */
	UFUNCTION(BlueprintPure, Category = "Attack")
	int32 GetAttackInstance() const { return AttackInstance; }

	UFUNCTION(BlueprintPure, Category = "Attack")
	FName GetCurrentMove() const { return Phase == EPhase::None ? NAME_None : CurrentMove; }

	/** "None", "Windup", "Committed", "Active" or "Recovery". */
	UFUNCTION(BlueprintPure, Category = "Attack")
	FString GetPhaseName() const;

	UFUNCTION(BlueprintPure, Category = "Attack")
	bool IsActiveWindow() const { return Phase == EPhase::Active; }

	UFUNCTION(BlueprintPure, Category = "Attack")
	float GetCommittedYaw() const { return CommittedYaw; }

	/** Counters for tests: commits seen, times the heading was pulled back, montages that stopped before RecoveryEndTime, largest yaw change between commit and the end of the active window (degrees). */
	UFUNCTION(BlueprintPure, Category = "Attack")
	int32 GetCommitCount() const { return CommitCount; }

	UFUNCTION(BlueprintPure, Category = "Attack")
	int32 GetInterruptedCount() const { return InterruptedCount; }

	UFUNCTION(BlueprintPure, Category = "Attack")
	float GetMaxYawDriftAfterCommit() const { return MaxYawDrift; }

	/** Boss montage position (seconds) of the last commit and of the first active moment, for tests. */
	UFUNCTION(BlueprintPure, Category = "Attack")
	float GetLastCommitPosition() const { return LastCommitPosition; }

	UFUNCTION(BlueprintPure, Category = "Attack")
	float GetLastActiveStartPosition() const { return LastActiveStartPosition; }

protected:
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	enum class EPhase : uint8 { None, Windup, Committed, Active, Recovery };

	void End(const TCHAR* Reason, float Position);
	bool BranchAllowedNow() const;
	bool PlayClip(const FRPGAttackTiming& Timing);
	int32 FindTimingIndex(const UAnimMontage* Montage) const;

	EPhase Phase = EPhase::None;
	FName CurrentMove;
	int32 TimingIndex = INDEX_NONE;
	int32 AttackInstance = 0;
	int32 CommitCount = 0;
	int32 InterruptedCount = 0;
	int32 IllegalStarts = 0;
	int32 DoubleLaunches = 0;
	int32 BranchAllowed = 0;
	int32 BranchDenied = 0;
	float CommittedYaw = 0.f;
	float MaxYawDrift = 0.f;
	float LastCommitPosition = -1.f;
	float LastActiveStartPosition = -1.f;
	float LastPosition = 0.f;
	float DeathCheckTimer = 0.f;
	bool bDead = false;
	TWeakObjectPtr<const UAnimMontage> DeniedMontage;
};
