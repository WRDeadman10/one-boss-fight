# Codex Brief 01: the 30 encounter soak runner (G4-4)

From Claude (technical lead) via the owner. You write files; you do NOT run the editor. Claude runs and debugs your draft in the editor and validates your report by evidence, then writes Brief 02.

## 1. Context (read first, in this order)
`AGENTS.md` (rules, same as `CLAUDE.md`), `Documentation/PROJECT_STATE.md` (state, gotchas, the "Team protocol" section), `Documentation/TASKS.md` row G4-4, `Documentation/TEST_PLAN.md` (what existing drivers prove), `Documentation/KNOWN_ISSUES.md` (KI-081, KI-083, KI-085), `Documentation/TEAM_MAILBOX.md` message C-1 (your task in short; you may answer there, append only).
Project: UE 5.5.4 soulslike boss duel, own C++ in `Source/OneBossFight` on a Blueprint-only pack. Regression drivers are Python files in `Scripts/Editor` that run inside the open editor (`Scripts/run_in_editor.py`), generator style (`yield seconds`), log prefix and a final `RESULT n/m passed` line.

## 2. Task
Create ONE driver, `Scripts/Editor/pie_soak.py`, and ONE doc, `Documentation/SOAK_NOTES.md`. Nothing else. Do not edit, rename or delete any existing file (the working tree has about 240 uncommitted changes that must survive).

The driver runs 30 boss encounters in a row, deterministically (no clever bot: scripted wake, scripted openings, scripted resets or kills), and proves that nothing gets stuck or illegal over many repetitions: double actions, illegal cancels, stuck states, stale actors, damage after an interrupt.

Required behaviour:
1. 30 encounters, each with an id and a scenario. Cycle through at least these scenarios (you choose the order and mix, document it): (a) natural fight for about 20 s with the player kept alive (refill) and standing in range, then reset; (b) forced stance break (`force_break_for_test`) then reset in the kneel; (c) health set to the phase two fraction so the roar plays, reset during the roar; (d) player killed (`debug_set_player_health(0.0)`), wait for the real respawn and the automatic encounter reset; (e) boss killed (`debug_kill_boss`): the pack destroys the dead boss about 4.4 s later, so the next encounter needs a NEW PIE (see `Scripts/Editor/pie_boss_death_states.py`: it stops PIE, waits until `get_game_world()` is None, starts PIE again, inside one driver). Decide how many encounters share one PIE and why; write it in the notes.
2. Per encounter log one line `[Soak] ENCOUNTER n scenario ...` with: generation (`RPGBossEncounter.get_generation`), reset count, phase (phase two yes/no), boss health and posture at the end, stagger count, riposte count, the tracker counters (`get_illegal_start_count`, `get_double_launch_count`, `get_attack_instance`, `get_commit_count`, `get_interrupted_count`) as deltas for this encounter, the reset outcome (boss home position, dormant, health back to max, not staggered, no montage playing, player health max), and on failure the failure context (what was expected, what was read, the last 5 boss moves).
3. Checks (each counted in RESULT whether it passes or not; a skipped check is a failed check, so the total is fixed and known): per encounter: the encounter reached the scenario's goal; after the reset the boss is in its start state; no illegal start and no double launch happened; the generation went up by exactly the number of resets; no stale actor (count the boss actors and the pack's projectile and wave actors in the world, expected 1 boss and 0 leftovers after a reset: find them by class name; read how `pie_a5_heal_punish.py` and `pie_leap_wave.py` find javelins and waves); no damage to the player after the boss's attack was interrupted by the reset (health must not drop in the 1.5 s after a reset). Plus end checks: all 30 ran, no tick error, no hang (watchdog). Expected RESULT total: you compute and document it.
4. Watchdogs: a heartbeat line every 15 s, a limit per encounter (60 s) and a total limit (set it from the notes; the run should take roughly 40 to 60 minutes), no pawn for 40 s = fail and finish. At the end clear any state you set.
5. Document in `SOAK_NOTES.md`: scenario table, why this order, every API name you used with the header and line where you found it, the expected check count, what could NOT be verified, the three places you expect it to misbehave first, and the `RunDrivers.ps1` row to add (`@{ N = 'pie_soak'; K = 'R'; Min = <n>; T = <seconds> }`; Claude adds it).

## 3. Rules and traps (these cost time before)
- Python names: UE Python exposes a C++ UFUNCTION `FooBarBaz` as `foo_bar_baz`. A function that is not a UFUNCTION does NOT exist in Python. READ THE HEADER before you use a name: `Source/OneBossFight/Player/RPGAttackTracker.h`, `RPGBossStagger.h`, `RPGBossPhases.h`, `RPGBossEncounter.h`, `RPGBossPosture.h`, `RPGCombatDebug.h`. `get_world_scale3d` and `get_relative_location` do NOT exist (`get_world_scale()` and `get_editor_property("relative_location")` do). Reading a property with `get_editor_property` is fine; NEVER `set_editor_property` on a component in PIE (KI-083): use UFUNCTION test hooks (`hold_for_test`, `reset_for_test`, `wake`, `set_cooldown_for_test`, ...).
- The first PIE after an editor start reads health 0 for the first frames (KI-081): start scenario logic only after the same 9 s wait the other drivers use. The dead boss is destroyed by the pack about 4.4 s after its death: one boss death per PIE. A boss that disappears before a kill is a failed setup, after a kill it is the expected end.
- Heal the player in scenarios that must not end by the player's death (`debug_refill_player`). The boss is held with `hold_for_test(True)` only where the scenario says so; the natural fight must not be held.
- Do not use the balance bot (`pie_build_fight.py`); this is a different tool.
- No commit, no push, no git command that changes the working tree, no editor, no build, no PIE. You may syntax-check: `python -I -c "import ast;ast.parse(open(path,encoding='utf-8').read())"`.

## 4. Acceptance criteria (Claude will check these)
1. Both files exist, the driver passes the syntax check, and no existing file changed (Claude compares the file list).
2. Every Python name in the driver exists in a header as a UFUNCTION with the right snake_case spelling (Claude greps each one).
3. The check count is fixed and equals the number in the notes on every path (a scenario that cannot run still records its checks as failed).
4. No `set_editor_property` on a component, no unguarded `yield` inside a nested function, a heartbeat, watchdogs, and a RESULT line on every exit path.
5. The notes list what could not be verified; nothing claims a run that did not happen.

## 5. Your report
Write `Documentation/Codex/REPORT_01.md` with: files written, the scenario table, the expected check count, the list of every API name with header and line, what you could not verify, and the three most likely failure points. Tell the owner "Report 01 is ready". Claude then runs the driver in the editor, fixes what the run shows, validates the report against the evidence and writes `BRIEF_02.md`.
