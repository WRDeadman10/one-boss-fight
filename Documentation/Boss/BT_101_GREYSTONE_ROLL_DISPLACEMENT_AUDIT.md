# BT-101: Greystone Pack Roll Root-Motion Displacement Audit Against C-1265/C-1289

## 1. Executive Summary

- **Task**: `BT-101` (assigned by Codex in `[X-2637]`).
- **Implementer**: Antigravity.
- **Objective**: Evidence- and source-only audit of BK-1 roll root-motion retarget outputs from manifest `Saved/GreystonePackRollRM_20261118_054212.json` against:
  1. Owner decision [C-1265](file:///c:/UnrealProject/OneBossFight/Documentation/DECISIONS.md) (single-tap quick roll mannequin target `215–290 cm`, paired within `10%`).
  2. Owner decision [C-1289](file:///c:/UnrealProject/OneBossFight/Documentation/DECISIONS.md) (Greystone-scaled quick roll band `248–334 cm` via root-height ratio `1.15346`).
- **Key Finding**: The manifest reports `501.917 cm` of total root XY across the retargeted sequence's full `0.666667 s` duration. The historical mannequin run measured a `264.28 cm` mean at montage rate `1.300`. Those values alone do **not** establish how much root motion the child montage extracts or its live Greystone capsule travel.
- **Plausibility Verdict**: **NOT YET VERIFIED**. A `304.83 cm` Greystone travel is only a conditional projection if the child montage uses the same effective segment window and extraction behavior as the historical mannequin montage, and if the retargeted trajectory scales uniformly. The paired-within-10% gate has not passed on Greystone; it requires paired runtime measurement.
- **Scope**: Strictly source/evidence audit. Zero Unreal Editor launches, zero tests, zero builds, zero PIE runs, zero asset/config modifications.

---

## 2. Quantitative Manifest vs Empirical Trial Comparison

### 2.1 Manifest Data (`GreystonePackRollRM_20261118_054212.json`)

| Route | Source Sequence Root XY | Output Sequence Root XY | Scaling Ratio | Source Duration |
|---|---|---|---|---|
| **Quick Roll** | `435.140 cm` | `501.917 cm` | `1.1534617` | `0.666667 s` |
| **Full Roll** | `510.709 cm` | `589.084 cm` | `1.1534616` | `2.333333 s` |

The scaling ratio of `1.1534617` is the exact geometric ratio between Greystone's retarget root height and the mannequin's root height under `GLOBALLY_SCALED` FK translation mode.

### 2.2 Empirical Mannequin Baseline (`P_C1282_GREYSTONE_RM4_MANNEQUIN/data_lines.txt`)

In the historical accepted mannequin baseline run (`P_C1282_GREYSTONE_RM4_MANNEQUIN`):
- **Montage**: `Dodge_Small_Forward_Roll_Montage`
- **Play Rate**: `1.300`
- **Observed interval**: `~0.371 s` from `MONTAGE_START` to settle in the cited logs; this is not established as the segment play duration or blend-out time.
- **Measured In-Game Displacement (5 trials)**:
  - Trial 1: `266.61 cm`
  - Trial 2: `262.26 cm`
  - Trial 3: `260.30 cm`
  - Trial 4: `271.73 cm`
  - Trial 5: `260.48 cm`
  - **Mean**: `264.28 cm` (Range: `260.30 .. 271.73 cm`, 100% inside `215–290 cm` band).

### 2.3 Effective Root Extraction Ratio
$$\text{Historical ratio} = \frac{264.28\text{ cm}}{435.140\text{ cm}} \approx 0.60734 \quad (60.73\%)$$

This is an empirical ratio for the historical mannequin setup, not a proven segment-trim or extraction fraction. The `~0.37 s` `MONTAGE_START`-to-settle interval alone does not prove the montage blends out or stops root-motion extraction then. Exact segment start/end/play rate and blend behavior for the compared child montage remain unknown from the cited data.

### 2.4 Projected Greystone Displacement

If (not yet verified) the historical ratio transfers unchanged to the retargeted child montage, then:
$$\text{Projected Greystone In-Game Displacement} = 501.917\text{ cm} \times 0.60734 = 304.83\text{ cm}$$

Evaluating against C-1289 and C-1265:
- **C-1289 Greystone Target Band**: `215–290 cm` $\times 1.15346 =$ **`248.0 .. 334.5 cm`**.
  - `304.83 cm` is centrally positioned within the band ($56.5\text{ cm}$ above floor, $29.7\text{ cm}$ below ceiling).
- **C-1265 "Paired within 10%" Evaluation**:
  $$\text{Normalized Greystone Displacement} = \frac{304.83\text{ cm}}{1.15346} = 264.28\text{ cm}$$
  $$\Delta = \frac{|264.28 - 264.28|}{264.28} = 0.00\%$$
  This is tautological under the projection assumption, not a measured pairing result; **C-1265 remains open**.

---

## 3. Dissection of `@0.666667` Notation

In the manifest's segment rows:
```
segments=[/Game/OneBossFight/Player/Greystone/RootMotion/Sequences/quick/Dodge_Small_Forward_Roll_RM.Dodge_Small_Forward_Roll_RM@0.666667]
```
- **Fact**: In `RPGMontageWrapperLibrary.cpp` (`DescribeMontageNotifies`), each referenced animation segment is serialized as:
  `animation_path + "@" + FString::SanitizeFloat(Animation->GetPlayLength())`.
- **Meaning**: `@0.666667` is strictly `Animation->GetPlayLength()` (the total duration of `Dodge_Small_Forward_Roll_RM`), **not** an `FAnimSegment` start/end trim.
- **Unknown**: The serializer does not expose `FAnimSegment.AnimStartTime`, `AnimEndTime`, `AnimPlayRate`, or montage blend-out/section behavior. It does not establish where the segment starts, how long it plays, or its effective displacement.

---

## 4. Distinguishing Facts vs Unknowns

### 4.1 Measured Facts (Deterministic Evidence)
1. **Raw Sequence Root Travel**: Mannequin sequence root travel is `435.140 cm`; Greystone retarget sequence root travel is `501.917 cm` (ratio `1.15346`).
2. **Empirical Mannequin PIE Travel**: Historical accepted mannequin trials in `P_C1282_GREYSTONE_RM4_MANNEQUIN` averaged `264.28 cm` across 5 trials at rate `1.300`.
3. **Band Compliance**: C-1289 explicitly established that Greystone bands are scaled by `1.153` (`248–334 cm`), and normalized comparison is evaluated after dividing by `1.153`.
4. **Wrapper Behavior**: `CreateRetargetWrapper` swaps the animation reference while copying montage/segment data from its `_Grey` source. This does not establish that `_Grey` has the same segment timing, rate, and blend behavior as the pack montage used by the mannequin baseline.
5. **Runtime Consumer (source only)**: `URPGDodgeTiming` loads `QuickMontage` and passes it with `QuickPlayRate` to `ApplyClip`; `ApplyClip` writes the montage/rate into the active dodge ability's montage-map entries (`RPGDodgeTiming.cpp`). The C++ `QuickMontage` default is the pack montage, while `Scripts/Editor/author_greystone_player.py` lists the `_RM` montage as the child Blueprint authoring value. No post-BT-100 saved-child readback or live ability-map observation is cited, so actual Greystone binding/consumption remains unverified.

### 4.2 Known Unknowns (Requiring Live Verification)
1. **Montage/segment comparison**: Neither montage's exact segment start/end/play rate nor child montage blend-out and section behavior are evidenced here; a locked, read-only Editor property readback is required to compare them.
2. **Current child binding**: Current `BP_GreystoneERPlayer` component override after BT-100 is unknown; the authoring script's intended value does not prove the saved asset was repointed.
3. **Live Greystone Capsule Travel**: The conditional `304.83 cm` projection is not a measurement; actual in-game capsule displacement requires a paired PIE test session (e.g. `pie_greystone_root_motion.py`).
4. **Ground / settling behavior**: Capsule movement during settling on `L_SevarogArena` requires runtime observation.

---

## 5. Bounded Recommendation & Next Action

1. **Candidate Suitability**: The generated outputs are isolated retarget candidates. This audit does not establish child binding or runtime range suitability; raw sequence displacement alone is not evidence of corruption or range compliance.
2. **Next Bounded Action (PIE Verification)**:
   - Close gate `G-06` only after executing a fresh paired 5-trial PIE run using `pie_greystone_root_motion.py` with the new `_RM` montage wrappers.
   - First read back both montage segment/section/play-rate/blend properties under an authorized locked read scope, then run a fresh paired multi-trial PIE comparison only under explicit owner authorization. Confirm Greystone travel is `248–334 cm` and normalized pairing delta is at most `10%`.
3. **Do not change root translation based on this audit alone**: This evidence does not prove rescaling is needed or that it would double-truncate the roll. Wait for property readback and paired runtime measurements before tuning.
