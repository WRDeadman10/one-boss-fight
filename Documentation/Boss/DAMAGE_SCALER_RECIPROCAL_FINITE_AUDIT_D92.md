# Damage scaler reciprocal-window and finite-input audit (D92)

Date: 2026-11-03. Static comparison of `FRPGDamageScaler` in `Source/OneBossFight/Player/RPGDamageScale.h` against its focused boundary tests. No test or build was run.

## Reciprocal matching boundary

`OnLoss` matches a prior hit when `Abs(Time - Hit.Time) <= Window` (`RPGDamageScale.h:48–57`); `OnHit` matches a prior loss with the same inclusive absolute comparison (`:77–86`). `Prune` removes records only when the forward difference is strictly greater than `Window` (`:104–107`). Thus both directions include exact equality, while the immediately adjacent value outside the interval is rejected.

Coverage is split across three focused files:

- `RPGDamageScalerReciprocalBoundaryTests.cpp:15–26`: loss at the exact upper boundary after a hit is matched; the next representable later instant is rejected and pruned.
- `RPGDamageScalerLowerWindowBoundaryTests.cpp:14–25`: hit exactly one window before a loss is matched; the next representable earlier instant is rejected.
- `RPGDamageScalerWindowBoundaryMutationTests.cpp:14–24`: exact equality and `nextafter(Window,+infinity)` use a zero timestamp to avoid decimal-rounding ambiguity.

These source fixtures support the reciprocal inclusive boundary claim; they have not been run in this audit.

## Nonfinite handling and test gap

- `OnLoss` returns 0 without queueing when time or amount is nonfinite (`:41–44`). Nonpositive finite amount also returns 0.
- `OnHit` returns 0 for nonfinite time. A negative or nonfinite multiplier is normalized to 1, so it claims a matching loss at the pack's unscaled damage rather than leaving it available for a later scaled hit (`:69–74`).
- `Prune` removes queued records whose time/amount/multiplier is nonfinite (`:102–107`).
- `Apply` rejects nonfinite health, adjustment, or maximum and returns the input health unchanged (`:95–100`). If `Health` itself is NaN/infinite, that same nonfinite value is propagated; no test currently characterizes that contract.

The dedicated reciprocal/lower-window tests contain no NaN or infinity cases. `RPGCodexTests.cpp:196–228` exercises normal matching, expiration, and clamped application but also no nonfinite values. `OnHit` with a bad multiplier and pending loss, invalid time/amount nonmutation, nonfinite queue pruning, and `Apply`'s nonfinite return policy therefore lack direct fixture assertions. Extreme finite `Amount * (1 - Multiplier)` can also overflow the returned adjustment; `Apply` then refuses that nonfinite adjustment and leaves health unchanged, but this path is untested.

## Disposition

The exact reciprocal window edges and immediate-outside values are represented in source tests. The acceptance condition for nonfinite cases is incomplete at test level: the implementation has explicit branches, but those branches and the nonfinite-Health pass-through are not covered. No runtime defect is claimed and no files outside this audit/document index were changed.
