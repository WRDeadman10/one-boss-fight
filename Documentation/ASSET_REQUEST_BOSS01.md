# Asset request: Boss 01 vertical slice (for Antigravity and the project owner)

Written 2026-10-20 by Claude. Scope: only 3D models, animations and VFX. Audio is a separate list (later).
Authority: `Master_Design_Freeze_v1_2_AI_Implementation_Ready.md` (the "Freeze") decides mechanics and numbers. This file
decides what art has to exist for those mechanics to be built and how it must be handed over.

## 1. Purpose of this document

Code, data and tests are done by Claude. Art is not. Every item below is something the Freeze requires that the project
cannot produce from what it already owns. The document exists so that Antigravity (and the owner) can:

1. See exactly which gaps are real, in priority order, and which gate each one blocks.
2. Build or source each asset to one format, so it drops into the editor without rework.
3. Work in parallel: Claude builds logic against stand-in assets (pack animations, engine cubes) and swaps the real
   asset in when it lands. Nothing here blocks code work until a gate says so.

Nothing in this file changes a Freeze rule. Where the Freeze names a prop (cane, golden dagger, hammer) this file
re-skins it (section 2) without changing the mechanic.

## 2. Boss 01 brief (original design, "legendary" feel)

Working title: **The Ember Warden** (placeholder; real name and story come in the story step).

- A fallen sentinel knight, 310 cm tall, two-handed great sword. Reads as ancient and sorrowful, not a generic monster.
- Silhouette must read at 30 m in fog: tall pointed helm or broken crown, long torn cape, one oversized pauldron, sword
  planted in the ground while dormant.
- Palette ties to the arena: black plate, dull iron, crimson cloth with gold trim (same as the arena banners), ember
  orange glow in armor seams and eyes. Phase two: more glow, armor cracks open, blade ignites.
- Why this skin: the Freeze mechanics (A1 to A6) are kept as they are. The Freeze props change so the boss is not a
  Margit copy: cane becomes the great sword (A4 is a low sweep with the blade), golden dagger becomes an ember javelin
  thrown with the off hand (A5), hammer becomes the same sword driven into the ground in the leap (A6). One weapon
  mesh instead of three, so less art and a stronger identity.
- Legendary-feeling beats (art needed for each is listed below): dormant pose with sword planted, a rising wake-up,
  fog-gate close, name banner, phase-two transformation, ember dissolve on death.

## 3. Handover format (every delivery)

| Item | Rule |
|---|---|
| Skeleton | Everything that plays on the boss or the player must use the **UE5 mannequin skeleton** the Advanced ARPG pack uses (`/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin`; reference mesh FBX in `Import/ThirdParty/Reference/SKM_CombatMannequin_Simple.fbx`). Do not add or rename bones. Extra cape or cloth bones are allowed as children of existing bones only |
| Units and axes | 1 unit = 1 cm, Z up, character faces +X, origin between the feet |
| Format | FBX (2020 or newer, binary), animation baked at 30 fps, no scale on the root, no leftover Blender armature object transforms |
| Location on disk | Own work (made by Antigravity in Blender): `Import/Boss01/<Category>/` and it may go to git. Downloaded or free-pack material: `Import/ThirdParty/` and `Content/ThirdParty/<PackName>/` (git ignored) |
| Naming | `SK_Boss01_*` skeletal mesh, `SM_Boss01_*` static mesh, `AN_Boss01_<Move>_<Part>` animation, `NS_Boss01_<Effect>` Niagara. Players: `AN_Player_*` |
| Root motion | State per clip: `in place` or `root motion`. Default is in place. Leaps and the riposte pair are the only root motion candidates |
| Loops | State per clip: loop or one shot. A loop must match first and last pose exactly |
| Timing sheet | Each animation comes with a text note (same folder, `<clip>.txt`): clip length in seconds, and these times in seconds from clip start when the move has them: `ApexReached`, `CommitTime` (last moment the boss may still turn), `ActiveStartTime` (blade can first hurt), `ActiveEndTime`, `RecoveryEndTime`. Times are what the animation shows, not what the game should do. Claude places the notifies from them |
| Sockets | Weapon meshes carry the same five sockets as the pack's `SM_KwangSword`: `BladeStart`, `BladeEnd`, `MiddleSocket`, `Weapon Start`, `Weapon End` (read in the editor, `DELTA_AUDIT.md` section 1). Reference FBX: `Import/ThirdParty/Reference/` |
| Proof | One preview render or a short playblast per clip (`.mp4` or `.gif`) next to the file |
| Verdict | Claude records each delivery in `TASKS.md` as Accepted or Returned with the reason. Nothing is wired in before then |

## 4. What the pack already covers (verdicts updated 2026-10-20 in `DELTA_AUDIT.md` section 2)

Source: names under `Advanced ARPG Combat System V3 - Unreal Engine\Content\AdvancedARPGCombat\...`. A name proves an
asset exists, not that it looks right. Claude confirms look and timing in task G0-2 and updates the status column.

| Need | Pack asset seen | Status |
|---|---|---|
| A1 quick slash, A3 combo | `GS_Attack01` to `GS_Attack04` montages (great sword boss) | Likely covered |
| A2 delayed overhead | `GS_ChargedAttack_Montage`, `ChargedAttack_Montage` | Partial. No held apex pose seen. Needs section 5.2 |
| A4 low sweep | nothing by name | **Gap** |
| A5 thrown projectile | only a fireball cast and `SM_Dagger_SpinTrail` (a trail mesh) | **Gap** |
| A6 leap | `GS_LeapAttack_Montage`, `GS_SprintAttackFollowUp_Montage` | Likely covered; may need a longer recovery clip |
| Roar for phase two | `Ability_R_Intro_Anim_Montage` (already used) | Covered, upgrade optional |
| Stance break fall and get up | `KnockdownStart_Anim`, `Knockdown_Getup_Anim` (already used) | Covered, a kneel pose would look better |
| Riposte pair | `GA_Player_FatalityAttack`, `GA_FatalityVictim`, backstab twins (abilities, montage names unknown) | Unknown. Claude checks first |
| Boss death | `GA_EnemyDeath`, `Death_Fwd`, `Death_Back` | Covered, legendary version optional |
| Dormant and wake | nothing | **Gap** |
| Strength build (great sword) | 2handed: four `PrimaryAttack_*_Slow`, charged, jump, `Ability_R` | Covered |
| Dex build (curved or twin blades) | `DualSwords` (A, B, C, air, dash, guard break) and `Twinblades` (A to E, air) | Covered; weapon meshes unknown |
| Flask drink | `DrinkingPotion_Montage` | Covered |
| Boss and player meshes | only the mannequin and a few armor pieces | **Gap** (section 5.1) |

## 5. The asset list

Priority: **P1** blocks a gate, **P2** needed for the polished slice, **P3** nice to have.
Wave 1 can start now. Wave 2 waits for Claude's pack check (G0-2), which will mark each row Needed or Covered here.

### 5.1 3D models

| ID | Asset | Spec | Pri | Wave | Needed by |
|---|---|---|---|---|---|
| M-01 | `SK_Boss01` body | Skeletal mesh on `SK_CombatMannequin`, authored at the skeleton's native scale (about 181 to 210 cm in mesh space; the engine scales the boss mesh 1.5, up to about 1.7 for 310 cm), silhouette per section 2. Under 80k triangles, 3 material slots (armor, cloth, glow) so glow can be driven per phase. Cape and cloth as extra child bones or a separate mesh | P1 | 1 | Gate 2 |
| M-02 | `SM_Boss01_Greatsword` | About 184 cm long (same as the pack's `SM_KwangSword`, which the engine scales to about 276 cm on the boss), unique design (broken-crown guard, notched blade). Sockets exactly as `SM_KwangSword`: `BladeStart`, `BladeEnd`, `MiddleSocket`, `Weapon Start`, `Weapon End`. Separate emissive material slot for the ignite effect. Under 15k triangles | P1 | 1 | Gate 1 |
| M-03 | `SM_Boss01_Javelin` | Thrown ember javelin, about 180 cm, projectile mesh. Under 3k triangles | P2 | 1 | Gate 2 |
| M-04 | Boss off-hand detail | Gauntlet or brazier-gauntlet that glows when A5 charges. Can be part of M-01 | P2 | 1 | Gate 2 |
| M-05 | Dex build weapons | Two curved swords (katana or scimitar style), 100 cm each, sockets as M-02 | P2 | 2 | Gate 3 |
| M-06 | Player armor sets | Strength: heavy plate look. Dex: light cloth and leather look. Skeletal meshes on the same skeleton as the mannequin, replacing the mannequin body. Antigravity reports Greystone armor pieces already rigged to the mannequin (Viking, Knight, Samurai, Yoddha looks): reuse those first | P2 | 2 | Gate 3 |
| M-07 | Build shrine | A small stone or sword-in-ground piece where the player picks a build, 150 to 250 cm | P2 | 2 | Gate 3 |
| M-08 | Fog gate frame | Stone frame for the entrance fog wall (the arch currently reads as two huge slabs), 800 cm wide | P3 | 2 | Gate 4 |
| M-09 | Boss corpse or cracked statue | What remains after the ember dissolve (optional) | P3 | 2 | Gate 4 |

### 5.2 Animations (all on the mannequin skeleton)

All boss clips are for the 310 cm boss: slow, heavy, weight-shifted. The `time` figures are the Freeze starting
values (A2 hold 1.20 s, commit 0.25 s before active); the clip decides the real numbers and the timing sheet reports them.

| ID | Clip | What it must show | Length guide | Pri | Wave | Needed by |
|---|---|---|---|---|---|---|
| A-01 | `A2_Raise` | Great sword lifted overhead in both hands, body leaning back, readable intention | 0.5 to 0.7 s | P1 | 1 | Gate 1 |
| A-02 | `A2_ApexHold` | Stable held pose at the top: tiny chest breathing and arm tension only, no drift. Loops cleanly (the Freeze forbids slowing a clip to fake a hold) | 1.0 to 1.2 s loop | P1 | 1 | Gate 1 |
| A-03 | `A2_Slam` | Fast downswing, blade hits the floor in front of the boss, brief dig-in, then weight settle and slow recovery straight into idle. Mark `ActiveStart`, `ActiveEnd`, `RecoveryEnd`. Blade must travel visibly before it hurts | 0.15 s swing, 1.2 s recovery | P1 | 1 | Gate 1 |
| A-04 | `A4_LowSweep` | Wind back and step in, then a wide horizontal sweep with the blade held low (the whole blade below knee height of the 190 cm player, 40 cm above floor at most), long recovery | windup 0.6, active 0.3, recovery 0.85 | P1 | 1 | Gate 2 |
| A-05 | `A5_JavelinThrow` | Great sword carried one handed in the right hand (point down), left hand charges a glowing javelin (0.4 s telegraph), then a hard throw, then recovery | 0.4 + flick + 0.6 s | P1 | 1 | Gate 2 |
| A-06 | `Boss_DormantIdle` | Kneeling or standing hunched, great sword planted point down in front, both hands on the pommel. Slow breathing loop | 4 to 6 s loop | P2 | 1 | Gate 4 |
| A-07 | `Boss_Wake` | From dormant to combat idle: head lifts, hands tighten, sword pulled out of the floor, stands to full height | 3 to 4 s | P2 | 1 | Gate 4 |
| A-08 | `Boss_StanceBreakKneel` | Loop where the boss drops to one knee and sags (the poise-broken state) with an exposed front. The riposte targets this pose | 2.5 s loop plus 0.6 s in and out | P2 | 2 | Gate 2 |
| A-09 | `Boss_PhaseTwoTransform` | Replaces the pack roar: the boss drives the sword into the ground, arms spread, armor cracks open (frame marker for the glow burst) | 2.0 s | P2 | 2 | Gate 2 |
| A-10 | `Boss_LeapExtra` | Only if the pack leap is too short: a heavier takeoff and a long crouched recovery after landing. Root motion with a fixed forward travel of 800 cm | 1.5 s | P2 | 2 | Gate 2 |
| A-11 | `Riposte_Player_Front` and `Riposte_Boss_Reaction` | Paired, aligned to one reference point: the player stands 150 cm from the boss front, plants a hard strike, the boss reacts. Impact frame marked. One pair for the great sword, one for the dual curved swords if time allows. Root motion on the player clip is allowed | 1.4 to 1.8 s | P1 | 2 | Gate 2 |
| A-12 | `Boss_DeathLegend` | Drops to both knees, sword falls, body slumps and stays (ember dissolve is VFX V-09) | 3 to 4 s | P3 | 2 | Gate 4 |
| A-13 | Dex combo polish | Only if the pack dual sword or twinblade chains look wrong on the boss target: four light attacks with distinct stages (Freeze section 20.2) | per clip | P2 | 2 | Gate 3 |

Cloth: the cape and banner motion is not an animation request. Claude drives it in the engine (sway or cloth).

### 5.3 VFX (Niagara for UE 5.5, no Cascade, no particle system that needs a missing plugin)

Rules: every effect is a Niagara system with exposed `Color`, `Intensity` and `Scale` user parameters, a one shot or a
loop that stops cleanly, GPU cost low (the arena already runs many lights and embers), no baked flipbooks over 1k.
Avoid the Blood VFX pack already in the project: its effects show nothing in UE 5.5 (KI-024).

| ID | Effect | Behavior | Pri | Wave | Needed by |
|---|---|---|---|---|---|
| V-01 | `NS_Boss01_SwordTrail` | Ribbon trail along the blade base to tip, active during the active trace window only, fades in 0.08 s, ember orange | P1 | 1 | Gate 1 |
| V-02 | `NS_Boss01_CommitFlash` | A short bright glow on blade and eyes at the commit point so the player can learn the timing. This is the main readability cue | P1 | 1 | Gate 1 |
| V-03 | `NS_Boss01_SlamImpact` | Ground impact: dust burst, ember burst, a fading crack decal, 300 cm radius, 0.6 s | P1 | 1 | Gate 1 |
| V-04 | `NS_Boss01_Shockwave` | Radial ground wave for A6, expanding from the center to 1200 cm, low to the floor (about 40 cm high ring, bright edge) so the player can see the height and jump it | P1 | 1 | Gate 2 |
| V-05 | `NS_Boss01_LandingWarning` | Ground circle warning for the leap landing spot, 0.8 s before impact | P2 | 1 | Gate 2 |
| V-06 | `NS_Boss01_PhaseTwoAura` | Loop: embers rising from the body, glowing armor cracks (material parameter driven), sword ignition along the blade | P1 | 1 | Gate 2 |
| V-07 | `NS_Boss01_TransformBurst` | One shot at the transformation frame of A-09: ember explosion and a short light flash | P2 | 2 | Gate 2 |
| V-08 | `NS_Boss01_Javelin` | Projectile trail and impact for A5 (ember streak, small burst on hit and on miss) | P2 | 1 | Gate 2 |
| V-09 | `NS_Boss01_DeathDissolve` | The body turns to embers from the feet up over 4 s, with a final flare. Needs a dissolve material for M-01 | P2 | 2 | Gate 4 |
| V-10 | `NS_Boss01_PostureBreak` | Short metallic spark burst on the boss chest when posture breaks (pairs with the chime) | P1 | 2 | Gate 2 |
| V-11 | `NS_Boss01_RipostePrompt` | Small glowing marker above the exposed boss chest while a riposte is possible | P2 | 2 | Gate 2 |
| V-12 | `NS_Player_BleedProc` | Blood burst on the boss at a hemorrhage proc, must work in 5.5 | P2 | 2 | Gate 3 |
| V-13 | `NS_Player_HitSpark` | Weapon hit spark for light and heavy hits, two intensities | P2 | 2 | Gate 3 |
| V-14 | `NS_Player_DodgeDust` | Small dust puff on roll start and end | P3 | 2 | Gate 4 |
| V-15 | `NS_Boss01_FogGate` | Thicker fog wall that fades in over 1.5 s (the gate closing) and out over 2 s. Claude has fog cards now; a Niagara version is an upgrade | P3 | 2 | Gate 4 |

## 6. Gaps Claude feels right now (be honest list)

1. **No boss silhouette.** The fight currently uses the pack's example boss. It cannot read as a legend until M-01 and
   M-02 exist. This is the largest gap for the portfolio.
2. **No hold pose for the slam, no low sweep, no throw.** Without A-01 to A-05 the Freeze's core attacks cannot be
   built, only approximated by pack clips.
3. **No riposte pair.** The pack may have one (fatality), unconfirmed. If not, A-11 is the one clip the whole stance
   break loop depends on.
4. **No dormant or wake animation.** The boss currently just stands until the player comes close.
5. **VFX that can show the timing.** The commit flash (V-02) and the shockwave height (V-04) are gameplay information,
   not decoration. Without them the dodge and jump cannot be tested fairly.
6. **Dex build look.** The pack covers the swing animations; weapon meshes and a distinct light armor look are missing.
7. **The pack boss mesh and sockets are unknown to me.** I have not opened the pack boss skeletal mesh, its sockets or
   its scale. G0-3 does this before any weapon is made.
8. **Facial or cloth animation, voice and lip sync are out of scope.**

## 7. Delivery order (suggested)

1. M-02 sword + A-01/A-02/A-03 + V-01/V-02/V-03 (Gate 1: the single delayed slam).
2. M-01 boss body (with all other boss clips retargeted to it).
3. A-04, A-05, M-03, V-04, V-06, V-08, V-10 (Gate 2 attacks and phase two look).
4. A-11, A-08, A-09 (stance break and riposte, after Claude's pack check).
5. A-06, A-07 and the polish items (Gate 4 presentation).
6. Dex build items (Gate 3).

Questions for Antigravity: do you author directly in Blender with the UE5 skeleton rig, or retarget other motion data?
Do you have editor access to this project, or hand over files only? (See `TASKS.md`, ownership rules.)
