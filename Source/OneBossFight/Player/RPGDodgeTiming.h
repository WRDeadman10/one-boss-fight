// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Engine/EngineTypes.h"
#include "UObject/SoftObjectPtr.h"
#include "RPGDodgeTiming.generated.h"

class UAnimMontage;
class UInputAction;
struct FInputActionInstance;

/**
 * Quick dodge and full roll on the dodge key for the pack's player.
 *
 * The pack already separates a tap from a hold: the dodge starts when the key is released and holding for half a second sprints instead (the sprint consumes the
 * buffered dodge). What it lacks is a second dodge, and it drops a dodge request that arrives while a dodge is still in its opening frames, so a fast double tap
 * (measured: presses 0.14 s apart) never produced a second dodge. This component keeps the pack's input path and ability (stamina cost, direction, state, buffering)
 * and adds, on every press of the dodge action:
 *   - a press more than DoubleTapWindow after the previous press: the quick dodge. The pack dodges when the key is released; this only picks the clip (short and
 *     fast) in the dodge ability instance's montage map, which the ability reads when it activates.
 *   - a press within DoubleTapWindow of the previous press: the full roll. If the quick dodge is running it is ended and the dodge ability is activated again at
 *     once with the full clip, from where the quick dodge has got to (so the roll continues the movement instead of restarting it), and the pack's own dodge on
 *     this key's release is consumed so there is exactly one roll per double tap. If no dodge is running (a slow double tap) only the clip is chosen and the pack
 *     dodges on release as for a tap.
 *   - a press while a full roll is running is ignored (no repeated rolls from key repeat or mashing).
 * RPGPlayerMovesSubsystem attaches it to the pack player when that pawn spawns.
 */
UCLASS(ClassGroup = (Player), meta = (BlueprintSpawnableComponent))
class ONEBOSSFIGHT_API URPGDodgeTiming : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGDodgeTiming();

	/** A second press within this many seconds of the previous press gives the full roll. */
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

	/** Dodges that turned backward (tests). */
	UFUNCTION(BlueprintPure, Category = "Dodge")
	int32 GetBackwardTurnCount() const { return BackwardTurnCount; }

	/** True when the last press chose the full roll (tests and debugging). */
	UFUNCTION(BlueprintPure, Category = "Dodge")
	bool WasLastPressFull() const { return bLastPressFull; }

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
	enum class EKind : uint8 { None, Quick, Full };

	/** Binds the dodge action on the pawn's input component once it exists (it is created when the pawn is possessed). */
	bool TryBind();
	void OnDodgePressed(const FInputActionInstance& Instance);
	/** The dodge ability instance the ASC created for this pawn, or null. */
	UObject* FindDodgeAbility() const;
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
	int32 ForcedRollCount = 0;
	int32 IgnoredPressCount = 0;
	double LastPressGap = -1.0;
	int32 BackwardTurnCount = 0;
	bool bWasActive = false;
	bool bTurning = false;
	float TurnTargetYaw = 0.f;
	TWeakObjectPtr<UObject> CachedAbility;
	/** The clip the ability will play or is playing. */
	EKind Selected = EKind::None;
};
