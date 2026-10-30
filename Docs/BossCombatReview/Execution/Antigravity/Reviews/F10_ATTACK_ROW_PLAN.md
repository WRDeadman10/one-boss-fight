# Slice F10: Weapon Attack Row Hit Path Implementation Plan

**Document Version:** 1.1.0  
**Author:** Antigravity  
**Task Reference:** `[C-455]`, `[C-456]` (Lead Claude Review & Direction, 2026-10-31)  
**Status:** ACCEPTED AS BASIS (With C-456 Scope Clarifications; Strict Offline Verification, Zero Git Push)  
**Target Framework:** OneBossFight Sevarog Combat Framework (Slice F10 Attack Row Hit Intake Authority)

---

## 1. Executive Overview & Architecture Pattern

Slice F10 bridges the **Weapon Attack Table (`URPGWeaponAttackTable` / `DA_WeaponAttacks`)** with the native **Framework Boss (`ARPGFrameworkBossCharacter`)**. In Slice F8 and F9, the framework boss evaluates hits using flat profile constants (`PlayerHitDamage`, `PlayerPostureHitAmount`, `BleedBuildupPerHit`), while legacy pack bosses resolve structured attack rows (`FRPGWeaponAttackRow`) from `DA_WeaponAttacks.uasset`.

Following Tech Lead Claude's architectural decision in `[C-456]`, Slice F10 implements a **clean reduced scope**:
1. **Authoritative Attack Row Interface**: `IRPGNativeBossHealth` is extended with `ApplyPlayerAttackHit(const FRPGWeaponAttackRow& AttackRow, double Multiplier = 1.0)`, with default implementation delegating to `ApplyPlayerHit(Multiplier)`.
2. **Framework Boss Per-Row Authority**: `ARPGFrameworkBossCharacter` resolves health loss via `PlayerHitDamage * AttackRow.HealthDamageMultiplier`, posture drain via `AttackRow.PostureDamage`, and bleed buildup via `AttackRow.BleedBuildup`.
3. **Deterministic Attack Row Test Hook**: `URPGHitIntake::InjectBossAttackHitForTest(AActor* Boss, FName Weapon, ERPGAttackKind Kind)` looks up the exact row in `DA_WeaponAttacks` (reporting `found=1` or `found=0` fallback) and logs `[FrameworkProof] attack_row weapon=%s kind=%s found=%d posture=%g bleed=%g healthMult=%g`.
4. **Real-Swing Timing Deferred to Future Slice (Known Limit)**: Real player weapon swings resolve attack data one frame later in `FinalizePending` (`Source/OneBossFight/Player/RPGHitIntake.cpp:379, 463-475`) and require same-swing multi-blade hit merging (`SeenMontages`). Routing native bosses through `Pending` is explicitly deferred out of Slice F10 and logged as a Known Issue (KI).
5. **Bleed Gating Dual Role**: `BleedBuildupPerHit` serves both as the fallback buildup amount AND as the gating flag in `BleedEnabled()` (`BleedBuildupPerHit > 0.f`).

---

## 2. Ground Truth Analysis: Current Hit Path vs Legacy Parity

### 2.1 Current Framework Hit Intake Bypass (`RPGHitIntake.cpp`)
In `Source/OneBossFight/Player/RPGHitIntake.cpp:413-421`, `URPGHitIntake::HandlePackHit` intercepts hits on actors implementing `IRPGNativeBossHealth`:
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
...
```
**Architectural Defect in Slice F8/F9**:
- The framework branch immediately returns after calling `Native->ApplyPlayerHit(1.0)`.
- It completely bypasses attack data lookup, attack classification (`RPGClassifyAttack`), and weapon table queries (`Table->Find(Record.Weapon, Record.Kind, Record.Row)`).
- Consequently, light attacks, heavy slams, charged swings, starter sword, strength claymore, and dexterity dual swords all hit the framework boss with identical flat numbers.

### 2.2 Legacy Hit Intake Path (`RPGHitIntake.cpp:538-546`)
In contrast, for legacy pack bosses, `RPGHitIntake.cpp:538-546` resolves the full `FRPGWeaponAttackRow` and routes per-attack parameters into separate components:
```cpp
		// The posture damage of the hit's table row goes into the boss's own pool; the stance break follows when it reaches zero (M9).
		if (AActor* Boss = Record.Target.Get())
		{
			if (URPGBossPosture* Posture = Boss->FindComponentByClass<URPGBossPosture>())
			{
				Posture->ApplyPostureDamage(Record.Row.PostureDamage, *FString::Printf(TEXT("%s %s"), *Record.Weapon.ToString(), RPGAttackKindName(Record.Kind)));
			}
		}
		// The bleed buildup of the hit's table row (the dexterity weapons build the status, M12).
		if (AActor* Boss = Record.Target.Get())
		{
			if (URPGBossBleed* Bleed = Boss->FindComponentByClass<URPGBossBleed>())
			{
				Bleed->AddBuildup(BleedOverride >= 0.f ? BleedOverride : Record.Row.BleedBuildup, *FString::Printf(TEXT("%s %s"), *Record.Weapon.ToString(), RPGAttackKindName(Record.Kind)));
			}
		}
```
Health damage is scaled via `Record.HealthMultiplier = Record.Row.HealthDamageMultiplier` (`RPGHitIntake.cpp:495`) and applied through `FRPGDamageScaler::Apply`.

### 2.3 Current Framework Boss Hit Processing (`RPGFrameworkBossCharacter.cpp`)
In `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:161-184`, the framework boss executes flat arithmetic against profile constants:
```cpp
double ARPGFrameworkBossCharacter::ApplyPlayerHit(double Multiplier)
{
    if (!bHittable||bDead||bFailed||!bInitialized||!FMath::IsFinite(Multiplier)||Multiplier<0.) return 0.;
    const double Before=Health, Loss=FMath::Min(Health,double(Dependencies->Profile->PlayerHitDamage)*Multiplier);
    Health-=Loss;
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] boss_hit damage=%g healthBefore=%g healthAfter=%g"),Loss,Before,Health);
    if (Health<=0.) {Die();return Loss;}
    if (PostureEnabled())
    {
        const double Now=GetWorld()->GetTimeSeconds();
        if (bStaggered) {UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] posture_held reason=StaggerActive posture=%g"),Posture);}
        else
        {
            const double Drain=FMath::Min(Posture,double(Dependencies->Profile->PlayerPostureHitAmount)*Multiplier);
            Posture-=Drain; LastPostureDrain=Now;
            UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] posture_drain amount=%g postureBefore=%g postureAfter=%g max=%g"),Drain,Posture+Drain,Posture,double(Dependencies->Profile->PostureMax));
            RPGBossRules::FFlags Flags; Flags.bDead=bDead; Flags.bStaggered=bStaggered;
            if (Posture<=0. && RPGBossRules::ResolveBreak(Flags,false)==RPGBossRules::EBreakResult::Started) StartStagger();
        }
    }
    if (BleedEnabled()) ApplyBleed(Multiplier);
    return Loss;
}
```

### 2.4 Real-Swing Deferred Timing & Known Limit
As identified in `[C-456]`, during real gameplay:
- Pack hit events build `HitData` asynchronously on the active target actor. `URPGHitIntake` captures `OutActiveTarget` at `RPGHitIntake.cpp:379` (`FindActiveTarget(BoundCollision.Get())`) and resolves `HitData` one frame later in `FinalizePending()` (`RPGHitIntake.cpp:463-475`).
- Multi-blade weapons (e.g. Dual Swords strike together) require same-swing deduplication via `SeenMontages` (`RPGHitIntake.cpp:462`) to prevent duplicate posture/bleed procs in a single frame.
- **Slice F10 Decision**: Integrating native bosses into the full deferred `Pending` queue is held out of Slice F10 and documented as a Known Limit (KI). Slice F10 focuses on the authoritative data pipeline: `DA_WeaponAttacks -> InjectBossAttackHitForTest -> IRPGNativeBossHealth::ApplyPlayerAttackHit -> ARPGFrameworkBossCharacter`.

---

## 3. Interface Design & Signature Evolution (`IRPGNativeBossHealth`)

### 3.1 Interface Evolution in `Source/OneBossFight/Player/RPGNativeBossHealth.h`
The native interface (`Source/OneBossFight/Player/RPGNativeBossHealth.h:18-24`) carries structured attack context while guaranteeing backward compatibility with existing tests:

```cpp
// Forward declarations
struct FRPGWeaponAttackRow;

class ONEBOSSFIGHT_API IRPGNativeBossHealth
{
    GENERATED_BODY()
public:
    /** Current or maximum health; false when this boss is not hittable (no authored health). */
    virtual bool ReadNativeHealth(bool bMax, double& Out) const = 0;

    /** Legacy player hit: scales authored profile defaults by Multiplier. */
    virtual double ApplyPlayerHit(double Multiplier) = 0;

    /**
     * Authoritative weapon attack hit: turns the weapon attack row (posture damage, bleed buildup,
     * health damage multiplier) and profile defaults into health loss, posture drain, and bleed buildup.
     * Default implementation delegates to ApplyPlayerHit(Row.HealthDamageMultiplier * Multiplier).
     */
    virtual double ApplyPlayerAttackHit(const FRPGWeaponAttackRow& AttackRow, double Multiplier = 1.0)
    {
        return ApplyPlayerHit(Multiplier);
    }
};
```

### 3.2 Injected Attack Row Test Hook (`RPGHitIntake.h/.cpp`)
In `Source/OneBossFight/Player/RPGHitIntake.h`:
```cpp
    /** Test hook: looks up (Weapon, Kind) in DA_WeaponAttacks and injects the resolved row into the boss. */
    UFUNCTION(BlueprintCallable, Category = "Hit Intake")
    void InjectBossAttackHitForTest(AActor* Boss, FName Weapon, ERPGAttackKind Kind);
```
Implementation in `RPGHitIntake.cpp`:
- Loads `URPGWeaponAttackTable::LoadOrDefault()`.
- Queries `Table->Find(Weapon, Kind, Row)`.
- Logs structured telemetric token:  
  `[FrameworkProof] attack_row weapon=%s kind=%s found=%d posture=%g bleed=%g healthMult=%g`
- Invokes `Native->ApplyPlayerAttackHit(Row, 1.0)`.

---

## 4. Pure Calculation Helper (`RPGBossMath.h`)

To eliminate algorithmic duplication and guarantee testability in offline unit tests, a pure evaluation helper is added to `Source/OneBossFight/Player/RPGBossMath.h`:

```cpp
namespace RPGBossMath
{
    struct FHitResolutionInput
    {
        double Multiplier = 1.0;
        bool bHasRow = false;
        float RowPostureDamage = 0.f;
        float RowBleedBuildup = 0.f;
        float RowHealthMultiplier = 1.f;
        float ProfileHitDamage = 100.f;
        float ProfilePostureFallback = 40.f;
        float ProfileBleedFallback = 0.f;
        double CurrentHealth = 250.0;
        double CurrentPosture = 100.0;
    };

    struct FHitResolutionOutput
    {
        double HealthLoss = 0.0;
        double PostureDrain = 0.0;
        float BleedBuildup = 0.f;
    };

    /**
     * Pure calculation of hit impacts.
     * When bHasRow is true, row values are authoritative (even if zero, e.g. Claymore has 0 bleed).
     * When bHasRow is false, profile fallbacks are used.
     * Health loss applies RowHealthMultiplier against ProfileHitDamage, clamped to CurrentHealth.
     */
    inline FHitResolutionOutput ResolveHitImpact(const FHitResolutionInput& In)
    {
        FHitResolutionOutput Out;
        if (!FMath::IsFinite(In.Multiplier) || In.Multiplier <= 0.0 || In.CurrentHealth <= 0.0)
        {
            return Out;
        }

        // 1. Health damage: Profile base scaled by attack row multiplier
        const double Multiplier = In.bHasRow ? double(In.RowHealthMultiplier) : 1.0;
        const double NominalDamage = double(In.ProfileHitDamage) * Multiplier * In.Multiplier;
        Out.HealthLoss = FMath::Clamp(NominalDamage, 0.0, In.CurrentHealth);

        // 2. Posture drain: Row posture if present, else profile fallback
        const double BasePosture = In.bHasRow ? double(In.RowPostureDamage) : double(In.ProfilePostureFallback);
        const double NominalDrain = BasePosture * In.Multiplier;
        Out.PostureDrain = FMath::Clamp(NominalDrain, 0.0, In.CurrentPosture);

        // 3. Bleed buildup: Row bleed if present, else profile fallback
        const float BaseBleed = In.bHasRow ? In.RowBleedBuildup : In.ProfileBleedFallback;
        Out.BleedBuildup = FMath::Max(0.f, BaseBleed * float(In.Multiplier));

        return Out;
    }
}
```

---

## 5. Profile Fields: Overrides vs Fallbacks

| Profile Field | Role in Slice F8 / F9 | Role in Slice F10 (With Attack Row) | Justification & Validation Rule |
|---|---|---|---|
| `PlayerHitDamage` | Sole source of hit damage ($100 \times \text{Multiplier}$) | **Base Hit Scale**: Scaled by `Row.HealthDamageMultiplier` | Calibrates baseline encounter pacing while respecting per-weapon scaling (e.g. starter sword $0.39\times$). |
| `PlayerPostureHitAmount` | Sole source of posture drain ($40 \times \text{Multiplier}$) | **Fallback Only**: Used only when hit has no row | Allows weapons to define light ($18$), heavy ($38$), or dex ($6$) drain, while preserving fallback for synthetic hits. |
| `BleedBuildupPerHit` | Sole source of bleed buildup ($60 \times \text{Multiplier}$) | **Dual Role**: Fallback amount AND `BleedEnabled()` gating flag | When `BleedBuildupPerHit > 0.f`, bleed is active on the boss; row bleed is applied per hit. |
| `PostureMax` | Authoritative posture pool size ($100$) | **Unchanged**: Authoritative boss property | Governs boss stance resistance; must not be overridden by weapons. |
| `BleedInitialThreshold` | Initial threshold ($100$) | **Unchanged**: Authoritative boss property | Governs boss status resistance; must not be overridden by weapons. |
| `BleedThresholdIncrease` | Threshold ramp per proc ($+20$) | **Unchanged**: Authoritative boss property | Boss defensive adaptation. |
| `BleedThresholdMax` | Maximum threshold cap ($200$) | **Unchanged**: Authoritative boss property | Boss defensive ceiling. |
| `BleedHpFraction` | Proc damage fraction ($0.20$) | **Unchanged**: Authoritative boss property | Boss ailment vulnerability. |

---

## 6. Execution in `RPGFrameworkBossCharacter`

In `ARPGFrameworkBossCharacter`:
```cpp
double ARPGFrameworkBossCharacter::ApplyPlayerAttackHit(const FRPGWeaponAttackRow& AttackRow, double Multiplier)
{
    if (!bHittable || bDead || bFailed || !bInitialized || !FMath::IsFinite(Multiplier) || Multiplier <= 0.)
    {
        return 0.;
    }

    const auto& P = *Dependencies->Profile.Get();
    RPGBossMath::FHitResolutionInput Input;
    Input.Multiplier = Multiplier;
    Input.bHasRow = true;
    Input.RowPostureDamage = AttackRow.PostureDamage;
    Input.RowBleedBuildup = AttackRow.BleedBuildup;
    Input.RowHealthMultiplier = AttackRow.HealthDamageMultiplier;
    Input.ProfileHitDamage = P.PlayerHitDamage;
    Input.ProfilePostureFallback = P.PlayerPostureHitAmount;
    Input.ProfileBleedFallback = P.BleedBuildupPerHit;
    Input.CurrentHealth = Health;
    Input.CurrentPosture = Posture;

    const RPGBossMath::FHitResolutionOutput Impact = RPGBossMath::ResolveHitImpact(Input);

    // Apply Health Loss
    const double Before = Health;
    Health -= Impact.HealthLoss;
    UE_LOG(LogTemp, Display, TEXT("[FrameworkProof] boss_hit damage=%g healthBefore=%g healthAfter=%g weapon=%s kind=%s"),
        Impact.HealthLoss, Before, Health, *AttackRow.Weapon.ToString(), RPGAttackKindName(AttackRow.Kind));

    if (Health <= 0.)
    {
        Die();
        return Impact.HealthLoss;
    }

    // Apply Posture Drain
    if (PostureEnabled())
    {
        const double Now = GetWorld()->GetTimeSeconds();
        if (bStaggered)
        {
            UE_LOG(LogTemp, Display, TEXT("[FrameworkProof] posture_held reason=StaggerActive posture=%g"), Posture);
        }
        else
        {
            Posture -= Impact.PostureDrain;
            LastPostureDrain = Now;
            UE_LOG(LogTemp, Display, TEXT("[FrameworkProof] posture_drain amount=%g postureBefore=%g postureAfter=%g max=%g weapon=%s kind=%s"),
                Impact.PostureDrain, Posture + Impact.PostureDrain, Posture, double(P.PostureMax),
                *AttackRow.Weapon.ToString(), RPGAttackKindName(AttackRow.Kind));

            RPGBossRules::FFlags Flags;
            Flags.bDead = bDead;
            Flags.bStaggered = bStaggered;
            if (Posture <= 0. && RPGBossRules::ResolveBreak(Flags, false) == RPGBossRules::EBreakResult::Started)
            {
                StartStagger();
            }
        }
    }

    // Apply Bleed Buildup
    if (BleedEnabled())
    {
        ApplyBleedWithAmount(Impact.BleedBuildup, AttackRow);
    }

    return Impact.HealthLoss;
}
```

---

## 7. PIE Test Cases & Proof Specification

### 7.1 Test Case Matrix (Injected Rows via `InjectBossAttackHitForTest`)

| Test Case | Injected Attack Row | Posture Drain / Hit | Bleed Buildup / Hit | Health Multiplier | Expected Behavior |
|---|---|---|---|---|---|
| **Case 1: Claymore JumpHeavy (Stance Break)** | `ClaymoreCombatStyle` `JumpHeavy` | $38.0$ | $0.0$ | $1.0$ | Hit 1: Posture $100 \rightarrow 62$.<br>Hit 2: Posture $62 \rightarrow 24$.<br>Hit 3: Posture $24 \rightarrow 0 \Rightarrow$ **Stance Break** triggered! |
| **Case 2: Dual Swords Light (Bleed Proc)** | `DualSwordCombatStyle` `Light` | $6.0$ | $20.0$ | $1.0$ | Hit 1: Buildup $20/100$.<br>Hit 2: Buildup $40/100$.<br>Hit 3: Buildup $60/100$.<br>Hit 4: Buildup $80/100$.<br>Hit 5: Buildup $100/100 \Rightarrow$ **Bleed Proc** (damage $49$, health $1$, nextThreshold $120$)! |
| **Case 3: Starter Sword Light (Damage Scaling)** | `SwordCombatStyle` `Light` | $18.0$ | $0.0$ | $0.39$ | Damage dealt $= 100 \times 0.39 = 39.0$.<br>Posture drain $= 18.0$. Zero bleed. |
| **Case 4: Regression Multiplier (No Row)** | Fallback row (defaults) | Profile fallback ($40.0$) | Profile fallback ($60.0$) | $1.0$ | Exact parity with Slice F8/F9 behavior. |

### 7.2 Verification Deliverables
1. **Grader**: `Docs/BossCombatReview/Execution/Antigravity/Reviews/grade_f10_log.py` validating that logged `attack_row`, `boss_hit`, `posture_drain`, and `bleed_buildup` tokens match the exact attack row parameters.
2. **Re-Open Test**: `Docs/BossCombatReview/Execution/Antigravity/Reviews/test_reopen_f10_attack_row_plan.py` asserting all file and line citations.
3. **Evidence Pinning**: Pin receipts in `evidence_sha256.txt` with pure CRLF.
