# KI-151: Real Pack Weapon Swing Implementation Plan

**Document Version:** 1.0.0  
**Author:** Antigravity  
**Task Reference:** `Documentation/TEAM_MAILBOX.md` `[C-463]` (Lead Claude Direction, 2026-10-31)  
**Target Issue:** KI-151 (Real pack weapon swing through Pending/FinalizePending for native bosses)  
**Status:** PROPOSED ARCHITECTURAL PLAN (Strict Offline Design, Zero Git Push, No Source/Content Edits)  
**Applicable Authorities:** `Source/OneBossFight/Player/RPGHitIntake.cpp`, `Source/OneBossFight/Player/RPGNativeBossHealth.h`, `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp`, `Source/OneBossFight/Combat/RPGInputTestUtils.h`

---

## 1. Executive Summary & Problem Formulation

### 1.1 Context & Background
In Slice F10 (`Commit 56bd93d`), the framework boss was bridged to the weapon attack table (`DA_WeaponAttacks.uasset`) through `IRPGNativeBossHealth::ApplyPlayerAttackHit(const FRPGWeaponAttackRow& Row, double Multiplier)`. However, Slice F10 verified this path exclusively via a synchronous test injection hook:
`URPGHitIntake::InjectBossAttackHitForTest(AActor* Boss, FName Weapon, ERPGAttackKind Kind)`

In real gameplay, when the player (Greystone) swings a physical weapon:
1. The pack's trace component registers collision with the boss and fires the `OnHit` delegate.
2. `URPGHitIntake::HandlePackHit(FHitResult HitResult)` intercepts the collision.
3. Currently, lines 443–447 in `RPGHitIntake.cpp` check if `Target` implements `IRPGNativeBossHealth`:
   ```cpp
   if (IRPGNativeBossHealth* Native = Cast<IRPGNativeBossHealth>(Target))
   {
       Native->ApplyPlayerHit(1.0);
       return;
   }
   ```
4. **The Defect (KI-151):** The native branch immediately returns after calling `ApplyPlayerHit(1.0)`. It completely bypasses:
   - Attack data extraction (`BuildRecord`, `ActiveTarget->HitData`)
   - Attack classification (`RPGClassifyAttack`)
   - Dual-blade multi-hit deduplication (`SeenMontages`)
   - Weapon attack table lookup (`Table->Find(Record.Weapon, Record.Kind, Record.Row)`)
   - `ApplyPlayerAttackHit(Row, 1.0)`

Consequently, any real physical weapon swing hitting the framework boss deals flat unscaled profile damage (`PlayerHitDamage`), ignores weapon type (Sword vs Claymore vs DualSwords), ignores attack kind (Light vs Strong vs Heavy), and deals zero posture drain and zero bleed buildup.

### 1.2 Objective
Route real physical weapon hits against native bosses through `URPGHitIntake::Pending` and `FinalizePending`, resolving the structured `FRPGWeaponAttackRow` and calling `Native->ApplyPlayerAttackHit(Record.Row, 1.0)`.

---

## 2. Ground Truth Analysis & Exact Line Citations

### 2.1 Native Short-Circuit in `HandlePackHit`
* **File:** `Source/OneBossFight/Player/RPGHitIntake.cpp:439-447`
```cpp
void URPGHitIntake::HandlePackHit(FHitResult HitResult)
{
	AActor* Target = HitResult.GetActor();
	// A boss with native health (the framework Sevarog) takes the hit directly: no pack damage execution, record, scaler or posture runs for it.
	if (IRPGNativeBossHealth* Native = Cast<IRPGNativeBossHealth>(Target))
	{
		Native->ApplyPlayerHit(1.0);
		return;
	}
```
* **Observation:** The immediate return prevents `FPending Entry` construction and scheduling of `FinalizePending`.

### 2.2 Record Construction in `BuildRecord`
* **File:** `Source/OneBossFight/Player/RPGHitIntake.cpp:361-399`
```cpp
FRPGHitRecord URPGHitIntake::BuildRecord(const FHitResult& HitResult, AActor* Target, UObject*& OutActiveTarget) const
{
	FRPGHitRecord Record;
	Record.Time = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0;
	Record.Target = Target;
	Record.HitBone = HitResult.BoneName;
	Record.ImpactPoint = HitResult.ImpactPoint;
	Record.Source = TEXT("none");

	// The weapon: the combat style the pack's combat component holds now.
	if (UObject* Combat = FindComponentByClassName(GetOwner(), TEXT("BP_CombatComponent_C")))
	{
		if (const UObject* Style = ReadObject(Combat, TEXT("CurrentCombatStyle")))
		{
			Record.Weapon = Style->GetFName();
		}
	}
	// The trace target that is swinging now: its hit data is read one frame later (FinalizePending).
	OutActiveTarget = BoundCollision.IsValid() ? FindActiveTarget(BoundCollision.Get()) : nullptr;
...
```
* **Observation:** `BuildRecord` is fully agnostic of the target type. It inspects `GetOwner()` (the player) to find `CurrentCombatStyle` and active montages. It works equally well for native and pack bosses.

### 2.3 Delayed Resolution in `FinalizePending`
* **File:** `Source/OneBossFight/Player/RPGHitIntake.cpp:469-578`
* **Multi-Blade Deduplication (`SeenMontages`, lines 476–486):**
  ```cpp
	TArray<FName> SeenMontages;
	for (FPending& Entry : Batch)
	{
		FRPGHitRecord& Record = Entry.Record;
		if (Record.Montage != NAME_None && SeenMontages.Contains(Record.Montage))
		{
			++MergedHitCount;
			UE_LOG(LogRPGHitIntake, Log, TEXT("a second hit of the same swing (montage %s) in the same frame on the boss is merged into the first one (merged so far %d)"), *Record.Montage.ToString(), MergedHitCount);
			continue;
		}
		SeenMontages.Add(Record.Montage);
  ```
* **Attack Data & Classification (lines 488–527):**
  Reads `HitData` from `ActiveTarget` one frame after `OnHit`, calls `RPGClassifyAttack`, applies `URPGSwingTracker` strong/charged overrides.
* **Table Query (lines 528–540):**
  Queries `URPGWeaponAttackTable::Find(Record.Weapon, Record.Kind, Record.Row)`.
* **Pack Boss Scaling vs Native Boss Invocation (lines 542–549):**
  ```cpp
		if (AActor* ScaledBoss = Record.Target.Get())
		{
			const double Adjust = Scaler.OnHit(GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0, Record.HealthMultiplier);
			if (FMath::Abs(Adjust) > 0.01)
			{
				AdjustBossHealth(ScaledBoss, Adjust, TEXT("record first"));
			}
		}
  ```
* **Native Boss Invocation Point (Target Injection):**
  Native bosses do not possess pack attribute components (`AdjustBossHealth` fails closed). Instead, if `Target` implements `IRPGNativeBossHealth`, `FinalizePending` must call:
  ```cpp
  if (IRPGNativeBossHealth* Native = Cast<IRPGNativeBossHealth>(Record.Target.Get()))
  {
      Native->ApplyPlayerAttackHit(Record.Row, 1.0);
  }
  ```

### 2.4 Framework Boss Row Execution
* **File:** `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:168-172`
```cpp
double ARPGFrameworkBossCharacter::ApplyPlayerAttackHit(const FRPGWeaponAttackRow& Row, double Multiplier)
{
    if (!bHittable||bDead||bFailed||!bInitialized||!FMath::IsFinite(Multiplier)||Multiplier<0.||!FMath::IsFinite(Row.HealthDamageMultiplier)||Row.HealthDamageMultiplier<0.f) return 0.;
    return ApplyHit(double(Row.HealthDamageMultiplier)*Multiplier,double(Row.PostureDamage)*Multiplier,double(Row.BleedBuildup)*Multiplier);
}
```
* **Observation:** `ARPGFrameworkBossCharacter` is already fully prepared to execute health scaling, posture drain, and bleed buildup directly from `Row`.

---

## 3. Minimal Code Change Specification

### 3.1 `Source/OneBossFight/Player/RPGHitIntake.h`
Add a native boss tracking flag to `struct FPending`:
```cpp
	struct FPending
	{
		FRPGHitRecord Record;
		TWeakObjectPtr<UObject> ActiveTarget;
		bool bNativeBoss = false; // KI-151: routes native boss through FinalizePending
	};
```

### 3.2 `Source/OneBossFight/Player/RPGHitIntake.cpp` (`HandlePackHit`)
Replace the short-circuit with queue insertion:
```cpp
void URPGHitIntake::HandlePackHit(FHitResult HitResult)
{
	AActor* Target = HitResult.GetActor();
	IRPGNativeBossHealth* Native = Cast<IRPGNativeBossHealth>(Target);
	const bool bPackBoss = Target && URPGPlayerMovesSubsystem::IsPackBoss(Target);

	// Refuse hits on non-boss actors
	if (!Native && !bPackBoss)
	{
		++OtherHitCount;
		return;
	}

	if (GetWorld())
	{
		HotUntil = GetWorld()->GetTimeSeconds() + FRPGDamageScaler::Window + 0.1;
	}

	FPending Entry;
	UObject* ActiveTarget = nullptr;
	Entry.Record = BuildRecord(HitResult, Target, ActiveTarget);
	Entry.ActiveTarget = ActiveTarget;
	Entry.bNativeBoss = (Native != nullptr);
	Pending.Add(MoveTemp(Entry));

	if (!bFinalizeScheduled && GetWorld())
	{
		bFinalizeScheduled = true;
		GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateUObject(this, &URPGHitIntake::FinalizePending));
	}
}
```

### 3.3 `Source/OneBossFight/Player/RPGHitIntake.cpp` (`FinalizePending`)
Branch between pack boss and native boss resolution after `Record.Row` is resolved:
```cpp
		// Native boss execution (KI-151): applies the resolved row directly to the framework boss
		if (Entry.bNativeBoss)
		{
			if (IRPGNativeBossHealth* Native = Cast<IRPGNativeBossHealth>(Record.Target.Get()))
			{
				Native->ApplyPlayerAttackHit(Record.Row, 1.0);
			}
		}
		else
		{
			// Pack boss execution: legacy scaler and health adjustment
			if (AActor* ScaledBoss = Record.Target.Get())
			{
				const double Adjust = Scaler.OnHit(GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0, Record.HealthMultiplier);
				if (FMath::Abs(Adjust) > 0.01)
				{
					AdjustBossHealth(ScaledBoss, Adjust, TEXT("record first"));
				}
			}
		}
```
*(Lines 560–574 for `URPGBossPosture` and `URPGBossBleed` components are safely bypassed for native bosses because `FindComponentByClass` returns null).*

### 3.4 Injected Test Hook Preservation
* `URPGHitIntake::InjectBossAttackHitForTest` maintains its existing immediate execution path (`Native->ApplyPlayerAttackHit(Row, 1.0)` synchronously). It does NOT enter `Pending`, ensuring all existing tests (F10 proof) continue to run synchronously without regression.

---

## 4. Risk Analysis & Mitigation Strategies

| Risk | Description | Impact | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **1. One-Frame Delay** | `FinalizePending` executes 1 tick after `HandlePackHit` via `SetTimerForNextTick`. | Minimal | In PIE runtime, 1 tick ($\approx 16.6\text{ ms}$) is imperceptible and necessary because the pack writes `HitData` after `OnHit`. Injected test hits (`InjectBossAttackHitForTest`) retain synchronous execution. |
| **2. Multi-Blade Merging** | Dual swords strike with 2 blades in 1 frame. The second hit matches `SeenMontages` and is discarded. | Intended Parity | In `DA_WeaponAttacks`, `HealthDamageMultiplier = 0.39f` represents the complete dual-sword swing. Applying both hits would deal double damage. Discarding the second hit preserves legacy parity (KI-092). |
| **3. Null `HitData` on Injected Hits** | Injected hits lack an `ActiveTarget` and cannot read reflected Blueprint properties. | Moderate | Injected hits (`InjectBossAttackHitForTest`) bypass `Pending` entirely, passing authored `Weapon` and `Kind` explicitly. A synthetic test hook for `Pending` explicitly mocks `Record.Weapon` and `Record.Kind`. |
| **4. In-Flight Actor Invalidation** | Boss actor could theoretically be destroyed between frame $N$ and $N+1$. | Negligible | `Record.Target` is stored as `TWeakObjectPtr<AActor>`, safely evaluated with `Record.Target.Get()` before invocation. |

---

## 5. Two-Tier Test Plan

### 5.1 Tier 1: Offline / Synthetic Verification (Zero Real Swing Required)
* **Objective:** Validate `FinalizePending` native branching, row lookup, and multi-blade merging without running the full pack animation graph.
* **Synthetic Test Hook in `URPGHitIntake`:**
  ```cpp
  #if !UE_BUILD_SHIPPING
  void InjectPendingHitForTest(AActor* Boss, FName Weapon, ERPGAttackKind Kind, FName Montage = NAME_None);
  #endif
  ```
  Enqueues an `FPending` entry with `bNativeBoss = true`, mock `Montage`, and calls `FinalizePending` next tick.
* **Test Cases:**
  1. `FrameworkNativePendingLightAttack`: Injects Sword Light attack; asserts `ApplyPlayerAttackHit` called with `HealthDamageMultiplier = 1.0`, `PostureDamage = 20.0`.
  2. `FrameworkNativePendingSeenMontageMerge`: Injects two identical montages in same batch; asserts second hit is merged into `MergedHitCount` and `ApplyPlayerAttackHit` called exactly ONCE.
  3. `FrameworkNativePendingTableFallback`: Injects unknown weapon/kind; asserts fallback row logged and used.

### 5.2 Tier 2: PIE Real-Swing Verification (Driven Real Swing)
* **Objective:** Prove a real physical weapon swing driven by input strikes the boss, routes through `Pending`, and deals table-derived damage in PIE.
* **Input Driver Mechanism:**
  Utilizes `URPGInputTestUtils::SetKeyDown(Controller, FName("LeftMouseButton"), true)` and `SetKeyDown(..., false)`.
  Alternatively, injects `IA_LightAttack` via `URPGInputTestUtils::InjectAction`.
* **Map & Profile:**
  - Map: `L_SevarogFrameworkProofKI151.umap` (derived from `L_SevarogFrameworkProofR2.umap`).
  - Profile: `DA_Sevarog_SwingProof_KI151.uasset`.
  - Position: Player placed at distance $D \approx 120.0\text{ cm}$ (well within pack sword blade reach of $150.0\text{ cm}$).
* **Execution Flow:**
  1. Boss spawns in idle stance at origin.
  2. PIE driver (`drive_ki151.py`) waits for initial settle ($1.0\text{ s}$).
  3. Driver issues `SetKeyDown("LeftMouseButton", true)` followed by `SetKeyDown("LeftMouseButton", false)`.
  4. Player character enters `AM_Greystone_LightAttack_01`.
  5. Scythe/Sword collision volume triggers `HandlePackHit`.
  6. `FinalizePending` logs:
     `[FrameworkProof] attack_row weapon=SwordCombatStyle kind=Light found=1 posture=20 bleed=0 healthMult=1`
  7. Boss logs:
     `[FrameworkProof] boss_hit damage=35 healthBefore=800 healthAfter=765`
     `[FrameworkProof] posture_drain amount=20 postureBefore=100 postureAfter=80 max=100`

---

## 6. Proof Map, Profile Bands, & Card Range Calibration

* **Proof Band:**  
  Set `DA_Sevarog_SwingProof_KI151` band to $[110.0, 135.0]\text{ cm}$ with `AcceptanceCm = 5.0\text{ cm}`.
* **Card Deck:**  
  Use newly calibrated R2 cards: `Move_Sevarog_SwingSlow_F7_R2` ($[105, 200]\text{ cm}$) and `Move_Sevarog_AntiGreed_F7_R2` ($[105, 185]\text{ cm}$).
* **Boss Non-Engagement:**  
  During player swing verification, boss card cooldowns are held or attack count set to 0 to prevent boss retaliation during measurement.

---

## 7. Acceptance Criteria & Sign-Off Checklist

1. [ ] `HandlePackHit` accepts native bosses without short-circuiting to `ApplyPlayerHit`.
2. [ ] `FPending` carries `bNativeBoss` flag.
3. [ ] `FinalizePending` calls `Native->ApplyPlayerAttackHit(Record.Row, 1.0)`.
4. [ ] Injected hits (`InjectBossAttackHitForTest`) continue immediate synchronous execution.
5. [ ] Multi-blade strikes in dual sword montages merge into a single hit (`MergedHitCount` increments).
6. [ ] PIE real-swing test confirms log lines:
   - `[FrameworkProof] attack_row`
   - `[FrameworkProof] boss_hit`
   - `[FrameworkProof] posture_drain`
7. [ ] All 209+ automation tests pass without regressions.
