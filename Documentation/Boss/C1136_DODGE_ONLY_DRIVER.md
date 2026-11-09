# C-1136 dodge-only driver

Date: 2026-11-09  
Scope: test-first offline driver mode for Lead runtime measurement. No gameplay Source change, Unreal/Editor/build/PIE, or asset edit by Codex.

## Driver behavior

`FIGHT_DODGE_ONLY=1` is opt-in and mutually exclusive with the parry and no-parry control modes. It starts at 180 cm; if a tick measures separation above 200 cm it repositions to 195 cm before scheduling/pressing. This prevents an out-of-range scheduled dodge from silently counting as a meaningful test. The mode returns before the normal attack/parry cycle.

Targets use C-1132's observed hit positions: tracked A1b .190, A3b .152, A1 .351, A3a .484 and A2 1.974 seconds; montage-name targets Mid01 .700 and SprintAttackFollowUp alternates .070/.456 by playback occurrence. Each target press point is contact minus .15 seconds, clamped to montage start when the subtraction is negative. The Sprint occurrence is a timing assignment because its two witnessed contacts differ; it does not mean both contacts are dodged in one playback.

The driver logs `DODGE_TARGET_SCHEDULED`, `DODGE_PRESS`, `DODGE_ATTEMPT` at the first sampled montage position at/after contact with read-only `Status.Invulnerable` state, and a linked `PLAYER_HIT`/`DODGE_RESULT` if the HP-drop sample follows. Unknown tag reads remain `UNKNOWN`. Runtime success is intentionally not claimed by an offline contract.

## Verification and handoff

- `python -m unittest Scripts.Editor.test_pie_full_fight_offline -q`: 39/39 passed, including montage contact/lead, tag read-only behavior, following-hit linkage and the 200 cm range clamp contract.
- `python -m py_compile Scripts/Editor/pie_full_fight.py Scripts/Editor/test_pie_full_fight_offline.py`: passed.
- Scoped `git diff --check` for the driver and tests: passed (Git reports the repository's LF-to-CRLF normalization warning for the test file).
- Lead must run this after the current parry-only run on the same build, inspect contact/tag/HP rows, and distinguish `false`, `true`, and `UNKNOWN`. No i-frame result is yet known.
