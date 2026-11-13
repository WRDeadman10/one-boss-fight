# QUEUE_BJ_AG Closeout (`BJ-A01..BJ-A50`, Batch 10: `BJ-A46..BJ-A50`)

**Authority:** [`QUEUE_BJ_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BJ_AG.md) (`50/50` tasks closed across 10 read-only 5-task batches: `[A-813]..[A-822]`)  
**Policy Compliance (`AGENTS.md`, `PROJECT_STATE.md:384`, `[X-1917]`):** `0` Unreal Editor, engine, UBT/build, PIE, packaged run, asset, config-default, Owner-pick, `git commit`, or `git push` operations; `0` speculative runtime C++ edits; `0` new queue created without Lead authorization. All code observations remain strictly classified as conditional edge cases / follow-up risks rather than confirmed runtime defects.

---

## 1. Deliverable Inventory (`BJ-A48`)

| Batch | Tasks | Receipt | Report File |
|---:|---|---|---|
| 1 | `BJ-A01..A05` | `[A-813]` | [`BJ_A01_A05_DAMAGE_AND_PARRY_AUDIT.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BJ_A01_A05_DAMAGE_AND_PARRY_AUDIT.md) |
| 2 | `BJ-A06..A10` | `[A-814]` | [`BJ_A06_A10_DODGE_AND_TRACKER_AUDIT.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BJ_A06_A10_DODGE_AND_TRACKER_AUDIT.md) |
| 3 | `BJ-A11..A15` | `[A-815]` | [`BJ_A11_A15_HIT_INTAKE_AND_STATE_AUDIT.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BJ_A11_A15_HIT_INTAKE_AND_STATE_AUDIT.md) |
| 4 | `BJ-A16..A20` | `[A-816]` | [`BJ_A16_A20_ENCOUNTER_SELECTION_LIFECYCLE_AUDIT.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BJ_A16_A20_ENCOUNTER_SELECTION_LIFECYCLE_AUDIT.md) |
| 5 | `BJ-A21..A25` | `[A-817]` | [`BJ_A21_A25_CARDS_SELECTOR_COMBO_AUDIT.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BJ_A21_A25_CARDS_SELECTOR_COMBO_AUDIT.md) |
| 6 | `BJ-A26..A30` | `[A-818]` | [`BJ_A26_A30_EXECUTOR_AND_TIMING_AUDIT.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BJ_A26_A30_EXECUTOR_AND_TIMING_AUDIT.md) |
| 7 | `BJ-A31..A35` | `[A-819]` | [`BJ_A31_A35_TARGET_TRACE_AND_NAV_AUDIT.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BJ_A31_A35_TARGET_TRACE_AND_NAV_AUDIT.md) |
| 8 | `BJ-A36..A40` | `[A-820]` | [`BJ_A36_A40_PHASE_EFFECTS_AND_CLEANUP_AUDIT.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BJ_A36_A40_PHASE_EFFECTS_AND_CLEANUP_AUDIT.md) |
| 9 | `BJ-A41..A45` | `[A-821]` | [`BJ_A41_A45_HUD_GUARDS_AND_TEST_QUALITY_AUDIT.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BJ_A41_A45_HUD_GUARDS_AND_TEST_QUALITY_AUDIT.md) |
| 10 | `BJ-A46..A50` | `[A-822]` | [`QUEUE_BJ_AG_CLOSEOUT.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BJ_AG_CLOSEOUT.md) |

---

## 2. Deduplicated Findings & Bounded Follow-Up Index (`BJ-A46`, `BJ-A47`, `BJ-A49`)

Every finding below is deduplicated to one root cause with exact `file:line`, scope, and Lead review disposition (`0` speculative edits applied):

| ID | Severity / Class | Location | Deduplicated Summary & Trigger Condition | Suggested Lead / Codex Action |
|---|---|---|---|---|
| `F-01` | Medium (Conditional Follow-Up) | [`RPGOwnedTagCleanup.h:21-67`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Pack/RPGOwnedTagCleanup.h#L21-L67) | Delayed `Status.Invulnerable` removal retries key only on `(WeakOwner, Tag)` without encounter-generation/lease identity; overlaps with Queue `BK-5` (Codex engineering assignment in `[C-1286]`). | Covered by Claude's ordered Queue `BK-5` two-generation reuse test + generation fence. |
| `F-02` | Medium/Low (Bounded NaN Guard) | [`RPGBossPosture.cpp:90, 125, 225`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPosture.cpp#L88-L128) | `ApplyPostureDamage` checks `Amount <= 0.f` without `!FMath::IsFinite(Amount)` (`NaN` comparison evaluates `false`, unlike `QueueParryPostureDamage` at `:125`). | Add `!FMath::IsFinite(Amount)` rejection + non-finite recovery guard in `TickComponent` when a build slot is free. |
| `F-03` | Low (Conditional Caller Edge) | [`RPGDamageResolver.cpp:188-193`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGDamageResolver.cpp#L188-L193) | Synthetic parry payload with `MoveId == NAME_None` or `AttackInstance <= 0` spends `Spent[Key]` cleanly while `BuildAttackKey` returns `""`, returning `false` from `NotifyParried`. | Keep payload discipline or reject invalid parry metadata if synthetic callers can omit it. |
| `F-04` | Low (Conditional Stamina Edge) | [`RPGPlayerParry.cpp:78, 89-113`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGPlayerParry.cpp#L78-L113) | With `StaminaCost > 0`, `Press()` writes stamina before `RPGParry::Press` checks cooldown/window; refusal queues `bRollbackPending`, blocking retry until rollback clears (`<= 5` ticks). | Defer stamina write until `RPGParry::Press` accepts, or add stateful test coverage. |
| `F-05` | Low (Conditional Detach Edge) | [`RPGPackParryContact.cpp:213, 224-225, 257-262`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGPackParryContact.cpp#L213-L262) | Component detach mid-parry leaves `bPreviousParryWindowOpen` set until generation/player change; failed `EvaluateCandidate` keeps `ObservedAttackKeys` spent intentionally against retries. | Conditional only on runtime component detach/reattach while actor stays alive (`[X-1917]`). |
| `F-06` | Low (Conditional Clip-Load Edge) | [`RPGDodgeTiming.cpp:519-556`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGDodgeTiming.cpp#L519-L556) | `OnDodgePressed` arms `PendingDodgeActivationRetryPress = 1` at `:520-550` before null-checking synchronously loaded montages at `:553-555`. | Clear retry state if montage preload fails. |
| `F-07` | Low (Conditional Tracker Edge) | [`RPGSwingTracker.cpp:167`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGSwingTracker.cpp#L167), [`RPGAttackTracker.cpp:418`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L418) | Same-montage restart at exact `0.0s` / identical `TimingIndex` can keep prior swing/window identity instead of triggering fresh start edges. | Documented assumption (`Montage` / `TimingIndex` change on restart); verify if rapid self-cancels are added. |
| `F-08` | Low (Dual-Blade Edge) | [`RPGHitIntake.cpp:594`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGHitIntake.cpp#L594) | Same-frame multi-hit merge deduplicates non-`None` `Record.Montage` keys; `NAME_None` montage bypasses `SeenMontages`. | Conditional only on synthetic hits lacking montage identity. |
| `F-09` | Low (Nested Rebind Edge) | [`RPGPlayerMovesSubsystem.cpp:590-595`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp#L590-L595) | Updating `PendingRebindGeneration` inside `PendingPlayerPossession` keeps the original `5.0s` timer deadline rather than resetting it. | Add multi-reset world test if rapid consecutive resets during possess become possible. |
| `F-10` | Low (Selector Hysteresis/Scale) | [`RPGBossMoveSelector.cpp:22-25, 52-54, 66`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossMoveSelector.cpp#L22-L66) | `ConeInside` clears only on explicit `"MoveModel.Cone"` refusal (not `Phase`/`Range` exit); maximal `1e6` stacked multipliers can overflow `float Score`. | Add non-cone hysteresis clear test if authored moves mix tight ranges with cone hysteresis. |
| `F-11` | Low (Executor Ordering & Cleanup) | [`RPGFrameworkMoveExecutor.cpp:100-124, 155-158, 288-386, 463-473`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L100-L158) | `StartCard` sets tick enabled prior to validation (`:155-158`, guarded by `!OwnedMontage`); clean `Rearm` (`:100-111`) does not explicitly call `ClearAreaSnare(true)` unlike `Abort`/`EndPlay`; `HitMaxSubsteps` caps coarse hitch steps. | Consider `ClearAreaSnare(true)` in `Rearm` if encounters reset cleanly mid-snare without `Abort`. |
| `F-12` | Low (Nav & Trace Edges) | [`RPGFrameworkBossCharacter.cpp:427`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L427), [`RPGBossLosLeashDeadlineTests.cpp:20-23`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGBossLosLeashDeadlineTests.cpp#L20-L23), [`RPGPackTrace.cpp:17, 308`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Pack/RPGPackTrace.cpp#L17-L308) | `HandleLeash` uses raw `MoveToLocation(ArenaOrigin)` without projection; `FLosMemory::LostAt` advances during leash skip; `GetStoredLocation` matches `EndsWith`; static `WarnedNames` spans PIE runs. | Live `L_SevarogArena` navmesh & socket naming keep these benign under Lead PIE gates. |
| `F-13` | Low (Phase Divisor Guard) | [`RPGBossPhases.cpp:384, 388, 526-551`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPhases.cpp#L384-L551) | `RemovePhaseTwoBuffs` divides by `MovementScale`/`AttackRateScale` without zero guard (protected by config validation); `NextFireball` reset relies on `FinishTransition`. | Guard `> KINDA_SMALL_NUMBER` if direct native writes are exposed. |
| `F-14` | Low (HUD Detach & Test Tautology) | [`RPGBossHud.cpp:193, 369-372`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/UI/RPGBossHud.cpp#L193-L372), [`RPGSourceTestGapTests.cpp:152, 154`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGSourceTestGapTests.cpp#L152-L154) | Detached victory HUD persists if `bRetryEnabled` stays `true` without level reload; `FRPGBossInterruptNoComponentsTest` ends with literal `TestTrue(..., true)` smoke assertions. | Replace literal `true` with component/tag non-mutation assertions; live HUD retry teardown requires `OpenLevel`. |

**Review Reconciliation:**
- `[X-1917]` accepted `A-813` / `A-814`.
- `[C-1286]` accepted `A-752..A-818` (all `BD_AG..BI_AG` and `BJ_AG` Batches 1–6) and verified `BUILD-298 GREEN 509/509` in `[C-1287]`. `A-819..A-822` (`BJ-A31..A50`) complete the queue cleanly with `0` unverified runtime claims.

---

## 3. Verification Executed After Final Closeout Edit & Handoff (`BJ-A50`)

- **Executed Commands:**
  - `python -m unittest discover -s Scripts/Tools -p "test_bi_*.py"` -> `14/14` (`OK`)
  - `python -m unittest discover -s Scripts/Tools -p "test_bh_*.py"` -> `12/12` (`OK`)
  - `python -m unittest discover -s Scripts/Tools -p "test_bf_*.py"` -> `14/14` (`OK`)
  - `python -m unittest discover -s Scripts/Tools -p "test_be_*.py"` -> `33/33` (`OK`)
  - `python -m unittest discover -s Scripts/Tools -p "test_bd_*.py"` -> `10/10` (`OK`)
  - `python -m unittest discover -s Scripts/Tools -p "test_b*_contract.py"` -> `102/102` (`OK`)
  - `python -m unittest Scripts.Tools.test_c1285_retarget_root_chain_contract Scripts.Tools.test_c1276_sevarog_s6_s8_contract Scripts.Tools.test_c1278_x26_acceptance_contract Scripts.Tools.test_probe_greystone_materials_contract Scripts.Tools.test_validate_queue_batches Scripts.Tools.test_check_shipping_guards Scripts.Tools.test_bg_a09_bf_x16_contract` -> `21/21` (`OK`)
  - `python Scripts/Tools/check_shipping_guards.py --source Source` -> `[SHIPPING_GUARDS] declarations=42 shipping_uses=0`
  - `python Scripts/Tools/check_doc_links.py` -> `broken_links=0`
- **Next Steps Held for Lead / Owner:**
  1. **Commits (`[C-1286]`/`[C-1287]` vs `AGENTS.md` / `PROJECT_STATE.md:384`):** Antigravity holds `git commit` (`0` commits, `0` pushes executed) strictly per project/user rules ("the user commits on their own, never commit or push unless asked") until explicit Owner approval.
  2. **Lead Acceptance Reviews (`[C-1286]` Item 3):** Monitor `Documentation/TEAM_MAILBOX.md` for Claude's RM4, X26, and BF-X05 result posts and review each against its acceptance table as it lands. No successor `50`-task queue is created unless Lead explicitly assigns one.
