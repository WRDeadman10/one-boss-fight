# Round 6 Phase 1 intake (lead, Claude, 2026-11-06)

Source: `D:\BenchTransfer\R6b\bench_results_GANPATIGAMERBOI_20261106_150650.zip` (1,543,766 bytes, SHA-256 `342582190518453db5fa6739e7ce08478682b28c5becc8c7fb3cd00ec3f10a8e`), unpacked to `Saved/bench_return/round6_20261106/` (git-ignored). Kit: R6b (commit 21dbcb18, BUILD-240), Development stage, selected data route (`-H019EncounterDefinition=.../DA_Sevarog_G044_Encounter`, log `route=data reason=StoredDefinition`), RTX 3060 proxy, driver 610.88, 1920x1080, 60 s fights.

## Numbers recomputed by the lead from every `summary.json` (median per arm)

| Arm | Runs | Primary % | Avg fps | p99 ms | GPU avg ms | Render p99 ms | Game p99 ms |
|---|---|---|---|---|---|---|---|
| TSR anchor | 4 | 72.9 | 26.66 | 45.7 | 36.2 | 45.4 | 6.6 |
| DLSS Quality | 3 | 66.7 | 29.82 | 42.1 | 32.2 | 41.6 | 6.9 |
| DLSS Balanced | 3 | 58.0 | 33.56 | 37.6 | 28.5 | 37.2 | 6.9 |
| DLSS Performance | 3 | 50.0 | 35.19 | 35.9 | 27.1 | 35.5 | 6.7 |

All match the benchmark PC's report. Every run `fight_started=true`; anchors report `TSR`, treatments `DLSS`. Mode witnesses read from each first-trial `game.log` "NGX DLSS Feature" line: Quality `MaxQuality(2)` 1281x721, Balanced `Balanced(1)` 1114x627, Performance `MaxPerf(0)` 960x540. The aborted first anchor (`..._144753`) is excluded.

Correction to the PC's report: these runs used the Development stage, whose build ID is `OBF-DEVELOPMENT-20261106T071240Z-ed06b4d6`; the `OBF-SHIPPING-...` ID it quoted belongs to the Shipping stage in the same kit.

## Reading

- GATE-04 (60 fps average, p99 <= 16.67 ms) is not reached by any mode: the best (Performance) is 35.2 fps / 35.9 ms p99, about 2.2x over the frame budget.
- The game is GPU-bound. Halving the internal resolution (TSR 72.9 % to DLSS 50 %) only cut GPU time from 36.2 to 27.1 ms, so roughly 25 ms of the frame does not scale with resolution (shadows, lights, sky/clouds, post; KI-108 named fire shadows and clouds). DLSS alone cannot reach the target; Phase 2 (16 runs: the per-feature switches on top of the accepted DLSS mode) is the next measurement, and closing the rest will need look-changing changes that require the owner's yes.

## Kit defects reported by the PC and fixed in the repo (not yet in a kit)

1. `Scripts/RunPerfExperiments.ps1`: Windows PowerShell 5.1 does not escape embedded quotes when passing an argument with spaces to the nested `powershell -File`, so `-LogCmds="LogDLSS Verbose,..."` split and the first DLSS run failed. Fixed the same way the PC did (embedded `"` escaped as `\"`).
2. `Scripts/MakeBenchKit.ps1` did not copy `Scripts/Tools/round6_benchmark_report.py`, so step 8 (receipt) could not be validated on the PC. Now copied.

## Open

- Owner: image-quality acceptance of one DLSS mode (it decides Phase 2's base).
- Step 8 receipt (`onebossfight.round6-benchmark/v1`) built from the raw runs and validated with `round6_benchmark_report.py` (Codex, offline).
- Phase 2: only after the owner's mode choice and the lead's acceptance.
