# V-C013 — Frame-time budget from retained Round 4/5 measurements

## Acceptance target

The project target is 60 FPS average and p99 <=16.67 ms at 1920x1080 on the RTX 2060 Super, with an explicitly owner-approved RTX 3060 proxy allowed for comparable measurements. The 16.67 ms limit is a whole-frame budget; CPU and GPU overlap, so their percentiles must not be added as if they were serial costs.

## Current evidence (not the target GPU)

| Capture | Avg FPS | Whole-frame p99 | Game-thread p99 | Render-thread p99 | GPU p99 | Interpretation |
|---|---:|---:|---:|---:|---:|---|
| Round 4 legacy, BUILD-222, RTX 3060 | 27.29 | 42.88 ms | 5.52–6.08 ms across route captures | ~41–43 ms | 41.46–43.19 ms | GPU/render-bound; target missed |
| Round 4 selected data route, BUILD-222, RTX 3060 | 27.10 | 42.85 ms | 5.52–6.08 ms across route captures | ~41–43 ms | 41.46–43.19 ms | GPU/render-bound; target missed |
| Round 5 TSR, BUILD-224, RTX 3060 | 28.6 median | ~41.6 ms | Not present in the cited mode summary | Not present | Not present | Proxy baseline; Round 5 summary reports avg FPS/p99 only |
| Round 5 DLSS Performance, BUILD-224, RTX 3060 | 38.1 median | 31.9 ms | Not present in the cited mode summary | Not present | Not present | Faster but still misses target; Round 6 selection pending |

Sources: `Documentation/PERFORMANCE_LOG.md` Round 4 and Round 5 sections; Round 4 raw summary table at `Docs/BossCombatReview/Execution/Claude/R4_BENCH_20261105/summary_table.txt`; Round 5 archive at `Docs/BossCombatReview/Execution/Claude/R5_BENCH_20261105/bench_results_round5.zip`. Preserve build, route, GPU, driver, resolution and session labels when comparing. Round 5 mode-level thread/GPU percentiles are not reported in the cited summary and are intentionally left blank.

## Budget interpretation

- Whole-frame: <=16.67 ms p99 is the binding gate.
- Game thread: Round 4's ~5.5–6.1 ms p99 is below whole-frame target, but leave headroom for hitches and other workloads; do not claim a finalized sub-budget from these captures.
- Render thread and GPU: both approach the whole-frame p99 on Round 4, so they need pass-level evidence before assigning per-system allocations.
- Round 2's single `ProfileGPU` sample is a different build/context and is not an additive budget. Round 6 must produce valid per-mode thread/GPU metrics and a Development `ProfileGPU` capture before any finer allocation is proposed.

This is a measurement table, not an accepted optimization or settings change.
