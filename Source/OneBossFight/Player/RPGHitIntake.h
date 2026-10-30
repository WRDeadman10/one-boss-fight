// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Engine/EngineTypes.h"
#include "Player/RPGAttackKind.h"
#include "Player/RPGDamageScale.h"
#include "Player/RPGWeaponAttackTable.h"
#include "RPGHitIntake.generated.h"

class UMaterialInterface;

/** What one player hit on the boss was (Gate 3, M7): who, with which weapon and which attack data, in what stance. Plain data, no Unreal object is held strongly. */
struct FRPGHitRecord
{
	/** Counts accepted boss hits of this session, from 1. */
	int32 Id = 0;
	double Time = 0.0;
	/** The asset name of the player's current combat style (SwordCombatStyle, ClaymoreCombatStyle, DualSwordCombatStyle, TwinbladeCombatStyle), None when unknown. */
	FName Weapon;
	/** The asset name of the attack data of this hit (DefaultMeleeAttackData, StrongMeleeAttackData, ChargedMeleeAttackData, MeleeKnockdownAttackData), None when unknown. */
	FName AttackData;
	ERPGAttackKind Kind = ERPGAttackKind::Unknown;
	/** True when the attack's montage started while the player was in the air (a jump attack that lands before its strike still is one). */
	bool bAirborneAtStart = false;
	/** True when more than one hit of the player arrived in the same frame: the pack's hit data then holds only the last one, so the kind of the others is a guess. */
	bool bAmbiguous = false;
	/** The pack's E_AttackPower byte of the attack data (0 default, 3 strong), -1 when unknown. */
	int32 AttackPower = -1;
	/** The pack's own PoiseDamage of the attack data (20 on every pack asset; nothing in the pack reads it), -1 when unknown. */
	float PackPoiseDamage = -1.f;
	/** The montage the player was playing when the hit arrived (None when none). */
	FName Montage;
	/** The stance at the moment of the hit. */
	bool bAirborne = false;
	FName HitBone;
	FVector ImpactPoint = FVector::ZeroVector;
	TWeakObjectPtr<AActor> Target;
	/** The weapon attack table row of this hit (posture damage, stamina, bleed, hyperarmor). */
	FRPGWeaponAttackRow Row;
	/** True when the table had a row for the weapon and kind; false when the table's Fallback was used. */
	bool bRowFound = false;
	/** The row's health damage multiplier (1 = the pack's damage, KI-097). */
	float HealthMultiplier = 1.f;
	/** Where the attack data came from: "HitData" (read one frame after the event), "TargetAttackData" or "none". */
	FName Source;

	FString ToString() const;
};

/**
 * Hit intake (Gate 3, M7). Listens to the pack's own hit event on the player: the player's BP_CollisionComponent has an event dispatcher OnHit(HitResult) that every trace target of the player's weapons (and hands) raises once for
 * each hit. For a hit on the boss this component builds an FRPGHitRecord (the combat style, the montage and the stance at that moment; the attack data of the active trace target's HitData, read ONE FRAME LATER because the
 * pack raises OnHit before it builds the hit data: at the event the hit data still holds the previous hit's, measured by pie_hit_intake.py) and broadcasts OnBossHit.
 * It changes nothing: posture, bleed and costs read the record (M8 and later). No pack asset is edited; the binding is by reflection and refuses to bind when the signature is not OnHit(FHitResult).
 * Attached to the pack player by RPGPlayerMovesSubsystem.
 */
UCLASS(ClassGroup = (Player))
class ONEBOSSFIGHT_API URPGHitIntake : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGHitIntake();

	DECLARE_MULTICAST_DELEGATE_OneParam(FOnBossHit, const FRPGHitRecord&);
	/** Raised once per hit on the boss, one frame after the pack's event, with the attack data read. */
	FOnBossHit OnBossHit;

	/** The pack's hit event arrives here (bound by reflection to BP_CollisionComponent.OnHit). */
	UFUNCTION()
	void HandlePackHit(FHitResult HitResult);

	/** Test drivers only (the proof map has no pack input): raises the same path as the pack's own hit event, on this boss. */
	UFUNCTION(BlueprintCallable, Category = "Hit intake")
	void InjectBossHitForTest(AActor* Boss);

	/** F10 test hook: one hit on a native-health boss carrying the DA_WeaponAttacks row of (Weapon, Kind) (no row: the boss's fallback, logged found=0). */
	UFUNCTION(BlueprintCallable, Category = "Hit intake")
	void InjectBossAttackHitForTest(AActor* Boss, FName Weapon, ERPGAttackKind Kind);

	/** KI-151 test hook: the same hit as a real swing would produce, through the Pending/FinalizePending path of a native-health boss (one frame later; Blades > 1 hits with the same Montage in the same frame merge into ONE hit, as the dual swords' two blades do). */
	UFUNCTION(BlueprintCallable, Category = "Hit intake")
	void InjectBossPendingHitForTest(AActor* Boss, FName Weapon, ERPGAttackKind Kind, int32 Blades);

	/**
	 * The pack names the intake reads, looked up on the pack's Blueprint classes with no world (for the PackWiring test: a pack update that renames one fails there, not silently in a fight):
	 * BP_CollisionComponent_C.OnHit(FHitResult), the trace target variables HitData, Attack Data and bCollisionEnabled?, BP_HitData_C.AttackData, BP_AttackData_C.AttackPower and PoiseDamage, the four melee attack data assets.
	 * Returns true when all are found; OutMissing lists what is not.
	 */
	static bool CheckPackNames(FString& OutMissing);

	/** The table the rows come from (the project's asset, or the built-in defaults when it is missing). */
	const URPGWeaponAttackTable* GetTable() const { return Table.Get(); }

	bool IsBound() const { return bBound; }
	const FRPGHitRecord& GetLastRecord() const { return LastRecord; }

	UFUNCTION(BlueprintPure, Category = "Hit intake")
	int32 GetBossHitCount() const { return BossHitCount; }

	/** Second (and later) hits of one swing on the boss in one frame, merged into the first record (the dual swords' two blades); records whose kind came from the swing and not from the generic Default attack data (M13). Tests. */
	UFUNCTION(BlueprintPure, Category = "Hit intake")
	int32 GetMergedHitCount() const { return MergedHitCount; }

	UFUNCTION(BlueprintPure, Category = "Hit intake")
	int32 GetSwingKindOverrideCount() const { return SwingKindOverrideCount; }

	/** Hits the pack reported on something that is not the boss (props, the arena). */
	UFUNCTION(BlueprintPure, Category = "Hit intake")
	int32 GetOtherHitCount() const { return OtherHitCount; }

	UFUNCTION(BlueprintPure, Category = "Hit intake")
	bool IsHitIntakeBound() const { return bBound; }

	/** True from the pack's hit event until the record is finished (the next frame): a hit that is on its way into the posture pool, the bleed and the stance break. The phase threshold waits for it (RPGBossPhases). */
	UFUNCTION(BlueprintPure, Category = "Hit intake")
	bool HasPendingRecords() const { return bFinalizeScheduled || Pending.Num() > 0; }

	UFUNCTION(BlueprintPure, Category = "Hit intake")
	FString GetLastRecordText() const { return LastRecord.ToString(); }

	/** The records of this session as text lines (last 64), for tests and logs. */
	UFUNCTION(BlueprintCallable, Category = "Hit intake")
	TArray<FString> GetRecordLines() const;

	/** Test drivers only: every hit adds this bleed buildup instead of its table row's (negative: off). */
	UFUNCTION(BlueprintCallable, Category = "Hit intake")
	void SetBleedOverrideForTest(float Buildup)
	{
#if !UE_BUILD_SHIPPING
		BleedOverride = Buildup;
#endif
	}

	/** Test drivers only: forgets the counters and the records. */
	UFUNCTION(BlueprintCallable, Category = "Hit intake")
	void ResetCounters();

	/** Health damage multiplier of the weapon table (KI-097): hits whose health loss was scaled, and the health given back (positive) or taken away (negative) in total. Tests. */
	UFUNCTION(BlueprintPure, Category = "Hit intake")
	int32 GetScaledHitCount() const { return ScaledHitCount; }

	UFUNCTION(BlueprintPure, Category = "Hit intake")
	float GetHealthAdjustTotal() const { return static_cast<float>(HealthAdjustTotal); }

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	struct FPending
	{
		FRPGHitRecord Record;
		TWeakObjectPtr<UObject> ActiveTarget;
		/** KI-151: the target is a native-health boss: FinalizePending hands it the attack row (ApplyPlayerAttackHit) instead of running the pack scaler, posture and bleed components. */
		bool bNative = false;
		/** Test hook only: use this attack kind instead of classifying the pack's attack data (there is none for a synthetic entry). */
		bool bForceKind = false;
		ERPGAttackKind ForcedKind = ERPGAttackKind::Unknown;
	};

	bool TryBind();
	void Unbind();
	/** Everything known at the moment of the event; the attack data is added by FinalizePending. */
	FRPGHitRecord BuildRecord(const FHitResult& HitResult, AActor* Target, UObject*& OutActiveTarget) const;
	/** One frame after the event: reads the active trace target's hit data, classifies the attack, numbers the records and broadcasts them. */
	void FinalizePending();

	/** Latches the stance when a new attack montage starts, every frame (a strong attack made in the air lands after the player does). */
	void TrackMontage();

	/** Watches the boss's health every frame and applies the weapon table's health damage multiplier (FRPGDamageScaler matches a loss with a hit record). */
	void TrackBossHealth(float DeltaTime);
	void AdjustBossHealth(AActor* Boss, double Adjust, const TCHAR* Why);

	TWeakObjectPtr<UObject> BoundCollision;
	UPROPERTY(Transient)
	TObjectPtr<URPGWeaponAttackTable> Table;
	UPROPERTY(Transient)
	TObjectPtr<UMaterialInterface> LoadedHitSparkFlipbook;
	TSet<FString> WarnedRows;
	FName TrackedMontage;
	float LastMontagePosition = 0.f;
	bool bTrackedAirborneAtStart = false;
	float BindRetryTimer = 0.f;
	TArray<FPending> Pending;
	bool bFinalizeScheduled = false;
	float BleedOverride = -1.f;
	bool bBound = false;
	bool bWarnedSignature = false;
	int32 BossHitCount = 0;
	int32 MergedHitCount = 0;
	int32 SwingKindOverrideCount = 0;
	int32 OtherHitCount = 0;
	FRPGHitRecord LastRecord;
	TArray<FString> Lines;

	FRPGDamageScaler Scaler;
	TWeakObjectPtr<AActor> WatchedBoss;
	double PrevBossHealth = -1.0;
	float BossSearchTimer = 0.f;
	float HealthSampleTimer = 0.f;
	double HotUntil = 0.0; // world time until which the boss's health is sampled every frame (a weapon hit's loss arrives in the frame of the pack's event or a few frames later)
	int32 ScaledHitCount = 0;
	double HealthAdjustTotal = 0.0;
};
