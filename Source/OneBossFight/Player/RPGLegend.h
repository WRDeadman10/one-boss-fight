// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Containers/Ticker.h"
#include "Subsystems/WorldSubsystem.h"
#include "Player/RPGCameraShakes.h"
#include "RPGLegend.generated.h"

class URPGAttackTracker;
class URPGBossEncounter;
class URPGBossHud;
class URPGBossPhases;
class URPGBossStagger;

/**
 * The bookkeeping of one time dilation effect, with no engine objects so that it can be tested alone. Rules: a second request while the effect runs never captures the already dilated value
 * as the one to restore (Saved stays what the first request saw), applied values are absolute and never multiplied (0.05, 0.25), and the deadline only ever moves later.
 */
struct ONEBOSSFIGHT_API FRPGDilationScope
{
	bool bActive = false;
	float Saved = 1.f;
	float Applied = 1.f;
	double DeadlineReal = 0.0;

	/** Starts the effect (captures Saved) or extends it (keeps Saved, moves the deadline to the later of the two). Returns true when this call started it. */
	bool Begin(float Value, double Now, double Seconds, float Current)
	{
		if (!bActive)
		{
			bActive = true;
			Saved = Current;
			Applied = Value;
			DeadlineReal = Now + Seconds;
			return true;
		}
		DeadlineReal = FMath::Max(DeadlineReal, Now + Seconds);
		return false;
	}

	bool Expired(double Now) const { return bActive && Now >= DeadlineReal; }

	/** Ends the effect and returns the value to restore. */
	float End()
	{
		bActive = false;
		return Saved;
	}
};

/**
 * The only owner of time dilation in the project (nothing else may call SetGlobalTimeDilation or write CustomTimeDilation). Hit stop slows two actors, slow motion slows the world; both end on REAL time,
 * so dilation cannot stretch them, and both are cancelled when the console variable rpg.Legend goes to 0, the encounter resets or the world is torn down: time is always restored.
 * Game worlds only (the same rule as URPGPlayerMovesSubsystem).
 */
UCLASS()
class ONEBOSSFIGHT_API URPGLegendSubsystem : public UWorldSubsystem
{
	GENERATED_BODY()

public:
	virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
	virtual void Deinitialize() override;

	static URPGLegendSubsystem* Get(const UObject* WorldContext);

	/** rpg.Legend: 1 (default) all effects on, 0 = no hit stop, slow motion, camera shake or music swap (counted as suppressed). */
	static bool IsLegendOn();
	/** rpg.LegendShakeScale: global multiplier of every shake (accessibility), 0 to 1. */
	static float GetShakeScaleCVar();

	/** Slows both actors to Dilation for RealSeconds. False (and counted) when the layer is off, the encounter is dormant or the generation is stale. */
	bool RequestHitStop(AActor* First, AActor* Second, float RealSeconds, float Dilation, const URPGBossEncounter* Encounter, int32 Generation);
	/** Slows the world to Scale for RealSeconds. Same refusals. */
	bool RequestSlowMotion(float Scale, float RealSeconds, const URPGBossEncounter* Encounter, int32 Generation);
	/** Ends every effect now, restores time, stops the shakes. Logs one line only when something was active. */
	void CancelAll(const TCHAR* Reason);

	UFUNCTION(BlueprintPure, Category = "Legend")
	bool IsHitStopActive() const { return HitStop.bActive; }

	UFUNCTION(BlueprintPure, Category = "Legend")
	bool IsSlowMotionActive() const { return SlowMotion.bActive; }

	UFUNCTION(BlueprintPure, Category = "Legend")
	int32 GetCancelCount() const { return CancelCount; }

	UFUNCTION(BlueprintPure, Category = "Legend")
	int32 GetRestoreCount() const { return RestoreCount; }

	UFUNCTION(BlueprintPure, Category = "Legend")
	int32 GetSuppressedCount() const { return SuppressedCount; }

	UFUNCTION(BlueprintPure, Category = "Legend")
	int32 GetRefusedCount() const { return RefusedCount; }

private:
	struct FStoppedActor
	{
		TWeakObjectPtr<AActor> Actor;
		float Saved = 1.f;
	};

	bool TickEffects(float DeltaSeconds);
	void EnsureTicker();
	void RestoreHitStop(const TCHAR* Reason);
	void RestoreSlowMotion(const TCHAR* Reason);
	bool CheckRequest(const URPGBossEncounter* Encounter, int32 Generation);

	FRPGDilationScope HitStop;
	FRPGDilationScope SlowMotion;
	TArray<FStoppedActor> Stopped;
	TWeakObjectPtr<const URPGBossEncounter> RequestOwner;
	int32 RequestGeneration = 0;
	FTSTicker::FDelegateHandle TickerHandle;
	int32 CancelCount = 0;
	int32 RestoreCount = 0;
	int32 SuppressedCount = 0;
	int32 RefusedCount = 0;
};

/**
 * The presentation layer of the boss fight (Freeze 247, 289; SPEC_M3): camera shake on the heavy slams (A2, A6) and on the phase two roar, hit stop on the riposte hit, slow motion on the kill.
 * No gameplay change: every effect is a cosmetic reaction to an event that already exists, polled once per frame with an idempotency key (nothing fires twice for one event) and ranked below
 * dead, reset and phase transition (Freeze 21, item 8). The music swap is the music component's own poll. Attached to the pack boss by URPGPlayerMovesSubsystem after the HUD and the debug components.
 */
UCLASS(ClassGroup = (Boss), meta = (BlueprintSpawnableComponent))
class ONEBOSSFIGHT_API URPGBossLegend : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGBossLegend();

	/** Switch of this boss; ANDed with the console variable rpg.Legend. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Legend")
	bool bEnabled = true;

	/** The thump of the A2 overhead and the A6 landing. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Legend|Shake")
	FRPGShakeSettings Slam;

	/** The rumble of the phase two roar. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Legend|Shake")
	FRPGShakeSettings Roar;

	/** Multiplier of both shakes (also multiplied by rpg.LegendShakeScale). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Legend|Shake", meta = (ClampMin = "0", ClampMax = "1"))
	float GlobalShakeScale = 1.f;

	/** A shake whose distance scale is below this does not start (counted as too far). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Legend|Shake", meta = (ClampMin = "0"))
	float MinShakeScale = 0.02f;

	/** Real seconds the boss and the player are slowed when the riposte lands (the Freeze task asks 0.06 to 0.10). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Legend|Time", meta = (ClampMin = "0"))
	float HitStopSeconds = 0.08f;

	/** The dilation of those two actors during the hit stop: nearly frozen, not zero (zero would stop animation notifies in the middle of an overlap). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Legend|Time", meta = (ClampMin = "0.01", ClampMax = "1"))
	float HitStopDilation = 0.05f;

	/** The world speed during the kill slow motion. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Legend|Time", meta = (ClampMin = "0.05", ClampMax = "1"))
	float SlowMotionScale = 0.25f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Legend|Time", meta = (ClampMin = "0"))
	float SlowMotionSeconds = 1.2f;

	/** No hit stop on a lethal riposte: the kill slow motion owns that moment, and a death ragdoll must never run while the animation is frozen. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Legend|Time")
	bool bSkipHitStopOnLethal = true;

	// Counters (once per event; the drivers read them).
	UFUNCTION(BlueprintPure, Category = "Legend") int32 GetSlamShakeCount() const { return SlamShakeCount; }
	UFUNCTION(BlueprintPure, Category = "Legend") int32 GetRoarShakeCount() const { return RoarShakeCount; }
	UFUNCTION(BlueprintPure, Category = "Legend") int32 GetHitStopCount() const { return HitStopCount; }
	UFUNCTION(BlueprintPure, Category = "Legend") int32 GetSlowMotionCount() const { return SlowMotionCount; }
	UFUNCTION(BlueprintPure, Category = "Legend") int32 GetShakeTooFarCount() const { return ShakeTooFarCount; }
	UFUNCTION(BlueprintPure, Category = "Legend") int32 GetShakeNotStartedCount() const { return ShakeNotStartedCount; }
	UFUNCTION(BlueprintPure, Category = "Legend") int32 GetSuppressedCount() const { return SuppressedCount; }
	UFUNCTION(BlueprintPure, Category = "Legend") float GetLastShakeScale() const { return LastShakeScale; }
	UFUNCTION(BlueprintPure, Category = "Legend") float GetLastShakeDistance() const { return LastShakeDistance; }

	/** The time subsystem's counters, forwarded so a driver needs one object. */
	UFUNCTION(BlueprintPure, Category = "Legend") bool IsHitStopActive() const;
	UFUNCTION(BlueprintPure, Category = "Legend") bool IsSlowMotionActive() const;
	UFUNCTION(BlueprintPure, Category = "Legend") int32 GetCancelCount() const;
	UFUNCTION(BlueprintPure, Category = "Legend") int32 GetRestoreCount() const;
	UFUNCTION(BlueprintPure, Category = "Legend") int32 GetTimeSuppressedCount() const;

	// Tests: the same handlers as the polls, without the idempotency key (so a test can fire twice in a row to prove that nothing stacks). They obey rpg.Legend and the generation rules.
	UFUNCTION(BlueprintCallable, Category = "Legend") bool FireSlamForTest(FName Move);
	UFUNCTION(BlueprintCallable, Category = "Legend") bool FireRoarForTest();
	UFUNCTION(BlueprintCallable, Category = "Legend") bool FireHitStopForTest(bool bLethal);
	UFUNCTION(BlueprintCallable, Category = "Legend") bool FireSlowMotionForTest();

protected:
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	bool EffectsAllowed(bool bAllowDead);
	bool PlayShake(TSubclassOf<UCameraShakeBase> ShakeClass, const FRPGShakeSettings& Settings, const FVector& Epicentre, int32& Counter);
	bool HandleSlam(FName Move);
	bool HandleRoar();
	bool HandleHitStop(bool bLethal);
	bool HandleSlowMotion();
	bool FindParts();

	UPROPERTY(Transient)
	TObjectPtr<URPGBossEncounter> Encounter;
	UPROPERTY(Transient)
	TObjectPtr<URPGAttackTracker> Tracker;
	UPROPERTY(Transient)
	TObjectPtr<URPGBossPhases> Phases;
	UPROPERTY(Transient)
	TObjectPtr<URPGBossStagger> Stagger;
	UPROPERTY(Transient)
	TObjectPtr<URPGBossHud> Hud;

	// Idempotency keys: what the last effect was made for.
	int32 LastSlamInstance = -1;
	int32 LastRoarCount = 0;
	int32 LastRiposteCount = 0;
	int32 LastVictoryCount = 0;
	int32 LastGeneration = 0;
	bool bRoarPrimed = false;
	bool bRiposteKeyPrimed = false;
	bool bVictoryPrimed = false;

	int32 SlamShakeCount = 0;
	int32 RoarShakeCount = 0;
	int32 HitStopCount = 0;
	int32 SlowMotionCount = 0;
	int32 ShakeTooFarCount = 0;
	int32 ShakeNotStartedCount = 0;
	int32 SuppressedCount = 0;
	float LastShakeScale = 0.f;
	float LastShakeDistance = 0.f;
};
