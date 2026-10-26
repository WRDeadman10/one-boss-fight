# AG-18: Capture Driver Drafts for In-Editor Visual Evidence (Revision 03)

**Document ID:** `AG18_CAPTURE_DRAFTS` (Rev 03)  
**Author:** Antigravity (Visual & Technical Animation Investigator)  
**Parent Work Order:** `ANTIGRAVITY_WORK_ORDER_04.md` (`AG-18`), updated for `[C-151]`  
**Target Drivers:**  
- [`pie_capture_cap01_a5.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_drafts/pie_capture_cap01_a5.py) (CAP-01: A5 Javelin Release Timing)  
- [`pie_capture_cap02_a4.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_drafts/pie_capture_cap02_a4.py) (CAP-02: A4 Low Sweep Query vs Visible Blade)  
- [`pie_capture_cap05_telegraph.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_drafts/pie_capture_cap05_telegraph.py) (CAP-05: Telegraph Readability & Charge-Up Glow)  
- [`pie_capture_cap06_recovery.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_drafts/pie_capture_cap06_recovery.py) (CAP-06: Punish Windows & Recovery Openings)  
**Analysis Engine:**  
- [`capture_analysis.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_analysis.py) (Hardened against C-151 black viewports, byte-identical freezes, and zero inter-phase delta)  
**Status:** DELIVERED (Draft Scripts Only; Option B Player-Camera Framing; Zero Execution by Antigravity)  

---

## 1. Executive Summary & Operating Rules

Per `ANTIGRAVITY_WORK_ORDER_04.md:18` and technical lead review `[C-151]`, Antigravity has overhauled the capture driver suite and offline analysis pipeline.

### Camera Architecture Overhaul (Option B per C-151)
In previous revisions, spawning a separate `CameraActor` in PIE led to black-screen resolves because the pack's `PlayerCameraManager` is tightly coupled to the player pawn's spring arm and exposure/post-processing pipeline.
Under **Option B**:
1. **Zero Spawned Camera Actors:** The drivers drop `SpawnCaptureCamera` and dedicated camera actors completely.
2. **Player Pawn Repositioning:** The driver saves original player transform and control rotation, teleports the player pawn to the optimal flank vantage point facing the boss, and sets `pc.set_control_rotation(rot)`.
3. **Player Mesh Occlusion Prevention:** Calls `pawn.set_actor_hidden_in_game(True)` during the capture window. The player character model is completely invisible in the viewport, providing an unobstructed 3D view of the boss while preserving 100% of the player camera lighting, post-processing, and Lumen pipeline.
4. **Clean Restoration:** In teardown (`cleanup_camera()`), the driver unhides the player pawn (`set_actor_hidden_in_game(False)`), restores the player's original location and rotation, and restores original control rotation.

### Two-Step Automated Recipe Discipline (Per C-151 Defect 2)
1. **Driver Defers Verdict:** The Python driver validates telemetry lifecycle and logs `TELEMETRY_CAPTURE_COMPLETE (5/5 driver steps verified; awaiting offline frame analysis)`. It **never** prints `RESULT n/m PASSED`.
2. **Analysis Engine Issues Verdict:** The PowerShell run recipe immediately chains `capture_analysis.py`, which validates the captured image files on disk (resolution, size $\ge 50\text{ KB}$, inner 3D viewport luminance $\ge 8.0$, std dev $\ge 4.0$, freeze rate $\le 50\%$, and inter-phase MAD $\ge 1.5$) and prints the official pass/fail verdict.

---

## 2. Capture Driver Specifications & Two-Step Recipes

### 2.1 CAP-01: A5 Javelin Throw Release Timing (`pie_capture_cap01_a5.py`)
- **Primary Objective:** Measure the physical moment of javelin separation from the boss's hand against authored intent ($0.400\text{ s}$) vs nominal ($0.450\text{ s}$) vs first sampled ($0.470\text{ s}$) per `E-007`.
- **Target Map:** `L_SevarogArena`
- **Framing Vantage (Option B):** Player at `(-650, 150, 110)` facing boss upper body `(0, 0, 80)` (yaw $-13^\circ$, pitch $+10^\circ$), player mesh hidden.
- **Two-Step Automated Recipe:**
  ```powershell
  # Step 1: Run driver in editor to capture telemetry & trigger Win32 PrintWindow loop
  powershell -ExecutionPolicy Bypass -File Scripts/RunEditorScript.ps1 -Script Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_drafts/pie_capture_cap01_a5.py
  # Step 2: Ingest captured frames and editor log to evaluate mathematical & visual verdict
  python -I Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_analysis.py --frames-dir Saved/Screenshots/CAP01_A5 --log Saved/Logs/OneBossFight.log --cap-id CAP-01
  ```

---

### 2.2 CAP-02: A4 Low Sweep Query vs Visible Blade (`pie_capture_cap02_a4.py`)
- **Primary Objective:** Capture the visible blade trajectory across the 12 active damage ticks, verifying planar query angle alignment ($51^\circ$ to $174^\circ$ per `E-008`) and floor Z clearance ($< 38\text{ cm}$).
- **Target Map:** `L_SevarogArena`
- **Framing Vantage (Option B):** Player at `(-350, 200, 110)` facing floor sweep arc `(0, 0, 30)` (yaw $-30^\circ$, pitch $-11^\circ$), player mesh hidden.
- **Two-Step Automated Recipe:**
  ```powershell
  powershell -ExecutionPolicy Bypass -File Scripts/RunEditorScript.ps1 -Script Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_drafts/pie_capture_cap02_a4.py
  python -I Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_analysis.py --frames-dir Saved/Screenshots/CAP02_A4 --log Saved/Logs/OneBossFight.log --cap-id CAP-02
  ```

---

### 2.3 CAP-05: Attack Telegraph Readability & Glow (`pie_capture_cap05_telegraph.py`)
- **Primary Objective:** Verify that visual telegraphs (weapon glow emitter `NS_Boss01_ChargeUp`, sprint dust `NS_Boss01_Sprint_Runup`) ignite $\ge 150\text{ ms}$ before damage collision windows open.
- **Target Map:** `L_SevarogArena`
- **Framing Vantage (Option B):** Player at `(-500, 100, 110)` facing boss telegraph apex `(0, 0, 150)` (yaw $-11^\circ$, pitch $+5^\circ$), player mesh hidden.
- **Two-Step Automated Recipe:**
  ```powershell
  powershell -ExecutionPolicy Bypass -File Scripts/RunEditorScript.ps1 -Script Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_drafts/pie_capture_cap05_telegraph.py
  python -I Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_analysis.py --frames-dir Saved/Screenshots/CAP05_Telegraph --log Saved/Logs/OneBossFight.log --cap-id CAP-05
  ```

---

### 2.4 CAP-06: Boss Recovery & Punish Windows (`pie_capture_cap06_recovery.py`)
- **Primary Objective:** Capture the $800\text{ ms}$ grounded blade recovery opening following heavy attacks (A2 Slam / Leap Attack) and verify player punish attack contact before boss returns to neutral.
- **Target Map:** `L_SevarogArena`
- **Framing Vantage (Option B):** Player at `(-300, 150, 110)` facing grounded blade rest `(0, 0, 40)` (yaw $-26^\circ$, pitch $-13^\circ$), player mesh hidden.
- **Two-Step Automated Recipe:**
  ```powershell
  powershell -ExecutionPolicy Bypass -File Scripts/RunEditorScript.ps1 -Script Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_drafts/pie_capture_cap06_recovery.py
  python -I Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_analysis.py --frames-dir Saved/Screenshots/CAP06_Recovery --log Saved/Logs/OneBossFight.log --cap-id CAP-06
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

---

## 4. Deliverable File Verification (SHA256 Digests)

- `pie_capture_cap01_a5.py`: `3a5b43e21fb0d3c7d8ef738efc69f114c27f100ee8278936560e025a63ada477`
- `pie_capture_cap02_a4.py`: `05cf708166299728357e08692afd584543c2bf5792801ca459fc061fef06f720`
- `pie_capture_cap05_telegraph.py`: `d393306847f7431e685eaf3e9fe0a2232e4bfcf11c44b8a703d790f5d6682400`
- `pie_capture_cap06_recovery.py`: `4322284426dd7cb64b53c1c34791c384ee70481e9dfb4ce5a7df1cbe85b30c60`
- `capture_analysis.py`: `f8668934c224ab559bfcefa1d738071a8b9d1e4cd176b1198ee3303ffe1afe22`
