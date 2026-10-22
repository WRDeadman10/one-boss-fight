# Death clip notes (G2-9, A-12)

Written by the death clip agent, 2026-10-22. Status: `RPGBossDeath.h/.cpp` and `pie_boss_death.py` are written, NOT compiled, NOT attached, NOT run. Nothing existing was edited.

## What is built
`URPGBossDeath` (`Source/OneBossFight/Player/RPGBossDeath.h/.cpp`), a component on the pack boss, plays Antigravity's `AN_Boss01_DeathLegend` (3.5 s, 30 fps: on the knees by 2.5 s, the same slumped pose to 3.5 s) when the boss dies. The pack kills the boss with `GA_EnemyRagdollDeath_C` (tag `Ability.Dead`: ragdoll, `PhysicsVelocitySpeed` 2000, `Death Task` `BP_EnemyDeathTask_C`) and destroys the actor a few seconds later (KI-083). Two designs, one enum `ERPGBossDeathMode` (property `DeathMode`, default `PackMontage`):

| Mode | What the component does | What it never does |
|---|---|---|
| `PackMontage` | One frame after BeginPlay, after every encounter reset (`URPGBossEncounter::GetResetCount` changes) and every `PackPollSeconds` (1 s): finds the live `GA_EnemyRagdollDeath_C` (`FindAbilityByClassName`) and sets its `DeathMontages` to `[AM_Boss01_DeathLegend]` by reflection (`FScriptArrayHelper`; elements may be montage objects or the pack's `F_AbilityMontage` structs, see below), only on this instance, idempotent, logged. Optional `bGuardPackDeath`: also freezes the montage at 3.0 s and keeps the ragdoll off. | Touch a pack asset, the ability's class defaults, or the ability itself. |
| `OwnClip` | First frame with `Attribute.Health` <= 0: plays the clip through `RPGBossClips::Play(Character, Clip, 0.1, 0)`, pauses the montage at `HoldAtSeconds` (3.0) so the kneeling pose stays, and every tick while dead takes the mesh out of physics (`SetAllBodiesSimulatePhysics(false)` + `SetSimulatePhysics(false)`) and puts it back on the capsule (relative transform remembered while alive). Restarts the clip (at most 8 times) when something stops the montage. Preloaded on the first tick, so the death frame never waits for the disk. | Delay, cancel or call the pack's death ability, touch the health attribute, or do anything after `EndPlay` (the pack destroying the boss). |

Both: state `alive` / `dying` (until `DyingSeconds` 2.5 s) / `dead`, counters, test hooks (`get_death_state_name()`, `get_death_mode_name()`, `get_death_count()`, `get_clip_play_count()`, `get_clip_restart_count()`, `get_pose_hold_count()`, `get_physics_off_count()`, `get_pack_set_count()`, `get_last_pack_result()`, `is_pose_held()`, `get_death_age()`, `set_death_mode_for_test("own"|"pack")`, `set_guard_pack_death_for_test(bool)`, `apply_pack_montage_now()`). The legend pass and the HUD victory poll health themselves and are not touched (Freeze 18.2: death first).

## Found while reading: the probe's montage mode will probably fail
`pie_death_probe.py` mode `montage` does `ab.set_editor_property("DeathMontages", [montage])`. `GA_Sev_Death` was made as a copy of the pack's `GA_EnemyDeath` (the non-ragdoll death; `GA_EnemyRagdollDeath_C` carries the same `DeathMontages` and `Random Montage Index?` variables, probably as its child: not verified), and `sevarog_pack_05b_death_style.py` / `fix_sev_montage_refs.py` set that variable with `cdo.set_editor_property("DeathMontages", [ability_montage(template, death)])` where `template` is an **`F_AbilityMontage` struct** borrowed from `GA_GS_Boss_EnterCombat_C.Enter Combat Montage` ("The pack's death ability has no montage entry to copy"). So the array most likely holds structs (fields `AnimMontage_5_<guid>`, `PlayRate_4_<guid>` 1.0, `EndTimeMultiplier_25_<guid>` 0.8), not montage objects. A plain montage in the list is rejected by Python. Patch for the probe (do not edit the probe from here; the owner or the main session does):
```python
import re
enter = ability(boss, "GA_GS_Boss_EnterCombat_C")
tpl = enter.get_editor_property("Enter Combat Montage")           # an F_AbilityMontage
text = re.sub(r'AnimMontage_5_[0-9A-F]+="[^"]*"', lambda m: 'AnimMontage_5_2620D50C4D110CA156B1A28F49A30836="/Script/Engine.AnimMontage\'%s\'"' % m_asset.get_path_name(), tpl.export_text())
tpl.import_text(text)
ab.set_editor_property("DeathMontages", [tpl])                      # m_asset = the loaded AM_Boss01_DeathLegend
```
The C++ does not depend on it: it reads the element type from the property (`FObjectPropertyBase` inner = montage objects; `FStructProperty` inner = finds the field whose name starts with `AnimMontage`, builds the element from the struct's own defaults, and with `PackEndTimeMultiplier` > 0 sets `EndTimeMultiplier`). Anything else is reported in `get_last_pack_result()` and as one warning after 5 looks.

## What the probes must show (`Saved/death_probe_mode.txt`: `plain`, `montage`, after `make_death_montage.py`)
| Q | Plain run | Montage run (with the struct patch) |
|---|---|---|
| Q1 does the boss ragdoll (mesh simulating) and when | expected from t=0 | does it still, and from when (together with the montage, after it, never) |
| Q2 which montage plays and where | none | `AM_Boss01_DeathLegend` (anim name `AN_Boss01_DeathLegend`) from t about 0, positions 0 to 3.5 |
| Q3 does the pelvis go down to about 44 cm above the floor and stay | no (ragdoll) | yes (kneel), and does it pop back up at the montage end (it blends out) |
| Q4 when is the boss destroyed (T_d) and does anything change on the way (hidden, collision) | T_d | T_d: after 3.5 s? before 2.6 s means the collapse is cut and neither mode can fix it (the pack's timer) |
| Q5 does the ability end or the boss get destroyed only when the montage ends | no montage | if yes, `bGuardPackDeath` (pausing the montage) would keep the boss for ever |

## Decision table
Attach (the owner adds `#include "Player/RPGBossDeath.h"` and this block next to the other boss components in `RPGPlayerMovesSubsystem.cpp`; `Attach` is a no-op when the boss already has one):
```cpp
	if (IsPackBoss(Pawn))
	{
		URPGBossDeath::Attach(Pawn, ERPGBossDeathMode::PackMontage); // or ERPGBossDeathMode::OwnClip: the death clip (G2-9, A-12)
	}
```
| Montage run shows | Mode | Also |
|---|---|---|
| Montage plays, mesh never simulates, boss lives >= 3.5 s, pelvis down | `PackMontage` | Done. If the pose pops up at the montage end before T_d: set `enable_auto_blend_out` False on the montage (as `AM_SevPack_Death`; the montage script is the owner's) or, only when Q5 is "no", `bGuardPackDeath` |
| Montage plays and the ragdoll runs with it or after it | `OwnClip` | Nothing else |
| Montage reported playing but the pelvis never goes down | `OwnClip` | Probably a slot mismatch: the factory montage is in `DefaultSlot`, the boss's slot is read from `GS_Attack01_Montage` (`RPGBossClips::SlotName`); `unreal.RPGMontageUtils.get_montage_slot` tells, `set_montage_slot` fixes the montage |
| No montage plays (array rejected, ability ignores it) | `OwnClip` | Read `get_last_pack_result()` first |
| T_d < 2.6 s in both runs | either | The full clip cannot be shown: the pack destroys the body first. Owner decides (not ours to delay the pack's flow, Freeze 18.2) |
| Only the plain run is available | `OwnClip` | It does not depend on the pack's array; its risks are below |

## Risks
- **Dynamic montage on a dying boss.** The clip is a dynamic montage in the boss's slot. If the pack's death flow stops all montages, or the AnimBP is replaced or paused (`bPauseAnims`, anim mode changed by the ragdoll), the pose is lost: OwnClip restarts the clip up to `MaxClipRestarts` times and logs it (`get_clip_restart_count()` above 0 in the test = the pack fights it); a paused or replaced AnimBP is not recoverable from here (the test's pelvis check shows a standing boss).
- **Pack destroys the actor.** Dead boss gone after T_d; `EndPlay` sets `bEnding` so nothing touches the mesh, physics or montage then. The test ends with the checks made so far when the boss disappears.
- **Ragdoll fights the pose (OwnClip).** The ragdoll starts in the death frame; the sim is switched off in the first tick that sees it. If the pack's event runs after our tick in that frame, one physics step runs with the throw velocity (a few cm, at most about 33 cm at 60 FPS) before the guard: the mesh is put back at its place on the capsule (relative transform kept while alive), so the jump lasts one frame. The pack's camera boom hangs on the mesh (DECISIONS, camera rig): one frame of camera jolt is possible. If the pack's `Death Task` waits for the ragdoll to settle or sleep, a mesh that never simulates may end that wait at once (the boss is destroyed earlier): Q4 shows it.
- **`bGuardPackDeath` can keep the boss for ever** if the pack's ability waits for the montage to complete (the montage is paused, never completes). Off by default; use only after Q5.
- **Montage defaults.** `make_death_montage.py` leaves auto blend out on: after 3.5 s the montage blends out to the AnimBP's pose (standing) when the pack keeps the boss longer than that.
- **Pack variable names.** `GA_EnemyRagdollDeath_C` and `DeathMontages` are exported names (UPROPERTY `PackDeathAbilityClassName`, `PackDeathMontagesName`); a pack update that renames them degrades to "the pack plays its own death" with a warning in the log (`LogRPGBossDeath`).

## Test plan
1. Close the editor, build; add the attach block; start the editor with `-nosound`; run `pie_debug_overlay.py` once, then `pie_boss_death.py` (log `[BossDeath]`, ends `RESULT n/m passed`; D1 to D9, see its header). The mode is the component default; `Saved/boss_death_mode.txt` (`own`, `pack`, `pack_guard`) switches it through the test hooks without a rebuild, one run per PIE (the dead boss is destroyed).
2. Expected for the chosen mode: the clip plays (D3), the pelvis kneels (D5) and never leaves 20 cm to the standing height in the first 3 s (D6), the mesh does not simulate while the clip plays (D7), the pose stays after 3.2 s (D8), the counters match the mode (D9). A boss destroyed before 2.6 s fails D4 on purpose (it is the information, see the table).
3. Then watch it once by eye (the camera, the sword in the hand, the kneel) and run `pie_riposte_lethal.py` and `pie_victory_lock.py` again: the victory fires once and the player's input lock is unchanged (the death component does not touch either).
4. Update `TASKS.md` (G2-9 / A-12), `DECISIONS.md` (the chosen mode and why), `KNOWN_ISSUES.md` (T_d and any pop or fight seen), `TEST_PLAN.md` (the new driver).

## Probe results and decision (2026-10-22, run by the session owner)
- Plain run (`pie_death_probe.py`, no change): the pack's `GA_EnemyRagdollDeath_C` puts the mesh into physics at once (simulating from 0.1 s, the pelvis drops from 136 to 38 cm by 1.4 s and lies at about 25 cm) and the pack destroys the boss **4.35 s** after the death.
- Montage run: Python cannot set `DeathMontages` on the live ability ("cannot be edited on instances": the property is EditDefaultsOnly). The C++ `PackMontage` mode wrote it by reflection (an `F_AbilityMontage` array entry, log "DeathMontages of GA_EnemyRagdollDeath_C set to [AM_Boss01_DeathLegend] (F_AbilityMontage)"), and the pack still ragdolled with no montage: the ragdoll ability ignores the array (the montage variant of the death ability is `GA_EnemyDeath`, which this boss does not use). **Decision: `OwnClip`.** `PackMontage` stays in the component as an unused mode.
- `AM_Boss01_DeathLegend` (made by `make_death_montage.py`) carries the boss's slot `FullBody` (read from `GS_Attack01_Montage` with `RPGMontageUtils.get_montage_slot`) and auto blend out off; the own-clip mode plays the AnimSequence through `RPGBossClips`, the montage asset is only needed by the unused `PackMontage` mode.
- OwnClip (`pie_boss_death.py` 10/10): the clip plays from 0.24 s after the death, the mesh is taken out of physics at once (the pack's ragdoll switches it on in the same frame), the pelvis goes from 146 to 74 cm (the clip's kneel, 47.7 cm x the mesh scale 1.5 + the floor) and stays, the pose is frozen at 3.0 s, the pack destroys the boss at 4.38 s (the held pose is on screen for about 1.4 s).
- Found by the first runs: a health of 0 in the first frames of a PIE (KI-081) counted as a death and started the clip on a living boss; fixed: a death counts only after the boss was seen alive.
- Cosmetic: the clip's standing pose is 17 cm higher at the pelvis than the pack's idle pose (146 against 129 cm), so the boss rises a little as the collapse starts (blend in 0.1 s); not fixable in code without a different clip.
