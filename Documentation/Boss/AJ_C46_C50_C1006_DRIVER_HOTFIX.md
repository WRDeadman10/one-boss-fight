# AJ-C46–C50 — C-1006 rejected-driver hotfix

Date: 2026-11-07  
Authority: Claude C-1006 and C-1007; Codex handoff X-1418.  
Status: Driver correction complete locally; Lead runtime rerun pending.

## C-1006 findings and corrections

C-1006 rejected the prior `pie_er_guard_counter.py` as non-runnable. It identified an unexpected indentation before `set_key(pc, "R", True)` and a second failure when the Lead's local syntax repair attempted to inject keyboard R through `RPGInputTestUtils.set_key_down`.

The driver now removes the R-key path and enters combat using the working control-latency probe's `Ability.EnterCombat` gameplay tag activation. It reuses the same 900 cm player placement and 180-degree control rotation; `RPGCombatDebug.debug_refill_player()` remains called each live tick. The boss remains unheld so its AI can generate guardable attacks. L1/R2 remain gamepad inputs and the existing cleanup releases any held keys.

When `ER_GC_ASSIGN=1` is set before the Lead run, the driver loads `/Game/OneBossFight/Player/Animations/AM_ER_Attack_GuardCounter` and transiently assigns it to `RPGDodgeTiming.guard_counter_montage` in PIE. A missing asset or failed assignment ends the probe with an explicit error. The driver contains no save operation; Codex did not execute Unreal or verify the reflected runtime property on a live object.

## Validation and evidence boundary

- `python -c "import ast; ast.parse(open('Scripts/Editor/pie_er_guard_counter.py', encoding='utf-8').read())"` — passed.
- Scoped `git diff --check -- Scripts/Editor/pie_er_guard_counter.py` — passed.
- Static review confirms the old keyboard-R call is gone, combat entry uses `Try Activate Abilities By Tag(Ability.EnterCombat)`, refill remains per-tick, and the optional assignment is behind `ER_GC_ASSIGN=1`.
- No Unreal, PIE, build, tests, asset edit, save, commit, or push was performed by Codex.

X-1418 asks Claude to rerun both routes. A missing successful-guard source log on legacy must be reported as the X-1415 hook-reachability finding; it is not a passing counter test. Runtime contact, acceptance log, hit record/HP delta, and any transient-assignment behavior remain Lead evidence gates.
