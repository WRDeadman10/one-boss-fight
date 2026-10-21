// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "UObject/SoftObjectPtr.h"
#include "Player/RPGBossRules.h"
#include "RPGBossStagger.generated.h"

class UAnimMontage;

/**
 * Stance break for the pack's boss (Elden Ring style): a poise break leaves the boss down for a few seconds, and hits taken while it is down are critical.
 *
 * The pack's poise gate (GA_BaseHitReaction, see DECISIONS) absorbs hits while poise lasts and, on a break, activates the boss's hit stun ability, a 0.8 s flinch after
 * which the boss attacks again at once. This component watches that ability. When it becomes active (a break):
 *   1. the flinch ability is ended, the pack's hit stun immunity effect (GE_HitStunImmune, 4 s) is applied so later hits do not replay a flinch over the pose, the boss's
 *      behaviour is held and its movement stopped;
 *   2. the pack's knockdown clip plays and is frozen near its end, so the boss falls and stays down until StaggerSeconds have passed;
 *   3. while it is down every point of health lost is multiplied by CriticalMultiplier (the extra is taken off the health attribute);
 *   4. the get-up clip plays, then the behaviour resumes, the immunity is removed, poise is refilled and a cooldown starts before the next stance break.
 * No pack asset is edited. RPGPlayerMovesSubsystem attaches it to the pack boss when that pawn spawns.
 */
UCLASS(ClassGroup = (Boss))
class ONEBOSSFIGHT_API URPGBossStagger : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGBossStagger();

	/** Seconds from the break until the get-up starts: the critical window is this long (the fall itself is 1.9 s). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stagger", meta = (ClampMin = "0.5"))
	float StaggerSeconds = 2.5f;

	/** Montage position (seconds) where the fall is frozen so the boss stays on the ground; the clip starts blending out at 1.67 s. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stagger", meta = (ClampMin = "0.1"))
	float FreezeAtPosition = 1.55f;

	/** The critical multiplier of the riposte hit (Freeze 17.4: applied once to the validated riposte only). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stagger", meta = (ClampMin = "1.0"))
	float CriticalMultiplier = 2.5f;

	/** Frontal riposte (Freeze 17.4): the player must stand within RiposteRange cm (centre to centre, horizontal) in front of the boss (a cone of RiposteConeDegrees in total) and press Light Attack
	 *  while the boss is down. The first hit that follows within RiposteArmSeconds is multiplied by CriticalMultiplier, once per stance break; every other hit is normal damage. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Riposte", meta = (ClampMin = "10.0"))
	float RiposteRange = 150.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Riposte", meta = (ClampMin = "10.0", ClampMax = "360.0"))
	float RiposteConeDegrees = 120.f;

	/** The player must also face the boss within this many degrees (total cone). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Riposte", meta = (ClampMin = "10.0", ClampMax = "360.0"))
	float RiposteFacingDegrees = 120.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Riposte", meta = (ClampMin = "0.1"))
	float RiposteArmSeconds = 1.2f;

	/** Called when the player presses Light Attack. Accepts or rejects the riposte (distance, cone, facing, state, once per break) and arms it. Returns true when accepted. */
	UFUNCTION(BlueprintCallable, Category = "Riposte")
	bool TryRiposte(const AActor* Player);

	/** True when a press right now would be accepted (boss down, riposte unused, player in range, in the boss's cone and facing it). The HUD prompt uses it; it changes nothing. */
	UFUNCTION(BlueprintPure, Category = "Riposte")
	bool IsRiposteAvailable(const AActor* Player) const;

	UFUNCTION(BlueprintPure, Category = "Riposte")
	bool IsRiposteArmed() const;

	UFUNCTION(BlueprintPure, Category = "Riposte")
	int32 GetRiposteCount() const { return RiposteCount; }

	UFUNCTION(BlueprintPure, Category = "Riposte")
	int32 GetRiposteRejectCount() const { return RiposteRejectCount; }

	/** Why the last press was rejected ("" when accepted or no press yet). */
	UFUNCTION(BlueprintPure, Category = "Riposte")
	FString GetLastRiposteResult() const { return LastRiposteResult; }

	/** Legacy rule: every hit while the boss is down is critical. The Freeze forbids it, so it is off; the riposte (G2-7) applies CriticalMultiplier instead. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stagger")
	bool bCriticalOnEveryHit = false;

	/** Seconds after a stance break ends in which a new poise break is ignored. 0 by default (Freeze 17.2: a hidden cooldown makes hits look like they do nothing): the posture pool refills to full at the end of
	 *  the get-up, so another break still takes three or more heavy hits. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stagger", meta = (ClampMin = "0.0"))
	float CooldownSeconds = 0.f;

	/** Class name of the boss's hit stun ability (a Blueprint instance in its ability system component). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stagger")
	FName HitStunAbilityClassName = TEXT("GA_GS_Boss_HitStun_C");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stagger")
	TSoftObjectPtr<UAnimMontage> FallMontage;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stagger")
	TSoftObjectPtr<UAnimMontage> GetUpMontage;

	/** The pack's temporary hit stun immunity effect (4 s, enough for the fall, the hold and the get-up). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stagger")
	TSoftClassPtr<UObject> ImmunityEffect;

	UFUNCTION(BlueprintPure, Category = "Stagger")
	bool IsStaggered() const { return Phase != EPhase::Idle; }

	/** True while hits are critical. */
	UFUNCTION(BlueprintPure, Category = "Stagger")
	bool IsCriticalWindowOpen() const { return Phase == EPhase::Down; }

	/** The one gate for a stance break (Freeze 21 priority, SPEC M4): dead, dormant, a phase transition (not interrupted by a normal break, Freeze 729), a break already running (exactly one) and the cooldown
	 *  each drop the request, counted and logged, never silently. The pack's hit stun edge and the test hooks both go through here. */
	RPGBossRules::EBreakResult RequestBreak(bool bIgnoreCooldown);

	/** Ends a stance break in progress without handing the boss back to its behaviour (an encounter reset does that itself): stops the clips, removes the immunity, refills poise, clears the cooldown. Safe at any time. */
	UFUNCTION(BlueprintCallable, Category = "Stagger")
	void AbortStagger();

	/** Tests: asks for a stance break now, ignoring the cooldown, through the real gate. Returns the result: "started", "dead", "dormant", "transition", "staggered" or "cooldown". */
	UFUNCTION(BlueprintCallable, Category = "Stagger")
	FString ForceBreakForTest();

	/** Tests: the same request but obeying the cooldown. */
	UFUNCTION(BlueprintCallable, Category = "Stagger")
	FString TryBreakForTest();

	/** Breaks the gate dropped, by reason ("transition", "dead", "dormant", "staggered", "cooldown"). */
	UFUNCTION(BlueprintPure, Category = "Stagger")
	int32 GetDroppedBreakCount(const FString& Reason) const;

	UFUNCTION(BlueprintPure, Category = "Stagger")
	FString GetLastBreakResult() const { return LastBreakResult; }

	/** World time the last stance break ended (-1 when none yet) and the seconds left of the cooldown. */
	UFUNCTION(BlueprintPure, Category = "Stagger")
	double GetLastEndTime() const { return LastEndTime; }

	UFUNCTION(BlueprintPure, Category = "Stagger")
	float GetCooldownRemaining() const;

	/** During a stance break the posture pool is held at 0 and further hits are ignored (Freeze 713); it refills at the end of the get-up (714). Off = the pack's pool cycles as before. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stagger")
	bool bHoldPostureAtZero = true;

	UFUNCTION(BlueprintPure, Category = "Stagger")
	int32 GetStaggerCount() const { return StaggerCount; }

	UFUNCTION(BlueprintPure, Category = "Stagger")
	int32 GetCriticalHitCount() const { return CriticalHitCount; }

protected:
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
	enum class EPhase : uint8 { Idle, Down, GetUp };

	void StartStagger();
	/** Ends the break. bClearCooldown (reset, abort) starts no cooldown. With bResumeBehaviour a phase transition that queued behind the break starts right here, with the behaviour still held (no gap, Freeze 770). */
	void EndStagger(bool bResumeBehaviour, bool bClearCooldown = false);
	/** Ends the pack's 0.8 s flinch ability so it cannot play over a roar or a death clip. Returns true when it was active. */
	bool EndPackFlinch();
	void HoldBehaviour();
	void ResumeBehaviour();
	/** Takes the extra critical damage off the health attribute when health dropped since the last tick. */
	void ApplyCritical();
	/** Null when a riposte would be accepted, otherwise the reason it would be rejected; OutDistance is the horizontal distance to the player. */
	const TCHAR* CheckRiposte(const AActor* Player, double& OutDistance) const;

	UAnimInstance* GetAnimInstance() const;

	EPhase Phase = EPhase::Idle;
	double PhaseStart = 0.0;
	double CooldownEnd = 0.0;
	bool bWasActive = false;
	bool bFrozen = false;
	bool bBehaviourHeld = false;
	double LastHealth = -1.0;
	double RiposteArmedUntil = -1.0;
	bool bRiposteUsed = false;
	int32 RiposteCount = 0;
	int32 RiposteRejectCount = 0;
	FString LastRiposteResult;
	int32 StaggerCount = 0;
	int32 CriticalHitCount = 0;
	double LastEndTime = -1.0;
	FString LastBreakResult;
	int32 DroppedTransition = 0;
	int32 DroppedDead = 0;
	int32 DroppedDormant = 0;
	int32 DroppedStaggered = 0;
	int32 DroppedCooldown = 0;
	TWeakObjectPtr<UObject> CachedHitStun;
};
