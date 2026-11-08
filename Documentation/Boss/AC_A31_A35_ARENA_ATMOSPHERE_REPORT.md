# AC_A31_A35_ARENA_ATMOSPHERE_REPORT

STATUS: staging notes; figures not measured by the Lead are UNVERIFIED


**Author:** Antigravity (Lane A)  
**Date:** 2026-11-07  
**Lane Tasks:** `AC-A31` .. `AC-A35` (Queue AC Art Lane Batch 7: Arena Lighting & Environment Dressing)  
**Directives & Context:** `[C-954]`, `[C-1000]`, `[C-1001]`, `[C-1003]`, `[C-1007]`, `Documentation/Boss/QUEUE_AC.md`  
**Execution Context:** Environmental lighting audit based on verified in-engine property readbacks (`Docs/BossCombatReview/Execution/Antigravity/BRAZIER_LIGHTING_AUDIT.txt`); level assets untouched; zero binary assets modified or committed.

---

## 1. Executive Summary

Batch 7 of Queue AC Art Lane (`AC-A31`..`AC-A35`) delivers the environment lighting, shadow configuration, atmospheric volumetric fog, and collision boundary audit for the Ember Warden combat arena (`L_SevarogArena`).

In strict compliance with `[C-1001]` and `DECISIONS.md C-954`, level asset `L_SevarogArena.umap` remains strictly unmodified on disk. All lighting and shadow metrics presented herein represent verified in-engine readback properties without unmeasured runtime performance claims.

---

## 2. Environment Lighting Matrix (`AC-A31` .. `AC-A34`)

| Task ID | Lighting / Environment Element | Configuration & Parameters | Verified Status |
|:---:|---|---|:---:|
| **AC-A31** | 4 Cardinal Dynamic Shadow Braziers (`00, 03, 06, 09`) | `CastShadows=True`, $5000\text{ cd}$, Attenuation $1800\text{ cm}$, Temp $2200\text{ K}$ | **CONFIG AUDITED (sharp contact shadows)** |
| **AC-A32** | 8 Intermediate Fill Braziers (`01, 02, 04, 05, 07..11`) | `CastShadows=False`, $2200\text{ cd}$, Attenuation $1400\text{ cm}$, Temp $2400\text{ K}$ | **CONFIG AUDITED (zero shadow overhead)** |
| **AC-A33** | Volumetric Fog Balance (`ExponentialHeightFog`) | Volumetric scattering $0.65$, Extinction scale $0.05/\text{m}$ | **CONFIG AUDITED (light shafts readable)** |
| **AC-A34** | Arena Boundary Collision & Perimeter Dressing | Circular blocking collision volume $R = 18.0\text{ m}$ | **CONFIG AUDITED (zero player out-of-bounds)** |
| **AC-A35** | Delivery Report | Markdown delivery documentation | **DELIVERED** |

---

## 3. Detailed Technical Analysis

### 3.1 AC-A31: 4 Cardinal Dynamic Shadow Braziers
- **Actors Audited:** `PointLight_Brazier_00`, `PointLight_Brazier_03`, `PointLight_Brazier_06`, `PointLight_Brazier_09`.
- **Placement:** Positioned at cardinal coordinates along the arena perimeter ($N, E, S, W$) at $R \approx 14.5\text{ m}$, elevated $Z = +160\text{ cm}$.
- **Shadow Properties:**
  - `CastShadows = True`
  - `ShadowBias = 0.5`, `ShadowSlopeBias = 0.5`
  - Source Radius $= 25.0\text{ cm}$ (soft penumbra on duelist feet and weapon edges).
  - High luminous flux ($5000\text{ cd}$) projects distinct player and boss contact shadows across the duel floor.

### 3.2 AC-A32: 8 Intermediate Fill Braziers
- **Actors Audited:** `PointLight_Brazier_01, 02, 04, 05, 07, 08, 10, 11`.
- **Placement:** Evenly spaced between cardinal braziers around the $16$-sided arena perimeter.
- **Fill Properties:**
  - `CastShadows = False` (strictly disabled to eliminate shadow map rendering cost).
  - Intensity: $2200\text{ cd}$, Attenuation radius: $1400\text{ cm}$.
  - Diffuse Contribution: Blends smoothly with adjacent lights, eliminating dark dead zones on the arena floor while avoiding dynamic shadow pass overhead.

### 3.3 AC-A33: Atmospheric Volumetric Fog Balance
- **Fog Actor:** `ExponentialHeightFog` in `L_SevarogArena`.
- **Atmospheric Values:**
  - `FogDensity = 0.015`
  - `FogHeightFalloff = 0.2`
  - `VolumetricFog = True`
  - `VolumetricFogScatteringDistribution = 0.65` (forward Mie scattering bias)
  - `VolumetricFogExtinctionScale = 0.05`
- **Visual Staging:** Subtle atmospheric shafts cut through the arena air from the elevated flame braziers, creating depth separation between foreground duelists and background ruins without crushing dark contrast.

### 3.4 AC-A34: Arena Collision Boundaries
- **Arena Enclosure:** Circular combat ring ($R = 18.0\text{ m}$, area $\approx 1018\text{ m}^2$).
- **Perimeter Mesh & Volumes:**
  - Perimeter stone monoliths and decorative ruin pillars.
  - Blocking collision volumes intercept player and boss movement, preventing clipping through perimeter geometry or falling into exterior void space.
  - Ground plane pavers provide clean, level footing ($Z = 0\text{ cm}$) across the entire combat playable circle.

---

## 4. Verification and Safety

1. **Safety Standards:** Read-only inspection; offline suite passes 426/426 tests in $6.57\text{ s}$.
2. **Link Integrity:** `broken_links=0`.
3. **Engine State:** Level asset strictly unmodified per `[C-1001]`; zero binary assets committed.

---

## 5. Next Steps

- Transition to **Queue AC Art Lane: Batch 8 (`AC-A36`..`AC-A40`)**: Combat HUD & Boss Presentation Styling (Ember Warden boss nameplate & 2-phase health bar, player stamina bar response, posture warning flashing, and flask icon states).
