# Restart result counters and retained-log index (Queue C S6–S7)

Read-only continuation of `RESULT_COUNTER_SCOPE_S3.md`. No counter contract or runtime behavior is changed here.

## Counter scope crosswalk

| Value | Owner / reset point | Emission | Restart evidence | Consumer result |
|---|---|---|---|---|
| `HitsAccepted` | `URPGFrameworkMoveExecutor`; `Rearm` does not reset it (`Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:96–105`). | Boss invariant and `RESULT` read executor totals (`Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:614–618`). | Each F8 run begins Gen2 at target HP 800; final HP 765, one 35-damage Gen2 contact, but invariant and result say `acceptedHits=2`. | Lifetime total is directly observed; whether RESULT should also expose generation-local values is a Lead decision. |
| `AppliedDamage` | Same executor lifetime; not reset by `Rearm` (`RPGFrameworkMoveExecutor.cpp:96–105`). | Invariant/RESULT (`RPGFrameworkBossCharacter.cpp:614–618`); card-end telemetry is card-scoped (`RPGFrameworkMoveExecutor.cpp:206`). | Each Gen2 invariant says `appliedDamage=70`, while the Gen2 HP delta is 35. | Lifetime accumulation is consistent with the observed 70; no reviewed grader compares the number to the generation delta. |
| `HitsGuarded`, `HitsParried` | Same lifetime fields and reset behavior (`RPGFrameworkMoveExecutor.cpp:96–105`). | Emitted with executor summary fields (`RPGFrameworkBossCharacter.cpp:614–618`). | The three restart runs reviewed here do not isolate a per-generation guard/parry counter contract. | No claim about generation-local guard/parry totals; add dedicated evidence only after the counter contract is decided. |

The F8/F9/F10 graders parse `RESULT` outcome, not the numeric hit totals (`grade_f8_log.py:139`, `grade_f9_log.py:84`, `grade_f10_log.py:95`). The validator checks accepted syntax but does not reconcile numeric fields with per-generation damage (`validate_framework_proof_logs.py:50,149`). `compare_runs.py:86,188–189` counts hit tokens across logs. These reviewed consumers therefore do not establish whether RESULT totals are lifetime or generation-local by contract.

## Restart evidence index

All paths are relative to repository root. Line numbers below are exact retained-log lines.

| Run | Gen1 terminal result | Generation reset | Gen2 invariant | Gen2 terminal result |
|---|---|---|---|---|
| `Docs/BossCombatReview/Execution/Claude/F8/ki150b/restart1/editor_raw.log` | 1869 `BossDefeated acceptedHits=1 attacks=2` | 1872 `generation=2` | 2275 `targetHPBefore=800 targetHPAfter=765 ... acceptedHits=2 appliedDamage=70` | 2276 `CompletedWithDamage acceptedHits=2 attacks=2` |
| `Docs/BossCombatReview/Execution/Claude/F8/ki150b/restart2/editor_raw.log` | 1864 `BossDefeated acceptedHits=1 attacks=2` | 1867 `generation=2` | 2233 `targetHPBefore=800 targetHPAfter=765 ... acceptedHits=2 appliedDamage=70` | 2234 `CompletedWithDamage acceptedHits=2 attacks=2` |
| `Docs/BossCombatReview/Execution/Claude/F8/ki150b/restart3/editor_raw.log` | 1854 `BossDefeated acceptedHits=1 attacks=2` | 1857 `generation=2` | 2257 `targetHPBefore=800 targetHPAfter=765 ... acceptedHits=2 appliedDamage=70` | 2258 `CompletedWithDamage acceptedHits=2 attacks=2` |

No log contains a separately emitted generation-local summary for all four executor counters. Per-generation totals remain unimplemented and intentionally deferred pending Lead's counter-scope decision.
