# E148 decision audit: cross-platform seed guarantee

`FRPGBossMoveSelector::Select` uses `FRandomStream(TieSeed + StartedCount)` and selects from the ordered eligible tie tier. Selector tests prove repeatability in the current test environment and that ties are bounded; they do not prove bit-identical sequences across engine versions, platforms, compiler/runtime changes, or candidate-order changes. Cue helpers additionally combine `GetTypeHash` values, which is not a documented cross-version replay contract here.

No owner decision is required for the current deterministic-within-build behavior. If replay/network compatibility across platforms or engine versions is a product requirement, the owner must approve that guarantee and a separately specified stable PRNG/hash contract before implementation. Do not advertise cross-platform seed stability on present evidence.

Verification: static source/test inspection only; no tests/build/Editor run.
