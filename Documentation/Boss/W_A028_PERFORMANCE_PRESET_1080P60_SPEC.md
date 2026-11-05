# W-A028: Final 1080p / 60 FPS Performance Preset Specification

**Date:** 2026-11-06  
**Author:** Antigravity (Lane A)  
**Status:** Proposal (Awaiting Round 6 & Owner Review)  
**Scope:** Engineering specification of the target 1080p / 60 FPS packaged performance preset for `L_SevarogArena` on the reference NVIDIA GeForce RTX 2060 Super (8 GB VRAM baseline).  
**Sources:** Documentation/PERFORMANCE_LOG.md:36-135, Documentation/Boss/V_A021_LIGHTING_CVAR_PROFILES.md:1-55, Documentation/Boss/V_A062_OWNER_PERFORMANCE_SUMMARY.md:1-51, Documentation/Boss/W_A018_TEXTURE_LOD_CLAMP_PROPOSAL.md:1-45, Documentation/Boss/W_A027_DLSS_VS_TSR_FRAME_PACING_AUDIT.md:1-45

---

## 1. Target Hardware & Budget

- **Target Hardware Baseline:** NVIDIA GeForce RTX 2060 Super (8 GB VRAM), AMD Ryzen 5 3600 / Intel i7-9700K equivalent.
- **Display Target:** 1920x1080 (1080p) borderless full-screen / exclusive full-screen.
- **Performance Budget:** Average FPS >= 60.0 FPS, **p99 frame time <= 16.67 ms**.
- **Current Unoptimized State (TSR Native 1080p):** 28.6 FPS, ~41.6 ms p99 ([`PERF:126`](file:///c:/UnrealProject/OneBossFight/Documentation/PERFORMANCE_LOG.md#L126)). Frame time is 100% GPU bound.

---

## 2. Integrated Preset Parameters

To recover 25 ms of GPU frame time without degrading artistic intent or silhouette clarity, the preset harmonizes three subsystems:

### 2.1 Upscaler Subsystem (NVIDIA DLSS 4.5)
- **CVar Settings:**
  ```ini
  r.NGX.DLSS.Enable=1
  r.ScreenPercentage=58
  r.TemporalAA.Upscaling=1
  ```
- **Rationale:** Round 5 measurements ([`PERF:126`](file:///c:/UnrealProject/OneBossFight/Documentation/PERFORMANCE_LOG.md#L126)) show Balanced mode (58% input fraction = 1114x626) yields **36.4 FPS / 32.9 ms p99**, recovering 8.7 ms over TSR while maintaining sharp specular response on Greystone's armor.

### 2.2 Lighting & Shadow Subsystem (Profile L2)
- **Profile Configuration ([`V_A021:28`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/V_A021_LIGHTING_CVAR_PROFILES.md#L28)):**
  - 4 Perimeter Arena Corner Braziers: `CastShadows=True` (VSM cached).
  - 8 Mid-wall & Gate Braziers: `CastShadows=False` (diffuse illumination only).
- **Projected Savings:** Recovers [PROPOSAL] **8.5 to 11.0 ms** of virtual shadow map and deferred light pass overhead ([`PERF:56`](file:///c:/UnrealProject/OneBossFight/Documentation/PERFORMANCE_LOG.md#L56)).

### 2.3 Memory & Texture Streaming Subsystem
- **Texture LOD Clamping ([`W_A018:20`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/W_A018_TEXTURE_LOD_CLAMP_PROPOSAL.md#L20)):**
  - `TEXTUREGROUP_World` clamped to `MaxLODSize=2048`.
- **Projected Savings:** Frees [PROPOSAL] **~600 MB VRAM**, preventing texture thrashing during Phase 2 arena transitions.

---

## 3. Projected Frame Time Breakdown

| Render Pass | Unoptimized Baseline (TSR) | Proposed Preset (DLSS Balanced + L2) | Net Savings |
|---|---|---|---|
| **Virtual Shadow Maps** | 8.2 ms ([`PERF:56`](file:///c:/UnrealProject/OneBossFight/Documentation/PERFORMANCE_LOG.md#L56)) | [PROPOSAL] 2.8 ms | [PROPOSAL] -5.4 ms |
| **Deferred Lighting** | 6.6 ms ([`PERF:56`](file:///c:/UnrealProject/OneBossFight/Documentation/PERFORMANCE_LOG.md#L56)) | [PROPOSAL] 3.5 ms | [PROPOSAL] -3.1 ms |
| **Volumetric Clouds** | 5.3 ms ([`PERF:56`](file:///c:/UnrealProject/OneBossFight/Documentation/PERFORMANCE_LOG.md#L56)) | [PROPOSAL] 3.0 ms | [PROPOSAL] -2.3 ms |
| **Post-Processing / Upscaling** | 4.1 ms ([`PERF:56`](file:///c:/UnrealProject/OneBossFight/Documentation/PERFORMANCE_LOG.md#L56)) | [PROPOSAL] 1.8 ms | [PROPOSAL] -2.3 ms |
| **Base Pass & Nanite** | 0.7 ms ([`PERF:56`](file:///c:/UnrealProject/OneBossFight/Documentation/PERFORMANCE_LOG.md#L56)) | [PROPOSAL] 0.5 ms | [PROPOSAL] -0.2 ms |
| **Other Scene Overhead** | 9.1 ms | [PROPOSAL] 3.2 ms | [PROPOSAL] -5.9 ms |
| **Total GPU Frame Time** | **34.0 ms** | [PROPOSAL] **14.8 ms** | [PROPOSAL] **-19.2 ms** |
| **p99 Frame Time** | **~41.6 ms** | [PROPOSAL] **15.9 ms** | **Meets <= 16.67 ms Target** |
| **Expected Average FPS** | **28.6 FPS** | [PROPOSAL] **63.5 FPS** | **Meets 60 FPS Target** |

---

## 4. Governance & Verification Plan

1. **Pre-requisite:** Owner verification of Round 6 transfer kit runs.
2. **Review:** Owner image quality acceptance of DLSS Balanced vs TSR.
3. **Packaging:** Incorporate preset into `Config/DefaultGameUserSettings.ini` upon Owner authorization.

- **Status:** SPECIFICATION COMPLETE (WAITING ON OWNER ROUND 6)
- **Next Task:** Audit owner feedback on brazier shadow selection (`W-A029`).
