# BJ-A11..BJ-A15: Hit Intake, Bleed, Damage Scale & Posture/Stamina Boundaries Audit

**Authority:** [`QUEUE_BJ_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BJ_AG.md) Batch 3 (`BJ-A11..BJ-A15`)  
**Scope:** Strictly read-only C++/test-source audit (`0` build/engine/commit operations).

---

## 1. `BJ-A11`: Hit Intake Validation & Key-Spending Ordering (`RPGHitIntake.cpp`, `RPGDamageResolver.cpp`)

- **`URPGHitIntake` Pending/Reset Path (`RPGHitIntake.cpp:200-217, 528-600`):**
  1. `HandlePackHit` (`:528-572`): Native bosses without active weapon `BoundCollision` route immediately to `Native->ApplyPlayerHit(1.0)` (`:537-543`); real weapon swings bind `Encounter` + capture `Entry.EncounterGeneration = Encounter->GetParticipantGeneration()` (`:560-565`) and queue `FinalizePending` for next tick (`:567-571`).
  2. `OnEncounterReset` (`:200-217`, tested by `FKI172PendingHitGenerationResetOrdering`): Clears `Pending` and invalidates `FinalizePendingTimer` immediately; `FinalizePending` (`:585-592`) double-guards by skipping any entry whose `Encounter->GetParticipantGeneration() != Entry.EncounterGeneration`.
  3. Dual-blade same-frame merge (`:594-600`): Deduplicates hits with identical non-`None` `Record.Montage` (`++MergedHitCount`). Edge (`Low`, `:594`): when `Record.Montage == NAME_None`, multiple hits in the same frame bypass `SeenMontages`.
- **Accepted Key Spending (`RPGDamageResolver.cpp:167-197`):** `Accepted` adds `Key` to `Spent` ONLY after `RPGBossDamage::HurtPlayer(...)` returns `true` (`:169`; health write failure returns `Failed` leaving `Key` unspent). `Parried` (`:188`) and `Blocked` (`:196`) always spend `Key`.

---

## 2. `BJ-A12`: Bleed & Damage-Scale Finite/Bounds Rules (`RPGBleedRules.h`, `RPGDamageScale.h`)

- **`RPGBleedRules::Apply` (`RPGBleedRules.h:48-73`):** Rejects non-finite `Amount`/`Config`/`State` fields, `Amount <= 0.f`, `InitialThreshold <= 0.f`, `ThresholdIncrease < 0.f`, `ThresholdMax < InitialThreshold`, `HpFraction < 0.f`, `State.Buildup < 0.f`, `State.Threshold <= 0.f`, `State.Procs < 0` -> `IgnoredAmount`. Priority order: `Dead` -> `Dormant` -> `Transition` -> `SameFrame` -> add + threshold proc (`Procs` saturates at `MAX_int32`, `Threshold = Min(Threshold + ThresholdIncrease, ThresholdMax)`).
- **`RPGBleedRules::ProcDamage` (`RPGBleedRules.h:76-84`):** Clamps `[0.f, Max(0.f, Health - 1.f)]` so bleed bursts never take the last HP.
- **`FRPGDamageScaler` (`RPGDamageScale.h:15-112`):** Bidirectional pairing within `Window = 0.35s`; rejects non-finite `Time`/`Amount`, falls back non-finite or `< 0.f` `Multiplier` to `1.f` (still consuming matching `FLoss` at `:74-77`), and `Apply` clamps `[1.0, Max(1.0, MaxHealth)]` (never kills or revives; returns unchanged `Health` on non-finite/non-positive inputs).

---

## 3. `BJ-A13`: Posture, Stamina & Parry-Reward Boundaries (`RPGBossPosture.cpp`, `RPGBossStaminaPressureRules.h`, `RPGPlayerParry.cpp`)

- **`RPGBossPosture::ApplyPostureDamage` (`RPGBossPosture.cpp:88-121`):**
  - **Medium/Low Bounded Follow-Up (`RPGBossPosture.cpp:90, 225`):** Guard reads `if (Amount <= 0.f || Posture < 0.f || IsDeadOrDormant())`. Missing `!FMath::IsFinite(Amount)`: passing `NaN` or `+inf` bypasses `Amount <= 0.f` (`NaN <= 0.f` is `false`), poisoning `Posture = NaN` (since `NaN < 0.f` at `:225` and `Posture <= 0.f` at `:107` are both `false`) until `ResetPool`/`RefillAfterBreak`. Contrast `QueueParryPostureDamage` (`:125`), which explicitly guards `FMath::IsFinite(ParryPostureDamage)`. Recommended 1-line Lead fix: reject `!FMath::IsFinite(Amount)` + reset non-finite `Posture` in `TickComponent`.
- **`RPGBossStaminaPressure` (`RPGBossStaminaPressureRules.h:8-12`):** Rejects non-finite inputs, `StaminaFraction` outside `[0, 1]`, `LowThreshold` outside `(0, 1]`, `MaxPressure` outside `[0, 3]` cleanly -> `0.`. Unwired by design (`C-1240` parity).
- **Parry-Reward Non-Double-Spend (`RPGPlayerParry.cpp:78, 154-172`):** `RewardDeduplicator.TryAccept(Generation, AttackKey)` prevents double posture/spark/slow-mo/refund per `(Generation, AttackKey)` before setting `bPendingParried = true`.

---

## 4. `BJ-A14..BJ-A15`: Native Test Mapping & Bounded Disposition

- **Mapped Tests:** `FKI172PendingHitGenerationResetOrdering` (`RPGGenerationResetRegressionTests.cpp:53-94`), `RPGBossDamageBleedFiniteInputTests.cpp:8-64`, `RPGBleedRulesPropertyTests.cpp`, `RPGBossBleedAdaptersTests.cpp`, `RPGDamageScaler{LowerWindow,Reciprocal,WindowBoundaryMutation}Tests.cpp`, `RPGBossStaminaPressureRulesTests.cpp`, `RPGCodexTests.cpp:202-229`.
- **Lead Follow-Up (`0` unbuilt C++ edits written offline):** Add `!FMath::IsFinite(Amount)` check in `RPGBossPosture.cpp:90` (`!FMath::IsFinite(Posture)` reset at `:225`) with a focused NaN/Inf `ApplyPostureDamage` test when the Lead engine build opens.
