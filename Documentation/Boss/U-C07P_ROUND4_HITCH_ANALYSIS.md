# U-C07p — Round 4 hitch evidence audit

## Scope and evidence

Read-only analysis of the Round 4 legacy warm-up and `r4_legacy_c` captures. The summary's 699 ms and 310 ms maxima are confirmed against raw per-frame CSVs. CSV columns are `frame,ms,game_ms,render_ms,gpu_ms`; neither run includes a timestamp column, so frame-to-log correlation is bounded by the benchmark start and log events, not exact wall-clock mapping.

| Run | Outlier row(s) | Frame time | Game thread | Render thread | GPU | Evidence |
|---|---:|---:|---:|---:|---:|---|
| `r4_legacy_warmup` | 19 | 699.2740 ms | 5.2315 ms | 32.2546 ms | 30.0489 ms | `Saved/bench_return/round4_20261105/runs/r4_legacy_warmup_20261105_145845/frames.csv`; SHA-256 `501CEBEFC73D05E5C4137C9CBE68363A07C61ED6E867120C3B27F45FF1F172CF` |
| `r4_legacy_c` | 1288 | 310.4318 ms | 308.7521 ms | 34.6139 ms | 32.3308 ms | `Saved/bench_return/round4_20261105/runs/r4_legacy_c_20261105_150217/frames.csv`; SHA-256 `851D736E5AF3D21398D03AA18AD36B051A56EC030B9488DBCCB1D285BF104F75` |
| `r4_legacy_c` | 1289 | 128.2369 ms | 129.1022 ms | 8.8527 ms | 35.1331 ms | same CSV |

No other frame over 100 ms appears in either capture. Frame 1288 and 1289 form consecutive game-thread stalls; the render/GPU columns do not show corresponding 100+ ms work. This locates the large measured stall on the game thread, but does not identify which task inside it caused the delay.

## Shader / streaming evidence

The warm-up process log `Saved/bench_return/round4_20261105/game1_OneBossFight-backup-2026.11.05-09.28.46.log` (SHA-256 `C2305191A6E7698A5DC6CF96536A0DC2CE386A87E89A8D7ACE57590A74D9790D`) records benchmark start at `09:27:40.171`, then an RTPSO creation at `09:27:44.506`: 21 shaders, 0 cached / 21 new, 144.87 ms total (59.42 ms compile + 85.34 ms link). This is in the 5 s warm-up window immediately before measured rows; it is direct evidence of shader pipeline compilation during startup and is temporally consistent with a warm-up capture outlier. The CSV has no clock timestamp, so the RTPSO line cannot be tied causally to frame 19.

For `r4_legacy_c`, the process log `Saved/bench_return/round4_20261105/game1_OneBossFight-backup-2026.11.05-09.32.19.log` (SHA-256 `E04E4EF95C673E4D09BEB611A43E07969B0737688B802570EEF073FAEE14276E`) records benchmark start at `09:31:12.815`. During warm-up it records an RTPSO creation at `09:31:14.323` (21 shaders, 66.83 ms total; 45.59 ms compile + 21.11 ms link) and `FlushAsyncLoading(143)` at `09:31:14.858`. These startup events precede the frame-1288 hitch by tens of seconds. The inspected shader/streaming records are startup events; because timestamps are absent from `frames.csv`, this capture cannot correlate any log record with frame 1288 or establish that a later event is absent at that frame.

The 699 ms warm-up sample has ordinary reported game/render/GPU thread durations despite its full-frame time. This points to a frame-pacing/present/wait or external scheduling delay outside those sampled thread durations; available data cannot distinguish among them. Do not label it a shader compile hitch as a confirmed cause. The logs prove RTPSO compilation happened in startup, but not that it caused that 699 ms sample.

## Disposition

- **Confirmed:** isolated ~310 ms game-thread stall over two adjacent measured frames in `r4_legacy_c`; RTPSO work and async-loading flushes are present during startup/warm-up.
- **Not established:** exact game-thread call/site for frame 1288; causal link from either startup RTPSO event to the 699 ms warm-up row; whether any individual hitch is shader, streaming, present, or OS scheduling without timestamped per-frame trace data.
- **Next evidence to collect:** rerun with Unreal Insights trace channels for frame, CPU, GPU, loading, and PSO events, plus a monotonic timestamp/frame index in the benchmark CSV. Compare a cold launch against a warmed shader/PSO-cache launch. Keep current visual settings unchanged.

This is a proxy Development capture on the RTX 3060 and is not a release-target performance result.
