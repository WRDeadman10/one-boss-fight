# AG-31: Capture Expected-Value Table & Offline Verdict Specification (Revision 3)

**Author:** Antigravity (Visual & Technical Animation Investigator)  
**Date:** 2026-10-26  
**Work Order:** `Docs/BossCombatReview/Execution/TASK_BOARD.md` (Task **A-T1 Revision 3**, answering `[C-135]`, `[C-137]`, `[C-138]`, and `[C-139]`)  
**Companion Analysis Engine:** [`Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_analysis.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_analysis.py)  
**Capture Driver Drafts:** `Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_drafts/` (`pie_capture_cap01_a5.py`, `cap02_a4.py`, `cap05_telegraph.py`, `cap06_recovery.py`)  
**Citations & Sources:** `Claude/Evidence/E-007_CAP01_A5_release_timing.md`, `Claude/Evidence/E-008_CAP02_A4_query_vs_visible_blade.md`, `Antigravity/AG3_TELEGRAPH_READABILITY_SPEC.md`

---

## 1. Executive Summary & Audit Hardening

Following Claude's technical lead reviews (`[C-135]`, `[C-137]`, `[C-138]`, and `[C-139]`), this specification and its companion analysis engine have been thoroughly hardened:

1. **Strict Monotonic Simulation Progression:** Rejects any capture whose simulation timestamps fail to advance by at least $0.020\text{ s}$ per frame ($dt_{\text{sim}} \ge 20\text{ ms}$). Same-tick rapid-fire bursts (e.g. 15 frames at $0.949\text{--}0.953\text{ s}$) are immediately rejected as invalid time-compression artifacts.
2. **Offline Image Variance & Blank Frame Detection (Zero Dependencies):** Built-in pure-Python `zlib`/`struct` pixel-variance analysis on captured PNGs (`verify_image_file`) rejects blank or unrendered frames (e.g. 17KB solid-color frames produced when RHI render target readbacks fail to resolve). Fully functional under isolated Python (`python -I`) without external dependencies (Pillow is optional acceleration).
3. **Engine Runtime Veto Ingestion:** The engine monitors runtime logs for attack vetoes (`LogRPGAttack: attack vetoed: a phase transition is running / boss is waking / boss is dormant`). Even if a driver outputs `RESULT 5/5`, a vetoed move is rejected as an invalid test run.
4. **Author Intent vs Code Release vs Sampled Observation (E-007 Alignment):**
   - Authored intent release marker: $0.400\text{ s}$ (Frame 12 @ 30fps sidecar intent, `E-007:7`).
   - Code active window release: $0.450\text{ s}$ (`URPGAttackTracker`, `E-007:5`).
   - Observed sampled release: $0.470\text{ s}$ (`E-007:3`).
   - Nominal offset: $0.050\text{ s}$ ($1.0\text{ frame}$ @ 20fps), Sampled offset: $0.070\text{ s}$ ($1.4\text{ frames}$ @ 20fps).
   - Per `E-007:7` and `D06B:40`, visual hand-release pose remains UNVERIFIED until frame-by-frame visual capture is executed. Readability impact is classified as a feel question for owner signoff, NOT a defect.
5. **A4 Active Query Window Reconciliation (AG31 vs AG32 vs E-008):**
   - The authoritative C++ production query window is $[0.609, 0.879]\text{ s}$ ($12\text{ ticks}$ of $24\text{ ms}$, duration $0.270\text{ s}$) per `E-008:10` (`RPGBossLowSweep`).
   - The historical preliminary envelope $[0.533, 1.100]\text{ s}$ was an initial offline sidecar estimate; it is superseded and withdrawn in favor of the live C++ probe measurements in `E-008:10`. AG31 and AG32 are now in 100% agreement.
6. **Capture Driver Draft Diagnostics (`[C-138]`):**
   - Deferred `editor_request_begin_play()` by $0.5\text{ s}$ of Slate ticks.
   - Raised PIE setup timeout to $120\text{ s}$ with $5\text{ s}$ diagnostic heartbeats detailing missing objects (`world`, `pc`, `pawn`, `boss`).
   - Dedicated $45\text{ s}$ capture burst limit.
   - Clean `quit` on completion.

---

## 2. Authoritative Benchmark Rules & Tolerance Envelopes

### CAP-01: A5 Javelin Release Timing

* **Combat Context:** Ember Warden long-range javelin throw (`AN_Boss01_A5_JavelinThrow`, duration $2.433\text{ s}$).
* **Authored Intent Release Marker:** $0.400\text{ s}$ (Source: `E-007:7`, AG sidecar intent, frame 12 @ 30fps).
* **Code Active Window Release:** $0.450\text{ s}$ (Source: `E-007:5`, `URPGAttackTracker::StartMove`).
* **Sampled Code Release:** $0.470\text{ s}$ (Source: `E-007:3`, first sampled tick at runtime frame rate).
* **Offset Nominal / Sampled:** $0.050\text{ s}$ ($50\text{ ms}$) nominal / $0.070\text{ s}$ ($70\text{ ms}$) sampled (Source: `E-007:3,7`).
* **Perceptual Status:** Feel question for owner, not a measured defect (`E-007:7`, `D06B:40`). Visual hand pose unverified.

| Metric | Source / Design Freeze | Nominal Value | Pass / Tolerance Envelope | Status & Classification |
|---|---|---|---|---|
| **Authored Release Intent** | `E-007:7` (Sidecar intent) | $0.400\text{ s}$ | $\pm 0.0\text{ ms}$ baseline | Authored Intent Reference |
| **Code Active Window** | `E-007:5` (Tracker) | $0.450\text{ s}$ | $0.050\text{ s}$ ($1\text{ frame}$ @ 20fps) | Engine Code Baseline |
| **Observed Sampled Release** | `E-007:3` (Log sample) | $0.470\text{ s}$ | $0.070\text{ s}$ ($1.4\text{ frames}$ @ 20fps) | Sampled Runtime Value |
| **Tolerance (Strict)** | PROPOSED (Antigravity proposal) | $\le 33.3\text{ ms}$ (1 frame @ 30fps) | Delta from target $\le 33.3\text{ ms}$ | PROPOSED (Feel decision) |
| **Tolerance (Ceiling)** | PROPOSED (Antigravity proposal) | $\le 50.0\text{ ms}$ | Delta from target $\le 50.0\text{ ms}$ | PROPOSED (Feel decision) |
| **Burst Frame Quota** | `AG18`, `pie_capture_cap01_a5` | 15 frames | Exact 15 frames required | Hard Quota |
| **Minimum Sim Step ($\Delta t_{\text{sim}}$)** | Engine Audit `[C-135]` | $\ge 0.020\text{ s}$ | $dt_{\text{sim}} \ge 20.0\text{ ms}$ | Mandatory Anti-Compression Check |
| **Image Integrity** | Offline Audit `[C-137]` | Non-blank PNG | Size $\ge 50\text{ KB}$, pixel std-dev $\ge 1.0$ | Mandatory Anti-Corruption Check |

> [!NOTE]
> **Owner Question (CAP-01):** Does the $0.050\text{ s}$ nominal / $0.070\text{ s}$ observed release offset after the $0.400\text{ s}$ authored marker create any perceptible mismatch in gameplay? `E-007` and `D06B` classify this as a feel question, not a defect. No retune is proposed.

---

### CAP-02: A4 Low Sweep Query vs Visible Blade

* **Combat Context:** Low sweep rotational attack across floor plane (`AN_Boss01_A4_LowSweep`, duration $2.533\text{ s}$).
* **Active Damage Window:** $[0.609, 0.879]\text{ s}$ (Source: `E-008:10`, 12 ticks of 24ms; duration $0.270\text{ s}$). Reconciled with AG32; supersedes preliminary sidecar estimate $[0.533, 1.100]\text{ s}$.
* **Query Reach:** $380.0\text{ cm}$ from root (Source: `E-008:7`, `RPGBossLowSweep.h`).
* **Visible Tip Max Reach:** $312.0\text{ cm}$ at $0.855\text{ s}$ (Source: `E-008:10`, bounds-axis endpoint).
* **Nominal Reach Delta:** $68.0\text{ cm}$ overreach before adding player capsule radius (Source: `E-008:10`).
* **Floor Dip Reference:** Visible tip at or below floor proxy at $[0.730, 0.807]\text{ s}$ and $[0.903, 1.025]\text{ s}$ (Source: `E-008:12`).

| Metric | Source / Design Freeze | Nominal Value | Pass / Tolerance Envelope | Status & Classification |
|---|---|---|---|---|
| **Active Window Range** | `E-008:10` (Probe log) | $[0.609, 0.879]\text{ s}$ | Duration $0.270\text{ s}$ (12 ticks) | Engine Query Window |
| **Query Reach** | `E-008:7` (`RPGBossLowSweep`) | $380.0\text{ cm}$ | Fixed C++ configuration | C++ Mechanism Reach |
| **Max Visible Tip Reach** | `E-008:10` (Probe log) | $312.0\text{ cm}$ | Sampled at $0.855\text{ s}$ | Visual Tip Bound |
| **Reach Overreach Delta** | `E-008:10` | $68.0\text{ cm}$ | Candidate defect pending capture | Measured Discrepancy |
| **Tolerance Reach Delta** | PROPOSED (Antigravity proposal) | $\le 15.0\text{ cm}$ | Overreach $\le 15.0\text{ cm}$ | PROPOSED (Owner Question) |
| **Burst Frame Quota** | `AG18`, `pie_capture_cap02_a4` | 16 frames | Exact 16 frames required | Hard Quota |
| **Minimum Sim Step ($\Delta t_{\text{sim}}$)** | Engine Audit `[C-135]` | $\ge 0.020\text{ s}$ | $dt_{\text{sim}} \ge 20.0\text{ ms}$ | Mandatory Anti-Compression Check |
| **Image Integrity** | Offline Audit `[C-137]` | Non-blank PNG | Size $\ge 50\text{ KB}$, pixel std-dev $\ge 1.0$ | Mandatory Anti-Corruption Check |

> [!NOTE]
> **Owner Question (CAP-02):** The production query reaches $68\text{ cm}$ beyond the farthest visible tip position (`E-008:10`). Is this overreach acceptable as a gameplay forgiving buffer, or should the query reach be matched to the visible blade in P4?

---

### CAP-05: Telegraph Lead Duration & Readability

* **Combat Context:** Heavy attack posture hold / raise telegraph (`AN_Boss01_A2_Raise`, duration $1.833\text{ s}$).
* **Nominal Reaction Lead Time (A1):** $330.0\text{ ms}$ (Source: `AG3:68`, standard $250\text{--}350\text{ ms}$ reaction threshold).
* **Nominal Reaction Lead Time (A2):** $200.0\text{--}250.0\text{ ms}$ (Source: `AG3:90`, justified by combo anticipation).
* **Strict Tolerance Lead Threshold:** $\ge 400.0\text{ ms}$ (Source: PROPOSED by Antigravity; NO SOURCE IN FREEZE; feel decision).
* **Hard Rejection Lead Floor:** $< 350.0\text{ ms}$ (Source: PROPOSED by Antigravity; NO SOURCE IN FREEZE; feel decision).

| Metric | Source / Design Freeze | Nominal Value | Pass / Tolerance Envelope | Status & Classification |
|---|---|---|---|---|
| **A1 Reaction Lead Time** | `AG3:68` | $330.0\text{ ms}$ | Conforms to standard reaction | Spec Nominal |
| **A2 Reaction Lead Time** | `AG3:90` | $200.0\text{--}250.0\text{ ms}$ | Combo anticipation window | Spec Nominal |
| **Strict Lead Tolerance** | PROPOSED (Antigravity proposal) | $\ge 400.0\text{ ms}$ | Lead $\ge 400.0\text{ ms}$ | PROPOSED (Feel decision) |
| **Rejection Floor** | PROPOSED (Antigravity proposal) | $< 350.0\text{ ms}$ | Lead $< 350.0\text{ ms}$ rejected | PROPOSED (Feel decision) |
| **Burst Frame Quota** | `AG18`, `pie_capture_cap05` | 18 frames | Exact 18 frames required | Hard Quota |
| **Minimum Sim Step ($\Delta t_{\text{sim}}$)** | Engine Audit `[C-135]` | $\ge 0.020\text{ s}$ | $dt_{\text{sim}} \ge 20.0\text{ ms}$ | Mandatory Anti-Compression Check |
| **Image Integrity** | Offline Audit `[C-137]` | Non-blank PNG | Size $\ge 50\text{ KB}$, pixel std-dev $\ge 1.0$ | Mandatory Anti-Corruption Check |

> [!NOTE]
> **Owner Question (CAP-05):** Standard human reaction threshold is $250\text{--}350\text{ ms}$ (`AG3:68`). Are the proposed $400\text{ ms}$ strict and $350\text{ ms}$ floor acceptable for boss telegraph leads?

---

### CAP-06: Recovery Opening Duration & Punish Vulnerability

* **Combat Context:** Post-slam grounded recovery opening (`AN_Boss01_A2_Slam`, duration $2.167\text{ s}$).
* **Nominal Recovery Opening:** NO SOURCE IN FREEZE (Owner decision required).
* **Strict Opening Tolerance:** $\ge 800.0\text{ ms}$ (Source: PROPOSED by Antigravity; NO SOURCE IN FREEZE; feel decision).
* **Hard Rejection Opening Floor:** $< 650.0\text{ ms}$ (Source: PROPOSED by Antigravity; NO SOURCE IN FREEZE; feel decision).

| Metric | Source / Design Freeze | Nominal Value | Pass / Tolerance Envelope | Status & Classification |
|---|---|---|---|---|
| **Recovery Opening Nominal** | NO SOURCE IN FREEZE | None declared | Requires Owner Determination | NO SOURCE IN FREEZE |
| **Strict Opening Tolerance** | PROPOSED (Antigravity proposal) | $\ge 800.0\text{ ms}$ | Vulnerable opening $\ge 800\text{ ms}$ | PROPOSED (Feel decision) |
| **Rejection Floor** | PROPOSED (Antigravity proposal) | $< 650.0\text{ ms}$ | Vulnerable opening $< 650\text{ ms}$ | PROPOSED (Feel decision) |
| **Burst Frame Quota** | `AG18`, `pie_capture_cap06` | 16 frames | Exact 16 frames required | Hard Quota |
| **Minimum Sim Step ($\Delta t_{\text{sim}}$)** | Engine Audit `[C-135]` | $\ge 0.020\text{ s}$ | $dt_{\text{sim}} \ge 20.0\text{ ms}$ | Mandatory Anti-Compression Check |
| **Image Integrity** | Offline Audit `[C-137]` | Non-blank PNG | Size $\ge 50\text{ KB}$, pixel std-dev $\ge 1.0$ | Mandatory Anti-Corruption Check |

> [!NOTE]
> **Owner Question (CAP-06):** There is NO SOURCE in the master design freeze for slam recovery duration. Is an $800\text{ ms}$ vulnerable opening desired for player punish windows?

---

## 3. Analysis Script Verification & Self-Test Results

The companion engine [`Evidence/capture_analysis.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_analysis.py) was updated with a pure-Python PNG scanner and executed against its hardened self-test suite under `python -I`:

```
Command: python -I Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_analysis.py --self-test
Result: 6/6 TESTS PASSED
PIL Accelerated: False (Zero-dependency raw PNG decoder active)

Test Case 1: Identical/Compressed Timestamps (Same-Tick Burst)
  PASS: Engine correctly REJECTED compressed timestamps (sim_time 0.949 to 0.953s across 15 frames).
  Captured Rejection: REJECTION: Simulation time compression detected at frame 2: dt_sim=0.0040s < 0.02s limit.

Test Case 2: Blank PNG Image Rejection (Zero-Dependency Variance Check)
  PASS: verify_image_file correctly REJECTED solid-color image (variance=0.0000 < 1.0).
  Captured Reason: Blank image detected (pixel std_dev=0.0000 < 1.0): blank_frame.png

Test Case 3: Missing Files on Disk
  PASS: Engine correctly REJECTED capture due to missing files on disk.
  Captured Rejection: REJECTION: Missing files on disk (0 found vs 15 logged).

Test Case 4: Engine Runtime Veto Detection (Phase Transition Veto)
  PASS: Engine correctly detected LogRPGAttack veto and REJECTED the run despite RESULT 5/5.
  Captured Rejection: ENGINE VETO: Attack execution was vetoed by engine runtime: 'A5 vetoed: a phase transition is running'.

Test Case 5: Source Citation & Owner Question Reporting
  PASS: Engine correctly marked recovery nominal as NO SOURCE IN FREEZE and surfaced Owner Question.
  Captured Metric: NO SOURCE IN FREEZE (Owner decision required)

Test Case 6: Valid Monotonic Capture Run
  PASS: Valid synthetic capture PASSED all checks. Status: PASS.
  Frames: 15, Span: 0.4662s.
```

---

## 4. Capture Draft Defect Resolutions Summary

| File | Defect Addressed | Heartbeat & Timeout Diagnostics | Status |
|---|---|---|---|
| `pie_capture_cap01_a5.py` | Delayed BeginPlay by 0.5s Slate ticks; removed `UEDPIE_` name filter; eliminated phase transition veto (`ResetPhases()`); slomo timed after wake settle; paced burst; synchronous disk wait; file size $\ge 50\text{KB}$; monotonic sim time; clean quit | 5s diagnostic heartbeat; 120s PIE timeout; 45s burst timeout; missing component reporting | **READY FOR C-T1 RUN** |
| `pie_capture_cap02_a4.py` | Delayed BeginPlay by 0.5s Slate ticks; removed `UEDPIE_` name filter; eliminated phase transition veto; slomo timed after wake settle; paced burst; synchronous disk wait; file size $\ge 50\text{KB}$; monotonic sim time; clean quit | 5s diagnostic heartbeat; 120s PIE timeout; 45s burst timeout; missing component reporting | **READY FOR C-T1 RUN** |
| `pie_capture_cap05_telegraph.py` | Delayed BeginPlay by 0.5s Slate ticks; removed `UEDPIE_` name filter; eliminated phase transition veto; slomo timed after wake settle; paced burst; synchronous disk wait; file size $\ge 50\text{KB}$; monotonic sim time; clean quit | 5s diagnostic heartbeat; 120s PIE timeout; 45s burst timeout; missing component reporting | **READY FOR C-T1 RUN** |
| `pie_capture_cap06_recovery.py` | Delayed BeginPlay by 0.5s Slate ticks; removed `UEDPIE_` name filter; eliminated phase transition veto; slomo timed after wake settle; paced burst; synchronous disk wait; file size $\ge 50\text{KB}$; monotonic sim time; clean quit | 5s diagnostic heartbeat; 120s PIE timeout; 45s burst timeout; missing component reporting | **READY FOR C-T1 RUN** |
| `capture_analysis.py` | Pure-Python zero-dependency PNG parser (`zlib`/`struct`); monotonic time check; file existence; pixel variance check; veto detection; exact E-007 citations; reconciled A4 window to `[0.609, 0.879]s` | Fully validated under `python -I` | **6/6 SELF-TEST PASS** |
