# Executor hit acceptance ordering audit (Queue D109)

**Scope:** static trace of framework executor hit counters relative to resolver outcomes and existing test coverage. No tests run.

`Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:282-300` builds one payload and calls `Resolver->Resolve` before changing hit counters. Only `Accepted` increments `HitsAccepted` and `CardAcceptedHits`, adds applied damage, conditionally increments `HitsGuarded`, and notifies boss posture/damage consumers. Only `Parried` increments `HitsParried`/`CardParriedHits` and records parried contact. Other outcomes (duplicate, refused, invalid target, etc.) do not enter either branch. The ring-window path at `:311-314` and direct blade-window path share this `ApplyHit` lambda, so both use the same outcome ordering.

Tests located in `Source/OneBossFight/Tests` cover the pure damage resolver's accepted/guarded/parried/refused semantics and hit-group dedupe, but this scan found no direct framework executor counter assertions (`HitsAccepted`, `HitsGuarded`, or `HitsParried` accessors) in test files. The harness exercises card abort/retry lifecycle, not a live hit acceptance sequence. Thus counter order is source-confirmed; stateful executor counter behavior under duplicate/refusal is not separately witnessed.

**Boundary:** resolver outcome is the authority for counter increments. `Guarded` is a subcategory of Accepted only when pre-hit blocking tag was observed; a Parried result is categorized separately. This audit does not claim runtime event/tick ordering or that every accepted result applied positive damage.
