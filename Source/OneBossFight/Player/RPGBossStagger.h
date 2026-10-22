// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "UObject/SoftObjectPtr.h"
#include "Player/RPGBossRules.h"
#include "RPGBossStagger.generated.h"

class UAnimMontage;
class UAnimSequence;

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

	/** The synchronized execution (Freeze 17.4, G2-7): an accepted press plays Antigravity's paired clips, the player's strike (AN_Riposte_Player_Front, 1.6 s, the player advances 90 cm) and the boss's reaction
	 *  (AN_Riposte_Boss_Reaction, 2.0 s), both with their impact at 0.8 s. The player's input is locked for the execution, the pack's own attack that the same press started is cut, the player slides to RipostePlayerStartGap from the boss
	 *  in the first RiposteAlignSeconds (the clip then closes the last 90 cm by its own root motion), and the critical damage is applied ONCE at the impact: RiposteBaseDamage x CriticalMultiplier (no weapon trace, no armed multiplier).
	 *  Off, or when a clip does not load: the stand-in (the pack's attack plays, the next hit within RiposteArmSeconds is critical). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Riposte")
	bool bUseRiposteClips = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Riposte")
	TSoftObjectPtr<UAnimSequence> RipostePlayerClip;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Riposte")
	TSoftObjectPtr<UAnimSequence> RiposteBossClip;

	/** Distance in cm from the boss at which the player's clip starts (the clip's root travels 90 cm, so the strike ends 60 cm from the boss; the top-down sheet of the clip pair). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Riposte", meta = (ClampMin = "50.0"))
	float RipostePlayerStartGap = 150.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Riposte", meta = (ClampMin = "0.05"))
	float RiposteAlignSeconds = 0.3f;

	/** Seconds from the start of the clips to the impact frame (frame 24 of both clips). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Riposte", meta = (ClampMin = "0.1"))
	float RiposteImpactSeconds = 0.8f;

	/** The base hit of the riposte; CriticalMultiplier is applied to it once (40 x 2.5 = 100 of the boss's 500). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Riposte", meta = (ClampMin = "0.0"))
	float RiposteBaseDamage = 40.f;

	UFUNCTION(BlueprintCallable, Category = "Riposte")
	void SetUseRiposteClipsForTest(bool bOn) { bUseRiposteClips = bOn; }

	/** True from the accepted press until the clips are over (or the execution was aborted). */
	UFUNCTION(BlueprintPure, Category = "Riposte")
	bool IsRiposteExecuting() const { return bRiposteRunning; }

	/** Impacts applied (one per execution, never two) and executions that were aborted before their end. */
	UFUNCTION(BlueprintPure, Category = "Riposte")
	int32 GetRiposteImpactCount() const { return RiposteImpacts; }

	UFUNCTION(BlueprintPure, Category = "Riposte")
	int32 GetRiposteAbortCount() const { return RiposteAborts; }

	/** True when a press right now would be accepted (boss down, riposte unused, player in range, in the boss's cone and facing it). The HUD prompt uses it; it changes nothing. */
	UFUNCTION(BlueprintPure, Category = "Riposte")
	bool IsRiposteAvailable(const AActor* Player) const;

	/** The bleed proc has just taken Loss health that is not a player hit: lower the baseline by exactly that, so the critical multiplier never sees it (Freeze 20.2) while a weapon hit that landed in the same frame still does. */
	void AcknowledgeHealthLoss(double Loss);

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

	/** Test drivers only. Python must not change a component property in PIE (set_editor_property re-runs the owning Blueprint's construction scripts, the pack's components are rebuilt and its gameplay effects point at the old ones):
	 *  these functions change the same values without that side effect. */
	UFUNCTION(BlueprintCallable, Category = "Stagger")
	void SetCooldownForTest(float Seconds) { CooldownSeconds = FMath::Max(0.f, Seconds); }

	UFUNCTION(BlueprintCallable, Category = "Stagger")
	void SetCriticalOnEveryHitForTest(bool bOn) { bCriticalOnEveryHit = bOn; }

	UFUNCTION(BlueprintCallable, Category = "Stagger")
	void SetStaggerSecondsForTest(float Seconds) { StaggerSeconds = FMath::Max(0.5f, Seconds); }

	UFUNCTION(BlueprintCallable, Category = "Stagger")
	void SetUseClipsForTest(bool bOn) { bUseClips = bOn; }

	/** Class name of the boss's hit stun ability (a Blueprint instance in its ability system component). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stagger")
	FName HitStunAbilityClassName = TEXT("GA_GS_Boss_HitStun_C");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stagger")
	TSoftObjectPtr<UAnimMontage> FallMontage;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stagger")
	TSoftObjectPtr<UAnimMontage> GetUpMontage;

	/** The project's own stance break clips (Antigravity, on the mannequin skeleton): the fall to the knees (StaggerFall, 0.7 s), the kneel (StaggerDown, a 1 s loop that plays for the rest of the stance break) and the get-up (the fall played
	 *  backwards at GetUpRate, so it ends exactly in the standing pose it started from). When both clips load they replace the pack's knockdown montages above, which stay the fallback. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stagger")
	bool bUseClips = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stagger")
	TSoftObjectPtr<UAnimSequence> FallClip;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stagger")
	TSoftObjectPtr<UAnimSequence> DownClip;

	/** Play rate of the backwards fall that gets the boss up (0.6: 1.2 s). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stagger", meta = (ClampMin = "0.1"))
	float GetUpRate = 0.6f;

	/** True while the running stance break plays the project's clips; the stage is "none", "fall", "down" or "getup". */
	UFUNCTION(BlueprintPure, Category = "Stagger")
	bool IsUsingClips() const { return bClipMode; }

	UFUNCTION(BlueprintPure, Category = "Stagger")
	FString GetClipStageName() const;

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
	/** Accepted press with the clips available: the execution is requested now and starts next frame (after the pack's own handling of the same press). */
	bool BeginRiposteExecution(const AActor* PlayerActor);
	void StartRiposteClips();
	void TickRiposte(double Now);
	void ApplyRiposteImpact();
	/** After the execution the player may stand inside the boss's capsule (the clip ends 60 cm from the boss's centre): the collision between them is switched back on and the player is slid out to the contact distance in 0.25 s. */
	void TickRiposteExit(double Now);
	/** Ends the execution. bCompleted: the clips ran to their end (the kneel loop resumes); otherwise it was aborted (death, reset, the stance break ended): the clips are stopped. */
	void EndRiposteExecution(bool bCompleted, const TCHAR* Why, bool bResumeKneel = false);
	/** Starts the stance break's clips (the fall) when they load; false means the pack's knockdown montages play instead. */
	bool StartClipFall();
	/** The fall hands over to the kneel loop when it ends, the kneel hands over to the get-up when the stance break time is up. */
	void TickClipDown(UAnimInstance* Anim, double Elapsed, double Now);
	/** Stops the stance break's montages (the pack's and the clips'). */
	void StopStaggerMontages(float BlendOut);
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

	enum class EClipStage : uint8 { None, Fall, Down, GetUp, Riposte };

	bool bRiposteIgnoring = false;
	bool bRiposteExiting = false;
	float RiposteAlignDone = 0.f;
	double RiposteExitStart = 0.0;
	FVector RiposteExitFrom = FVector::ZeroVector;
	FVector RiposteExitTo = FVector::ZeroVector;
	bool bRiposteRunning = false;
	bool bRiposteStarted = false;
	bool bRiposteImpactDone = false;
	double RiposteStartTime = 0.0;
	double RiposteEndTime = 0.0;
	FVector RiposteAlignFrom = FVector::ZeroVector;
	FVector RiposteAlignTo = FVector::ZeroVector;
	int32 RiposteImpacts = 0;
	int32 RiposteAborts = 0;
	TWeakObjectPtr<ACharacter> RipostePlayer;
	TWeakObjectPtr<UAnimMontage> RipostePlayerMontage;

	UPROPERTY(Transient)
	TObjectPtr<UAnimSequence> LoadedRipostePlayer;

	UPROPERTY(Transient)
	TObjectPtr<UAnimSequence> LoadedRiposteBoss;
	bool bClipMode = false;
	EClipStage ClipStage = EClipStage::None;
	TWeakObjectPtr<UAnimMontage> ClipMontage;

	UPROPERTY(Transient)
	TObjectPtr<UAnimSequence> LoadedFall;

	UPROPERTY(Transient)
	TObjectPtr<UAnimSequence> LoadedDown;

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
