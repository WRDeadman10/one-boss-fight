# Designer reference: normalized warp curves

`RPGBossWarpCurve::Fraction` maps normalized elapsed time to a normalized distance fraction. The rule is unwired; callers choose a curve and apply its result to the total warp budget.

| Input | Unit | Default | Valid domain |
|---|---|---:|---|
| `T01` | fraction of warp duration | none | finite; clamped to 0–1 |
| `Curve` | enum | none | `Linear`, `Smooth`, `Overshoot` |
| `OvershootAmount` | normalized amount | 0.12 | finite, 0 to 0.5 inclusive |
| Return value | fraction of total distance | 0 for invalid input | 0–1 for Linear/Smooth; Overshoot may exceed 1 before returning to 1 |

Linear returns `t`. Smooth uses smoothstep `t²(3−2t)`. Overshoot uses an ease-out-back curve that can pass 1 and returns to exactly 1 at the endpoint. Time outside the interval is clamped before curve evaluation.

Non-finite time/overshoot, overshoot outside its domain, or an unknown curve returns 0. Source: [`RPGBossWarpCurveRules.h`](../../Source/OneBossFight/Player/RPGBossWarpCurveRules.h:7), unit tests: [`RPGBossWarpCurveRulesTests.cpp`](../../Source/OneBossFight/Tests/RPGBossWarpCurveRulesTests.cpp:6).
