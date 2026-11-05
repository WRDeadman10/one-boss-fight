# Queue D131 — executor open-window terminal cleanup audit

Date: 2026-11-03  
Method: static trace of move-model/executor terminal paths and existing tests; no tests run.

## Cleanup paths

- Normal move-model finish (`Cross` at RecoveryEnd) emits Finished, sets Idle, resets the current card and clears `OpenWindows`.
- `Abort` calls `CloseAndClear`, which emits Close for every currently open window, emits Aborted, clears the set/card, and returns the model to Idle. Clock-mode, invalid/backward clock, and clock-overflow failures also call this cleanup.
- `ResetGeneration` closes/aborts the current move before advancing the generation.
- Executor `Abort` centralizes cleanup and is called for arena leash, stance break, boss death, failure, EndPlay, watchdog, and other failure/lifecycle paths. Executor EndPlay also calls Abort.

## Test coverage

`RPGBossEncounterLoopTests.cpp` opens a window, checks `OpenWindowCount() > 0`, resets generation, then asserts Close precedes Aborted; it does not assert count is zero afterward. The move-model and executor tests exercise finish/abort/reset behavior and event/state cleanup, but repository search found only the one positive `OpenWindowCount` assertion, no direct zero-count assertion after clean finish, abort, death/failure, EndPlay, or clock refusal. Harness abort starts at time zero before its synthetic window opens, so it is not a positive-window cleanup test.

## Result / limits

Source paths clear open-window state on finish and terminal abort/reset. No direct count-baseline regression assertions establish each path's invariant, and executor lifecycle paths are not independently exercised with an active window in the current harness. No code or test changed; static review only.
