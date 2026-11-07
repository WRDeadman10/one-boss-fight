# AA-A09: Elden Ring Combat Animations — Look Renders Review Set

Author: Antigravity  
Status: READY FOR OWNER & LEAD REVIEW (R2 HOTFIXED)  
Mandate: C-953 Item 5, C-955, C-958, C-960  
Target Rig: `SK_CombatMannequin` (~1.80 m height)  

---

## 1. Executive Summary

This review set compiles the rendered look grabs, full-motion review videos, and 6-frame strip inspection tiles for the 4 core Elden Ring player moves authored in Blender under R2 Hotfix standards (pack motion blending, unaltered bone axes). All renders feature:
- **Pack Source Blending:** Built from Advanced ARPG Combat source sequences (`Dodge_Small_Forward_Roll`, `BlockLoop`, `Attack_PrimaryA_Anim`, `PrimaryAttack_A_Slow_Anim`, `MM_Jump`, `MM_Fall_Loop`), preserving all native bone coordinate axes and natural body dynamics.
- **1080p Framing & Mesh:** `SKM_CombatMannequin_Simple_LOD0` mesh and `SM_KwangSword` visible and lit; dynamic tracking camera maintaining ~80% character screen height.
- **Studio Environment:** Neutral studio grey background (`#47474d`) with 3-point sun lighting (Key, Fill, Rim).
- **Multi-Pass Review Video:** Side View (1.0x) -> Front View (1.0x) -> Side View (0.5x Slow-Motion) encoded in H.264 MP4.
- **6-Frame Strips:** Tiled 6x1 PNG strips (1920x180) providing instant pose-strip progression for technical review.
- **Verified Scale:** Exactly 1.786 m armature standing height matching Unreal Engine's `SK_CombatMannequin` unit scale.

---

## 2. Visual Review Cards

### 1. ER-A1: `Backstep_Back`
- **Role:** Fast, low evasive hop backwards with immediate recovery into counter-attacks.
- **Motion Characteristics:** Zero yaw rotation (strictly faces opponent); crouched spring push-off; smooth deceleration into combat idle.
- **Timing:** 0.467 s (15 frames @ 30 fps). I-frames: 0.067–0.267 s.
- **Root Translation:** 200 cm straight backwards (-Y).
- **6-Frame Strip (6x1 Tile):** [strip_Backstep_Back.png](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Backstep_Back/strip_Backstep_Back.png)
- **Look Frame-Grab (Apex):** [look_Backstep_Back.png](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Backstep_Back/look_Backstep_Back.png)
- **Review Video:** [review_Backstep_Back.mp4](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Backstep_Back/review_Backstep_Back.mp4)

---

### 2. ER-A4: `Attack_GuardCounter`
- **Role:** Heavy counter-strike triggered immediately after absorbing an attack on shield guard.
- **Motion Characteristics:** Uncoils from tight guard; forceful 100 cm forward step; explosive horizontal greatsword slash across torso line; heavy follow-through.
- **Timing:** 0.800 s (25 frames @ 30 fps). Hit window: 0.333–0.533 s. Impact peak: 0.433 s.
- **Root Translation:** 100 cm forward (+Y).
- **6-Frame Strip (6x1 Tile):** [strip_Attack_GuardCounter.png](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Attack_GuardCounter/strip_Attack_GuardCounter.png)
- **Look Frame-Grab (Impact):** [look_Attack_GuardCounter.png](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Attack_GuardCounter/look_Attack_GuardCounter.png)
- **Review Video:** [review_Attack_GuardCounter.mp4](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Attack_GuardCounter/review_Attack_GuardCounter.mp4)

---

### 3. ER-A3: `Attack_Air_Heavy_Plunge`
- **Role:** Devastating jumping heavy downward plunge that crushes poise and slams into the ground.
- **Motion Characteristics:** Two-handed sword lift at jump apex; vertical downward plunge accelerating toward the ground; deep knee crouch ground impact slam.
- **Timing:** 0.867 s (27 frames @ 30 fps). Ground impact: 0.500 s.
- **Root Translation:** In-place (driven by jump trajectory and Unreal gravity).
- **6-Frame Strip (6x1 Tile):** [strip_Attack_Air_Heavy_Plunge.png](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Attack_Air_Heavy_Plunge/strip_Attack_Air_Heavy_Plunge.png)
- **Look Frame-Grab (Slam):** [look_Attack_Air_Heavy_Plunge.png](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Attack_Air_Heavy_Plunge/look_Attack_Air_Heavy_Plunge.png)
- **Review Video:** [review_Attack_Air_Heavy_Plunge.mp4](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Attack_Air_Heavy_Plunge/review_Attack_Air_Heavy_Plunge.mp4)

---

### 4. ER-A2: `Attack_Air_Light`
- **Role:** Fast, agile aerial slash during jump ascent or descent.
- **Motion Characteristics:** Upper body torso coil to the right; rapid diagonal downward one-handed swipe; seamless recovery into falling loop or landing cushion.
- **Timing:** 0.567 s (18 frames @ 30 fps). Hit window: 0.200–0.333 s. Impact peak: 0.233 s.
- **Root Translation:** In-place (driven by jump trajectory).
- **6-Frame Strip (6x1 Tile):** [strip_Attack_Air_Light.png](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Attack_Air_Light/strip_Attack_Air_Light.png)
- **Look Frame-Grab (Arc Apex):** [look_Attack_Air_Light.png](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Attack_Air_Light/look_Attack_Air_Light.png)
- **Review Video:** [review_Attack_Air_Light.mp4](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Attack_Air_Light/review_Attack_Air_Light.mp4)

---

## 3. Review Verdict Checklist for Owner / Lead

- [ ] Armature proportions read cleanly against `SK_CombatMannequin`.
- [ ] Root motion direction matches intended game axes (-Y for backstep, +Y for counter).
- [ ] Motion anticipation, hit apex, and recovery weight feel responsive for a soulslike duel.
- [ ] Lighting and grey background provide high visual clarity across all 4 videos.
