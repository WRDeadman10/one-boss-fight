# Selector tie-order determinism audit (Queue D106)

**Scope:** static comparison of candidate iteration, tie-tier construction, and current selector tests. No tests run.

`Source/OneBossFight/Player/RPGBossMoveSelector.cpp:64-68` scans candidates in input order and replaces the winner only for strictly greater score; exact ties therefore retain the earliest eligible candidate when `TieBand == 0`. At `:73-81`, nonzero tie band gathers eligible tier indices in trace/input order and uses `FRandomStream(TieSeed + StartedCount)` to choose an index from that array. Thus determinism holds for identical candidate order/state/seed, but candidate reordering can change selected identity even with the same seed; there is no identity sort before the random pick.

`Source/OneBossFight/Tests/RPGBossMoveSelectorTests.cpp:65-69` verifies exact ties choose lowest input index repeatedly with the deterministic zero-band rule. The bounded-tie test at `:104-123` checks same seed/same candidate sequence repeatability, different seed sequence variation, and deterministic zero-band behavior. It does not permute candidate order while holding seed and started count constant.

Conclusion: input-order dependence is explicit and source-supported. It is acceptable as a deterministic contract only while candidate order is stable; cross-order identity invariance is not tested or promised. No change recommended absent a requirement for permutation-invariant selection.
