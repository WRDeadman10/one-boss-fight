# Delta audit: Freeze v1.2 against the project (G0-1, G0-2, G0-3)

2026-10-20, Claude. Read only: no gameplay file, Blueprint or asset was changed. Evidence labels follow Freeze 8.3.
"Code-confirmed" = I read the C++ in `Source/OneBossFight/`. "Runtime-confirmed" = an earlier PIE run recorded in `TEST_PLAN.md`,
not re-run today. Pack Blueprints are read by name and notifies only (graphs not traced end to end), so pack behavior is at best Present.

## 1. Pack facts for Antigravity (G0-3, read in the editor today)

| Fact | Value |
|---|---|
| Boss Blueprint | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss` (parent `BP_MasterSoulEnemy_C`) |
| Boss and player mesh | both use `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin_Simple` |
| Skeleton | `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin` (the one skeleton all pack animations use) |
| Mannequin size | 111 x 42 x 181 cm at scale 1 |
| Boss scale | mesh component scale **1.5** (so 272 cm tall), mesh offset z -142, capsule radius 63, half height 144. Actor scale 1 |
| Player | capsule radius 42, half height 96, mesh scale 1 |
| Skeleton sockets (43) | hands: `HandRTrace`, `HandLTrace`, `WeaponSocket_R`, `WeaponSocket_L`, `HeavySwordSocket_R` (on `hand_r`), `KatanaSocket`, `Twinsword_L/R`, `Hand_RTwinBlade_L/R`, `SnS_Socket`, `AxeSocket`, `ShieldSocket`; back: `GreatSwordAttachSocket` (spine_02), `HeavySwordSheath_Back`, `DualSwordSheath_L/R`, `TwinbladeSheath_L/R` (spine_01); feet: `FootRTrace`, `FootLTrace`; magic: `Muzzle_01` (hand_r), `Muzzle_02` (hand_l), `MagicHandTarget_R`, `weapon_r_muzzle`; head: `headSocket` |
| Boss weapon | `BP_KwangSword` (`.../Blueprints/Weapons/Claymore/ClaymoreInstances/`, parent `BP_BaseWeapon_C`), mesh `.../DemoAssets/Meshes/Weapons/Paragon/SM_KwangSword`, **23 x 16 x 184 cm** (about 276 cm on the scaled boss) |
| Weapon mesh sockets (trace) | `BladeStart`, `BladeEnd`, `MiddleSocket`, `Weapon Start`, `Weapon End`. The pack's sweeping trace (`BP_SweepingSocketTraceTarget`) reads a list of socket names on the weapon mesh and builds a name per entry; it also has `TrailStartSocket` and `TrailEndSocket` for the trail. Match the Kwang sword layout: same five sockets, same names, along the blade |
| Trace notify | `ANS_CollisionTrace_C` (variables: collision target tag, event tag, attack data, swing direction, trace radius modifier) |
| Other pack notifies seen on boss and player montages | `ANS_DisableMovement`, `ANS_SetDesiredRotation` (the boss's tracking window), `ANS_HitStunImmune`, `ANS_iFrames`, `ANS_InputBuffer`, `ANS_MovementCancel`, `ANS_CancelFrames`, `AN_PerformFollowUp`, `AN_EndAnimatingAbility` |

Consequences for the request:
1. The boss body (M-01) must be authored for `SK_CombatMannequin` at **the skeleton's native scale** (bone lengths as the mannequin, character about 181 to 210 cm tall in mesh space). The engine scales the mesh component: 1.5 now, up to about 1.7 for 310 cm. Do not author at 310 cm.
2. The great sword (M-02) is authored at about 184 cm and attaches to `HeavySwordSocket_R` or `WeaponSocket_R` (I confirm which when it is wired). Same five sockets as `SM_KwangSword`.
3. The mesh component scale also scales the sword and all effects attached to boss sockets.

### Boss attack montage facts (pack, read today)

| Montage | Length | Notes |
|---|---|---|
| `GS_Attack01` | 1.20 s | rotation window 0 to 0.32 s, trace 0.17 to 0.47 s, follow-up notify 0.54 s |
| `GS_Attack02` | 1.27 s | rotation 0 to 0.24, trace 0.14 to 0.44 |
| `GS_Attack03` | 1.27 s | rotation 0 to 0.28, trace 0.12 to 0.42 |
| `GS_Attack04` | 1.47 s | rotation 0 to 0.28, trace 0.16 to 0.46 |
| `GS_ChargedAttack` | 3.40 s | no rotation notify, two trace windows: 1.57 to 1.76 and 1.93 to 2.11. A real 1.5 s delayed attack already: the stand-in for A2 |
| `GS_LeapAttack` | 1.87 s | rotation 0 to 0.16 and 0.69 to 0.83, trace 0.75 to 1.17. Covers A6 motion; no shockwave |
| `GS_SprintAttackFollowUp` | 1.87 s | two traces at 0.04 and 0.36 |
| `Knockdown_Start` / `Getup` | 1.92 / 1.40 s | getup has `ANS_iFrames` for 1.03 s |
| `Ability_R_Intro` | 1.53 s | the roar used for phase two |
| `Dodge_To_Idle` | 2.33 s | `ANS_iFrames` 0 to 0.70 s, input buffer from 0.48 s |
| `DrinkingPotion` | 1.13 s | item used at 0.51 s, cancel frames 0 to 0.32 s |

All pack montages have one section (`Default`) and no hold. The boss tracks only in the first 0.2 to 0.3 s of each montage.

## 2. Pack coverage verdict (updates the table in `ASSET_REQUEST_BOSS01.md`)

| Need | Verdict |
|---|---|
| A1, A3 | Covered by `GS_Attack01` to `04` (and the combo exists already) |
| A2 | Stand-in covered by `GS_ChargedAttack` (windup to 1.57 s). Real hold clip still needed (A-01 to A-03) for the Freeze's looping hold and the sword/body fit |
| A4 low sweep | Gap confirmed: no low sweep in the boss montages |
| A5 throw | Gap confirmed |
| A6 leap | Covered in motion by `GS_LeapAttack`; shockwave VFX and height rules are new. A-10 only if the clip feels too short |
| Roar, knockdown, getup, death, potion | Covered |
| Riposte pair | Not yet checked: needs the fatality ability graphs (G2-7 first step) |
| Dormant and wake | Gap confirmed |
| Dex build clips | Covered (DualSwords, Twinblades); meshes are straight swords (Antigravity) |

## 3. Freeze requirement status

Labels: P = Present, C = Code-confirmed, R = Runtime-confirmed earlier (see `TEST_PLAN.md`), Partial, Missing.

| Req | Freeze item | Status | Where | Gap and smallest change |
|---|---|---|---|---|
| D-01 | Tap quick, double tap full roll | C, R | `RPGDodgeTiming` | Window is **0.30 s already** in code (my earlier note of 0.35 was wrong). Window runs press to press, inclusive (`<=`). Freeze 11.2 anchor question answered: first press to second press |
| D-02 | Second tap consumed once, no triple | C, R | `ForceFullRoll`, ignore while full roll runs | Needs scripted D06 trial |
| D-03 | No-input dodge goes backward | C, R | `bBackwardWithoutInput` | Lock-on case not tested (KI-059 area) |
| D-04 | I-frames, separate windows quick/full, montage seconds | P | pack `ANS_iFrames` in `Dodge_To_Idle` (0 to 0.70 s), plays at rate 1.3 for quick | One window serves both. Needs measuring where the damage resolves and a separate quick window (G1-5) |
| D-05 | Damage rejected at resolution, not by montage | Missing (unverified) | pack damage Blueprints | Read the pack damage path first (G1-5) |
| D-06 | Cleanup on every dodge exit | Partial | pack ability end, our `bTurning` reset | Test death, reset, interruption |
| TR-01 | Swept trace, previous to current | P | pack `BP_SweepingSocketTraceTarget` (stores `LastSocketLocations`, loops sockets) | Confirm sweep and tunneling (H01 to H03) in a scripted test |
| TR-02 | Per attack instance dedupe | P | pack collision component and attack data | Read the hit set logic; confirm reset per instance (H04) |
| TR-03 | Trace stops on interrupt, stagger, death | Partial | notify end, ability end | Our stagger plays a montage over it; test H07 |
| TR-04 | Debug draw and reasons | Missing | | G0-6 |
| AI-01 | Boss state vocabulary | Partial | pack behavior tree and manager, our `Dormant/Held` flags | Map in G1-8 |
| AI-02 | Tracking only until commit, rotation lock | Partial | pack `ANS_SetDesiredRotation` windows (0.24 to 0.32 s of each montage, none on the charged attack) | Own commit notify and lock needed for A2 (G1-2) |
| AI-03 | Heal-punish A5 | Done on the delivered clip | `URPGBossHealPunish`, `ARPGBossJavelin`, tracker move A5 | Javelin effect, `JavelinSpawn` socket and flinch open. Deviation: javelin damage 12 (Freeze 30), see DECISIONS |
| ATK-01 | A1, A3 | Done on stand-ins | `URPGAttackTracker` stages A1, A1b, A3a, A3b with commitment, heading lock and the branch check | Windup length needs the authored clips |
| ATK-02 | A2 delayed overhead with hold | Partial | `GS_ChargedAttack` stand-in | Hold clip and data (G1) |
| ATK-03 | A4 low sweep | Done on the delivered clip | `URPGBossLowSweep`, tracker move A4 | Knockdown and natural selection open. Deviation: damage 20 (Freeze 50), see DECISIONS |
| ATK-04 | A6 leap and shockwave | Done on the pack leap | tracker stage A6, `URPGBossShockwave`, leap lock until phase two (`URPGBossPhases`) | Landing validation, wave visual and hit reaction open. Deviation: wave damage 48 (Freeze 120), see DECISIONS |
| POST-01 | 100 pt posture, 6 s delay, 13 per s | Missing | pack has **poise** (`BP_PoiseExtendedAttribute`), hit power maps to poise damage by `Scripts/poise_by_power.py` | Build posture component (G2-5); keep poise only as the pack's flinch gate |
| POST-02 | One break event into the stagger owner | Partial | `URPGBossStagger` triggers when the pack's hit stun ability activates | New entry point from posture (G2-6) |
| POST-03 | Stagger and cooldown visible | Partial | `CooldownSeconds` 5 s silently ignores a break, logged only | Must be visible or removed (17.2) |
| POST-04 | Critical on the riposte hit only | **Conflict** | `URPGBossStagger::ApplyCritical` multiplies all health loss while down | Remove blanket multiplier (G0-5), apply in the riposte (G2-7) |
| POST-05 | Frontal riposte, 150 cm, cone | Missing | | G2-7 |
| PH-01 | Phase two once at 0.60 | **Conflict** | `PhaseTwoHealthFraction = 0.5` in `RPGBossPhases.h` | Set 0.60 (G0-5) |
| PH-02 | Idempotent, death wins | Partial | `bPhaseTwo` set once; returns when health <= 0 | Add explicit dead flag and queue behind riposte (G2-8) |
| PH-03 | Stats scaled once | C, R | `bBuffsApplied` guard | Keep; test L04 |
| PH-04 | Queue behind stagger | C | tick skips while `IsStaggered()`, then starts | Matches 30.2 item 8 for stagger; riposte not built |
| PH-05 | Legacy fireball off | **Conflict** | `TryFireball`, `FireballAbility` granted at runtime | Disable by default (G0-5), keep the asset |
| PH-06 | Hammer spawn | Replaced | re-skin: sword ignites (VFX) | G2-8, V-06 |
| RST-01 | Reset restores all (18.3) | Partial | `URPGBossEncounter::ResetEncounter` (stagger abort, health, poise, transform, behavior, perception, montage) | Generation token and HUD state (bar, banner, victory latch) done; missing: projectiles, spawned props, audio state. G2-10 |
| RST-02 | Reset safe twice | Unknown | | Test L10 |
| RST-03 | Generation token | Missing | | G0-8 |
| DEAD-01 | Death short circuit, victory once | Done | stagger ends on death; phase ignores dead; `URPGBossHud` state machine fires `OnVictory` once per generation (L11 part) | Combat input lock and retry prompt (G2-9) |
| BLD-01 | Strength numbers | Partial | `URPGBossStagger` untouched; jump heavy poise 50 | Posture data in G3-1 |
| BLD-02 | Dex 4-hit chain | Missing | pack dual swords have A, B, C, air, dash | G3-3 |
| BLD-03 | Bleed | Missing | pack has a poison effect only | G3-4 |
| BLD-04 | Build selector | Missing | | G3-5 |
| UI-01 | Boss bar, name, posture flash, prompt | Done | `URPGBossHud` and `URPGBossHudWidget` (the pack's `BP_BossHUD` bar is collapsed by reflection on the boss's "Boss HUD" variable) | Player side stays the pack's |
| AUD-01 | Boss music phases | Partial | `URPGBossMusic` fades one track in and out | Phase swap (AU-1, G2-14) |
| ENC-01 | Dormant until 1200 cm or hurt | C, R | `URPGBossEncounter` | Keep |
| TEST-01 | Automation tests | C | 6 tests incl. gate and percentile | Extend per feature |
| DBG-01 | Debug mode (22) | Missing | | G0-6 |

## 4. Parameter registry (Freeze 36): where each value lives now

| Parameter | Freeze | Now | Owner |
|---|---|---|---|
| `Dodge.DoubleTapWindow` | 0.30 | 0.30 | `URPGDodgeTiming` |
| `Dodge.QuickDuration` / `Distance` | 0.43 s, 300 cm | 0.43 s clip at rate 1.3 (about 0.33 s), 300 cm | pack clip + `QuickPlayRate` |
| `Dodge.FullRollDuration` / `Distance` | 0.92 s, 500 cm | pack long dodge, 0.92 s, 500 cm | pack clip |
| `Boss.PostureMax / RegenDelay / RegenRate` | 100, 6 s, 13/s | none | to create (posture component) |
| `Boss.PhaseTwoThreshold` | 0.60 | 0.50 | `URPGBossPhases` |
| Phase two move, attack rate, damage scale | 1.2, 1.2, 1.25 | same | `URPGBossPhases` |
| `Boss.RiposteRange / Cone / Multiplier` | 150, 120 deg, 2.5 | none (multiplier applied to all hits) | to create |
| `Boss.StaggerHoldDuration` / `Cooldown` | 2.5, 5.0 | 2.5, 5.0 | `URPGBossStagger` |
| Heal punish range / cooldown | 400 to 1000 cm, 4 s | 400 to 1000 cm, 4 s | `URPGBossHealPunish` (`MinRange`, `MaxRange`, `Cooldown`, `FlightTime`, `Damage`) |
| Bleed values | 100, 20, 0.105, +20, 200 | none | to create |

## 5. Corrections to my earlier notes
- The dodge window was never 0.35 s in code. G0-5 no longer changes it.
- The boss is 272 cm tall (mannequin 181 cm x 1.5), not 310 cm. To reach about 310 cm, raise the mesh scale to about 1.7 (capsule and lock-on height retested then).
- The pack's `GS_ChargedAttack` is already a delayed 1.5 s attack, so Gate 1 starts with a stand-in that is close to the real thing.

## 6. Next
G0-4 is this section 4. G0-5 now means: phase two 0.60, fireball off, remove the blanket critical (move it to the riposte later). G0-6 debug mode and G0-7 timing driver come next, then Gate 1.
