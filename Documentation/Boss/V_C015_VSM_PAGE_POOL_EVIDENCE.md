# V-C015 — Virtual Shadow Map page-pool evidence by fire-shadow count

## Offline evidence result

The requested `rpg.Perf.FireShadows=0..12` page-pool series is **not present** in retained logs. The checked Round 2 experiment text has one `E18_fire_shadow_off` result (`rpg.Perf.FireShadows=0`), but no VSM page-pool statistics by count. The retained GPU profile records one 8.2 ms VSM frame (projection mask 4.1, non-Nanite raster 2.9, page allocation 0.7, Nanite 0.5); it does not enumerate fire-light count or page-pool demand. One Round 2 log line reports 16 VSM page allocations unserved, which indicates a page-pool overflow in that capture but does not identify per-light contribution.

| Fire-shadow count | Page-pool stat in checked retained logs | Status |
|---:|---|---|
| 0 | No count-specific stat located | no data |
| 1–11 | No count-specific stat located | no data |
| 12 / project setup | One unrelated log reports 16 page allocations unserved; count attribution unavailable | not a count series |

Sources: `Documentation/Boss/U-C01_GPU_COST_MODEL.md`; `Saved/bench_return/r2/game1_OneBossFight.log:1964`; `Saved/bench_return/r2/perf_experiments_20261025_002407.txt`. The historical `E18` run disabled fire-light shadows as a group and does not prove linear per-light scaling. No synthetic values or interpolated curve are supplied.

## Data needed to complete the model

For each count from 0 through 12, capture the same Development build/map/route/resolution and fixed camera/fight state, recording configured active fire shadows, VSM page-pool allocated/available/unserved counters, GPU pass timings, frame p99, and visible shadow result. Repeat each count and retain raw log plus frame/summary receipts. Verify the exact UE 5.5.4 stat/CVar that exposes the counters before running; if no count-specific counter exists, report that limitation and use a controlled ProfileGPU comparison instead. Treat any visual change as an owner-reviewed experiment; do not convert the resulting table into defaults here.
