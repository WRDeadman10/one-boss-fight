// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "UObject/SoftObjectPtr.h"
#include "Player/RPGBossRules.h"
#include "RPGBossPhases.generated.h"

class UAnimMontage;

/**
 * Phase two for the pack's great-sword boss. At PhaseTwoHealthFraction of its health (once per fight, not while it is dormant or in a stance break):
 *   1. transition: the boss's behaviour is held, the pack's temporary hit stun immunity is applied (so the roar cannot be interrupted) and a power-up clip plays;
 *   2. from then on it moves MovementScale times faster, its attack montages play AttackRateScale times faster (shorter telegraphs), its Attack attribute is multiplied by
 *      DamageScale, and every FireballCooldown seconds, when the player is between FireballMinRange and FireballMaxRange and the boss is not busy, it casts the pack's
 *      magic enemy fireball (granted at runtime, no pack asset is edited).
 * ResetPhases (called by URPGBossEncounter when the encounter resets) puts everything back to phase one. Attached by RPGPlayerMovesSubsystem.
 */
UCLASS(ClassGroup = (Boss))
class ONEBOSSFIGHT_API URPGBossPhases : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGBossPhases();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Phase", meta = (ClampMin = "0.0", ClampMax = "1.0"))
	float PhaseTwoHealthFraction = 0.6f; // Master Design Freeze 30.1 and 36: phase two starts on the first crossing to 60 % of health or below

	/** Seconds the boss is held for the transition (the clip is 1.5 s). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Phase", meta = (ClampMin = "0.2"))
	float TransitionSeconds = 1.8f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Phase")
	TSoftObjectPtr<UAnimMontage> TransitionMontage;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Phase")
	TSoftClassPtr<UObject> ImmunityEffect;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Phase", meta = (ClampMin = "1.0"))
	float MovementScale = 1.2f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Phase", meta = (ClampMin = "1.0"))
	float AttackRateScale = 1.2f;

	/** Multiplier of the Attack attribute (the pack's damage uses it). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Phase", meta = (ClampMin = "1.0"))
	float DamageScale = 1.25f;

	/** The legacy fireball is not part of the approved moveset (Freeze 16 A6, 30.1): off by default. The ability asset stays referenced so nothing is deleted. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Fireball")
	bool bFireballEnabled = false;

	/** The pack magic enemy's fireball ability (a Blueprint class). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Fireball")
	TSoftClassPtr<UObject> FireballAbility;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Fireball")
	FVector2D FireballCooldown = FVector2D(6.f, 10.f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Fireball")
	float FireballMinRange = 500.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Fireball")
	float FireballMaxRange = 1800.f;

	/** Class name prefix of the boss attack abilities whose montage play rates are scaled in phase two. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Phase")
	FString AttackAbilityPrefix = TEXT("GA_GS_Boss_");

	/** A6, the leap, is a phase two move (Freeze 16, 30.1): until the phase transition has finished the leap ability's tag is in the boss's blocked ability tags, so the pack's behaviour cannot pick it. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Phase")
	bool bLockLeapUntilPhaseTwo = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Phase")
	FName LeapAbilityTag = TEXT("Ability.Melee.LeapAttack");

	UFUNCTION(BlueprintPure, Category = "Phase")
	bool IsLeapBlocked() const { return bLeapBlocked; }

	UFUNCTION(BlueprintPure, Category = "Phase")
	bool IsPhaseTwo() const { return bPhaseTwo; }

	UFUNCTION(BlueprintPure, Category = "Phase")
	bool IsInTransition() const { return bTransition; }

	UFUNCTION(BlueprintPure, Category = "Phase")
	int32 GetFireballCount() const { return FireballCount; }

	UFUNCTION(BlueprintPure, Category = "Phase")
	int32 GetPhaseTwoCount() const { return PhaseTwoCount; }

	/** Back to phase one: speeds, attack rates and the Attack attribute restored, the fireball stopped, the roar's immunity effect and posture pin removed. */
	UFUNCTION(BlueprintCallable, Category = "Phase")
	void ResetPhases();

	/** Posture is paused during the roar (Freeze 766): the pool is pinned at its value and hits are ignored, so the pack gate cannot refill it. Off = the pack's gate keeps cycling it. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Phase")
	bool bPausePostureInTransition = true;

	/** Called by the stance break when it ends: starts a transition that crossed its threshold during the break, with the behaviour still held when bBehaviourAlreadyHeld (no gap, no resume in between).
	 *  Returns true when a transition began. Stateless: the queue is derived from health, so a reset or a death clears it by itself. */
	bool TryStartQueuedTransition(bool bBehaviourAlreadyHeld);

	/** True while the threshold is crossed but a stance break keeps the transition waiting (Freeze 770 and 1201). */
	UFUNCTION(BlueprintPure, Category = "Phase")
	bool IsTransitionQueued() const;

	/** World time the last transition began (-1 none) and how many began from the end of a stance break. */
	UFUNCTION(BlueprintPure, Category = "Phase")
	double GetLastTransitionStartTime() const { return LastTransitionStart; }

	UFUNCTION(BlueprintPure, Category = "Phase")
	int32 GetQueuedStartCount() const { return QueuedStarts; }

protected:
	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	/** The Freeze 21 rule applied to the boss's state right now (health, dormancy, stagger, phase flags). */
	RPGBossRules::ETransitionResult ResolveNow() const;
	/** bHeldAlready: the stance break that just ended still holds the behaviour; the transition takes that hold over instead of stopping the behaviour a second time. */
	void StartTransition(bool bHeldAlready);
	void FinishTransition();
	/** Removes the hit stun immunity the roar applied (the effect would otherwise outlive the roar by about 2 s and a reset), and releases the posture pin. */
	void RemoveImmunity();
	void ApplyPhaseTwoBuffs();
	void RemovePhaseTwoBuffs();
	/** Multiplies the PlayRate of every montage entry of the boss's attack abilities by Factor. */
	void ScaleAttackRates(float Factor);
	void TryFireball(double Now);
	/** Adds or removes LeapAbilityTag in the ability system component's blocked ability tags. Returns false while the component is not there yet. */
	bool SetLeapBlocked(bool bBlocked);
	void HoldBehaviour();
	void ResumeBehaviour();

	bool bPhaseTwo = false;
	bool bTransition = false;
	bool bHeld = false;
	bool bBuffsApplied = false;
	bool bFireballGiven = false;
	bool bLeapBlocked = false;
	bool bImmunityApplied = false;
	double LastTransitionStart = -1.0;
	int32 QueuedStarts = 0;
	double TransitionEnd = 0.0;
	double NextFireball = 0.0;
	double AppliedAttack = 0.0;
	float BaseWalkSpeed = 0.f;
	float LastSetSpeed = 0.f;
	int32 FireballCount = 0;
	int32 PhaseTwoCount = 0;
};
