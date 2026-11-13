// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Engine/EngineTypes.h"
#include "Player/RPGAttackKind.h"
#include "UObject/SoftObjectPtr.h"
#include "RPGDodgeTiming.generated.h"

class UAnimMontage;
class UInputAction;
class UMaterialInterface;
struct FInputActionInstance;

struct FRPGGuardCounterArrayBackup
{
	TWeakObjectPtr<UObject> Ability;
	FName PropertyName = NAME_None;
	FString ExportedArray;
};

/**
 * Optional dodge clip selection for the pack's player. The pack still owns input,
 * stamina, direction, state, and buffering. A single tap selects the quick roll;
 * when an approved BackstepMontage is assigned, a standing tap selects that
 * clip instead. The full-roll-on-double-tap behavior is opt-in and disabled by
 * default (bDoubleTapLongRoll=false); the default second press selects quick
 * again and is subject to the pack ability's own active/buffer rules.
 * RPGPlayerMovesSubsystem attaches it to the pack player when that pawn spawns.
 */
class UInputMappingContext;

UCLASS(ClassGroup = (Player), meta = (BlueprintSpawnableComponent))
class ONEBOSSFIGHT_API URPGDodgeTiming : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGDodgeTiming();
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

	/** Owner decision 2026-11-06 (Elden Ring dodge: tap = roll or backstep, hold = dash): the double-tap long roll is OFF by default. True restores the old
	 *  behavior (a second press within DoubleTapWindow gives the full roll). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dodge")
	bool bDoubleTapLongRoll = false;

	/** A second press within this many seconds of the previous press gives the full roll (only with bDoubleTapLongRoll). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dodge", meta = (ClampMin = "0.05"))
	float DoubleTapWindow = 0.30f;

	/** The pack's dodge key action. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dodge")
	TSoftObjectPtr<UInputAction> DodgeAction;

	/** Clip of a single tap: short and fast (the pack's roll clip, 0.43 s and 3 m at rate 1). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dodge")
	TSoftObjectPtr<UAnimMontage> QuickMontage;

	/** Clip of a double tap: the pack's long dodge (0.92 s and 5 m). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dodge")
	TSoftObjectPtr<UAnimMontage> FullMontage;

	/** Play rates written with the clips. The quick clip has a slow wind-up, a higher rate makes the start snappier (distance does not change with rate). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dodge", meta = (ClampMin = "0.1"))
	float QuickPlayRate = 1.3f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dodge", meta = (ClampMin = "0.1"))
	float FullPlayRate = 1.0f;

	/** Class name of the pack's player dodge ability (a Blueprint) and the name of its montage map variable. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dodge")
	FName DodgeAbilityClassName = TEXT("GA_Player_Dodge_C");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dodge")
	FName MontageMapName = TEXT("DodgeMontage");

	/** The pack's input tag of the dodge key (consumed so the key's release does not dodge again after a forced roll). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dodge")
	FName DodgeInputTag = TEXT("InputTag.Dodge");

	/** With no direction input at the moment a dodge starts, turn away from the camera and dodge that way (backward) instead of along the current facing (forward, the
	 *  pack's default, which when locked on is into the target). The pack has no backstep clip, so this is a turn and a roll away, not a hop that keeps facing. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dodge|Backward")
	bool bBackwardWithoutInput = true;

	/** Degrees per second the pawn turns towards the backward direction while the dodge's root motion runs (1800 turns 180 degrees in 0.1 s; slower values curve the path
	 *  because the clip is already moving). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dodge|Backward", meta = (ClampMin = "90"))
	float BackwardTurnRate = 1800.f;

	/** The movement input counts as "no direction" below this size (0 to 1). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dodge|Backward", meta = (ClampMin = "0.0", ClampMax = "1.0"))
	float NoInputThreshold = 0.1f;

	/** Optional (Elden Ring style, owner request 2026-11-06): the backstep clip. When set, a press with no direction input plays this clip (a hop straight back that keeps
	 *  facing: no turn, no roll). Empty (the default) keeps today's behavior (turn away and roll). The clip is authored by Antigravity (ER-A1) and has no rotation notify. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dodge|Backstep")
	TSoftObjectPtr<UAnimMontage> BackstepMontage;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dodge|Backstep", meta = (ClampMin = "0.1"))
	float BackstepPlayRate = 1.0f;

	/** Optional guard-counter montage, empty by default. A successful blocked contact arms one R2 tap; absent/invalid montage keeps the pack strong attack unchanged. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat|Guard Counter")
	TSoftObjectPtr<UAnimMontage> GuardCounterMontage;

	/** Optional airborne light clip. Empty by default, preserving the pack's existing FallingAttackMontages route. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat|Air Attacks")
	TSoftObjectPtr<UAnimMontage> AirLightMontage;

	/** Optional airborne heavy clip. Empty by default, preserving the pack's existing StrongAttackMontages route. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat|Air Attacks")
	TSoftObjectPtr<UAnimMontage> AirHeavyMontage;

	/** PROPOSAL only: maximum game-time interval from a successful blocked contact to the R2 counter tap. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat|Guard Counter", meta = (ClampMin = "0.05", ClampMax = "2.0"))
	float GuardCounterWindowSeconds = 0.60f;

	/** Arms the counter window after a guarded contact is confirmed by the boss resolver or player-side pack reaction observer. */
	void NotifySuccessfulGuardContact();
	/** Development probe: true while the most recent confirmed guard remains inside the R2 counter window. */
	#if WITH_EDITORONLY_DATA
	UFUNCTION(BlueprintCallable, Category = "Development|Guard Counter", meta = (DevelopmentOnly))
	#endif
	bool IsGuardCounterArmed() const;
	/** Development probe: synthetically arms the same counter window for isolated R2-path validation. */
	#if WITH_EDITORONLY_DATA
	UFUNCTION(BlueprintCallable, Category = "Development|Guard Counter", meta = (DevelopmentOnly))
	#endif
	void DebugArmGuardCounter();
	/** Development probe: returns the pack-created ability classes/states and the tag container used by the gameplay-tag interface. */
	#if WITH_EDITORONLY_DATA
	UFUNCTION(BlueprintCallable, Category = "Development|Guard Counter", meta = (DevelopmentOnly))
	#endif
	FString DescribeGuardState() const;
	/** The montage currently carrying a temporary attack-array override (kept through playback after arrays are restored). */
	UAnimMontage* GetActiveMontageOverride() const { return ActiveOverrideMontage.Get(); }
	/** The semantic attack kind for Montage, or Unknown when it is not the active temporary override. */
	ERPGAttackKind GetActiveMontageOverrideKind(const UAnimMontage* Montage) const;

	/** Owner 2026-11-06 ("All three"): Elden Ring attack inputs on the gamepad (R1 press light, R2 tap strong, R2 hold charged), a project context added ABOVE the
	 *  pack's IMC_AdvancedControls so it consumes those keys. Empty disables it (the pack's mapping returns: R1 release light, R1 hold charged, R2 strong). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Input|EldenRing")
	TSoftObjectPtr<UInputMappingContext> EldenRingMappingContext;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Input|EldenRing")
	int32 EldenRingMappingPriority = 10;

	/** The project actions the Elden Ring context maps (R1 press, R2 tap) and the pack actions they replay by injection for InjectSeconds (pie3: the pack
	 *  starts the strong attack on key DOWN and ignores a Pressed-trigger light, so the keys drive our own actions and the pack's actions are replayed). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Input|EldenRing")
	TSoftObjectPtr<UInputAction> EldenRingLightAction;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Input|EldenRing")
	TSoftObjectPtr<UInputAction> EldenRingHeavyTapAction;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Input|EldenRing")
	TSoftObjectPtr<UInputAction> PackLightAction;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Input|EldenRing")
	TSoftObjectPtr<UInputAction> PackStrongAction;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Input|EldenRing", meta = (ClampMin = "0.02"))
	float InjectSeconds = 0.12f;

	/** Light / strong replays started by the Elden Ring keys (tests). */
	UFUNCTION(BlueprintPure, Category = "Input|EldenRing")
	int32 GetEldenRingLightCount() const { return EldenRingLightCount; }

	UFUNCTION(BlueprintPure, Category = "Input|EldenRing")
	int32 GetEldenRingStrongCount() const { return EldenRingStrongCount; }

	/** True once the Elden Ring context was added for this pawn's local player (tests). */
	UFUNCTION(BlueprintPure, Category = "Input|EldenRing")
	bool IsEldenRingInputActive() const { return bEldenRingContextAdded; }

	/** Presses that chose the backstep clip (tests). */
	UFUNCTION(BlueprintPure, Category = "Dodge")
	int32 GetBackstepCount() const { return BackstepCount; }

	/** Dodges that turned backward (tests). */
	UFUNCTION(BlueprintPure, Category = "Dodge")
	int32 GetBackwardTurnCount() const { return BackwardTurnCount; }

	/** True when the last press chose the full roll (tests and debugging). */
	UFUNCTION(BlueprintPure, Category = "Dodge")
	bool WasLastPressFull() const { return bLastPressFull; }

	/** BQ-14 / KI-059 pure seams (moved verbatim from HasNoDirectionInput / OnDodgePressed; behaviour unchanged). */
	static bool IsNoDirectionInput(float InputSize, float Threshold) { return InputSize < Threshold; }
	static bool IsDoubleTapLongRoll(bool bEnabled, double PressGapSeconds, float WindowSeconds) { return bEnabled && PressGapSeconds <= WindowSeconds; }

	/** Number of presses seen, and how many of them forced a roll over a running quick dodge (tests). */
	UFUNCTION(BlueprintPure, Category = "Dodge")
	int32 GetPressCount() const { return PressCount; }

	UFUNCTION(BlueprintPure, Category = "Dodge")
	int32 GetForcedRollCount() const { return ForcedRollCount; }

	/** Seconds between the last press and the one before it (the value the window rule used), presses ignored because a full roll was running, and the stage for the debug overlay. */
	UFUNCTION(BlueprintPure, Category = "Dodge")
	double GetLastPressGap() const { return LastPressGap; }

	UFUNCTION(BlueprintPure, Category = "Dodge")
	int32 GetIgnoredPressCount() const { return IgnoredPressCount; }

	/** "None", "QuickEvade" or "FullRoll" (Freeze 22). */
	UFUNCTION(BlueprintPure, Category = "Dodge")
	FString GetStageName() const;

protected:
	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	enum class EKind : uint8 { None, Quick, Full, Backstep };

	/** True when the movement input is below NoInputThreshold (the pawn is standing still as far as the player is concerned). */
	bool HasNoDirectionInput() const;
	/** Adds EldenRingMappingContext to the local player's Enhanced Input subsystem once the pawn is possessed (retried every tick until it succeeds). */
	void TryAddEldenRingContext();
	/** Binds the two Elden Ring actions once, and replays the pack's light / strong action while a replay is running. */
	void TickEldenRingInput();
	void OnEldenRingLight(const FInputActionInstance& Instance);
	void OnEldenRingHeavyTap(const FInputActionInstance& Instance);
	bool ApplyGuardCounterMontageOverride(UAnimMontage* Montage);
	bool ApplyMontageArrayOverride(UAnimMontage* Montage, FName ArrayName, ERPGAttackKind Kind);
	void RestoreMontageArrayBackups();
	void RestoreGuardCounterMontageOverride();
	void TickGuardCounterMontageOverride(double Now);

	/** Binds the dodge action on the pawn's input component once it exists (it is created when the pawn is possessed). */
	bool TryBind();
	void OnDodgePressed(const FInputActionInstance& Instance);
	/** The dodge ability instance the ASC created for this pawn, or null. */
	UObject* FindDodgeAbility() const;
	/** One non-forced fallback through the pack ASC if the first allowed input press did not activate. */
	bool TryActivateDodgeAbilityByClass(UObject* Ability, bool& bMethodCalled, bool& bReturnRead);
	/** Prevent a buffered copy of the already-retried press from replaying after activation. */
	bool ConsumeBufferedDodgeInput() const;
	bool IsAbilityActive(UObject* Ability) const;
	/** Writes the clip, play rate and nothing else into every entry of the dodge ability instance's montage map. */
	bool ApplyClip(UObject* Ability, UAnimMontage* Montage, float PlayRate) const;
	/** Ends the running dodge and activates the ability again with the full clip. */
	bool ForceFullRoll(UObject* Ability);
	/** A dodge just became active: when there is no direction input, start turning away from the camera. */
	void OnDodgeStarted();
	void StepBackwardTurn(float DeltaTime);

	double LastPressTime = -1.0e9;
	bool bBound = false;
	bool bLastPressFull = false;
	int32 PressCount = 0;
	/** First-press Development trace deferred one component tick to observe pack activation after IA_Dodge dispatch. */
	int32 PendingDodgeActivationDiagnosticPress = 0;
	int32 PendingDodgeActivationRetryPress = 0;
	bool bPendingDodgeActivationCanActivate = false;
	bool bFirstDodgeActivationRetryAttempted = false;
	double PendingDodgeActivationRetryAfterTime = -1.0;
	int32 ForcedRollCount = 0;
	int32 IgnoredPressCount = 0;
	double LastSuccessfulGuardTime = -1.0e9;
	double LastGuardTagProbeTime = -1.0e9;
	double LastGuardMonitorLogTime = -1.0e9;
	TArray<TWeakObjectPtr<UObject>> CachedBlockReactionAbilities;
	/** Keep the default first-use backstep resident so its first dodge press never blocks on soft loading. */
	UPROPERTY(Transient)
	TObjectPtr<UAnimMontage> LoadedBackstepMontage = nullptr;
	double LastBlockReactionAbilitySearchTime = -1.0e9;
	bool bWasBlockReactionActive = false;
	bool bLastObservedBlocking = false;
	double GuardCounterOverrideEndTime = -1.0;
	TWeakObjectPtr<UAnimMontage> ActiveOverrideMontage;
	ERPGAttackKind ActiveOverrideKind = ERPGAttackKind::Unknown;
	bool bActiveOverrideStarted = false;
	TArray<FRPGGuardCounterArrayBackup> GuardCounterArrayBackups;
	double LastPressGap = -1.0;
	int32 BackwardTurnCount = 0;
	int32 BackstepCount = 0;
	bool bEldenRingContextAdded = false;
	bool bEldenRingActionsBound = false;
	double InjectLightUntil = -1.0;
	double InjectStrongUntil = -1.0;
	int32 EldenRingLightCount = 0;
	int32 EldenRingStrongCount = 0;
	bool bWasActive = false;
	bool bTurning = false;
	float TurnTargetYaw = 0.f;
	TWeakObjectPtr<UObject> CachedAbility;
	UPROPERTY(Transient)
	TObjectPtr<UMaterialInterface> LoadedDodgeDustFlipbook;
	/** The clip the ability will play or is playing. */
	EKind Selected = EKind::None;
};
