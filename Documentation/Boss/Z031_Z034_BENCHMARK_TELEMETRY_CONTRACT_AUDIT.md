# Queue Z Batch 7 — benchmark and telemetry contract

**Scope:** Z031–Z035 read-only source/docs/evidence reconciliation. No benchmark, test, Editor, build or package was run.

## Z031 — sample, discard and percentile semantics

`ARPGBenchmarkRunner` logs raw wall-clock frame intervals, begins collecting at elapsed warmup time and records until warmup + duration (`Source/OneBossFight/Benchmark/RPGBenchmarkRunner.cpp:258–302`). `Scripts/RunBenchmark.ps1` defaults to 1920×1080 and 900 s timeout; the runner's documented default is 5 s warmup and 60 s record (`PERFORMANCE_LOG.md`, `Scripts/RunBenchmark.ps1`). `FRPGFrameStats::Compute` removes nonfinite/nonpositive values, then calculates frame count; average FPS is count / sum(frame-ms)/1000, not mean per-frame FPS. p50/p95/p99 use nearest-rank (`ceil(p*n)-1`) after ascending sort (`RPGFrameStats.cpp:5–51`).

Whole-frame, game-thread, render-thread and GPU samples are separate statistics. Thread times overlap; they must not be added (`RPGBenchmarkRunner.cpp:511–523`). The binding acceptance pair is average FPS and whole-frame p99. P99 is a frame-time percentile in milliseconds, not “99% FPS.” `SummarizeBenchmark.py` prints precomputed summary fields and rejects remote/virtual GPU labels and fights where `fight_started=false`; it does not recompute p99 from `frames.csv`.

## Z032 — active target and historical values

Current target: packaged 1920×1080, full encounter including phase two, average ≥60 FPS and whole-frame p99 ≤16.67 ms on the RTX 2060 Super; owner-approved RTX 3060 proxy is accepted for comparable results. 120 FPS / 8.33 ms is stretch telemetry only (`DECISIONS.md:404,602`; `PERFORMANCE_LOG.md:3,16`; `RPGFrameStats.h:8–12,35–48`). Round 4 legacy/data and Round 5 modes remain dated proxy measurements, not a current result. Round 4 selected route was 27.10 FPS / 42.85 ms p99; R5 Performance 38.1 FPS / 31.9 ms p99. R6 has no returned bundle per `TEST_PLAN.md` and X/Y intake reports, so R5 is not an R6 substitute.

Found and corrected stale acceptance text in the old PERF-01 row of `TEST_PLAN.md`: it stated ≥120 FPS / 8.33 ms as the target, contrary to current decisions. The row now states ≥60 FPS / 16.67 ms and leaves 120/8.33 as stretch only. Historical 120 FPS references remain where explicitly marked superseded/stretch.

## Z033 — graphics mode witnesses and limitations

Development Round 6 runner records active temporal upscaler, debug name, view-family primary resolution-fraction upper bound and AA method. Round 6 intake requires Dynamic Resolution off so the upper bound equals requested active primary fraction; the field is not an observed rendered-rectangle ratio (`RPGBenchmarkRunner.cpp` Development telemetry; `PERFORMANCE_LOG.md` Round 6 prep; `V_C018_DYNAMIC_RESOLUTION_DLSS_FEASIBILITY.md`). Treatment runs are rejected unless active upscaler is DLSS and the saved game log contains a matching `Creating NGX DLSS Feature ... NGXPerfQuality=` token (`RunPerfExperiments.ps1`; `round6_benchmark_report.py:13–18,60–67`). TSR anchors have separate identity. `PERFORMANCE_LOG.md` records that later archive inspection found matching feature-log mode witnesses in all 12 R5 DLSS treatment logs, correcting the earlier absent-witness note.

This proves a mode only when tied to that run's log and requested mode; CVar request, AA method or screen-fraction field alone is insufficient. The primary fraction is not physical output resolution, and Development-only telemetry is not packaged Shipping acceptance. No returned R6 rows/logs exist to verify this contract against new outcomes.

## Z034 — R6 identity/provenance contract

Round 6 schema requires per-run metrics, route/map, fight-start, GPU and settings/mode evidence. Yet current return status is **no R6 run bundle**. Existing X/Y intake states staged kit `BUILD_INFO` lacks package build ID and executable SHA-256; no raw R6 summaries, frames, game logs or run receipt exists. A future run needs an identity chain binding source revision/build record to staged package and inner executable, configuration, cooked manifest/content, run args/hardware/session, and immutable summary/frames/game-log hashes. Without it, valid metric shape cannot prove which source/package produced the measurement.

## Z035 — receipt and unresolved gates

Static source establishes the calculation contract; R4/R5 values are historical measurements with cited hardware/session/build limits. The R6 mode series and screen-fraction telemetry are Development evidence gates; a final target claim still needs the required packaged Shipping full-fight capture on acceptable hardware and a bound run identity. Absolute target remains missed by available R4/R5 values. No new performance outcome is claimed.

**Disposition:** Batch 7 complete locally. `git diff --check` is the only validation of this doc correction.
