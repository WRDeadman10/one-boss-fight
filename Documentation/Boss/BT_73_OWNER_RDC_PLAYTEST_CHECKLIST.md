# BT-73: Owner RDC Full-Mode Playtest Checklist & Operating Guide

- **Date:** 2026-11-17
- **Task ID:** BT-73 / BT-90 (board `BT-73`, `BT-90`)
- **Implementer:** Antigravity
- **Lead / Reviewer:** Codex
- **Reference Tasks:** BT-62, BT-67, BT-68, BT-69, BT-70, BT-71, BT-72, BT-88, BT-90

---

## 1. Current State & Scope Boundaries

### What an Owner Full-Mode Playtest Proves:
1. **Interactive Duel Execution:** Proves that an operator can pilot Greystone (`BP_GreystoneERPlayer`) in `L_SevarogArena` using live keyboard and mouse inputs, exchanging combat hits with Sevarog across both Phase 1 and Phase 2.
2. **Deterministic Encounter Progression:** Proves that player attacks apply 100 damage and 60 posture damage per hit, reducing Sevarog's 1,500 HP to 0 across 15 hits.
3. **Phase & Stagger Mechanics:** Proves that Sevarog transitions to Phase 2 at `<= 60%` HP (900 HP / 6 hits) and enters a 2.5-second stagger window upon accumulating 100 posture.
4. **Encounter Victory & Teardown:** Proves that reaching 0 HP executes Sevarog's `Die()` sequence, logs `[FrameworkProof] RESULT outcome=BossDefeated`, triggers `criteria.boss_death_completed_encounter = true`, requests `editor_request_end_play()`, and cleanly tears down PIE without engine hangs.
5. **C-1155 Safety & Restorability:** Proves that dual atomic locks (`ENGINE_LOCK.json`) and temporary config modifications (`bEnableSevarogFrameworkArenaRoute=True`) are completely restored byte-for-byte upon session termination.

### What an Owner Full-Mode Playtest Does NOT Prove:
1. **Raw BehaviorTree Observability Gate (BT-62 Limitation):** It does **not** resolve the uninstrumented BehaviorTree task-tick observability requirement (`raw_behavior_tree_tick_count`). Even on a flawless `BossDefeated` duel, the driver receipt will report `ACCEPTANCE_STATUS=BLOCKED` (`accepted: false`) pending an Owner decision on `[X-2558]`.
2. **Packaged Build / Shipping Cook Qualification:** It does **not** substitute for packaged standalone builds, cooking pipelines, or shipping performance validation (p99 <= 16.67ms on target hardware).
3. **Standalone Greystone Visual Smoke (`BT-83`):** It does **not** cover the separate opt-in route `rpg.GreystonePlayerTestPawn=1` in `L_SevarogArena`, which is separately gated on fresh Owner approval bound to runner hash `FAB7A89A...`.
4. **Unseen AI State Coverage:** It proves the combat path experienced during the run, not exhaustive branch coverage across all latent BehaviorTree composite nodes.

---

## 2. Context & Lessons from BT-71 Abort & BT-72 Hardening

### Why Manual RDC Input is Mandatory (BT-71 Findings):
In BT-71 (`Run_20261116_233212_e01fc5f9`), an automated Computer Use agent attempted to control the fight programmatically. Windows desktop security boundaries and session isolation rejected the input hooks:
```text
GetCursorPos failed: Access is denied (0x80070005)
```
Consequently, programmatic control failed, no combat inputs were delivered, and manual intervention was required to abort the runner. **Automated or simulated input injection will not work in headless or non-interactive sessions.** The playtest must be conducted manually by a human operator logged into an active Remote Desktop (RDC) session with physical input focus.

### Runner Hardening & Timeout Discipline (BT-72 Updates):
- **Bounded Full-Mode Execution:** `run_sevarog_arena_route_acceptance.ps1` enforces `-FullTimeoutSeconds` (default: **3600 seconds / 1 hour**, bounded by `[ValidateRange(1, 86400)]`).
- **Timestamp Bounding:** Any receipt or exit event recorded after `$deadline` is strictly rejected to prevent stale or race-delayed receipts from passing.
- **Graceful Teardown & Lock Retention:** If the deadline expires, the runner calls `CloseMainWindow()` on its owned Editor process and waits up to 30 seconds. If the process terminates, it restores config and releases locks (`TIMED_OUT`). If the Editor fails to close, the runner intentionally retains temporary config and locks (`TIMED_OUT_LOCKS_RETAINED`) to prevent corrupting runtime state.

---

## 3. Pre-Flight Verification & Runner Hash Gate

### A. Pre-Flight Host Cleanliness:
Before launching, verify from PowerShell that no leftover processes or locks exist:

1. **Check for Running Unreal Processes:**
   ```powershell
   Get-Process -Name UnrealEditor, UnrealEditor-Cmd -ErrorAction SilentlyContinue
   ```
   *Expected:* No output (0 processes).

2. **Check for Engine Locks:**
   ```powershell
   Test-Path C:\UnrealProject\OneBossFight\ENGINE_LOCK.json
   Test-Path C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\ENGINE_LOCK.json
   ```
   *Expected:* Both return `False`.

### B. Runner Hash Re-Binding Requirement:
Following BT-72, the route acceptance runner source hash is:
- `Scripts/Editor/run_sevarog_arena_route_acceptance.ps1`: `5DF121989AA43A6D07B42C9451EFE027155C0B12B0087F0C5890EEACB5E74A3E`

> [!WARNING]
> Historical lead approval receipts bound to the pre-BT-72 runner hash (`94DD2FE8...`) will fail preflight at line 107 (`ABORT: approved subsystem and boss character source hashes do not match the current files`). The lead approval receipt passed via `-LeadApprovalReceipt` must contain `acceptance_runner_sha256 = "5DF121989AA43A6D07B42C9451EFE027155C0B12B0087F0C5890EEACB5E74A3E"`. The refreshed, verified lead approval receipt is located at `Saved\C1619RouteBuild\BT71_LeadApprovalRefresh_20261117_1830\route_lead_approval.json`.

---

## 4. Launching the Full-Mode Playtest

Run the route acceptance runner from PowerShell inside the active RDC desktop session:

```powershell
cd C:\UnrealProject\OneBossFight
powershell -ExecutionPolicy Bypass -File Scripts\Editor\run_sevarog_arena_route_acceptance.ps1 `
    -LeadApprovalReceipt Saved\C1619RouteBuild\BT71_LeadApprovalRefresh_20261117_1830\route_lead_approval.json `
    -Mode Full `
    -FullTimeoutSeconds 3600
```

### Execution Progression:
1. Runner verifies preflight cleanliness and source hash bindings.
2. Acquires dual C-1155 atomic locks (`ENGINE_LOCK.json` + `Docs\BossCombatReview\Execution\ENGINE_LOCK.json`).
3. Backs up `Config/DefaultGame.ini` to `<RUN_DIR>\DefaultGame.ini.original`.
4. Sets `bEnableSevarogFrameworkArenaRoute=True` in `Config/DefaultGame.ini`.
5. Launches `UnrealEditor.exe` loading `L_SevarogArena` and executes `pie_sevarog_arena_route_acceptance.py`.
6. Editor starts, runs preflight verification, and requests PIE begin play after a 2-second stabilization delay.
7. Player spawns as Greystone (`BP_GreystoneERPlayer`) facing Sevarog in `L_SevarogArena`.

---

## 5. In-Game Combat & Tuning Guide

### Player Controls:
- **Movement:** `W`, `A`, `S`, `D`
- **Camera Look:** Mouse
- **Light Attack:** Left Mouse Button (LMB)
- **Heavy Attack:** Right Mouse Button (RMB) / Shift + LMB
- **Dodge / Roll:** Spacebar
- **Lock-On:** Middle Mouse Click (or Target Lock key)

### Approved Combat Tuning & Parameters:
- **Player Health:** 800 / 800 HP.
- **Player Attack Damage:** 100 damage per hit to boss.
- **Sevarog Health Pool:** 1,500 HP (requires 15 clean hits to defeat).
- **Phase 2 Transition:** Occurs when Sevarog's HP drops to `<= 60%` (900 HP / after 6 hits).
- **Posture Damage & Stagger:**
  * Each player hit deals 60 posture damage.
  * Reaching 100 posture triggers a **2.5-second stagger window**, giving the player an opening for successive attacks.

### Victory Sequence:
1. Deplete Sevarog's HP from 1,500 to 0.
2. At 0 HP, Sevarog executes `Die()`, ceases attack routines, and emits:
   `[FrameworkProof] RESULT outcome=BossDefeated acceptedHits=... attacks=...`
3. The acceptance driver detects this marker, sets `criteria.boss_death_completed_encounter = true`, writes `<RUN_DIR>\acceptance.json`, calls `editor_request_end_play()`, and requests clean Editor exit.

---

## 6. Teardown & Recovery Verification

When the session concludes, inspect the runner's final console output and run artifacts:

```text
RESULT=...
MODE=Full
STAGE=completed
REASON=...
RUN=C:\UnrealProject\OneBossFight\Saved\SevarogArenaRoute\Run_YYYYMMDD_HHMMSS_XXXXXXXX
EDITOR_PID=...
DRIVER_RECEIPT=C:\UnrealProject\OneBossFight\Saved\SevarogArenaRoute\Run_YYYYMMDD_HHMMSS_XXXXXXXX\acceptance.json
EDITOR_LOG=C:\UnrealProject\OneBossFight\Saved\SevarogArenaRoute\Run_YYYYMMDD_HHMMSS_XXXXXXXX\editor.log
TEMP_CONFIG_ENABLED=True
CONFIG_RESTORED=True
EDITOR_STILL_RUNNING=False
LOCKS_CREATED=2
LOCKS_RELEASED=2
LOCKS_KEPT=
ACCEPTANCE_STATUS=BLOCKED
CRITERIA={"boss_death_completed_encounter":true,"live_actor_census_framework_one_pack_zero":true,"montage_inactive_at_suppression":true,"pack_bosshud_viewport_count_zero":true,"production_encounter_binding_one_zero":true,"production_sevarog_max_health_1500":true,"production_tick_selected_card_observed":true,"raw_behavior_tree_tick_count":"BLOCKED_NOT_INSTRUMENTED"}
NO_BUILD=1
NO_ASSET_SAVE=1
NO_COMMIT=1
```

### Verification Checklist:
- [ ] `CONFIG_RESTORED=True` (verifies `DefaultGame.ini` matches original SHA256 byte-for-byte).
- [ ] `EDITOR_STILL_RUNNING=False` (verifies owned Editor process has fully terminated).
- [ ] `LOCKS_RELEASED=2` (both C-1155 atomic locks removed).
- [ ] `LOCKS_KEPT=` (empty string; no locks retained).
- [ ] `ACCEPTANCE_STATUS=BLOCKED` (expected while BehaviorTree task ticks remain uninstrumented).
- [ ] `<RUN_DIR>\acceptance.json` contains `"boss_death_completed_encounter": true`.

---

## 7. Abort & Troubleshooting Procedures

### Intentional Manual Abort:
- **Recommended Method:** Close the Unreal Editor main window (click **X** in the top-right corner, or press `Alt + F4`).
- **Do NOT rely solely on Escape:** Pressing Escape terminates PIE, which causes the BT-68 teardown guard to fail closed after 2.0s without boss defeat. Closing the main window cleanly initiates full process shutdown and triggers automatic runner cleanup.

### Handling Timeouts:
- At the 3,600s deadline, the runner issues `CloseMainWindow()` and waits up to 30 seconds.
- If the Editor exits cleanly, `RESULT=TIMED_OUT` is logged, config is restored, and locks are released.
- If the Editor hangs and fails to exit within 30 seconds, `RESULT=TIMED_OUT_LOCKS_RETAINED` is reported. Locks and temporary config are intentionally preserved on disk to protect against concurrency hazards.

### Safe Recovery from Lock Retention (`TIMED_OUT_LOCKS_RETAINED` / `RESTORE_OR_LOCK_CLEANUP_FAILED`):
1. **Do not manually restore config or delete either lock.** Keep the run directory, status, receipt, backup, and lock files intact while diagnosing.
2. Check `<RUN_DIR>\status.txt` and its `EDITOR_PID`; verify that PID and all `UnrealEditor` / `UnrealEditor-Cmd` processes are absent. If an Editor is alive, stop recovery and close only the process owned by this run through its window.
3. Compare the current `Config\DefaultGame.ini` hash with the recorded pre-run hash and `<RUN_DIR>\DefaultGame.ini.original`. If the values disagree, the backup is missing, or ownership is unclear, stop and ask the lead to recover; do not overwrite the current config.
4. Release locks only through the documented C-1155 recovery procedure after verifying each lock's `owner_token` exactly matches this run's token and confirming no other process/run owns it. If either lock has another token or ownership cannot be verified, preserve both locks and escalate. Never blanket-delete `ENGINE_LOCK.json` files.
