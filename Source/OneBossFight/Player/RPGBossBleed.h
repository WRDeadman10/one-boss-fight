// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Player/RPGBleedRules.h"
#include "RPGBossBleed.generated.h"

class UNiagaraSystem;
class USoundBase;

/**
 * Bleed (hemorrhage) status of the boss (Gate 3, M12; Freeze 20.2). Player hits add the buildup of their weapon attack table row (URPGHitIntake calls AddBuildup); at the threshold the status procs once: the buildup resets,
 * the next threshold rises, and the boss loses a fraction of its maximum health in one burst with a blood effect and an impact sound. The rules are in RPGBleedRules.h. A proc never kills (it leaves one point of health),
 * never happens on a dead or sleeping boss or during the phase transition, and is not multiplied by the riposte critical (the stagger component is told that the health loss is not a hit). Reset with the encounter.
 * Attached to the boss by RPGPlayerMovesSubsystem.
 */
UCLASS(ClassGroup = (Boss))
class ONEBOSSFIGHT_API URPGBossBleed : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGBossBleed();

	/** Buildup at which the first proc happens (Freeze 36 Boss.BleedInitialThreshold: 100). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Bleed", meta = (ClampMin = "1.0"))
	float InitialThreshold = 100.f;

	/** Added to the threshold after every proc (Boss.BleedThresholdIncrease: 20). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Bleed", meta = (ClampMin = "0.0"))
	float ThresholdIncrease = 20.f;

	/** The threshold never rises above this (Boss.BleedThresholdMax: 200). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Bleed", meta = (ClampMin = "1.0"))
	float ThresholdMax = 200.f;

	/** Fraction of the maximum health a proc takes (Boss.BleedBossHpFraction: 0.105). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Bleed", meta = (ClampMin = "0.0", ClampMax = "1.0"))
	float HpFraction = 0.105f;

	/** The blood burst at the proc (the project's blood pack, a placeholder until the effect of the art list, V-12). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Bleed")
	TSoftObjectPtr<UNiagaraSystem> ProcEffect;

	/** Where the burst appears, above the boss's origin (cm). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Bleed")
	float EffectHeight = 170.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Bleed")
	TSoftObjectPtr<USoundBase> ProcSound;

	/** The loaded effect and sound (loaded once in BeginPlay: a proc must not stall the frame on a package load). */
	UPROPERTY(Transient)
	TObjectPtr<UNiagaraSystem> LoadedEffect;

	UPROPERTY(Transient)
	TObjectPtr<USoundBase> LoadedSound;

	/** Adds the buildup of one hit. Returns what happened (RPGBleedRules::Name). Ignored when Amount is zero or negative. */
	RPGBleedRules::EResult AddBuildup(float Amount, const TCHAR* Source);

	/** Test drivers only: the same as a hit of this buildup (no weapon needed). Returns the result text. */
	UFUNCTION(BlueprintCallable, Category = "Bleed")
	FString AddBuildupForTest(float Amount);

	/** Encounter reset (Freeze 18.3): no buildup, the first threshold, the proc counter kept for tests. Safe to call twice. */
	UFUNCTION(BlueprintCallable, Category = "Bleed")
	void ResetBleed();

	UFUNCTION(BlueprintPure, Category = "Bleed")
	float GetBuildup() const { return State.Buildup; }

	UFUNCTION(BlueprintPure, Category = "Bleed")
	float GetThreshold() const { return State.Threshold; }

	UFUNCTION(BlueprintPure, Category = "Bleed")
	int32 GetProcCount() const { return State.Procs; }

	/** Buildups that were not added (dead, sleeping, in the phase transition, same frame as a proc). */
	UFUNCTION(BlueprintPure, Category = "Bleed")
	int32 GetIgnoredCount() const { return Ignored; }

	UFUNCTION(BlueprintPure, Category = "Bleed")
	float GetLastProcDamage() const { return LastProcDamage; }

	UFUNCTION(BlueprintPure, Category = "Bleed")
	FString GetLastResult() const { return LastResult; }

protected:
	virtual void BeginPlay() override;

private:
	RPGBleedRules::FConfig MakeConfig() const;
	void DoProc();

	RPGBleedRules::FState State;
	uint64 ProcFrame = MAX_uint64;
	int32 Ignored = 0;
	float LastProcDamage = 0.f;
	FString LastResult = TEXT("none");
};
