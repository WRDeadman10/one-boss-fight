# Poise regeneration zero-ramp audit (Queue D94)

**Scope:** source/test comparison for the pure `RPGBossPoiseRegen::Rate` helper. It is documented as unwired. Static review only; no test was run.

## Equation and guard order

`Source/OneBossFight/Player/RPGBossPoiseRegenRules.h:8-16` first refuses nonfinite values and invalid ranges (base rate 0..1e6, elapsed >= 0, delay 0..1e6, ramp strictly positive and <=1e6, max scale 1..3). Before delay it returns 0. At/after delay it computes `T = clamp((elapsed-delay)/ramp, 0, 1)` and returns `base * (1 + (maxScale-1)*T)`. There is no retained mutable state: reset behavior belongs to the caller's elapsed-since-hit input.

## Existing tests

- `Source/OneBossFight/Tests/RPGBossPoiseRegenRulesTests.cpp:10-14` checks pre-delay zero, equality at a positive delay yields base rate, midpoint ramp, max-scale cap, a 1001-sample monotonic/bounded sweep, and infinite elapsed refusal.
- `Source/OneBossFight/Tests/RPGBossPoiseRegenZeroRampMutationTests.cpp:10-15` explicitly checks zero ramp duration returns zero.

## Gaps / conclusions

- No explicit test uses zero elapsed. The equation implies base rate when `DelaySeconds == 0`, and zero rate when a positive delay remains; the existing sweep begins at elapsed 0 but uses delay 1, so it only proves the latter.
- Zero ramp is intentionally invalid (`RampSeconds <= 0`), covered by a focused mutation test; a negative ramp is not separately asserted.
- The test checks a sampled ramp endpoint well beyond its end, but not exact equality `SecondsSinceHit == DelaySeconds + RampSeconds` or the adjacent representable times. The clamp makes the exact endpoint max-scaled by inspection.
- `MaxScale == 1` should make the ramp flat, but there is no direct assertion. The configured upper bound `MaxScale == 3` and rejection above it are also not tested; existing positive config uses 1.5.
- There is no internal reset state. If an integration stores elapsed time, its reset-to-zero and hit timestamp lifecycle need a separate caller audit; this pure helper alone cannot establish that behavior.
- All accepted numeric ranges keep the computed multiplier bounded by 3 and base by 1e6. No overflow is apparent from valid arguments; invalid/nonfinite inputs return zero before arithmetic.

**Acceptance:** current source behavior is explicit; tests cover representative delay/ramp/cap boundaries and invalid zero ramp. Remaining adjacent-edge, scale endpoint, and caller reset cases are precisely listed above; no undocumented mutable reset contract was inferred.
