# E-009: pack reuse exports (Codex D09_PACK_REUSE_DELTA jobs 1 to 27), Claude, 2026-10-25

Kind: engine export (read-only text export of live editor assets, binary of E-001 plus the DD-1 step 1 DLL; same probe as E-002/E-006, `probes/p0_export_text.py`, sha256 `a48651c1...4c19`, unchanged). No asset saved, compiled or modified. Run from a closed editor through `Scripts/RunEditorScript.ps1`; job file `Saved/p0_jobs.txt` (45 jobs).

Files: 45 `exports/PR2_*.t3d` (asset text and generated-class CDO for jobs 1 to 22 Blueprints, asset text for data assets, state machines, BT and animations 23 to 27). Hashes: `exports/PR2_SHA256.txt` (sha256 `6092c190...26f2`). All 45 jobs returned True; no NOT FOUND.

## Facts read so far (CDO values; graphs not yet analysed)
| Question | Fact | File |
|---|---|---|
| Does `DefaultGrabAttackData` name any paired montage? | No. It holds the damage GE `GE_MeleeDamage_DamageOnly`, `IsUnblockableAttack?=True`, a trail particle and an impact effect only. The montage source of the grab is elsewhere (ability graph or style). | `PR2_DefaultGrabAttackData.t3d` |
| `GA_EnemyGrabAttack` defaults | tag `Ability.Grab.Attack`, `AttackData=DefaultGrabAttackData`, `Random Attack Index?=True`, `ActiveAbilityMontage=None`, no cost, no cooldown | `PR2_CDO_GA_EnemyGrabAttack.t3d` |
| `GA_EnemyDodge` | `DodgeMontage=()` empty (confirms the earlier CDO export), so it cannot play without a bound montage array | `PR2_CDO_GA_EnemyDodge.t3d:7` |
| `GA_AI_BlockGuard` | `BlockingHeldTime=2.0`, melee block distance 350, ranged 900, `ActivationChance=100`, cancels `Ability.Sprint`, owns `Status.Blocking`, no cost, cooldown 0 | `PR2_CDO_GA_AI_BlockGuard.t3d` |
| `GA_EnemyHeal` | `Heal Gameplay Effect=None` (no heal effect configured) | `PR2_CDO_GA_EnemyHeal.t3d:2` |

## Not done (open, stated plainly)
The dependency closure (every montage, sequence, curve, notify, GE and style referenced by jobs 1 to 22 including runtime-set arrays), the graph questions of D09 (guard angle and drain, dodge i-frame and path, grab selection/alignment/release/aborts, parry window and results), and the MotionWarping component query are NOT answered by these files: they need the graph edge parser (`probes/bp_t3d_edges.py`) and a closure script. AG-12's claim that the grab is "authored for unarmed bipedal creatures" is not supported or refuted by the data asset alone.

## Revision 02: closure batch PR3 (AG-12 list, 20 assets, 32 files), 2026-10-25 23:20
Files `exports/PR3_*.t3d`, hashes `exports/PR3_SHA256.txt`; all asset exports True; the `PR3_CDO_*` of the four style/info DATA assets (styles and `ExampleGreatSwordBoss` are `BP_CombatStyle`/`BP_EnemyInfo` instances, not classes) were NOT FOUND by design and their asset text is the evidence.
- The Ember Warden's own style (`PR3_ExampleGreatSwordBossCombatStyle.t3d`) grants: `GA_GS_Boss_HitStun`, `_EnterCombat`, `_ExitCombat`, `_CloseAttack`, `_CloseRare`, `_MidRangeAttack`, `_LeapAttack`, `_SprintAttack`, `_RetaliationAttack`, `GA_GS_Boss_TurnInPlace` and `GA_EnemyRagdollDeath` (names matched in the file; the style does NOT grant guard, dodge, grab or heal abilities).
- `GA_GS_Boss_TurnInPlace` (`PR3_CDO_GA_GS_Boss_TurnInPlace.t3d:4-7`) has all four turn montages (left/right 90, left/right 180) BOUND and tag `Ability.TurnInPlace`; so a populated turn-in-place already exists on this boss, unlike the generic `GA_EnemyTurnInPlace` (all slots None, `PR2_CDO_GA_EnemyTurnInPlace`). Whether `BT_ExampleBoss` ever activates it: see the grep counts in C-129.
- `ExampleGreatSwordBoss` (`BP_EnemyInfo`): health 500, `Attribute.Attack` 35, behaviour tree `BT_ExampleBoss`, anim class `ABP_HumanoidEnemyCharacter`, name "Greystone Knight" (the pack's label, unchanged), extended attributes health and the project's poise attribute.
