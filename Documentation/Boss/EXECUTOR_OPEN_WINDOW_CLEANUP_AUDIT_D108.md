# Executor open-window cleanup audit (Queue D108)

**Scope:** static trace of model/executor terminal paths and existing coverage; no tests run.

The window set is owned by `FRPGBossMoveModel` (`RPGBossMoveModel.h:73-76`) and surfaced through executor `OpenWindowCount`. `RPGBossMoveModel.cpp:125-132` `CloseAndClear` emits a Close event for every currently open window, then resets `OpenWindows`, clears the active card, and returns model state to Idle. Normal progression closes each window at its authored end and the model finishes at RecoveryEnd (`:76-86`). `Abort` and `ResetGeneration` both funnel through `CloseAndClear` (`:135-149`).

At executor level, `Abort` is idempotent after abort/finish, releases a held grab, calls `Model_.Abort`, stops the owned montage, disables ticking, unlocks motion, and records cleanup once (`RPGFrameworkMoveExecutor.cpp:580-598`). The clean finish path observes idle model and stopped montage before restoring rate and marking `bFinished` (`:193-209`). EndPlay calls Abort (`:603-605`).

Tests: `RPGBossMoveModelTests.cpp:113-140` checks committed/active/recovery/idle abort, active-window Close-before-Aborted event order, repeat-abort no events, and invalid-clock failure cleanup. A broader property case at `:230-245` checks exactly one terminal abort event. The executor harness (`RPGBossExecutorHarnessTests.cpp:93-140`) proves abort leaves `IsIdle`, recovers, retries with fresh token, accepts newer rearm, and repeated cleanup remains idle. Current tests do not assert `OpenWindowCount()==0` after each executor terminal path; most model checks assert emitted events/state, not the exposed count.

**Conclusion:** source converges all model terminal paths on `CloseAndClear`, so open-window count should return to zero; event and idle evidence is present, but the direct count assertion across normal finish/abort/reset/failure paths is absent. EndPlay, death/failure, and live executor cleanup remain source-derived unless separately exercised.
