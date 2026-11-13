// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "InputAction.h"
#include "Player/RPGParryRules.h"
#include "Player/RPGParryGradeRules.h"
#include "Player/RPGPackParryRules.h"
#include "RPGPlayerParry.generated.h"

/**
 * The player's parry window (owner decision 2026-11-02). The pack's IA_Parry press opens a short window (RPGParryRules::Press); URPGDamageResolver asks IsWindowOpen at the moment a boss contact would hurt the player and answers
 * Parried (no damage, the hit is spent). Nothing is written to a pack asset by this component; the pack's own GA_PlayerParry (granted through the combat styles) only cancels the block. Attached by RPGPlayerMovesSubsystem.
 */
UCLASS(ClassGroup = (Boss))
class ONEBOSSFIGHT_API URPGPlayerParry : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGPlayerParry();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Parry", meta = (ClampMin = "0.05"))
	float WindowSeconds = static_cast<float>(RPGParry::DefaultWindowSeconds);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Parry", meta = (ClampMin = "0.05"))
	float CooldownSeconds = static_cast<float>(RPGParry::DefaultCooldownSeconds);

	/** Optional pack stamina paid to open a parry window; zero preserves the default cost-free behavior. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Parry", meta = (ClampMin = "0.0"))
	float StaminaCost = 0.f;

	/** Optional additional Niagara parry visual. Empty preserves the current visual path; Development preview is controlled by rpg.Art.Tier1. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Parry|Visuals")
	TSoftObjectPtr<class UNiagaraSystem> ParrySparkVFX;

	UFUNCTION(BlueprintPure, Category = "Parry|Visuals")
	int32 GetTier1VisualSpawnCount() const { return Tier1VisualSpawnCount; }

	/** Opens the window like a press of the parry input (the input binding calls this); returns whether a window was opened. */
	UFUNCTION(BlueprintCallable, Category = "Parry")
	bool Press();

	UFUNCTION(BlueprintCallable, Category = "Parry")
	bool IsWindowOpen() const;

	/** Read-only counter accessors for runtime diagnostics and capture receipts. */
	UFUNCTION(BlueprintPure, Category = "Parry|Diagnostics")
	int32 GetPressCount() const { return PressCount; }

	UFUNCTION(BlueprintPure, Category = "Parry|Diagnostics")
	int32 GetParriedCount() const { return ParriedCount; }

	/** Timing grade of a contact at the current game time, or None outside the valid window. */
	RPGParryGrade::EGrade GradeNow() const;
	FString LastGradeName() const;

	/** True when Actor has this component and its window is open now. */
	static bool IsParrying(const AActor* Actor);
	/** Called by the damage resolver when a contact is actually parried. */
	static void NotifyParried(AActor* Actor);
	/** Shared once-per-attack reward entry for pack contacts and project resolver contacts. */
	static bool NotifyParried(AActor* Actor, AActor* Boss, const FString& AttackKey, uint64 Generation, RPGParryGrade::EGrade Grade);

	int32 PressCount = 0, ParriedCount = 0;
	int32 Tier1VisualSpawnCount = 0;

	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	bool TryBind();
	/** The pack's own impact decision (SM_ImpactDecision) reads Status.ParryActive, which the pack's ParryFramesNS sets with AddOwnedGameplayTag: the window sets and clears the same tag so the pack's melee hits are parried by the pack's own logic too. */
	void SetParryTag(bool bOn, const TCHAR* Reason);
	void FinishStaminaCost();
	void OnParryPressed();
	double Now() const;

	TSoftObjectPtr<UInputAction> ParryAction;
	RPGParry::FState State;
	bool bBound = false;
	bool bTagOn = false;
	/** Generation that opened the currently owned parry tag. */
	uint64 OwnedTagGeneration = 0;
	bool bCostPending = false, bPendingParried = false, bRollbackPending = false;
	int32 RefundRetries = 0; // audit X-450: a failed refund write is retried a few times, then given up with a log line
	RPGParryGrade::EGrade LastGrade = RPGParryGrade::EGrade::None;
	RPGPackParry::FRewardDeduplicator RewardDeduplicator;
	double StaminaBeforeCost = 0., PaidStaminaCost = 0.;
};
