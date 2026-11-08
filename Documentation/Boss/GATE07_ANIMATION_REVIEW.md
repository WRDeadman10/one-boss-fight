# GATE-07: Animation Review Registry

Author: Antigravity  
Status (C-1021 / BUILD-255): the owner approved the reel and ordered implementation. `URPGDodgeTiming` Source defaults now point to all four `AM_ER` montages; `PackWiring` loads them and BUILD-255 passed 484/484. A-607's saved notify proof and C-1004's runtime-assigned two-route air hits remain valid for their tested scope (AirLight -16.0 HP, AirHeavy -22.4 HP). Fresh PIE and package proof for the default-wired route remain open.
Reference Spec: `Documentation/Boss/ER_PLAYER_CONTROLS_SPEC.md`  
Historical C-1004 audit: BUILD-249 and Lead PIE r5 showed classification and damage on both routes using runtime assignment. A-607's raw T3D confirmed the notify property edit (Strong on AirHeavy/GuardCounter, unset on AirLight). Owner approval and Source default wiring arrived later in C-1021; C-1004 does not establish post-wiring runtime behavior.
Owner Mandate: C-953 Item 5, C-955, C-958, C-960, C-964, C-968, C-971, C-972  

---

## 1. Review Deliverables & Motion Verification

The owner approved the complete seven-item reel and ordered implementation (C-1021); BUILD-255 wired the four ER montage Source defaults. The motion and length notes below describe the approved clips. Fresh default-wired PIE and package proof remain separate Lead gates.
- **`ER-A1 Backstep_Back` (R7):** C-977 reports a real backward stride, planted feet, arms close to the body, and sword pointing straight up with its tip leaving the strip frame. Do not describe its sword as forward/down. A-589/C-979 report the montage trimmed/read back to 0.4667 s (15 frames). Reel approved C-1021; in-game check pending.
- **`ER-A4 Attack_GuardCounter`:** C-968 accepted the clip for import. A-584 readback: 50 frames @ 30 fps (1.6667 s); accepted slice F10..F34 (0.8000 s). A-589/C-979 report the montage trimmed/read back to 0.8000 s after BUILD-248. Reel approved C-1021; in-game check pending.
- **`ER-A3 Attack_Air_Heavy_Plunge` (R5 / C-995):** Re-sliced to PrimaryB 0.200..1.067 s (0.867 s). Forward strike and plunge retained, explicit C-1004 r5 result shows about -22.4 HP on both routes. C-999 shared-start note is historical; reel approved C-1021, default-wired PIE pending.
- **`ER-A2 Attack_Air_Light` (R5 / C-995):** Re-sliced to PrimaryB 0.200..0.800 s (0.600 s). Forward strike and lunge retained, explicit C-1004 r5 result shows about -16.0 HP on both routes. C-999 shared-start note is historical; reel approved C-1021, default-wired PIE pending.
- **Weapon Mesh & Shading:** Single white diffuse blade (`Metallic=0.0`, `Roughness=0.5`, `Base Color=0.95`) eliminating two-blade specular split artifacts.

The Tier 2 row wording below preserves its pre-reel staging verdicts. C-1021 reports approval of the complete reel; final Tier 2 appearance and runtime wiring still require in-game Lead evidence.

| Clip ID | Clip Name | Duration | Keyed Bones | Motion Metrics (F0 -> Mid) | Review Video | 6-Frame Strip | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ER-A1** | `Backstep_Back` | 0.467 s (15 f) | 160 | A-587 reports -200 cm root; C-977 strip: backward stride, feet planted, arms close, sword points up/out of frame; AM readback 0.4667 s (A-589) | [review_Backstep_Back.mp4](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Backstep_Back/review_Backstep_Back.mp4) | [strip_Backstep_Back.png](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Backstep_Back/strip_Backstep_Back.png) | **ACCEPTED / OWNER REEL APPROVED (C-1021); SOURCE DEFAULT WIRED (BUILD-255); PIE PENDING** |
| **ER-A4** | `Attack_GuardCounter` | source 1.667 s; accepted slice / AM 0.800 s | 160 | A-584 readback F10..F34 (0.3333..1.1333 s); montage readback 0.8000 s (A-589) | [review_Attack_GuardCounter.mp4](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Attack_GuardCounter/review_Attack_GuardCounter.mp4) | [strip_Attack_GuardCounter.png](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Attack_GuardCounter/strip_Attack_GuardCounter.png) | **ACCEPTED / OWNER REEL APPROVED (C-1021); SOURCE DEFAULT WIRED (BUILD-255); LIVE HIT PENDING** |
| **ER-A3** | `Attack_Air_Heavy_Plunge` | 0.867 s (27 f) | 160 | Re-sliced C-995 (PrimaryB F6..F32, 0.200..1.067 s); forward strike/plunge retained; montage readback 0.8667 s; C-998 hit -16 HP superseded by C-1004 r5 -22.4 HP on both routes, matching pack control | [review_Attack_Air_Heavy_Plunge.mp4](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Attack_Air_Heavy_Plunge/review_Attack_Air_Heavy_Plunge.mp4) | [strip_Attack_Air_Heavy_Plunge.png](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Attack_Air_Heavy_Plunge/strip_Attack_Air_Heavy_Plunge.png) | **ACCEPTED / OWNER REEL APPROVED (C-1021); SOURCE DEFAULT WIRED (BUILD-255); POST-WIRING PIE PENDING** |
| **ER-A2** | `Attack_Air_Light` | 0.600 s (19 f) | 160 | Re-sliced C-995 (PrimaryB F6..F24, 0.200..0.800 s); forward strike/lunge retained; montage readback 0.6000 s; C-1004 r5 -16.0 HP on both routes, matching pack control | [review_Attack_Air_Light.mp4](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Attack_Air_Light/review_Attack_Air_Light.mp4) | [strip_Attack_Air_Light.png](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Attack_Air_Light/strip_Attack_Air_Light.png) | **ACCEPTED / OWNER REEL APPROVED (C-1021); SOURCE DEFAULT WIRED (BUILD-255); POST-WIRING PIE PENDING** |
| **Tier 2** | `AN_Boss01_ParryRecoil` | 0.600 s (18 f) | 160 | C-985 accepts full body in frame, knock-back & turn with sword held for owner review (blade tip clips top in F4-F6; acceptable) | [review_Boss01_ParryRecoil.mp4](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Tier2_Art/review_Boss01_ParryRecoil.mp4) | [strip_Boss01_ParryRecoil.png](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Tier2_Art/strip_Boss01_ParryRecoil.png) | **ACCEPTED FOR OWNER REVIEW (C-985)** |
| **Tier 2 Aura** | `NS_Boss_PhaseTwoAura` | loop / 3.2 s review | - | C-985 accepts rising embers, blade flame & unchanged body for owner review; colour reads salmon in the unlit preview; final look in engine; owner review pending | [review_NS_Boss_PhaseTwoAura.mp4](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Tier2_Art/review_NS_Boss_PhaseTwoAura.mp4) | [NS_Boss_PhaseTwoAura_After.png](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Tier2_Art/NS_Boss_PhaseTwoAura_After.png) | **ACCEPTED FOR OWNER REVIEW (C-985)** |
| **Tier 2 PPM** | `PPM_ParryDistortion` | pulse / 2.4 s review | - | Look target accepted C-982 (radial chromatic aberration fringe + subtle desaturation); review video delivered | [review_PPM_ParryDistortion.mp4](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Tier2_Art/review_PPM_ParryDistortion.mp4) | [PPM_ParryDistortion_After.png](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Tier2_Art/PPM_ParryDistortion_After.png) | **LOOK TARGET ACCEPTED (C-982); DELIVERED FOR OWNER REVIEW** |

---

## 2. ER-A1 `Backstep_Back` Evidence (R7)

* **Deliverable Directory:** `Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Backstep_Back/`
* A-587 reports 160 keyed bones, 15 frames at 30 fps (0.467 s), -200 cm root, and R6 legs/root retained with an R7 upper-body pose.
* C-977's strip observation: backward stride, feet plant, arms are in at the body, sword points straight up and its tip leaves the frame. This contradicts A-587's “forward/down” sword description; that claim is not repeated here.
* Review strip and video remain owner-review evidence; no owner acceptance is recorded in the mailbox through C-977.

---

## 3. ER-A4 `Attack_GuardCounter` Review Details

* **Deliverable Directory:** `Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Attack_GuardCounter/`
* **FBX Asset:** `Attack_GuardCounter.fbx` (712.7 KB, SK_CombatMannequin, FBX_SCALE_NONE, no leaf bones).
* **Look Render:** `look_Attack_GuardCounter.png` (Frame 13 peak impact).
* **Review Video:** `review_Attack_GuardCounter.mp4` (1080p, Side Profile 1.0x -> Front View 1.0x -> Side Profile 0.5x slow-motion).
* **Notify & Timing Data:**
  - `WindupEnd`: Frame 9 (0.300 s)
  - `HitWindowStart`: Frame 10 (0.333 s)
  - `Impact`: Frame 13 (0.433 s)
  - `HitWindowEnd`: Frame 16 (0.533 s)
  - `RecoverEnd`: Frame 24 (0.800 s)
  - Root Travel: 100.0 cm forward step along +Y (facing strictly preserved at Yaw 0.0°).
* **What to Look For:**
  1. Starts cleanly from shield-guard blocking pose.
  2. Explosive torso torque and lunge step forward.
  3. Forceful horizontal slash with full extension through impact window.
  4. Controlled deceleration and smooth follow-through returning to combat idle.

---

## 4. ER-A3 `Attack_Air_Heavy_Plunge` Review Details

* **Deliverable Directory:** `Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Attack_Air_Heavy_Plunge/`
* **FBX Asset:** `Attack_Air_Heavy_Plunge.fbx` (729.5 KB, SK_CombatMannequin, FBX_SCALE_NONE, no leaf bones).
* **Look Render:** `look_Attack_Air_Heavy_Plunge.png` (Frame 15 landing ground slam).
* **Review Video:** `review_Attack_Air_Heavy_Plunge.mp4` (1080p, Side Profile 1.0x -> Front View 1.0x -> Side Profile 0.5x slow-motion).
* **Notify & Timing Data:**
  - `AirborneWindupEnd`: Frame 6 (0.200 s)
  - `HitWindowStart`: Frame 11 (0.367 s)
  - `LandingImpact`: Frame 15 (0.500 s)
  - `HitWindowEnd`: Frame 16 (0.533 s)
  - `RecoverEnd`: Frame 26 (0.867 s)
  - Root Travel: None (In-place; jump physics drives character movement).
* **What to Look For:**
  1. High two-handed overhead sword lift during jump apex.
  2. Heavy, accelerating vertical downward plunge through chest plane.
  3. Powerful ground impact slam at F15 with knees compressing into a deep squat.
  4. Shockwave follow-through and stable recovery to combat idle.

---

## 5. ER-A2 `Attack_Air_Light` Review Details

* **Deliverable Directory:** `Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Attack_Air_Light/`
* **FBX Asset:** `Attack_Air_Light.fbx` (655.8 KB, SK_CombatMannequin, FBX_SCALE_NONE, no leaf bones).
* **Look Render:** `look_Attack_Air_Light.png` (Frame 7 diagonal air slash apex).
* **Review Video:** `review_Attack_Air_Light.mp4` (1080p, Side Profile 1.0x -> Front View 1.0x -> Side Profile 0.5x slow-motion).
* **Notify & Timing Data:**
  - `AirborneWindupEnd`: Frame 4 (0.133 s)
  - `HitWindowStart`: Frame 6 (0.200 s)
  - `Impact`: Frame 7 (0.233 s)
  - `HitWindowEnd`: Frame 10 (0.333 s)
  - `RecoverEnd`: Frame 17 (0.567 s)
  - Root Travel: None (In-place; jump physics drives character movement).
* **What to Look For:**
  1. Upper torso coils right in jump apex.
  2. Crisp one-handed diagonal downward slash across body plane.
  3. Distinct from the ground light attack (horizontal swipe).
  4. Follow-through flows naturally into airborne fall loop or landing.



