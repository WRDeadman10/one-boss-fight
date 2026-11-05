# Encounter completion/restart matrix (Queue D110)

**Scope:** static source/test matrix for framework boss terminal outcomes and restart. No tests run.

| Path | Source behavior | Restart eligibility / state |
|---|---|---|
| Completed | `RPGFrameworkBossCharacter.cpp:611-625` sets `bSucceeded=true` only when a started move has finished and executor is clean; logs CompletedAllParried/CompletedWithDamage or CompletedTelemetryOnly. | `CanRestart` accepts succeeded state with a newer generation. |
| Boss defeated | `:876-885` idempotently sets `bDead`, stops movement, aborts executor, and logs BossDefeated. | Restart is allowed for newer generation. |
| Failure | `:887-893` sets sticky `bFailed`, stops movement, aborts executor. | `CanRestart` rejects failures; no retry path through this method. |
| Restart | `:856-874` validates terminal state/new generation, target health, and executor rearm before assigning new generation; resets `bSucceeded`, `bDead`, attack count, boss combat/perception state, selector, and phase, then starts walking. | `bFailed` remains false by precondition and is not rewritten. Old outcome flags are cleared for success/death restart. |

The guard is inline in `RPGFrameworkBossCharacter.h:58-59`: initialized, not failed, terminal via dead or succeeded, and new generation strictly greater. The model independently tests generation abort/rewind (`RPGBossMoveModelTests.cpp:148-154`), but this search found no direct `ARPGFrameworkBossCharacter::RestartEncounter` actor test or matrix proving Completed/Dead restart and Failed refusal together. Runtime result logging and actor restart behavior are therefore source-derived.
