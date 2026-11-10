# Queue BB X06–X10 handoff

Date: 2026-11-10  
Scope: teardown tag ownership, proof-hook issue tracking, and Sevarog approach navigation.

## X06–X07: surviving-pawn tag cleanup

`RPGOwnedTagCleanup.h` now provides a world-timer retry owner independent of the component being torn down. On `EndPlay`, `RPGIFrameMonitor` and `RPGPlayerParry` still attempt their immediate pack removal; when the reflected call fails, they schedule retries until the pack removal function can be issued or the weak actor is gone. It stops on successful invocation so another system's separate ownership of the same tag is not removed. Delay backs off from 0.25 s to 4 s. No asset or default gameplay path changed.

The native policy fixture checks the continue/stop condition at `Source/OneBossFight/Tests/RPGOwnedTagCleanupTests.cpp`. A live Blueprint removal failure is not simulated by this pure rule test. The C-1269 locked Development build and DD27j-hash-pinned suite passed 503/503, including `OneBossFight.Player.OwnedTagCleanup.RetryPolicy`.

## X08: development proof-hook reset

The existing C-1252a entry in `KNOWN_ISSUES.md` now names the omitted fields: `ProofIFStart`, `ProofIFPressAt`, `ProofIFProbes`, `bProofIFPressed`, and `ProofGStart` (`RPGFrameworkBossCharacter.h:86–87`; reset path `RPGFrameworkBossCharacter.cpp:867–870`). This is development proof telemetry carried across same-fixture test restarts, not a production gameplay-state leak. No reset behavior was changed.

## X09–X10: out-of-band navigation

**BLOCKED (exact root cause not isolated).** The retained `C1258A_RANGE_RETRY/nav_failure_baseline.log` proves one nav actor, a full path request (`RPGFrameworkBossController.cpp:43–48`), and a later `Framework.Nav.MoveFailed` terminal (`OnMoveCompleted`, `:51–58`). The spawn projection moved 217.275 cm vertically (`RPGFrameworkBossCharacter.cpp:145–149`; report `C1258A_SEVAROG_IN_BAND_NAV_AND_END.md`). That makes an elevated off-nav start a plausible cause, but the callback records neither the `FPathFollowingResult` code/flags nor the boss's actual path-follow position/velocity at failure. Therefore the projection delta alone does not prove why path following failed.

X10 is **BLOCKED** until a Lead rerun captures the failure result and the root cause is established. No map edit or behavior change was made. The established in-band test-only bypass remains guarded, default off, and does not claim that normal navigation is fixed.

## Validation / review boundary

The C-1269 locked Editor Development build succeeded and the DD27j-hash-pinned `Automation RunTests OneBossFight` suite completed 503/503 with no failures, including `OneBossFight.Player.OwnedTagCleanup.RetryPolicy`. This verifies the native retry-policy fixture; the live Blueprint removal-failure case is still not simulated. X09 remains blocked pending a Lead-owned failure-case PIE run that records `FPathFollowingResult` and the pawn's terminal path-follow state.
