// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "UObject/SoftObjectPtr.h"
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

	UFUNCTION(BlueprintPure, Category = "Phase")
	bool IsPhaseTwo() const { return bPhaseTwo; }

	UFUNCTION(BlueprintPure, Category = "Phase")
	bool IsInTransition() const { return bTransition; }

	UFUNCTION(BlueprintPure, Category = "Phase")
	int32 GetFireballCount() const { return FireballCount; }

	UFUNCTION(BlueprintPure, Category = "Phase")
	int32 GetPhaseTwoCount() const { return PhaseTwoCount; }

	/** Back to phase one: speeds, attack rates and the Attack attribute restored, the fireball stopped. */
	UFUNCTION(BlueprintCallable, Category = "Phase")
	void ResetPhases();

protected:
	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	void StartTransition();
	void FinishTransition();
	void ApplyPhaseTwoBuffs();
	void RemovePhaseTwoBuffs();
	/** Multiplies the PlayRate of every montage entry of the boss's attack abilities by Factor. */
	void ScaleAttackRates(float Factor);
	void TryFireball(double Now);
	void HoldBehaviour();
	void ResumeBehaviour();

	bool bPhaseTwo = false;
	bool bTransition = false;
	bool bHeld = false;
	bool bBuffsApplied = false;
	bool bFireballGiven = false;
	double TransitionEnd = 0.0;
	double NextFireball = 0.0;
	double AppliedAttack = 0.0;
	float BaseWalkSpeed = 0.f;
	float LastSetSpeed = 0.f;
	int32 FireballCount = 0;
	int32 PhaseTwoCount = 0;
};
