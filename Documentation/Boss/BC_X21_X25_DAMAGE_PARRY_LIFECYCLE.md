# Queue BC Batch 5: X21–X25 damage and parry contracts

## X21 — outgoing framework damage rejection policy

`URPGFrameworkMoveExecutor` creates/reuses `URPGDamageResolver`; its damage path resolves only when damage is enabled and resolver, target, and owner are valid. `RPGDamageRules::Decide` precedence is target dead → attacker dead/stale generation → duplicate key → invulnerability → parry → accepted. For accepted project-authored hits only, block applies afterward when the payload opts in, target is player 0, and `Status.Blocking` is present. Rejected invulnerable contacts do not spend the key; accepted, parried, and blocked hits do. This avoids asserting behavior for pack trace moves that use another path.

## X22 — native-health incoming route

Framework actors expose `IRPGNativeBossHealth`; executor setup installs paired alive/generation providers into the resolver. Player-to-boss contacts call the interface's `ApplyHit` path rather than pack `HurtPlayer`/attribute damage. The pack resolver path writes `Attribute.Health` via `HurtPlayer` and optionally uses `URPGBossEncounter` generation. These routes share decision/dedupe concepts but not a proven full gameplay-equivalence contract. Prior BC-X13 records missing production HUD/encounter completion wiring for native death.

## X23 — parry reward key dedupe

Pack trace observation derives a key from generation + boss ID + move + attack instance, or fallback montage name + start time rounded to centiseconds. The project damage resolver's direct parry route invokes the same `URPGPlayerParry::NotifyParried`, which passes through `FRewardDeduplicator`; it accepts a key once per generation and resets keys on generation change. Pack observer additionally tracks observed keys and resets its candidate/contact state when the encounter generation or player changes. Source proves the key gates, not that every pair of hit groups is authored correctly; no authored multi-hit asset claim is made.

## X24 — i-frame monitor teardown and retry

The monitor samples after animation updates, tracks whether `Status.Invulnerable` belongs to an observed montage, and leaves foreign tags alone. If an owned tag survives past its notify window or montage disappearance grace, removal is retried each tick until successful. Death removal is attempted on the observed alive→dead edge; EndPlay attempts once and schedules `RPGOwnedTagCleanup` if the tag cannot be removed. Encounter reset attempts removal once and closes the record only on success; a failure is not retried by the reset callback itself, but the stale-window watchdog can retry if its stale condition is met. That narrow sequencing case lacks a focused transition test in this audit; it is a coverage gap, not a confirmed runtime failure.

## X25 — parry component teardown and retry

The parry component clears pending stamina rollback/refund and removes its owned diagnostic tag up to five times during EndPlay; failed tag removal transfers cleanup to `RPGOwnedTagCleanup`. While active, parry-tag removal is retried from component tick when the window closes. Stamina-cost rollback/refund retries from Tick while pending and makes up to five attempts at EndPlay, but no external owner survives component destruction to retry persistent attribute-write failure after those attempts. This bounded failure path is not demonstrated in runtime; it is a lifecycle-test gap/risk worth covering with a deterministic injected writer failure. No logic change made.

## Scope

Static source audit only. No tests were added or run, no source changes, build, Unreal, PIE, or asset operation. `git diff --check` has no whitespace errors (line-ending notices only).
