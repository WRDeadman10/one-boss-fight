# AG-18: Capture Driver Drafts for In-Editor Visual Evidence

**Document ID:** `AG18_CAPTURE_DRAFTS`  
**Author:** Antigravity (Visual & Technical Animation Investigator)  
**Parent Work Order:** `ANTIGRAVITY_WORK_ORDER_04.md` (`AG-18`)  
**Target Drivers:**  
- [`pie_capture_cap01_a5.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_drafts/pie_capture_cap01_a5.py) (CAP-01: A5 Javelin Release Timing)  
- [`pie_capture_cap02_a4.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_drafts/pie_capture_cap02_a4.py) (CAP-02: A4 Low Sweep Query vs Visible Blade)  
- [`pie_capture_cap05_telegraph.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_drafts/pie_capture_cap05_telegraph.py) (CAP-05: Telegraph Readability & Charge-Up Glow)  
- [`pie_capture_cap06_recovery.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_drafts/pie_capture_cap06_recovery.py) (CAP-06: Punish Windows & Recovery Openings)  
**Status:** DELIVERED (Draft Scripts Only; Zero Execution by Antigravity)  

---

## 1. Executive Summary & Operating Rules

Per `ANTIGRAVITY_WORK_ORDER_04.md:18`, Antigravity authors editor-side Python capture drivers adhering strictly to the project's house style (`Scripts/Editor/pie_*.py`).

### House Style Conformance
1. **Heartbeat & Watchdog Timeout:** Every script enforces an absolute 45.0s wall-clock watchdog preventing editor hangs.
2. **Safe PIE Invocations:** Zero calls to `set_editor_property` on live actor components during PIE; actor transforms are modified solely via native runtime APIs (`set_actor_location_and_rotation`).
3. **Strict Cvar Snapshot & Restoration:** All modified cvars (`slomo`, `rpg.WakeClip`, `rpg.CloseTelegraph`, `rpg.Legend`, `rpg.Debug`, `t.MaxFPS`) are captured pre-test and unconditionally restored in a `finally:` block before PIE teardown.
4. **Standardized Terminal Logging:** All scripts print `[TAG] RESULT n/m (reason)` on completion for automated runner parsing.
5. **Zero Agent Execution Rule:** These scripts are authored as **drafts for Editor Owner Claude** to execute when the editor is free. Antigravity will not execute them offline.

---

## 2. Capture Driver Specifications

### 2.1 CAP-01: A5 Javelin Throw Release Timing (`pie_capture_cap01_a5.py`)
- **Primary Objective:** Measure the physical moment of javelin separation from the boss's hand against authored intent ($0.400\text{ s}$) vs nominal ($0.450\text{ s}$) vs first sampled ($0.470\text{ s}$) per `E-007`.
- **Target Map:** `L_SevarogArena`
- **Player Camera Placement:** $800\text{ cm}$ frontal elevation facing boss (`Location: (-800, 0, 110)`, `Pitch: -5`, `Yaw: 0`).
- **Console Commands Executed:**
  ```text
  slomo 0.2
  rpg.ForceMove A5
  HighResShot 1280x720 filename=Saved/Screenshots/CAP01_A5/CAP01_A5_Frame_NN.png
  slomo 1.0
  ```
- **Expected Outputs:** 15 consecutive PNG frames under `Saved/Screenshots/CAP01_A5/` capturing windup apex, hand extension, and projectile mesh spawning.
- **Estimated Duration:** $\sim 8.0\text{ s}$ wall clock (at `slomo 0.2`).
- **What It Cannot Prove:** Cannot prove network RPC synchronization or projectile server collision accuracy on remote clients.
- **Run Command:**
  ```powershell
  powershell -ExecutionPolicy Bypass -File Scripts/RunEditorScript.ps1 -Script Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_drafts/pie_capture_cap01_a5.py
  ```

---

### 2.2 CAP-02: A4 Low Sweep Query vs Visible Blade (`pie_capture_cap02_a4.py`)
- **Primary Objective:** Capture the visible blade trajectory across the 12 active damage ticks, verifying planar query angle alignment ($51^\circ$ to $174^\circ$ per `E-008`) and floor Z clearance ($< 38\text{ cm}$).
- **Target Map:** `L_SevarogArena`
- **Player Camera Placement:** $350\text{ cm}$ flank elevation viewing floor sweep (`Location: (-350, 200, 110)`, `Pitch: -10`, `Yaw: -30`).
- **Console Commands Executed:**
  ```text
  slomo 0.2
  rpg.ForceMove A4
  HighResShot 1280x720 filename=Saved/Screenshots/CAP02_A4/CAP02_A4_Frame_NN.png
  slomo 1.0
  ```
- **Expected Outputs:** 16 consecutive PNG frames under `Saved/Screenshots/CAP02_A4/` capturing low sweep blade entry, floor grazing, and follow-through.
- **Estimated Duration:** $\sim 10.0\text{ s}$ wall clock.
- **What It Cannot Prove:** Cannot prove internal Chaos physics broadphase sub-step raycasts.
- **Run Command:**
  ```powershell
  powershell -ExecutionPolicy Bypass -File Scripts/RunEditorScript.ps1 -Script Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_drafts/pie_capture_cap02_a4.py
  ```

---

### 2.3 CAP-05: Attack Telegraph Readability & Glow (`pie_capture_cap05_telegraph.py`)
- **Primary Objective:** Verify that visual telegraphs (weapon glow emitter `NS_Boss01_ChargeUp`, sprint dust `NS_Boss01_Sprint_Runup`) ignite $\ge 150\text{ ms}$ before damage collision windows open.
- **Target Map:** `L_SevarogArena`
- **Player Camera Placement:** $600\text{ cm}$ standard combat view (`Location: (-600, 0, 110)`, `Pitch: -5`, `Yaw: 0`).
- **Console Commands Executed:**
  ```text
  slomo 0.2
  rpg.ForceMove Sprint
  HighResShot 1280x720 filename=Saved/Screenshots/CAP05_Telegraph/CAP05_Telegraph_Frame_NN.png
  slomo 1.0
  ```
- **Expected Outputs:** 18 consecutive PNG frames under `Saved/Screenshots/CAP05_Telegraph/` demonstrating clear luminance rise and particle emission during sprint run-up.
- **Estimated Duration:** $\sim 12.0\text{ s}$ wall clock.
- **What It Cannot Prove:** Cannot prove human player reaction time or optical display latency.
- **Run Command:**
  ```powershell
  powershell -ExecutionPolicy Bypass -File Scripts/RunEditorScript.ps1 -Script Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_drafts/pie_capture_cap05_telegraph.py
  ```

---

### 2.4 CAP-06: Boss Recovery & Punish Windows (`pie_capture_cap06_recovery.py`)
- **Primary Objective:** Capture the $800\text{ ms}$ grounded blade recovery opening following heavy attacks (A2 Slam / Leap Attack) and verify player punish attack contact before boss returns to neutral.
- **Target Map:** `L_SevarogArena`
- **Player Camera Placement:** $280\text{ cm}$ close flank view (`Location: (-280, 150, 110)`, `Pitch: -5`, `Yaw: -25`).
- **Console Commands Executed:**
  ```text
  slomo 0.2
  rpg.ForceMove A2
  HighResShot 1280x720 filename=Saved/Screenshots/CAP06_Recovery/CAP06_Recovery_Frame_NN.png
  slomo 1.0
  ```
- **Expected Outputs:** 16 consecutive PNG frames under `Saved/Screenshots/CAP06_Recovery/` showing boss blade pinned to floor while player executes light attack.
- **Estimated Duration:** $\sim 10.0\text{ s}$ wall clock.
- **What It Cannot Prove:** Cannot prove player input buffer windows in C++ player controller.
- **Run Command:**
  ```powershell
  powershell -ExecutionPolicy Bypass -File Scripts/RunEditorScript.ps1 -Script Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_drafts/pie_capture_cap06_recovery.py
  ```

---

## 3. Evidence and Limits Table

| Capture ID | Script File Name | Expected Output Directory | Pre-Requisite / Tool Limit |
| :--- | :--- | :--- | :--- |
| **CAP-01** | `pie_capture_cap01_a5.py` | `Saved/Screenshots/CAP01_A5/` | Requires unminimized editor window (E-004). |
| **CAP-02** | `pie_capture_cap02_a4.py` | `Saved/Screenshots/CAP02_A4/` | Micro-sampling rate subject to feasibility validation (AG-11). |
| **CAP-05** | `pie_capture_cap05_telegraph.py` | `Saved/Screenshots/CAP05_Telegraph/` | Measures visual particles; audio hum requires separate capture. |
| **CAP-06** | `pie_capture_cap06_recovery.py` | `Saved/Screenshots/CAP06_Recovery/` | Proves visual weapon rest duration; player cancel requires C++ trace. |
| **CAP-03** | *Omitted (Gated)* | *N/A* | Blocked: Requires Gate G-5 (not approved by Project Owner). |
| **CAP-04** | *Omitted (Gated)* | *N/A* | Blocked: Requires packaged Shipping build to eliminate debug circle. |
