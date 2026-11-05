# Gap-closer exit boundary audit (Queue D103)

**Scope:** static source/test comparison for the pure range gate. It is documented as unwired; no test or runtime was run.

`Source/OneBossFight/Player/RPGBossGapCloserRules.h:8-13` rejects nonfinite/negative range or thresholds and reversed hysteresis (`ExitRangeCm < EnterRangeCm`). Otherwise a new action is recommended only at strict `RangeCm > ExitRangeCm`; an already-active action persists only at strict `RangeCm > EnterRangeCm`. Equality returns false in either state, so an active action stops exactly at enter range. Equal enter/exit thresholds are accepted and simply collapse the hysteresis interval.

`Source/OneBossFight/Tests/RPGBossGapCloserRulesTests.cpp:10-14` checks an inside exit-range sample, above-exit start, above-enter persistence, exact-enter stop, reversed config, and NaN range. `RPGBossGapCloserExitBoundaryMutationTests.cpp:10-16` checks exact 600 exit does not start and 600.001 does.

Gaps: no next-representable values immediately around either boundary; no exact equality/adjacency for the active enter boundary beyond equality; no explicit negative range or nonfinite threshold cases; equal thresholds are accepted but not tested. The helper decides only whether to close range; action execution, movement stop at the endpoint, vertical distance, and runtime wiring are outside the proved contract.
