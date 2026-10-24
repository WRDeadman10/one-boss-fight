// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Player/RPGAttackKind.h"
#include "Player/RPGWeaponAttackTable.h"
#include "RPGSwingTracker.generated.h"

/** One swing of the player: an attack montage of the pack's weapon ability, from its start. */
struct FRPGSwing
{
	/** Counts swings of this session, from 1. */
	int32 Id = 0;
	double StartTime = 0.0;
	FName Montage;
	/** The pack's combat style asset name (SwordCombatStyle, ...). */
	FName Weapon;
	/** The kind of the attack from the ability's montage arrays (Light, Strong, Charged, JumpLight, JumpHeavy), Unknown when the montage is in none of them (dodge, jump, drink, ...). */
	ERPGAttackKind Kind = ERPGAttackKind::Unknown;
	/** The stance when the montage started. */
	bool bAirborneAtStart = false;
	/** The table row of (Weapon, Kind). */
	FRPGWeaponAttackRow Row;
	bool bRowFound = false;
	/** The hyperarmor window of the swing in montage seconds (the row's, or a test override): both negative when the swing has none. */
	float HyperArmorStart = -1.f;
	float HyperArmorEnd = -1.f;
	/** Stamina taken (positive) or given back (negative) on top of the pack's own cost so that the swing costs what the row says; 0 when the row leaves the pack's cost. */
	float StaminaExtra = 0.f;

	bool IsAttack() const { return Kind != ERPGAttackKind::Unknown; }
	FString ToString() const;
};

/**
 * Swing tracker (Gate 3, M10 and M11). Watches the player's montages every frame; when an attack montage of one of the pack's weapon abilities starts it knows the swing: the combat style (the weapon), the kind
 * (found by looking the montage up in the ability's AttackMontages, StrongAttackMontages, ChargedAttackMontages and FallingAttackMontages arrays: the pack's attack data is only known at the first hit), the stance, and the
 * weapon attack table row. Then it makes the swing cost what the row says: the pack's own cost (15 stamina per swing, GE_MeleeAttackCost, shared by every weapon) has just been paid, so the difference is taken or
 * given back by setting the stamina attribute (no pack asset is edited; the pack's own Modify Attribute needs enum arguments that a call from C++ does not get right). Hyperarmor (M11, Freeze 20.1): inside the row's window of a swing the player carries the pack's hit stun immunity effect
 * (the same GE_HitStunImmune the boss uses; the player's GA_PlayerHitStun lists Status.HitStunImmune in its blocked tags), so a hit does not interrupt the swing; the damage effect is separate, health is still lost.
 * Attached to the pack player by RPGPlayerMovesSubsystem.
 */
UCLASS(ClassGroup = (Player))
class ONEBOSSFIGHT_API URPGSwingTracker : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGSwingTracker();

	/** What the pack takes for every melee swing (GE_MeleeAttackCost, read in the audit: Attribute.Stamina -15). A row's cost is reached by taking the difference. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Swing", meta = (ClampMin = "0.0"))
	float PackStaminaCost = 15.f;

	/** Off: the table's stamina column is ignored and the pack's cost stands (the starting point, and a switch for tests). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Swing")
	bool bApplyStaminaCosts = true;

	const FRPGSwing& GetCurrentSwing() const { return Current; }
	const FRPGSwing& GetLastAttackSwing() const { return LastAttack; }

	UFUNCTION(BlueprintPure, Category = "Swing")
	int32 GetSwingCount() const { return SwingCount; }

	UFUNCTION(BlueprintPure, Category = "Swing")
	int32 GetAttackSwingCount() const { return AttackSwingCount; }

	/** Total stamina taken or given back on top of the pack's cost (positive: taken). */
	UFUNCTION(BlueprintPure, Category = "Swing")
	float GetStaminaExtraTotal() const { return StaminaExtraTotal; }

	UFUNCTION(BlueprintPure, Category = "Swing")
	FString GetLastSwingText() const { return LastAttack.ToString(); }

	/** The swings of this session as text lines (last 64), for tests. */
	UFUNCTION(BlueprintCallable, Category = "Swing")
	TArray<FString> GetSwingLines() const { return Lines; }

	/** Test drivers only: forgets the counters and the lines. */
	UFUNCTION(BlueprintCallable, Category = "Swing")
	void ResetCounters();

	/** Test drivers only: makes every swing of this kind cost Cost stamina in total (instead of the table's value) until ClearCostOverrides. */
	UFUNCTION(BlueprintCallable, Category = "Swing")
	void SetCostOverrideForTest(ERPGAttackKind Kind, float Cost);

	/** Test drivers only: forgets every override and puts the original weapon attack table back (SetRowHyperArmorForTest works on a copy). */
	UFUNCTION(BlueprintCallable, Category = "Swing")
	void ClearCostOverrides();

	/** True while the player carries the hyperarmor effect. */
	UFUNCTION(BlueprintPure, Category = "Swing")
	bool IsHyperArmorActive() const { return bHyperArmor; }

	/** Windows that opened this session. */
	UFUNCTION(BlueprintPure, Category = "Swing")
	int32 GetHyperArmorWindowCount() const { return HyperArmorWindows; }

	/** Test drivers only: swings of this kind get the hyperarmor window [Start, End] in montage seconds (until ClearCostOverrides). */
	UFUNCTION(BlueprintCallable, Category = "Swing")
	void SetHyperArmorOverrideForTest(ERPGAttackKind Kind, float Start, float End);

	/** Test drivers only: puts the hyperarmor window [Start, End] into the table row of (Weapon, Kind) of a transient COPY of the weapon attack table (the asset is never touched), so the row to swing path runs as it does with an authored
	 *  row. The row is added when the table has none for the weapon. Undone by ClearCostOverrides. */
	UFUNCTION(BlueprintCallable, Category = "Swing")
	void SetRowHyperArmorForTest(FName Weapon, ERPGAttackKind Kind, float Start, float End);

	/** True when the player's GA_PlayerHitStun lists Status.HitStunImmune in its ActivationBlockedTags: the tag that the hyperarmor window puts on the player then stops the pack's hit stun ability from starting (read from the live ability instance;
	 *  the ability only starts through the hit pipeline's event with source tags, so a test cannot start it by hand). */
	UFUNCTION(BlueprintPure, Category = "Swing")
	bool IsPlayerHitStunBlockedByImmunity() const;

	/** The pack's immunity effect lasts 4 s: a window that stays open longer gets the effect applied again after this many seconds (0 or less: never). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Swing")
	float HyperArmorRefreshSeconds = 3.f;

	/** Test drivers only (Python must not change a component property in PIE: it re-runs the owner's construction scripts and breaks the pack's components). */
	UFUNCTION(BlueprintCallable, Category = "Swing")
	void SetHyperArmorRefreshForTest(float Seconds)
	{
#if !UE_BUILD_SHIPPING
		HyperArmorRefreshSeconds = Seconds;
#endif
	}

	/** Times the effect was applied again inside one window. */
	UFUNCTION(BlueprintPure, Category = "Swing")
	int32 GetHyperArmorRefreshCount() const { return HyperArmorRefreshes; }

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	/** A new attack montage started: classify, number, apply the row. */
	void OnMontageStarted(const class UAnimMontage* Montage, bool bAirborne);
	/** The kind of attack of this montage from the player's weapon abilities; Unknown when no ability lists it. */
	ERPGAttackKind ClassifyMontage(const FString& MontageName, bool bAirborne) const;
	/** Takes Delta stamina (negative: gives back) by setting the current value (clamped to 0 and the maximum); the pack's own Modify Attribute needs enum arguments that a zeroed call does not get right. */
	bool AddStamina(double Delta);
	/** Opens or closes the hyperarmor window by the montage position of the current swing. */
	void UpdateHyperArmor(const class UAnimMontage* Montage, float Position);
	void SetHyperArmor(bool bOn);
	/** Applies or removes the pack's immunity effect on the player. False when the ability system or the effect class is missing. */
	bool ApplyImmunity();
	void RemoveImmunity();

	/** The table the swings read: the asset (or the built-in defaults), or the test copy. */
	UPROPERTY(Transient)
	TObjectPtr<URPGWeaponAttackTable> Table;

	UPROPERTY(Transient)
	TObjectPtr<URPGWeaponAttackTable> OriginalTable;

	UPROPERTY(Transient)
	TObjectPtr<URPGWeaponAttackTable> TestTable;

	FRPGSwing Current;
	FRPGSwing LastAttack;
	FName TrackedMontage;
	float LastMontagePosition = 0.f;
	int32 SwingCount = 0;
	int32 AttackSwingCount = 0;
	float StaminaExtraTotal = 0.f;
	TMap<ERPGAttackKind, float> CostOverrides;
	TMap<ERPGAttackKind, FVector2D> HyperArmorOverrides;
	bool bHyperArmor = false;
	double HyperArmorAppliedAt = 0.0;
	/** The swing (Id) for which applying the pack's effect failed: not tried again every frame of its window. */
	int32 ApplyFailedSwing = -1;
	int32 HyperArmorRefreshes = 0;
	int32 HyperArmorWindows = 0;
	TSet<FString> WarnedRows;
	TArray<FString> Lines;
};
