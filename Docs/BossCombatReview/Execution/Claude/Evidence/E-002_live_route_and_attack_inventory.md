# E-002 Live route, decision tree and attack inventory (CI-P0-C-01 steps b/c, first pass)

> **Revision 2 (2026-10-25, after Codex review D04 R1/R2 and the hand-over).** Statements below that contradict this block are superseded: (1) the boss has 11 abilities, not 10; (2) "75 %" and "25 %" are attempt probabilities of BT chance decorators, not frequencies of successful actions (a rejected attempt falls through to later branches); (3) for MidRange/Sprint/Retaliation the omission is of the PROJECT tracker's stage, identity, heading lock, telegraph and veto; the pack's own checks (state, cooldown, `Status.ActionCommitted`) are partly read in Addendum 3 and the project's `RPGBossInterrupt::CancelOffence` closes the pack trace independently of the native move id, so "no cleanup" is too broad; (4) the claim that A4 "never occurs in a shipped fight" is limited to the inspected native, BT and combat-style evidence: `StartMove` is BlueprintCallable and a Blueprint caller is not excluded; (5) "Sprint runs only while Leap is on cooldown" is wrong in two ways: Leap can also be rejected by the ability-system block tag (phase one) or by any `Can Activate Ability?` predicate, and in phase two Sprint can follow any Leap rejection; (6) the graph evidence in E-002-08 and Addendum 3 consists of node inventories exported through `bp_graph.py`/`bp_pins.py` (connection counts only): exact edge-level flow needs the text exports with `LinkedTo` endpoints, which are recovered in E-006 (pending); a notify class name such as `ANS_HitStunImmune` does not by itself prove stagger or posture-break immunity.

Captured 2026-10-25 by Claude. Provenance: fingerprint in `E-001_fingerprint.md` (editor binary matches working-tree source; live cvars `rpg.WakeClip` 0 and `rpg.CloseTelegraph` 0 at capture, i.e. driver warm-up state). Everything below was read from the running editor without saving or compiling any asset.

## Evidence IDs

| ID | What | Raw file | Method | Result |
|---|---|---|---|---|
| E-002-01 | Placed boss and map | bridge `get_level_actors` | `Scripts/mcp_call.py get_level_actors` | 1 actor `BP_ExampleGreatSwordBoss_C_3` label `GreatswordBoss`, level `L_SevarogArena` |
| E-002-02 | Boss info asset (EnemyInfoRef target) | `exports/ExampleGreatSwordBoss_info.t3d` | `probes/p0_export_text.py` (AssetExportTask, text only) | AI pawn class `BP_ExampleGreatSwordBoss_C`, anim `ABP_HumanoidEnemyCharacter_C`, combat style `ExampleGreatSwordBossCombatStyle`, **BehaviorTree `BT_ExampleBoss`**, behavior class `SM_Humanoid_CombatBehavior_C`, default state `Behavior.Nothing`, base health 500 (the encounter raises it to 2000, KI-098), extended attributes health + `BP_PoiseExtendedAttribute` |
| E-002-03 | Runtime behavior tree | `exports/BT_ExampleBoss.t3d`, `exports/BT_ExampleBoss_tree.md` | export + `probes/bt_t3d_tree.py` (offline parser, runtime nodes not editor graph) | tree below |
| E-002-04 | Combat style abilities | `exports/ExampleGreatSwordBossCombatStyle.t3d` | export | 11 boss abilities: HitStun, EnterCombat, ExitCombat, CloseAttack, CloseRare, MidRangeAttack, LeapAttack, SprintAttack, RetaliationAttack, TurnInPlace and `GA_EnemyRagdollDeath` (the live dump lists the ragdoll death ability after TurnInPlace; the player abilities that follow in the dump are not boss grants) |
| E-002-05 | Ability class defaults | `exports/CDO_GA_GS_Boss_*.t3d`, `CDO_GA_Enemy*.t3d` | CDO export | tags, cooldowns, attack data |
| E-002-06 | **Live ability instances in PIE** | `exports/live_boss_abilities_dump_PIE_2026-10-25.txt` | existing `Scripts/Editor/pie_dump_abilities.py` unchanged, `URPGCombatDebug::DumpAbilities`; editor log 05:12:59 UTC (10:42 IST) | resolved montage per ability, below |
| E-002-07 | State machine tunables | `exports/CDO_SM_Humanoid_CombatBehavior.t3d` | CDO export | numbers below |

## Runtime route (U01)

L_SevarogArena -> placed `BP_ExampleGreatSwordBoss_C_3` (EnemyInfo `ExampleGreatSwordBoss`) -> controller `BP_BaseAIController_C_0` (from the live dump: Behavior Manager Component path `BP_BaseAIController_C_0.BehaviorManagerComponent`) -> `BT_ExampleBoss` + blackboard `BB_Base` -> pack ability system component `BP_AdvancedAbilitySystemComponent_C` on the boss (the pack's custom Blueprint ability system, not Epic GAS) with the ten abilities above; `StateManagerComponent` and `BP_CombatComponent_C` are on the pawn. Project C++ components (RPGAttackTracker, Encounter, Phases, Stagger, ...) are attached by `RPGPlayerMovesSubsystem`; they are not part of the pack route (see report architecture section when written).

## Behavior tree decision structure (U02), from E-002-03

Root `Main Selector` (services: `S_CalculateTargetValues` every 0.10 s writing TargetActor / DistanceToTarget / AngleToTarget; `S_UpdateBehavior` every 1.0 s). Children are gated by `D_IsCurrentBehaviorEqual` (abort Both for Dead and Hit, Self for the rest): Dead, Hit, Parried, Toggle Combat, Patrol, Nothing, **Attacking**, Reposition, Retaliate, Defend, Strafing, Healing, Custom, Turning, Follow, ReturnToPost. Under `Behavior.Attacking` (Selector_8):

| Order | Gate | Selection |
|---|---|---|
| 0 | `Behavior.Attacking.Retaliation` | tag `Ability.Melee.RetaliationAttack` |
| 1 | DistanceToTarget < 250 | 25 % `Ability.Melee.CloseRare`, else `Ability.Melee.Close` |
| 2 | DistanceToTarget < 800 | 25 % `Ability.Melee.FarRare`, else `Ability.Melee.Far` |
| 3 | DistanceToTarget < 1000 | 25 % `Ability.Melee.RangedRare`, else `Ability.Melee.Ranged` |
| 4 | DistanceToTarget > 249, abort Self | MoveTo TargetActor, acceptable radius 50, strafe allowed |

State-machine numbers (`SM_Humanoid_CombatBehavior` CDO, E-002-07): AttackingDistance 800, AttackingBehaviorMaxDistance 1000, StartFollowingRange 800, MinFollowingRange 350, StrafingRange 800, chance to attack after attacking 40, while following 50, while strafing 45, after turning 50, after hit 60, after defending 40, AggressionLevel 8, RetaliateDistance 800, MinimumTurningDistance 250, heal state below 50 % health within 800 (no boss ability carries `Ability.Heal`/`Ability.Retaliate`, so those two states have no ability to run: unverified consequence, see unresolved list).

## Live attack inventory (U03), from E-002-04..06

Resolved on the live PIE instances (montage arrays are per instance, empty on the CDO):

| Ability (tags) | Resolved montage(s) | Cooldown | Natural trigger path | Tracked by `RPGAttackTracker` | Notes |
|---|---|---|---|---|---|
| `GA_GS_Boss_CloseAttack` (`Ability.Melee.Close`) | GS_Attack01, 02 (03, 04 follow in the array; native `RPGBossCloseClipSwap` swaps authored clips at run time) | 0 | BT: Attacking, distance < 250, attempted after the 25 % rare roll fails (an attempt order, not a share of successful actions) | yes A1/A1b/A3a/A3b | |
| `GA_GS_Boss_CloseRare` (`Ability.Melee.CloseRare`) | GS_ChargedAttack_Montage | 0 | same node, 25 % | yes A2 | |
| `GA_GS_Boss_MidRangeAttack` (`Ability.Melee.Far`) | **ExampleSwordMob/Mid01_Anim_Montage** | 0 | BT: Attacking, distance < 800, attempted when the 25 % FarRare roll fails or FarRare fails (attempt order, not a share of successful actions) | **NO** | pack mob clip, no native stage, heading lock, branch check or veto |
| `GA_GS_Boss_LeapAttack` (`Ability.Melee.LeapAttack`, **`Ability.Melee.FarRare`**) | GS_LeapAttack_Montage | 15 s | BT FarRare node (25 %); native lock until phase two | yes A6 | shares the FarRare tag with Sprint |
| `GA_GS_Boss_SprintAttack` (`Ability.Melee.SprintAttack`, **`Ability.Melee.FarRare`**) | **GS_SprintAttackFollowUp_Montage** (ability class also has SprintSpeed 800, Timelimit 1.5 s, FollowUpRange 200) | 0 | BT FarRare node (25 %) | **NO** | natural damaging move with no native tracking; which of Leap/Sprint the FarRare node picks is decided inside `T_TryActivateAbilitiesByTags` (graph not yet read) |
| `GA_GS_Boss_RetaliationAttack` (`Ability.Melee.RetaliationAttack`) | **ExampleSwordMob/RetaliationAttack_Montage** | 0 | `Behavior.Attacking.Retaliation` via `Can Enter Retaliation Attack?` (conditions not yet read) | **NO** | pack mob clip |
| `GA_GS_Boss_TurnInPlace`, EnterCombat, ExitCombat, HitStun | non-damaging | | | n/a | |
| A4 low sweep | project clip `AN_Boss01_A4_LowSweep` played by `RPGAttackTracker::PlayClip` | tracker-owned | **no natural trigger**: not in the BT or the style, and the only caller of `StartMove("A4")` is `URPGBossLowSweep::StartForTest` (`RPGBossLowSweep.cpp:25-33`, returns false in Shipping); a repo-wide search of Source (excluding tests) finds no other caller | yes | source-confirmed: A4 never occurs in a natural or shipped fight (prior audit G06) |
| A5 javelin | project clip `AN_Boss01_A5_JavelinThrow` via `PlayClip` | tracker-owned, own cooldown in `URPGBossHealPunish` | native reaction to the player's potion montage: `URPGBossHealPunish` calls `Tracker->StartMove(ThrowMove, false)` (`RPGBossHealPunish.cpp:138`), so it is natural but conditional on the player healing | yes | |
| Ranged / RangedRare nodes | no boss ability has those tags | | BT nodes fail; falls through to MoveTo | n/a | |

**Finding F-1 (source and live-confirmed, high):** three natural, damaging pack abilities (Mid01 mid-range slash, the sprint-attack follow-up, the retaliation attack) run through the pack path with no entry in `RPGAttackTracker::Attacks`, so they get no instance identity, no committed heading, no priority veto, no phase/stagger legality check, no telegraph rate, and they are not in any existing test's move list. They share the `Close`/`Far` BT bands with the tracked moves, so their natural share of boss actions is not small (the Far branch is 75 % of every attack decision in the 250 to 800 cm band). The prior audit flagged this as "must not be silently omitted" (U03); it is now confirmed to be live. Natural frequency is NOT yet measured (see next steps). Classification: source-confirmed and live-resolved; impact on feel not measured.

## Unresolved / next in this evidence set

1. `T_TryActivateAbilitiesByTags` graph: how it picks among several abilities with the same tag (Leap vs Sprint under FarRare) and what it does when the pick is on cooldown.
2. `Can Enter Retaliation Attack?` / `Try Retaliate` conditions (what triggers `Behavior.Attacking.Retaliation`).
3. Natural frequency of each pack move in a real fight (needs a bounded observer during an existing bot fight; labelled bot-driven, not human).
4. Montage notify tracks and effective timing of Mid01, SprintAttackFollowUp and RetaliationAttack (U06).
5. Trace/damage route for those three (U05): does the pack attack data path (`DefaultMeleeAttackData`) apply, and do `RPGTraceGuard` / `RPGDamageResolver` see them.
6. (Resolved in the table above: no native A4 scheduler; Blueprint callers of StartMove not excluded.)

## Addendum 2026-10-25 (same session): graph reads and historical natural-fight evidence

- **E-002-08 FarRare selection order (live graph, `T_TryActivateAbilitiesByTags`, function `Activate Abilities`)**: `Get Abilities By All Tags(Ability Tags)` -> `For Each Loop` -> `Try Activate Ability`, first success wins and returns true (bForceActivation read from the node). The loop order is the ability system's granted-ability order. The style lists LeapAttack before SprintAttack (E-002-04), and `URPGBossPhases` blocks `Ability.Melee.LeapAttack` in the ability system component until phase two (`RPGBossPhases.cpp:125, 197-215`, `bLockLeapUntilPhaseTwo` default true, `RPGBossPhases.h:87`). Source-confirmed consequence, NOT yet runtime-observed in a fresh run: **in phase one every FarRare pick (25 % of the 250 to 800 cm decisions) that survives the loop falls through Leap to the untracked sprint attack**; in phase two Leap is tried first and Sprint only runs while Leap is on its 15 s cooldown.
- **E-002-09 Historical natural-fight observations (mutable saved files, 2026-10-24: Starter 19:35, Strength 03:45, Dex 03:50 (file mtimes); copies with hashes in `exports/historical/`; NOT a fresh build/run, bot-driven)**: `Saved/build_fight_result_Strength.txt` line 16: a bot-controlled Strength fight took 3 hits for 108 health, one of them from untracked `Mid01_Anim_Montage`; the same file line 21 and the Dex file line 21 list `Mid01_Anim_Montage x1` as attack-like and untracked, plus unnamed dynamic montages (`AnimMontage_377`, `AnimMontage_429`, `AnimMontage_65`: dynamic montages from the clip swap or clip players) and `GS_EquipWeapon_Montage` (enter combat). No sprint-attack or retaliation montage appears in these three runs; one run per build is not a frequency estimate. The bot's own notes (`Documentation/M14_FIGHT_NOTES.md:79, 90`) already flag the mid range and sprint montages as untracked and dodged at a guessed time.

## Addendum 2 (same session): notify tracks of the three untracked pack moves and the retaliation trigger

- **E-002-10 Notify tracks (live, existing helper `RPGMontageUtils::DescribeNotifies` through `probes/p0_montage_notifies.py`; raw: `exports/montage_notifies_2026-10-25.txt`; montage-local seconds, play rate 1.0, nothing saved)**:

| Montage | Length | Rotation window (`ANS_SetDesiredRotation`) | Trace window(s) (`ANS_CollisionTrace`) | Other notifies |
|---|---|---|---|---|
| `Mid01_Anim_Montage` (MidRange, untracked) | 2.667 s | 0.127 to 0.615 | 0.637 to 0.884 (one window, 0.247 s) | no `ANS_DisableMovement`, no `AN_EndAnimatingAbility`: the ability ends with the montage, about 1.78 s after the trace closes |
| `GS_SprintAttackFollowUp_Montage` (Sprint, untracked) | 1.867 s | none | 0.037 to 0.230 and 0.364 to 0.551 | `ANS_DisableMovement` 0 to 3.4 s; the strike starts 0.037 s after the follow-up montage begins (the visible run-up belongs to the ability's sprint phase before it, not to this montage) |
| `RetaliationAttack_Montage` (Retaliation, untracked) | 1.267 s | 0 to 0.257 | 0.444 to 0.630 | `ANS_HitStunImmune` for the whole 1.267 s (the move cannot be staggered by a hit reaction), `AnimNotifyState_Trail` 0.446 to 0.636 |
| `GS_Attack01..04`, `GS_ChargedAttack`, `GS_LeapAttack`, `AM_Boss01_A1/A3a/A3b` | in the file | | | tracker rows agree with these notify times (e.g. A3a trace 0.40 to 0.60, A2 second window 1.925 to 2.104, A6 trace 0.754 to 1.175) |

  The two A4/A5 project clips are plain animation sequences: their notifies are not readable from Python (the probe says so; the montage wrappers are what the tracker plays).
- **E-002-11 Retaliation trigger (live graph, `SM_Humanoid_CombatBehavior`, functions `CanEnterRetaliationAttack?` and `TransitionHit`/`Try Retaliate`)**: `Behavior.Attacking.Retaliation` is entered from `TransitionHit` -> `Try Retaliate` when `CanEnterRetaliationAttack?` is true: attributes component and behavior manager valid, a focused combat target is valid, the blackboard `bCombatEnabled` is true, **`Attribute.HitCount` >= its max (3 in the boss info, E-002-02)** and the target distance <= `RetaliateDistance` (800). So the move fires after the boss's pack hit counter reaches 3 while the player is within 8 m. Whether the pack's hit counter ever reaches 3 in this project (poise gate and hyperarmor rules change which hits count as reactions, `GA_BaseHitReaction` is edited) is NOT established: UNVERIFIED, needs a runtime observation of `Attribute.HitCount` in a real fight.

## Addendum 3 (2026-10-25, after the Codex hand-over): raw graph evidence for E-002-08 and the selection predicates

Raw exports (bridge `bp_graph.py`/`bp_pins.py`, read only, files in `exports/`):
- `graph_T_TryActivate_ActivateAbilities_pins.txt` (function `Activate Abilities` of `T_TryActivateAbilitiesByTags`, nodes with pins): `Get Abilities By All Tags` -> `For Each Loop` -> `Try Activate Ability` per element, `LastSuccessfulAbility` set, `Is Valid` / `bForceActivation` branch, returns true on the first success.
- `graph_ASC_GetAbilitiesByAllTags_and_TryActivate.txt`: `Get Abilities by All Tags` iterates `CreatedAbilities` in array order, keeps those whose `AbilityTags` `Has All Tags` of the query (`Add` to `L_Abilities`). `Try Activate Ability`: `Is Valid`, then (unless force) `Does Satisfy Tag Requirements?`, then `Can Activate Ability?` on the ability, then `Cancel Abilities with Any Tags`, `Append to Owned Gameplay Tags`, `Add Blocked Ability Tags`, `Activate Ability`, `Add Activated Ability`, `OnAbilityActivated`. The array order equals the live dump order (E-002-06: Leap listed before Sprint), so under FarRare the Leap is tried first, then Sprint (E-002-08 is now backed by raw graph output; the fall-through reasons beyond the Leap's tag block and cooldown are the predicates below).
- `graph_GA_EnemyMeleeAttack_CanActivate.txt` and `graph_GA_MeleeBase_CanActivate.txt` (`Can Activate Ability?`): `GA_EnemyMeleeAttack` requires a valid focused combat target, combat enabled, this ability not already active, no other animating ability (`Get Animating Ability`), and no active cooldown; `GA_MeleeBase` additionally rejects when the performer has `Status.ActionCommitted`, when the state is `Character.State.Attacking`, when resources are insufficient, or when the combat type is a specific enumerator.
- Consequence for frequency reasoning (source-confirmed, runtime not measured): a rejected Close attempt does not end the decision; the Selector falls through to the next distance band whose gate is also true (distance < 800), so a Close rejection with the player at 129 cm can legitimately end in a Far/Mid attempt. This is a candidate explanation of the single observed `Mid01_Anim_Montage` start at 129 cm (E-004); it is not verified: the reason the Close attempt was rejected at that moment is not recorded.
