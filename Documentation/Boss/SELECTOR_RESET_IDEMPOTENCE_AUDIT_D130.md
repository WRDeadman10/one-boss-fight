# Queue D130 — selector reset idempotence audit

Date: 2026-11-03  
Method: static field/reset/test trace; no tests run.

## State and behavior

Mutable encounter history is `LastStartClock` (per-card cooldown timestamps), `Recent` (bounded repeat history), `StartedCount` (tie seed offset), and `ConeInside` (mutable cone hysteresis memory). `Reset` is a no-op before initialization; after initialization it restores timestamps to `-1`, clears repeat and cone history, and sets `StartedCount` to zero. It preserves `Config`, `Candidates`, and `bInitialized`, so the selector remains usable. Applying that same assignment/clear operation repeatedly yields the same baseline.

## Existing tests

`RPGBossMoveSelectorTests.cpp` checks cooldown/repeat history reset with a clock lower than the old start, and a separate cone-hysteresis test verifies the remembered exit-band eligibility is forgotten after reset. Bounded tie selection tests use fixed seed and repeat sequences; no explicit reset-then-repeat-tie assertion was found to pin `StartedCount` reset or repeated-reset equivalence.

## Result / limits

Source behavior is idempotent for initialized selectors; no defect found. Direct repeated-reset equivalence and tie-seed replay after reset are test gaps. Reset is not a reinitialization and does not alter candidate/config identity. Static only.
