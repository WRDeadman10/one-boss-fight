# BJ-A01..BJ-A05: Incoming Damage & Parry Combat-Source Audit

**Authority:** [`QUEUE_BJ_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BJ_AG.md) Batch 1 (`BJ-A01..BJ-A05`)  
**Scope:** Strictly read-only C++/test-source audit (`0` engine/build/PIE/asset/commit operations; `0` speculative edits to working pure rules).

---

## 1. `BJ-A01`: Resolver Precedence & Edge Conditions (`RPGDamageResolver.h/.cpp`)

Verified contact decision order in [`RPGDamageResolver.cpp:134-208`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGDamageResolver.cpp#L134-L208) and [`RPGDamageResolver.h:101-116`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGDamageResolver.h#L101-L116):

| Priority | Guard Condition | File:Line | Outcome | Spends `Spent[Key]`? |
|---:|---|---|---|---|
| `1` | `!bEnabled || !Target || !GetWorld()` | `RPGDamageResolver.cpp:137-141` | `Failed` | No |
| `2` | `!bHaveHealth || Before <= 0.0 || Status.Dead` | `RPGDamageResolver.cpp:148`, `.h:103` | `RejectedDead` | No |
| `3` | `!bAttackerAlive || Payload.Generation != CurrentGeneration()` | `RPGDamageResolver.cpp:149-150`, `.h:104` | `RejectedStale` | No |
| `4` | `Spent.Contains(KeyOf(Payload))` (`MoveId\|AttackInstance\|HitKey`) | `RPGDamageResolver.cpp:151`, `.h:105` | `RejectedDuplicate` | Already spent |
| `5` | `RPGBossDamage::IsInvulnerable(Target)` (`Status.Invulnerable`) | `RPGDamageResolver.cpp:153`, `.h:106` | `RejectedInvulnerable` | No |
| `6` | `URPGPlayerParry::IsParrying(Target)` | `RPGDamageResolver.cpp:154`, `.h:107` | `Parried` | **Yes** (`:188`) |
| `7` | `ApplyGuard(Base, bCanBeBlocked, Target == GetPlayerPawn(0) && Status.Blocking)` | `RPGDamageResolver.cpp:158-160`, `.h:112-115` | `Blocked` | **Yes** (`:196`) |
| `8` | `RPGBossDamage::HurtPlayer(...)` succeeds (`false` -> `Failed`) | `RPGDamageResolver.cpp:167-179` | `Accepted` (or `Failed`) | **Yes** on `Accepted` (`:169`); No on `Failed` |

- **Edge Finding (`Low`, `RPGDamageResolver.cpp:188-193`):** For `Outcome == Parried` when `Payload.MoveId == NAME_None` or `Payload.AttackInstance <= 0`, `Spent.Add(Key)` marks the swing spent first, then `RPGPackParry::BuildAttackKey(Payload.Generation, GetOwner()->GetUniqueID(), Payload.MoveId, Payload.AttackInstance, NAME_None, 0.0)` returns `""`, causing `URPGPlayerParry::NotifyParried` to return `false` (`RPGPackParryRules.h:44-54`, `RPGPlayerParry.cpp:157`). Bounded Lead follow-up only if test/synthetic payloads ever omit `MoveId`/`AttackInstance`.

---

## 2. `BJ-A02`: Parry Window / Cost / Grade Boundaries

- **`RPGParry` (`RPGParryRules.h:13-26`):** `DefaultWindowSeconds = 0.25`, `DefaultCooldownSeconds = 0.7`. `Press` rejects non-finite inputs, `WindowSeconds <= 0.`, or `Now < State.ReadyAt`; raises cooldown `< WindowSeconds` to `WindowSeconds`. `IsOpen` is half-open `[OpenedAt, OpenedAt + WindowSeconds)`. Initial `FState{-1.e9, -1.e9}` assumes normal non-negative / `> -1.e9` world timestamps.
- **`RPGParryCost` (`RPGParryCostRules.h:9-27`):** `CanPress` requires finite non-negative `Stamina >= Cost`. `StaminaAfter` charges `Cost * 0.5` when `bParried` else `Cost`, failing closed to `0.` on non-finite/negative values and clamping `>= 0.`. `ParryRefund` clamps at `MaxStamina` and fails closed to `0.`.
- **`RPGParryGrade` (`RPGParryGradeRules.h:21-46`):** Half-open `Offset / WindowSeconds` fractions: `[0.0, 0.4)` -> `Perfect` (`1.0`), `[0.4, 0.8)` -> `Good` (`0.6`), `[0.8, 1.0)` -> `Late` (`0.3`); negative/NaN/`Window <= 0.`/`Offset >= Window` -> `None` (`0.0`).
- **Component Stamina Ordering Finding (`Low`, `RPGPlayerParry.cpp:78, 89-113, 202-235`):** With `StaminaCost > 0`, `Press()` writes reduced stamina (`StaminaAfter(Before, Cost, false)`) at `:96` *before* `RPGParry::Press` checks cooldown/window at `:102`. If cooldown refuses or `WindowSeconds <= 0`, `:108-112` enters `bCostPending = true; bRollbackPending = true`, blocking subsequent `Press()` calls at `:78` while rollback retries up to `5` ticks (`FinishStaminaCost`).

---

## 3. `BJ-A03`: Pack Parry Observer Identity & Deduplication (`RPGPackParryContact.cpp`, `RPGPackParryRules.h`)

- `CurrentAttackKey` (`RPGPackParryContact.cpp:71-91`): `BossId == 0` fails closed (`""`); tracked `(Move != None && Instance > 0)` produces `G{Gen}|B{BossId}|M{Move}|I{Instance}`; untracked falls back to `G{Gen}|B{BossId}|U{Montage}|T{RoundToInt64(StartWorld * 100.0)}` (refuses `Rate <= SMALL_NUMBER` or non-finite rate/pos).
- `FRewardDeduplicator::TryAccept` (`RPGPackParryRules.h:67-85`): rejects `""`, clears `AcceptedKeys` whenever `Generation != CurrentGeneration`, and blocks repeat rewards within the generation.
- **Observer Edge Conditions (`Low`):**
  1. `RPGPackParryContact.cpp:224-225`: `ObservedAttackKeys.Add(AttackKey)` executes at admission *before* the `0.1s` `EvaluateCandidate` window resolves; if a swing's first contact fails `EvaluateCandidate` due to unrelated health loss, that swing key remains suppressed for the swing instance (fail-closed anti-retry).
  2. `RPGPackParryContact.cpp:213, 257-262`: If `URPGPlayerParry` component is detached mid-window, `:213` returns early and `:257` never clears `bPreviousParryWindowOpen` until `ClearEncounterState` (`Generation` or `Player` pointer change).

---

## 4. `BJ-A04..BJ-A05`: Test Coverage Comparison & Pure-Rule Disposition

- **Well-Covered:** 32-flag `Decide` + `ApplyGuard` (`RPGAutomationTests.cpp:202-212`, `RPGBossBlockChipRulesTests.cpp:36-39`), `Press`/`IsOpen`/`PressSchedule`/`Cooldown` property (`RPGParryTests.cpp`, `RPGParryPropertyTests.cpp:38-60`), `10,000`-step + `nextafter` `Grade` monotonicity (`RPGParryGradeTests.cpp`, `RPGParryPropertyTests.cpp:10-36`), `ParryCost` (`RPGParryCostTests.cpp`), `CanStartCandidate`/`EvaluateCandidate`/`BuildAttackKey`/`FRewardDeduplicator` (`RPGPackParryContactTests.cpp:15-83`).
- **Named Uncovered Boundary Cases (Follow-Up Test Additions for Lead Engine Slot):**
  1. `RPGPackParryRules::BuildAttackKey`: explicit `BossId == 0` fail-closed test with valid tracked `Move`/`AttackInstance`, and `Montage == NAME_None` with finite `MontageStartWorldSeconds`.
  2. `RPGPackParryRules::EvaluateCandidate`: negative `RequiredSeconds < 0.` and negative `LossTolerance < 0.` inputs (`RPGPackParryRules.h:35-36`).
  3. `RPGParryCost::ParryRefund`: zero `MaxStamina = 0.` clamp test (`0.`).
- **Pure-Rule Defect Disposition (`BJ-A05`):** Zero pure-rule defects found; all component/boundary notes (`Low`) logged above cleanly without unrequested production mutations (`0` engine/build/test runs).
