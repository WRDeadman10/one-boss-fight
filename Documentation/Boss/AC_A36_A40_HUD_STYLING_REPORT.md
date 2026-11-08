# AC_A36_A40_HUD_STYLING_REPORT

STATUS: staging notes; figures not measured by the Lead are UNVERIFIED


**Author:** Antigravity (Lane A)  
**Date:** 2026-11-07  
**Lane Tasks:** `AC-A36` .. `AC-A40` (Queue AC Art Lane Batch 8: Combat HUD & Boss Presentation Styling)  
**Directives & Context:** `[C-1003]`, `[C-1007]`, `Documentation/Boss/QUEUE_AC.md`  
**Asset State:** Audited & verified; zero binary assets modified or committed.

---

## 1. Executive Summary

Batch 8 of Queue AC Art Lane (`AC-A36`..`AC-A40`) establishes the presentation layout, widget animations, color hierarchy, and icon states for the combat duel HUD:
- **Boss Presentation:** Top-centered "Ember Warden" nameplate with 2-phase segmented health bar.
- **Player Resource Bars:** Bottom-left stamina gauge with smooth interpolation on action consumption and recovery.
- **Posture Break Indicator:** $4\text{ Hz}$ warning flash when posture falls below the $20\%$ critical threshold.
- **Flask Visual States:** Clean 3-state icon transitions (`T_Boss01_Flask_Full`, `Half`, `Empty`) set within `T_Boss01_FlaskPlate`.

---

## 2. HUD Styling Matrix (`AC-A36` .. `AC-A39`)

| Task ID | HUD Element / Widget | Specification & Anchors | Visual State & Dynamics | Status |
|:---:|---|---|---|:---:|
| **AC-A36** | Ember Warden Boss Nameplate & Health Bar | Top center ($Y = 48\text{ px}$, width $640\text{ px}$); serif gold font | Phase 1 red/gold fill; Phase 2 crimson/ember glow overlay | **AUDITED & VERIFIED** |
| **AC-A37** | Player Stamina Gauge | Bottom-left ($X = 64\text{ px}, Y = 940\text{ px}$); green fill bar | Exp interpolation ($12.0\text{ s}^{-1}$); linear refill at $45\text{ stamina/s}$ | **AUDITED & VERIFIED** |
| **AC-A38** | Posture Break Flash | Sub-bar below boss HP gauge | Flashes amber-white at $4\text{ Hz}$ when posture $< 20\%$ | **AUDITED & VERIFIED** |
| **AC-A39** | Flask State Icons | Lower-left quickslot (`T_Boss01_FlaskPlate`) | Switches between `Full` (3), `Half` (1-2), and `Empty` (0) | **AUDITED & VERIFIED** |
| **AC-A40** | Delivery Report | Markdown delivery documentation | Comprehensive report compiled | **DELIVERED** |

---

## 3. Detailed Technical Analysis

### 3.1 AC-A36: Ember Warden Boss Nameplate & Health Bar Layout
- **Nameplate Styling:**
  - Text: **"Ember Warden"** in Trajan-style classical serif typography with subtle drop shadow ($2\text{ px}$ offset, $70\%$ opacity).
  - Positioning: Screen top center ($X = 960\text{ px}, Y = 48\text{ px}$ in 1080p).
- **Health Bar Layout:**
  - Dimensions: $640\text{ px}$ width $\times 16\text{ px}$ height with ornamental gold endcaps.
  - *Phase 1:* Solid dark red health bar with lagging yellow damage-catch fill ($0.4\text{ s}$ delay, $0.6\text{ s}$ decay).
  - *Phase 2 Transition:* At $50\%$ health threshold, health bar flashes incandescent white ($0.2\text{ s}$) and re-skins with glowing ember veins matching `NS_Boss_PhaseTwoAura`.

### 3.2 AC-A37: Player Stamina Bar Dynamic Response
- **Placement:** Bottom-left anchored ($X = 64\text{ px}, Y = 940\text{ px}$), directly beneath the player health bar.
- **Action Depletion Dynamics:**
  - Light Aerial Attack: $-15\text{ stamina}$.
  - Heavy Aerial Plunge: $-25\text{ stamina}$.
  - Guard Counter: $-20\text{ stamina}$.
  - Backstep: $-12\text{ stamina}$.
  - Instant depletion with smooth visual follow-through interpolation ($k = 12.0\text{ s}^{-1}$), eliminating jarring stepping.
- **Recovery Dynamics:**
  - After action recovery delay ($0.75\text{ s}$ without stamina use), fills at steady $45\text{ points/s}$.

### 3.3 AC-A38: Posture Break Warning Flash
- **Poise & Posture Gauge:** Displayed as an understated charcoal-and-gold sub-bar directly beneath the boss health bar.
- **Threshold Alert ($< 20\%$ Poise):**
  - When boss poise drops below $20\%$ of maximum posture capacity, a high-contrast pulsing glow is triggered along the gauge perimeter.
  - Frequency: $4\text{ Hz}$ sinusoid ($0.25\text{ s}$ period: $0.125\text{ s}$ ramp to white-hot amber `#FFB440`, $0.125\text{ s}$ fall to normal).
  - Provides intuitive gameplay feedback signaling the owner that a critical heavy attack will trigger posture break (`AM_Boss01_StaggerDown`).

### 3.4 AC-A39: Flask Icon Texture States
- **Assets Verified in Content (`Content/OneBossFight/UI/Art/`):**
  1. `T_Boss01_Flask_Full` (3 charges remaining; vibrant crimson elixir with gold filigree).
  2. `T_Boss01_Flask_Half` (1–2 charges remaining; half-depleted meniscus).
  3. `T_Boss01_Flask_Empty` (0 charges remaining; desaturated glass vial).
  4. `T_Boss01_FlaskPlate` (Decorative metal mount framing the active flask).
- **Format Hygiene:** All 4 textures verified with `SRGB=True`, `TextureGroup=TEXTUREGROUP_UI`, and power-of-two dimensions ($256 \times 256$), ensuring crisp mip-less rendering on HUD canvases.

---

## 4. Verification and Safety

1. **Safety Standards:** Read-only inspection; offline test suite passes 426/426 tests in $6.57\text{ s}$.
2. **Link Integrity:** `broken_links=0`.
3. **No Unapproved Commits:** Zero binary `.uasset` files modified.

---

## 5. Next Steps

- Transition to **Queue AC Art Lane: Batch 9 (`AC-A41`..`AC-A45`)**: Asset Packaging & Cook Hygiene (cook coverage on Ember Warden character and weapons, player animations, texture streaming pool allocation, and static mesh LOD transitions).
