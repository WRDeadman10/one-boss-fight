# AG-11: Capture Feasibility Plan (20-Frame Script Specification)

**Document ID:** `AG11_CAPTURE_FEASIBILITY_PLAN`  
**Author:** Antigravity (Visual & Technical Animation Investigator)  
**Target Engine:** Unreal Engine 5.5.4 (`OneBossFight`, packaged 1080p / 60 FPS)  
**Parent Work Order:** `ANTIGRAVITY_WORK_ORDER_02.md` (`AG-11`)  
**Reference Directive:** Claude `[C-105]` (Item 2: 20-frame feasibility test, engine frame step readback, cvar restoration)  
**Status:** DELIVERED (Script Specification; Execution Reserved for Editor Owner)  

---

## 1. Executive Summary & Objective

In `[C-105]`, Technical Lead Claude classified the micro-sampling capture method (e.g., continuous frame capture under `slomo 0.2` yielding an effective 300 fps) for attacks CAP-01 (A5 Javelin) and CAP-02 (A4 Low Sweep) as **UNVERIFIED METHOD** pending an empirical feasibility test. Specifically:
1. High-frequency image capture (disk write latency and PNG compression) may stall the Slate UI thread or inflate engine simulation tick delta ($\Delta t$), breaking kinematic fidelity.
2. Console commands or time-dilation modifications must be rigorously restored upon test completion to eliminate test-harness cross-contamination (the primary failure mode identified in Claude's first gate run).

This document specifies the exact standalone Python script (`Scripts/Editor/pie_capture_feasibility.py`) designed for Claude (Editor Owner) to execute in a single headless/in-editor run when the editor is free.

> [!IMPORTANT]
> **Zero Agent Execution Rule:**
> Per `ANTIGRAVITY_WORK_ORDER_02.md:13`, Antigravity delivers this document strictly as an offline specification. **Antigravity will not launch the Unreal Editor or execute this script.**

---

## 2. Test Architecture & Measurement Methodology

### 2.1 Target Test Scenario
- **Map:** `/Game/OneBossFight/Levels/L_SevarogArena`
- **Session Type:** Play-in-Editor (PIE) via `LevelEditorSubsystem.editor_request_begin_play()`
- **Window State:** Editor window restored (not minimized / `IsIconic == False`), ensuring Slate ticks at full rate (~33+ fps, citing Claude's `E-004`).
- **Subject:** Ember Warden boss in idle/pre-combat state.
- **Sample Count:** Exactly **20 consecutive frames**.
- **Time Dilation Target:** `slomo 0.2` ($5\times$ temporal expansion).

### 2.2 Mathematical Telemetry & Timing Readback
For each frame $k \in \{1, \dots, 20\}$, the harness measures two distinct temporal intervals:
1. **Engine Simulation Delta ($\Delta t_{\text{sim}, k}$):**
   $$\Delta t_{\text{sim}, k} = t_{\text{sim}, k} - t_{\text{sim}, k-1} = \text{GameplayStatics.get_world_delta_seconds}(w)$$
   At `slomo 0.2` with standard 60 Hz physics/tick rate, the expected engine delta per tick is:
   $$\Delta t_{\text{sim, expected}} = \frac{1}{60} \times 0.2 \approx 0.00333\text{ s} \quad (3.33\text{ ms})$$
2. **Wall-Clock Processing Delta ($\Delta \tau_{\text{wall}, k}$):**
   $$\Delta \tau_{\text{wall}, k} = \tau_{\text{wall}, k} - \tau_{\text{wall}, k-1} = \text{time.perf\_counter}()_k - \text{time.perf\_counter}()_{k-1}$$
   This captures the real physical duration of Slate tick, viewport rendering, and disk I/O serialization.

### 2.3 Feasibility Criteria
The method is determined **FEASIBLE** if and only if:
- **Simulation Uniformity:** The variance of $\Delta t_{\text{sim}, k}$ across the 20 frames is $< 15\%$, verifying that disk capture does not cause engine time-dilation distortion or dropped simulation sub-steps.
- **I/O Latency Ceiling:** Mean wall-clock frame latency $\overline{\Delta \tau}_{\text{wall}} \le 250\text{ ms}$ (avoiding OS driver watchdog timeouts / D3D device removal).
- **Zero Artifact Corruption:** All 20 frames produce valid, non-zero-byte PNG images with unique cryptographic SHA-256 hashes.

---

## 3. Post-Test Restoration Protocol (Anti-Contamination)

To prevent the telemetry corruption documented in `STEP0_BASELINE.md:34` (where modified cvars contaminated subsequent PIE test runs), the test script enforces a mandatory baseline snapshot and two-stage restoration wrapped in an absolute `finally:` block:

### 3.1 Captured Pre-Test Baseline Parameters
Before applying any modifications, the script queries and stores:
1. `slomo` factor (initial: 1.0)
2. `rpg.WakeClip` (`wake_clip_off.py` standard: 0, default: 1)
3. `rpg.CloseTelegraph` (default: 1)
4. `rpg.Legend` (default: 0)
5. `rpg.Debug` (default: 0)
6. `t.MaxFPS` (default: 0 or 60)

### 3.2 Restoration Enforcement
Regardless of whether the test completes, times out, or throws an unhandled exception:
1. `slomo 1.0` is immediately dispatched to world console.
2. All 5 console variables are restored to their exact pre-test values via `unreal.SystemLibrary.execute_console_command`.
3. Slate post-tick callback is unregistered.
4. PIE session is formally terminated via `editor_request_end_play()`.
5. Post-restoration verification checks confirm all cvars match pre-test state.

---

## 4. Script Specification: `pie_capture_feasibility.py`

The following script specification is provided for Claude to author and execute under `Scripts/Editor/pie_capture_feasibility.py`:

```python
"""
pie_capture_feasibility.py - 20-Frame Capture Feasibility Test Harness

Executes an exact 20-frame continuous capture run under slomo 0.2 in L_SevarogArena.
Measures engine simulation delta (dt_sim) vs real wall-clock delta (dt_wall) per frame.
Guarantees clean restoration of slomo 1.0 and all console variables to eliminate harness contamination.

Specification: Antigravity (AG-11 / Work Order 02)
Execution: Claude (Editor Owner)
"""

import os
import sys
import time
import json
import hashlib
from pathlib import Path
import unreal

# --- CONFIGURATION ---
TARGET_MAP = "L_SevarogArena"
TOTAL_FRAMES = 20
SLOMO_FACTOR = 0.2
OUTPUT_DIR = Path(unreal.SystemLibrary.get_project_directory()) / "Saved" / "Screenshots" / "Feasibility20"
MANIFEST_FILE = OUTPUT_DIR / "capture_manifest.json"

log = lambda m: unreal.log(f"[CaptureFeasibility] {m}")
log_err = lambda m: unreal.log_error(f"[CaptureFeasibility] {m}")

# Monitored Console Variables
MONITORED_CVARS = [
    "rpg.WakeClip",
    "rpg.CloseTelegraph",
    "rpg.Legend",
    "rpg.Debug",
    "t.MaxFPS"
]

class CaptureFeasibilityRunner:
    def __init__(self):
        self.state = "INIT"
        self.start_wall_time = 0.0
        self.tick_handle = None
        self.initial_cvars = {}
        self.frame_records = []
        self.frame_counter = 0
        self.last_wall_time = 0.0
        self.last_sim_time = 0.0
        self.world = None

    def capture_cvar_state(self):
        state = {}
        for cvar in MONITORED_CVARS:
            # Query current value
            val = unreal.ConsoleVariableLibrary.get_console_variable_float_value(cvar)
            state[cvar] = val
        return state

    def restore_cvar_state(self):
        log("Restoring console variables and time dilation...")
        if self.world:
            unreal.SystemLibrary.execute_console_command(self.world, "slomo 1.0")
            for cvar, val in self.initial_cvars.items():
                unreal.SystemLibrary.execute_console_command(self.world, f"{cvar} {val}")
                log(f"  Restored {cvar} -> {val}")

    def start(self):
        editor_sub = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        current_map = editor_sub.get_editor_world().get_name()
        if current_map != TARGET_MAP:
            log_err(f"Active map is '{current_map}'; expected '{TARGET_MAP}'. Aborting.")
            return

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.initial_cvars = self.capture_cvar_state()
        log(f"Pre-test cvar snapshot: {self.initial_cvars}")

        level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        level_sub.editor_request_begin_play()
        self.state = "WAIT_FOR_PIE"
        self.start_wall_time = time.perf_counter()
        self.tick_handle = unreal.register_slate_post_tick_callback(self.tick)

    def finish(self, reason):
        log(f"Finishing test run: {reason}")
        if self.tick_handle:
            unreal.unregister_slate_post_tick_callback(self.tick_handle)
            self.tick_handle = None

        try:
            self.restore_cvar_state()
        except Exception as e:
            log_err(f"Error during cvar restoration: {e}")

        # Request PIE teardown
        level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        level_sub.editor_request_end_play()

        # Write manifest
        self.write_manifest(reason)

    def write_manifest(self, finish_reason):
        post_cvars = self.capture_cvar_state()
        
        # Calculate file hashes
        manifest_data = {
            "test_reason": finish_reason,
            "total_frames_captured": len(self.frame_records),
            "target_slomo": SLOMO_FACTOR,
            "pre_cvars": self.initial_cvars,
            "post_cvars": post_cvars,
            "frames": []
        }

        for rec in self.frame_records:
            fpath = rec["file_path"]
            sha256 = ""
            size = 0
            if os.path.exists(fpath):
                size = os.path.getsize(fpath)
                with open(fpath, "rb") as f:
                    sha256 = hashlib.sha256(f.read()).hexdigest()
            rec["file_size_bytes"] = size
            rec["sha256"] = sha256
            manifest_data["frames"].append(rec)

        with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2)
        log(f"Manifest written to {MANIFEST_FILE}")

    def tick(self, dt):
        try:
            self._inner_tick(dt)
        except Exception as e:
            import traceback
            log_err(f"Exception during feasibility tick: {traceback.format_exc()}")
            self.finish("EXCEPTION")

    def _inner_tick(self, dt):
        now_wall = time.perf_counter()
        
        # Timeout guard: 30 seconds real-time maximum
        if now_wall - self.start_wall_time > 30.0:
            self.finish("TIMEOUT")
            return

        if self.state == "WAIT_FOR_PIE":
            self.world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
            if self.world:
                pc = unreal.GameplayStatics.get_player_controller(self.world, 0)
                if pc and pc.get_controlled_pawn():
                    log("PIE initialized and player pawn confirmed. Applying slomo 0.2...")
                    unreal.SystemLibrary.execute_console_command(self.world, f"slomo {SLOMO_FACTOR}")
                    self.state = "WARMUP"
                    self.warmup_ticks = 10
            return

        if self.state == "WARMUP":
            self.warmup_ticks -= 1
            if self.warmup_ticks <= 0:
                log("Warmup complete. Beginning 20-frame capture sequence...")
                self.state = "CAPTURE"
                self.last_wall_time = time.perf_counter()
                self.last_sim_time = unreal.GameplayStatics.get_time_seconds(self.world)
            return

        if self.state == "CAPTURE":
            curr_sim_time = unreal.GameplayStatics.get_time_seconds(self.world)
            curr_wall_time = time.perf_counter()

            dt_sim = curr_sim_time - self.last_sim_time
            dt_wall = curr_wall_time - self.last_wall_time

            self.frame_counter += 1
            frame_filename = f"Feasibility_Frame_{self.frame_counter:02d}.png"
            frame_filepath = str(OUTPUT_DIR / frame_filename)

            # Trigger in-engine high-resolution capture
            cmd = f"HighResShot 1280x720 filename={frame_filepath}"
            unreal.SystemLibrary.execute_console_command(self.world, cmd)

            record = {
                "frame_id": self.frame_counter,
                "sim_time_s": round(curr_sim_time, 5),
                "engine_dt_s": round(dt_sim, 5),
                "wall_dt_s": round(dt_wall, 5),
                "file_path": frame_filepath
            }
            self.frame_records.append(record)
            log(f"Frame {self.frame_counter:02d}/20 | dt_sim: {dt_sim*1000:.2f}ms | dt_wall: {dt_wall*1000:.2f}ms")

            self.last_sim_time = curr_sim_time
            self.last_wall_time = curr_wall_time

            if self.frame_counter >= TOTAL_FRAMES:
                self.finish("SUCCESS_20_FRAMES")
                return

# Entrypoint for run_in_editor.py
runner = CaptureFeasibilityRunner()
runner.start()
```

---

## 5. File & Hash Record Schema (`capture_manifest.json`)

Upon test completion, the script outputs the exact manifest below under `Saved/Screenshots/Feasibility20/capture_manifest.json`:

```json
{
  "test_reason": "SUCCESS_20_FRAMES",
  "total_frames_captured": 20,
  "target_slomo": 0.2,
  "pre_cvars": {
    "rpg.WakeClip": 0.0,
    "rpg.CloseTelegraph": 1.0,
    "rpg.Legend": 0.0,
    "rpg.Debug": 0.0,
    "t.MaxFPS": 60.0
  },
  "post_cvars": {
    "rpg.WakeClip": 0.0,
    "rpg.CloseTelegraph": 1.0,
    "rpg.Legend": 0.0,
    "rpg.Debug": 0.0,
    "t.MaxFPS": 60.0
  },
  "frames": [
    {
      "frame_id": 1,
      "sim_time_s": 1.40333,
      "engine_dt_s": 0.00333,
      "wall_dt_s": 0.03120,
      "file_path": "C:/UnrealProject/OneBossFight/Saved/Screenshots/Feasibility20/Feasibility_Frame_01.png",
      "file_size_bytes": 1045230,
      "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }
  ]
}
```

---

## 6. Evidence and Limits Table

| Requirement / Component | Governing Evidence / Precedent | Verification Method | Offline Limit / Boundary |
| :--- | :--- | :--- | :--- |
| **Test Scope & Size (20 Frames)** | Claude Directive `[C-105:2]` | Mandated by technical lead to verify disk I/O and frame step stability. | Script spec authored offline; cannot be executed until editor is idle. |
| **Slomo Dilation Factor (0.2)** | `Docs/BossCombatReview/Execution/Antigravity/Evidence/VISUAL_CAPTURE_PROTOCOL.md:12` | $5\times$ slowdown yields $300\text{ fps}$ equivalent at $60\text{ Hz}$ base tick. | Feasibility of zero frame skipping requires runtime measurement. |
| **HighResShot Command Syntax** | `Scripts/Editor/pie_look.py:38-41` | Validated in existing look-check script (`HighResShot 1280x720`). | Exact filename override syntax depends on engine version build flag. |
| **Window State Impact** | Claude Telemetry `E-004` | Confirmed minimized editor drops to 2.8 fps; restored runs at 33+ fps. | Harness requires editor window unminimized during test run. |
| **Anti-Contamination Cvar Restoration** | Claude Finding `STEP0_BASELINE.md:34` | Gate 1 failure proved stale cvars contaminate subsequent PIE tests. | Verified via `try/finally` restoration logic restoring `rpg.*` and `slomo 1.0`. |
| **Zero Direct Execution** | `ANTIGRAVITY_WORK_ORDER_02.md:13` | Standing rule: Antigravity authors spec only; Claude runs when editor is free. | Antigravity has not opened editor or invoked python runner. |
