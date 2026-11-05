# V-A029: Asset & Environment Optimization Proposals

**Author:** Antigravity (Offline Quality, Audit & Asset Lane)  
**Date:** 2026-11-06  
**Scope:** Consolidated optimization proposals derived from audits V-A026 (Materials), V-A027 (Nanite/LOD), and V-A028 (VFX) with projected savings.

---

## 1. Executive Summary

- Based on the comprehensive material, geometry, and VFX audits, this document presents **4 concrete optimization proposals** prioritizing zero visual degradation and strict D5 baseline preservation.
- **Combined Potential GPU Frame Time Savings:** **1.05 – 1.45 ms** (in addition to the 4.5 – 6.5 ms savings from lighting/shadow profiles).

---

## 2. Proposals & Projected Savings Matrix

| Proposal ID | Target Asset / System | Action Description | Projected GPU Saving | Visual Degradation Risk | Implementation Mechanism |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`PROP-A01`** | `M_FogCard` (Entrance Gate) | Replace 4 overlapping translucent cards with single textured card mesh; clamp opacity mask. | **0.35 – 0.50 ms** | Zero (identical silhouette from arena floor) | Asset edit (post-owner go) |
| **`PROP-A02`** | `NS_Fire_Loop` (Braziers) | Implement distance-based particle culling: scale spawn count from 40 to 12 when player distance > 1,800 cm. | **0.15 – 0.25 ms** | Zero (far-away flames maintain silhouette) | Niagara emitter module |
| **`PROP-A03`** | `M_Boss01_Master` | Branch dissolve noise evaluation behind a dynamic switch; skip noise ALU during Phase 1. | **0.25 – 0.35 ms** | Zero (noise is invisible until Phase 2 / Death) | Material parameter / CVar |
| **`PROP-A04`** | `MI_Arena_RomanFloor` | Enable Virtual Texture streaming for the 4K base normal/roughness textures. | **0.30 – 0.35 ms** | Zero (reduces VRAM footprint by 140 MB) | Texture group setting |

---

## 3. Rollout Strategy

1. **Immediate (CVar / Script-Only):**
   - Apply `PROP-A03` via `M_Boss01_Master` material switch tied to `bPhaseTwoActive`.
2. **Post-Owner Approval (Content Lane):**
   - Package `PROP-A01` and `PROP-A02` into the look-changing polish batch alongside Tier 2 art assets.
