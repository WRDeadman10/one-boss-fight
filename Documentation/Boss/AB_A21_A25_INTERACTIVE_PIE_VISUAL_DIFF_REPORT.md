# AB_A21_A25_INTERACTIVE_PIE_VISUAL_DIFF_REPORT

STATUS: staging notes; figures not measured by the Lead are UNVERIFIED


**Author:** Antigravity (Lane A)  
**Date:** 2026-11-07  
**Lane Tasks:** `AB-A21` .. `AB-A25` (Queue AB Art Batch 5)  
**Directives & Constraints:** `[C-985]`, `[C-998]`, `[C-999]`, `[C-1000]`, `[C-1001]`, `Documentation/Boss/QUEUE_AB.md`  
**Environment Note:** Headless automated commandlet processes lack an active display swapchain (`KI-188`); interactive PIE provides authoritative ground-truth validation.

---

## 1. Executive Summary

This report delivers the execution protocol, frame-level visual checkpoints, and observation run sheets for **Queue AB Art Batch 5 (`AB-A21`..`AB-A25`)**.

Building upon the accepted C-995 re-sliced animations, Lead PIE reach measurements (`P_C992_AIRHITS`: AirLight 133 cm, AirHeavy 105–108 cm), and Tier 2 camera framing audits, these 5 cases establish the definitive interactive review sheet for the owner's PIE evaluation session in `L_SevarogArena`.

---

## 2. Test Cases and Visual Checkpoints

### AB-A21: Case 1 — Guard Counter Visual Verification
- **Activation Sequence:** Hold Block (`Right Mouse` / `L1`), absorb incoming boss strike, then immediately input Heavy Attack (`Left Shift + LMB` / `R2`).
- **Visual Staging Checkpoints:**
  1. *0.000..0.123 s:* Greystone absorbs impact; sword resets into low counter-thrust posture. Direction lock maintains character facing toward Sevarog (`ANS_SetDesiredRotation_C`).
  2. *0.168 s:* Hit trace window initiates (`ANS_CollisionTrace_C`); blade sweeps upward and forward.
  3. *0.257 s:* Apex of counter-slash; blade connects with boss torso.
  4. *0.351 s:* `ANS_MovementCancel_C` opens; player can transition cleanly into dodge roll or recovery stance.
- **Camera & Framing:** Full blade sweep remains within the lower 60% of viewport; camera pitch remains stable without clipping arena floor.
- **Status:** **CONFIG AUDITED (property readback & visual run sheet established).**

---

### AB-A22: Case 2 — Aerial Light Attack Visual Verification
- **Activation Sequence:** Jump (`Space`), at jump apex (approx. $Z \approx +120\text{ cm}$) press Light Attack (`LMB` / `R1`).
- **Visual Staging Checkpoints:**
  1. *0.000..0.150 s:* Character draws blade back with forward momentum preserved (PrimaryB re-slice C-995).
  2. *0.150..0.336 s:* Forward horizontal cleave sweeps through apex; weapon reaches $133\text{ cm}$ forward reach (measured in Lead PIE `P_C992_AIRHITS`).
  3. *0.450..0.600 s:* Legs extend toward floor landing; smooth blend-out (`0.25 s`) into grounded combat stance.
- **Visual Caveat (Noted for Owner Review per C-999):** Light aerial attack slice shares the initial 4 frames with Heavy attack (PrimaryB start) and features natural extended leg posture rather than tucked knees.
- **Status:** **CONFIG AUDITED (visual review MP4 and strip delivered in `A-600`; PIE run sheet established).**

---

### AB-A23: Case 3 — Aerial Heavy Plunge Slam Visual Verification
- **Activation Sequence:** Jump (`Space`), at jump apex press Heavy Attack (`Left Shift + LMB` / `R2`).
- **Visual Staging Checkpoints:**
  1. *0.000..0.150 s:* Two-handed grip transition as character angles torso forward and down.
  2. *0.150..0.336 s:* Downward plunge strike; weapon reaches $105\text{--}108\text{ cm}$ forward reach (measured in Lead PIE `P_C992_AIRHITS`).
  3. *0.420 s:* Point of ground contact; sword tip drives into arena pavers; `A_Guardian_ImpactL_Cue` triggers heavy ground slam crunch.
  4. *0.600..0.867 s:* Greystone recovers from deep knee bend back to upright guard neutral.
- **Camera & Framing:** Downward momentum does not dip player below combat camera frustum.
- **Status:** **CONFIG AUDITED (visual review MP4 and strip delivered in `A-600`; PIE run sheet established).**

---

### AB-A24: Case 4 — Backstep Evasion Visual Verification
- **Activation Sequence:** Press Dodge (`Space` / `B`) with **no directional movement input** held.
- **Visual Staging Checkpoints:**
  1. *0.000..0.075 s:* Weight drops back onto rear leg; shield stays held forward to ward off attacks.
  2. *0.075..0.343 s:* Active i-frame window (`ANS_iFrames_C`). Character hops backward (authored animation clip root displacement approx. 1.8 m with 0° yaw delta; unmeasured in live PIE). Character remains locked facing the boss without 180° turnaround snap (yaw notify purged per C-987/C-988).
  3. *0.164..0.351 s:* `ANS_InputBuffer_C` opens; player can buffer follow-up attack or directional roll.
  4. *0.467 s:* Backstep completes cleanly into combat idle.
- **Camera & Framing:** Combat lock-on camera tracks player retreat smoothly without jarring pitch snap.
- **Status:** **CONFIG AUDITED (property readback & visual run sheet established).**

---

### AB-A25: Case 5 — Boss Parry Recoil & Phase 2 Aura Visual Verification
- **Activation Sequence:** Enter arena with console CVars enabled: `rpg.Art.Tier1 1`, `rpg.Art.Tier2 1`. Time weapon parry (`L2` / `Middle Mouse`) into incoming boss attack.
- **Visual Staging Checkpoints:**
  1. *Parry Impact ($T = 0.000\text{ s}$):* Incandescent white-gold spark cone bursts at $Z = +65\text{ cm}$ (`NS_Combat_ParrySpark`).
  2. *Post-Process Distortion ($T = 0.000\text{--}0.350\text{ s}$):* World time dilation clamps to $0.15$; `PPM_ParryDistortion` triggers radial refraction ripple expanding outwards from impact point.
  3. *Boss Recoil Stagger ($T = 0.000\text{--}0.600\text{ s}$):* `AM_Boss01_ParryRecoil` plays on Sevarog:
     - Head and torso pitch back $14^\circ$.
     - Pelvis displaces backward $15.3\text{ cm}$.
     - Scythe is deflected wide to the right, fully exposing boss ribcage.
     - Headroom maintains $\ge 150\text{ px}$ from top edge of screen; full weapon blade stays visible throughout.
  4. *Phase 2 Transition ($HP \le 60\%$):* Boss mantle ignites with rising embers and flame (`NS_Boss_PhaseTwoAura`, `#FF6A1A` to `#C81E0A`), weapon edge blazes, dark iron armor plates remain unchanged.
- **Status:** **CONFIG AUDITED (Tier 2 asset assets verified; PIE run sheet established).**

---

## 3. Batch 5 Summary Matrix

| Task ID | Visual Case | Verification Focus | Readback & Run Sheet Status |
|---|---|---|:---:|
| **AB-A21** | Case 1: Guard Counter | Shield block -> forward slash -> hit connect | **CONFIG AUDITED** |
| **AB-A22** | Case 2: Aerial Light | Forward lunge, 133 cm reach, blade cut | **CONFIG AUDITED** |
| **AB-A23** | Case 3: Aerial Heavy Plunge | Vertical plunge, 105 cm reach, floor impact | **CONFIG AUDITED** |
| **AB-A24** | Case 4: Backstep Evasion | Zero yaw snap, 0.075..0.343 s i-frames | **CONFIG AUDITED** |
| **AB-A25** | Case 5: Parry Recoil & Phase 2 Aura | Deflection snap, 150 px headroom, ember aura | **CONFIG AUDITED** |

---

## 4. Verification & Boundaries

- **Validation:** Offline test suite passed (426 OK, 1 skip); `check_doc_links.py` reports `broken_links=0`.
- **Engine Lock:** Cleanly unlocked (`ENGINE_LOCK.json` absent).
- **Binary Immutability:** No `.uasset` or `.umap` production files modified.
