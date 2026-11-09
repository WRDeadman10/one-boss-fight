# SFX Batch 3: Boss Attack Whooshes & Heavy Foley Candidate Specification

**Document Version:** 1.0  
**Authority:** Claude Lead Directive `[C-1197]`, `[C-1203]` (2026-11-09).  
**Owner:** Antigravity (`Art/Review/Audit`).  
**Status:** PROPOSED (Awaiting Owner Audition Selection; No Apply).  
**Scope:** Tasks SFX-11 through SFX-15 in [`Documentation/Boss/QUEUE_SFX.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_SFX.md).

---

## 1. Candidate Selection Matrix

| Task ID | Gameplay Event | Anim Montage / Hook Site | Candidate Options (In Repo) | Asset Path | Duration / Character |
|---|---|---|---|---|---|
| **SFX-11** | **Boss A1 Horizontal Slash** | `AM_Boss01_A1`<br>(Horizontal blade arc) | **Option A (Preferred):** Medium Blade Cleave<br>**Option B:** Swift Velocity Swoosh<br>**Option C:** Pack Standard Swing | `/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_1_Cue`<br>`/Game/RealisticSwordSoundEffects/Cues/Sword_Swoosh/Swoosh_1_Cue`<br>`/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Sword_Swing_Cue` | ~0.42s, crisp cutting arc<br>~0.25s, sharp high-velocity<br>~0.38s, balanced standard |
| **SFX-12** | **Boss A2 Overhead Cleave** | `AM_Boss01_A2`<br>(Downward 2-handed slam) | **Option A (Preferred):** Heavy Vertical Cleave<br>**Option B:** Weighted Downward Drag<br>**Option C:** Deep Wind Drag | `/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_3_Cue`<br>`/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Axe_Swing_Cue`<br>`/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_5_Cue` | ~0.55s, powerful vertical cut<br>~0.48s, heavy downward mass<br>~0.50s, deep bass whoosh |
| **SFX-13** | **Boss A3 Ground Stomp** | `AM_Boss01_A3`<br>(Footfall & shockwave ring) | **Option A (Preferred):** Shockwave Concussion<br>**Option B:** Detonation Rumble<br>**Option C:** Stone Guardian Thud | `/Game/Vefects/Easy_Shockwaves_VFX/Audio/Cues/SFX_Vefects_Shockwave_01_1s_Cue`<br>`/Game/StarterContent/Audio/Explosion_Cue`<br>`/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Guardian_ImpactL_Cue` | ~0.90s, sharp sub-bass crack<br>~1.10s, low rolling thunder<br>~0.85s, dense stone impact |
| **SFX-14** | **Boss Mid01 Forward Thrust** | `AM_Boss01_Mid01`<br>(Piercing forward lunge) | **Option A (Preferred):** Piercing Air Wake<br>**Option B:** Directional Air Cut<br>**Option C:** Linear Slicing Thrust | `/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_Short_1_Cue`<br>`/Game/RealisticSwordSoundEffects/Cues/Sword_Swoosh/Swoosh_4_Cue`<br>`/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_7_Cue` | ~0.28s, focused forward pierce<br>~0.30s, sharp displacement<br>~0.35s, linear edge slice |
| **SFX-15** | **Boss Sprint Gap-Closer** | `AM_Boss01_Sprint`<br>(Running momentum horizontal strike) | **Option A (Preferred):** Sweeping Momentum Whoosh<br>**Option B:** Heavy Velocity Displacement<br>**Option C:** High-Speed Wide Edge | `/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_2_Cue`<br>`/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Hammer_Swing_Cue`<br>`/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_8_Cue` | ~0.58s, heavy momentum carry<br>~0.52s, wide air drag<br>~0.46s, fast arc whoosh |

---

## 2. Design Rationale & Timing Alignment

1. **Weight Differentiation:**
   - Player Greystone swings use light, rapid whooshes (`~0.20-0.30s`). Boss Sevarog/Ember attacks must communicate enormous mass and momentum (`~0.45-0.60s`), giving the player clear auditory cues for dodge/parry window anticipation.
2. **Hit-Stop & Anticipation Sync:**
   - In `AM_Boss01_A1` and `AM_Boss01_A2`, the whoosh sound cue triggers slightly before the active trace damage frames to serve as a vital telegraph for player reflex parrying.
3. **No-Pack Asset Mutation:**
   - In line with project rules, all sounds will be integrated via optional montage anim notifies or C++ component delegates without modifying any core pack data.
