# AQ-C06–C10 — attack/lunge overlap probe

## Maintained mode

`Scripts/Editor/pie_camera_engage.py` now accepts `CAM_MODE=attack`. It wakes the boss, holds its behavior tree for deterministic scripted starts, enters player combat, then teleports the player once to 115 cm from the boss. After that initial setup it does not reposition the player; it circles and applies a small distance-correction movement input. `CAM_SPEED` still scales movement.

At the existing 10 Hz camera sample cadence, the probe records player-to-boss distance and counts samples in the requested 80–150 cm band. While the tracker is neutral and the player is inside that band, it calls `RPGAttackTracker.start_move(move_id, True)` using the configured `CAM_ATTACK_MOVES` list (default `A4,A6`). Accepted starts advance to the next move; refusals are logged and retried after a one-second delay. The summary records requested IDs, successful starts, refusals, in-band sample count, and observed in-band distance range. A4 is the tracked low sweep, A6 the tracked phase-two leap; `Close` is also supported when requested. A successful tracker start is not proof that a weapon hit, camera intersection, or option acceptance occurred.

During attack mode, when LockOnFraming is disabled, the probe holds camera control facing away from the boss so the spring arm may pass through the boss and exercise HideBossInside. If LockOnFraming is enabled, the driver leaves control yaw alone for C to frame; B+C behavior still requires a dedicated Lead run. The maintained driver retains `orbit`, `away`, `retreat`, and `fixed` modes and the validated CVar parser. It never writes component editor properties or saves assets.

## Lead run request

Use clean per-route processes. Confirm the tracker component and encounter started, then run attack mode with `CAM_ATTACK_MOVES=A4,A6` (or add `Close` as a separate tested run), first with HideBossInside=0 and then =1, keeping LockOnFraming=0 for the B comparison. Run legacy and selected-data routes. Check `ATTACK_START`, camera samples overlapping the tracked move phases, hide transitions/count/duration, distance-band counts/range, and terminal summary. Retain logs plus video showing the player, boss, and camera framing. If testing B+C, enable both Cvars in a distinct run and record view-to-boss error and look-input/reacquisition separately; it does not replace the off/B comparison.

## Validation boundary

Test-first coverage was extended to reject unsupported/duplicate attack IDs and to require the attack mode, tracker call, awake-boss hold, distance band, and attack summary fields. `python -m unittest Scripts.Editor.test_pie_camera_engage_contract` passes 6/6; `python -m py_compile Scripts/Editor/pie_camera_engage.py Scripts/Editor/test_pie_camera_engage_contract.py` passes. These are offline source checks only. Codex did not invoke Unreal, build, or run PIE; attack acceptance remains Lead-owned.
