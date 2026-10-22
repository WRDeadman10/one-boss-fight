// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "RPGBossPosture.generated.h"

/**
 * Boss posture (Master Design Freeze 17, Layer A): a hidden 100 point pool that player hits drain and that refills on its own. Since Gate 3 (M9) the pool is OURS: a float in this component, drained by the value of the
 * weapon attack table row of each hit (Player/RPGWeaponAttackTable, delivered by Player/RPGHitIntake), not by the pack's poise attribute. The Freeze asks to keep posture and poise apart (17.1): the pack's poise
 * (Attribute.Poise, 100) stays what the pack made it, the boss's armour against flinching, and this component PINS it full (writes the maximum back every tick, a hit's own subtraction of 20 or 50 included) so the pack's hit
 * stun never starts by itself; the pack's gate edit in GA_BaseHitReaction stays as it is (no pack asset is edited). A pool that reaches zero asks URPGBossStagger for the stance break (RequestBreak).
 * This component owns:
 *   - the drain (ApplyPostureDamage): clamped at zero, one break request when it reaches zero, nothing while a hold is running (counted);
 *   - regeneration: starts RegenDelaySeconds after the last drain and then adds RegenPerSecond (RPGBossMath::RegenStep);
 *   - the hold policy of the stance break and the phase transition;
 *   - bookkeeping for tests and the debug overlay: posture, drain events, time since the last drain.
 * Boss attacks never drain it (it is only drained by hits on the boss).
 */
UCLASS(ClassGroup = (Boss))
class ONEBOSSFIGHT_API URPGBossPosture : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGBossPosture();

	/** The size of the pool (Freeze 17.2: 100 points). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Posture", meta = (ClampMin = "1.0"))
	float PostureMax = 100.f;

	/** Seconds after the last drain before posture starts to come back (Freeze 17.2: 6.0). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Posture", meta = (ClampMin = "0.0"))
	float RegenDelaySeconds = 6.f;

	/** Points per second once it regenerates (Freeze 17.2: 13). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Posture", meta = (ClampMin = "0.0"))
	float RegenPerSecond = 13.f;

	/** Keep the pack's poise attribute full so the pack's own hit stun never starts (the posture pool is this component's, see the class comment). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Posture")
	bool bPinPackPoise = true;

	UFUNCTION(BlueprintPure, Category = "Posture")
	float GetPosture() const { return Posture; }

	UFUNCTION(BlueprintPure, Category = "Posture")
	float GetMaxPosture() const { return PostureMax; }

	/** Number of drains seen (a hit that lowered posture) and the world time of the last one. */
	UFUNCTION(BlueprintPure, Category = "Posture")
	int32 GetDrainCount() const { return DrainCount; }

	UFUNCTION(BlueprintPure, Category = "Posture")
	double GetLastDrainTime() const { return LastDrainTime; }

	/** True when the pack's own regeneration of the poise attribute was switched off (it is pinned full anyway). */
	UFUNCTION(BlueprintPure, Category = "Posture")
	bool IsConfigured() const { return bConfigured; }

	/** What happened to a posture damage request. */
	enum class EDrainResult : uint8 { Applied, Held, Ignored };

	/**
	 * Takes Amount points from the pool (the weapon attack table's value of one hit). Ignored: no amount, a dead or dormant boss. Held: a hold is running (stance break or phase transition), the hit is counted and does nothing.
	 * Applied: the pool is lowered (clamped at zero), the regeneration timer restarts, and a pool at zero asks the stance break gate (URPGBossStagger::RequestBreak) once.
	 */
	EDrainResult ApplyPostureDamage(float Amount, const TCHAR* Source);

	/** Test drivers only: puts the pool at a value, counted as a drain when it lowers it (a hit would have done so). Does not ask for a break. */
	UFUNCTION(BlueprintCallable, Category = "Posture")
	void SetPostureForTest(float Value);

	/** Encounter reset (Freeze 18.3): a full pool, no hold, regeneration idle. Safe to call twice. */
	UFUNCTION(BlueprintCallable, Category = "Posture")
	void ResetPool();

	/** The end of a stance break (Freeze 714): a full pool, whether a hold was running (it ends) or not (a stance break with bHoldPostureAtZero off leaves the pool at zero). Regeneration waits RegenDelaySeconds after this call. */
	void RefillAfterBreak();

	/** True when the pack's poise attribute is pinned full (so the pack's own hit stun is not a break source: the pool is). */
	bool IsPackPoisePinned() const { return bPinPackPoise && bConfigured; }

	/** The pack's hit stun started although the pack's poise was pinned (two heavy hits inside one 0.05 s pin interval took the pack's 100 to 0): it is not a break (the pool decides), the caller ended the flinch.
	 *  Counted and logged, and the poise is pinned again at once. */
	void NotePackStunSuppressed();

	UFUNCTION(BlueprintPure, Category = "Posture")
	int32 GetPackStunSuppressedCount() const { return PackStunSuppressed; }

	/** Hold policy (SPEC M4, Freeze 713 and 766): during a stance break the pool is held at 0 (more hits are ignored and counted); during the phase transition it is pinned at the value it had (posture is paused).
	 *  None = normal. */
	enum class EHold : uint8 { None, Zero, Pinned };

	/** Zero puts the pool at 0 now; Pinned keeps the current value. Does nothing when a hold is already running. */
	void BeginHold(EHold Mode);

	/** Ends the hold. bRefill gives the maximum (end of the get-up, Freeze 714). Regeneration waits RegenDelaySeconds after this call. No-op when nothing is held. */
	void EndHold(bool bRefill);

	UFUNCTION(BlueprintPure, Category = "Posture")
	FString GetHoldName() const;

	/** Hits that arrived while a hold was running (ignored posture damage). */
	UFUNCTION(BlueprintPure, Category = "Posture")
	int32 GetSuppressedDrainCount() const { return SuppressedDrains; }

	/** Posture damage requests that reached zero and asked for a stance break, and the result text of the last one ("started", "dropped: ..." in RPGBossRules names). */
	UFUNCTION(BlueprintPure, Category = "Posture")
	int32 GetBreakRequestCount() const { return BreakRequests; }

	UFUNCTION(BlueprintPure, Category = "Posture")
	FString GetLastBreakResult() const { return LastBreakResult; }

	/** The amount and source of the last applied drain. */
	UFUNCTION(BlueprintPure, Category = "Posture")
	float GetLastDrainAmount() const { return LastDrainAmount; }

	UFUNCTION(BlueprintPure, Category = "Posture")
	FString GetLastDrainSource() const { return LastDrainSource; }

protected:
	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	/** Writes the pack's regeneration settings of the poise attribute object (a Blueprint instance) to off, by reflection (the attribute is pinned full anyway). */
	bool ConfigureAttribute();

	/** Writes the maximum back into the pack's poise attribute when a hit lowered it. */
	void PinPackPoise();

	bool IsDeadOrDormant() const;

	EHold Hold = EHold::None;
	float HeldValue = 0.f;
	int32 SuppressedDrains = 0;
	int32 PackStunSuppressed = 0;
	float Posture = -1.f;
	int32 DrainCount = 0;
	int32 BreakRequests = 0;
	float LastDrainAmount = 0.f;
	FString LastDrainSource;
	FString LastBreakResult = TEXT("none");
	double LastDrainTime = -1.0;
	bool bConfigured = false;
};
