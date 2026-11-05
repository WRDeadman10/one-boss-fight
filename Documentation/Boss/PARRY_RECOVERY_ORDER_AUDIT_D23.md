# Parry recovery order audit (Queue D23)

Scope: static source and existing-test audit of parry-added boss recovery, its cleanup, and interactions with combo continuation and stance-break recovery. No production source changes; no tests/build/Editor/PIE run.

## Timing and order

1. Both ordinary swept windows and the grab-release contact route call `RecordParriedContact` only when the resolver returns `Parried` (`Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:282-294,405-416`). The helper reads the player's current grade and the boss profile, derives the card's recovery duration from `(RecoveryEndSeconds - ActiveEndSeconds) / CardPlayRate`, scales it through `RPGBossRecoveryWindow`, then calls `NoteParried` (`RPGFrameworkMoveExecutor.cpp:35-45`).
2. `NoteParried` queues a next-tick posture reaction and retains the greatest finite recovery duration received before consumption (`Source/OneBossFight/Boss/RPGFrameworkBossCharacter.h:43-49,127-128`). The posture reaction runs at the start of `Tick` (`RPGFrameworkBossCharacter.cpp:237-240`); `ApplyHit` may drain posture and call `StartStagger` at zero (`:638-661`).
3. The queued extra recovery is consumed only in the finished-and-clean move block: set `ParryRecoveryUntil = Now + PendingParryRecoverySeconds`, log grade/duration, and clear the pending fields. `Tick` returns while `Now < ParryRecoveryUntil`, before combo-gate handling or preparing/selecting another attack (`RPGFrameworkBossCharacter.cpp:578-610`, especially `:591-608`). Thus a parry extends the neutral interval after the current move's own recovery, and when that move belongs to a combo it delays the combo gate/continuation too. The absolute deadline uses world time; it is not a timer callback.
4. A stance break aborts a still-running move, clears active combo/pause state, and enters stagger (`RPGFrameworkBossCharacter.cpp:693-716`). At stagger end an aborted move is rearmed and `bStartedMove` is cleared before normal selection resumes (`:718-732`). `StartStagger`/`EndStagger` do not clear the pending parry-recovery fields. Restart, death, and failure do clear them (`:855-889`); initialization also clears them (`:78`).

## Conditional lifecycle risk

If an enabled parry posture reaction reaches zero posture while the parried boss move is still active, the next-tick reaction can start stagger and abort that move before the normal finished-and-clean recovery consumer is reached. Since stagger recovery clears `bStartedMove` but leaves `PendingParryRecoverySeconds` intact, the queued parry duration appears able to survive the break and be consumed after a later, unrelated move finishes. This is a source-derived conditional risk, not a runtime-reproduced defect or confirmed design violation. Record as low, unverified KI-177; test the simultaneous parry/posture-break path before any production change.

## Existing coverage and gap

`OneBossFight.Framework.ParryRecovery.WiringBoundary` tests pure grade scaling, scale composition, unknown grade, and NaN input (`Source/OneBossFight/Tests/RPGBossParryRecoveryWiringTests.cpp:7-18`). `OneBossFight.Framework.Runtime.ParryRecoveryProfile` tests profile validation (`RPGFrameworkRuntimeTests.cpp:193-205`). Neither drives `ARPGFrameworkBossCharacter::Tick`, `StartStagger`/`EndStagger`, executor abort/rearm, combo gating, or the pending-to-active deadline lifecycle. No existing parry-recovery stateful actor test was found. A focused fixture should prove: ordinary parry delays the next decision; combo parry delays the next combo card; stance break during pending recovery does not leak the interval into a later unrelated move; restart/death/failure clear queued state.

## Boundary

The profile scale and grade-derived duration are covered as pure rules/profile validation only. The exact actor ordering and KI-177 path remain un-witnessed until a stateful fixture or runtime proof exercises them. This audit does not assert a specific visual, audio, or pack-boss behavior.
