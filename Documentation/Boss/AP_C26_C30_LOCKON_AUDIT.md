# Queue AP-C26–C30 — LockOnFraming edge and isolation audit

**State:** offline edge contracts and source audit complete; Lead build/PIE pending.

## Scope boundary

C-1051 option C's owner wording is “a lock-on/orbit framing that keeps the boss in front.” The implementation uses only the player-owned spring arm and the live pack boss. It recognizes the pack boss through `URPGPlayerMovesSubsystem::IsPackBoss`, casts to `ACharacter` before reading its position, and resolves the actor each enabled tick. No target or nonlocal controller restores the prior spring-arm mode. A target swap clears the manual grace and re-baselines the observed controller input without discarding the original arm setting.

The camera rig reads controller rotation as manual camera input but does not write controller rotation, player transform, movement input, attack aim, or target selection. After the grace interval it changes only spring-arm yaw, clamps pitch to existing rig bounds, and leaves camera collision enabled. A zero horizontal player-to-boss vector skips automatic yaw; `FindDeltaAngleDegrees` handles wraparound. Off, lost target/controller, or EndPlay restores the arm's saved `bUsePawnControlRotation`. The independent BossBlocks capsule response and HideBossInside local component list retain their own state/cleanup methods.

## Batch audit and evidence

The combined offline contracts cover all three distinct default-off Cvars; lock-on target replacement, nonlocal/lost target cleanup, angle wrapping, zero-vector handling, input grace, pitch limits and no movement/controller writes; hide bounds/hysteresis and local-only mesh effects; and BossBlocks target restore. Focused suite result: 22/22. All three test files pass `py_compile`; doc links=0; diff check has no whitespace errors (existing line-ending notices only).

No C-1051 camera option is preferred or owner-approved in the mailbox. The 0.35 s manual grace, 120 deg/s yaw cap, and HideBossInside 5 cm margins are provisional test values. Claude's build, native suite, and legacy/data probe/feel runs remain the runtime acceptance authority. See the AP-C01–C05 through AP-C26–C30 handoffs for per-option run sheets.
