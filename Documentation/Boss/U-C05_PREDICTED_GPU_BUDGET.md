# U-C05 — Predicted GPU budget and visual cost

## Current measured starting point

Owner Round 4 on the RTX 3060 proxy (BUILD-222 Development, 1920x1080, console session) reports legacy 27.29 FPS / p99 42.88 ms and selected route 27.10 FPS / p99 42.85 ms. The selected p99 would need to fall by at least 26.18 ms to reach 16.67 ms. The runs are GPU-bound; no Round 4 per-pass GPU profile is available. Evidence: `Docs/BossCombatReview/Execution/Claude/R4_BENCH_20261105/summary_table.txt` and the individual `runs/r4_selected_*` summaries.

## Measured historical candidate budgets (Round 2, older build)

| Candidate | Observed average FPS / p99 | Historical p99 delta vs late E00 | Visual cost | BUILD-222 prediction |
|---|---:|---:|---|---|
| `rpg.Perf.FireShadows=0` (E18) | 71.55 / 15.35 ms | -8.50 ms | All 12 brazier point lights lose dynamic shadows; lighting remains. | **Not measured.** Applying the old delta arithmetically to the Round 4 selected baseline gives about 34.35 ms, still over budget; this projection is only a scenario illustration, not an estimate. |
| `rpg.Perf.FireLights=0` (E17) | 77.73 / 14.24 ms | -9.61 ms | All 12 brazier point lights disappear; highest known visual cost among the isolated light trials. | **Not measured.** Carrying the old delta arithmetically gives about 33.24 ms, still over budget; do not treat as a forecast. |
| `rpg.Perf.FireLights=0` + fire FX, gate/dressing mist, and embers off (E25) | 78.45 / 13.94 ms | -9.91 ms | Combined and visually substantial removal of the point lights, flame/smoke/spark particles, fog cards, dressing mist, and ember field. | **Not measured.** Carrying the old delta arithmetically gives about 32.94 ms, still over budget; do not treat as a forecast. |

Source summaries: `Saved/bench_return/r2/runs/E18_fire_shadow_off_20261025_001426/summary.json`, `E17_fire_lights_off_20261025_001314/summary.json`, `E25_fire_mist_embers_off_20261025_002251/summary.json`, and late baseline `E00_baseline_20261025_002532/summary.json`. Round 2 values met the absolute target in that older run context, but the project/build differs and Round 4's baseline is much slower. The measured historical delta cannot be assumed to transfer.

## Budget conclusion

No combination can be honestly predicted to reach 16.67 ms on the current build from the available evidence. The known isolated fire-light changes account for only 8.50–9.61 ms of historical p99 improvement, while Round 4 needs at least 26.18 ms. The single-frame costs for VSM, deferred lights, clouds, and TSR in `U-C01_GPU_COST_MODEL.md` are not independent savings and must not be summed to fill that gap.

Round 5 should first retest the lower-visual-cost fire-shadow count/radius trials, then the VSM/cloud/AA/Lumen variables in `Scripts/round5_experiments.json`. A combination becomes a candidate only after its own run meets both thresholds on the RTX 3060 proxy and passes visual review; proxy success does not establish the RTX 2060 Super gate. Performance remains measure-and-propose. No shipped look or scalability change is authorized by this sheet.
