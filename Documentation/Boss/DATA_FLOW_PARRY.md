# One parry: input to boss reaction

```mermaid
sequenceDiagram
  participant Input as Player IA_Parry
  participant Parry as Player Parry Component
  participant Tag as Pack Parry Tag
  participant Executor as Boss Executor
  participant Resolver
  participant Boss
  Input->>Parry: Started
  Parry->>Parry: Press: cooldown and optional stamina check
  Parry->>Tag: Set Status.ParryActive
  Note over Parry: Window is open by game-clock time
  Executor->>Resolver: Contact payload during window
  Resolver->>Parry: IsParrying at contact instant
  Resolver->>Parry: NotifyParried
  Resolver-->>Executor: Parried; hit key spent, no player HP damage
  Executor->>Boss: Count parry, queue posture reaction/recovery
  Note over Parry: Window closes; clear tag and settle/refund optional stamina
```

## Source checkpoints

- `URPGPlayerParry` binds the action at BeginPlay and retries while the input component is late (`RPGPlayerParry.cpp:20-58`). The action calls `Press`; the state rules enforce the timed window and cooldown. Optional stamina may be charged (`:60-99`).
- A successful press sets `Status.ParryActive`; the tag is also consumed by pack-owned impact logic. `TickComponent` clears it when the timed window closes (`:26-38,89-99,179-191`).
- The damage resolver asks `IsParrying` only after liveness, freshness, duplicate and invulnerability checks. On `Parried`, it spends the hit key and calls `NotifyParried` (`RPGDamageResolver.cpp:151-185`).
- `NotifyParried` records grade and marks an optional stamina charge as earned (`RPGPlayerParry.cpp:122-135`). Stamina settlement/refund waits until the window closes; failed cleanup stays pending for retry, and EndPlay makes bounded cleanup attempts (`:137-176`).
- The executor records parried hits and tells the framework boss, which queues posture reaction for the following boss tick (`RPGFrameworkMoveExecutor.cpp:289-294,411-414`; `RPGFrameworkBossCharacter.h:43-48`).

The resolver's `Parried` result proves the framework contact used this window. It does not by itself prove the pack boss's separate reaction behavior; that remains tracked in `KNOWN_ISSUES.md` KI-153.
