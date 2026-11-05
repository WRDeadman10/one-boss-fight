# S116 — center-bias geometry feasibility audit

## Authored geometry

`B_MOV002/create_centerbias_content.py` sets arena center `(250,0)`, radius 300 cm, bias 1, start fraction 0.5, boss spawn `(-300,400)`, and band `[110,140]` (`:22–24,76–83,102–105,160`). The profile readback confirms radius/center/bias at `B_MOV002/content_run1/editor_raw.log:1378`; the remaining fixture values, including the band, are logged at `:1379`. The profile creates the map fixture with the authored arena center and spawn transform (`create_centerbias_content.py:156–160`).

At the walk request, the target is the origin in XY. Thus `ToCenter=(250,0)`, normalized center direction is `(1,0)`, and the initial boss-to-target `Away=(-300,400)/500=(-0.6,0.8)`. With bias 1, `CenterBiasedAway` returns `(1,0)`; bias 0 returns the original `(-0.6,0.8)` (`RPGFrameworkBossController.cpp:17–31`, `RPGBossTrackRules.h:31–42`). Target distance from center is 250 cm, greater than the threshold `0.5*300=150`, so `near=1` in both runs.

The requested destination uses the authored band midpoint `(110+140)/2=125` cm. Before nav projection, the expected biased destination is `(125,0)` and the zero-bias control is `(-75,100)`. Their center-axis displacement is +200 cm in X; the full predicted separation is `sqrt(200^2+100^2)=223.607 cm`. Nav projection and the arrival tolerance can move the final point, so use these as directional/geometry expectations, not exact endpoint equality.

## Retained A/B evidence

- Enabled: `pie_biased_v2/editor_raw.log:1588` logs `targetFromCenterCm=250 thresholdCm=150 bias=1 near=1 away=(-0.6,0.8) biased=(1,0)`. Arrival at `:1592` is `(122.511,3.516)`, range 122.561 cm inside the band.
- Control: `pie_control_bias0_v2/editor_raw.log:1591` logs the same center distance/threshold/near state with `bias=0` and unchanged direction `(-0.6,0.8)`. Arrival at `:1593` is `(-77.080,102.773)`, range 128.467 cm inside the band.
- The control explicitly runs `rpg.BossProofCenterBias 0` (`pie_control_bias0_v2/editor_raw.log:1394–1395`); the profile still authors bias 1. Compare the same target-origin and arena geometry, not the selector's card-range filter.

The measured endpoint delta is approximately `(199.591,-99.257)` cm, consistent with the hand-calculated center-side direction and displacement. No new runtime run was performed. The existing paired logs supply the geometry needed for the feasibility acceptance.
