# One attack: decision to hit

This sequence describes the native framework boss path. Pack AI can drive other attacks and does not use every step below.

```mermaid
sequenceDiagram
  participant Boss as Framework Boss
  participant Selector
  participant Executor
  participant Model as Move Model
  participant Resolver
  participant Player
  Boss->>Boss: Validate target / health invariant
  Boss->>Selector: Snapshot (range, yaw, phase, clock, context)
  Selector->>Selector: Hard eligibility + cooldown; score eligible cards
  Selector-->>Boss: chosen card or no candidate + traces
  Boss->>Executor: StartCard(card, snapshot)
  Executor->>Model: Begin timeline
  Executor->>Executor: Play and observe montage position
  Executor->>Model: Advance observed local time
  Model-->>Executor: commit / window / recovery / finish events
  Executor->>Executor: Sweep geometry in direct-then-secondary order
  Executor->>Resolver: Resolve(target, move/instance/generation/hit key)
  Resolver->>Player: apply HP only when accepted
  Resolver-->>Executor: Accepted / Parried / rejection / miss result
  Executor-->>Boss: damage, parry, finish or abort accounting
```

## Source checkpoints

1. The boss builds a decision snapshot, selector traces each candidate, and the chosen card is started (`RPGFrameworkBossCharacter.cpp:428-518`). The selector applies model eligibility and cooldown before score, then applies optional tie-band selection (`RPGBossMoveSelector.cpp:33-80`).
2. `StartCard` validates idle/target/card context before playback; executor ticks observe the montage and advance the move model from its observed local position (`RPGFrameworkMoveExecutor.cpp:120-173,175-273`).
3. The executor emits model events, then applies warp, sweeps windows, checks grabs and fires cues (`:265-272`). Direct windows precede secondary windows; both resolve through the shared resolver (`:274-300,411-414`).
4. The payload's move ID, attack instance, generation, and hit key let the resolver distinguish old, duplicate and accepted contacts (`RPGDamageResolver.h:28-48`). It reads health/liveness, current generation, invulnerability and parry, then applies the decision (`RPGDamageResolver.cpp:133-190`).
5. Accepted damage updates executor and boss accounting; a parry is counted and queues the boss posture reaction for the next boss tick (`RPGFrameworkMoveExecutor.cpp:289-294,411-414`; `RPGFrameworkBossCharacter.h:43-48`).

The move model reaching Idle is not alone enough to call the executor clean: its owned montage must also be cleared (`RPGFrameworkMoveExecutor.cpp:593-596`).
