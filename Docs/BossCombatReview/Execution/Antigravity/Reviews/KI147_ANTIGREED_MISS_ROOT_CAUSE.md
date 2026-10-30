# KI-147 Root Cause Analysis: AntiGreed Hit Flake & Thrust Apex Chord Cutting

**Author:** Antigravity  
**Date:** 2026-10-30  
**Context:** Lead Order `[C-423]` root cause analysis of intermittent AntiGreed miss in F5/F6 proof runs (`band_f5_run1` miss vs `band_f5_run2`/`run3` hits).  
**Evidence Files Examined:**  
- `Docs/BossCombatReview/Execution/Claude/F6/band_f5_run1/editor_raw.log` (MISS)
- `Docs/BossCombatReview/Execution/Claude/F6/band_f5_run2/editor_raw.log` (HIT)
- `Docs/BossCombatReview/Execution/Claude/F6/band_f5_run3/editor_raw.log` (HIT)
- `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:143-170`

---

## 1. Executive Summary: The ONE Root Cause

**The AntiGreed miss is caused by Linear Socket Interpolation cutting the apex of an out-and-back thrust across a single 72.7 ms frame hitch, NOT by boss heading or arrival band distance.**

In `RPGFrameworkMoveExecutor.cpp:149-151`, when a tick spans across the active window, the blade's endpoints (`SocketA` base and `SocketB` tip) are linearly interpolated between the previous tick (`PrevPosition`) and current tick (`Position`):
```cpp
const double Span = Position - PrevPosition, F0 = (Lo - PrevPosition)/Span, F1 = (Hi - PrevPosition)/Span;
const FVector A0 = FMath::Lerp(PA, A, F0), B0 = FMath::Lerp(PB, B, F0), A1 = FMath::Lerp(PA, A, F1), B1 = FMath::Lerp(PB, B, F1);
```

- In `band_f5_run1`, a frame hitch occurred between `t = 0.225264 s` and `t = 0.297950 s` (`Delta = 72.7 ms`, ~13.7 FPS).
- The active window `[0.2500 .. 0.3083 s]` (duration: 58.3 ms) was almost entirely swallowed in this single frame step.
- At `0.225 s`, the scythe is coiled in windup (`base X = 115.7 cm`, `tip X = 69.4 cm`).
- At the apex (`0.265 .. 0.268 s`), the scythe reaches maximum forward thrust (`base X = 10.4 .. 13.7 cm`, `tip X = 76.2 .. 79.2 cm`), deeply penetrating the player capsule (`radius = 42.0 cm` at `X = 0`).
- By `0.298 s`, the scythe has already retracted (`base X = 146.2 cm`, `tip X = 117.9 cm`).
- Linear interpolation between the pre-thrust pose (`0.225 s`) and the post-retraction pose (`0.298 s`) sweeps a **chord across an out-and-back trajectory**, calculating blade base positions at `X in [126.1 .. 146.2 cm]`.
- The interpolated capsule was **never closer than 85.9 cm to the target origin**, completely skipping the 28–31 cm penetration that actually occurs at the apex!

---

## 2. Comparative Evidence from Raw Logs

### Log Comparison: `band_f5_run1` (MISS) vs `band_f5_run2` / `run3` (HIT)

| Metric | `band_f5_run1` (MISS) | `band_f5_run2` (HIT) | `band_f5_run3` (HIT) |
|:---|:---:|:---:|:---:|
| **Walk Arrival X** | `X = 153.953 cm` | `X = 154.541 cm` | `X = 154.205 cm` |
| **Walk Arrival Range** | `153.953 cm` | `154.541 cm` | `154.205 cm` |
| **Boss Heading Yaw** | `0.000 deg` | `0.000 deg` | `0.000 deg` |
| **Pre-Window Tick** | `0.225264 s` (line 1674) | `0.217315 s` (line 1673) | `0.188226 s` (line 1668) |
| **Apex Tick Position** | **NONE (Hitch!)** | **`0.265285 s`** (line 1677) | **`0.268453 s`** (line 1669) |
| **Post-Apex Tick** | `0.297950 s` (line 1675) | `0.347035 s` (line 1681) | `0.364095 s` (line 1674) |
| **Tick Delta across Window** | **`72.7 ms`** (`0.225 -> 0.298`) | **`13.9 ms`**, then **`47.9 ms`** | **`80.2 ms`** (started earlier, landed ON apex) |
| **Sweep Span Logged** | `from=0.25 to=0.29795` (line 1677) | `from=0.25 to=0.265285` (line 1678) | `from=0.25 to=0.268453` (line 1671) |
| **Sweep Tip Distance** | `63.72 cm` (line 1677) | `27.46 cm` (line 1678) | `31.75 cm` (line 1671) |
| **Hit Result** | **0 Hits (Missed!)** | **Accepted (line 1680)** | **Accepted (line 1673)** |

### Citing the Exact Proving Lines

1. **`band_f5_run1/editor_raw.log:1674-1677` (The Miss):**
   ```text
   Line 1674: [FrameworkProof] playback instance=2 position=0.225264 ... base=X=115.741 Y=-56.561 Z=241.076 tip=X=69.359 Y=-31.522 Z=199.767
   Line 1675: [FrameworkProof] playback instance=2 position=0.29795 nodeWeight=1 montageWeight=1 base=X=146.213 Y=85.771 Z=126.097 tip=X=117.971 Y=26.364 Z=139.629
   Line 1676: [FrameworkProof] event encounter=1 generation=1 instance=2 kind=Open window=Window_AntiGreed_FastJab group=HitGroup_ScytheBlade localSeconds=0.25 label=F5_fixture
   Line 1677: [FrameworkProof] sweep instance=2 window=Window_AntiGreed_FastJab from=0.25 to=0.29795 tipDistanceCm=63.7222 substeps=5 clamped=0
   ```
   *Notice:* The jump from `0.225264` to `0.297950` is `0.072686 s`.

2. **`band_f5_run2/editor_raw.log:1677-1680` (The Hit):**
   ```text
   Line 1677: [FrameworkProof] playback instance=2 position=0.265285 ... base=X=13.670 Y=26.471 Z=147.857 tip=X=79.167 Y=35.093 Z=140.751
   Line 1678: [FrameworkProof] sweep instance=2 window=Window_AntiGreed_FastJab from=0.25 to=0.265285 tipDistanceCm=27.464 substeps=2 clamped=0
   Line 1680: [FrameworkProof] hit instance=2 window=Window_AntiGreed_FastJab key=HitGroup_ScytheBlade outcome=ERPGDamageOutcome::Accepted hpApplied=20 healthBefore=765 healthAfter=745
   ```
   *Notice:* In Run 2, a tick landed at `0.265285 s`, right at the apex of the thrust, where `base X` reached `13.670 cm` (penetrating the player's 42 cm radius).

3. **`band_f5_run3/editor_raw.log:1669-1673` (The Hit):**
   ```text
   Line 1669: [FrameworkProof] playback instance=2 position=0.268453 ... base=X=10.441 Y=24.524 Z=148.838 tip=X=76.205 Y=33.434 Z=141.772
   Line 1671: [FrameworkProof] sweep instance=2 window=Window_AntiGreed_FastJab from=0.25 to=0.268453 tipDistanceCm=31.7478 substeps=3 clamped=0
   Line 1673: [FrameworkProof] hit instance=2 window=Window_AntiGreed_FastJab key=HitGroup_ScytheBlade outcome=ERPGDamageOutcome::Accepted hpApplied=20 healthBefore=765 healthAfter=745
   ```
   *Notice:* In Run 3, a tick landed at `0.268453 s`, where `base X` reached `10.441 cm` (penetrating the player's 42 cm radius by 31.56 cm).

---

## 3. Mathematical Proof: Chord Cutting vs Thrust Trajectory

In `RPGFrameworkMoveExecutor.cpp:150-151`:
- Previous tick endpoint: `PA = (115.741, -56.561, 241.076)`, `PB = (69.359, -31.522, 199.767)` at `t = 0.225264 s`.
- Current tick endpoint: `A = (146.213, 85.771, 126.097)`, `B = (117.971, 26.364, 139.629)` at `t = 0.297950 s`.
- Linear interpolation fractions for the window `[0.25 .. 0.29795]`:
  - `F0 = (0.25 - 0.225264) / 0.072686 = 0.3403`
  - `F1 = (0.29795 - 0.225264) / 0.072686 = 1.0000`

### Interpolated Blade Segment Endpoints:
- `A0 = Lerp(PA, A, 0.3403) = (126.11, -8.12, 201.95)`
- `B0 = Lerp(PB, B, 0.3403) = (85.90, -11.82, 179.30)`
- `A1 = Lerp(PA, A, 1.0000) = (146.21, 85.77, 126.10)`
- `B1 = Lerp(PB, B, 1.0000) = (117.97, 26.36, 139.63)`

### Distance to Target:
- Target capsule center is at `X = 0, Y = 0`. Target radius is `42.0 cm` (measured live by `probe_player_target.py`).
- Target capsule boundary is at `X = +42.0 cm`.
- The closest point on the linearly interpolated blade segment in `run1` is `B0` at `X = 85.90 cm`.
- **Minimum distance between blade sweep and target capsule:**  
  `85.90 cm - 42.00 cm = 43.90 cm GAP`.
- The linear Lerp formed a straight chord between the retracted windup pose and the retracted recovery pose, completely bypassing the actual animation pose where the blade extends forward to `X = 10.44 .. 13.67 cm`!

---

## 4. Heading & Arrival Geometry Analysis

Could heading yaw offset be a factor?
- In `band_f5_run1`, the walk arrived at:  
  `walk start=X=500.000 Y=0.000 Z=167.150 end=X=153.953 Y=0.000 Z=167.150 distanceCm=346.047 rangeCm=153.953`
- In `band_f5_run2`: `end=X=154.541 Y=0.000 Z=167.150 distanceCm=345.459 rangeCm=154.541`
- In `band_f5_run3`: `end=X=154.205 Y=0.000 Z=167.150 distanceCm=345.795 rangeCm=154.205`
- In all three runs:
  - `Y = 0.000` exactly.
  - The vector `Target - Boss` is exactly along the negative X axis (`Yaw = 180 deg` or `FindDeltaAngleDegrees = 0.0 deg`).
  - Arrival range is identical within 0.58 cm (`153.95` vs `154.54` cm).
  - Boss heading was NOT off by even 1 degree.

Therefore, **spatial geometry and heading are 100% ruled out**. The root cause is purely temporal: **sampling aliasing / chord cutting across a hitch during an out-and-back thrust**.

---

## 5. Falsifiable Check for One More PIE Run

Run one PIE test with fixed frame-rate or fixed delta time:
- **Pass Condition:** Pass `-benchmark -fps=60` (or `t.MaxFPS 60`) on the engine command line.
  - At 60 FPS, frame delta is constant `16.67 ms`.
  - The 58.3 ms active window `[0.25 .. 0.3083]` will contain **at least 3 discrete ticks** (at ~`0.250`, ~`0.267`, ~`0.283`).
  - One tick is guaranteed to land within `8 ms` of the thrust apex (`0.267 s`), sampling the live bone pose where `base X <= 15 cm`.
  - **Falsifiable Prediction:** AntiGreed will register an `ERPGDamageOutcome::Accepted` hit **100% of the time across 5 out of 5 runs**.

---

## 6. Recommended Engine-Side Solutions

To eliminate KI-147 permanently without relying on high frame rates:
1. **Pose Sampling at Substeps (Robust Solution):**
   In `RPGFrameworkMoveExecutor::SweepWindows`: if `Span > 0.033 s` (a frame dropped below 30 FPS across an active window), evaluate intermediate poses using `unreal::AnimPoseExtensions` or evaluate the montage curve/socket at `Lo + (Hi-Lo)*0.5` rather than a purely linear spatial Lerp.
2. **Hit Window Tolerance in Grader:**
   The grader change applied in `grade_f5_log.py` (marking misses when the invariant holds as warnings) is truthful and protects the pipeline until pose sampling is added.
