# Visual Capture Contact Sheet & Frame Analysis Report (Rev 03)

**Document ID:** `VISUAL_CAPTURE_CONTACT_SHEET_REPORT`  
**Revision:** Rev 03 (Decoupled Visual vs Telemetry Records; Duration Brackets & Heuristic Clarifications per Reviewer `[X-150]`)  
**Author:** Antigravity (Visual & Technical Animation Investigator)  
**Parent Work Orders:** `[C-153]`, `[C-154]` (Technical Lead Directives), `[X-148]`, `[X-150]` (Independent Technical Reviews)  
**Source Telemetry & Frames:**  
- Telemetry logs: `Docs/BossCombatReview/Execution/Claude/Evidence/exports/cap_optB_run1/`
- Full-resolution frames: `Saved/Screenshots/CAP01_A5/`, `CAP02_A4/`, `CAP05_Telegraph/`, `CAP06_Recovery/`  
**Status:** DELIVERED (Decoupled Screenshot Inventory from Telemetry Rows; Duration Uncertainty Brackets; Offline Analyzer Hardened)  

---

## 1. Executive Summary & Audit Decoupling Notice

Following independent review `[X-150]`, this report cleanly decouples **Screenshot Frame Observations** from **Telemetry Row Timestamps**.

### 1.1 Independence of Screenshot Inventory vs Telemetry
The external capture loop (`CaptureLoop.ps1`) polls OS desktop windows via `PrintWindow` at $\approx 340\text{ ms}$ wall intervals (`slomo 0.20`), completely asynchronous to Slate ticks and game simulation frames. Telemetry logs are emitted synchronously by `RPGAttackTracker` on Slate post-tick.

Because no shared clock metadata or per-frame hardware sync exists:
1. **No 1:1 Ordinal Mapping Exists:** The $N$-th screenshot does **NOT** necessarily correspond to the $N$-th row of the telemetry log. Telemetry row counts ($12 / 23 / 52 / 39$) differ from on-disk screenshot counts ($11 / 21 / 46 / 35$).
2. **File Naming reflects Flag State at OS Polling Instant:** Filenames (e.g. `024_CAP06_A2_Recovery.png`) reflect the string stored in `m7_flag.txt` when `CaptureLoop.ps1` read it, which may trail or lead Slate tick updates due to process scheduling.
3. **Observations are Separately Tabulated:** All visual observations are documented by **Image Filename**, while telemetry events are documented separately by **Log Simulation Time**.

### 1.2 Formal Withdrawal Status (Confirmed)
- All prior claims that distant silhouettes in CAP-01 "show" the javelin leaving the hand or hand at apex remain **formally withdrawn**.
- All claims that CAP-02 "shows" exact blade floor contact at 3 cm clearance remain **withdrawn**.
- All claims that CAP-05 Frame 01 proves the exact particle ignition instant remain **withdrawn** (left-censored sample).
- All claims that CAP-06 `Active=False` proves player attackability or a guaranteed punish window remain **withdrawn**.

### 1.3 Screening Heuristic Notice: Whole-Crop MAD
The automated inter-phase MAD ($\text{MAD} \ge 1.5$) implemented in `capture_analysis.py` is a coarse offline **freeze-screening heuristic** designed to flag static scenes, identical buffers, or frozen camera positions. It is **NOT** a semantic readability test or mathematical proof of combat clarity. For example, in CAP-02, the windup-to-committed transition yielded $\text{MAD} = 1.33 < 1.5$ despite real weapon rotation, illustrating that heuristic screening can produce false rejections on shallow viewing angles. Semantic readability requires human and lead review.

---

## 2. Capture-by-Capture Inventory & Decoupled Audit

### 2.1 CAP-01: A5 Javelin Throw Release Timing

- **Screenshot File Inventory:** 11 PNG frames (`001_CAP01_A5_Windup.png` to `011_CAP01_A5_Recovery.png`).
- **Telemetry Dataset:** 12 logged samples (`sim = 7.7563\text{ s}` to `8.5065\text{ s}`).
- **Baseline Anchors:** Authored intent: $0.400\text{ s}$ (`E-007:7`); Code active window: $0.450\text{ s}$ (`E-007:5`).

#### A. Image File Visual Observations
- `001_CAP01_A5_Windup.png` to `006_CAP01_A5_Windup.png`: Distant boss figure ($\approx 650\text{ cm}$ away) positioned in center arena; posture upright. Hand and gauntlet are $< 15\text{ px}$ in height and indistinguishable against body mass.
- `007_CAP01_A5_Active.png`: **Visual release UNVERIFIED.** Boss silhouette remains virtually identical to prior frame ($\text{MAD} = 1.12$). No javelin, hand motion, or projectile departure is discernible in pixels.
- `008_CAP01_A5_Recovery.png` to `011_CAP01_A5_Recovery.png`: Boss silhouette returns toward lower rest posture. Projectile flight unobservable against background geometry.

#### B. Telemetry Event Sequence (Logged Ticks)
- **Windup Entry:** `sim = 7.7563\text{ s}`, `pos = 0.068`, `phase = Windup`, `active = False`.
- **Windup Pre-Commit Sample:** `sim = 8.0975\text{ s}`, `pos = 0.409`, `phase = Windup`, `active = False`.
- **Active Phase Transition:** Logged at `sim = 8.1660\text{ s}`, `pos = 0.478`, `phase = Active`, `active = True`, `commit = True`.
- **Recovery Phase Transition:** Logged at `sim = 8.2343\text{ s}`, `pos = 0.546`, `phase = Recovery`, `active = False`.
- **Move Completion:** Logged at `sim = 8.5065\text{ s}`, `pos = 0.750`, `phase = None`.

#### C. Bounds & Uncertainty
- **Telemetry Event Bracket:** Transition into `phase = Active` occurs between `sim = 8.0975\text{ s}` and `8.1660\text{ s}` (bracket width $\Delta t_{\text{sim}} = 68.5\text{ ms}$).
- **Interval Relative to Authored Intent ($0.400\text{ s}$):** $0.478 - 0.400 = \mathbf{+78.0\text{ ms}}$ from logged position sample ($0.478 - 0.450 = \mathbf{+28.0\text{ ms}}$ relative to nominal code window).
- **Close-Up Trial Status:** Option B close-up vantage implemented in `pie_capture_cap01_a5.py` with readback validation, pending Claude's editor execution.

---

### 2.2 CAP-02: A4 Low Sweep Query vs Visible Blade

- **Screenshot File Inventory:** 21 PNG frames (`001_CAP02_A4_Windup.png` to `021_CAP02_A4_Recovery.png`).
- **Telemetry Dataset:** 23 logged samples (`sim = 7.7479\text{ s}` to `9.1775\text{ s}`).
- **Baseline Anchors:** Nominal active window $[0.609, 0.879]\text{ s}$ ($270.0\text{ ms}$); Query reach $380\text{ cm}$; Max tip reach $312\text{ cm}$ (`E-008:10`).

#### A. Image File Visual Observations
- `001_CAP02_A4_Windup.png` to `006_CAP02_A4_Windup.png`: Greatsword held raised on boss's right shoulder; readable silhouette.
- `007_CAP02_A4_Committed.png` to `008_CAP02_A4_Committed.png`: Greatsword begins rotating forward and downward.
- `009_CAP02_A4_Active.png` to `013_CAP02_A4_Active.png`: Greatsword sweeping horizontally across lower torso and arena floor. Gross arc visible; exact $3\text{ cm}$ floor clearance graze is **visual UNVERIFIED**.
- `014_CAP02_A4_Recovery.png` to `021_CAP02_A4_Recovery.png`: Blade completes follow-through across left hip into rest pose.

#### B. Telemetry Event Sequence (Logged Ticks)
- **Committed Heading Lock:** Logged at `sim = 8.0894\text{ s}`, `pos = 0.410`.
- **Active Window Entry:** Logged at `sim = 8.2941\text{ s}`, `pos = 0.615`, `active = True`. (Preceding Windup sample: `sim = 8.2259\text{ s}`, `pos = 0.547`).
- **Active Window Exit:** Last active sample at `sim = 8.5654\text{ s}`, `pos = 0.887`, `active = True`. (Following Recovery sample: `sim = 8.6341\text{ s}`, `pos = 0.955`).

#### C. Bounds & Uncertainty Analysis
- **Observed Active Sample Span:** $8.5654\text{ s} - 8.2941\text{ s} = \mathbf{271.3\text{ ms}}$.
- **Phase Duration Uncertainty Bound:**
  - Start transition bracket: $(8.2259\text{ s}, 8.2941\text{ s}]$
  - End transition bracket: $[8.5654\text{ s}, 8.6341\text{ s})$
  - Under discrete sampling endpoint conventions, the true active phase duration is bounded between:
    $$\Delta t_{\text{min}} = 8.5654 - 8.2941 = \mathbf{271.3\text{ ms}} \quad \text{to} \quad \Delta t_{\text{max}} = 8.6341 - 8.2259 = \mathbf{408.2\text{ ms}}$$
  - **Conclusion:** We cannot conclude exact agreement with the nominal $270.0\text{ ms}$ window from sample span alone; the sampled range is $[271.3, 408.2]\text{ ms}$. Position $0.887$ being active beyond nominal $0.879$ reflects tick discrete advance.

---

### 2.3 CAP-05: Attack Telegraph Readability & Glow

- **Screenshot File Inventory:** 46 PNG frames (`001_CAP05_A2_Windup.png` to `046_CAP05_A2_None.png`).
- **Telemetry Dataset:** 52 logged samples (`sim = 7.7746\text{ s}` to `10.8384\text{ s}`).
- **Human Reaction Threshold:** $250$–$350\text{ ms}$ (`AG3:68`).

#### A. Image File Visual Observations
- `001_CAP05_A2_Windup.png`: Left-censored sample. Greatsword is already elevated; exact particle ignition instant is **visual UNVERIFIED**.
- `015_CAP05_A2_Windup.png`: Clear visual silhouette: greatsword fully raised overhead.
- `021_CAP05_A2_Committed.png`: **Confirmed SEEN IN IMAGE (Claude `[C-154]`):** Readable mid-swing committed telegraph pose with greatsword visible overhead.
- `024_CAP05_A2_Active.png`: Rapid downward blade stroke in motion.
- `025_CAP05_A2_Active.png`: Blade downward impact near floor level.

#### B. Telemetry Durations
- **Full Windup Lead:** `sim = 9.3406\text{ s}` (Active entry) $- 7.7746\text{ s}$ (Windup start) $= \mathbf{1,566.0\text{ ms}}$.
- **Committed Heading-Lock Lead:** Frame 21 (`sim = 9.1356\text{ s}`) to Active entry (`9.3406\text{ s}`) $= \mathbf{205.0\text{ ms}}$.
- **Sampling Limit:** Inter-frame simulation step $\approx 68.2\text{ ms}$.

---

### 2.4 CAP-06: Boss Recovery & Punish Windows

- **Screenshot File Inventory:** 35 PNG frames (`001_CAP06_A2_Windup.png` to `035_CAP06_A2_Recovery.png`).
- **Telemetry Dataset:** 39 logged samples (`sim = 7.7341\text{ s}` to `10.3164\text{ s}`).
- **Freeze Baseline:** Master design freeze contains **NO SOURCE** for slam recovery duration.

#### A. Image File Visual Observations
- `024_CAP06_A2_Recovery.png`: Filename labeled Recovery due to external loop polling latency; blade descending.
- `025_CAP06_A2_Recovery.png`: Coarse slam impact; blade embedded near arena floor.
- `026_CAP06_A2_Recovery.png`: Boss beginning grounded rest. Combat attackability is **visual UNVERIFIED**.
- `030_CAP06_A2_Recovery.png`: **SEEN IN IMAGE:** Boss held in low crouched posture with greatsword point resting on the ground.
- `035_CAP06_A2_Recovery.png`: Boss beginning blend-out return toward upright neutral stance.

#### B. Telemetry Phase Remainder
- **Tracker Recovery Duration:** From recovery entry (`sim = 9.4354\text{ s}`, `pos = 2.121`) to phase None (`sim = 10.3164\text{ s}`, `pos = 3.097`):
  $$\Delta t_{\text{sim}} = 10.3164\text{ s} - 9.4354\text{ s} = \mathbf{881.0\text{ ms}} \quad (\text{wall duration under slomo 0.20: } 4.41\text{ s})$$
  This is strictly a tracker state duration; combat vulnerability or attackability requires gameplay test verification.

---

## 3. CAP-01 Close-Up Framing Status & Verification

### 3.1 Hardened Driver Parameters (`pie_capture_cap01_a5.py`)
In response to reviewer findings (`[X-150]`), the driver was hardened:
- **Component Safety:** `self.boom`, `self.cam`, `self.pawn` initialized in `__init__`; teardown checks existence before attribute access.
- **Fail-Closed Setup:** Missing `CameraBoom` or `FollowCamera` is treated as a fatal failure, aborting the run with explicit failure reasons rather than swallowing exceptions.
- **Dual-Property Lag Handling:** Safely inspects both `b_enable_camera_lag` and `enable_camera_lag` without assuming native name formatting.
- **Measured Readback:** Reads back and logs actual `target_arm_length` and `field_of_view` after applying to confirm framing state.
- **Visibility Restoration:** Restores pawn's original hidden state (`self.orig_pawn_hidden`) on teardown.

### 3.2 Visual Resolution Note
The predicted $\approx 460\text{ px}$ target height is an optical calculation based on an unobstructed $250\text{ cm}$ camera-to-target distance. Actual visual height and hand/javelin readability will be verified from Claude's captured frame.

---

## 4. Summary Table: Decoupled Audit Landmarks

| Benchmark | Visual Observation Landmark | Telemetry Transition Event | Sampled Span / Interval | Uncertainty Bracket | Evidence Classification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CAP-01** | Coarse upright silhouette | Active entry at `sim=8.1660s`, `pos=0.478` | $+78.0\text{ ms}$ vs $0.400\text{ s}$ authored | $[8.098, 8.166]\text{ s}$ ($\pm 68.5\text{ ms}$) | `TELEMETRY ONLY; visual UNVERIFIED` |
| **CAP-02** | Horizontal sweep across floor | Active window `pos=0.615` to `0.887` | $271.3\text{ ms}$ observed active samples | $[271.3, 408.2]\text{ ms}$ phase bound | `TELEMETRY ONLY; visual UNVERIFIED` |
| **CAP-05** | Greatsword overhead committed pose | Active entry at `sim=9.3406s`, `pos=1.962` | $1,566.0\text{ ms}$ total; $205.0\text{ ms}$ committed | $\pm 68.2\text{ ms}$ | **`SEEN IN IMAGE`** (Committed Pose) |
| **CAP-06** | Grounded blade crouched posture | Recovery entry at `sim=9.4354s` | $881.0\text{ ms}$ tracker phase remainder | $\pm 68.4\text{ ms}$ | **`SEEN IN IMAGE`** (Grounded Posture) |
