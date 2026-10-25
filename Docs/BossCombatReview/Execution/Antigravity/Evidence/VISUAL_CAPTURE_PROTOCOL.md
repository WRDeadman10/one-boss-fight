# Visual Capture Protocol: CAP-01 through CAP-06 Runtime Evidence Standard

**Document ID:** `VISUAL_CAPTURE_PROTOCOL` (Revision 02)  
**Date:** 2026-10-25  
**Author:** Antigravity (Accountable Visual & Technical Animation Investigator)  
**Reviewers:** Claude (Technical Lead & Editor Owner), Codex GPT-6 Astra (Technical Reviewer & Data Architect)  
**Governance & Gate Status:** Ready for execution pending editor availability and owner tool approvals. Strictly conforms to owner gate decisions (`DATA_DRIVEN_ARCHITECTURE_GATE.md` Section 0: G-4 NOT approved, G-5 NOT approved; no unauthorized editor sessions).  
**Revision History:**
- **Revision 01 (2026-10-25):** Initial comprehensive protocol draft submitted in `A-52`.
- **Revision 02 (2026-10-25):** Updated per Claude's technical review `[C-105]`:
  1. *CAP-04 Correction:* Identified that `RPGBossShockwave.cpp:164-166` executes `DrawDebugCircle` directly under `#if !UE_BUILD_SHIPPING` without any `rpg.Debug` guard. A debug-off view is impossible in the editor or Development builds; marked CAP-04 as **BLOCKED until a packaged Shipping build is created** (`Scripts/Package.ps1 -Configuration Shipping`), noting Development captures can only show the debug-on reference.
  2. *Sampling Rate Feasibility:* Marked the proposed `slomo 0.2` micro-sampling rate for CAP-01 and CAP-02 as **UNVERIFIED METHOD** pending a 20-frame feasibility test by Claude when the editor is free (evaluating per-frame capture overhead, frame-step stability, and clean `slomo 1` restoration).
  3. *Nomenclature & Window State Facts:* Replaced "Greystone capsule" with the active player capsule of the pack mannequin (the boss is the Ember Warden on the pack boss; Greystone is a retired character asset). Corrected window state notes to state only measured facts from E-004 (minimized window `IsIconic == true` ticked at ~2.8 fps; restored window ticked at ~33 fps), withdrawing speculative claims regarding OS/DWM clamping mechanisms.

---

## 1. Executive Summary & Epistemological Boundaries

This protocol establishes the exact, reproducible in-engine capture specification for all visual evidence requirements (`CAP-01` through `CAP-06`) defined in `CAPTURE_NEEDS.md`. It provides the technical framework for the day editor sessions are scheduled or capture tools are approved.

### 1.1 What Visual Captures CAN Show
1. **Spatial Mesh Alignment:** Exact spatial relationship between rendered skeletal meshes (`SKM_Boss01`), weapon meshes (`SM_Boss01_Greatsword`), and camera frustums at specific montage timestamps.
2. **Overlay vs Geometry Correspondence:** Visual overlay congruence (or divergence) between production debug queries (`DrawDebugCircle`, `ANS_CollisionTrace` line sweeps, `ShowDebug COLLISION`) and rasterized weapon pixels.
3. **Temporal Visual Milestones:** Precise engine video frame indices for visual milestones, such as hand-release poses, weapon apex pauses, or particle instantiation.
4. **Perceptual & Aesthetic Artifacts:** Observable clipping with the environment (e.g., blade penetrating arena stone flooring), rotational popping, and foot sliding/skating during high-rate tracking yaw ($360^\circ/\text{s}$).
5. **Shipping Visibility:** Presence or total absence of rendered Niagara particle effects, decals, or material rings when development debug drawing is stripped in packaged Shipping builds (`#if !UE_BUILD_SHIPPING`).

### 1.2 What Visual Captures CANNOT Show
1. **Physical Contact / Damage Registration:** A screenshot or rasterized video frame **does not measure contact**. In Unreal Engine, collision resolution is strictly mathematical, evaluated via PhysX/Chaos primitives (`RPGBossMath::SweepTouches`, `SweepMultiByChannel`, ASC Gameplay Effects) during the engine tick. Pixel overlap in screen-space does not constitute a gameplay hit.
2. **Sub-Frame Trajectory Extrema:** Discrete frame sampling samples discrete poses; mathematical continuous sweep queries may detect overlaps between sampled visual frames.
3. **Internal Logic / Cancellation Call Stacks:** Visual captures document the *manifestation* of motion interruptions or state transitions, but cannot prove the *originating caller* (e.g., whether `Montage_Stop` was triggered by an animation notify, a state tree condition, an ability cancellation, or a gameplay tag removal).
4. **Authoritative Hit Consensus:** Standalone captures do not establish client-server replication authority (QA-008).

---

## 2. Global Execution Environment & Reproducibility Standard

### 2.1 Cvar Baseline State
Before recording any capture sequence, the following console variables must be explicitly initialized via `probes/p0_set_cvars.py`:
- `rpg.WakeClip 0` (suppresses the wake clip animation to ensure repeatable trial start poses)
- `rpg.CloseTelegraph 0` (suppresses auxiliary combat telegraph overlays to prevent visual clutter)
- `rpg.Legend 0` (suppresses on-screen debug legend text from occluding characters)
- `rpg.Debug 1` (enabled for debug query overlay captures; note that native debug primitives guarded solely by `#if !UE_BUILD_SHIPPING` remain active in Development regardless of this cvar)

### 2.2 Window & Viewport State
- **Window State:** Restored editor window (`WinShot` / OS window handle restored). **Never minimized or occluded**.
  > [!NOTE]
  > Measured baseline fact from Claude's E-004: When the Unreal Editor window was minimized (`IsIconic == true`), PIE ticked at approximately $2.8\text{ fps}$; upon restoring the window, PIE ticked at approximately $33\text{ fps}$. Restoring the window is strictly required for stable engine tick rates. Any attribution to specific OS Desktop Window Manager (DWM) scheduling mechanics is treated as an unverified hypothesis.
- **Viewport Resolution:** Strictly `1920 x 1080` (1080p, matching target packaged resolution and G4 runbook standards).
- **Aspect Ratio:** 16:9.
- **Color Space:** 24-bit RGB / sRGB, Gamma 2.2.
- **Camera Aspect Clamping:** Locked to viewport (no letterboxing or variable aspect ratios).

### 2.3 Temporal Sampling Rates & Feasibility Status
- **Nominal Real-Time Captures:** $60.0\text{ fps}$ fixed frame rate (`t.MaxFPS 60`).
- **High-Precision Micro-Timing Captures (`slomo 0.2`):**
  > [!WARNING]
  > **STATUS: UNVERIFIED METHOD.** The project currently possesses tools for single-frame captures (`Scripts/shot.sh`, `Scripts/Editor/pie_look.py` using `HighResShot`, and `Scripts/CaptureWindow.ps1` using `PrintWindow`), but does not have a verified continuous frame-by-frame capture pipeline under `slomo`. Executing continuous frame captures at `slomo 0.2` (nominal $300\text{ fps}$ effective) requires an empirical **20-frame feasibility test** by Claude when the editor is free to evaluate:
  > 1. Per-frame screenshot latency and disk write overhead.
  > 2. Stability of the engine delta time and tick progression.
  > 3. Clean and guaranteed restoration of `slomo 1.0` and all modified cvars after capture, preventing test environment contamination.

### 2.4 Weapon Geometry & Coordinate Baseline (Authoring Contract Rev 03 & Claude E-008)
- **Actor:** The boss is the **Ember Warden** (built on the pack boss).
- **Target Dummy / Player:** The player capsule is the **pack mannequin's capsule** ($R \approx 34\text{--}42\text{ cm}$; Greystone is a retired character asset).
- **Mesh:** `SM_Boss01_Greatsword` attached to component `RPGLookSword`.
- **Component World Scale:** `1.50` (authored blade extent $163.30\text{ cm} \implies$ physical blade length $+244.95\text{ cm}$ along the local blade axis).
- **Socket Reality:** Confirmed **0 engine sockets** at runtime (`KI-070` holds; tested socket names `SOCKET_Weapon_Start`, `SOCKET_Weapon_End`, `BladeStart`, `BladeEnd`, `SOCKET_TrailEndSocket` return false).
- **Blade Trajectory Indicator:** All visual blade overlays must transform the local physical tip coordinate $(0, 0, +163.30\text{ cm})$ by the component's world transform matrix.

---

## 3. Capture-by-Capture Detailed Specifications

```
+--------+------------------------------------+--------------------------------+-----------------------+
| ID     | Target Move & Objective            | Tool Dependency & Status       | Primary Framing       |
+--------+------------------------------------+--------------------------------+-----------------------+
| CAP-01 | A5 Javelin Release vs Spawn Sync   | READY (Rate: UNVERIFIED METHOD)| Left Flank Profile    |
| CAP-02 | A4 Low Sweep Query vs Blade Tip    | READY (Rate: UNVERIFIED METHOD)| Top-Down 3/4 Iso      |
| CAP-03 | Untracked Pack Abilities Motion    | BLOCKED (Requires G-5)         | Medium Duel Combat    |
| CAP-04 | A6 Shockwave Expanding Ring Visual | BLOCKED (Requires Shipping)    | Wide Arena Overhead   |
| CAP-05 | A2 Slam Live Twirl vs Poise Hold   | READY (Visuals do not need G-4)| Front-Quarter Duel    |
| CAP-06 | Windup Yaw Tracking vs Foot Slip   | READY                          | Low-Angle Boot/Floor  |
+--------+------------------------------------+--------------------------------+-----------------------+
```

---

### CAP-01: A5 Gauntlet Ember Javelin Visual Release vs Actor Spawn Synchronization

- **Target Move:** A5 (Gauntlet Ember Javelin Throw / `RPGBossHealPunish` / `AN_Boss01_A5_JavelinThrow`).
- **Objective:** Measure the exact temporal offset between the authored visual hand-release pose (authored at $0.400\text{ s}$ / Frame 12) and the live engine projectile instantiation (`ARPGBossJavelin` spawned at tracker active window $0.450\text{ s}$, observed at $0.470\text{ s}$ in E-007).
- **Gate Dependency:** **NO G-4/G-5 NEEDED (READY)**. Executed via existing driver `Scripts/Editor/pie_a5_heal_punish.py` (which triggers boss heal punish reaction via `IA_UseTool`).
- **Camera Setup:**
  - **Type:** Orthogonal or low-distortion telephoto profile camera.
  - **World Location:** Local boss offset `(-120.0, -280.0, 220.0)` cm (with boss at `(0, 0, 146.0)`, camera placed at `(-120.0, -280.0, 366.0)`).
  - **Rotation:** Pitch $-12.0^\circ$, Yaw $+65.0^\circ$, Roll $0.0^\circ$.
  - **Focal Distance:** $320.0\text{ cm}$, framing dorsal brazier, upper torso, and left arm throw arc.
  - **Field of View (FOV):** $45.0^\circ$ ($50\text{ mm}$ focal length equivalent).
- **Temporal Resolution:** Target `slomo 0.2` at $60.0\text{ fps}$ (effective $300\text{ fps}$, marked **UNVERIFIED METHOD** pending feasibility test) from montage local time $0.300\text{ s}$ to $0.550\text{ s}$.
- **Overlay Content:**
  1. Engine HUD timestamp, frame index, and montage local playback position.
  2. Projectile actor (`ARPGBossJavelin`) origin crosshair and bounding sphere upon instantiation.
  3. Left gauntlet bone proxy indicator (`hand_l` / brazier socket point).
- **Epistemological Scope:**
  - **CAN SHOW:** Visible frame index of hand fingers releasing the javelin vs the exact frame index where the javelin actor appears in the world.
  - **CANNOT SHOW:** Javelin flight damage trajectory, collision sweep hit against player capsule, or player stagger reaction.

---

### CAP-02: A4 Ground Low Sweep Production Query vs Blade Tip & Capsule

- **Target Move:** A4 (Ground Low Sweep / `RPGBossLowSweep` / `AN_Boss01_A4_LowSweep`).
- **Objective:** Document the physical discrepancy between the production planar query sector (Reach $380.0\text{ cm}$, Inner Radius $60.0\text{ cm}$, Height $40.0\text{ cm}$, $+90^\circ$ to $-90^\circ$ sweep) and the visible greatsword tip ($+163.3\text{ cm}$ local, $1.5\text{x}$ scale, maximum sampled reach $312.0\text{ cm}$ in E-008), plus visual floor clipping.
- **Gate Dependency:** **NO G-4/G-5 NEEDED (READY)**. Executed via existing probe `probes/p0_a4_geometry.py` using `URPGBossLowSweep.StartForTest(true)`.
- **Camera Setup:**
  - **Type:** Elevated 3/4 Isometric Perspective.
  - **World Location:** `(-350.0, -350.0, 480.0)` cm looking down toward boss root `(0, 0, 146.0)`.
  - **Rotation:** Pitch $-35.0^\circ$, Yaw $+45.0^\circ$, Roll $0.0^\circ$.
  - **Focal Distance:** $620.0\text{ cm}$, encompassing the entire $380.0\text{ cm}$ sweep radius and pack mannequin player capsule parked at $250.0\text{ cm}$ and $380.0\text{ cm}$.
  - **Field of View (FOV):** $55.0^\circ$.
- **Temporal Resolution:** Target `slomo 0.2` at $60.0\text{ fps}$ (effective $300\text{ fps}$, marked **UNVERIFIED METHOD** pending feasibility test) through active window montage $0.550\text{ s}$ to $0.950\text{ s}$.
- **Overlay Content:**
  1. `RPGBossMath::SweepTouches` planar sector boundary lines (`DrawDebugCircle` / sectoral sweep cone lines in red/yellow).
  2. Visible blade tip trajectory line (computed endpoint transformed from local $(0,0,163.3)$ at $1.5\text{x}$ scale) in cyan.
  3. Pack mannequin player collision capsule wireframe (`ShowDebug COLLISION`).
  4. Arena floor plane reference grid ($Z = 0.0$ / ground stone level).
- **Epistemological Scope:**
  - **CAN SHOW:** The $\ge 68.0\text{ cm}$ spatial gap where the query reaches beyond the visible blade tip; the $51^\circ\text{ to }174^\circ$ angular lag between query angle and blade angle; visible blade intersection with the arena floor geometry.
  - **CANNOT SHOW:** Mathematical penetration calculation inside `RPGBossMath::SweepTouches`; dynamic jump invulnerability evaluation.

---

### CAP-03: Untracked Pack Abilities Motion & Visual Presentation

- **Target Moves:**
  1. `MidRange`: `Mid01_Anim_Montage` (`GA_GS_Boss_MidRangeAttack`)
  2. `Sprint`: `GS_SprintAttackFollowUp_Montage` (`GA_GS_Boss_SprintAttack`)
  3. `Retaliation`: `RetaliationAttack_Montage`
- **Objective:** Evaluate animation windup readability, weapon trace coverage relative to the blade mesh, and visual hit-stun immunity cues.
- **Gate Dependency:** **REQUIRES G-5 (BLOCKED FOR AUTOMATED EXECUTION)**.
  > [!IMPORTANT]
  > Gate G-5 ("Allow a Development-only test hook that can start the three pack moves Mid01, sprint, retaliation on demand") was **NOT APPROVED** by the project owner in `DATA_DRIVEN_ARCHITECTURE_GATE.md`.
  > Therefore, automated on-demand scripted capture of CAP-03 is **BLOCKED**.
  > **Authorized Fallback:** Captures can only be acquired via natural bot combat observation or manual interactive PIE duel recording when these abilities are naturally selected by the Behavior Tree.
- **Camera Setup:**
  - **Type:** Medium Combat Framing / Chase Camera.
  - **World Location:** Relative offset `(350.0, 400.0, 220.0)` cm from combat engagement midpoint.
  - **Rotation:** Pitch $-15.0^\circ$, Yaw $-130.0^\circ$, Roll $0.0^\circ$.
  - **Focal Distance:** $550.0\text{ cm}$, framing both Boss and Player across $200\text{--}800\text{ cm}$ separation.
  - **Field of View (FOV):** $65.0^\circ$.
- **Temporal Resolution:** $60.0\text{ fps}$ real-time capture.
- **Overlay Content:**
  1. Live montage notify names and active damage window markers (`ANS_CollisionTrace_C`).
  2. Active weapon trace sweep lines rendered by `ANS_CollisionTrace`.
- **Epistemological Scope:**
  - **CAN SHOW:** Motion clarity, telegraph visibility, and weapon trace sweep alignment against the visible mesh.
  - **CANNOT SHOW:** Behavior tree selection scoring, priority tree evaluation, or AI target selection logic.

---

### CAP-04: A6 Shockwave Expanding Ring (Debug-Off Observation)

- **Target Move:** A6 (Phase 2 Leap Slam / `RPGBossShockwave` / `AN_Boss01_A6_LeapSlam`).
- **Objective:** Verify whether any production Niagara VFX or material ring renders in the environment when debug visualization is suppressed in Shipping builds, directly evaluating defect VIS-05.
- **Gate Dependency:** **BLOCKED PENDING PACKAGED SHIPPING BUILD**.
  > [!IMPORTANT]
  > In `Source/OneBossFight/Player/RPGBossShockwave.cpp:164-166`, the expanding ring is rendered directly via:
  > ```cpp
  > #if !UE_BUILD_SHIPPING
  >     DrawDebugCircle(GetWorld(), FVector(Origin.X, Origin.Y, GroundZ + 8.f), Radius, 64, FColor(255, 140, 40), false, -1.f, 0, 8.f, FVector(1, 0, 0), FVector(0, 1, 0), false);
  > #endif
  > ```
  > This debug draw is compiled into all non-Shipping configurations and is **NOT guarded by `rpg.Debug` or any runtime cvar**. Setting `rpg.Debug 0` in the editor will not disable `DrawDebugCircle`.
  > A true debug-off capture can **ONLY exist in a packaged Shipping build** (`Scripts/Package.ps1 -Configuration Shipping`, executed outside the editor).
  > **Status:** CAP-04 is **BLOCKED** until a Shipping package is produced. Captures taken in Development or Editor builds can ONLY demonstrate the debug-on reference.
- **Camera Setup:**
  - **Type:** High-Angle Wide Arena Camera.
  - **World Location:** `(0.0, -900.0, 650.0)` cm looking down at arena center `(0.0, 0.0, 146.0)`.
  - **Rotation:** Pitch $-35.0^\circ$, Yaw $+90.0^\circ$, Roll $0.0^\circ$.
  - **Focal Distance:** $1100.0\text{ cm}$, framing the full expansion circumference ($2200\text{ cm}$ diameter).
  - **Field of View (FOV):** $75.0^\circ$.
- **Temporal Resolution:** $60.0\text{ fps}$ real-time capture from slam impact $t = 0.0\text{ s}$ through full expansion $t = 1.200\text{ s}$.
- **Overlay Content:**
  - Packaged Shipping Run: Strictly native game visuals (no debug circles possible).
  - Development Run: `DrawDebugCircle` reference overlay only.
- **Epistemological Scope:**
  - **CAN SHOW:** Total presence or absence of rendered visual wave assets (particles, meshes, decals) in the game world.
  - **CANNOT SHOW:** Mathematical radial damage falloff or player jump clearance calculation.

---

### CAP-05: A2 Overhead Slam Live Twirl vs Authored Poise Hold

- **Target Move:** A2 (Delayed Overhead Slam / `GS_ChargedAttack_Montage` vs Authored 3-part set `AN_Boss01_A2_Raise/ApexHold/Slam`).
- **Objective:** Record the visual presentation of the pack's multi-revolution blade twirl during windup and document weapon clipping through boss shoulder/cape armor, establishing a visual baseline against the authored 3-part stationary hold.
- **Gate Dependency:** **READY IN EDITOR (Visuals do not require G-4)**.
  > [!NOTE]
  > While Gate G-4 (`Montage_Stop` call-stack diagnostic) was requested to identify the internal software canceller and NOT approved, capturing the *visual animation playback* does not require G-4. It can be triggered via existing test driver `pie_a4_low_sweep.py` patterns or natural combat.
- **Camera Setup:**
  - **Type:** Front-Quarter Combat Framing.
  - **World Location:** Local offset `(220.0, -180.0, 220.0)` cm relative to boss root.
  - **Rotation:** Pitch $-10.0^\circ$, Yaw $+145.0^\circ$, Roll $0.0^\circ$.
  - **Focal Distance:** $300.0\text{ cm}$, framing full boss height and sword apex.
  - **Field of View (FOV):** $55.0^\circ$.
- **Temporal Resolution:** $60.0\text{ fps}$ real-time across windup ($0.000\text{ s}$ to $1.500\text{ s}$).
- **Overlay Content:**
  1. Montage section markers, notify names, and playback position counter.
  2. Blade tip trajectory trail (rendered via local $(0,0,163.3)$ transform).
- **Epistemological Scope:**
  - **CAN SHOW:** Visual trajectory of the sword during windup, visual clipping with character mesh, and motion readability.
  - **CANNOT SHOW:** The internal code or Blueprint reason why `Montage_Stop` is invoked at runtime.

---

### CAP-06: Windup Tracking Yaw vs Foot Grounding (VIS-07)

- **Target Moves:** A1 (`AN_Boss01_A1_QuickSlash`) and A3a (`AN_Boss01_A3a_Combo1`).
- **Objective:** Document whether $360^\circ/\text{s}$ angular tracking during in-place windups causes observable foot sliding/skating across the arena floor stone textures.
- **Gate Dependency:** **READY IN EDITOR (NO G-4/G-5 NEEDED)**. Executed in live PIE duel with player moving tangentially at maximum angular velocity.
- **Camera Setup:**
  - **Type:** Low-Angle Ground / Foot Contact Close-Up.
  - **World Location:** Local offset `(150.0, -120.0, 45.0)` cm relative to boss feet.
  - **Rotation:** Pitch $-5.0^\circ$, Yaw $+140.0^\circ$, Roll $0.0^\circ$.
  - **Focal Distance:** $190.0\text{ cm}$, tightly framing boss boots contact with floor stone tiles.
  - **Field of View (FOV):** $40.0^\circ$ (tight telephoto lens to amplify sliding perspective against ground grout lines).
- **Temporal Resolution:** $60.0\text{ fps}$ real-time capture during player lateral sprint.
- **Overlay Content:**
  1. Instantaneous boss tracking yaw rate ($^\circ/\text{s}$).
  2. Ground-projected foot bone markers (`foot_l`, `foot_r`).
  3. Arena stone tile seam reference grid.
- **Epistemological Scope:**
  - **CAN SHOW:** Physical foot translation across floor textures during root yaw rotation (skating/sliding artifacts).
  - **CANNOT SHOW:** Friction coefficients, capsule physics contact forces, or root motion math.

---

## 4. Tool Dependencies & Gate Approvals Matrix

The following matrix audits tool requirements and gate authorizations across all captures:

| Capture ID | Target Ability | Existing Driver / Trigger | Required Gate Hook | Gate Status | Operational Feasibility |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CAP-01** | A5 Heal Punish | `pie_a5_heal_punish.py` | None | **APPROVED** | Test hook ready; micro-sampling rate **UNVERIFIED METHOD** pending 20-frame feasibility test. |
| **CAP-02** | A4 Low Sweep | `p0_a4_geometry.py` | None | **APPROVED** | Test hook ready; micro-sampling rate **UNVERIFIED METHOD** pending 20-frame feasibility test. |
| **CAP-03** | Mid / Sprint / Retal | None (no native Python hook) | **G-5** (pack move hook) | **NOT APPROVED** | **BLOCKED for automation.** Manual/natural PIE observation only. |
| **CAP-04** | A6 Shockwave | Phase 2 trigger / PIE test | Shipping Package | **APPROVED (G4-2)** | **BLOCKED until Shipping build.** Development only shows debug-on reference. |
| **CAP-05** | A2 Slam | `pie_a2` / `StartMove` | None (G-4 not needed for visuals) | **APPROVED** | Ready for visual motion capture in editor. |
| **CAP-06** | A1 / A3a Tracking | PIE lateral sprint duel | None | **APPROVED** | Ready for execution via manual/bot PIE duel. |

---

## 5. Storage, Metadata Schema, and Hash Auditing

All captures must be stored under the repository evidence directory and accompanied by cryptographic hashes and machine-readable metadata.

### 5.1 Directory Layout
```
Docs/BossCombatReview/Execution/Antigravity/Evidence/captures/
├── CAP01_A5/
│   ├── CAP01_A5_ProfileLeft_slomo02_0012_20261025T193000.png
│   ├── CAP01_A5_ProfileLeft_slomo02_0012_20261025T193000.json
│   └── CAP01_A5_strip_20261025T193000.png
├── CAP02_A4/
│   ├── CAP02_A4_TopDownIso_slomo02_0024_20261025T193500.png
│   ├── CAP02_A4_TopDownIso_slomo02_0024_20261025T193500.json
│   └── CAP02_A4_strip_20261025T193500.png
...
└── CAPTURE_MANIFEST.json
```

### 5.2 File Naming Convention
- **Raw Frames:** `CAP{NN}_{MOVE_ID}_{VIEW}_{RATE}_{FRAME:04d}_{TIMESTAMP}.png`
- **Metadata Sidecar:** `CAP{NN}_{MOVE_ID}_{VIEW}_{RATE}_{FRAME:04d}_{TIMESTAMP}.json`
- **Sequence Contact Strip:** `CAP{NN}_{MOVE_ID}_{VIEW}_{RATE}_strip_{TIMESTAMP}.png`

### 5.3 Machine-Readable Sidecar Schema (`.json`)
Every recorded image must have an identical basename JSON sidecar adhering to this structure:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "capture_id": "CAP-01",
  "file_name": "CAP01_A5_ProfileLeft_slomo02_0012_20261025T193000.png",
  "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "timestamp_utc": "2026-10-25T19:30:00Z",
  "git_commit": "c482d2d854580b8529f7335707768564bc7a61dd",
  "environment": {
    "engine_version": "5.5.4",
    "window_state": "RESTORED_FOREGROUND",
    "viewport_resolution": [1920, 1080],
    "cvars": {
      "rpg.WakeClip": 0,
      "rpg.CloseTelegraph": 0,
      "rpg.Legend": 0,
      "rpg.Debug": 1
    }
  },
  "temporal": {
    "time_dilation": 0.2,
    "effective_fps": 300.0,
    "engine_time_s": 14.285,
    "montage_position_s": 0.400,
    "frame_index": 12
  },
  "camera": {
    "world_location_cm": [-120.0, -280.0, 366.0],
    "world_rotation_deg": [-12.0, 65.0, 0.0],
    "fov_deg": 45.0
  },
  "epistemological_bounds": {
    "proves": "Visual release pose timing relative to actor spawn tick in viewport rasterization.",
    "does_not_prove": "Collision sweep contact, player damage, or hit registration."
  }
}
```

### 5.4 Hash Manifest Generation
Upon completion of any capture session, an automated manifest script (`generate_capture_manifest.py`) computes SHA-256 hashes for all PNG and JSON files and compiles `CAPTURE_MANIFEST.json` to ensure tamper-proof evidence records.
