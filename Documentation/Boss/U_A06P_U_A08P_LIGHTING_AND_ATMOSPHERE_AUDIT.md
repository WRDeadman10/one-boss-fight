# Queue U: Arena Lighting & Atmosphere Performance Audit (U-A06p .. U-A08p)

**Date:** 2026-11-05
**Author:** Antigravity (Quality & Performance Lane)
**Task Scope:** U-A06p (Arena Lighting Audit & Shadow Cost Classes), U-A07p (Shadow-Caster Reduction Proposal), U-A08p (Volumetric Cloud & Sky Cost Proposal)
**References:** [C-893], [C-895], [C-896], [C-897], `U-C01_GPU_COST_MODEL.md`, `U-C05_PREDICTED_GPU_BUDGET.md`, `Scripts/Editor/atmosphere.py`, `Scripts/Editor/dress_arena.py`

---

## 1. U-A06p: Authoritative Arena Lighting Audit (`L_SevarogArena`)

Based on the level construction and dressing scripts (`Scripts/Editor/dress_arena.py`, `atmosphere.py`, `Source/OneBossFight/Arena/RPGFireSource.cpp`), the lighting, shadow, and atmospheric setup of `L_SevarogArena` is inventoried below:

| Actor / Component Label | Class | Mobility | Intensity / Units | Radius / Distance | Casts Shadows | Cost Class | Observed / Model Cost |
|---|---|---|---|---|---|---|---|
| **`BrazierFire_00` .. `BrazierFire_11`** (12 braziers) | `ARPGFireSource` &rarr; `UPointLightComponent` | Movable | 5,000.0 lm | 3,200.0 cm ($32\text{ m}$) | **Yes** (dynamic VSM) | **CRITICAL / EXTREME** | **~8.50 ms** p99 delta in Round 2 E18; overlapping 32m radius VSM passes across Nanite & non-Nanite geometry. |
| **`LanternFire`** (16 lanterns) | `ARPGFireSource` &rarr; `UPointLightComponent` | Movable | 900.0 lm | 1,800.0 cm ($18\text{ m}$) | No | **LOW** | Unshadowed deferred point lights, batched effectively. |
| **`CandleFire`** (12 groups) | `ARPGFireSource` &rarr; `UPointLightComponent` | Movable | 40.0 lm | 500.0 cm ($5\text{ m}$) | No | **NEGLIGIBLE** | Micro-fill point lights, zero shadow overhead. |
| **`Sun`** | `ADirectionalLight` &rarr; `UDirectionalLightComponent` | Movable | 3.2 lux (pitch 2.5°, yaw 215°) | Dynamic dist: 9,000 cm | **Yes** (Volumetric + Cascaded/VSM) | **HIGH** | Primary directional shadow caster, raking dusk angle, light shaft bloom. |
| **`Moon`** | `ADirectionalLight` &rarr; `UDirectionalLightComponent` | Movable | 2.6 lux (pitch -36°, yaw 240°) | Dynamic dist: 9,000 cm | **Yes** (Volumetric + Cascaded/VSM) | **HIGH** | Secondary directional shadow caster, maintains scene readability post-sunset. |
| **`SkyLight`** | `ASkyLight` &rarr; `USkyLightComponent` | Movable | 1.1 | Global | Real-Time Capture = **True** | **MEDIUM / HIGH** | Continuous real-time reflection capture feeds Lumen diffuse indirect and specular probes. |
| **`DuskFog`** | `AExponentialHeightFog` | — | Density 0.011 / 0.05 | Dist: 8,000 cm | Enable Volumetric = **True** | **MEDIUM / HIGH** | Volumetric raymarching against Sun & Moon shadow volumes. |
| **`CloudDeck`** | `AVolumetricCloud` &rarr; `UVolumetricCloudComponent` | — | Material: `m_SimpleVolumetricCloud_Inst` | Alt: 4 km, H: 7 km | View raymarching | **VERY HIGH** | **5.30 ms** single-frame cost in ProfileGPU (`game1_OneBossFight.log:1862`). |
| **`DuskPost`** | `APostProcessVolume` (Unbound) | — | Lumen Quality 2.0 | Global | Dynamic GI & Reflections = **Lumen** | **VERY HIGH** | Primary GI & reflection pass (~10-12 ms inclusive). |

---

## 2. U-A07p: Shadow-Caster Reduction Proposals (CVar-Only vs. Asset Edits)

The 12 perimeter braziers currently cast dynamic virtual shadow maps with an expansive $32\text{ m}$ radius, creating massive overlap in the arena center where the duel occurs.

### 2.1 CVar-Only Proposals (Zero Asset Edits, Approved for Round 5 Experiments)
In `Source/OneBossFight/Arena/RPGPerfSwitches.cpp`, runtime switches already exist in non-Shipping builds:

1. **Option A: Cardinal Shadowing (`rpg.Perf.FireShadows 4`)**
   - **Configuration:** Only the 4 cardinal braziers (00, 03, 06, 09) cast dynamic shadows; the remaining 8 braziers cast diffuse light only.
   - **Predicted Saving:** **4.0 to 5.5 ms** GPU frame time.
   - **Visual Cost:** **Very Low.** All 12 braziers retain their fire, smoke, sparks, audio crackle, and warm lighting. The player and boss still cast radial shadows onto the arena floor from the 4 primary directions.
2. **Option B: Fire Radius Contraction (`rpg.Perf.FireRadiusScale 0.65` + `rpg.Perf.FireShadows 4`)**
   - **Configuration:** Contraction of brazier attenuation radius from 3,200 cm to 2,080 cm ($35\%$ contraction), reducing the quadratic illumination area by $\sim 58\%$.
   - **Predicted Saving:** **5.5 to 6.5 ms** GPU frame time.
   - **Visual Cost:** **Low.** Slightly darker arena center, raked shadows localized to the perimeter where braziers stand.
3. **Option C: Brazier Shadows Off (`rpg.Perf.FireShadows 0`)**
   - **Configuration:** All 12 braziers unshadowed; directional shadows from Sun and Moon remain intact.
   - **Predicted Saving:** **7.0 to 8.5 ms** GPU frame time (matching historical E18 delta: -8.5 ms p99).
   - **Visual Cost:** **Medium.** Radial shadows from fires are lost; characters cast shadows exclusively from Sun/Moon.

### 2.2 Asset-Level Proposal (Owner Decision Only)
- If the owner approves visual changes after Round 5:
  - Update `dress_arena.py` line 398 to set `shadows = (i % 3 == 0)` (4 cardinal lights cast shadows).
  - Bake static lighting into lightmaps for the static perimeter columns and floor, leaving only dynamic shadows for movable characters.

---

## 3. U-A08p: Volumetric Cloud & Sky Cost Proposals (CVar-Level)

### 3.1 Cloud Raymarching Scaling (Zero Look Change, Approved for Round 5)
Volumetric clouds account for $\sim 5.30\text{ ms}$ of render time. Raymarching sample count can be scaled down via standard Unreal CVars without removing the clouds:

1. **Cloud Sample Scale (`r.VolumetricCloud.ViewRaySampleCountScale 0.5`)**
   - Halves the number of raymarch samples through the cloud layer.
   - **Predicted Saving:** **2.0 to 2.8 ms** GPU frame time.
   - **Visual Cost:** **Negligible.** Minor boundary softening at horizon distances; identical cloud shapes, sky silhouette, and sunset colors.
2. **Cloud Shadow Sample Scale (`r.VolumetricCloud.Shadow.ViewRaySampleCountScale 0.5`)**
   - Halves secondary shadow samples inside the cloud deck.
   - **Predicted Saving:** **0.8 to 1.2 ms** GPU frame time.
   - **Visual Cost:** **None.**

### 3.2 SkyLight Optimization
1. **Real-Time Capture Rate Limit (`r.SkyLight.RealTimeReflectionCapture 0` or cached)**
   - Re-capturing the sky every frame in a fixed-time-of-day dusk arena is unnecessary.
   - **Predicted Saving:** **1.2 to 1.8 ms** GPU frame time.
   - **Visual Cost:** **Zero.** Time of day in `L_SevarogArena` does not rotate dynamically during the boss duel.

---

## 4. Cumulative Performance Projection with DLSS 4.5

Combining these measure-and-propose variables with NVIDIA DLSS 4.5 (enabled in BUILD-223):

| Optimization Layer | Applied Controls | Predicted GPU Saving | Estimated GPU Time (RTX 3060) |
|---|---|---|---|
| **Round 4 Baseline** | Authored settings, TSR native | — | **~42.85 ms** (27.10 FPS) |
| **Layer 1: DLSS SR Quality** | `r.NGX.DLSS.Enable 1`, Quality mode ($1280\times 720 \to 1080\text{p}$) | -12.0 to -14.0 ms | **~29.0 to 30.5 ms** (~33 FPS) |
| **Layer 2: Brazier Shadows (Option A)** | `rpg.Perf.FireShadows 4` | -4.5 to -5.5 ms | **~24.0 to 25.5 ms** (~40 FPS) |
| **Layer 3: Cloud & SkyLight CVars** | `r.VolumetricCloud.ViewRaySampleCountScale 0.5`, SkyLight static | -3.5 to -4.5 ms | **~20.0 to 21.5 ms** (~48 FPS) |
| **Layer 4: DLSS Performance / Balanced** | DLSS Balanced ($1114\times 626$) or Performance ($960\times 540$) | -4.0 to -6.0 ms | **~15.5 to 17.5 ms** (**58 - 64 FPS**) |

**Conclusion:** Achieving the 60 FPS / 16.67 ms gate is mathematically feasible on the RTX 3060 proxy using **DLSS Quality/Balanced combined with CVar-level shadow scaling (4 braziers) and cloud sample reduction**, requiring **zero asset edits** and preserving the authored artistic look.
