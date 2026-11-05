# Selector reset idempotence audit (Queue D107)

**Scope:** static review of selector mutable state, reset implementation, and existing tests. No tests run.

`Source/OneBossFight/Player/RPGBossMoveSelector.cpp:97-101` resets per-candidate cooldown timestamps to -1, clears repeat history and cone-memory map, and sets the tie-break `StartedCount` to zero; it does not clear immutable config/candidates or de-initialize the selector. A second reset performs the same assignments, so the source operation is idempotent.

Current test witnesses: `RPGBossMoveSelectorTests.cpp:78-83` starts a candidate, resets once, then checks the old cooldown/history cannot block selection at an earlier encounter clock; `:219-224` confirms reset clears cone hysteresis memory. No test calls Reset twice or compares post-reset traces/sequences against a freshly initialized selector, so state-completeness is inferred from source field inventory rather than fully asserted.

`FRPGBossMoveSelector` mutable state includes `LastStartClock`, `Recent`, `StartedCount`, and mutable `ConeInside` (`RPGBossMoveSelector.h:70-75`); all four are cleared/reset by the method. The initialized flag is intentionally retained so Reset re-arms the same selector. No shared/world state is visible in this class-level reset.
