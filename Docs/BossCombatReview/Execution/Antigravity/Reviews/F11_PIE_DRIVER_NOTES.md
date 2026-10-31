# F11 PIE Driver Notes: Posture Break & Phase-Two Driving

Date: 2026-10-31
Author: Antigravity (offline committer/reviewer)
Reference: Task C-521 / C-522, F11 Stagger & Phase 2 Animation Specification (`F11_STAGGER_PHASE_ANIM_SPEC.md` v3)
Scope: Reference guide detailing how `Claude/F4/drive_pie.py` (and wrapper `Claude/F4/run_pie.ps1`) drives automated PIE tests to prove F11 stagger animation triplet playback and phase two transition sequence playback.

---

## 1. Executive Summary & Verification Context

In F11, the native boss framework extends its posture break and phase transition systems with sequence-based animation playback:
1. **Stagger Triplet Playback**: When the boss posture pool is depleted to 0 (triggering `stance_break`), the boss enters a stagger state that plays a dynamic sequence triplet (`StaggerStartAnim`, `StaggerLoopAnim`, `StaggerEndAnim`) on slot `FullBody`.
2. **Phase Transition Hold**: When boss health crosses the phase threshold `PhaseTwoFraction` (triggering `phase_transition`), if `PhaseTransitionAnim` is configured, card selection is suppressed and held in `PhaseTransition` state for the exact duration of the clip (`L_phase` seconds).

To prove these behaviors in live Unreal Engine PIE without manual input, the automated PIE driver `drive_pie.py` coordinates slate post-tick callbacks, map loading, navigation projection, player hit injection, input simulation, and log monitoring.

This document details:
- How existing driver options and control files force a posture break (mid-attack and neutral).
- How existing options drive phase two threshold crossing.
- Exact citations of the F8 and F6c test rows in `Documentation/TEST_PLAN.md`.
- Exact PowerShell command lines to execute F11 proof runs against `L_SevarogFrameworkProofF11` and regression maps.

---

## 2. Driver Architecture & Control File Contracts

The driver (`Docs/BossCombatReview/Execution/Claude/F4/drive_pie.py`) operates via the Slate post-tick callback (`unreal.register_slate_post_tick_callback(tick)`). It executes inside a windowed Unreal Editor instance launched by `Claude/run_editor_script.ps1` with `-NullRhi 0 -PyCmd 1`.

### 2.1 Lifecycle Phases
1. `load`: Waits 30 ticks, then calls `unreal.EditorLoadingAndSavingUtils.load_map(MAP)` and issues console command `RebuildNavigation`.
2. `navwait`: Projects point `Vector(300, 0, 10)` onto navigation mesh until `NavigationSystemV1.is_navigation_being_built(world)` returns `False` and projection succeeds (minimum 2.0 s, timeout 60.0 s).
3. `begin`: Waits 20 ticks, then calls `LevelEditorSubsystem.editor_request_begin_play()`.
4. `run`: Ticks PIE simulation, injects scheduled hits and inputs based on control files, monitors editor log (`current_log.txt`) for `RESULT` or `ERROR` tokens, or times out (`PIE_TIMEOUT = 60.0` s).
5. `quit`: Ends PIE via `LevelEditorSubsystem.editor_request_end_play()`, unregisters the Slate callback, and executes console command `QUIT_EDITOR`.

### 2.2 Control File Registry (`Claude/F4/`)
The driver reads configuration parameters from dedicated one-line text files written by `run_pie.ps1` before editor launch:
- `current_map.txt`: Absolute package path of the proof level (e.g., `/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofF11`).
- `current_log.txt`: Path to destination log file (`<OutDir>/editor_raw.log`).
- `current_inject.txt`: Comma-separated timestamps in seconds elapsed since the first `[FrameworkProof] playback_start` log line. At each timestamp, calls `RPGHitIntake.inject_boss_hit_for_test(boss)` on the live boss.
- `current_inject_pie.txt`: Comma-separated timestamps in seconds elapsed since PIE start (`S['pie_t']`). Injects hits regardless of boss attack state (enables neutral / walking stance breaks).
- `current_inject_row.txt`: Comma-separated entries `seconds:WeaponStyle:AttackKind[:via]` after `playback_start` (e.g. `0.5:ClaymoreCombatStyle:JumpHeavy`). Injects weapon-specific rows from `DA_WeaponAttacks`.
- `current_real_swing.txt`: Comma-separated entries `seconds[:Light|Strong|Charged]` after arrival to inject real Enhanced Input actions (`IA_NormalAttack`, `IA_StrongAttack`, `IA_ChargedAttack`) via `RPGInputTestUtils.inject_action`.
- `current_real_build.txt`: Target build name (`Starter`, `Strength`, `Dex`) switched via console command `rpg.Build <build>`.
- `current_restart.txt`: Existence flag. When present and `[FrameworkProof] boss_dead` is observed, calls `RPGFrameworkProofFixture.restart_encounter_for_test(2)` to verify Generation 2 encounter reset.
- `current_live.txt`: Timestamp after `playback_start` to test invalid restart invocation against a live boss (must be refused).
- `current_dodge.txt` / `current_dodge_action.txt`: Timestamps for key or Enhanced Input dodge injection.
- `current_diag_long.txt`: Existence flag enabling 1.0 s periodic player/boss health diagnostics.

---

## 3. How `drive_pie.py` Forces a Posture Break

### 3.1 Mechanism Overview
A posture break occurs when the boss's posture pool (tracked by `RPGFrameworkBossCharacter::CurrentPosture`, max defined by `URPGBossFrameworkProfile::MaxPosture`) is reduced to 0 by player attacks. When posture reaches 0:
1. `RPGFrameworkBossCharacter::OnStanceBreak()` aborts active attack execution (`MoveExecutor->AbortExecution()`).
2. Logs: `[FrameworkProof] cleanup reason=StanceBreak`.
3. Logs: `[FrameworkProof] stance_break state=<MidAttack|Neutral> duration=<StaggerSeconds>`.
4. In F11, plays dynamic montage sequences on slot `FullBody`:
   - `stagger_anim state=Start clip=<StaggerStartAnim> length=<L_start>`
   - `stagger_anim state=Loop clip=<StaggerLoopAnim> length=<L_loop> count=<LoopCount>`
   - `stagger_anim state=End clip=<StaggerEndAnim> length=<L_end>`
   - `stagger_anim state=Finished`
5. On completion, refills posture pool and logs: `[FrameworkProof] stagger_recovery postureRefilled=<MaxPosture>`.

### 3.2 Mid-Attack Stance Break (In-Attack Interrupt)
- **Driver Parameter**: `current_inject.txt` (via `run_pie.ps1 -Inject "t1,t2,..."`).
- **Timing Origin**: Offset relative to the first `[FrameworkProof] playback_start` line (boss card animation actively playing).
- **Driver Logic**:
  ```python
  if S['dodge_t'] is not None and len(INJECTED) < len(INJECT) and (S['pie_t'] - S['dodge_t']) >= INJECT[len(INJECTED)]:
      intake.inject_boss_hit_for_test(bosses[0])
      INJECTED.append(S['pie_t'])
  ```
- **Posture Breakdown**: For a boss profile with `MaxPosture = 100` and default hit posture drain of 60 per hit:
  - Hit 1 at t = 0.5 s: Posture drops 100 -> 40.
  - Hit 2 at t = 0.9 s: Posture drops 40 -> 0.
  - At t = 0.9 s: Stance break triggers mid-attack (`state=MidAttack`).
- **Test Plan Citation**:
  - `Documentation/TEST_PLAN.md:400` - **BUILD-78: F8 posture / stance break (C-448, 2026-10-31)**
    - *Profile*: `DA_Sevarog_PostureProof_F8`
    - *Map*: `L_SevarogFrameworkProofF8`
    - *Test execution*: Injected hits at 0.5 s and 0.9 s after `playback_start`. Posture drained 100 -> 40 -> 0. Logged `cleanup reason=StanceBreak`, `stance_break state=MidAttack duration=1`, stagger measured 1.07-1.12 s, `stagger_recovery postureRefilled=100`.

### 3.3 Neutral Stance Break (Pre-Arrival / Walking Interrupt)
- **Driver Parameter**: `current_inject_pie.txt` (via `run_pie.ps1 -InjectPie "t1,t2,..."`).
- **Timing Origin**: Direct PIE elapsed time `S['pie_t']`, firing while the boss is walking toward the player before reaching card selection range.
- **Driver Logic**:
  ```python
  if INJECT_PIE and len(INJECTED_PIE) < len(INJECT_PIE) and S['pie_t'] >= INJECT_PIE[len(INJECTED_PIE)]:
      intake.inject_boss_hit_for_test(bosses[0])
      INJECTED_PIE.append(S['pie_t'])
  ```
- **Behavior**:
  - Hits arrive at t = 0.8 s and 1.2 s during walk.
  - Posture pool reaches 0 -> triggers `stance_break state=Neutral`.
  - Boss movement stops, stagger plays.
  - Upon stagger completion (`stagger_recovery`), boss logs `[FrameworkProof] walk_resumed`, arrives at combat range, and enters normal combat.
- **Test Plan Citation**:
  - `Documentation/TEST_PLAN.md:402` - **BUILD-79: F8 neutral break + walk resume (C-449, 2026-10-31)**
    - *Options*: `-InjectPie "0.8,1.2"`, `-DiagLong`.
    - *Verification*: Verified neutral break interrupt, stagger duration, and clean resumption of navigation walk to arrival across 3/3 runs.
  - `Documentation/TEST_PLAN.md:404` - **BUILD-80: KI-150 second cause closed (C-451, 2026-10-31)**
    - *Verification*: Fixed target health initialization race by awaiting `pack_style_known` before target arming; confirmed mid-attack and neutral breaks remain 100% green.

### 3.4 Weapon-Specific Attack Row Stance Break
- **Driver Parameter**: `current_inject_row.txt` (via `run_pie.ps1 -InjectRow "seconds:WeaponStyle:AttackKind[:via],..."`).
- **Test Plan Citation**:
  - `Documentation/TEST_PLAN.md:408` - **BUILD-82: F10 attack row (C-457, 2026-10-31)**
    - *Profile*: `DA_Sevarog_AttackRowProof_F10`
    - *Map*: `L_SevarogFrameworkProofF10`
    - *Verification*: Claymore `JumpHeavy` x3 (drain 38 per hit: 100 -> 62 -> 24 -> 0) triggered `stance_break state=MidAttack`. Dual Swords `Light` x5 tested bleed threshold.

---

## 4. How `drive_pie.py` Forces a Phase 2 Crossing

### 4.1 Mechanism Overview
The boss profile defines:
- `PhaseTwoFraction`: Floating point threshold (e.g. 0.60 or 0.50).
- `PhaseTransitionAnim`: Soft object path to transition animation sequence.
- Phase 1 and Phase 2 card candidate pools.

When an injected hit or real attack inflicts damage such that:
`CurrentHealth / MaxHealth <= PhaseTwoFraction`
The boss state latches `bPhaseTwoLatched = true`:
1. If the boss is currently mid-attack or staggering, the phase transition event is held until the next neutral decision gate.
2. At the neutral gate, the boss enters state `PhaseTransition`.
3. Logs: `[FrameworkProof] phase_transition from=Phase_1 to=Phase_2 health=<CurrentHP>/<MaxHP>`.
4. In F11, plays `PhaseTransitionAnim` on slot `FullBody`:
   - Logs: `[FrameworkProof] phase_anim state=Start clip=<SequenceName> length=<L_phase> holdDuration=<L_phase>`.
   - Card selection is suppressed for `L_phase` seconds.
   - When `L_phase` elapses, logs: `[FrameworkProof] phase_anim state=Finished phase=Phase_2`.
   - Card selection begins immediately, restricted to Phase 2 eligible cards.
5. If `PhaseTransitionAnim` is null/unset: selection begins in the exact same tick (zero delay), preserving F6c immediate transition parity.

### 4.2 Test Plan Citations for Phase 2 Verification
- `Documentation/TEST_PLAN.md:382` - **BUILD-69: F6c phase authority (C-430, 2026-10-30)**
  - *Profile*: `DA_Sevarog_PhaseProof_F6c` (MaxHealth 250, PhaseTwoFraction 0.60 -> threshold 150 HP).
  - *Map*: `L_SevarogFrameworkProofF6c`
  - *Driver configuration*: `current_inject.txt: 0.5,0.9` (two hits inflicting 100 damage each).
  - *Result*: Attack 1 played under Phase_1. After hit 2, health dropped to 50/250 (< 150). `phase_transition` latched, and subsequent attacks were chosen strictly from Phase_2 cards.
- `Documentation/TEST_PLAN.md:388` - **BUILD-72: F6c with baked phase-two cards (C-433, 2026-10-30)**
  - *Profile*: `DA_Sevarog_PhaseProofBaked_F6c`
  - *Map*: `L_SevarogFrameworkProofF6cBaked`
  - *Result*: Verified baked collision sweep execution across Phase 1 and Phase 2 cards.
- `Documentation/TEST_PLAN.md:390` - **BUILD-73: KI-145 SwingMedium reach confirmed in PIE (C-435, 2026-10-30)**
  - *Profile*: `DA_Sevarog_PhaseProofNear_F6c`
  - *Map*: `L_SevarogFrameworkProofF6cNear`
  - *Result*: Calibrated player-boss engagement distance to ~129 cm to ensure consistent hit contact.

---

## 5. Map Assets & Test Profiles in Content/

The following proof assets exist in `Content/OneBossFight/FrameworkProof/`:

| Asset Name | Asset Type | Primary Role |
| :--- | :--- | :--- |
| `L_SevarogFrameworkProofF11.umap` | World / Level | Dedicated F11 animation proof level (includes player start, boss fixture, navmesh bounds). |
| `DA_Sevarog_AnimProof_F11.uasset` | Boss Profile | Dedicated F11 test profile configured with stagger triplet sequences and phase transition sequence on slot `FullBody`. |
| `L_SevarogFrameworkProofF8.umap` | World / Level | F8 posture regression proof level. |
| `DA_Sevarog_PostureProof_F8.uasset` | Boss Profile | F8 posture test profile (no animation triplet, tests posture drain and timing). |
| `L_SevarogFrameworkProofF6c.umap` | World / Level | F6c phase authority proof level. |
| `DA_Sevarog_PhaseProof_F6c.uasset` | Boss Profile | F6c phase test profile (unphased stagger, verifies immediate phase crossing). |
| `L_SevarogFrameworkProofF6cNear.umap`| World / Level | Near-distance phase proof map (~129 cm engagement range). |
| `DA_Sevarog_PhaseProofNear_F6c.uasset`| Boss Profile | Near-distance profile for consistent hit contact. |

---

## 6. Exact Command Lines for F11 Proof Execution

All PIE proof runs must be executed via `Claude/F4/run_pie.ps1` (or low-level `Claude/run_editor_script.ps1`) with the editor closed beforehand. Each run produces a standalone evidence folder under `Docs/BossCombatReview/Execution/Claude/F11/<run_name>/` containing `editor_raw.log`, `pre_state.txt`, and `post_state.txt`.

### 6.1 Proof Run 1: Mid-Attack Stance Break (F11 Stagger Triplet Playback)
Forces a posture break while the boss is executing an attack animation. Verifies that the attack is aborted, `StaggerStartAnim`, `StaggerLoopAnim`, and `StaggerEndAnim` play sequentially on `FullBody`, posture refills, and combat resumes.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File Docs/BossCombatReview/Execution/Claude/F4/run_pie.ps1 `
  -Map "/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofF11" `
  -OutDir "Docs/BossCombatReview/Execution/Claude/F11/mid_break_run1" `
  -Task "f11_mid_break" `
  -Inject "0.5,0.9"
```

**Key Log Assertions**:
- `[FrameworkProof] playback_start moveId=...`
- `[FrameworkProof] boss_hit damage=... postureDrain=...`
- `[FrameworkProof] cleanup reason=StanceBreak`
- `[FrameworkProof] stance_break state=MidAttack duration=...`
- `[FrameworkProof] stagger_anim state=Start clip=...`
- `[FrameworkProof] stagger_anim state=Loop clip=... count=...`
- `[FrameworkProof] stagger_anim state=End clip=...`
- `[FrameworkProof] stagger_anim state=Finished`
- `[FrameworkProof] stagger_recovery postureRefilled=100`
- `[FrameworkProof] RESULT CompletedWithDamage`

### 6.2 Proof Run 2: Neutral Stance Break (Pre-Arrival Walking Stagger)
Forces a posture break before the boss reaches the player (during navigation walk). Verifies that walk stops, stagger triplet plays, posture refills, and navigation resumes via `walk_resumed`.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File Docs/BossCombatReview/Execution/Claude/F4/run_pie.ps1 `
  -Map "/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofF11" `
  -OutDir "Docs/BossCombatReview/Execution/Claude/F11/neutral_break_run1" `
  -Task "f11_neutral_break" `
  -InjectPie "0.8,1.2"
```

**Key Log Assertions**:
- `[FrameworkProof] walk start=...`
- `[FrameworkProof] injected PIE-time hit 1 at pie_t=0.8`
- `[FrameworkProof] injected PIE-time hit 2 at pie_t=1.2`
- `[FrameworkProof] stance_break state=Neutral duration=...`
- `[FrameworkProof] stagger_anim state=Start` -> `Loop` -> `End` -> `Finished`
- `[FrameworkProof] stagger_recovery postureRefilled=100`
- `[FrameworkProof] walk_resumed`
- `[FrameworkProof] RESULT CompletedWithDamage`

### 6.3 Proof Run 3: Phase 2 Crossing with Transition Animation & Selector Hold
Forces boss health below `PhaseTwoFraction`. Verifies that `PhaseTransitionAnim` plays, card selection is suppressed for `L_phase` seconds, logs `phase_anim state=Finished`, and Phase 2 card selection begins.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File Docs/BossCombatReview/Execution/Claude/F4/run_pie.ps1 `
  -Map "/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofF11" `
  -OutDir "Docs/BossCombatReview/Execution/Claude/F11/phase_trans_run1" `
  -Task "f11_phase_trans" `
  -Inject "0.5,0.9"
```

**Key Log Assertions**:
- `[FrameworkProof] phase_transition from=Phase_1 to=Phase_2 health=...`
- `[FrameworkProof] phase_anim state=Start clip=... length=... holdDuration=...`
- Verify: Zero `card_selected` lines emitted while `PhaseTransition` state is active.
- `[FrameworkProof] phase_anim state=Finished phase=Phase_2`
- `[FrameworkProof] card_selected ... phase=Phase_2`
- `[FrameworkProof] RESULT CompletedWithDamage`

### 6.4 Proof Run 4: Complete Lifecycle (Stagger + Phase Crossing + Encounter Restart)
Chains posture break, health reduction across phase threshold, boss death, and generation 2 encounter restart via `current_restart.txt`.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File Docs/BossCombatReview/Execution/Claude/F4/run_pie.ps1 `
  -Map "/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofF11" `
  -OutDir "Docs/BossCombatReview/Execution/Claude/F11/lifecycle_restart_run1" `
  -Task "f11_lifecycle" `
  -Inject "0.5,0.9,1.3,2.5" `
  -Restart
```

**Key Log Assertions**:
- Generation 1: Stagger break, phase transition, boss death (`boss_dead`).
- Fixture restart: `restart_encounter_for_test(2) -> True`.
- Generation 2: Animations reset, state returns to Phase_1 neutral, second `RESULT` emitted.

### 6.5 Proof Run 5: Low-Level Direct Script Invocation (Reference Syntax)
When invoking `run_editor_script.ps1` directly without `run_pie.ps1`, prepare control files first:

```powershell
# 1. Prepare control files in Claude/F4
$E = "Docs/BossCombatReview/Execution/Claude/F4"
"/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofF11" | Set-Content "$E/current_map.txt"
"Docs/BossCombatReview/Execution/Claude/F11/manual_run/editor_raw.log" | Set-Content "$E/current_log.txt"
"0.5,0.9" | Set-Content "$E/current_inject.txt"
Remove-Item "$E/current_restart.txt" -ErrorAction SilentlyContinue
Remove-Item "$E/current_inject_pie.txt" -ErrorAction SilentlyContinue

# 2. Invoke editor script
& "Docs/BossCombatReview/Execution/Claude/run_editor_script.ps1" `
  -Script "$E/drive_pie.py" `
  -OutDir "Docs/BossCombatReview/Execution/Claude/F11/manual_run" `
  -Task "f11_manual" `
  -NullRhi 0 `
  -PyCmd 1 `
  -TimeoutSeconds 240
```

---

## 7. Regression Validation Map Reference

To guarantee that F11 animation additions do not regress earlier milestones, Claude's proof suite should execute regression checks on legacy proof levels:

1. **F8 Posture Regression**:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File Docs/BossCombatReview/Execution/Claude/F4/run_pie.ps1 `
     -Map "/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofF8" `
     -OutDir "Docs/BossCombatReview/Execution/Claude/F11/reg_f8" `
     -Task "f11_reg_f8" `
     -Inject "0.5,0.9"
   ```
2. **F6c Phase Regression (Unset Transition Clip Parity)**:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File Docs/BossCombatReview/Execution/Claude/F4/run_pie.ps1 `
     -Map "/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofF6cNear" `
     -OutDir "Docs/BossCombatReview/Execution/Claude/F11/reg_f6c" `
     -Task "f11_reg_f6c" `
     -Inject "0.5,0.9"
   ```
   *Expected*: Zero selection delay when `PhaseTransitionAnim` is null (F6c byte-identical behavior).
