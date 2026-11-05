# V-C009 — Round 4 hitch and PSO precache proposal

## What the evidence supports

`U-C07P_ROUND4_HITCH_ANALYSIS.md` confirms two different outliers. The 699.274 ms warm-up frame has ordinary recorded game/render/GPU thread durations. A 144.87 ms RTPSO creation (59.42 ms compile + 85.34 ms link) occurs in the same five-second warm-up window, but the frame CSV has no wall-clock timestamp, so causation is unproven. In `r4_legacy_c`, frames 1288 and 1289 are 310.432 ms and 128.237 ms, with ~309/129 ms game-thread time and only ~32/35 ms GPU time. RTPSO creation and `FlushAsyncLoading(143)` appear in that run's startup log tens of seconds earlier; those records do not explain the later game-thread stall.

Do not present PSO precaching as a fix for the 310 ms stall or the 699 ms full-frame outlier. The data identifies an investigation path, not a root cause.

## Proposed diagnostic run

1. Capture a repeatable Development/data-route fight with Unreal Insights CPU, frame, GPU, loading, and PSO trace channels. Add a monotonic timestamp and frame index to each benchmark CSV row so frame outliers can be aligned to log/trace events.
2. Capture both a cold-cache launch and a warm-cache launch under identical build, route, resolution, driver, and graphics settings. Record cache-clearing method and keep raw traces/logs/CSV hashes. Do not compare cold and warm samples as if they were the same user scenario.
3. On UE 5.5.4, verify relevant PSO variables and validation commands through engine help before use. Capture `r.PSOPrecache.Validation=2`/`stat PSOPrecache` evidence only in Development; inspect miss/too-late counts and trace timers against each timestamped outlier. UE's current PSO documentation describes automatic asynchronous precaching and validation, but those 5.8 docs are background only; the installed 5.5.4 engine's help/source is authoritative for this project.
4. If a traced hitch is a PSO miss/too-late event, compare the current automatic precache path with one narrowly scoped remedy: wait for outstanding initial-load PSO work behind an existing loading transition, or add a measured bundled cache if the trace identifies repeatable states that automatic precaching misses. Test a clean package and both the proxy and target GPU.
5. If the trace instead identifies async loading, present wait, or another game-thread call, investigate that event specifically. Do not increase PSO worker threads or retain more PSOs by default without proving that the hitch is PSO-related and measuring CPU contention/memory cost.

## Acceptance and risks

An implementation proposal requires repeated timestamp-correlated evidence that the selected intervention removes or reduces the identified PSO miss/hitch, does not add visible proxy/material delay, does not regress fight p99, and stays within memory/package constraints. Keep visuals unchanged. Record startup/loading time as well as in-fight frame p99; moving work into a loading screen is acceptable only if its added wait is measured and approved.

References: [Epic PSO precaching overview](https://dev.epicgames.com/documentation/en-us/unreal-engine/pso-precaching-for-unreal-engine) (UE 5.8 reference, verify details against installed UE 5.5.4), [U-C07p Round 4 hitch evidence](U-C07P_ROUND4_HITCH_ANALYSIS.md).
