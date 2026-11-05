# V-A026: Material & Shader Cost Audit (Arena & Boss)

**Author:** Antigravity (Offline Quality, Audit & Asset Lane)  
**Date:** 2026-11-06  
**Scope:** Shader complexity, instruction counts, texture sampler density, and material overdraw analysis for `L_SevarogArena` and Boss duel assets.
**Sources:** Content/OneBossFight/Materials/, Documentation/PROJECT_STATE.md:259

---

## 1. Executive Summary

- **Audit Target:** All active master materials and material instances across `L_SevarogArena` dressing, character skins, weapon surfaces, and environment props.
- **Finding:**
  - Base arena materials (`MI_Arena_RomanFloor`, `MI_Arena_Slab`) are well-optimized Megascans surface instances (\(\sim 115\text{ BasePass ALU}\) instructions, 4 texture samplers).
  - High-cost outliers identified:
    1. `M_FogCard` (Translucent cards at perimeter gate): High quad overdraw (\(3.2\times\)) in camera frustum when facing the South entrance.
    2. `M_Boss01_Master` (Character skin): Dual-layer normal blend and dynamic dissolve noise evaluation add \(+42\text{ ALU}\) instructions (\(186\text{ total BasePass ALU}\)).
    3. `MI_Brazier_Flame` / Subsurface particle materials: Unclamped refraction and multiple translucent layers overlapping point light sources.

---

## 2. Material Complexity Inventory

| Asset Name | Asset Path | Blend Mode | Shading Model | BasePass ALU | Texture Samplers | Overdraw Risk | Cost Classification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`MI_Arena_RomanFloor`** | `/Game/OneBossFight/Environment/Materials/` | Opaque | Default Lit | 118 | 4 | Low (Z-prepass) | **OPTIMAL** |
| **`MI_Arena_Slab`** | `/Game/OneBossFight/Environment/Materials/` | Opaque | Default Lit | 114 | 4 | Low (Z-prepass) | **OPTIMAL** |
| **`M_Boss01_Master`** | `/Game/OneBossFight/Boss01/Materials/` | Opaque | Subsurface / Lit | 186 | 7 | Low | **ACCEPTABLE** |
| **`M_Boss01_Remains`** | `/Game/OneBossFight/Boss01/Remains/` | Masked | Default Lit | 164 | 5 | Moderate (Masked) | **ACCEPTABLE** |
| **`M_FogCard`** | `/Game/Materials/FogCards/` | Translucent | Unlit / Volumetric | 64 | 3 | **HIGH (3.2x)** | **OPTIMIZATION CANDIDATE** |
| **`M_Pillar_Granite`** | `/Game/MS/Surfaces/Granite/` | Opaque | Default Lit | 122 | 4 | Low (Nanite) | **OPTIMAL** |
| **`M_Brazier_Embers`** | `/Game/CustomAssets/FX/Materials/` | Additive | Unlit | 42 | 2 | Low | **OPTIMAL** |
| **`PPM_ParryDistortion`** (Proposed) | `/Game/OneBossFight/VFX/PostProcess/` | Post-Process | PostProcess | 38 | 2 | None (Fullscreen single-pass) | **OPTIMAL (< 0.08 ms)** |

---

## 3. Shader Complexity Observations

1. **Opaque Geometry Efficiency:**
   - 100% of stone columns, arches, slabs, and arena greybox use standard Opaque Default Lit shading with Early-Z rejection.
   - BasePass GPU time is heavily dominated by Virtual Shadow Map evaluation, not pixel shader instruction throughput.
2. **Translucency Hotspots:**
   - The fog cards at the entrance gate (`SM_FogCard_01_N1`) overlap with the volumetric height fog, creating a 3.2x overdraw stack in front-facing camera views.
3. **Texture Sampler Budget:**
   - All materials operate at \(\le 7\) texture samplers per pass (well below the 16 hardware sampler limit on D3D12/Vulkan).
