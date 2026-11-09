# C-1140 dodge i-frame rise timing and target filter

Date: 2026-11-09
Scope: driver-only, read-only telemetry and offline contracts. No Source/gameplay behavior, Unreal/Editor/build/PIE, or asset changes by Codex.

## Changes

- `FIGHT_DODGE_TARGET` accepts `all` (default) or `Mid01`; targeted mode requires `FIGHT_DODGE_ONLY=1`.
- `FIGHT_DODGE_TARGET=Mid01` waits for `Mid01_Anim_Montage` and `GS_SprintAttackFollowUp_Montage`, ignores other montages, and resolves timing by montage name rather than tracker move.
- Each pending dodge samples `Status.Invulnerable` on each driver tick. A known false-to-true transition emits `DODGE_IFRAME_TAG_RISE` with observed seconds since press. An unknown-to-true transition is separately labeled `DODGE_IFRAME_TAG_FIRST_SEEN`; it is not misreported as a measured rise. `DODGE_RESULT` includes press tag state and measured rise delay (or UNKNOWN).
- All tag reads use the existing read-only `HasMatchingGameplayTag` probe. Contact tag sampling uses the same per-tick observation, avoiding a second query at contact.

## Verification and limits

- `python -m unittest Scripts.Editor.test_pie_full_fight_offline -q`: 41/41 passed, including tag-rise timing and Mid01/Sprint filtering.
- `python -m py_compile Scripts/Editor/pie_full_fight.py Scripts/Editor/test_pie_full_fight_offline.py`: passed.
- `git diff --check` passes for the driver, tests and TEST_PLAN. TASKS.md contains unrelated pre-existing whitespace errors in its already-dirty whole-file diff, so the whole-file check is not clean; the new C-1140 entry itself has no trailing whitespace.
- No Lead runtime run was performed by Codex. The telemetry reports the first driver-tick observation of the tag edge; it does not claim sub-tick animation timing or prove a causal i-frame outcome. Lead should run `FIGHT_DODGE_ONLY=1,FIGHT_DODGE_TARGET=Mid01` to gather Mid01/Sprint samples.
