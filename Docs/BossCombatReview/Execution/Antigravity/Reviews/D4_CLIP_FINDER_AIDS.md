# D4 Clip Finder Aids & Contact Sheet Tooling

**Author:** Antigravity (Offline Reviewer / Committer Agent)  
**Date:** 2026-10-31  
**Context:** Track D Reference Frame Extraction (C-493, C-494, C-495, C-496)  
**Tooling Script:** [`contact_sheet.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Reviews/contact_sheet.py)  
**Test Suite:** [`test_contact_sheet.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Reviews/test_contact_sheet.py)  
**Target Video:** `Documentation/Boss/Morgott_82_Point_Combat_Reference/Elden Ring - Morgott, The Omen King Boss Fight.webm`  

---

## 1. Overview & Purpose

The D4 tooling aids Lead Claude and reviewers in rapidly locating, inspecting, and annotating key combat milestones (**W** = windup start, **C** = cancel window, **A** = active start, **E** = active end, **R** = recovery blend marker, **RE** = actionable recovery complete) across reference footage.

Rather than scrubbing through video players or exporting unindexed frame folders, `contact_sheet.py` extracts a specified time window in original-video seconds and compiles it into **ONE single high-resolution contact sheet PNG**. Every sampled tile displays its exact timestamp and canonical evidence filename directly on the image, allowing instantaneous identification of milestone frames.

---

## 2. FFmpeg Filtergraph Pipeline & Windows Gotchas

As established during Lead Claude's test runs (C-494, C-496) and verified during tool authoring, FFmpeg filtergraph construction for contact sheet generation requires precise handling of Windows font configs, scale-relative font sizing, and PTS seeking semantics.

### 2.1 The 4-Stage Filter Chain
`contact_sheet.py` constructs a contiguous 4-stage filtergraph:
```text
drawtext -> select -> scale -> tile
```
1. **`drawtext` (Frame Annotation):** Burns the original timestamp and canonical evidence frame filename onto every decoded frame at the bottom-left.
2. **`select` (Decimation):** Decimates the stream by the sampling step (default: every 3rd frame via `select='not(mod(n\,3))'`).
3. **`scale` (Tile Resizing):** Resizes each frame to the target tile width (default: 960px width, preserving aspect ratio via `scale=960:-1`).
4. **`tile` (Grid Assembly):** Arranges the sampled tiles into a single grid image (default: 5 columns $\times$ $R$ rows via `tile=layout=5xR`).

### 2.2 Gotcha 1: Windows Font Escaping & Ordering
- **Problem:** FFmpeg's `drawtext` filter on Windows relies on `libfreetype`/`libfontconfig`. Without an explicit font file, FFmpeg fails with `Fontconfig error: Cannot load default config file` and outputs no frames.
- **Drive Colon Trap:** A path like `C:/Windows/Fonts/arial.ttf` contains a colon (`:`). FFmpeg uses `:` as a key-value delimiter in filter strings, causing filter parse failure.
- **Solution:** The colon must be escaped: `fontfile='C\:/Windows/Fonts/arial.ttf'`.
- **Filtergraph Ordering:** `drawtext` must be positioned **BEFORE** decimation (`select`) and scaling (`scale`). If `scale` or `fps` precede `drawtext`, the frame counter `n` and PTS evaluate against decimated/scaled stream coordinates rather than true source video frames.

### 2.3 Gotcha 2: Scale-Relative Font Sizing & HUD Avoidance (C-496)
- **Problem:** When `drawtext` burns labels onto the 3840-pixel source frame before downscaling to a 960px or 480px tile, a fixed font size (e.g. 20–30px) is scaled down by a factor of 4 to 8, rendering the burned label illegible (~3–7px tall). Furthermore, top-left positioning collides with the in-game boss health and player status HUD.
- **Scale-Relative Sizing Solution:** `contact_sheet.py` computes the source drawtext font size dynamically based on the target output tile width:
  $$\text{fontsize} = \text{round}\left(\frac{\text{label\_px} \times \text{source\_width}}{\text{scale\_width}}\right)$$
  With `--label-px 20` and `--source-width 3840`:
  * For 960px tiles: $\text{fontsize} = \text{round}(20 \times 3840 / 960) = 80$.
  * For 480px tiles: $\text{fontsize} = \text{round}(20 \times 3840 / 480) = 160$.
  On the final scaled contact sheet, the text renders at exactly 20px height.
- **Bottom-Left Placement:** Labels are positioned at `x=margin, y=h-th-margin` with a semi-transparent black backing box (`box=1:boxcolor=black@0.75`) and bright yellow text (`fontcolor=yellow`). This avoids the top-left game HUD completely and guarantees readability against any arena background.

### 2.4 Gotcha 3: PTS Offset on Pre-Input Seeking
- **Problem:** When fast-seeking with `-ss <start>` placed before `-i`, FFmpeg seeks to the nearest keyframe and resets stream Presentation Time Stamps (`%{pts}`) to 0 at the start of the decoded chunk.
- **Solution:**
  1. For timestamp formatting, pass the start time offset into the drawtext macro: `%{pts\:hms\:<start_sec>}`.
  2. For canonical frame indexing, compute the base frame index $F_0$ from the combat zero offset ($t_0 = 105.0$ s) and reference frame rate ($59.9401$ fps):
     $$F_0 = \text{round}((t_{\text{start}} - 105.0) \times 59.9401) + 1$$
     Each decoded frame $n$ evaluates to $F_0 + n$.
  3. The burned text displays:
     ```text
     t= 00:01:50.961 | morgott_c0_00358.png (f=358)
     ```

---

## 3. Camera Dynamics & Confidence Rating

Reference boss footage uses an untethered third-person camera that dynamically adjusts FOV, pans with player motion, and occasionally cuts or zooms during major boss maneuvers. As required by C-494, all measurements must document camera conditions and state confidence.

### 3.1 Camera Conditions to Record in Ledger `notes`
Reviewers must record the camera behavior in the `"notes"` field of `D2_MEASUREMENT_LEDGER.json`:
- **Unobstructed Track:** Boss and player both clearly visible; attack release and weapon apex unoccluded.
- **Player Occlusion:** Player character passes between camera and boss during windup or active frames.
- **Off-Screen Apex:** Boss leaps or weapon arcs partially outside the camera frustum before strike.
- **Camera Cut / Dynamic Zoom:** Dramatic FOV reduction or angle transition during multi-phase transitions.

### 3.2 Confidence Rating Guidelines
The ledger and ingest pipeline validate `"confidence"` against the set `{"high", "medium", "low"}`:
- **`high`:** Both character models, weapon trajectory, hit impact flash, and actionable recovery blend are fully framed and sharply discernable.
- **`medium`:** Minor camera motion or partial weapon occlusion during windup/recovery, but contact frame and active frames are unambiguous within $\pm 1$ frame.
- **`low`:** Significant camera occlusion, motion blur, or off-screen action requiring extrapolation from adjacent combo swings or sound cues.

---

## 4. Safety & Repository Cleanliness

To comply strictly with project rules regarding large media files and clean git history:
1. **External Output Enforcement:** `contact_sheet.py` asserts that the output file path (`--out`) is located **strictly outside the git repository** (e.g. `C:/temp/` or `/tmp/`). Any attempt to output inside the repository raises a `SAFETY VIOLATION` error and halts execution.
2. **Zero Media in Git:** Contact sheets, extracted PNG frames, and raw video clips are strictly prohibited from being staged or committed. Only scripts, documentation, and hashes in `evidence_sha256.txt` are tracked.

---

## 5. Usage & Verification

### 5.1 Dry-Run (Command Inspection)
Inspects parameter calculation and prints the exact FFmpeg command without touching video or disk:
```powershell
python -I Docs\BossCombatReview\Execution\Antigravity\Reviews\contact_sheet.py --start 110.95 --duration 0.5 --step 1 --width 480 --columns 6 --dry-run
```
**Output:**
```text
[DRY-RUN] FFmpeg command:
ffmpeg -ss 110.950 -t 0.500 -i "C:\UnrealProject\OneBossFight\Documentation\Boss\Morgott_82_Point_Combat_Reference\Elden Ring - Morgott, The Omen King Boss Fight.webm" -vf "drawtext=fontfile='C\:/Windows/Fonts/arial.ttf':text='t=%{pts\:hms\:110.950} | morgott_c0_%{eif\:358+n\:d\:5}.png (f=%{eif\:358+n\:d})':fontsize=160:fontcolor=yellow:box=1:boxcolor=black@0.75:boxborderw=32:x=160:y=h-th-160,select='not(mod(n\,1))',scale=480:-1,tile=layout=6x5" -frames:v 1 -update 1 -y C:\temp\contact_sheet_dryrun.png
```

### 5.2 Real Run (0.5s Window at 480px Tile Width)
Generates the contact sheet for a 0.5s window at 480px tile width:
```powershell
python -I Docs\BossCombatReview\Execution\Antigravity\Reviews\contact_sheet.py --start 110.95 --duration 0.5 --step 1 --width 480 --columns 6 --out C:/temp/test_c496_480.png
```
**Result:**
- Generated `C:/temp/test_c496_480.png` (6,068,912 bytes, $2880 \times 1350$ resolution, 30 tiles at $480 \times 270$ each, layout 6x5).
- Inspected label crop `C:/temp/label_crop.png`: label `t= 00:01:50.961 | morgott_c0_00358.png (f=358)` is sharply legible at bottom-left in yellow on black background box.

### 5.3 Automated Test Suite
Verifies Windows font path escaping, grid layout computation, start frame math, filtergraph order, scale-relative font sizing (80px for 960px, 160px for 480px), bottom-left positioning, repository safety checks, and argument handling:
```powershell
python -I Docs\BossCombatReview\Execution\Antigravity\Reviews\test_contact_sheet.py
```
**Result:**
- `6/6 PASS` (0 errors, 0 failures).

---

## 6. Automated Ledger Population Tooling (`fill_ledger.py`)

To eliminate manual arithmetic during clip measurement (D3/D5), [`fill_ledger.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Reviews/fill_ledger.py) populates measurement ledgers directly from visual frame milestones identified in contact sheets.

### 6.1 Features & Workflow
- **Automated Arithmetic:** Reviewers supply only integer frame markers (`--W`, `--C`, `--A`, `--E`, `--R`, `--RE`) and a confidence rating (`--confidence high|medium|low`). The tool automatically calculates:
  $$t_{*\_\text{orig}} = \text{round}\left(105.0 + \frac{\text{frame} - 1}{59.9401}, 3\right)$$
  $$t_{*\_\text{combat}} = \text{round}(t_{*\_\text{orig}} - 105.0, 3)$$
- **Auto-Generated Evidence Filenames:** Sets canonical evidence list containing all six key frames (`morgott_c0_{frame:05d}.png`).
- **Template Protection:** Creates the destination ledger from the template on first use; strictly refuses writing to `--ledger` directly.
- **Immediate Ingest Validation:** Runs `ingest_measurements.validate_entry` immediately on the populated clip and prints the derived card proposal.
- **Overwrite Protection:** Refuses overwriting an already-measured clip unless `--force` is explicitly passed.

### 6.2 CLI Example
```powershell
python -I Docs\BossCombatReview\Execution\Antigravity\Reviews\fill_ledger.py `
    --clip REF_CurvedSwordCombo_Chain1 `
    --W 447 --C 456 --A 465 --E 472 --R 479 --RE 500 `
    --confidence high --notes "camera: unobstructed track"
```
**Output:**
```json
SUCCESS: Clip 'REF_CurvedSwordCombo_Chain1' filled and validated in 'Docs/BossCombatReview/Execution/Claude/D3/D3_MEASURED_LEDGER.json'.
Card Proposal:
{
  "MoveId": "Move_EmberWarden_CurvedSlash_H1",
  "Confidence": "high",
  "ActiveStartSeconds": 0.3003,
  "ActiveEndSeconds": 0.4171,
  "RecoveryEndSeconds": 0.8842,
  "WindupFrames": 18,
  "ActiveFrames": 7,
  "RecoveryFrames": 28,
  "RecoveryTailFrames": 21,
  "TotalAnimationFrames": 53,
  "DesignStatus": "DESIGN INPUT (measured from owner footage, observation only)"
}
```

### 6.3 Test Suite (`test_fill_ledger.py`)
```powershell
python -I Docs\BossCombatReview\Execution\Antigravity\Reviews\test_fill_ledger.py
```
**Result:** `7/7 PASS` (round-trip test + 5 refusal defect tests).
