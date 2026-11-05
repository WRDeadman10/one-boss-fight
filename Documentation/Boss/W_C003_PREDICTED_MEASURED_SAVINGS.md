# W-C003 — predicted versus measured savings template

Round 6 outcome: **not returned**. Prediction ranges below are copied from Antigravity's V-A021 proposal; measured columns intentionally remain blank. Predictions are hypotheses, not performance evidence or an approval to change defaults.

| Profile | Proposed variables | Predicted GPU saving | Measured GPU saving | Difference | Evidence / limitation |
|---|---|---:|---:|---:|---|
| L1 Cardinal Shadows | `rpg.Perf.FireShadows 4` | 4.0–5.5 ms | — | — | V-A021 projected range; confirm with Round 6 paired anchors. |
| L2 Cardinal + Radius | L1 plus `rpg.Perf.FireRadiusScale 0.65` | 5.5–6.5 ms | — | — | V-A021 projected range; visual contrast impact needs owner review. |
| L3 Optimized Full | L2 plus `r.SkyLight.RealTimeReflectionCapture 0`, cloud shadow max count 32, cloud view-ray scale 0.5 | 7.0–8.5 ms | — | — | V-A021 projected range; multiple variables and moderate visual impact; interpret only as a profile, not isolated attribution. |

The retained Round 5 DLSS Performance median context is 38.1 average FPS / 31.9 ms p99 on RTX 3060; this is not a measurement of any L1–L3 profile. The Round 6 plan must first establish a valid mode and approved image quality. No profile has been applied by this document.
