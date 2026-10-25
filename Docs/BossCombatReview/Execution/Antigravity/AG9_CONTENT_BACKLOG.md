# AG-9: Content Production Backlog for P1–P8 Boss Combat Program

**Document ID:** `AG9_CONTENT_BACKLOG` (Rev 01)  
**Date:** 2026-10-25  
**Author:** Antigravity (Accountable Visual & Technical Animation Investigator)  
**Addressed to:** Claude (Technical Lead & Editor Owner), Codex GPT-6 Astra (Technical Reviewer & Data Architect), Project Owner  
**Authority & Mandate:** Task AG-9 of Work Order 02 (`ANTIGRAVITY_WORK_ORDER_02.md`). Specification only; **NO ASSET AUTHORING OR IMPORT EXECUTED**.  
**Companion Artifact:** `Docs/BossCombatReview/Execution/Antigravity/AG9_CONTENT_BACKLOG.csv` (machine-readable data sheet).

---

## 1. Executive Summary & Inventory Scope

This backlog compiles every single artistic, animation, visual effect, acoustic, and interface asset required across the complete P1–P8 Boss Combat Improvement Program. It consolidates deliverables from:
1. **Required Former-N/A Rows (AG-1):** HIT-012 (Grab), ANM-003 (Hold), ANM-006 (Warp), DEF-005 (Defenses), AWR-008 (Adaptive Tells), SEL-008 (Fallback).
2. **Second-Boss & Build Canary (AG-2):** Cinder Knight Alistair, Halberd weapon moveset, Vanguard build assets.
3. **P1 Telegraph & Readability Improvements (AG-3):** 14-move visual and acoustic telegraph cues.
4. **Production Shockwave Assets (AG-4):** RV-01 / VIS-05 / G01 Shipping-visible Niagara ring and audio.
5. **A2 Master Montage Integration (AG-5):** VIS-02 composite montage assembling the delivered trio.

Every item is classified by purpose: **Required Audit Row Requirement** vs **Second-Boss Canary** vs **P0 Defect Fix**.

---

## 2. Master Content Production Backlog Table

```
+-----+-------------------------------+--------------------------------------------------+---------------+-------------+---------+--------+------------+---------------------------------------+
| ID  | Asset Name                    | Repository Content Path                          | Category      | Scope       | Owner   | Phase  | Effort     | Acceptance Test                       |
+-----+-------------------------------+--------------------------------------------------+---------------+-------------+---------+--------+------------+---------------------------------------+
```

| ID | Asset Name | Engine Content Path (`/Game/OneBossFight/...`) | Asset Category | Purpose Scope | Asset Owner | Phase Dependency | Effort Size & Reason | Acceptance Test |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **B-01** | `AM_Boss01_A2_OverheadSlam` | `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A2_OverheadSlam` | Montage | P0 Defect Fix (VIS-02) | Claude (Editor) | Phase P1 / P2 | **Small**: Combines 3 already delivered clips with seams | `pie_a4_low_sweep.py` / `pie_look.py` |
| **B-02** | `SFX_A2_ReleaseCue` | `/Game/OneBossFight/Boss01/Audio/SFX_A2_ReleaseCue` | Sound Wave | Audit (ANM-003) | Antigravity (WAV) | Phase P1 | **Small**: 150ms metallic snap transient | Audio waveform lead check ($\ge 150\text{ ms}$) |
| **B-03** | `NS_Boss01_Shockwave_Ring` | `/Game/OneBossFight/Boss01/VFX/NS_Boss01_Shockwave_Ring` | Niagara System | P0 Defect Fix (RV-01) | Antigravity / Claude | Phase P1 | **Medium**: Dynamic parameter-driven torus ribbon | `G4-3` Packaged Shipping capture |
| **B-04** | `NE_Shockwave_MeshRibbon` | `/Game/OneBossFight/Boss01/VFX/NE_Shockwave_MeshRibbon` | Niagara Emitter | P0 Defect Fix (RV-01) | Antigravity | Phase P1 | **Medium**: Geometry mesh ribbon emitter | Viewport bounding height test ($\le 38\text{ cm}$) |
| **B-05** | `M_Shockwave_Wavefront` | `/Game/OneBossFight/Boss01/Materials/M_Shockwave_Wavefront` | Material | P0 Defect Fix (RV-01) | Antigravity | Phase P1 | **Small**: Unlit emissive flame shader | Visual contrast audit |
| **B-06** | `SFX_Shockwave_Impact` | `/Game/OneBossFight/Boss01/Audio/SFX_Shockwave_Impact` | Sound Wave | P0 Defect Fix (RV-01) | Antigravity (WAV) | Phase P1 | **Small**: Low-frequency concussive transient | Audio playback sync at $t = 0.754\text{ s}$ |
| **B-07** | `SFX_Shockwave_Travel` | `/Game/OneBossFight/Boss01/Audio/SFX_Shockwave_Travel` | Sound Wave | P0 Defect Fix (RV-01) | Antigravity (WAV) | Phase P1 | **Small**: Spatialized expanding rush loop | Continuous audio tracking radius |
| **B-08** | `SFX_Shockwave_JumpPass`| `/Game/OneBossFight/Boss01/Audio/SFX_Shockwave_JumpPass` | Sound Wave | P0 Defect Fix (RV-01) | Antigravity (WAV) | Phase P1 | **Small**: Whoosh confirming clearance | Driver assertion `bClearedBand == true` |
| **B-09** | `SOCKET_Riposte` | Added to `Content/OneBossFight/Boss01/Body/SK_Boss01_Body` | Mesh Socket | Audit (HIT-010/012) | Claude (Editor) | Phase P1 | **Small**: Placed on `spine_03` at chest $(0, 20, 0)$ | Socket readback probe |
| **B-10** | `T_Riposte_Reticle` | `/Game/OneBossFight/UI/Textures/T_Riposte_Reticle` | Texture2D | Audit (HIT-010/012) | Antigravity (PNG) | Phase P1 | **Small**: High-contrast targeting glyph | UI reticle rendering in Stagger |
| **B-11** | `SFX_PostureBreak_Shatter`| `/Game/OneBossFight/Boss01/Audio/SFX_PostureBreak_Shatter` | Sound Wave | P1 Readability | Antigravity (WAV) | Phase P1 | **Small**: 3 kHz glass-shatter transient | Audio cue audibility test |
| **B-12** | `NS_Boss01_FloorSparks` | `/Game/OneBossFight/Boss01/VFX/NS_Boss01_FloorSparks` | Niagara System | P1 Readability (A3a) | Antigravity | Phase P1 | **Small**: Floor-scraping friction sparks | Ground contact particle test |
| **B-13** | `AN_Boss01_Grab_Attack` | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_Grab_Attack` | Anim Sequence | Audit (HIT-012) | Antigravity (FBX) | Phase P2 / P3 | **Large**: Attacker grab, lift, slam, and whiff | Bone alignment validator |
| **B-14** | `AN_Player_Grab_Victim` | `/Game/OneBossFight/Player/Animations/AN_Player_Grab_Victim` | Anim Sequence | Audit (HIT-012) | Antigravity (FBX) | Phase P2 / P3 | **Large**: Paired struggle, slammed, get-up | Paired transform deviation test |
| **B-15** | `AM_Boss01_Grab_Attack` | `/Game/OneBossFight/Boss01/Animations/AM_Boss01_Grab_Attack` | Montage | Audit (HIT-012) | Claude (Editor) | Phase P2 / P3 | **Medium**: 6-section montage with capture check | Automated grab driver |
| **B-16** | `SOCKET_Grab_Victim` | Added to `SK_Boss01_Body` at `hand_l` | Mesh Socket | Audit (HIT-012) | Claude (Editor) | Phase P2 / P3 | **Small**: Exact palm hold transform | Paired alignment verification |
| **B-17** | `AN_Boss01_LungeTravel` | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_LungeTravel` | Anim Sequence | Audit (ANM-006) | Antigravity (FBX) | Phase P2 / P4 | **Medium-Large**: 450cm root motion forward lunge | Root motion curve linearity check |
| **B-18** | `AM_Boss01_LungeTravel` | `/Game/OneBossFight/Boss01/Animations/AM_Boss01_LungeTravel` | Montage | Audit (ANM-006) | Claude (Editor) | Phase P2 / P4 | **Medium**: Configured with early warp window | Motion warp clamp assertion |
| **B-19** | `AN_Boss01_Guard_Suite` | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_Guard_*` (5 clips) | Anim Sequences | Audit (DEF-005) | Antigravity (FBX) | Phase P3 / P5 | **Large**: Enter, Loop, Recoil, Break, Exit | Posture break duration (2.0s) |
| **B-20** | `AN_Boss01_Parry_Suite` | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_Parry_*` (4 clips) | Anim Sequences | Audit (DEF-005) | Antigravity (FBX) | Phase P3 / P5 | **Medium**: Startup (180ms), Deflect, Riposte, Whiff | Parry window timing test |
| **B-21** | `AN_Boss01_Dodge_Suite` | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_Dodge_*` (3 clips) | Anim Sequences | Audit (DEF-005) | Antigravity (FBX) | Phase P3 / P5 | **Medium**: Backstep (300cm), Lateral hops (220cm) | I-Frame window test (240ms) |
| **B-22** | `AN_Boss01_Adapt_Tell` | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_Adapt_Tell` | Anim Sequence | Audit (AWR-008) | Antigravity (FBX) | Phase P6 | **Small**: Additive upper-body posture shift | Additive layer evaluation test |
| **B-23** | `AN_Boss01_Fallback_Suite`| `/Game/OneBossFight/Boss01/Animations/AN_Boss01_Fallback_*` (2 clips) | Anim Sequences | Audit (SEL-008) | Antigravity (FBX) | Phase P6 | **Small-Medium**: Pacing walk loop and flourish | Bounded task duration (1.5–3.0s) |
| **B-24** | `SKM_Canary_Alistair` | `/Game/OneBossFight/Canary/Meshes/SKM_Canary_Alistair` | Skeletal Mesh | Canary (Second Boss) | Antigravity (FBX) | Phase P8 | **Medium**: Weathered knight on `SK_CombatMannequin` | Skeleton compatibility validator |
| **B-25** | `SM_Canary_Halberd` | `/Game/OneBossFight/Canary/Weapons/SM_Canary_Halberd` | Static Mesh | Canary (Second Boss) | Antigravity (FBX) | Phase P8 | **Small**: Heavy 220cm polearm with sockets | Socket placement readback |
| **B-26** | `AN_Canary_Lifecycle` | `/Game/OneBossFight/Canary/Animations/AN_Canary_*` (6 clips) | Anim Sequences | Canary (Second Boss) | Antigravity (FBX) | Phase P8 | **Medium**: Dormant, Wake, Stagger, Riposte, Roar, Death | Canary lifecycle driver |
| **B-27** | `AN_Canary_M1_Cleave` | `/Game/OneBossFight/Canary/Animations/AN_Canary_M1_DoubleCleave` | Anim Sequence | Canary (Move 1) | Antigravity (FBX) | Phase P8 | **Medium**: Dual-window cleave animation | Dual-window damage test |
| **B-28** | `AN_Canary_M2_Soulfire`| `/Game/OneBossFight/Canary/Animations/AN_Canary_M2_SoulfireArc` | Anim Sequence | Canary (Move 2) | Antigravity (FBX) | Phase P8 | **Small-Medium**: Overhead projectile release chop | Projectile release timing test |
| **B-29** | `NS_Canary_SoulfireArc` | `/Game/OneBossFight/Canary/VFX/NS_Canary_SoulfireArc` | Niagara System | Canary (Move 2) | Antigravity | Phase P8 | **Medium**: Traveling crescent blue frost-flame arc | Projectile hit registration test |
| **B-30** | `AN_Canary_M3_Quake` | `/Game/OneBossFight/Canary/Animations/AN_Canary_M3_RadialQuake` | Anim Sequence | Canary (Move 3) | Antigravity (FBX) | Phase P8 | **Small-Medium**: Pommel floor slam animation | Radial wave expansion test |
| **B-31** | `AN_Canary_M4_Branch` | `/Game/OneBossFight/Canary/Animations/AN_Canary_M4_*` (3 clips) | Anim Sequences | Canary (Move 4) | Antigravity (FBX) | Phase P8 | **Medium**: Thrust intro, vault success, stumble whiff | Branch gate decision test |
| **B-32** | `SM_Player_Halberd` | `/Game/OneBossFight/Weapons/SM_Player_SilversteelHalberd` | Static Mesh | Canary (New Weapon) | Antigravity (FBX) | Phase P8 | **Small**: 190cm player polearm static mesh | Weapon equip & socket audit |
| **B-33** | `T_Icon_Halberd` | `/Game/OneBossFight/UI/Textures/T_Icon_SilversteelHalberd` | Texture2D | Canary (New Weapon) | Antigravity (PNG) | Phase P8 | **Small**: 256x256 RGBA UI icon | Build picker icon display test |
| **B-34** | `AN_Player_Halberd_Suite`| `/Game/OneBossFight/Player/Animations/AN_Player_Halberd_*` (4 clips) | Anim Sequences | Canary (New Weapon) | Antigravity (FBX) | Phase P8 | **Medium-Large**: Light 1-2, Heavy charged, Dodge attack | Attack table execution test |
| **B-35** | `DA_Build_Vanguard` | `/Game/OneBossFight/Builds/DA_Build_Vanguard` | Data Asset | Canary (Fourth Build) | Claude (Editor) | Phase P8 | **Small**: PrimaryDataAsset referencing Halberd | Build loadout & PIE equip test |

---

## 3. Evidence and Limits

| Claim / Field | Source File / Anchor | Kind | Status / Limit |
| :--- | :--- | :--- | :--- |
| Asset Count (35 backlog items) | Merged from AG1, AG2, AG3, AG4, AG5 | Production Planning | Complete scope for 83-row conforming closure |
| Path Layout (`Content/OneBossFight/...`) | Existing project conventions (`PROJECT_STATE.md`) | Repository Standard | Conforms to `DirectoriesToAlwaysCook` |
| Sizing Estimates (Small / Medium / Large) | Aligned with Codex `D05_CONDITIONAL_ROWS_COSTING.md` | Estimation Judgment | Relative complexity; calendar days not promised |

### What Could NOT Be Verified Offline:
1. Exact package sizes and memory footprint of unauthored Niagara systems cannot be determined before authoring.
2. Actual sound attenuation curves in the `L_SevarogArena` level geometry cannot be verified without in-editor audio auditioning.
