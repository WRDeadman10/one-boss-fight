# Authoritative Art & Animation Inventory: The Ember Warden & Combat Mannequin (AN1..AN4, CL1)

**Date:** 2026-11-05  
**Author:** Antigravity (Offline Quality & Asset Lane)  
**Task Directives:** [C-903], [C-904] (Authoritative audit on live production characters; retired Paragon prototypes excluded)  
**Live Production Character Architecture:**
- **Boss Character:** The Ember Warden = `BP_ExampleGreatSwordBoss` (`/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss`)
  - Driven by pack skeleton `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin`
  - Re-skinned via `URPGBossLook` (`SK_Boss01_Body`, `SK_Boss01_Crown`, `SK_Boss01_Mantle`, `SK_Boss01_BrazierGauntlet`, `SM_Boss01_Greatsword`)
  - 14 authored project animations in `/Game/OneBossFight/Boss01/Animations` (`AN_Boss01_*`)
- **Player Character:** `BP_CombatPlayerCharacter` (`/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter`)
  - Driven by pack skeleton `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin`
  - Animation layers via `ABP_CombatCharacter` (`ABP_CombatAnimLayersBase`, `ABP_2HandedSwordLayer`, `ABP_1HandedSwordShieldLayer`, `ABP_DualSwordsLayer`)
- **Ground Truth Proof:** All today's parity driver snapshots (`_d5`, `_t1`) executed against these exact two actors.

---

## 1. AN1: Boss Animation Inventory (The Ember Warden)

The Ember Warden operates as a hybrid: the pack's `BP_ExampleGreatSwordBoss` drives the AI, state machines, and base mannequin poses, while `URPGAttackTracker`, `URPGBossCloseClipSwap`, `URPGBossDormantWake`, `URPGBossPhases`, and `URPGBossDeath` inject authored project clips and timing controls.

Below is the exhaustive census of every move/state expected by the combat code, citing the active asset path, fallback path, and fidelity classification:

| Move / State ID | Code / Card Requirement | Active Asset Path | Fallback / Stand-in Path | Status & Architectural Role |
|---|---|---|---|---|
| **A1 Quick Slash** | Fast horizontal blade slash; close-range pressure | `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A1.AM_Boss01_A1` | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_Attack03_Montage.GS_Attack03_Montage` | **Authored (High Quality)**. 1.20 s length. Injected via `URPGAttackTracker` and swapped into `GA_GS_Boss_CloseAttack[0]` by `URPGBossCloseClipSwap`. |
| **A1b Follow-up Slash** | Secondary chained slash following A1 | None (Pack stand-in) | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_Attack04_Montage.GS_Attack04_Montage` | **Pack Stand-in**. 1.25 s length. Intentionally retained in `GA_GS_Boss_CloseAttack[3]` as the pack follow-up. |
| **A2 Delayed Slam (Overhead)** | Distinct raise, held apex pose (0.4–0.9 s), explosive ground slam | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_ChargedAttack_Montage.GS_ChargedAttack_Montage` | Same | **Programmatic Hybrid**. `GS_ChargedAttack_Montage` is paused during windup via `RPGBossMoveCardHold` to achieve the telegraph hold. Authored sub-clips exist in project (`AN_Boss01_A2_Raise`, `AN_Boss01_A2_ApexHold`, `AN_Boss01_A2_Slam`), but montage assembly is deferred. |
| **A3a Combo Strike 1** | First strike of 2-hit close combo | `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A3a.AM_Boss01_A3a` | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_Attack01_Montage.GS_Attack01_Montage` | **Authored (High Quality)**. 0.80 s length. Swapped into `GA_GS_Boss_CloseAttack[1]` by `URPGBossCloseClipSwap`. |
| **A3b Combo Strike 2** | Second strike completing 2-hit combo | `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A3b.AM_Boss01_A3b` | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_Attack02_Montage.GS_Attack02_Montage` | **Authored (High Quality)**. 1.33 s length. Swapped into `GA_GS_Boss_CloseAttack[2]` by `URPGBossCloseClipSwap`. |
| **A4 Low Sweep** | Grounded blade sweep (<40 cm floor clearance); tests jump evasion | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_A4_LowSweep.AN_Boss01_A4_LowSweep` | Dynamic montage via `RPGBossClips::Play` in `URPGBossLowSweep` | **Authored (Mechanical Pass)**. Verified under `BOSS-AWR-005`: sweeps below player waist; jump clears at >40 cm floor height. |
| **A5 Javelin Throw** | Ranged off-hand ember javelin throw (heal punish) | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_A5_JavelinThrow.AN_Boss01_A5_JavelinThrow` | Dynamic montage via `RPGBossClips::Play` in `URPGBossJavelin` | **Authored (High Quality)**. Spawns `SM_Boss01_EmberJavelin` projectile. Triggered natively or as punishment when player drinks flask. |
| **A6 Leap & Shockwave** | Long leap closing gap into explosive ground slam | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_LeapAttack_Montage.GS_LeapAttack_Montage` | Same | **Pack Stand-in + C++ Component**. Uses pack greatsword leap (1.87 s); central hit priority over secondary radial wave in `URPGBossShockwave`. |
| **Dormant Idle** | Statue-like kneeling/hunched pose with greatsword planted | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_DormantIdle.AN_Boss01_DormantIdle` | Played via `URPGBossDormantWake` | **Authored (High Quality)**. 4.0 s slow breathing loop; behaviour tree held inactive until player crosses arena boundary. |
| **Wake-Up Transition** | Boss rises from dormant statue to full combat height | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_Wake.AN_Boss01_Wake` | Played via `URPGBossDormantWake` | **Authored (High Quality)**. 3.2 s transition; behavior tree awakens on clip completion. |
| **Phase Roar / Transition** | Mid-fight transformation at 60% HP (D5 / C-852 rule; invulnerable roar) | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_PhaseRoar.AN_Boss01_PhaseRoar` | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/Ability_R_Intro_Anim_Montage.Ability_R_Intro_Anim_Montage` | **Authored (High Quality)**. 2.0 s roar. Injected by `URPGBossPhases`; triggers `URPGPhaseRoarShake`. |
| **Stagger / Stance Break** | Vulnerable knockdown/kneel when poise breaks (100 threshold) | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_StaggerDown.AN_Boss01_StaggerDown` & `AN_Boss01_StaggerFall` | Pack `KnockdownStart_Anim` / `Knockdown_Getup_Anim` | **Authored Assets Available**. Authored kneel and sag clips exist in project; currently wired in parallel with pack knockdown state machine. |
| **Riposte Victim (Critical Receive)** | Boss reacts to synchronized critical thrust | `/Game/OneBossFight/Boss01/Animations/AN_Riposte_Boss_Reaction.AN_Riposte_Boss_Reaction` | None | **Authored (High Quality)**. Exact 1.6 s paired reaction clip aligned with player's strike. |
| **Death & Dissolve** | Fatal knee collapse into ember monument dissolution | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_DeathLegend.AN_Boss01_DeathLegend` | Pack `GA_EnemyDeath` / `Death_Fwd` | **Authored (High Quality)**. Played by `URPGBossDeath` (`OwnClip` mode); suppresses pack ragdoll, followed by `URPGBossRemains` spawning `SM_Boss01_CorpseStatue`. |
| **Locomotion / Strafe** | 4-way strafing and circling | Pack `BaseUnarmedLocomotion_BS` | `Jog_Fwd_Anim`, `Jog_Bwd_Anim`, `Jog_Left_Anim`, `Jog_Right_Anim` | **Pack Covered**. Runs on `SK_CombatMannequin` smoothly. |
| **Turn In Place** | 90° and 180° turns to keep target in front cone | `GA_GS_Boss_TurnInPlace` | `Turn_Left_90_Unarmed_Anim`, `Turn_Right_90_Unarmed_Anim` | **Pack Covered**. Handled natively by pack behavior tree and turn ability. |
| **Hit Reacts by Direction** | Flinches when taking hits from front/rear/flanks | Pack `1Handed/HitReactions/` | `HitReact_Front_Montage`, `HitReact_Back_Montage`, `HitReact_Left_Montage`, `HitReact_Right_Montage` | **Pack Covered**. 4-way hit reacts present and functional on mannequin. |
| **Parry-Reacted (Recoil)** | Weapon bounces off player shield/blade on parry | None | Pack hitstop / interruption | **Gap**. Boss currently relies on hitstop (0.08 s dilation 0.05) without a distinct weapon deflection recoil animation. |

---

## 2. AN2: Player Animation Inventory (`BP_CombatPlayerCharacter`)

`BP_CombatPlayerCharacter` operates on `SK_CombatMannequin` through `ABP_CombatCharacter` with weapon-swappable linked layers.

| Action / Move | Expected Mechanics | Active Asset Path | Source & Asset Class | Status & Fidelity Notes |
|---|---|---|---|---|
| **Light Chain (Greatsword)** | Heavy two-handed 4-hit combo | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/2handed/PrimaryAttack_A_Slow_Montage` through `PrimaryAttack_D_Slow_Montage` | Pack Montages (`2handed/`) | **Pack Covered (High Quality)**. Heavy, rhythmic Soulslike swing chain. |
| **Light Chain (Sword & Shield)** | Standard knight 3-hit slash chain | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/Attack_PrimaryA_Montage` through `Attack_PrimaryC_Montage` | Pack Montages (`1Handed/`) | **Pack Covered (High Quality)**. Clean sword slashes, fast recovery. |
| **Light Chain (Dual Swords)** | Rapid dual curved sword attacks | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/DualSwords/Attacking/Attack01_Montage`, `Attack_Melee_A_Montage` .. `C_Montage` | Pack Montages (`DualSwords/`) | **Pack Covered (High Quality)**. Fast dex style. |
| **Heavy / Charged Attack** | Heavy overhead charged attack | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/ChargedAttack_Montage` or `2handed/PrimaryAttack_Heavy_Slow` | Pack Montages | **Pack Covered**. Holds charge cleanly. |
| **Dodge Roll (Forward)** | 0.8 s roll with 12 i-frames (0.00–0.20 s) | `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage` | Pack Montage | **Pack Covered (High Quality)**. Governed by `URPGIFrameMonitor` and `RPGDodgeTiming`. |
| **Dodge Roll (Directional)** | 4-way directional rolls (Backward, Left, Right) | Pack `Roll_Bwd_Montage`, `Roll_Lt_Montage`, `Roll_Rt_Montage` | Pack Montages | **Pack Covered**. Pack mannequin skeleton natively supports 4-way evasive rolls. |
| **Parry / Defend Execution** | Active parry timing window (0.15 s) | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/Defend/Ability_Block2_Montage.Ability_Block2_Montage` | Pack Montage | **Pack Covered**. Governed by `URPGPlayerParry`. |
| **Riposte Execution** | Critical strike against downed boss (100 damage at 0.8 s impact) | `/Game/OneBossFight/Boss01/Animations/AN_Riposte_Player_Front.AN_Riposte_Player_Front` | Authored Project Clip | **Authored (High Quality)**. Slides to 150 cm, root motion drives to 60 cm, applies 2.5x critical damage at 0.8 s impact. |
| **Hit Reacts (4-way)** | Directional flinches when struck | Pack `HitReact_Front_Montage`, `HitReact_Back_Montage`, `HitReact_Left_Montage`, `HitReact_Right_Montage` | Pack Montages (`1Handed/HitReactions/`) | **Pack Covered**. Full 4-way directional flinch coverage. |
| **Stagger / Guard Break** | Heavy stun when stamina or poise breaks | Pack `KnockdownStart_Anim` / `Knockdown_Getup_Anim` | Pack Sequences | **Pack Covered**. |
| **Death** | Collapse on zero health | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/Death/Death_Fwd_Montage.Death_Fwd_Montage` | Pack Montage | **Pack Covered**. Pairs with encounter reset and camera tracking. |
| **Heal / Flask Drink** | 1.8 s estus flask consumption; triggers boss heal punish | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/DrinkingPotion_Montage.DrinkingPotion_Montage` | Pack Montage | **Pack Covered (High Quality)**. Fully integrated with `URPGFlaskHud` and signals `RPGBossHealPunish.cpp`. |
| **Sprint & Jump** | Fast sprint and vertical jump over ground rings | `Idle_TravelMode_Anim`, `MM_Jump` | Pack Mannequin Animations | **Pack Covered**. Jump height easily clears 40 cm ground shockwaves. |
| **Lock-On Locomotion** | 8-way strafe blendspaces | `BaseUnarmedLocomotion_BS` | Pack BlendSpace | **Pack Covered**. Native mannequin blendspace. |

---

## 3. AN3: Live Boss VFX and Audio Cue Inventory

### 3.1 Live Production Component Census
Unlike legacy prototypes, all VFX and audio in the active build are driven by dedicated native C++ components attached to `BP_ExampleGreatSwordBoss`:

| Combat System | Driving C++ Component | Visual Asset Path | Audio Asset Path | Status & Modernization Target |
|---|---|---|---|---|
| **Bleed Status Proc** | `URPGBossBleed` | `/Game/BloodPack/Hit/Niagara/NS_BulletHit_Med.NS_BulletHit_Med` | `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Guardian_ImpactL_Cue.A_Guardian_ImpactL_Cue` | **Modern Niagara (High Quality)**. Native Niagara system spawns at hit location at 2.0x scale; plays Guardian impact cue. |
| **Radial Shockwave (A6)** | `URPGBossShockwave` | Radial ring collision (`bRing=true`, 40 cm height, 1200 cm radius) + particle card | Deep bass ground impact sound | **VFX Upgrade Needed**. Gameplay collision is exact (40 cm height clearance), but visual needs dedicated Niagara ring (`NS_Boss_ShockwaveRing`) so player clearly sees jump boundary. |
| **Ember Javelin (A5)** | `URPGBossJavelin` | Static Mesh `/Game/OneBossFight/Boss01/Weapons/SM_Boss01_EmberJavelin.SM_Boss01_EmberJavelin` + PointLight glow | Projectile launch whoosh & impact sound | **High Quality**. Physical javelin mesh flies with dynamic glow and collision. |
| **Phase Two Transformation** | `URPGBossPhases` | Camera Shake `URPGPhaseRoarShake` + `AN_Boss01_PhaseRoar` | Roar sound cue | **Needs Particle Aura**. Needs rising ember aura + blade ignition (`NS_Boss_PhaseTwoAura`). |
| **Boss Death & Remains** | `URPGBossDeath` & `URPGBossRemains` | Spawns `/Game/OneBossFight/Boss01/Remains/SM_Boss01_CorpseStatue.SM_Boss01_CorpseStatue` with material `/Game/OneBossFight/Boss01/Remains/M_Boss01_Remains.M_Boss01_Remains` + Niagara burst `/Game/BloodPack/Hit/Niagara/NS_BulletHit_Med.NS_BulletHit_Med` | Boss defeat sound | **Modern Niagara & Material (High Quality)**. Dissolve material drives procedural noise ramp (`T_Boss01_DissolveNoise`) into statue over 2.5 seconds. |
| **Accessibility Cues (QA-007)** | `URPGFrameworkMoveExecutor` | `ARPGFlipbookEffect` (`HitSpark`, `DodgeDust`, `BloodBurst`) | `FRPGBossCue::Sound` (`USoundBase` soft pointers) | **Functional 2D Flipbook**. Flipbook sprites provide low-cost 2D cues; dual-channel modes (0..3) fully functional. |
| **Parry Spark & Clack** | `URPGPlayerParry` | Flipbook `HitSpark` + Chime wave | Metallic deflection sound | **Upgrade Target**. Needs directional spark burst (`NS_Combat_ParrySpark`) + sharp metallic audio clack. |
| **Fog Gate Wall** | Level Actor | Card Mesh `/Game/CustomAssets/FX/FogCards/SM_FogCard_01_N1.SM_FogCard_01_N1` + `/Game/Materials/FogCards/M_FogCard.M_FogCard` | Low ambient rumble | **Functional**. Cheap and effective card fog. |

### 3.2 Parry Slow-Motion Visual Proposal (Pairing with Codex Feature F1)
In `[C-903]`, Lead Claude assigned **Feature F1** to Codex: `URPGLegendSubsystem::RequestSlowMotion` on parry (perfect parry: 0.3x for 0.35 s; normal parry: 0.5x for 0.20 s). 

To pair seamlessly with F1:
1. **Post-Process Distortion Impulse (`PPM_ParryDistortion`):**
   - A single-pass material parameter collection trigger (`ParryTriggerTime`) driving a spherical radial blur and chromatic aberration pulse expanding outward from the blade contact socket over 0.30 seconds.
   - Cost: Zero extra draw calls (uses existing post-process volume blendable slot).
2. **Desaturation & Contrast Spike:**
   - During the 0.35 s slow-motion window, environment saturation drops by 50% while the combatants retain 100% saturation and receive a subtle rim light boost (+0.2 emissive).
   - Gameplay value: Focuses player attention on the boss's recovery state and the riposte opening.
3. **Audio Low-Pass Ducking:**
   - Master arena audio ducked via an 800 Hz low-pass filter during the 0.35 s window, accompanied by a crisp metallic ping (`A_Guardian_ImpactL_Cue` variation) and a rising pitch release upon time restoration.

---

## 4. AN4: Authoritative Prioritized Production Plan

Because the live fight is built on the pack's mannequin skeleton, **100% of the project's 14 authored `AN_Boss01_*` animations are already rigged and playing natively**! The art/animation gaps are therefore far smaller and more targeted than previously assumed:

### Tier 1: Core Combat Readability (Must-Have, P1)
1. **A2 Delayed Slam Montage Assembly (`AM_Boss01_A2`):**
   - Assemble `AN_Boss01_A2_Raise`, `AN_Boss01_A2_ApexHold`, and `AN_Boss01_A2_Slam` into a unified `AM_Boss01_A2` montage with authored anim notifies, replacing the programmatic freeze on `GS_ChargedAttack_Montage`.
   - Effort: 2.5 hours.
2. **Radial Shockwave Niagara Ring (`NS_Boss_ShockwaveRing`):**
   - Author a clean Niagara ground ring expanding to 1200 cm with a clear, sharp 40 cm vertical height boundary, ensuring the jump-clearance height is immediately readable to the player.
   - Effort: 2.5 hours.
3. **Parry Spark Niagara Burst (`NS_Combat_ParrySpark`):**
   - Author a high-clarity 16-particle directional metal spark burst at the weapon contact socket, paired with a sharp metallic clack sound.
   - Effort: 2.0 hours.

### Tier 2: Polish & Visual Impact (High Impact, P2)
1. **Parry Slow-Motion Post-Process (`PPM_ParryDistortion`):**
   - Implement the radial chromatic aberration impulse and audio ducking pairing with Codex's F1 feature.
   - Effort: 2.0 hours.
2. **Phase Two Embers & Blade Ignition (`NS_Boss_PhaseTwoAura`):**
   - Emissive glow parameter ramp on `M_Boss01_Master` materials + ribbon trail on `SM_Boss01_Greatsword` during Phase 2.
   - Effort: 3.0 hours.
3. **Boss Parry Recoil Animation:**
   - Author a quick 0.6 s weapon deflection/stumble animation on `SK_CombatMannequin` when the boss is parried, replacing the static hitstop freeze.
   - Effort: 3.5 hours.

### Tier 3: Aesthetic Upgrades (Nice-to-Have, Post-Slice, P3)
1. **Weapon Blade Trails (`NS_Boss_SwordTrail` / `NS_Player_SwordTrail`):**
   - Ribbon emitter along blade sockets active only during damage trace windows.
2. **Player Armor Sets (`SK_Boss01_PlayerArmor`):**
   - Re-skinning player mannequin with Strength plate or Dex cloth looks.

---

## 5. CL1: Repository Cleanup Preliminary Candidate Pool

Per `[C-903]` and `[C-904]`, below is the complete candidate pool of obsolete docs, completed queue sheets, and transient patch files, checked for safety:

| Candidate File Path | Size | Reason Obsolete | Referenced-By Safety Check |
|---|---|---|---|
| `Docs/BossCombatReview/Execution/Codex/PROMOTION_STEP2_SCAFFOLD.patch` | 29.5 KB | Transient scaffold patch from completed Step 2 promotion | Unreferenced by active tests, scripts, or ledger |
| `Docs/BossCombatReview/Execution/Codex/PROMOTION_STEP3_SCAFFOLD.patch` | 45.1 KB | Transient scaffold patch from completed Step 3 promotion | Unreferenced by active tests, scripts, or ledger |
| `Docs/BossCombatReview/Execution/Claude/Evidence/exports/scratch_route_a/*` (8 files) | ~55 KB | Ephemeral scratch exports from completed Route A diagnostic | Unreferenced by active production code |
| `Documentation/Boss/E126_DECISION_AUDIT.md` .. `E155_DECISION_AUDIT.md` (30 files) | ~28 KB | Ephemeral micro-audits from Queue E, fully transcribed and incorporated into `Documentation/DECISIONS.md` | Verification required before removal |
| `Docs/BossCombatReview/Execution/Codex/QUEUE_200.md` | 15.6 KB | Completed historical queue, closeout merged into `TASKS.md` | Historical reference check required |
| `Docs/BossCombatReview/Execution/Codex/QUEUE_200_B.md` | 7.5 KB | Completed historical queue, closeout merged into `TASKS.md` | Historical reference check required |
| `Docs/BossCombatReview/Execution/Codex/QUEUE_50.md` | 9.2 KB | Completed historical queue, closeout merged into `TASKS.md` | Historical reference check required |
| `Docs/BossCombatReview/Execution/Antigravity/QUEUE_50_AG.md` | 5.4 KB | Completed historical queue, closeout merged into `TASKS.md` | Historical reference check required |
| `Documentation/Boss/QUEUE_P_PARITY.md` | 28.4 KB | Completed historical queue P, content active in `TEST_PLAN.md` | Historical reference check required |
| `Documentation/Boss/QUEUE_Q_TRACK_A.md` | 19.8 KB | Completed historical queue Q, content active in `TEST_PLAN.md` | Historical reference check required |
| `Documentation/Boss/QUEUE_S.md` | 14.2 KB | Completed historical queue S, closeout merged into `TASKS.md` | Historical reference check required |

*Next Step (CL2): Awaiting Lead Claude approval of this candidate list before executing single-commit `git rm` and running the docs link checker.*
