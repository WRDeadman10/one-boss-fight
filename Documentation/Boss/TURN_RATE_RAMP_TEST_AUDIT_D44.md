# Turn-rate ramp test audit (Queue D44)

Scope: map ramp start/end, interpolation, clamp, monotonicity and invalid-value test coverage against the pure rule. Static review only; no tests/build/Editor run.

## Rule contract

- `RPGBossTurnRateRamp::Rate` rejects nonfinite inputs, negative elapsed, nonpositive ramp duration, and either rate outside `[0,720]`; otherwise it clamps `Elapsed/Ramp` to `[0,1]`, applies smoothstep, and linearly interpolates start to end (`Source/OneBossFight/Player/RPGBossTurnRateRamp.h:7-15`). It supports increasing or decreasing ramps and is explicitly unwired (`:5-6`; `Documentation/Boss/RULES_REFERENCE_110_TURN_RATE_RAMP.md:3`).
- Invalid input returns 0, which is also a valid authored endpoint; a caller would need separate validation/error handling to distinguish refusal from a legitimate zero limit. No maintained caller currently consumes the rule.

## Existing tests and gaps

- `OneBossFight.Framework.TurnRateRamp.Rules` covers start at t=0 (60), midpoint at t=.5 of 1 s (120), clamping beyond end (180), a 1001-sample monotonic increase within bounds, NaN elapsed, and negative start rate (`Source/OneBossFight/Tests/RPGBossTurnRateRampTests.cpp:8-17`).
- Gaps: exact `Elapsed==RampSeconds`; immediately below/above that endpoint; zero start/end and maximum 720 endpoints; decreasing-ramp monotonicity; zero/negative/nonfinite ramp duration; invalid end rate and rates just outside 0/720; nonfinite rate inputs; period-scale independence. There is no test of application to `StepYaw` or runtime card turning because the rule is unwired.
- Existing test proves the increasing interior profile and a post-end clamp, not endpoint behavior across both directions or runtime turning. No source mismatch is established.

Bounded future tests: endpoint equality/adjacent times; increasing and decreasing endpoints at 0/720; invalid domain edges for both rates/duration; and a composition test only if a caller is later wired. Do not claim animation turn timing from this pure interpolation rule.
