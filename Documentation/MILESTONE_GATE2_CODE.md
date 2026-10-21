# Milestone: Gate 2 code completion

Started 2026-10-20. Owner of every row: Claude (C). This file is the resume point: if a session ends (limit, crash), the next session reads this file first and continues at the first row whose status is not Done. Nothing here depends on chat memory.

## Resume protocol (read this after any interruption)
1. Read this file, then `TASKS.md` (Done list on top) and `git status --short` to see which files changed.
2. A row marked **Doing** may be half done: read its spec in `Documentation/milestones/`, look at `git diff` of the files listed in its row, finish or revert that row only, then mark it.
3. Never leave the editor in a state that blocks the next session: end PIE (`Scripts/Editor/pie_stop.py`), keep the project built (`Scripts/Rebuild.ps1 -Tests` ends with the editor relaunched).
4. Sub-agent rules of this milestone: agents are used only for work that can be repeated safely: read-only research, design specs written to one named file under `Documentation/milestones/` (each spec ends with `STATUS: COMPLETE`; an agent that finds a complete spec returns it instead of redoing the work), and read-only code review. **No agent edits `Source/`, `Content/`, `Config/` or runs the editor, a build or a PIE.** Implementation, builds, PIE runs and doc updates are done by Claude in the main thread, one row at a time, so an interruption can never leave two half-finished edits behind.
5. After each row: update this table, the Done list in `TASKS.md`, `TEST_PLAN.md`, and run the regression drivers listed at the bottom.

## Rows
| Row | Task (TASKS id) | Spec | Driver | Done when | Status |
|---|---|---|---|---|---|
| M0 | Design specs for M1 to M4, each reviewed by three lenses | `milestones/SPEC_M1_trace.md` .. `SPEC_M4_transition.md` | - | four specs end with `STATUS: COMPLETE` and `REVIEWED` | Doing (workflow `gate2-code-design`, run wf_22ddb5e9-320, started 2026-10-20; if the session ended, rerun it: finished specs are skipped) |
| M1 | Weapon trace review (G1-4; Freeze 13, tests H01 to H07, H11) | `SPEC_M1_trace.md` | `pie_trace_audit.py` | swept trace proven not to tunnel, one damage event per swing, trace ends on interruption, stagger, phase change, death, reset; debug line separates "trace overlap" from "damage accepted" | Todo |
| M2 | Damage path and i-frames (G1-5; Freeze 14, 32.1, tests D12 to D15, H08) | `SPEC_M2_damage.md` | `pie_damage_path.py` | invulnerability decided where damage resolves, i-frame start/end measured in montage seconds at 30, 60 and 120 fps, cleared on interrupt, death and reset | Todo |
| M3 | Legend pass (G2-14; Freeze 289, 247): camera shake on the slam and the roar, hit stop on the riposte, slow motion on the kill, music phase swap | `SPEC_M3_legend.md` | `pie_legend.py` | each effect fires once per event, time dilation is always restored (reset, death, PIE end), Phase 2 track starts at phase two, one frame capture per effect looked at | Todo |
| M4 | A stance break that starts during a phase transition (G2-6; Freeze 17, 21) and phase-transition queue rules (G2-8) | `SPEC_M4_transition.md` | `pie_transition_rules.py` | the transition wins, the break is dropped or queued as the Freeze says, no stuck state | Todo |
| M5 | One command that runs all PIE drivers and prints a table (G2-16 groundwork) | - | `Scripts/RunDrivers.ps1` | prints PASS/FAIL per driver with counts; used as the regression gate after every row | Built 2026-10-20 (parses); first run pending |

## Regression drivers (run after each row; all must stay green)
`pie_a4_low_sweep.py` 14, `pie_a5_heal_punish.py` 31, `pie_player_death_reset.py` 25, `pie_close_attacks.py` 43, `pie_leap_wave.py` 17, `pie_attack_rules.py` 13, `pie_phase_reset.py` 14, `pie_riposte.py`, `pie_boss_hud.py` 29, `pie_victory_lock.py` 9, plus the 6 automation tests (`Scripts/Rebuild.ps1 -Tests`).

## Workflow state (update when it changes)
- Workflow `gate2-code-design`, run id wf_22ddb5e9-320, script `C:/Users/winss/.claude/projects/C--Users-winss-Documents-Unreal-Projects-OneBossFight/a3ffd588-64a8-415a-91f0-f37df864c384/workflows/scripts/gate2-code-design-wf_22ddb5e9-320.js`. If a new session finds specs ending `STATUS: DRAFT` or without `REVIEWED`, rerun it with `Workflow({scriptPath})` (no resume id needed across sessions): every agent first reads its spec file and continues from it. A spec that ends `STATUS: COMPLETE` is usable as input even before `REVIEWED`.
- Lesson (2026-10-21): the first version told designers to write the spec once at the end, so three of four agents held 25 minutes of research only in memory. Agents now checkpoint a `STATUS: DRAFT` file every 10 tool calls.
- Spec status 2026-10-21 00:21: M4 COMPLETE (review running), M2 COMPLETE, M1 and M3 designers still working.
