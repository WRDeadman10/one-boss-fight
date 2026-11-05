# Move-card warp curve edge audit (Queue D45)

Scope: compare `RPGBossWarpCurve::Fraction` endpoints, normalized-time clamp, overshoot domain, and existing tests with the executor's separate timed warp. Static review only; no tests/build/Editor run.

## Rule semantics and relationship to card fields

- `Fraction` rejects nonfinite `T01`/overshoot amount and overshoot outside `[0,.5]`, clamps normalized time to `[0,1]`, then selects Linear, Smoothstep, or ease-out-back Overshoot (`Source/OneBossFight/Player/RPGBossWarpCurveRules.h:5-20`). For all three valid modes, endpoints are 0 at `T=0` and 1 at `T=1`; Overshoot may exceed 1 inside the domain and returns to 1 at the end.
- This helper is explicitly unwired. Current card warp instead uses `WarpStartSeconds`/`WarpEndSeconds`, `RPGBossApproach::StepCm`, and the remaining-distance/budget `RPGBossTrack::WarpStepCm` path (`Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:422-477`). The separate `RPGBossWarpExactDurationBoundaryTests.cpp` tests that executor step schedule, not `RPGBossWarpCurve::Fraction` duration or card integration.

## Existing tests and mutation gaps

- `OneBossFight.Framework.WarpCurve.Rules` tests exact 0/1 endpoints for all modes, linear/smooth midpoint, overshoot above 1 at midpoint, pre/post-time clamp, and one invalid overshoot amount (`Source/OneBossFight/Tests/RPGBossWarpCurveRulesTests.cpp:8-18`). It does not test the overshoot's intermediate peak location or endpoint-adjacent values.
- No dedicated warp-curve duration input exists: `Fraction` receives normalized time only. Duration validation belongs to its caller, but no caller currently wires the helper. The exact-duration mutation fixture covers `WarpStepCm` with a remaining-time schedule and does not prove curve duration behavior.
- Missing direct cases: `T` just below/above endpoints; nonfinite T and amount; overshoot amounts exactly 0 and .5 and adjacent outside values; invalid enum value; smooth monotonicity/end derivative or overshoot return-to-end across sample points; negative/zero card duration and curve-to-move consumer composition if a caller is added.

No endpoint mutation mismatch is identified. Existing tests match the rule's exact endpoint and clamp semantics, but do not establish authoring/runtime application to a move card or exact duration behavior for this unwired helper.
