# S115 — arena leash inside/outside control

## Authored baseline

The MOV005 fixture starts the target at `(0,0)` in the XY plane; the boss is spawned at `(500,0)`. `ArenaOrigin` is captured from the target's start location unless an explicit authored center is enabled (`RPGFrameworkBossCharacter.cpp:66`, `.h:79`). Profile `DA_Sevarog_ArenaLeash_MOV005` sets `ArenaRadiusCm=250` and `bArenaLeash=true`, with readback in `B_MOV005/content_run1/editor_raw.log:1373` and the fixture reference in `:1409`. The boundary is strict: distance `>250` is `OffArena` (`RPGFrameworkBossCharacter.cpp:115`); exactly 250 remains inside.

## Outside-radius pass

Keep the target's baseline at `(0,0)`, start a normal card, then move it to `(0,500)` (distance 500 from the captured center). The expected ordered signals are:

1. `target_shift_injected ... dy=500`.
2. `arena_leash state=Start targetDistanceCm=500 radiusCm=250 centerX=0 centerY=0`.
3. If a card is active: its `event ... kind=Aborted`, followed by `cleanup reason=ArenaLeash modelIdle=1 ownedMontageStopped=1`.
4. `arena_leash state=AtCenter distanceCm<=AcceptanceCm+30` after the boss reaches the origin tolerance (`RPGFrameworkBossCharacter.cpp:205–225`).

The retained `B_MOV005/pie_leash3/editor_raw.log:1611–1615` shows this ordering and the values above: the target shift interrupts active instance 1 at local time 0.283333, cleanup follows, and the boss reaches 32.9333 cm from center.

## Inside-radius resume and negative control

From `(0,500)`, move the target to `(0,100)` (distance 100 from the same origin). Expect `target_shift_injected ... dy=-400`, then `arena_leash state=Resume bossDistanceToCenterCm=... atCenter=1`; the next walk-to-band must pass the ordinary arrival band, and a later `playback_start` proves neutral behavior resumed. The retained trace has Resume at `B_MOV005/pie_leash3/editor_raw.log:1616–1617`, a subsequent `walk start` at `:1619` (range 122.817, band 110–140), and playback instance 2 at `:1642`.

For the no-leash control, use the same profile and target baseline but keep the target at `(0,0)` or shift it to `(0,249)`; it must emit no `arena_leash` state and must continue ordinary behavior. Include the exact boundary `(0,250)` as an inside check and `(0,251)` as the smallest outside check if the proof is intended to verify the comparison itself. The existing positive run proves an outside-to-inside transition, but does not provide a separate inside-only control or test the 250 cm boundary.

## Evidence boundary

The retained run demonstrates active-move abort, return to center, re-entry, band arrival, and resumed playback. It does not prove exact-boundary behavior or an inside-only negative control. `command.json` invokes the shared `F4/drive_pie.py`; that driver reads mutable `current_map.txt` and `current_shift.txt`, so preserve those inputs in a future run manifest if a self-contained replay is needed. No new runtime run was performed for this checklist.

## Setup
## Control
## PASS
## FAIL
