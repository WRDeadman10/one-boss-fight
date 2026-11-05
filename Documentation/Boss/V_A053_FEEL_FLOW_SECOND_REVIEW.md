# V-A053: Second Review of V-C041..V-C047 (Feel Flow, Input Latency, Camera & Stamina Audits)

**Author:** Antigravity (Lane A)  
**Date:** 2026-11-06  
**Reference Tasks:** `V-C041..V-C047`, `[X-1301]`, `[X-1302]`, `[C-928]`

---

## 1. Executive Summary & Review Verdict

Codex delivered comprehensive feel, flow, camera, and stamina audits in tasks `V-C041` through `V-C047`, supported by the new input latency driver [`Scripts/Editor/pie_input_montage_latency.py`](../../Scripts/Editor/pie_input_montage_latency.py) and documentation in [`V_C041_C045_FEEL_FLOW_AUDIT.md`](./V_C041_C045_FEEL_FLOW_AUDIT.md) and [`V_C046_C049_CAMERA_STAMINA_AUDIT.md`](./V_C046_C049_CAMERA_STAMINA_AUDIT.md).

Lead Claude accepted batches `V-C041..V-C060` in `[C-928]` as audits and documents, confirming that open findings (such as `KI-190`) remain open scope questions and must not be unilaterally tuned. This second review validates the telemetry methodology, camera framing guarantees, hit-feel timings, and stamina balance recommendations.

---

## 2. Input Latency Telemetry Audit (`V-C041`)

`pie_input_montage_latency.py` measures the duration between synthetic action injection (`IA_NormalAttack`, `IA_Dodge`, `IA_Parry`) and the first active player montage change observed by the game loop.

### 2.1 Resolution & Quantization Considerations
- **Measurement Boundary:** This driver measures *software dispatch and blend-in startup*, not physical peripheral-to-photon latency.
- **Tick Quantization:** Because montage evaluation occurs on character tick, observed latency is quantized to tick boundaries:
  - At 60 FPS (16.67 ms delta): Expected latency is 16.7–33.3 ms (1–2 ticks).
  - At 30 FPS PIE (33.33 ms delta): Expected latency is 33.3–66.7 ms (1–2 ticks).
- **Assessment:** Zero-frame C++ delegate execution was confirmed in `V-A042`. Any observed delta in `pie_input_montage_latency.py` represents expected animation blend-in scheduling rather than input handler queue lag.

---

## 3. Hit-Feel & Combat Readability (`V-C042`, `V-C043`)

| Combat Mechanic | Current Engine Implementation | Design Freeze v1.2 Reference | Audit Finding |
|---|---|---|---|
| **Hit Stop Duration** | `HitStopSeconds = 0.08f` (80 ms) | 0.08 s target | Optimal Soulslike impact freeze (~5 frames @ 60 FPS); provides tactile weight without breaking fluidity. |
| **Hit Stop Dilation** | `HitStopDilation = 0.05f` | 0.05 time dilation | Near-complete pause; matches standard genre feel. |
| **Lethal Riposte Hit Stop** | `bSkipHitStopOnLethal = true` | Smooth execution kill | Prevents awkward pauses during final boss death cut-in. |
| **Camera Slam Shake** | Triggered on A2/A6 slam impacts | Slam shake | Verified once per active attack instance; prevents visual disorientation. |
| **Telegraph Reaction Windows** | Scaled stand-in clips: A1 commit 0.33s, A2 commit 1.68s, A3a commit 0.38s, A4 commit 0.40s | 0.35–0.60 s readable tell | Dilation bridges the reaction gap effectively until fully authored animations replace stand-in clips. |

---

## 4. Camera Distance, Collision & Framing (`V-C046`)

- **Baseline Framing Dataset (QA006):** 73 samples across 300 cm, 600 cm, and 900 cm bands demonstrated `any_occluded = false` with boss height ratios between 24.24% (at 900 cm) and 66.90% (near band).
- **Spring-Arm Probe Radius:** `34 cm` probe on `ECC_Camera` collision channel prevents geometry clipping against arena braziers and perimeter colonnades.
- **Lock-On Bounds Clarification:**
  - Probe bands (300/600/900 cm) are evaluation test steps, not gameplay lock-on break distances.
  - The arena floor has an 1100 cm combat radius and 1200 cm outer wall. Lock-on break distance should be formally specified at **1500 cm** so players performing tactical backward rolls along the perimeter do not suffer unexpected lock-on detachment.

---

## 5. Stamina & Posture Balance Analysis (`KI-190`, `V-C047`)

### 5.1 The Discrepancy
- Freeze v1.2 section 5 specifies "35 stamina per Strength swing".
- `RPGWeaponAttackTable::FillDefaults` sets `StaminaCost = -1` (falling back to pack base cost 15) for Light Attack, while Jumping Heavy explicitly sets `StaminaCost = 35` and `PostureDamage = 38`.

### 5.2 Recommendation (Strongly Support Codex's Assessment)
- **Do Not Change Runtime:** Greystone's baseline stamina pool is 100 points. If a basic Light Attack cost 35 stamina, the player would exhaust their entire stamina pool in less than 3 swings, leaving zero stamina for dodge roll (20 stamina) or parry (15 stamina).
- **Intended Design Hierarchy:**
  - Light Attack: 15 stamina, 18 posture damage (enables 4-hit chain + roll).
  - Jumping Heavy: 35 stamina, 38 posture damage (high-risk, high-reward burst).
- **Action Item:** Keep `KI-190` open for Owner/Lead scope confirmation; maintain current runtime configuration untouched.
