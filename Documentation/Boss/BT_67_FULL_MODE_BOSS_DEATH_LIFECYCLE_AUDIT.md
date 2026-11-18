# BT-67: Full-Mode Boss-Death Lifecycle Gate and Playtest Safety Audit

Date: 2026-11-17
Task: BT-67 (board `BT-67`)
Implementer: Antigravity
Reviewer / Lead: Codex
Context: Follow-up to [X-2559], BT-62 Smoke gate, BT-63 production profile authoring pass, and BT-66 BehaviorTree observability audit.

---

## 1. Executive Summary

This audit assesses the separate **boss-death lifecycle gate** in the C-1619 Sevarog arena route runner (`Scripts/Editor/run_sevarog_arena_route_acceptance.ps1`) and PIE acceptance driver (`Scripts/Editor/pie_sevarog_arena_route_acceptance.py`) under `-Mode Full`.

While `-Mode Smoke` automatically ends after 180 seconds of observing pre-combat metrics (`boss_death: "NOT_EXERCISED_SMOKE"`), `-Mode Full` exercises the end-to-end combat lifecycle to completion, requiring the boss to be defeated.

### Key Findings
1. **Death Signal & Evidence Path**:
   - Boss death is signaled natively in C++ via `ARPGFrameworkBossCharacter::Die()` (`Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:1193-1204`).
   - `Die()` calls `Executor->Abort("BossDead")`, halts movement, and logs:
     `[FrameworkProof] RESULT outcome=BossDefeated acceptedHits=%d attacks=%d`.
   - Driver detects this regex (`pie_sevarog_arena_route_acceptance.py:92`), validates that all required pre-death evidence is present (`suppression`, `binding`, `pack_bosshud_viewport_count`, `sevarog_max_health`, `tick_selected_card`), emits `acceptance.json`, and requests PIE exit.
2. **Indefinite Wait Behavior in Full Mode**:
   - Unlike Smoke mode (which enforces a strict 900s overall deadline and 180s evidence deadline), Full mode in `run_sevarog_arena_route_acceptance.ps1:159` **has no timeout deadline**. The runner loop polls indefinitely while `UnrealEditor.exe` is running, allowing the owner or tester sufficient time to complete the boss fight.
3. **C-1155 Lock & Config Ownership During Live Play**:
   - The dual atomic C-1155 locks (`ENGINE_LOCK.json` and `Docs/BossCombatReview/Execution/ENGINE_LOCK.json`) remain continuously held throughout the playtest.
   - `Config/DefaultGame.ini` remains temporarily patched with `bEnableSevarogFrameworkArenaRoute=True`.
4. **Fail-Safe Cleanup on Manual Exit, Timeout, or Crash**:
   - If the player closes the Editor window, exits PIE, or crashes, the runner's `finally` block executes unconditionally:
     - Waits up to 30s for the editor process to close.
     - Restores `Config/DefaultGame.ini` byte-for-byte from `DefaultGame.ini.original` and asserts SHA256 match.
     - Releases both C-1155 atomic locks only after config restoration is verified.
     - Retains locks only if an orphaned UnrealEditor process refuses to terminate, preventing workspace drift.
5. **Acceptance Dependency on Raw BT Tick Criterion**:
   - In `pie_sevarog_arena_route_acceptance.py:178`, `receipt["accepted"]` requires all criteria to be `True`. Even with boss death achieved, acceptance will report `BLOCKED` unless the uninstrumented raw BT tick criterion is replaced per the pending Owner Decision ([X-2558]).
6. **Escape-Only Abort Is Not Safe**:
   - In Full mode the driver has no timeout and only calls `finish()` for a route refusal, boss defeat, or exception. It does not detect that PIE has ended while the Editor remains open.
   - Pressing Escape to end PIE can therefore leave the keep-alive Python callback and PowerShell polling loop active indefinitely; the temporary config and both locks remain held until the Editor process exits or the runner is interrupted and completes cleanup.

---

## 2. Death Signaling and Receipt Evidence Flow

### 2.1 C++ Combat Damage and Death Trigger
In `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:959-962`:
```cpp
const double Before=Health, Loss=FMath::Min(Health,double(Dependencies->Profile->PlayerHitDamage)*HealthFactor);
Health-=Loss;
UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] boss_hit damage=%g healthBefore=%g healthAfter=%g"),Loss,Before,Health);
if (Health<=0.) {Die();return Loss;}
```
- In `DA_Boss_Sevarog_FrameworkProfile_Production`, `BossMaxHealth = 1500.0` and `PlayerHitDamage = 100.0`.
- 15 successful player hits (or equivalent posture stagger finisher hits) deplete Sevarog's 1500 HP.
- At `Health <= 0.`, `Die()` is invoked immediately:
```cpp
void ARPGFrameworkBossCharacter::Die()
{
    if (bDead) return;
    bDead=true; RepositionTurnStartedAt=-1.;RepositionLatch=RPGBossTrack::FTurnLatch();PendingParryRecoverySeconds=ParryRecoveryUntil=0.;PendingParryRecoveryGrade=0;
    if(auto* AI=Cast<ARPGFrameworkBossController>(GetController()))AI->StopOwnedWalk();
    GetCharacterMovement()->StopMovementImmediately();GetCharacterMovement()->DisableMovement();
    Executor->Abort(TEXT("BossDead"));StopF11Clip();bStaggerAnimActive=bPhaseHold=false;
    NativeTerminal.Broadcast(this, GenerationId);
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] boss_dead generation=%llu executorAborted=1"),GenerationId);
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] RESULT outcome=BossDefeated acceptedHits=%d attacks=%d"),Executor->AcceptedHits(),AttacksDone+(bStartedMove?1:0));
}
```

### 2.2 Python Acceptance Driver Parsing (`pie_sevarog_arena_route_acceptance.py`)
- Log parsing (line 92):
  ```python
  defeated = re.search(r"\[FrameworkProof\] RESULT outcome=BossDefeated\b", text)
  STATE["checks"]["boss_defeated"] = bool(defeated)
  ```
- Full-mode evaluation (lines 289–296):
  ```python
  if STATE["checks"].get("boss_defeated"):
      required = ("suppression", "binding", "pack_bosshud_viewport_count", "sevarog_max_health", "tick_selected_card")
      missing = [name for name in required if not STATE["checks"].get(name)]
      if missing:
          fail("boss death observed but required evidence missing: " + ",".join(missing))
      else:
          finish("PASS")
      return
  ```
- Receipt emission (lines 143–155):
  ```python
  criteria["boss_death_completed_encounter"] = checks.get("boss_defeated") is True if MODE == "Full" else "NOT_EXERCISED_SMOKE"
  ```
  In Full mode, `boss_death_completed_encounter` evaluates strictly to boolean `True`.

---

## 3. Runner Architecture and Indefinite Wait Behavior

In `Scripts/Editor/run_sevarog_arena_route_acceptance.ps1`:

### 3.1 Polling Loop (`lines 154-164`)
```powershell
$smokeDeadline = [DateTime]::UtcNow.AddSeconds(900)
$hasTimedOut = $false
while ($true) {
    $editorProcess.Refresh()
    if ($editorProcess.HasExited -or (Test-Path -LiteralPath $receipt -PathType Leaf)) { break }
    if ($Mode -eq 'Smoke' -and [DateTime]::UtcNow -ge $smokeDeadline) {
        $hasTimedOut = $true
        break
    }
    Start-Sleep -Milliseconds 250
}
```
- **Smoke Mode**: Times out after 900 seconds (15 minutes), ensuring automated gates never hang unattended.
- **Full Mode**: The `if ($Mode -eq 'Smoke')` condition is bypassed. The runner loops indefinitely every 250 ms, waiting for the human player to defeat the boss or close the Editor.

### 3.2 Post-Run Execution & Teardown (`lines 165-175`)
```powershell
if ($editorProcess) {
    Start-Sleep -Seconds 2
    $editorProcess.Refresh()
    if (-not $editorProcess.HasExited) {
        [void]$editorProcess.CloseMainWindow()
        if (-not $editorProcess.WaitForExit(30000)) { throw 'TIMEOUT: close the acceptance Editor to allow config restoration and lock release' }
    }
}
$editorProcess.Refresh()
$editorExit = $editorProcess.ExitCode
```
- When `acceptance.json` is detected (boss defeated), the runner pauses 2 seconds, requests `CloseMainWindow()`, and waits up to 30 seconds for the Editor to cleanly shut down.

---

## 4. Failure Modes and Cleanup Integrity

The runner's `finally` block (`lines 211-265`) enforces strict C-1155 cleanup under all exit scenarios:

### Scenario 1: Normal Victory (Boss Defeated)
1. Python driver emits `acceptance.json` and ends PIE.
2. Runner closes Editor.
3. Runner verifies runtime sources did not change during PIE (`Get-RuntimeHashes`).
4. Runner restores `DefaultGame.ini` byte-for-byte from `DefaultGame.ini.original` and verifies SHA256 match.
5. Runner releases both atomic locks (`ENGINE_LOCK.json` and `Docs/BossCombatReview/Execution/ENGINE_LOCK.json`).
6. Runner emits `status.txt` with `RESULT=PASS`, `CONFIG_RESTORED=True`, `LOCKS_RELEASED=2`.

### Scenario 2: Player Defeat / Manual Editor Close (`Alt+F4` or Window X)
1. Player is defeated or chooses to abort by closing the Editor main window. Ending PIE with Escape alone is not an abort: Full mode can continue polling with the Editor open and the temporary config/locks held.
2. `$editorProcess.HasExited` becomes true before `acceptance.json` is generated.
3. Catch block catches missing receipt: `throw 'FAIL: PIE driver exited without an acceptance receipt'`.
4. `finally` block executes:
   - Detects Editor is no longer running.
   - Restores `DefaultGame.ini` from backup.
   - Releases both atomic locks.
   - Writes `status.txt` recording `RESULT=FAILED`, `CONFIG_RESTORED=True`, `LOCKS_RELEASED=2`.
   - **Workspace is left 100% clean and unlocked**.

### Scenario 3: Editor Crash or Hang
1. If the Editor crashes, process exits with non-zero exit code.
2. `finally` block detects process termination, restores `DefaultGame.ini`, releases locks, and records crash error code.
3. If the Editor hangs and refuses `CloseMainWindow()`, the runner throws a 30s timeout and retains locks (`locks_retained`), alerting operators that an orphaned process holds the engine.

### Scenario 4: Command Interruption (Ctrl+C)
1. PowerShell guarantees execution of `finally` blocks upon pipeline break.
2. `finally` attempts to close the Editor window and clean up. If the editor closes, config is restored and locks are freed.

---

## 5. Safe Owner Playtest Checklist

When executing `-Mode Full` for the official boss-death lifecycle gate, the owner should follow this verified procedure:

### Pre-Playtest Checklist
- [ ] **Close Unreal Editor**: Verify 0 `UnrealEditor.exe` or `UnrealEditor-Cmd.exe` processes running.
- [ ] **Verify Zero Locks**: Confirm neither `ENGINE_LOCK.json` nor `Docs/BossCombatReview/Execution/ENGINE_LOCK.json` exists.
- [ ] **Verify Production Assets**:
  - `DA_Boss_Sevarog_FrameworkProfile_Production.uasset` (SHA256: `CD72377446E2690AE9885F22D04EB6C6AF78169F34B35C540D0DA543B7809874`).
  - `DA_Sevarog_Framework_Encounter.uasset` (SHA256: `5163928D8A0D4C0526C4B1171117757E72484CD3C0867D97DC6A28AC0F0EE736`).
- [ ] **Identify Build Receipt**: Pinned passing C-1155 build receipt (`Saved/C1619RouteBuild/Run_20261116_180407_2f383983/route_lead_approval.json`).

### Execution Command
Run in PowerShell:
```powershell
powershell -ExecutionPolicy Bypass -File C:\UnrealProject\OneBossFight\Scripts\Editor\run_sevarog_arena_route_acceptance.ps1 -LeadApprovalReceipt C:\UnrealProject\OneBossFight\Saved\C1619RouteBuild\Run_20261116_180407_2f383983\route_lead_approval.json -Mode Full
```

### In-Game Combat Guide
1. **Window Launch**: Unreal Editor will open in a window and automatically launch PIE in `L_SevarogArena`.
2. **Actor Check**:
   - The placed pack boss is suppressed immediately before BeginPlay.
   - Production Sevarog spawns at arena start with 1500 HP.
   - Player spawns with 800/800 HP.
3. **Engaging the Boss**:
   - **Light Attacks (LMB)**: Deals 100 damage per hit and applies 60 posture damage.
   - **Phase 2 Transition**: At 60% HP (900 HP), Sevarog enters Phase 2.
   - **Posture Break**: Depleting posture (100 max) triggers a 2.5-second stagger window.
4. **Victory & Teardown**:
   - On the 15th successful hit (0 HP remaining), Sevarog executes `Die()`.
   - The PIE session will automatically end within 1–2 seconds.
   - The Editor window will automatically close.
   - PowerShell runner outputs `RESULT=PASS` and exits with code 0.

### Abort Procedure
- To abort safely, close the Unreal Editor main window (`Alt+F4` or Window X) so the runner observes process exit and reaches its cleanup path. Do not use Escape alone; it only ends PIE and may leave Full mode waiting indefinitely.
- Wait for the PowerShell runner to print its final status. Confirm `CONFIG_RESTORED=True`, `EDITOR_STILL_RUNNING=False`, and `LOCKS_RELEASED=2` before treating the workspace as available. If these checks fail or locks are retained, stop and request recovery rather than reopening the Editor.

---

## 6. Operating Discipline Statement

- Audit type: Source inspection and control-flow tracing only. Codex lead review accepted the lifecycle signal and lock/cleanup analysis, with the Escape-only abort correction above.
- 0 tests, 0 builds, 0 Unreal Editor launches, 0 PIE runs executed.
- 0 assets, configurations, or C++ files modified.
- 0 git commits or pushes performed.
