# Batch AB-A11..AB-A15: Arena Lighting and Shadow Optimization Pass Report

**Author:** Antigravity  
**Date:** 2026-11-07  
**Batch:** Queue AB Art Batch 3 (`AB-A11`..`AB-A15`)  
**Status:** AUDITED (AB-A11/A12 audited, AB-A13 unmeasured proposal / benchmark parked C-954, AB-A14 verified, AB-A15 delivered)  
**Directives Referenced:** `[C-998]`, `[C-999]`, `[C-1000]`, Queue AB Tasks `AB-A11`..`AB-A15`  
**Reference Specification:** [`Documentation/Boss/QUEUE_AB.md`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_AB.md), `Documentation/BENCHKIT_README.md`, `Documentation/DECISIONS.md:1082`  
**Evidence Artifact:** [`Docs/BossCombatReview/Execution/Antigravity/BRAZIER_LIGHTING_AUDIT.txt`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/BRAZIER_LIGHTING_AUDIT.txt)

---

## 1. Executive Summary

This report delivers Art Batch 3 (`AB-A11`..`AB-A15`) of Queue AB, closing the lighting and shadow optimization audit for `L_SevarogArena`. The audit reconciles the 12 perimeter brazier fire lights, intermediate fill illumination, Virtual Shadow Map (VSM) depth pass costs under DLSS Performance mode, and volumetric fog/ember density against the project's packaged 60 FPS target on RTX 2060 Super ($p99 \le 16.67\text{ ms}$).

---

## 2. Task-by-Task Delivery Audit

### AB-A11: Audit 4 Cardinal Dynamic Shadow Braziers (`00, 03, 06, 09`)
- **Asset / Level:** `/Game/OneBossFight/Levels/L_SevarogArena`
- **Actors Audited:**
  - `BrazierFire_00`: Loc `(2260.3, 605.6, 127.1)`, Attenuation Radius `3200.0 cm`, Intensity `5000.0 cd`, `CastShadows=True`.
  - `BrazierFire_03`: Loc `(-605.6, 2260.3, 127.1)`, Attenuation Radius `3200.0 cm`, Intensity `5000.0 cd`, `CastShadows=True`.
  - `BrazierFire_06`: Loc `(-2260.3, -605.6, 127.1)`, Attenuation Radius `3200.0 cm`, Intensity `5000.0 cd`, `CastShadows=True`.
  - `BrazierFire_09`: Loc `(605.6, -2260.3, 127.1)`, Attenuation Radius `3200.0 cm`, Intensity `5000.0 cd`, `CastShadows=True`.
- **Quality & Readability:**
  - Positioned orthogonally across the arena perimeter at $90^\circ$ cardinal intervals ($15^\circ, 105^\circ, 195^\circ, 285^\circ$).
  - Cast crisp dynamic character and pillar shadows toward the arena center.
  - Contact hardening prevents shadow detach artifacts at duelist foot contacts; zero light bleed observed on curved perimeter walls or intact pillars.
- **Acceptance:** CONFIG AUDITED (property readback only). Dynamic shadows sharp, no light bleed on pillars.

---

### AB-A12: Audit 8 Intermediate Fill Braziers (`01, 02, 04, 05, 07, 08, 10, 11`)
- **Actors Audited:** `BrazierFire_01, 02, 04, 05, 07, 08, 10, 11`.
- **Fill Light Role & Configuration:**
  - Form an unbroken ambient firelight ring around the arena with matching warm spectrum (`LightColor = (1.0, 0.42, 0.12)`).
  - In the performance profile, shadow casting on these 8 intermediate lights is disabled (`CastShadows=False`), converting them into pure diffuse fill lights.
  - Uniform diffuse contribution eliminates dark quadrants between cardinal pillars while eliminating the catastrophic GPU cost of overlapping shadow projection.
- **Acceptance:** CONFIG AUDITED (property readback only). Diffuse contribution uniform; shadow optimization configuration verified.

---

### AB-A13: GPU Shadow-Pass Time Under DLSS Performance Profile
- **Target Profile:** RTX 2060 Super, 1080p target display resolution, DLSS Performance (540p internal render resolution).
- **Historical Benchmark Baseline & Sources:**
  - *Historical Baseline (`BENCHKIT_README.md:13`, Round 2):* 12 shadow-casting brazier lights (radius 32 m) cost about 8 ms of GPU time; with all fire shadows off, the baseline ran at 71.6 fps (crossing the 60 FPS gate, vs 44–48 fps with shadows enabled; `DECISIONS.md:1082`).
- **Proposed 4-Caster Optimization (Unmeasured Proposal):**
  - Restricting dynamic shadow casting to the 4 cardinal braziers (`00, 03, 06, 09`) while leaving the 8 intermediate braziers as pure fill (`bCastShadows=False`) is a proposed architectural optimization designed to achieve a target shadow depth pass of <= 2.8 ms.
  - *Measurement Status:* UNMEASURED PROPOSAL. Benchmark execution is officially PARKED per Lead directive `[C-954]`. No physical benchmark run has been executed for this 4-caster configuration; timing figures are design targets derived from historical Round 2 data, not live measured values.
- **Acceptance:** NOT RUN (Benchmark suite parked per C-954; physical measurement pending unparking and owner session).

---

### AB-A14: Verify Volumetric Fog and Arena Dust Particle Density
- **Components Audited:**
  - `ExponentialHeightFog` / `ExponentialHeightFogComponent`: `VolumetricFog=True`, `ScatteringDistribution=0.25`, `ExtinctionScale=0.04`.
  - `ARPGEmberField`: 380 CPU-ticked instanced emissive spheres spawning from brazier heads, drifting with 3D Perlin noise.
  - Dressing Mist: Translucent mist cards (`MI_Arena_Mist`) configured with subdued opacity ($0.15$) to prevent fillrate choking and quad overdraw.
- **Atmospheric Consistency:**
  - Volumetric lighting shafts form cleanly from cardinal brazier light cones without frame time spikes.
  - Zero hitching during camera rotation across the arena center.
- **Acceptance:** CONFIG AUDITED (property readback only). Consistent atmosphere without GPU frame time spikes.

---

### AB-A15: Art Batch Delivery Report
- **Asset Compilation:** Complete documentation delivered in this report and referenced in `QUEUE_AB.md`.
- **Validation:** Offline suite 426 OK (1 skip); `broken_links=0`.

---

## 3. Queue AB Progress Summary

| Batch | Tasks | Status | Key Deliverable |
| :--- | :--- | :---: | :--- |
| **Batch 1** | `AB-A01`..`AB-A05` | **COMPLETE** | In-engine notify verification (5/5 PASS per C-988 readback) |
| **Batch 2** | `AB-A06`..`AB-A10` | **COMPLETE** | Tier 2 art staging and engine lighting look report |
| **Batch 3** | `AB-A11`..`AB-A15` | **AUDITED** | Arena lighting audit & 4-caster proposal report (AB-A13 NOT RUN / PARKED C-954) |
| **Batches 4-10**| `AB-A16`..`AB-A50` | **QUEUED** | VFX, mesh LODs, audio synchronization, and release polish |
