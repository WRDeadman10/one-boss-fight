// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Combat/RPGCombatTypes.h"
#include "Combat/RPGWeaponData.h"
#include "RPGCombatComponent.generated.h"

class UAnimMontage;
class URPGAttributeComponent;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FRPGCombatStateChangedSignature, ERPGCombatState, OldState, ERPGCombatState, NewState);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FRPGHitReceivedSignature, const FRPGHitInfo&, Hit, const FRPGHitResult&, Result);
DECLARE_MULTICAST_DELEGATE_OneParam(FRPGHitWindowChanged, bool /*bOpen*/);

/**
 * Logical combat state machine plus the single damage path for one combatant.
 *
 * Animation drives timing: anim notify states call SetHitWindow / SetComboWindow / SetInvulnerable /
 * SetCancelWindow, and the montage ending returns the character to Locomotion. Without a montage the
 * same windows run from fallback times, so every rule here is testable by calling TickCombat().
 *
 * Allowed transitions (anything else is refused, and a refused input is buffered briefly):
 *   Locomotion/Blocking -> Attacking, Dodging, Blocking
 *   Attacking/Recovery  -> ComboWindow (notify), Dodging only inside a cancel window or recovery
 *   ComboWindow         -> Attacking (next attack), Dodging
 *   any non-Dead        -> Staggered (poise break), Dead
 *   Staggered/Dodging/Attacking/Recovery -> Locomotion (action ends)
 */
UCLASS(ClassGroup = (Combat), meta = (BlueprintSpawnableComponent))
class ONEBOSSFIGHT_API URPGCombatComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGCombatComponent();

	// ---- Configuration -------------------------------------------------------------------

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat")
	TObjectPtr<URPGWeaponData> Weapon;

	/** Combatants on the same team never damage each other. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat")
	int32 TeamId = 0;

	/** Seconds an early input is remembered. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat|Input", meta = (ClampMin = "0"))
	float InputBufferSeconds = 0.4f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat|Dodge", meta = (ClampMin = "0"))
	float DodgeStaminaCost = 25.f;

	/** Units per second applied along the dodge direction. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat|Dodge", meta = (ClampMin = "0"))
	float DodgeSpeed = 900.f;

	/** Fallback (no montage) total duration. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat|Dodge", meta = (ClampMin = "0.05"))
	float DodgeDuration = 0.6f;

	/** Fallback (no montage) invulnerability start and end, seconds from dodge start. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat|Dodge")
	FVector2D DodgeIFrames = FVector2D(0.05, 0.35);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat|Stagger", meta = (ClampMin = "0.05"))
	float StaggerDuration = 0.7f;

	/** Fraction of damage that gets through a block. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat|Block", meta = (ClampMin = "0", ClampMax = "1"))
	float BlockDamageMultiplier = 0.2f;

	/** Stamina lost per point of incoming damage while blocking. Zero stamina breaks the guard. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat|Block", meta = (ClampMin = "0"))
	float BlockStaminaPerDamage = 0.8f;

	// ---- Queries -------------------------------------------------------------------------

	UFUNCTION(BlueprintPure, Category = "Combat")
	ERPGCombatState GetState() const { return State; }

	UFUNCTION(BlueprintPure, Category = "Combat")
	bool IsDead() const { return State == ERPGCombatState::Dead; }

	UFUNCTION(BlueprintPure, Category = "Combat")
	bool IsHitWindowOpen() const { return bHitWindowOpen; }

	UFUNCTION(BlueprintPure, Category = "Combat")
	bool IsInvulnerable() const { return bInvulnerable || bExternalInvulnerable; }

	UFUNCTION(BlueprintPure, Category = "Combat")
	bool IsCancelWindowOpen() const { return bCancelWindowOpen; }

	/** Free movement input is only honored in these states. */
	UFUNCTION(BlueprintPure, Category = "Combat")
	bool CanMove() const { return State == ERPGCombatState::Locomotion || State == ERPGCombatState::Blocking; }

	UFUNCTION(BlueprintPure, Category = "Combat")
	int32 GetComboIndex() const { return ComboIndex; }

	UFUNCTION(BlueprintPure, Category = "Combat")
	ERPGBufferedAction GetBufferedAction() const { return BufferedAction; }

	/** The attack currently being performed (valid while Attacking/ComboWindow/Recovery). */
	const FRPGAttackData& GetCurrentAttack() const { return CurrentAttack; }

	// ---- Requests (input / AI) -----------------------------------------------------------
	// Each returns true if the action started. A refused request is buffered when it could succeed soon.

	UFUNCTION(BlueprintCallable, Category = "Combat")
	bool RequestLightAttack();

	UFUNCTION(BlueprintCallable, Category = "Combat")
	bool RequestHeavyAttack();

	/** Direction is world space; zero means "step back". */
	UFUNCTION(BlueprintCallable, Category = "Combat")
	bool RequestDodge(FVector Direction);

	UFUNCTION(BlueprintCallable, Category = "Combat")
	bool StartBlock();

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void StopBlock();

	// ---- Animation-driven windows (called by anim notify states or the fallback timeline) ----

	/** Opens or closes the damage window. Ignored outside an attack so a stale notify cannot arm a trace. */
	void SetHitWindow(bool bOpen);
	void SetComboWindow(bool bOpen);
	void SetInvulnerable(bool bInvulnerableNow);

	/** Invulnerability owned by a controller (boss entrance, phase transition). Survives state changes. */
	UFUNCTION(BlueprintCallable, Category = "Combat")
	void SetExternalInvulnerable(bool bInvulnerableNow) { bExternalInvulnerable = bInvulnerableNow; }
	void SetCancelWindow(bool bOpen);

	/** The current action is over (montage finished or fallback timeline done). Returns to Locomotion. */
	UFUNCTION(BlueprintCallable, Category = "Combat")
	void EndCurrentAction();

	// ---- Damage path ---------------------------------------------------------------------

	/** The only way a hit changes a combatant. Handles death, i-frames, blocking, damage, poise and stagger. */
	UFUNCTION(BlueprintCallable, Category = "Combat")
	FRPGHitResult ProcessIncomingHit(const FRPGHitInfo& Hit);

	/** Outgoing hit data for the attack being performed; the melee trace stamps location and direction. */
	FRPGHitInfo BuildOutgoingHit() const;

	/**
	 * Starts an attack from data that is not part of a weapon (boss attacks). Costs no stamina. Only allowed
	 * while free to act. Returns true if it started.
	 */
	bool StartCustomAttack(const FRPGAttackData& Attack);

	/**
	 * One-shot area hit around Center for animation-driven shockwaves and slams. Hits each enemy-team combatant
	 * in range once with the current attack's damage. Returns how many were hit.
	 */
	int32 ApplyRadialHit(const FVector& Center, float Radius);

	/** Interrupts the current action and enters Staggered. No effect when dead. */
	UFUNCTION(BlueprintCallable, Category = "Combat")
	void Stagger();

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void Die();

	/** Back to Locomotion with a clean slate. Used for retry and the training dummy. */
	UFUNCTION(BlueprintCallable, Category = "Combat")
	void ResetCombat();

	/** Advances fallback timelines and the input buffer. Called by the component tick; callable directly in tests. */
	void TickCombat(float DeltaTime);

	// ---- Events --------------------------------------------------------------------------

	UPROPERTY(BlueprintAssignable, Category = "Combat")
	FRPGCombatStateChangedSignature OnStateChanged;

	UPROPERTY(BlueprintAssignable, Category = "Combat")
	FRPGHitReceivedSignature OnHitReceived;

	/** The melee trace listens to this to arm and disarm itself. */
	FRPGHitWindowChanged OnHitWindowChanged;

protected:
	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	enum class EFallbackKind : uint8 { None, Attack, Dodge, Stagger };

	/** Finds the sibling attribute component and, on first use, subscribes to its death event. */
	URPGAttributeComponent* GetAttributes();
	void SetState(ERPGCombatState NewState);
	bool StartAttack(ERPGAttackType Type);
	bool StartDodge(const FVector& Direction);
	bool CanDodgeNow() const;
	void Buffer(ERPGBufferedAction Action);
	void TryConsumeBuffer();
	void UpdateTickState();
	void StopActionMontage();

	/** Plays the montage and ends the action when it blends out. Returns false if there is no montage or anim instance. */
	bool PlayActionMontage(UAnimMontage* Montage, float PlayRate);
	void OnMontageBlendingOut(UAnimMontage* Montage, bool bInterrupted, int32 ForActionId);
	UFUNCTION()
	void OnDeathFromAttributes();
	void BeginFallback(EFallbackKind Kind, float Duration);

	ERPGCombatState State = ERPGCombatState::Locomotion;
	bool bHitWindowOpen = false;
	bool bComboWindowOpen = false;
	bool bInvulnerable = false;
	bool bExternalInvulnerable = false;
	bool bCancelWindowOpen = false;

	FRPGAttackData CurrentAttack;
	ERPGAttackType CurrentAttackType = ERPGAttackType::Light;
	int32 ComboIndex = 0;

	ERPGBufferedAction BufferedAction = ERPGBufferedAction::None;
	FVector BufferedDodgeDirection = FVector::ZeroVector;
	float BufferTimeRemaining = 0.f;

	/** Identifies the running action so a late montage callback from an older one is ignored. */
	int32 ActionId = 0;

	/** True while the block input is held, so blocking resumes after another action ends. */
	bool bBlockHeld = false;

	EFallbackKind FallbackKind = EFallbackKind::None;
	float FallbackElapsed = 0.f;
	float FallbackDuration = 0.f;
	bool bBoundToAttributes = false;
};
