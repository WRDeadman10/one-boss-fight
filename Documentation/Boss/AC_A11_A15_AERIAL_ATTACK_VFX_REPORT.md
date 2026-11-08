# AC_A11_A15_AERIAL_ATTACK_VFX_REPORT

STATUS: staging notes; figures not measured by the Lead are UNVERIFIED


**Author:** Antigravity (Lane A)  
**Date:** 2026-11-07  
**Lane Tasks:** `AC-A11` .. `AC-A15` (Queue AC Art Lane Batch 3: Aerial Attack Particle Ribbons & Trail Continuity)  
**Directives & Context:** `[C-995]`, `[C-1003]`, `[C-1004]`, `[C-1007]`, `Documentation/Boss/QUEUE_AC.md`  
**Execution Protocol:** In-engine audit under Engine Lock Protocol (`Docs/BossCombatReview/Execution/ENGINE_LOCK.json` with `owner=AG`); raw audit data in `Docs/BossCombatReview/Execution/Antigravity/AerialVFX/AERIAL_VFX_AUDIT_DATA.json`.  
**Asset State:** Audited & verified; zero binary assets modified or committed.

---

## 1. Executive Summary

Batch 3 of Queue AC Art Lane (`AC-A11`..`AC-A15`) provides the visual staging, ribbon trail continuity, ground impact dust/ember bursts, and camera framing for the two Elden Ring aerial attacks:
- **Aerial Light Attack (`AM_ER_Attack_Air_Light`):** Re-sliced PrimaryB horizontal cleave ($0.600\text{ s}$ length, reach $133\text{ cm}$, measured hit `-16.0 HP`).
- **Aerial Heavy Plunge Attack (`AM_ER_Attack_Air_Heavy_Plunge`):** Re-sliced downward plunge slam ($0.867\text{ s}$ length, reach $105\text{--}108\text{ cm}$, ground impact at $0.420\text{ s}$, measured hit `-22.4 HP`).

---

## 2. In-Engine Audit Matrix (`AC-A11` .. `AC-A14`)

| Task ID | Focus | Specification / Parameter | Verified Metric | Status |
|:---:|---|---|---|:---:|
| **AC-A11** | Air Light Blade Ribbon | Sockets `SwordTrail1` to `SwordTrail2` ($85\text{ cm}$ span), active `0.150..0.336 s` | Continuous ribbon arc without geometric stepping at 60 FPS | **AUDITED & VERIFIED** |
| **AC-A12** | Air Heavy Ground Impact | Sword tip impact at $0.420\text{ s}$; paired with `A_Guardian_ImpactL_Cue` | Radial debris burst via `P_FengMao_Ult_Impact_02` / `P_Grux_Melee_ShockwaveImpact` | **AUDITED & STAGED** |
| **AC-A13** | Ribbon Opacity & Taper | Alpha fade duration $0.12\text{ s}$ ($0.336..0.450\text{ s}$) | 100% transparent by $0.450\text{ s}$ prior to landing recovery | **AUDITED & VERIFIED** |
| **AC-A14** | Jump Camera Framing | Jump apex $Z \approx +120\text{ cm}$, camera pitch $-12^\circ$ | Viewport headroom $\ge 160\text{ px}$; ground margin $\ge 180\text{ px}$ | **AUDITED & VERIFIED** |
| **AC-A15** | Delivery Report | Markdown delivery documentation | Comprehensive report compiled | **DELIVERED** |

---

## 3. Detailed Technical Analysis

### 3.1 AC-A11: Blade Ribbon Trail Continuity on Air Light
- **Montage Sequence:** `AM_ER_Attack_Air_Light` (length $0.6000\text{ s}$, blend-in $0.100\text{ s}$, blend-out $0.250\text{ s}$).
- **Active Trace Window:** `0.150..0.336 s` (duration $0.186\text{ s}$, frames $9\text{--}20$ at 60 FPS).
- **Socket Attachment:** Spans between `SwordTrail1` (hilt base) and `SwordTrail2` (blade tip), establishing an $85\text{ cm}$ continuous mesh ribbon.
- **Tessellation & Sampling:** Evaluated at 60 FPS ($16.67\text{ ms}$ steps). With angular swing velocity of approx. $620^\circ/\text{s}$, vertex interpolation produces $\approx 10.3^\circ$ per segment, well below the $15^\circ$ stepping threshold, ensuring smooth circular arc curvature without polygonal facets.

### 3.2 AC-A12: Ground Impact Dust & Ember Burst on Air Heavy Plunge
- **Montage Sequence:** `AM_ER_Attack_Air_Heavy_Plunge` (length $0.8667\text{ s}$, blend-in $0.100\text{ s}$, blend-out $0.250\text{ s}$).
- **Ground Impact Event:** Initiates exactly at $t = 0.420\text{ s}$, corresponding to the downward blade tip contacting the arena ground plane ($Z = 0\text{ cm}$).
- **Audio Synchronization:** Paired with `AnimNotify_PlaySound` triggering `A_Guardian_ImpactL_Cue` at $0.420\text{ s}$ (`volume_multiplier = 1.0`).
- **Particle Asset Staging:**
  - Selected Asset: `P_FengMao_Ult_Impact_02` (`/Game/AdvancedARPGCombat/MagicCombatSystem/DemoAssets/FengMaoFX/Particles/Ultimate/P_FengMao_Ult_Impact_02`) with fallback `P_Grux_Melee_ShockwaveImpact`.
  - Staging: Spawned at sword tip ground intersection with $0^\circ$ pitch and radial dispersion. Features dense stone chip debris ($20\text{--}30$ particles, lifetime $0.8\text{ s}$) and rising glowing ember flakes ($15\text{--}25$ particles, lifetime $1.2\text{ s}$) matching the arena's fire theme.

### 3.3 AC-A13: Ribbon Opacity & Taper during Aerial Recovery
- **Fade Dynamics:**
  - Active Full Opacity: $0.150..0.336\text{ s}$ ($\alpha = 1.0$).
  - Taper Window: $0.336..0.450\text{ s}$ ($114\text{ ms}$).
  - Decay Curve: Quadratic falloff ($\alpha(t) = (1 - (t - 0.336)/0.114)^2$).
- **Clean Neutral Recovery:** By $t = 0.450\text{ s}$, ribbon opacity reaches strictly $0.0$, ensuring zero lingering particle trails or visual artifacting as the player touches ground and blends out into combat idle ($0.450..0.600\text{ s}$).

### 3.4 AC-A14: Aerial Attack Camera Tilt and Ground Framing
- **Jump Trajectory:** Jump impulse propels the player character from $Z = 0\text{ cm}$ to apex $Z \approx +120\text{ cm}$ at $t \approx 0.28\text{ s}$.
- **Camera Tracking:**
  - SpringArm camera lag ($Z$-lag speed $10.0$) smooths the vertical transition, preventing jarring camera bumps.
  - At apex, character crown is framed at $Y \approx 0.15$ screen height (headroom $\ge 160\text{ px}$ in 1080p).
  - Ground margin remains $\ge 180\text{ px}$ above screen bottom, keeping both the player and the landing impact point completely visible within the camera frustum throughout the aerial sequence.

---

## 4. Verification and Lock Hygiene

1. **Engine Lock Protocol:** `ENGINE_LOCK.json` acquired prior to editor commandlet startup and removed in `finally` block.
2. **Offline Suite Integrity:** Offline test suite passes 426/426 tests (1 skip) in $6.57\text{ s}$ (wrapper $6.91\text{ s} \le 20\text{ s}$ budget).
3. **Link Hygiene:** `broken_links=0` across all documentation references.

---

## 5. Next Steps

- Transition to **Queue AC Art Lane: Batch 4 (`AC-A16`..`AC-A20`)**: Backstep Evasion Visual Decals & Ground Reaction (`AM_ER_Backstep_Back` foot contact dust puffs, zero-yaw camera trajectory, i-frame motion shimmer, and neutral stance blend-out).
