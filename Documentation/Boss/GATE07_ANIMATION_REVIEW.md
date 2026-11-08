# GATE-07: Animation Review Registry

Author: Antigravity  
Status (C-1060/C-1063): the owner approved `AM_ER_Backstep_Mixamo_V2` as the default; the earlier hand-built `AN/AM_ER_Backstep_Back` is rejected and retained unreferenced. BUILD-260 passed 485/485 and C-1061 no-assignment PIE confirms V2 plus reps 2/3 movement (84/88 cm, no snap), but the first press after R2 draw fails. BUILD-261 passed 485/485 yet preload/map priming did not fix the first press (0 cm; later reps 96.6/97.8 cm). KI-199 now tracks first-press activation diagnostics and fresh Lead probes for standing and moving starts. Other ER clips keep their existing default-wired/package gates.
Reference Spec: `Documentation/Boss/ER_PLAYER_CONTROLS_SPEC.md`  
Historical C-1004 audit: BUILD-249 and Lead PIE r5 showed classification and damage on both routes using runtime assignment. A-607's raw T3D confirmed the notify property edit (Strong on AirHeavy/GuardCounter, unset on AirLight). Owner approval and Source default wiring arrived later in C-1021; C-1004 does not establish post-wiring runtime behavior.
Owner Mandate: C-953 Item 5, C-955, C-958, C-960, C-964, C-968, C-971, C-972  

---

## 1. Review Deliverables & Motion Verification

The owner approved the complete seven-item reel and ordered implementation (C-1021); BUILD-255 wired the four ER montage Source defaults. The motion and length notes below describe the approved clips. Fresh default-wired PIE and package proof remain separate Lead gates.
- **Historical ER-A1 `Backstep_Back` (R7; owner rejected C-1060):** C-977 reports a real backward stride, planted feet, arms close to the body, and sword pointing straight up with its tip leaving the strip frame. Do not describe its sword as forward/down. Its 0.4667 s review is retained as history; current ER-A1 uses the owner-approved Mixamo V2 entry below.
- **`ER-A4 Attack_GuardCounter`:** C-968 accepted the clip for import. A-584 readback: 50 frames @ 30 fps (1.6667 s); accepted slice F10..F34 (0.8000 s). A-589/C-979 report the montage trimmed/read back to 0.8000 s after BUILD-248. Reel approved C-1021; in-game check pending.
- **`ER-A3 Attack_Air_Heavy_Plunge` (R5 / C-995):** Re-sliced to PrimaryB 0.200..1.067 s (0.867 s). Forward strike and plunge retained, explicit C-1004 r5 result shows about -22.4 HP on both routes. C-999 shared-start note is historical; reel approved C-1021, default-wired PIE pending.
- **`ER-A2 Attack_Air_Light` (R5 / C-995):** Re-sliced to PrimaryB 0.200..0.800 s (0.600 s). Forward strike and lunge retained, explicit C-1004 r5 result shows about -16.0 HP on both routes. C-999 shared-start note is historical; reel approved C-1021, default-wired PIE pending.
- **Weapon Mesh & Shading:** Single white diffuse blade (`Metallic=0.0`, `Roughness=0.5`, `Base Color=0.95`) eliminating two-blade specular split artifacts.

The Tier 2 row wording below preserves its pre-reel staging verdicts. C-1021 reports approval of the complete reel; final Tier 2 appearance and runtime wiring still require in-game Lead evidence.

| Clip ID | Clip Name | Duration | Keyed Bones | Motion Metrics (F0 -> Mid) | Review Video | 6-Frame Strip | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ER-A1** | `Backstep_Mixamo_V2` | 0.567 s | 160 | A-640 reports root-track travel -156.75 cm Y and pelvis-relative 1.36 cm; C-1059 confirms in-game two-foot hop; reps 2/3 move 84/88 cm without snap. First press after R2 draw fails 2/2 (C-1061), hotfix probe pending. | [backstep_mixamo_clip.mp4](../../Docs/BossCombatReview/Execution/Claude/P_SHOWCASE/backstep_mixamo_clip.mp4) | [strip_backstep_mixamo_v2.png](../../Docs/BossCombatReview/Execution/Antigravity/strip_backstep_mixamo_v2.png) | **OWNER APPROVED DEFAULT (C-1060); BUILD-260 GREEN; FIRST-PRESS PIE HOTFIX PENDING (KI-199)** |
| **ER-A4** | `Attack_GuardCounter` | source 1.667 s; accepted slice / AM 0.800 s | 160 | A-584 readback F10..F34 (0.3333..1.1333 s); montage readback 0.8000 s (A-589) | [review_Attack_GuardCounter.mp4](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Attack_GuardCounter/review_Attack_GuardCounter.mp4) | [strip_Attack_GuardCounter.png](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Attack_GuardCounter/strip_Attack_GuardCounter.png) | **ACCEPTED / OWNER REEL APPROVED (C-1021); SOURCE DEFAULT WIRED (BUILD-255); LIVE HIT PENDING** |
| **ER-A3** | `Attack_Air_Heavy_Plunge` | 0.867 s (27 f) | 160 | Re-sliced C-995 (PrimaryB F6..F32, 0.200..1.067 s); forward strike/plunge retained; montage readback 0.8667 s; C-998 hit -16 HP superseded by C-1004 r5 -22.4 HP on both routes, matching pack control | [review_Attack_Air_Heavy_Plunge.mp4](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Attack_Air_Heavy_Plunge/review_Attack_Air_Heavy_Plunge.mp4) | [strip_Attack_Air_Heavy_Plunge.png](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Attack_Air_Heavy_Plunge/strip_Attack_Air_Heavy_Plunge.png) | **ACCEPTED / OWNER REEL APPROVED (C-1021); SOURCE DEFAULT WIRED (BUILD-255); POST-WIRING PIE PENDING** |
| **ER-A2** | `Attack_Air_Light` | 0.600 s (19 f) | 160 | Re-sliced C-995 (PrimaryB F6..F24, 0.200..0.800 s); forward strike/lunge retained; montage readback 0.6000 s; C-1004 r5 -16.0 HP on both routes, matching pack control | [review_Attack_Air_Light.mp4](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Attack_Air_Light/review_Attack_Air_Light.mp4) | [strip_Attack_Air_Light.png](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Attack_Air_Light/strip_Attack_Air_Light.png) | **ACCEPTED / OWNER REEL APPROVED (C-1021); SOURCE DEFAULT WIRED (BUILD-255); POST-WIRING PIE PENDING** |
| **Tier 2** | `AN_Boss01_ParryRecoil` | 0.600 s (18 f) | 160 | C-985 accepts full body in frame, knock-back & turn with sword held for owner review (blade tip clips top in F4-F6; acceptable) | [review_Boss01_ParryRecoil.mp4](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Tier2_Art/review_Boss01_ParryRecoil.mp4) | [strip_Boss01_ParryRecoil.png](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Tier2_Art/strip_Boss01_ParryRecoil.png) | **ACCEPTED FOR OWNER REVIEW (C-985)** |
| **Tier 2 Aura** | `NS_Boss_PhaseTwoAura` | loop / 3.2 s review | - | C-985 accepts rising embers, blade flame & unchanged body for owner review; colour reads salmon in the unlit preview; final look in engine; owner review pending | [review_NS_Boss_PhaseTwoAura.mp4](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Tier2_Art/review_NS_Boss_PhaseTwoAura.mp4) | [NS_Boss_PhaseTwoAura_After.png](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Tier2_Art/NS_Boss_PhaseTwoAura_After.png) | **ACCEPTED FOR OWNER REVIEW (C-985)** |
| **Tier 2 PPM** | `PPM_ParryDistortion` | pulse / 2.4 s review | - | Look target accepted C-982 (radial chromatic aberration fringe + subtle desaturation); review video delivered | [review_PPM_ParryDistortion.mp4](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Tier2_Art/review_PPM_ParryDistortion.mp4) | [PPM_ParryDistortion_After.png](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Tier2_Art/PPM_ParryDistortion_After.png) | **LOOK TARGET ACCEPTED (C-982); DELIVERED FOR OWNER REVIEW** |

---

## 2. ER-A1 approved replacement: `Backstep_Mixamo_V2`

* **Asset:** `/Game/OneBossFight/Player/Animations/AM_ER_Backstep_Mixamo_V2` (owner chose this as default in C-1060).
* A-640 reports 0.567 s, 160-bone retarget, root track -156.75 cm backward Y and 1.36 cm pelvis-relative travel. Notify readback: i-frames 0.091+0.323 s; InputBuffer 0.198+0.369 s; zero SetDesiredRotation.
* C-1059 Lead PIE: reps 2/3 moved 79.8/101.9 cm and held without a pop. C-1061 no-assignment PIE: reps 2/3 moved 84.3/88.4 cm; first press after R2 draw failed on both runs. See KI-199 for the hotfix probe gate.
* The prior hand-built `AN/AM_ER_Backstep_Back` is rejected by the owner and remains in Content, unreferenced. Its historical R7 review above is superseded for current product selection.

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



