# Framework boss character

`ARPGFrameworkBossCharacter` is the native authority for the proof boss's encounter state, health, phase, posture, bleed, target-health invariant, and executor coordination. `InitializeProof` takes the fixture, profile, explicit target, encounter and generation identifiers; public restart is restricted to terminal success/death and a newer generation (`RPGFrameworkBossCharacter.h:23-24,57-60`).

## State to inspect

The private state groups initialization/failure/arrival/move/success (`RPGFrameworkBossCharacter.h:69-72`), health and hittability/death (`:74-76`), phase and posture/stagger (`:97-100`), bleed (`:106-109`), expected target HP (`:69`), and pending parry reaction (`:127`). `ExpectedTargetHP` is adjusted only when accepted damage is applied (`:42-43`); tick checks the live target against that expectation and fails the encounter on invalid target or unexplained health drift (`RPGFrameworkBossCharacter.cpp:248-262`).

## Tick order

The authoritative `Tick` first calls `Super`, then exits for uninitialized or terminal states and applies queued parry posture before other encounter work (`RPGFrameworkBossCharacter.cpp:237-240`). It performs target/leash and health-invariant checks (`:248-262`), advances proof hooks only in non-Shipping blocks (`:264-281`), then advances dodge, flask, activity and LOS observations in that order (`:337-340`). Later it ticks overlay/stagger presentation and the encounter decision flow; the selector decision starts a card through the executor, while finished clean cards pass through recovery/combo/next-attack gates (`:348-364`, `:516-609`).

Death, failure, and teardown are separate transitions: `Die` marks terminal state and cleans active playback, `Fail` records the failure reason and stops the run, and `EndPlay` releases owned runtime state (`RPGFrameworkBossCharacter.cpp:874-893`).

Read with [Executor reference](REF_EXECUTOR.md), [Selector reference](REF_SELECTOR.md), and [Resolver reference](REF_RESOLVER.md). These references describe source behavior, not a claim that all branches have live proof coverage.
