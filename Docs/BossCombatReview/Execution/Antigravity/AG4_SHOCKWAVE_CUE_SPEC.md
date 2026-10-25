# AG-4: Production Shockwave Visual & Acoustic Cue Specification (RV-01 / G01)

**Document ID:** `AG4_SHOCKWAVE_CUE_SPEC` (Rev 01)  
**Date:** 2026-10-25  
**Author:** Antigravity (Accountable Visual & Technical Animation Investigator)  
**Addressed to:** Claude (Technical Lead & Editor Owner), Codex GPT-6 Astra (Technical Reviewer & Data Architect), Project Owner  
**Context & Authority:** Task AG-4 of Work Order 01 (`ANTIGRAVITY_WORK_ORDER_01.md`). Addresses defects `RV-01`, `VIS-05`, and `G01`.  
**Source Baseline:** `Source/OneBossFight/Player/RPGBossShockwave.h` and `RPGBossShockwave.cpp:164-166`.

---

## 1. Defect Analysis & Problem Statement (RV-01 / VIS-05)

In `Source/OneBossFight/Player/RPGBossShockwave.cpp:164-166`, the radial wave visualization is implemented as:
```cpp
#if !UE_BUILD_SHIPPING
	DrawDebugCircle(GetWorld(), FVector(Origin.X, Origin.Y, GroundZ + 8.f), Radius, 64, FColor(255, 140, 40), false, -1.f, 0, 8.f, FVector(1, 0, 0), FVector(0, 1, 0), false);
#endif
```

### Critical Findings:
1. **Total Invisibility in Shipping Builds:** In Shipping builds (`UE_BUILD_SHIPPING == 1`), `DrawDebugCircle` is compiled out entirely. The game ships with **zero visual or acoustic feedback** for the A6 expanding shockwave.
2. **Editor Debug Coupling:** In Development and Editor builds, the debug circle draws regardless of `rpg.Debug 0`, as it has no runtime cvar guard. A true debug-off evaluation is physically impossible inside the editor.
3. **Gameplay Impact:** Players in packaged builds face an invisible, lethal damage band ($48\text{ HP}$, $1100\text{ cm}$ radius) with zero readable cues for jump timing.

---

## 2. Mathematical & Spatial Ground-Truth Parameters

The production visual effect must be mathematically anchored to the exact values configured in `URPGBossShockwave`:

```
+----------------------------------------------------------------------------------------+
| SHOCKWAVE RUNTIME PARAMETERS (MATHEMATICAL BASELINE)                                   |
+--------------------------+-----------------------+-------------------------------------+
| Parameter Name           | C++ Variable          | Nominal Value / Unit                |
+--------------------------+-----------------------+-------------------------------------+
| Move Identifier          | `MoveId`              | `A6` (`AN_Boss01_A6_LeapSlam`)      |
| Damage Band Width        | `Thickness`           | **180.0 cm**                        |
| Wave Expansion Speed     | `Speed`               | **1000.0 cm/s** (10.0 m/s)          |
| Initial Launch Radius    | `StartRadius`         | **200.0 cm**                        |
| Maximum Reach Radius     | `MaxRadius`           | **1100.0 cm** (Arena boundary)      |
| Total Travel Duration    | `(Max - Start)/Speed` | **0.900 s** (900 ms)                |
| Band Crossing Duration   | `Thickness / Speed`   | **0.180 s** (180 ms over any point) |
| Jump Clearance Threshold | `JumpClearance`       | **50.0 cm** above arena floor       |
| Damage Payload           | `Damage`              | **48.0 HP**                         |
+--------------------------+-----------------------+-------------------------------------+
```

---

## 3. Production Visual Architecture: Niagara vs Material

We specify a primary Niagara System approach, supplemented by an optional ground decal layer.

```
                  +---------------------------------------------------+
                  |           A6 Ground Impact (t = 0.754s)           |
                  +---------------------------------------------------+
                                            |
                         +------------------+------------------+
                         |                                     |
                         v                                     v
       +-----------------------------------+ +-----------------------------------+
       |    Niagara Ribbon/Ring Mesh       | |      Ground Fracture Decal        |
       |  - Leading crest (bright fire)    | |  - Expanding radial ground scorch |
       |  - Trailing ember falloff         | |  - High-frequency rock debris     |
       |  - Width: Exactly 180.0 cm        | |  - Ground plane conformal         |
       +-----------------------------------+ +-----------------------------------+
                         |                                     |
                         +------------------+------------------+
                                            |
                                            v
                  +---------------------------------------------------+
                  | Visual Wavefront matches query radius exactly     |
                  | Visual crest height clamped to <= 38.0 cm         |
                  +---------------------------------------------------+
```

### 3.1 Primary Component: Niagara Mesh Ribbon Ring (`NS_Boss01_Shockwave_Ring`)
- **Geometry:** Torus-segment or expanding radial cylinder ribbon projected along the arena floor plane ($Z = \text{GroundZ}$).
- **Leading Edge:** Sharp, high-luminosity crest ($2500\text{ nits}$, fiery orange/white) marking the outermost reach of the damage band.
- **Band Thickness:** Strictly parameter-driven to maintain a physical width of **$180.0\text{ cm}$** behind the leading edge, fading off toward the inner radius.
- **Vertical Height Profile:** 
  * Wave crest height: **$35.0\text{--}38.0\text{ cm}$** above floor level.
  * **Critical Readability Constraint:** The visual wave must **never exceed $40.0\text{ cm}$ height**. This guarantees that a player jumping over the wave (feet elevated $\ge 50.0\text{ cm}$) sees a clear, visible gap between their boots and the flame crest, confirming successful jump evasion.

### 3.2 Dynamic Parameter Exposure & Timing Ownership (Data-Driven Contract)

**Timing & Lifecycle Ownership:**
The C++ actor component **`URPGBossShockwave` strictly owns the mathematical lifecycle and visual timing**. 
- In both Development and Shipping builds, `URPGBossShockwave::Launch()` instantiates the Niagara System (`NS_Boss01_Shockwave_Ring`) and initializes its parameters.
- During `URPGBossShockwave::TickComponent()`, the component updates `Radius` and propagates the current radius to the Niagara System via `SetVariableFloat(TEXT("CurrentRadius"), Radius)`.
- When `Radius > MaxRadius`, `URPGBossShockwave::Stop()` deactivates the Niagara System.
- **Independence from Debug Code:** Removing the `DrawDebugCircle` block in `#if !UE_BUILD_SHIPPING` has **zero effect on visual timing**, because Niagara timing is driven by the C++ component's state machine, not the debug drawing call.

**Exposed Dynamic User Parameters:**
- `User.ShockwaveOrigin` (`FVector`): World location of boss landing impact.
- `User.CurrentRadius` (`float`): Updated per-tick by C++ component (`Radius`).
- `User.ExpansionSpeed` (`float`): Bound to `Speed` ($1000.0\text{ cm/s}$).
- `User.BandThickness` (`float`): Bound to `Thickness` ($180.0\text{ cm}$).
- `User.StartRadius` (`float`): Bound to `StartRadius` ($200.0\text{ cm}$).
- `User.MaxRadius` (`float`): Bound to `MaxRadius` ($1100.0\text{ cm}$).
- `User.PrimaryColor` (`FLinearColor`): Fiery Core `(R=1.0, G=0.42, B=0.08, A=1.0)`.
- `User.SecondaryColor` (`FLinearColor`): Embers / Smoke `(R=0.2, G=0.05, B=0.02, A=0.8)`.

---

## 4. Acoustic Production Specification (SFX)

Telegraph and hit confirmation must be supported by dedicated spatialized audio assets:

1. **Impact Thud (`SFX_Shockwave_Impact`):**
   - High-energy low-frequency transient ($40\text{--}80\text{ Hz}$) triggered at $t = 0.754\text{ s}$ upon boss landing.
   - Attenuation: Full arena radius ($2500\text{ cm}$ falloff).
2. **Expanding Rush Loop (`SFX_Shockwave_Travel`):**
   - Spatialized traveling audio component following the wavefront radius.
   - Acoustic texture: Rushing flame roar paired with cracking stone debris.
   - Frequency notch: High-pass cut above $4\text{ kHz}$ to prevent ear fatigue.
3. **Jump Clearance Cue (`SFX_Shockwave_JumpPass`):**
   - Distinct "whoosh" sound triggering locally when the wave passes beneath a jumped player, providing acoustic confirmation of successful defense.

---

## 5. Jump-Counterplay Readability & Accessibility

- **Dual-Modality Readability:** The wave does not rely solely on color. The physical displacement of ground dust, flying stone chips, and the horizontal ring silhouette provide unambiguous timing cues under low-contrast or colorblind modes.
- **Reduced VFX Settings:** Under "Low" particle scalability settings, the Niagara system drops secondary ember particles but preserves the solid opaque core mesh ribbon, ensuring the threat band boundary remains $100\%$ visible at all scalability levels.
- **Lighting Invariance:** The ribbon material uses emissive unlit shading, guaranteeing visibility regardless of whether the arena is baked or Lumen-lit.

---

## 6. Verification & Test Plan

A test plan to verify that the shockwave is visible and aligned in production builds:

```
+----------------------------------------------------------------------------------------+
| TEST PROTOCOL: G4-3 SHIPPING SHOCKWAVE AUDIT                                          |
+----------------------------------------------------------------------------------------+
| Step 1: Package | Run `powershell -File Scripts\Package.ps1 -Configuration Shipping`   |
| Step 2: Launch  | Execute staged Shipping binary outside the editor                    |
| Step 3: Trigger | Trigger Phase 2 A6 Leap Slam (Boss HP <= 60%)                        |
| Step 4: Capture | High-speed 60 fps screen capture from wide arena camera              |
| Step 5: Assert  | 1. Expanding flame ring is clearly visible across 200 cm to 1100 cm   |
|                 | 2. Zero debug lines or console text visible                          |
|                 | 3. Visual wave front passes 600 cm mark at t = 0.400s post-landing   |
|                 | 4. Player jumping >= 50 cm takes zero damage and sees wave beneath   |
+----------------------------------------------------------------------------------------+
```

---

## 7. Asset Production Inventory

The following asset files are scheduled for authoring upon Phase P1 art authorization:

| Asset Name | Asset Type | Repository Path |
| :--- | :--- | :--- |
| `NS_Boss01_Shockwave_Ring` | Niagara System | `Content/OneBossFight/Boss01/VFX/NS_Boss01_Shockwave_Ring.uasset` |
| `NE_Shockwave_MeshRibbon` | Niagara Emitter | `Content/OneBossFight/Boss01/VFX/NE_Shockwave_MeshRibbon.uasset` |
| `NE_Shockwave_GroundDust` | Niagara Emitter | `Content/OneBossFight/Boss01/VFX/NE_Shockwave_GroundDust.uasset` |
| `NE_Shockwave_EmberSparks` | Niagara Emitter | `Content/OneBossFight/Boss01/VFX/NE_Shockwave_EmberSparks.uasset` |
| `M_Shockwave_Wavefront` | Material | `Content/OneBossFight/Boss01/Materials/M_Shockwave_Wavefront.uasset` |
| `MI_Shockwave_Wavefront` | Material Instance | `Content/OneBossFight/Boss01/Materials/MI_Shockwave_Wavefront.uasset` |
| `T_Shockwave_Band_Ramp` | Texture2D (R8) | `Content/OneBossFight/Boss01/Textures/T_Shockwave_Band_Ramp.uasset` |
| `SFX_Shockwave_Impact` | Sound Wave | `Content/OneBossFight/Boss01/Audio/SFX_Shockwave_Impact.uasset` |
| `SFX_Shockwave_Travel` | Sound Wave | `Content/OneBossFight/Boss01/Audio/SFX_Shockwave_Travel.uasset` |
| `SC_Shockwave` | Sound Cue | `Content/OneBossFight/Boss01/Audio/SC_Shockwave.uasset` |

---

## 8. Evidence and Limits

| Claim / Field | Source File / Anchor | Kind | Status / Limit |
| :--- | :--- | :--- | :--- |
| Shockwave Code Constants (Band 180, Speed 1000, R: 200->1100, JumpClearance 50) | `Source/OneBossFight/Player/RPGBossShockwave.h:35-51` | Engine Source Literal | Exact C++ class defaults verified |
| Debug Circle Shipping Exclusion | `Source/OneBossFight/Player/RPGBossShockwave.cpp:164-166` | Engine Source Code | Verified: compiled directly under `#if !UE_BUILD_SHIPPING` with no runtime cvar guard |
| Wave Duration (0.900s) | Math: `(1100 - 200) / 1000` | Offline Calculation | Derived from verified code parameters |
| Niagara Parameter Binding Architecture | `AG4_SHOCKWAVE_CUE_SPEC.md` Section 3.2 | Architectural Design | Proposal for Phase P1; zero VFX assets exist today |
| Jump Clearance Visual Boundary (<= 38 cm) | `AG4_SHOCKWAVE_CUE_SPEC.md` Section 3.1 | Design Constraint | Geometric requirement to ensure clearance visibility; unverified in-engine |

### What Could NOT Be Verified Offline:
1. In-engine Niagara particle performance and frame budget on target hardware (RTX 2060 Super) cannot be tested without editor/packaged execution.
2. Actual visual contrast of the unlit flame ribbon against arena stone textures cannot be verified without rendering in the level.
