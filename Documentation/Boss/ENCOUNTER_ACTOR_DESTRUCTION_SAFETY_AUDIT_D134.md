# Queue D134 — encounter actor destruction safety audit

Date: 2026-11-03  
Method: static weak-reference/callback/cleanup trace; no runtime destruction test.

## Target destruction

Boss stores target/controller/fixture as weak pointers. `TargetFault` checks controller and target validity, `IsActorBeingDestroyed`, controller↔pawn possession identity, and world identity before reading attributes. Boss Tick converts invalid/destroyed/unreadable target state into `Fail`; Fail stops owned AI movement and character movement and aborts the executor. The executor also uses weak owner/target/resolver references; its tick checks owner, target validity, anim identity, world identity, and target destruction before reading target state, then routes the failure to boss Fail (or directly aborts if owner is gone). `SweepWindows` itself returns early if target/owner/resolver is unavailable, with the preceding executor tick providing the normal active-card failure path.

## Boss destruction / callback scope

Boss `EndPlay` stops owned AI movement, aborts the executor, stops stagger presentation, and clears dependency/weak target/controller/fixture references. Executor `EndPlay` calls idempotent Abort. The resolver's life/generation providers capture the boss weakly and return false/zero after invalidation. No timer registration was found in these boss/executor sources; periodic work is component/actor ticking, disabled/stopped on terminal cleanup.

## Limits / findings

Source is fail-closed for target/boss invalidation on the observed tick and EndPlay paths. A target destroyed between an executor validity check and its synchronous sweep/resolve work is not guarded by a lock; Unreal game-thread sequencing is assumed. No dedicated automation/runtime test destroys the target or boss during an active callback and verifies the watchdog/tick/timer state. No assertion about timer cleanup is applicable because these classes do not register timers in the scanned sources. Static only.
