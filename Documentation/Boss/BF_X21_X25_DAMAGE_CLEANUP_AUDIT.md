# Queue BF Batch 5 — damage identity and owned cleanup audit

Status: read-only source/test audit. No runtime source change was warranted by this pass. No Unreal, build, PIE, assets, commit, or push.

## X21 — damage rejection precedence

| Order | Rule | Source | Consequence |
|---|---|---|---|
| 1 | Resolver enabled, target valid, world valid | `RPGDamageResolver.cpp:134-141` | Otherwise `Failed`, before policy evaluation. |
| 2 | Readable health > 0 and no `Status.Dead` | `RPGDamageResolver.cpp:147-148` | Dead/unreadable target becomes `RejectedDead`. |
| 3 | Attacker alive and payload generation current | `RPGDamageResolver.cpp:149-155`; `RPGDamageResolver.h:101-108` | Dead attacker or stale generation becomes `RejectedStale`. |
| 4 | Swing identity is not already spent | `RPGDamageResolver.cpp:151-155` | A prior spent hit is `RejectedDuplicate`. |
| 5 | Read `Status.Invulnerable` at resolution time | `RPGDamageResolver.cpp:153-155` | Dodge i-frames reject before parry. |
| 6 | Read parry window if not invulnerable | `RPGDamageResolver.cpp:154-155`; `RPGParryTests.cpp:32-38` | Parry is spent and not damaging. |
| 7 | Apply guard only to an otherwise accepted, explicitly blockable hit on the actual local player pawn | `RPGDamageResolver.cpp:156-160`; `RPGDamageResolver.h:112-115` | Guard cannot supersede dead/stale/duplicate/dodge/parry. |
| 8 | Write player health and spend only after successful write | `RPGDamageResolver.cpp:164-180` | Failed write does not add the key to `Spent`. |

This is the boss-to-player resolver path (A4/A5/A6, as described in `RPGBossDamage.h:12-18`). Player-to-boss damage enters through `RPGHitIntake.cpp:482-486, 541, 696` and `IRPGNativeBossHealth::ApplyPlayerAttackHit` (`RPGNativeBossHealth.h:61-63`, implemented in `RPGFrameworkBossCharacter.cpp:843-873`). These are separate directions with different adapters and should not be presented as a single symmetric rule chain.

## X22 — duplicate identity and multi-target limit

`KeyOf` is `MoveId|AttackInstance|HitKey` (`RPGDamageResolver.cpp:37-39`); `Generation` is omitted from the string, but `SyncGeneration` clears spent/overlap sets whenever the current generation changes (`RPGDamageResolver.cpp:70-78`). The card validator allows repeated `HitGroup` only by design; secondary windows must share a direct group (`RPGBossMoveCard.cpp:220-223`), and the executor orders direct windows before secondary windows then derives `HitKey` from `HitGroup` (`RPGFrameworkMoveExecutor.cpp:293-299`). The resolver records accepted, parried, and blocked keys; invulnerability/stale/dead contacts remain retryable (`RPGDamageResolver.cpp:164-204`).

The spent key does not contain target identity. Because the current contract is one boss duel against the local player and the key is stored on the boss-owned resolver, this is consistent with the shipped single-target path. If a move is expanded to resolve against multiple player-controlled targets, the first accepted target would suppress the same move/instance/hit key on the next target; that is a bounded extension risk, not a reproduced defect in the one-player contract. Current pure policy tests cover precedence (`RPGAutomationTests.cpp:182-213`) but do not simulate multi-target resolver state.

## X23/X24 — retry lifecycle and live actor reuse

`ScheduleAfterRemovalFailure` is called by parry teardown only after five immediate attempts fail (`RPGPlayerParry.cpp:237-245`). The shared helper captures a `TWeakObjectPtr`, checks invalid/destroying owners before each call, stops when reflected removal is issued, and schedules a one-shot timer only while the owner has a world (`RPGOwnedTagCleanup.h:37-66`). Delay is bounded exponential: 0.25 s, 0.5 s, 1 s, 2 s, then 4 s for all later attempts (`RPGOwnedTagCleanup.h:21-25`). The timer handle is local to that attempt, so the caller cannot explicitly cancel an already scheduled retry; actor/world teardown and the weak/destroying checks are the lifetime fences.

There is no encounter-generation or tag-ownership token in the captured retry state. If a still-live actor is reused for a new encounter after an old removal failure, an old retry could remove the same tag after the new encounter re-adds it. This is a plausible lifecycle race from source, not a verified runtime incident. Existing ownership has no generic generation for live actor reuse; do not describe the weak pointer alone as protecting against reuse. A follow-up fix needs a per-owner/tag generation or equivalent lease and a focused two-generation test before changing the semantics.

## X25 — pure retry rule gap

`RPGOwnedTagCleanup::ShouldRetry` only retries while the owner is alive and the removal call failed. `RetryDelaySeconds` clamps invalid/nonpositive attempts to the first delay and caps the long-run delay at 4 seconds (`RPGOwnedTagCleanup.h:15-25`). Existing `OwnedTagCleanup.RetryPolicy` tests owner/result combinations, attempts `-10`, `1–6`, and `10000`, and a three-call failure-then-success schedule (`RPGOwnedTagCleanupTests.cpp:6-34`). No bounded pure scheduling gap was found; timer cancellation and generation identity are integration/lifecycle questions outside that pure delay rule.

## Disposition

- X21: precedence is source-backed and separately distinguishes outgoing versus incoming adapters.
- X22: current duel's single-target identity is sound; target identity must be added if multi-target damage becomes supported.
- X23: weak lifetime and bounded backoff are present; retry attempt is unbounded in count while a live actor keeps refusing removal.
- X24: actor reuse has no captured generation/lease fence; record as a source-level risk pending a targeted two-generation acceptance case.
- X25: existing pure rule tests cover the invalid-attempt bounds and normal schedule; no code/test gap found to fill in this task.

No claim of live actor reuse, world teardown, or timer cancellation behavior is made.
