# Restart result-counter scope (Queue C S3, 2026-11-03)

## Observed behavior

`URPGFrameworkMoveExecutor::Rearm` does not clear `HitsAccepted`, `HitsGuarded`, `HitsParried`, or `AppliedDamage` (`Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:96–105`). Boss completion uses these totals in `invariant` and `RESULT` (`Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:615–618`). The counters therefore describe executor lifetime across encounter generations.

In each retained F8 restart run, generation one reports `BossDefeated acceptedHits=1 attacks=2`; after `encounter_reset generation=2`, the generation-two invariant reports target HP `800 -> 765` while `acceptedHits=2 appliedDamage=70` (`Docs/BossCombatReview/Execution/Claude/F8/ki150b/restart1/editor_raw.log:1869,1872,2275–2276`; restart2 `1864,1867,2233–2234`; restart3 `1854,1857,2257–2258`). The generation-two health delta and single successful generation-two contact are 35 damage / one hit; result counters are cumulative.

## Consumer and grading behavior

- `grade_f8_log.py:139`, `grade_f9_log.py:84`, and `grade_f10_log.py:95` parse only the RESULT outcome word; they do not read numeric RESULT counters.
- `validate_framework_proof_logs.py:50,149` allows the optional numeric fields by syntax but does not compare them to generation-local damage.
- `compare_runs.py:86,188–189` counts `hit` telemetry lines and compares counts across logs; it does not consume RESULT `acceptedHits`.
- `CARD_END` reports per-card `hitsAccepted` / `appliedDamage` (`RPGFrameworkMoveExecutor.cpp:206`); it does not establish a generation-local RESULT contract.

No reviewed grader asserts that these RESULT counters are generation-local or cumulative. The report leaves the contract decision to Lead (C-712 requested the evidence before deciding). Once decided, add a pure two-generation regression and update the log/schema/docs together; no runtime counters changed in this task.
