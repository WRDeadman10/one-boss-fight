# Strafe-stuck detector edge test audit (Queue D37)

Scope: map expected/moved ratio, elapsed observation window, zero-delta behavior, and accumulator reset against source and existing tests. Static only; no tests run.

## Source semantics

- `Update` accumulates expected distance, moved distance, and `Dt`; negative/nonfinite inputs reset the three accumulators, and nonfinite accumulated totals also reset (`Source/OneBossFight/Player/RPGBossStuckRules.h:18-36`). Zero values are accepted and simply add zero.
- `IsStuck` refuses nonfinite/negative ratio, nonfinite/nonpositive window, an already-flipped state, elapsed time below the requested window, or nonpositive expected distance. It flips once only when `AccumMoved / AccumExpected < MinRatio`; exact ratio equality is not stuck (`:39-53`). Runtime calls it with `.5` and `.3` (`RPGFrameworkBossCharacter.cpp:503-505`).

## Existing coverage

- `OneBossFight.Framework.BossStuck.Rules` uses 18 steps of `.016` (< .3 s) and one `.02` step (> .3 s), then verifies blocked movement flips once and free movement never flips (`Source/OneBossFight/Tests/RPGBossStuckTests.cpp:12-28`). It does not assert exact `.3`-second inclusion or adjacent representable values around that threshold.
- The 0–100 ratio sweep checks below, exact, and above `.5`; equality correctly expects false (`:29-37`). It samples by integer ratios, not adjacent floating representations.
- Invalid NaN movement and accumulator overflow fail closed (`:26-28,39-42`), but the test does not explicitly assert every accumulator was zeroed or prove recovery on the next valid update. Zero `Dt`, zero expected movement, zero moved movement, and negative inputs have no named assertions. The recovery policy test (`RPGBossStuckRecoveryRulesTests.cpp:8-12`) is a separate one-time attempt/cap rule, not detector coverage.

## Gaps and bounded proposal

Add detector mutation coverage for elapsed exactly `.3` and next representable values below/above; ratio next-representable values below/equal/above `.5`; zero `Dt` before/at/after the window; zero expected distance; negative input reset with state-field assertions; and a valid update after reset. Keep detector-state checks separate from actor/geometry proof. No production issue is established by these test gaps.
