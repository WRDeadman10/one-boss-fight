# BT-88: Greystone Visual Smoke Lifecycle Wait Diagnosis (Run 1)

**Author:** Antigravity (Implementer)
**Date:** 2026-11-17
**Scope:** Source- and log-only diagnosis of Run 1 (`Run_20261117_161913_a87434f6`), strictly separating empirical log/source facts from working hypotheses, and verifying lifecycle conditions for the 180s retry.
**Constraint:** Strict source-only; 0 tests, 0 builds, 0 Unreal Editor launches, 0 PIE runs, 0 asset/config mutations, 0 git commits/pushes.

---

## 1. Action Completed: Removal of Unauthorized Test Source

As instructed in `[X-2601]`, the untracked test file `Scripts/Tools/test_greystone_visual_smoke_contract.py` was immediately deleted without execution.
- File status: Removed from workspace (`Test-Path` returned `False`).
- Preserved deliverable files:
  * `Scripts/Editor/run_greystone_visual_smoke.ps1` (SHA256: `FAB7A89AC4710F9F955F8A3E9DDA18C97F0882BC973132E210213B070B14DB1F`)
  * `Scripts/Editor/pie_greystone_visual_smoke.py` (SHA256: `68CF485F54858B943A5D7B1DE2D209768898E0F143B79E550D06B35836EB4AF1`)
  * `Scripts/Tools/validate_greystone_visual_smoke_receipt.py` (SHA256: `8DBE1427B4A9769851A2345CEFD77AF410CE04223B43F6576ACD1D8BBEB956BE`)

---

## 2. Empirical Log and Source Facts (Run 1)

The following statements are direct empirical facts extracted from `Saved/GreystoneVisualSmoke/Run_20261117_161913_a87434f6/editor.log` and the runner/driver sources, without interpretation:

### 2.1 Chronological Telemetry and Log Events
1. **Process Launch & Deadline Anchor:**
   - At `16:19:13.852Z`, `run_greystone_visual_smoke.ps1` started `UnrealEditor.exe` with `-ExecutePythonScript` and set `$deadline = [DateTime]::UtcNow.AddSeconds(60)` (`16:20:13.852Z`).
2. **Python Script Entry:**
   - At `16:20:13.852Z` (Line 1696, Frame [ 2]), the engine invoked the `-ExecutePythonScript` entry point:
     `LogPython: [GreystoneVisualSmoke] INITIALIZING_GREYSTONE_VISUAL_SMOKE_DRIVER token=a87434f6c3f44fd58cb1db3747dcc3b7`
   - *Note on bootstrap:* This timestamp confirms the Python entry point was reached by the engine; it does not indicate completion of all background startup subsystems.
3. **Runner Timeout Expiration:**
   - At `16:20:13.852Z`, exactly 60.0 seconds after launch, the runner's polling loop evaluated `[DateTime]::UtcNow -ge $deadline` as true, broke the loop, and logged:
     `[RunGreystoneSmoke] Execution reached timeout deadline (60 s).`
   - After a 1-second sleep (`16:20:14.852Z`), the runner invoked `$editorProcess.CloseMainWindow()`.
4. **Level Loading and PIE Request:**
   - At `16:20:13.854Z` - `16:20:14.120Z` (Lines 1699-1734), the Python script executed `load_level("/Game/OneBossFight/Maps/L_SevarogArena")`.
   - At `16:20:14.121Z` (Line 1735), the Python script registered the Slate post-tick callback and called `editor_request_begin_play()`.
5. **PIE World Start:**
   - At `16:20:20.200Z` (Line 1781, Frame [ 2]), the engine logged:
     `PIE: Play in editor total start time 6.044 seconds.`
   - At `16:20:20.247Z` (Line 1782, Frame [ 2]), the driver's Slate callback observed the world:
     `LogPython: [GreystoneVisualSmoke] PIE_WORLD_FOUND raw=L_SevarogArena normalized=L_SevarogArena`
     Driver set `STATE["phase"] = "waiting_for_possession"` and `STATE["started_at"] = 16:20:20.247Z`.
6. **Automation Controller Large Delta Warning:**
   - At `16:20:20.247Z` (Line 1783, Frame [ 2]), the engine logged:
     `LogAutomationController: Ignoring very large delta of 6.57 seconds in calls to FAutomationControllerManager::Tick() and not penalizing unresponsive tests`
   - During Frame [ 3], another large delta occurred. At `16:20:29.856Z` (Line 1864, Frame [ 3]), the engine logged:
     `LogAutomationController: Ignoring very large delta of 9.61 seconds in calls to FAutomationControllerManager::Tick() and not penalizing unresponsive tests`
7. **World Teardown and Loss:**
   - During Frame [ 3], the OS message queue dispatched window closure to Slate:
     * `16:20:29.636Z` (Line 1838): `LogWorld: BeginTearingDown for /Game/OneBossFight/Maps/UEDPIE_0_L_SevarogArena`
     * `16:20:29.639Z` (Line 1839): `LogWorld: UWorld::CleanupWorld for L_SevarogArena, bSessionEnded=true, bCleanupResources=true`
   - At `16:20:29.852Z` (Line 1848, Frame [ 3]), the driver's Slate post-tick callback executed. In `waiting_for_possession`, `unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()` returned `None`.
   - Driver emitted:
     `LogPython: Error: [GreystoneVisualSmoke] SMOKE_FAILED reason=PIE game world lost while waiting for possession`
8. **Pawn Possession / Replacement Observation in Run 1:**
   - Lines 1856-1858 record the exact state of possession when the test terminated:
     `POSSESSED_PAWN class=None path=None`
     `SOURCE_MESH component=None hidden=0 mesh=None anim=None tick=None`
     `VISIBLE_MESH component=None visible=0 mesh=None anim=None parent=None`
   - Neither the initial pawn nor the replacement Greystone pawn was ever possessed or verified in Run 1.
9. **Fail-Closed Cleanup & Lock Discipline:**
   - At `16:20:29.853Z` (Lines 1849-1853), the driver executed `rpg.GreystonePlayerTestPawn 0`, verified readback == `"0"`, wrote receipt (`accepted=False`), and removed the Slate callback.
   - At `16:20:30Z`, the Editor process exited cleanly (exit code 0).
   - The runner verified `DefaultGame.ini` SHA256 integrity, released its owned locks matching `$token`, and threw the timeout exception.

---

## 3. Inferences and Working Hypotheses (Distinguished from Facts)

The following items are technical inferences and working hypotheses based on code inspection, not established empirical facts:

1. **Cause of the 9.61s Delta in Frame [ 3]:**
   - *Inference:* Lines 1812-1827 log multiple `LogStreaming: Display: ImportPackages: SkipPackage` entries for missing vector fields/textures, and lines 1828-1835 log three `LogMaterial: Warning` compilation failures (`M_Swirl_Plasma`, `M_DustInvis`).
   - *Distinction:* While these asset loading and material compilation events occurred concurrently during the 9.61s tick, the log does **not** prove that shader or material compilation was the sole or primary cause of the delta. Other background activities (streaming, garbage collection, Slate layout) may have contributed.
2. **Timing of Player Possession and Replacement:**
   - *Hypothesis:* Based on static inspection of `URPGPlayerMovesSubsystem::OnPackPawnSpawned` and `SetTimerForNextTick`, pawn replacement is designed to trigger on the frame immediately following initial pawn spawn.
   - *Distinction:* Because pawn spawn and possession were not observed before teardown, and whether initial spawn actually occurred is unknown (the log records only that the final possessed pawn snapshot was `None` without logging a spawn event), the timing of possession and pawn replacement under live PIE conditions has **not been empirically measured or observed**. Claims that possession or replacement will occur in `<1.0s` are unverified working hypotheses.
3. **Prognosis for 180s Timeout Retry:**
   - *Hypothesis:* In Run 1, ~67 seconds elapsed between process start and PIE world discovery (`16:19:13` to `16:20:20`). With `$TimeoutSeconds` raised to 180 (BT-86), the runner is expected not to issue `CloseMainWindow()` during initial world setup.
   - *Distinction:* Whether the test will cleanly pass within the 180s window remains an unverified hypothesis that can only be proven by an authorized live execution under C-1155.

---

## 4. Runner Timeout Polling & Driver Callback Mechanics

### 4.1 Runner Polling Architecture (`run_greystone_visual_smoke.ps1`)
- The runner anchors a wall-clock deadline immediately following `Start-Process`:
  ```powershell
  $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
  ```
- Polling loop interval: `Start-Sleep -Milliseconds 250`.
- Timeout check:
  ```powershell
  if ([DateTime]::UtcNow -ge $deadline) {
      $hasTimedOut = $true
      break
  }
  ```
- Post-timeout shutdown sequence:
  1. Sleeps 1.0 second.
  2. Calls `$editorProcess.Refresh()`.
  3. If still running, calls `$editorProcess.CloseMainWindow()`.
  4. Waits up to 10 seconds for clean exit via `WaitForExit(10000)`. If unexited, logs warning and leaves process for diagnostic recovery (no force-kill per `[X-2584]`).
  5. Enters `finally` block to verify `DefaultGame.ini` integrity before releasing locks matching the owned run token.

### 4.2 Driver Slate Callback Architecture (`pie_greystone_visual_smoke.py`)
- Callback registration:
  ```python
  HANDLE = unreal.register_slate_post_tick_callback(tick)
  ```
- Driver state machine phases:
  1. `waiting_for_pie`: Polls `UnrealEditorSubsystem.get_game_world()`. Times out after 15.0s if no world appears.
  2. `waiting_for_possession`: Starts when world is detected. Polls for `PlayerController(0).get_pawn()` matching `BP_GreystoneERPlayer_C`. Times out after 15.0s if no valid pawn is possessed. Fails immediately if `get_game_world()` becomes `None`.
  3. `observation_settle`: Observes mesh visibility, anim class, and log errors for 1.5 seconds.
  4. `finish("PASS")` / `fail(reason)`: Unregisters Slate callback, restores CVar, writes `receipt.json`.

---

## 5. Summary & Recommendation

1. **Root Cause of Run 1 Termination:**
   - The runner's 60-second timeout expired at `16:20:13.852Z`, queuing `CloseMainWindow()`.
   - PIE began at `16:20:20.200Z`, but during the subsequent 9.61s engine delta tick (Frame [ 3]), Slate processed the queued window closure, tearing down the PIE world.
   - When the driver's Slate post-tick callback executed at `16:20:29.852Z`, `get_game_world()` was `None`, resulting in `PIE game world lost while waiting for possession`.
2. **Current Source Deliverables:**
   - Runner (`FAB7A89A...`): Default timeout configured to 180s with deadline anchored at process launch.
   - Driver (`68CF485F...`): Fail-closed Slate callback and CVar restoration verified.
   - Receipt Validator (`8DBE1427...`): Fail-closed parser ready.
3. **Execution Gate:**
   - Zero tests, builds, editor launches, or PIE runs have been performed.
   - The BT-83 retry remains strictly gated on fresh Owner approval bound to the canonical runner hash (`FAB7A89A...`).
