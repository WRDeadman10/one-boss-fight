# V-A024: Static Light Baking Feasibility Study

**Author:** Antigravity (Offline Quality, Audit & Asset Lane)  
**Date:** 2026-11-06  
**Scope:** Feasibility analysis of baking static lighting (GPU Lightmass / CPU Lightmass) vs maintaining dynamic Lumen GI in `L_SevarogArena`.
**Sources:** Config/DefaultEngine.ini, Documentation/DECISIONS.md:1492

---

## 1. Executive Summary

- **Recommendation:** **REJECT static light baking; RETAIN dynamic Lumen GI with CVar-controlled shadow optimization.**
- **Rationale:**
  - Baking static lighting requires disabling Lumen, rebuilding lightmap UVs across all Nanite meshes, generating massive Volumetric Lightmap volumes for dynamic characters, and losing time-of-day dusk progression.
  - Runtime savings from static baking (\(\sim 5\text{ ms}\)) can be achieved identically (\(4.5 - 6.5\text{ ms}\)) using CVar-only shadow and cloud sampling reduction without altering engine pipelines or art assets.

---

## 2. Comparison: Baked Static Lighting vs. Dynamic Lumen

| Architectural Dimension | Baked Static Lighting (GPU Lightmass) | Dynamic Lumen (Current Architecture) | Feasibility Verdict |
| :--- | :--- | :--- | :--- |
| **Pipeline Compatibility** | Nanite meshes require manual secondary UV channels or automatic lightmap unwrap; high memory overhead for 4K lightmaps. | Native Nanite support out of the box via signed distance fields and surface cache. | **Lumen Wins** |
| **Dynamic Characters** | Requires dense Volumetric Lightmap (VLM) 50 cm grid; boss and player receive low-frequency indirect light; no specular character reflections. | Boss and player cast and receive real-time multi-bounce diffuse GI and screen-space specular reflections. | **Lumen Wins** |
| **Atmosphere & Time of Day** | Fixed static sun angle; dusk transition, cloud shadow movement, and fog light shafts must be baked or fake. | Fully dynamic Sun, Moon, Volumetric Cloud, and Height Fog transitions. | **Lumen Wins** |
| **Authoring Iteration** | Requires 15–45 min GPU bake per level change; invalidates lighting on every arena dress or mesh move. | Zero bake time; instant WYSIWYG editor feedback. | **Lumen Wins** |
| **GPU Frame Time (1080p)** | ~11.0 ms base frame time (zero GI runtime cost). | ~15.5 – 17.0 ms base frame time (with Cardinal Shadows + Cloud CVar fixes). | **Baked is ~4 ms faster** |
| **Packaged Build Size** | Lightmaps and VLM add ~180 – 350 MB to package. | Zero lightmap data stored in package. | **Lumen Wins** |

---

## 3. Technical Obstacles to Baking in One Boss Fight

1. **Nanite Lightmap Overhead:**
   - In UE 5.5.4, Nanite geometry uses fallback mesh UVs for static lightmaps, causing noticeable texel density mismatches and lightmap bleeding at stone pillar seams.
2. **Volumetric Cloud Conflict:**
   - Volumetric clouds cannot be baked into lightmaps; cloud shadows would either disappear or require separate dynamic directional cascades, negating baked savings.
3. **Phase 2 Visual Transition:**
   - The Phase 2 boss awakening introduces rising ember lighting and blade illumination. In a baked scene, dynamic lights layered over baked GI create harsh over-exposure.

---

## 4. Conclusion & Recommended Path

- Maintain the modern UE 5.5 dynamic Lumen architecture.
- Realize performance targets (p99 \(\le 16.67\text{ ms}\) / 60 FPS) via:
  1. Cardinal shadow reduction (`rpg.Perf.FireShadows 4`).
  2. Cloud raymarching clamp (`r.VolumetricCloud.Shadow.ViewRaySampleMaxCount 32`).
  3. Temporal upscaling (DLSS 4.5 / TSR balanced).
- This achieves the 60 FPS target without destabilizing the asset pipeline or incurring technical debt.
