# Framework move executor

`URPGFrameworkMoveExecutor` is the runtime adapter between one compiled move card, the boss animation instance, the move timeline model, swept hit windows, and `URPGDamageResolver`. The boss owns it as a component; the component holds weak boss/target references and the active montage/card state. See `RPGFrameworkMoveExecutor.cpp:61-90` and `:69-90`.

## Lifecycle and state

- `Initialize` validates game-thread use, owner/target/world identity, dependencies, montage instance and the first card before it records the playback context (`RPGFrameworkMoveExecutor.cpp:69-90`).
- `Start`/`StartCard` require a clean idle state and an active target; `Rearm`, `RecoverAfterAbort`, and `PrepareNextAttack` distinguish encounter reset, interrupted recovery and normal next-card playback (`:92-123`).
- Each component tick observes montage position and slot weight, rejects backwards/non-finite playback, advances the move model, then applies warp, hit-window sweeps, grab logic and cues (`:175-273`). Model events are logged before world effects are processed (`:265-272`).
- Direct windows are swept before secondary windows. Shared hit-group keys and the common resolver deduplicate simultaneous blade/ring contacts (`:274-300`, `:411-414`).

## Motion locks and cleanup

The executor saves and takes ownership of movement settings when a card needs a motion lock; `UnlockMotion` restores only settings it owns (`:531-549`). `Abort` aborts the model, stops the owned montage, disables component ticking, releases the motion lock and records cleanup (`:571-589`). `EndPlay` routes through the same abort cleanup (`:595-596`). `IsIdle` requires both an idle model and no owned montage; `IsClean` is the same predicate (`:593-594`).

## Reading the log

Look for `[CARD_START]`, `[CARD_END]`, `[FrameworkProof] playback`, event tokens, `hit`, and `cleanup`. The executor records accepted, guarded, and parried contacts separately; a parry is reported by the resolver, and the boss posture reaction is queued for the next boss tick (`RPGFrameworkMoveExecutor.cpp:289-294`, `:411-414`; `RPGFrameworkBossCharacter.h:43-48`).

This is a source reference. It does not claim a live runtime trace for every branch.

For boss-wide generation reset ordering and which executor/selector/player/proof-hook state persists, see `FRAMEWORK_BOSS_RESET_GUIDE_S145.md` (archived).

For lifetime versus per-card damage counters and a line-reconciled retained log example, see `EXECUTOR_ACCOUNTING_GUIDE_S146.md` (archived).
